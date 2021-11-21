import scipy.io
import os
import numpy as np
import numpy.testing as npt
import pytest

import GHA
import tests.utils as utils

# Test that python multifit_apply_noisegate code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "multifit_apply_noisegate-0f9d47e6d77a.mat",
        "multifit_apply_noisegate-3bd1e25ab820.mat",
        "multifit_apply_noisegate-7df086974a0a.mat",
    ],
)
def test_multifit_apply_noisegate(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)

    noisegatelevel = np.transpose(
        np.tile(np.array(data["sGt"].item()[1][0][0][0][0][0][0]), (2, 1))
    )
    noisegateslope = np.transpose(
        np.tile(np.array(data["sGt"].item()[1][0][0][0][0][0][1]), (2, 1))
    )

    l = data["sGt"]["l"].item()
    sGt = np.zeros((np.shape(l)[0], np.shape(l)[1], 2))
    sGt[:, :, 0] = l
    sGt[:, :, 1] = data["sGt"]["r"].item()

    output = GHA.multifit_apply_noisegate(
        sGt,
        data["sGt"]["frequencies"][0][0],
        data["sGt"]["levels"][0][0][0],
        noisegatelevel,
        noisegateslope,
    )
    npt.assert_allclose(output["sGt"], sGt, atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(output["sGt"]), file=regtest)
