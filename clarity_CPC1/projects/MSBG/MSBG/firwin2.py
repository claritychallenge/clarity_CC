import math
import numpy as np
import scipy.signal


def firwin2(n, f, a, window=None, antisymmetric=None):
    """FIR filter design using the window method.

    Partial implementation of scipy firwin2 but using our own MATLAB-derived fir2.

    Args:
        n (int): The number of taps in the FIR filter.
        f (ndarray): The frequency sampling points. 0.0 to 1.0 with 1.0 being Nyquist.
        a (ndarray): The filter gains at the frequency sampling points.
        window (string or (string, float), optional): See scipy.firwin2 (default: (None))
        antisymmetric (bool, optional): Unused but present to main compatability with scipy firwin2.

    Returns:
        ndarray:  The filter coefficients of the FIR filter, as a 1-D array of length n.

    """
    window_shape = None
    if type(window) == tuple:
        window_type, window_param = window if window is not None else (None, 0)
    else:
        window_type = window

    order = n - 1

    if window_type == "kaiser":
        window_shape = scipy.signal.kaiser(n, window_param)

    if window_shape is None:
        b, _ = fir2(order, f, a)
    else:
        b, _ = fir2(order, f, a, window_shape)

    return b


def fir2(nn, ff, aa, npt=None):
    """FIR arbitrary shape filter design using the frequency sampling method.

    Translation of MATLAB fir2.

    Args:
        nn (int): Order
        ff (ndarray): Frequency breakpoints (0 < F < 1) where 1 is Nyquist rate.
                        First and last elements must be 0 and 1 respectively
        aa (ndarray): Magnitude breakpoints
        npt (int, optional): Number of points for freq response interpolation
            (default: max (smallest power of 2 greater than nn, 512))

    Returns:
        ndarray: nn + 1 filter coefficients

    """
    # Work with filter length instead of filter order
    nn += 1

    if npt is None:
        npt = 2.0 ** np.ceil(math.log(nn) / math.log(2)) if nn >= 1024 else 512
        wind = scipy.signal.hamming(nn)
    else:
        wind = npt
        npt = 2.0 ** np.ceil(math.log(nn) / math.log(2)) if nn >= 1024 else 512
    lap = np.fix(npt / 25)

    nbrk = max(len(ff), len(aa))

    ff[0] = 0
    ff[nbrk - 1] = 1

    H = np.zeros(npt + 1)
    nint = nbrk - 1
    df = np.diff(ff, n=1)

    npt += 1
    nb = 0
    H[0] = aa[0]

    for i in np.arange(nint):
        if df[i] == 0:
            nb = int(np.ceil(nb - lap / 2))
            ne = nb + lap - 1
        else:
            ne = int(np.fix(ff[i + 1] * npt)) - 1

        j = np.arange(nb, ne + 1)
        inc = 0 if nb == ne else (j - nb) / (ne - nb)
        H[nb : (ne + 1)] = inc * aa[i + 1] + (1 - inc) * aa[i]
        nb = ne + 1

    dt = 0.5 * (nn - 1)
    rad = -dt * 1j * math.pi * np.arange(0, npt) / (npt - 1)
    H = H * np.exp(rad)

    H = np.concatenate((H, H[npt - 2 : 0 : -1].conj()))
    ht = np.real(np.fft.ifft(H))

    b = ht[0:nn] * wind

    return b, 1


if __name__ == "__main__":
    [b, a] = fir2(15, [0.0, 0.1, 0.5, 1.0], [1.0, 1.0, 0.0, 0.0])
    print(a, b)

    window = scipy.signal.hamming(16)
    [b, a] = fir2(15, [0.0, 0.1, 0.5, 1.0], [1.0, 1.0, 0.0, 0.0], window)
    print(a, b)
