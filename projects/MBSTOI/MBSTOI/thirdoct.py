def thirdoct(fs, nfft, num_bands, min_freq):
    """Returns the 1/3 octave band matrix and its center frequencies
    Based on mpariente/pystoi

    Args:
        fs (int): sampling rate
        nfft (int): FFT size
        num_bands (int): number of one-third octave bands
        min_freq (int): center frequency of the lowest one-third octave band

    Returns:
        obm (ndarray): octave band matrix
        cf (ndarray): center frequencies
        fids (ndarray): indices of frequency band edges

    """
    import numpy as np

    f = np.linspace(0, fs, nfft + 1)
    f = f[: int(nfft / 2) + 1]
    k = np.array(range(num_bands)).astype(float)
    cf = np.power(2.0 ** (1.0 / 3), k) * min_freq
    freq_low = min_freq * np.power(2.0, (2 * k - 1) / 6)
    freq_high = min_freq * np.power(2.0, (2 * k + 1) / 6)
    obm = np.zeros((num_bands, len(f)))  # a verifier
    fids = np.zeros((num_bands, 2))

    for i in range(len(cf)):
        # Match 1/3 oct band freq with fft frequency bin
        f_bin = np.argmin(np.square(f - freq_low[i]))
        freq_low[i] = f[f_bin]
        fl_ii = f_bin
        f_bin = np.argmin(np.square(f - freq_high[i]))
        freq_high[i] = f[f_bin]
        fh_ii = f_bin
        # Assign to the octave band matrix
        obm[i, fl_ii:fh_ii] = 1
        fids[i, :] = [fl_ii + 1, fh_ii]

    cf = cf[np.newaxis, :]

    return obm, cf, fids, freq_low, freq_high
