import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python generate_key_percent code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 3e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    ["generate_key_percent-eb85c6dee44a.mat"],
)
def test_generate_key_percent(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    key, used_thr_dB = MSBG.generate_key_percent(
        data["sig"], data["thr_dB"], data["winlen"]
    )
    npt.assert_allclose(key, data["key"] - 1, rtol=RTOL)
    npt.assert_allclose(used_thr_dB, data["used_thr_dB"], rtol=RTOL)
    print(utils.hash_numpy(key), file=regtest)
    print(used_thr_dB, file=regtest)
