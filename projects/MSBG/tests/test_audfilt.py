import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python audfilt code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data


@pytest.mark.parametrize(
    "filename",
    [
        "audfilt-716e9ddb5f34.mat",
        "audfilt-71e7fe27cd11.mat",
        "audfilt-e0f54fb68ffb.mat",
        "audfilt-fae76b3b9a17.mat",
        "audfilt-c8a58791f8f2.mat",
    ],
)
def test_audfilt(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    audfiltered = MSBG.audfilt(data["rl"], data["ru"], data["sampfreq"], data["asize"])
    npt.assert_allclose(audfiltered, data["filter"])
    print(utils.hash_numpy(audfiltered), file=regtest)
