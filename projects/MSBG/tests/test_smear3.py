import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# from MSBG import smear3, utils


# Test that python smear3 code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 5e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    ["smear3-137292960ecc.mat", "smear3-5653f686b734.mat", "smear3-fde015f27c78.mat"],
)
def test_smear3(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    outbuffer = MSBG.smear3(data["fsmear"], data["inbuffer"])
    npt.assert_allclose(outbuffer, data["outbuffer"], rtol=RTOL)
    print(utils.hash_numpy(outbuffer), file=regtest)
