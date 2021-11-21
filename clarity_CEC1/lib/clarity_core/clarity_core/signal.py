"""Functions for handling signals."""

import numpy as np
from numpy.fft import fft, ifft, fftshift
import math
from scipy.signal import convolve, find_peaks
import scipy.io
import soundfile
from soundfile import SoundFile
import logging

from clarity_core.config import CONFIG

TAIL_DURATION_CONSTANT = CONFIG.tail_duration

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

# Fixed filter used in computing speech weighted SNRs
with pkg_resources.path("clarity_core", "speech_weight.mat") as fp:
    SPEECH_FILTER = scipy.io.loadmat(fp, squeeze_me=True)
    SPEECH_FILTER = np.array(SPEECH_FILTER["filt"])


def read_signal(filename, offset=0, nsamples=-1, nchannels=0, offset_is_samples=False):
    """Read a wavefile and return as numpy array of floats.

    Args:
        filename (string): Name of file to read
        offset (int, optional): Offset in samples or seconds (from start). Defaults to 0.
        nchannels: expected number of channel (default: 0 = any number OK)
        offset_is_samples (bool): measurement units for offset (default: False)
    Returns:
        ndarray: audio signal
    """
    try:
        wave_file = SoundFile(filename)
    except:
        # Ensure incorrect error (24 bit) is not generated
        raise Exception(f"Unable to read {filename}.")

    if nchannels != 0 and wave_file.channels != nchannels:
        raise Exception(
            f"Wav file ({filename}) was expected to have {nchannels} channels."
        )

    if wave_file.samplerate != CONFIG.fs:
        raise Exception(f"Sampling rate is not {CONFIG.fs} for filename {filename}.")

    if not offset_is_samples:  # Default behaviour
        offset = int(offset * wave_file.samplerate)

    if offset != 0:
        wave_file.seek(offset)

    x = wave_file.read(frames=nsamples)

    return x


def write_signal(filename, x, fs, floating_point=True):
    """Write a signal as fixed or floating point wav file."""

    if fs != CONFIG.fs:
        logging.warning(f"Sampling rate mismatch: {filename} with sr={fs}.")
        # raise ValueError("Sampling rate mismatch")
    
    if floating_point is False:
        if CONFIG.test_nbits == 16:
            subtype = "PCM_16"
            # If signal is float and we want int16
            x *= 32768
            x = x.astype(np.dtype("int16"))
            assert np.max(x) <= 32767 and np.min(x) >= -32768
        elif CONFIG.test_nbits == 24: 
            subtype = "PCM_24"
    else:
        subtype = "FLOAT"

    soundfile.write(filename, x, fs, subtype=subtype)


def pad(signal, length):
    """Zero pad signal to required length.

    Assumes required length is not less than input length.
    """
    assert length >= signal.shape[0]
    return np.pad(
        signal, [(0, length - signal.shape[0])] + [(0, 0)] * (len(signal.shape) - 1)
    )


def sum_signals(signals):
    """Return sum of a list of signals.

    Signals are stored as a list of ndarrays whose size can vary in the first
    dimension, i.e., so can sum mono or stereo signals etc.
    Shorter signals are zero padded to the length of the longest.

    Args:
        signals (list): List of signals stored as ndarrays

    Returns:
        ndarray: The sum of the signals

    """
    max_length = max(x.shape[0] for x in signals)
    return sum(pad(x, max_length) for x in signals)


def apply_brir(signal, brir, n_tail=TAIL_DURATION_CONSTANT):
    """Convolve a signal with a BRIR.

    Args:
        signal (ndarray): The mono or stereo signal stored as array of floats
        brir (ndarray): The binaural room impulse response stored a 2xN array of floats
        n_tail (int): Truncate output to input signal length + n_tail
    Returns:
        ndarray: The convolved signals

    """
    output_len = len(signal) + n_tail
    brir = np.squeeze(brir)

    if len(np.shape(signal)) == 1 and len(np.shape(brir)) == 2:
        signal_l = convolve(signal, brir[:, 0], mode="full", method="fft")
        signal_r = convolve(signal, brir[:, 1], mode="full", method="fft")
    elif len(np.shape(signal)) == 2 and len(np.shape(brir)) == 2:
        signal_l = convolve(signal[:, 0], brir[:, 0], mode="full", method="fft")
        signal_r = convolve(signal[:, 1], brir[:, 1], mode="full", method="fft")
    else:
        logging.error("Signal does not have the required shape.")
    output = np.vstack([signal_l, signal_r]).T
    return output[0:output_len, :]


def compute_snr(target, noise, pre_samples=0, post_samples=-1):
    """Return the SNR.

    Take the overlapping segment of the noise and get the speech-weighted
    better ear SNR. (Note, SNR is a ratio -- not in dB.)
    """

    pre_samples = int(CONFIG.fs * CONFIG.pre_duration)
    post_samples = int(CONFIG.fs * CONFIG.post_duration)

    segment_target = target[pre_samples:-post_samples]
    segment_noise = noise[pre_samples:-post_samples]
    assert len(segment_target) == len(segment_noise)

    snr = better_ear_speechweighted_snr(segment_target, segment_noise)

    return snr


def better_ear_speechweighted_snr(target, noise):
    """Calculate effective better ear SNR."""
    if np.ndim(target) == 1:
        # analysis left ear and right ear for single channel target
        left_snr = speechweighted_snr(target, noise[:, 0])
        right_snr = speechweighted_snr(target, noise[:, 1])
    else:
        # analysis left ear and right ear for two channel target
        left_snr = speechweighted_snr(target[:, 0], noise[:, 0])
        right_snr = speechweighted_snr(target[:, 1], noise[:, 1])
    # snr is the max of left and right
    be_snr = max(left_snr, right_snr)
    return be_snr


def speechweighted_snr(target, noise):
    """Apply speech weighting filter to signals and get SNR."""
    target_filt = scipy.signal.convolve(
        target, SPEECH_FILTER, mode="full", method="fft"
    )
    noise_filt = scipy.signal.convolve(noise, SPEECH_FILTER, mode="full", method="fft")

    # rms of the target after speech weighted filter
    targ_rms = np.sqrt(np.mean(target_filt ** 2))

    # rms of the noise after speech weighted filter
    noise_rms = np.sqrt(np.mean(noise_filt ** 2))
    sw_snr = np.divide(targ_rms, noise_rms)
    return sw_snr


def apply_ramp(x, dur):
    """Apply half cosine ramp into and out of signal

    dur - ramp duration in seconds
    """
    ramp = np.cos(np.linspace(math.pi, 2 * math.pi, int(CONFIG.fs * dur)))
    ramp = (ramp + 1) / 2
    y = np.array(x)
    y[0 : len(ramp)] *= ramp
    y[-len(ramp) :] *= ramp[::-1]

    return y


def cross_correlation_using_fft(x, y):
    f1 = fft(x)
    f2 = fft(np.flipud(y))
    cc = np.real(ifft(f1 * f2))
    return fftshift(cc)


def find_delay(x, y):
    """Find delay between signals x and y.

    shift < 0 means that y starts 'shift' time steps before x
    shift > 0 means that y starts 'shift' time steps after x
    """
    assert len(x) == len(y)
    c = cross_correlation_using_fft(x, y)
    assert len(c) == len(x)
    zero_index = int(len(x) / 2) - 1
    shift = zero_index - np.argmax(c)
    return shift


def create_HA_inputs(infile_names, merged_filename):
    """Create input signal for baseline hearing aids."""

    if (infile_names[0][-5] != "1") or (infile_names[2][-5] != "3"):
        raise Exception("HA-input signal error: channel mismatch!")

    signal_CH1 = read_signal(infile_names[0])
    signal_CH3 = read_signal(infile_names[2])

    merged_signal = np.zeros((len(signal_CH1), 4))
    merged_signal[:, 0] = signal_CH1[
        :, 0
    ]  # channel index 0 = front microphone on the left hearing aid
    merged_signal[:, 1] = signal_CH1[
        :, 1
    ]  # channel index 1 = front microphone on the right hearing aid
    merged_signal[:, 2] = signal_CH3[
        :, 0
    ]  # channel index 2 = rear microphone on the left hearing aid
    merged_signal[:, 3] = signal_CH3[
        :, 1
    ]  # channel index 3 = rear microphone on the right hearing aid

    write_signal(merged_filename, merged_signal, CONFIG.fs, floating_point=True)


def find_delay_impulse(ddf, initial_value=22050):
    """Find binaural delay in signal ddf given initial location of unit impulse, initial_value."""
    pk0 = find_peaks(ddf[:, 0])
    pk1 = find_peaks(ddf[:, 1])
    delay = np.zeros((2, 1))
    if len(pk0[0]) > 0:
        # m = np.max(ddf[pk0[0], 0])
        pkmax0 = np.argmax(ddf[:, 0])
        delay[0] = int(pkmax0 - initial_value)
    else:
        logging.error("Error in selecting peaks.")
    if len(pk1[0]) > 0:
        pkmax1 = np.argmax(ddf[:, 1])
        delay[1] = int(pkmax1 - initial_value)
    else:
        logging.error("Error in selecting peaks.")
    return delay


# def compressor_twochannel(x, Fs, T, R, attackTime, releaseTime):
#     """
#     This function implements a two channel compressor where the
#     same scaling is applied to both channels. This function is based on
#     the standard MATLAB dynamic range compressor [1] and its "Hack
#     Audio" implementation: https://www.hackaudio.com/

#     [1] Giannoulis, Dimitrios, Michael Massberg, and Joshua D. Reiss. "Digital
#     Dynamic Range Compressor Design: A Tutorial and Analysis." Journal of
#     Audio Engineering Society. Vol. 60, Issue 6, 2012, pp. 399-408.


#     Args:
#         x (ndarray): signal.
#         Fs (int): sampling rate.
#         T (int): threshold relative to 0 dBFS.
#         R (int): compression ratio.
#         attackTime (float): attack time in seconds.
#         releaseTime (float): release time in seconds.

#     Returns:
#         ndarray: signal y


#     """
#     N = len(x)
#     channels = np.shape(x)[1]
#     if channels != 2:
#         raise ValueError("Channel mismatch.")
#     y = np.zeros((N, 2))
#     lin_A = np.zeros((N, 1))

#     # Get attack and release times
#     alphaA = np.exp(-np.log(9) / (Fs * attackTime))
#     alphaR = np.exp(-np.log(9) / (Fs * releaseTime))

#     gainSmoothPrev = 0  # Initialise smoothed gain variable

#     # Loop over each sample
#     for n in range(N):
#         # Derive dB of sample x[n]
#         xn_left = np.abs(x[n, 0])
#         xn_right = np.abs(x[n, 1])
#         xn = max(xn_left, xn_right)
#         with np.errstate(divide="ignore"):
#             x_dB = 20 * np.log10(np.divide(xn, 1))

#         # Ensure there are no values of negative infinity
#         if x_dB < -96:
#             x_dB = -96

#         # Check if sample is above threshold T
#         # Static Characteristic - applying hard knee
#         if x_dB > T:
#             gainSC = T + (x_dB - T) / R  # Perform compression
#         else:
#             gainSC = x_dB  # No compression

#         # Compute the gain change as the difference
#         gainChange_dB = gainSC - x_dB

#         # Smooth the gain change using the attack and release times
#         if gainChange_dB < gainSmoothPrev:
#             # Attack
#             gainSmooth = ((1 - alphaA) * gainChange_dB) + (alphaA * gainSmoothPrev)
#         else:
#             # Release
#             gainSmooth = ((1 - alphaR) * gainChange_dB) + (alphaR * gainSmoothPrev)

#         # Translate the gain to the linear domain
#         lin_A[n, 0] = 10 ** (np.divide(gainSmooth, 20))

#         # Apply linear amplitude to input sample
#         y[n, 0] = lin_A[n, 0] * x[n, 0]
#         y[n, 1] = lin_A[n, 0] * x[n, 1]

#         # Update smoothed gain
#         gainSmoothPrev = gainSmooth

#     return y


# def get_rms_blocks(data, fs, block_size):

#     input_data = data.copy()

#     numChannels = input_data.shape[1]
#     numSamples = input_data.shape[0]

#     overlap = 0.75  # Overlap of 75% of the block duration
#     step = 1.0 - overlap  # Step size by percentage

#     T = numSamples / fs  # length of the input in seconds
#     numBlocks = int(np.round(((T - block_size) / (block_size * step))) + 1)
#     block_range = np.arange(0, numBlocks)
#     rms = np.zeros(shape=(numChannels, numBlocks))

#     for ch in range(numChannels):
#         for block in block_range:
#             l = int(
#                 block_size * (block * step) * fs
#             )  # Lower bound of integration (in samples)
#             u = int(
#                 block_size * (block * step + 1) * fs
#             )  # Upper bound of integration (in samples)
#             # Calculate rms
#             with np.errstate(divide="ignore"):
#                 rms[ch, block] = np.sqrt(np.mean(input_data[l:u, ch] ** 2))

#     return rms


# def crest_factor(x):
#     """
#     Calculate crest factor using 35 ms block size.

#     Args:
#         x (array): signal vector

#     Returns:
#         float: CF is crest factor
#         float: CFdB is crest factor in dB

#     """

#     rms_x = np.sqrt(np.mean(x**2))
#     block_size = 0.035
#     peaks = get_rms_blocks(x,CONFIG.fs,block_size)
#     peak = np.max(abs(peaks))

#     CF = peak/rms_x
#     CFdB = 20 * np.log10(CF)

#     return CF, CFdB, peak

# def soft_clip(x, clip_limit=1):
#     """Implementation of a cubic soft-clipper
#     https://ccrma.stanford.edu/~jos/pasp/Cubic_Soft_Clipper.html
#     """
#     deg = 3

#     maxamp = np.max(abs(x))

#     if maxamp < clip_limit:
#         return x
#     elif maxamp >= clip_limit:
#         xclipped = np.where(
#             x > clip_limit,
#             (deg - 1) / deg,
#             np.where(x < -clip_limit, -(deg - 1) / deg, x - x ** deg / deg),
#         )
#         return xclipped


# def asl_P56(x, fs, nbits):
#     """
#     This implements ITU P.56 method B [1]. Translation of Philipos C. Loizou
#     and Yi Hu's asl_P56 function by Rui Cheng
#      @vipchengrui See vipchengrui/MASG

#     Args:
#         x: column vector of floating point speech data
#         fs: sampling frequency
#         nbits: number of bits

#     Returns:
#         asl_ms (float): active speech level mean square energy
#         asl: active factor
#         c0: active speech level threshold

#     References:
#     [1] ITU-T (1993). Objective measurement of active speech level. ITU-T
#         Recommendation P. 56

#     """
#     from scipy.signal import lfilter

#     T = 0.03  # time constant of smoothing, in seconds
#     H = 0.2  # hangover time in seconds
#     M = 15.9  # margin in dB of the difference between threshold and active speech level
#     thres_no = nbits - 1  # number of thresholds, for 16 bit, it's 15
#     eps = 2.2204e-16

#     I = int(np.ceil(fs * H))  # hangover in samples
#     g = np.exp(-1 / (fs * T))  # smoothing factor in enevlop detection
#     c = [pow(2, i) for i in range(-15, thres_no - 16 + 1)]
#     # vector with thresholds from one quantizing level up to
#     # half the maximum code, at a step of 2, in the case of 16bit samples,
#     # from 2^-15 to 0.5
#     a = [0 for i in range(thres_no)]  # activity counter for each level threshold
#     hang = [I for i in range(thres_no)]  # % hangover counter for each level threshold

#     sq = sum(pow(x, 2))  # long-term level square energy of x
#     x_len = len(x)  # length of x

#     # use a 2nd order IIR filter to detect the envelope q
#     x_abs = abs(x)
#     p = lfilter([1 - g], [1, -g], x_abs)
#     q = lfilter([1 - g], [1, -g], p)

#     for k in range(x_len):
#         for j in range(thres_no):
#             if q[k] >= c[j]:
#                 a[j] = a[j] + 1
#                 hang[j] = 0
#             elif hang[j] < I:
#                 a[j] = a[j] + 1
#                 hang[j] = hang[j] + 1
#             else:
#                 break

#     c0 = 0
#     asl = 0
#     asl_ms = 0
#     if a[0] == 0:
#         logging.error("asl_P56 error: a[0] = 0")
#     else:
#         AdB1 = 10 * np.log10(sq / a[0] + eps)

#     CdB1 = 20 * np.log10(c[0] + eps)
#     if AdB1 - CdB1 < M:
#         print("! ! ! ERROR ! ! !")

#     AdB = [0 for i in range(thres_no)]
#     CdB = [0 for i in range(thres_no)]
#     Delta = [0 for i in range(thres_no)]
#     AdB[0] = AdB1
#     CdB[0] = CdB1
#     Delta[0] = AdB1 - CdB1

#     for j in range(1, thres_no):
#         AdB[j] = 10 * np.log10(sq / (a[j] + eps) + eps)
#         CdB[j] = 20 * np.log10(c[j] + eps)

#     for j in range(1, thres_no):
#         if a[j] != 0:
#             Delta[j] = AdB[j] - CdB[j]
#             if Delta[j] <= M:  # M = 15.9
#                 # interpolate to find the asl
#                 asl_ms_log, cl0 = bin_interp(
#                     AdB[j], AdB[j - 1], CdB[j], CdB[j - 1], M, 0.5
#                 )
#                 asl_ms = pow(10, asl_ms_log / 10)
#                 asl = (sq / x_len) / asl_ms
#                 c0 = pow(10, cl0 / 20)
#                 break

#     return asl_ms, asl, c0


# def bin_interp(upcount, lwcount, upthr, lwthr, Margin, tol):
#     """
#     This implements bin_interp in active speech level calculation.
#     Python implementation from MATLAB: Rui Cheng
#     @vipchengrui See vipchengrui/MASG
#     """

#     if tol < 0:
#         tol = -tol

#     # Check if extreme counts are not already the true active value
#     iterno = 1
#     if abs(upcount - upthr - Margin) < tol:
#         asl_ms_log = upcount
#         cc = upthr
#         return asl_ms_log, cc
#     if abs(lwcount - lwthr - Margin) < tol:
#         asl_ms_log = lwcount
#         cc = lwthr
#         return asl_ms_log, cc

#     # Initialize first middle for given (initial) bounds
#     midcount = (upcount + lwcount) / 2.0
#     midthr = (upthr + lwthr) / 2.0
#     # Repeats loop until `diff' falls inside the tolerance (-tol<=diff<=tol)
#     while 1:
#         diff = midcount - midthr - Margin
#         if abs(diff) <= tol:
#             break
#         # if tolerance is not met up to 20 iteractions, then relax the tolerance by 10%
#         iterno = iterno + 1
#         if iterno > 20:
#             tol = tol * 1.1
#         if diff > tol:  # then new bounds are ...
#             midcount = (upcount + midcount) / 2.0
#             # upper and middle activities
#             midthr = (upthr + midthr) / 2.0
#             # ... and thresholds
#         elif diff < -tol:  # then new bounds are ...
#             midcount = (midcount + lwcount) / 2.0
#             # middle and lower activities
#             midthr = (midthr + lwthr) / 2.0
#             # ... and thresholds

#     # Since the tolerance has been satisfied, midcount is selected
#     # as the interpolated value with a tol [dB] tolerance.
#     asl_ms_log = midcount
#     cc = midthr

#     return asl_ms_log, cc
