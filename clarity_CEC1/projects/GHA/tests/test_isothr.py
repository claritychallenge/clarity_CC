import scipy.io
import os
import numpy.testing as npt
import pytest

import GHA
import tests.utils as utils

# Test that python isothr code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "isothr-477de90197eb.mat",
    ],
)
def test_isothr(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    vIsoThrDB = GHA.isothr(data["vsDesF"])
    npt.assert_allclose(vIsoThrDB, data["vIsoThrDB"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(vIsoThrDB), file=regtest)
