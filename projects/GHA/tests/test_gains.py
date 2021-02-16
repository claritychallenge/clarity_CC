import scipy.io
import os
import numpy.testing as npt
import pytest

import GHA
import tests.utils as utils

# Test that python gains code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "gains-2a1a209b7395.mat",
        "gains-3bb0b90ed39b.mat",
        "gains-060d44926c1e.mat",
        "gains-652ea99c4a63.mat",
        "gains-768ddf8136fb.mat",
        "gains-9546d3a7639f.mat",
        "gains-a5c4ac2674ef.mat",
        "gains-a50ed2cc9529.mat",
        "gains-df582b9c80a4.mat",
    ],
)
def test_gains(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    g = GHA.gains(
        data["compr_thr_inputs"],
        data["compr_thr_gains"],
        data["compression_ratios"],
        data["levels"],
    )
    npt.assert_allclose(g, data["g"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(g), file=regtest)
