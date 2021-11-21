import logging
import numpy as np
import math
import MSBG


WIN_SECS = 0.01  # Window length in seconds


def generate_key_percent(sig, thr_dB, winlen, percent_to_track=None):
    """Generate key percent.

    Locates frames above some energy threshold or tracks a certain percentage
    of frames. To track a certain percentage of frames in order to get measure
    of rms, adaptively sets threshold after looking at histogram of whole recording

    Args:
        sig (ndarray): The signal to analyse
        thr_dB (float): fixed energy threshold (dB)
        winlen (int): length of window in samples
        percent_to_track (float, optional): Track a percentage of frames (default: {None})

    Raises:
        ValueError: percent_to_track is set too high

    Returns:
        (ndarray, float) -- "key" and rms threshold
            The key array of indices of samples used in rms calculation,
            and the threshold used to get a more accurate rms calculation

    """
    winlen = int(winlen)
    sig = sig.flatten()
    if winlen != math.floor(winlen):  # whoops on fractional indexing: 7-March 2002
        winlen = math.floor(winlen)
        logging.warning(f"Window length must be integer: now {winlen}")

    siglen = len(sig)

    expected = thr_dB
    # new Dec 2003. Possibly track percentage of frames rather than fixed threshold
    if percent_to_track is not None:
        logging.info(f"tracking {percent_to_track} percentage of frames")
    else:
        logging.info("tracking fixed threshold")

    # put floor into histogram distribution
    non_zero = np.power(10, (expected - 30) / 10)

    nframes = -1
    totframes = math.floor(siglen / winlen)
    every_dB = np.zeros(totframes)

    for ix in np.arange(0, winlen * totframes - 1, winlen):
        nframes += 1
        this_sum = np.sum(np.power(sig[ix : (ix + winlen)].astype("float"), 2))
        every_dB[nframes] = 10 * np.log10(non_zero + this_sum / winlen)
    nframes += 1

    # from now on save only those analysed
    every_dB = every_dB[:nframes]

    # Bec 2003, was 100 to give about a 0.5 dB quantising of levels
    n_bins, levels = np.histogram(every_dB, 140)
    if percent_to_track is not None:
        # min number of bins to use
        inactive_bins = (100 - percent_to_track) * nframes / 100
        n_levels = len(levels)
        inactive_ix = 0
        ix_count = 0
        for ix in np.arange(0, n_levels, 1):
            inactive_ix = inactive_ix + n_bins[ix]
            if inactive_ix > inactive_bins:
                break
            else:
                ix_count += 1
        if ix == 1:
            logging.warning("Counted every bin.........")
        elif ix == n_levels:
            raise ValueError("Generate_key_percent: no levels to count")
        expected = levels[max(1, ix_count)]

    # set new threshold conservatively to include more bins than desired
    used_thr_dB = expected

    # histogram should produce a two-peaked curve: thresh should be set in valley
    # between the two peaks, and set threshold a bit above that,
    # as it heads for main peak
    frame_index = np.nonzero(every_dB >= expected)[0]
    valid_frames = len(frame_index)
    key = np.zeros((1, valid_frames * winlen))[0]

    # convert frame numbers into indices for sig
    for ix in np.arange(valid_frames):
        meas_span = np.arange(
            (frame_index[ix] * winlen), (frame_index[ix] + 1) * winlen
        )
        key_span = np.arange(((ix) * winlen), (ix + 1) * winlen, 1)
        key[key_span] = meas_span
        key = key.flatten()

    return key, used_thr_dB


def measure_rms(signal, fs, dB_rel_rms, percent_to_track=None):
    """Measure rms.

    A sophisticated method of measuring RMS in a file. It splits the signal up into
    short windows, performs  a histogram of levels, calculates an approximate RMS,
    and then uses that RMS to calculate a threshold level in the histogram and then
    re-measures the RMS only using those durations whose individual RMS exceed that
    threshold.

    Args:
        signal (ndarray): the signal of which to measure the rms
        fs (float): sampling frequency
        dB_rel_rms (float): threshold for frames to track
        percent_to_track (float, optional): track percentage of frames,
            rather than threshold (default: {None})

    Returns:
        (tuple): tuple containing

        - rms (float): overall calculated rms (linear)
        - key (ndarray): "key" array of indices of samples used in rms calculation
        - rel_dB_thresh (float): fixed threshold value of -12 dB
        - active (float): proportion of values used in rms calculation

    """
    fs = int(fs)
    # first RMS is of all signal.
    first_stage_rms = np.sqrt(np.sum(np.power(signal, 2) / len(signal)))
    # use this RMS to generate key threshold to get more accurate RMS
    key_thr_dB = max(20 * np.log10(first_stage_rms) + dB_rel_rms, -80)

    # move key_thr_dB to account for noise less peakier than signal
    key, used_thr_dB = MSBG.generate_key_percent(
        signal, key_thr_dB, round(WIN_SECS * fs), percent_to_track=percent_to_track
    )

    idx = key.astype(int)  # move into generate_key_percent
    # statistic to be reported later, BUT save for later
    # (for independent==1 loop where it sets a target for rms measure)
    active = 100 * len(key) / len(signal)
    rms = np.sqrt(np.sum(np.power(signal[idx], 2)) / len(key))
    rel_dB_thresh = used_thr_dB - 20 * np.log10(rms)

    return rms, idx, rel_dB_thresh, active
