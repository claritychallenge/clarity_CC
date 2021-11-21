import scipy.io
import os
import numpy.testing as npt
import pytest

import MBSTOI
import tests.utils as utils

# Test that python stft code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "stdft-0b2a1a6268af.mat",
        "stdft-5c02cbc7b568.mat",
        "stdft-4027a90186e3.mat",
        "stdft-c4a94cdd947b.mat",
        "stdft-c14737fc8be8.mat",
        "stdft-ec85a7ed84da.mat",
    ],
)
def test_stft(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    win_size = int(data["N"])
    fft_size = int(data["N_fft"])

    stft_out = MBSTOI.stft(data["x"], win_size, fft_size)

    npt.assert_allclose(stft_out, data["x_stdft"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(stft_out), file=regtest)
