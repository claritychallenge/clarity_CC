from scipy.signal import convolve, lfilter
import numpy as np
import numpy.testing as npt


def test_fftfilt():
    """Test output of fftfilt matches output of filter."""

    x = np.random.random(10000000)

    bshrt = np.random.random(20)
    sfs = convolve(bshrt, x, mode="full")
    sfs = sfs[0 : len(x)]
    sls = lfilter(bshrt, 1, x)
    npt.assert_allclose(sfs, sls)

    blong = np.random.random(2000)
    sfl = convolve(blong, x, mode="full", method="fft")
    sfl = sfl[0 : len(x)]
    sll = lfilter(blong, 1, x)
    npt.assert_allclose(sfl, sll)
