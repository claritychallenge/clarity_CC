import scipy.io
import os
import numpy as np
import numpy.testing as npt
import pytest

import MBSTOI
import tests.utils as utils

# Test that python thirdoct code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    ["thirdoct-041e968faa07.mat"],
)
def test_thirdoct(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    fs = int(data["fs"])
    N_fft = int(data["N_fft"])
    numBands = int(data["numBands"])
    mn = int(data["mn"])
    obm, cf, fids, freq_low, freq_high = MBSTOI.thirdoct(fs, N_fft, numBands, mn)

    npt.assert_allclose(obm, data["A"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(cf, data["cf"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(fids, data["fids"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(obm), file=regtest)
