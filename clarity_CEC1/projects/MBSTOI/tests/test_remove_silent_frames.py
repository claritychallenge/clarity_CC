import scipy.io
import os
import numpy.testing as npt
import pytest

import MBSTOI
import tests.utils as utils

# Test that python remove_silent_frames code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-05  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    ["remove_silent_frames-8f736607df9b.mat", "remove_silent_frames-fe8ea6b27505.mat"],
)
def test_remove_silent_frames(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    xl_sil, xr_sil, yl_sil, yr_sil = MBSTOI.remove_silent_frames(
        data["xl"],
        data["xr"],
        data["yl"],
        data["yr"],
        data["range"],
        data["N"],
        data["K"],
    )

    npt.assert_allclose(xl_sil, data["xl_sil"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(xr_sil, data["xr_sil"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(yl_sil, data["yl_sil"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(xr_sil, data["xr_sil"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(xl_sil), file=regtest)
