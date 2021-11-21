import numpy as np
from scipy import signal
import MSBG

# from MSBG.scipy_matlab import firwin2
from MSBG.firwin2 import firwin2

"""
Ideal pre-emphasis (starts off as SII 1997), then rescaled for Moore et al. 2008
NB last two are -15dB/oct before rescaling below
(Moore et al 2008 E&H paper suggests that shape would be better as -7.5
dB/oct, at least up to 8, and -13 dB/oct above there.)
"""
HZ = np.array(
    [0, 100, 200, 450, 550, 707, 1000, 1414, 2000, 2828, 4000, 5656, 8000, 16e3, 32e3]
)
EMPHASIS = np.array(
    [0, 0.0, 0.0, 0, -0.5, -4.5, -9.0, -13.5, -18, -22.5, -27, -31.5, -36.0, -51, -66]
) * (7.5 / 9)


def gen_tone(freq, duration, fs=MSBG.MASTER_FS, level=0):
    return (
        1.4142
        * np.power(10, (0.05 * level))
        * np.sin(2 * np.pi * freq * np.arange(1, duration * fs + 1) / fs)
    )


def gen_eh2008_speech_noise(duration, fs=MSBG.MASTER_FS, level=None, supplied_b=None):
    """Generate speech shaped noise.

    Start with white noise and re-shape to ideal SII, ie flat to 500 Hz, and
    sloping -9db/oct beyond that.

    Slightly different shape from SII stylised same as
    EarHEar 2008 paper, Moore et al.

    Args:
        duration (int): Duration of signal in seconds
        fs (int): Sampling rate
        level (float, optional): Normalise to level dB if present
        supplied_b (ndarray, optional): High-pass filter
            (default: uses built-in pre-emphasis filter)

    Returns:
        ndarray: Noise signal

    """
    duration = int(duration)
    fs = int(fs)
    n_samples = duration * fs

    # this rescales so that we get -7.5 dB/oct up to 8kHz, and -13 dB/oct above that
    norm_freq = HZ / (fs / 2)
    last_f_idx = np.max(np.where(norm_freq < 1))
    norm_freq = np.append(norm_freq[0 : last_f_idx + 1], 1)

    # -9 dB/oct constant slope
    emph_nyq = EMPHASIS[last_f_idx] + 9 * np.log10(norm_freq[last_f_idx]) / np.log10(2)
    norm_emph = np.append(EMPHASIS[0 : last_f_idx + 1], emph_nyq)
    m = np.exp(np.log(10) * norm_emph / 20)

    # Create type II filter with 10 msec window and even number of taps
    n_taps = int(2 * np.ceil(10 * (fs / 2000))) + 1
    b = (
        supplied_b
        if supplied_b is not None
        else firwin2(n_taps, norm_freq, m, window="hamming", antisymmetric=False)
    )

    # white noise, 0 DC
    nburst = np.random.random((1, n_samples + len(b))) - 0.5

    # remove low-freq noise that may bias RMS estimate, -33dB at 50 Hz
    eh2008_nse1 = signal.lfilter(b, 1, nburst)

    # high-pass filter to remove low freqs (will be 2-pass with filtfilt)
    hpfB, hpfA = signal.ellip(3, 0.1, 50, 100 / (fs / 2), "high")
    padlen = 3 * (max(len(hpfA), len(hpfB)) - 1)
    eh2008_nse = signal.filtfilt(hpfB, hpfA, eh2008_nse1, padlen=padlen).flatten()

    # this introduces a delay so remove it, ie time-ADVANCE audio
    # compensating shift to time-align all filter outputs
    dly_shift = int(np.floor(len(b) / 2))
    valid_len = int(np.size(eh2008_nse) - dly_shift)  # _advance_ filter outputs
    # time advance
    eh2008_nse[0:valid_len] = eh2008_nse[dly_shift:]
    eh2008_nse = eh2008_nse[0:n_samples]

    if level is not None:
        eh2008_nse = (
            eh2008_nse
            * np.power(10, 0.05 * level)
            / np.sqrt(np.sum(np.power(eh2008_nse, 2)) / len(eh2008_nse))
        )

    return eh2008_nse
