import scipy.io
import os
import numpy as np
import numpy.testing as npt
import pytest

import MBSTOI
import tests.utils as utils

# Test that python ec code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-03  # error tolerance for allclose check
ATOL = 1e-02  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "mbstoi_annot-e02e822c0170.mat",
        "mbstoi_annot-01f9dd82a581.mat",
        "mbstoi_annot-aebe8d462d60.mat",
        "mbstoi_annot-167fe272bb34.mat",
    ],
)
def test_ec(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)

    xl_hat = data["xl_hat"]
    N = data["N"]
    J = data["J"]
    d = np.zeros((J, np.shape(xl_hat)[1] - N + 1))
    p_ec_max = np.zeros((J, np.shape(xl_hat)[1] - N + 1))

    d1, p_ec_max1 = MBSTOI.ec(
        xl_hat,
        data["xr_hat"],
        data["yl_hat"],
        data["yr_hat"],
        J,
        N,
        data["fids"],
        data["cf"],
        data["taus"],
        data["ntaus"],
        data["gammas"],
        data["ngammas"],
        d,
        p_ec_max,
        data["sigma_epsilon"],
        data["sigma_delta"],
    )

    npt.assert_allclose(d1, data["d"], atol=ATOL, rtol=RTOL)
    npt.assert_allclose(p_ec_max1, data["p_ec_max"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(d1), file=regtest)
