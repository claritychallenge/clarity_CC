import scipy.io
import os
import numpy.testing as npt
import numpy as np
import pytest

import GHA
import tests.utils as utils

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "sGt20201130.mat",
    ],
)
def test_gainrule_camfit_compr2(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)

    sFitModel = {}
    sFitModel["frequencies"] = np.array(
        [177.0, 297.0, 500.0, 841.0, 1414.0, 2378.0, 3999.99976, 6726.99951, 11314.0]
    )
    sFitModel["edge_frequencies"] = np.array(
        [
            9.99999994e-09,
            2.29279297e02,
            3.85356964e02,
            6.48459717e02,
            1.09049243e03,
            1.83370972e03,
            3.08415283e03,
            5.18729199e03,
            8.72406250e03,
            1.00000010e07,
        ]
    )
    sFitModel["levels"] = np.linspace(-10, 110, 121)
    l = np.array([45, 45, 35, 45, 60, 65, 70, 65])
    r = np.array([40, 40, 45, 45, 60, 65, 80, 80])
    audf = np.array([250, 500, 1000, 2000, 3000, 4000, 6000, 8000])
    noisegatelevels = np.array([38, 38, 36, 37, 32, 26, 23, 22, 8])
    noisegateslope = 0
    level = 0  # variable

    audiogram = GHA.Audiogram(levels_l=l, levels_r=r, cfs=audf)
    sGt = GHA.gainrule_camfit_compr(
        audiogram, sFitModel, noisegatelevels, noisegateslope, level=level
    )
    newl = sGt["sGt"][:, :, 0]
    newr = sGt["sGt"][:, :, 1]

    npt.assert_allclose(newl, data["l"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(newr, data["r"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(newl), file=regtest)