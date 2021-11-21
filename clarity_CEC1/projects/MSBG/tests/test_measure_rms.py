import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python measure_rms code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 3e-07  # error tolerance for allclose check


@pytest.mark.parametrize("filename", ["measure_rms-28ef8a718450.mat"])
def test_measure_rms(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    rms, key, rel_dB_thresh, active = MSBG.measure_rms(
        data["signal"], data["fs"], data["dB_rel_rms"]
    )
    npt.assert_allclose(rms, data["rms"], rtol=RTOL)
    npt.assert_allclose(key, data["key"] - 1, rtol=RTOL)  # index so subtract 1 OK
    npt.assert_allclose(rel_dB_thresh, data["rel_dB_thresh"], rtol=RTOL)
    print(rms, file=regtest)
    print(utils.hash_numpy(key), file=regtest)
    print(rel_dB_thresh, file=regtest)
