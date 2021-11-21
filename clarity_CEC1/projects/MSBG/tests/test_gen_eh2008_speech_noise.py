import scipy.io
import os
import numpy.testing as npt
import numpy as np
import pytest

import MSBG
import tests.utils as utils

# Test that python gen_eh2008_speech_noise code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

# Error tolerances
ATOL = 2e-06
RTOL = 1e-07

MIN_SDR = 60  # Minimum allowable SDR between Python and MATLAB reference


@pytest.mark.parametrize(
    "filename",
    ["gen_eh2008_speech_noise-bfdbc377d595.mat"],
)
def test_gen_eh2008_speech_noise(filename):
    np.random.seed(0)
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    eh2008_nse = MSBG.gen_eh2008_speech_noise(data["durn"], data["fs"])
    assert len(eh2008_nse) == len(data["eh2008_nse"])

    sdr = utils.compute_siSDR(eh2008_nse, data["eh2008_nse"])
    assert sdr > MIN_SDR

    npt.assert_allclose(eh2008_nse, data["eh2008_nse"], atol=ATOL, rtol=RTOL)


@pytest.mark.parametrize(
    "filename",
    ["gen_eh2008_speech_noise-bfdbc377d595.mat"],
)
def test_gen_eh2008_speech_noise_supplied_b(filename, regtest):
    np.random.seed(0)
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    # Use filter computed by MATLAB.
    eh2008_nse = MSBG.gen_eh2008_speech_noise(
        data["durn"], data["fs"], supplied_b=data["b"]
    )
    assert len(eh2008_nse) == len(data["eh2008_nse"])

    sdr = utils.compute_siSDR(eh2008_nse, data["eh2008_nse"])
    assert sdr > MIN_SDR

    npt.assert_allclose(eh2008_nse, data["eh2008_nse"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(eh2008_nse), file=regtest)
