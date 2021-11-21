import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python makesmearmat3 code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data


@pytest.mark.parametrize(
    "filename",
    [
        "makesmearmat3-2ae9e0460ba5.mat",
        "makesmearmat3-5e7107c37e01.mat",
        "makesmearmat3-ee05ec106111.mat",
        "makesmearmat3-9cbca82fa910.mat",
    ],
)
def test_makesmearmat3(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    fsmear = MSBG.make_smear_mat3(data["rl"], data["ru"], data["fs"])
    npt.assert_allclose(fsmear, data["fsmear"], rtol=1e-9, atol=1e-11)
    print(utils.hash_numpy(fsmear), file=regtest)
