import scipy.io
import os
import numpy.testing as npt
import numpy as np
import pytest

import GHA
import tests.utils as utils

# Test that python gainrule_camfit_compr code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "gainrule_camfit_compr-6da830cc8f68.mat",
        "gainrule_camfit_compr-6e65c87ee62b.mat",
        "gainrule_camfit_compr-1618e266e222.mat",
        "gainrule_camfit_compr-16767de02e26.mat",
        "gainrule_camfit_compr-0429235d484f.mat",
        "gainrule_camfit_compr-d7f97bb4f715.mat",
    ],
)
def test_gainrule_camfit_compr(filename, regtest):
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

    sFitModel = dict()
    sFitModel["frequencies"] = data["sFitmodel"]["frequencies"][0][0][0]
    sFitModel["levels"] = data["sFitmodel"]["levels"][0][0][0]
    sFitModel["edge_frequencies"] = data["sFitmodel"]["edge_frequencies"][0][0][0]
    noisegatelevels = 45
    noisegateslope = 1

    sGt = GHA.gainrule_camfit_compr(
        audiogram, sFitModel, noisegatelevels, noisegateslope, level=110
    )
    newl = sGt["sGt"][:, :, 0]
    newr = sGt["sGt"][:, :, 1]
    l = data["sGt"]["l"][0][0]
    r = data["sGt"]["r"][0][0]
    npt.assert_allclose(newl, l, atol=ATOL, rtol=RTOL)
    npt.assert_allclose(newr, r, atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(newl), file=regtest)
