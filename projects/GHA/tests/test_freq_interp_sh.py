import scipy.io
import os
import numpy.testing as npt
import pytest

import GHA
import tests.utils as utils

# Test that python freq_interp_sh code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "freq_interp_sh-0f57406abc9b.mat",
        "freq_interp_sh-2ac43169948c.mat",
        "freq_interp_sh-2de494696ba1.mat",
        "freq_interp_sh-4c7002ab30fe.mat",
        "freq_interp_sh-9f24b084a3fa.mat",
        "freq_interp_sh-0273019f0bc1.mat",
        "freq_interp_sh-a24e883a5cfb.mat",
        "freq_interp_sh-f2ef2e3378d2.mat",
    ],
)
def test_freq_interp_sh(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    y = GHA.freq_interp_sh(data["f_in"], data["y_in"], data["f"])
    npt.assert_allclose(y, data["y"], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(y), file=regtest)
