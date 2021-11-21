def stft(x, win_size, fft_size):
    """Short-time Fourier transform based on MBSTOI MATLAB code.

    Args:
        x (ndarray): input signal
        win_size (int): N, the size of the window and the signal frames
        fft_size (int): Nfft, the size of the fft in samples (zero-padding or not)

    Returns
        ndarray: 2D complex array, the short-time Fourier transform of x.

    """
    import numpy as np

    hop = int(win_size / 2)
    frames = list(range(0, len(x) - win_size, hop))
    stft_out = np.zeros((len(frames), fft_size), dtype=np.complex128)

    w = np.hanning(win_size + 2)[1:-1]
    x = x.flatten()

    for i in range(len(frames)):
        ii = list(range(frames[i], (frames[i] + win_size), 1))
        stft_out[i, :] = np.fft.fft(x[ii] * w, n=fft_size, axis=0)

    return stft_out
