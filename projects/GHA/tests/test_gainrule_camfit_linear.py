import scipy.io
import os
import numpy.testing as npt
import numpy as np
import pytest

import GHA
import tests.utils as utils

# Test that python gainrule_camfit_linear code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "gainrule_camfit_linear-2e01a2344b92.mat",
        "gainrule_camfit_linear-08af30d79d9a.mat",
        "gainrule_camfit_linear-9a7f17c8259b.mat",
        "gainrule_camfit_linear-5779e9beb522.mat",
        "gainrule_camfit_linear-c3b5e87a9931.mat",
        "gainrule_camfit_linear-fa06a5c60ce3.mat",
    ],
)
def test_gainrule_camfit_linear(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    sAud = data["sAud"]
    l = sAud["l"].item()
    r = sAud["r"].item()
    l = sAud["l"]
    audf = np.squeeze(l[0][0][0][0][0][0][0][0][0][0][0])
    # Raise value error if fcheck does not match audf
    l = np.squeeze(l[0][0][0][0][0][0][0][0][0][0][1])
    r = sAud["r"]
    r = np.squeeze(r[0][0][0][0][0][0][0][0][0][0][1])
    audiogram = GHA.Audiogram(levels_l=l, levels_r=r, cfs=audf)
    noisegatelevels = 45
    noisegateslope = 1

    sGt = GHA.gainrule_camfit_linear(
        audiogram, data["sFitmodel"], noisegatelevels, noisegateslope
    )
    newl = sGt["sGt"][:, :, 0]
    newr = sGt["sGt"][:, :, 1]
    l = data["sGt"]["l"][0][0]
    r = data["sGt"]["r"][0][0]
    npt.assert_allclose(newl, l, atol=ATOL, rtol=RTOL)
    npt.assert_allclose(newr, r, atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(newl), file=regtest)
