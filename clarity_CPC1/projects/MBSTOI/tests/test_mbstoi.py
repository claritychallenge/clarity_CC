import scipy.io
import os
import numpy as np
import numpy.testing as npt
import pytest

import MBSTOI
import tests.utils as utils

# Test that python mbstoi code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 5e-03  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "mbstoi_annot-8b4a5f419dfd.mat",
        "mbstoi_annot-7a958369ccc8.mat",
        "mbstoi_annot-95f6716ff4f6.mat",
        "mbstoi_annot-0006b088882d.mat",
        "mbstoi_annot-9ff42bee0a8e.mat",
        "mbstoi_annot-e3a652cdd0d9.mat",
        "mbstoi_annot-01f9dd82a581.mat",
        "mbstoi_annot-aebe8d462d60.mat",
        "mbstoi_annot-167fe272bb34.mat",
    ],
)
def test_mbstoi(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)

    sii = MBSTOI.mbstoi(data["xl"], data["xr"], data["yl"], data["yr"])
    npt.assert_allclose(sii, data["sii"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(sii), file=regtest)
