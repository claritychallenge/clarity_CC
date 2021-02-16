# See README.md

# The program measures the file digital RMS from channel 1.

# Original commentary from MATLAB version:
# If add_calibration == True ...
# Each channel being processed has inserted on its start a 500 Hz tone, followed by a
# short burst of EarHear 2008 (Moore et al) shaped noise: EH2008 shape: Flat spectrum
# level to 500 Hz, then sloping off 7.5dB/octave above that to 8 kHz, then -13 dB/oct.
# Credit to B.R.Glasberg who implemented the original C-code filterbank and recruitment
# ITU reference position conversion courtesy of Peter Hughes at BTRL (2001). These are
# the negative of values in Table 14a of ITU P58 (05/2013),
# accessible at http://www.itu.int/rec/T-REC-P.58-201305-I/en.
# Converts from ear reference point (ERP) to eardrum reference point (DRP)

import logging
import math
import numpy as np
from scipy import interpolate, signal
from scipy.signal import firwin, lfilter

import MSBG
import MSBG.data.src_to_cochlea_filters as data
from MSBG.firwin2 import firwin2
from clarity_core.config import CONFIG

fs = MSBG.MASTER_FS

# Cut off frequency of low-pass filter at end of simulations:
# prevents possible excessive processing noise at high frequencies.
UPPER_CUTOFF_HZ = 18000


class Ear(object):
    """Representation of a pairs of ears.

    Attributes:
        src_pos (str): Position of sources, free/diffuse field placement
        audiogram (Audiogram): The audiogram for the ears.

    """

    def __init__(self, src_pos, audiogram):
        """Constructor for the Ear class.

        Args:
            src_pos (str): Position of the source
            audiogram (Audiogram): The ear's audiogram

        """
        self.audiogram = audiogram
        self.cochlea = MSBG.Cochlea(self.audiogram)
        self.calibration_signal = None
        if np.max(audiogram.levels[audiogram.levels != None]) > 80:
            logging.warning(
                "Impairment too severe: Suggest you limit audiogram max to 80-90 dB HL, \
                otherwise things go wrong/unrealistic."
            )
        self.src_correction = Ear.get_src_correction(src_pos)

    @staticmethod
    def get_src_correction(src_pos):
        """Select relevant external field to eardrum correction.

        Args:
            src_pos (str): Position of src. One of ff, df or ITU

        """
        if src_pos == "ff":
            src_correction = data.FF_ED
        elif src_pos == "df":
            src_correction = data.DF_ED
        elif src_pos == "ITU":  # transfer to same grid
            f = interpolate.interp1d(data.ITU_HZ, data.ITU_ERP_DRP, kind="linear")
            src_correction = f(data.HZ)
        else:
            logging.error(
                f"Invalid src position ({src_pos}). Must be one of ff, df or ITU"
            )
            raise ValueError("Invalid src position")
        return src_correction

    @staticmethod
    def src_to_cochlea_filt(ip_sig, src_correction, fs, backward=False):
        """Simulate middle and outer ear transfer functions.

        Made more general, Mar2012, to include diffuse field as well as ITU reference points,
        that were included in DOS-versions of recruitment simulator, released ca 1999-2001,
        and on hearing group website, Mar2012 variable [src_pos] takes one of 3 values: 'ff', 'df' and 'ITU'
        free-field to cochlea filter forwards or backward direction, depends on 'backward' switch.
        NO LONGER via 2 steps. ff to eardrum and then via middle ear: use same length FIR 5-12-97.

        Args:
            ip_sig (ndarray): signal to process
            src_correction (str): correction to make for src position
            fs (int): sampling frequency
            backward (bool, optional): if true then cochlea to src (default: False)

        Returns:
            ndarray: the processed signal

        """
        logging.info("performing outer/middle ear corrections")

        # make sure that response goes only up to fs/2
        nyquist = int(fs / 2)
        ixf_useful = np.nonzero(data.HZ < nyquist)

        hz_used = data.HZ[ixf_useful]
        hz_used = np.append(hz_used, nyquist)

        # sig from free field to cochlea: 0 dB at 1kHz
        correction = src_correction - data.MIDEAR
        f = interpolate.interp1d(data.HZ, correction, kind="linear")
        last_correction = f(nyquist)  # generate synthetic response at Nyquist

        correction_used = np.append(correction[ixf_useful], last_correction)
        if backward:  # ie. coch->src rather than src->coch
            correction_used = -correction_used
        correction_used = np.power(10, (0.05 * correction_used))

        correction_used = correction_used.flatten()
        # Create filter with 23 msec window to do reasonable job down to about 100 Hz
        # Scales with fs, falls over with longer windows in fir2 in original MATLAB version
        n_wdw = 2 * math.floor((fs / 16e3) * 368 / 2)
        hz_used = hz_used / nyquist

        b = firwin2(n_wdw + 1, hz_used.flatten(), correction_used, window=("kaiser", 4))
        op_sig = signal.lfilter(b, 1, ip_sig)

        return op_sig

    @staticmethod
    def make_calibration_signal(REF_RMS_DB):
        """Add the calibration signal to the start of the signal.

        Args:
            signal (ndarray): input signal

        Returns:
            ndarray: the processed signal

        """
        # Calibration noise and tone with same RMS as original speech,
        # Tone at nearest channel centre frequency to 500 Hz
        # For testing, ref_rms_dB must be equal to -31.2

        noise_burst = MSBG.gen_eh2008_speech_noise(duration=2, fs=fs, level=REF_RMS_DB)
        tone_burst = MSBG.gen_tone(freq=520, duration=0.5, fs=fs, level=REF_RMS_DB)
        silence = np.zeros(int(0.05 * fs))  # 50 ms duration
        return (
            np.concatenate((silence, tone_burst, silence, noise_burst, silence)),
            silence,
        )

    @staticmethod
    def array_to_list(chans):
        """Convert ndarray into a list of 1-D arrays."""
        if len(chans.shape) == 1:
            chans = chans[..., np.newaxis]
        return [chans[:, i] for i in range(chans.shape[1])]

    def process(
        self,
        chans,
        add_calibration=False,
    ):
        """Run the hearing loss simulation.

        Args:
            chans (ndarray): signal to process, shape either N, Nx1, Nx2
            add_calibration (bool): prepend calibration tone and speech-shaped noise
                (default: False)

        Returns:
            ndarray: the processed signal

        """

        fs = 44100  # This is the only sampling frequency that can be used
        if fs != CONFIG.fs:
            logging.error(
                "Warning: only a sampling frequency of 44.1kHz can be used by MSBG."
            )

        logging.info(f"Processing {len(chans)} channels")

        # Get single channel array and convert to list
        chans = Ear.array_to_list(chans)

        levelreFS = 10 * np.log10(np.mean(np.array(chans) ** 2))

        equiv_0dB_SPL = CONFIG.equiv0dBSPL + CONFIG.ahr

        leveldBSPL = equiv_0dB_SPL + levelreFS
        CALIB_DB_SPL = leveldBSPL
        TARGET_SPL = leveldBSPL
        REF_RMS_DB = CALIB_DB_SPL - equiv_0dB_SPL

        # Need to know file RMS, and then call that a certain level in SPL:
        # needs some form of pre-measuring. 3rd arg is dB_rel_rms (how far below)
        calculated_rms, idx, rel_dB_thresh, active = MSBG.measure_rms(chans[0], fs, -12)

        change_dB = TARGET_SPL - (equiv_0dB_SPL + 20 * np.log10(calculated_rms))

        # Rescale input data and check level after rescaling
        chans = [x * np.power(10, 0.05 * change_dB) for x in chans]
        new_rms_db = equiv_0dB_SPL + 10 * np.log10(
            np.mean(np.power(chans[0][idx], 2.0))
        )
        logging.info(
            f"Rescaling: leveldBSPL was {leveldBSPL:3.1f} dB SPL, now {new_rms_db:3.1f}dB SPL. Target SPL is {TARGET_SPL:3.1f} dB SPL."
        )

        # Add calibration signal at target SPL dB
        if add_calibration == True:
            if self.calibration_signal is None:
                self.calibration_signal = Ear.make_calibration_signal(REF_RMS_DB)
            chans = [
                np.concatenate(
                    (self.calibration_signal[0], x, self.calibration_signal[1])
                )
                for x in chans
            ]

        # Transform from src pos to cochlea, simulate cochlea, transform back to src pos
        chans = [Ear.src_to_cochlea_filt(x, self.src_correction, fs) for x in chans]
        chans = [self.cochlea.simulate(x, equiv_0dB_SPL) for x in chans]
        chans = [
            Ear.src_to_cochlea_filt(x, self.src_correction, fs, backward=True)
            for x in chans
        ]

        # Implement low-pass filter at top end of audio range: flat to Cutoff freq, tails
        # below -80 dB. Suitable lpf for signals later converted to MP3, flat to 15 kHz.
        # Small window to design low-pass FIR, to cut off high freq processing noise
        # low-pass to something sensible, prevents exaggeration of > 15 kHz
        winlen = 2 * math.floor(0.0015 * fs) + 1
        lpf44d1 = firwin(winlen, UPPER_CUTOFF_HZ / int(fs / 2), window=("kaiser", 8))
        chans = [lfilter(lpf44d1, 1, x) for x in chans]

        return chans
