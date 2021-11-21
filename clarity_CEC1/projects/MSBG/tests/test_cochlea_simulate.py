import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python cochlea_simulate code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-07  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "cochlea_simulate_NOTHING-ce40fb2e6cf4.mat",
        "cochlea_simulate_MILD-d4d286ffac7c.mat",
        "cochlea_simulate_MODERATE-0fd966e78afe.mat",
        "cochlea_simulate_SEVERE-cb2b84eb3d9c.mat",
    ],
)
def test_cochlea_simulate(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename)
    audiogram = MSBG.Audiogram(
        cfs=data["audiogram_cfs"][0], levels=data["audiogram"][0]
    )
    cochlea = MSBG.Cochlea(audiogram)
    coch_sig_out = cochlea.simulate(data["coch_sig"][0], data["equiv0dBfileSPL"][0])

    assert coch_sig_out.shape[0] == data["coch_sig_out"].shape[1]
    npt.assert_allclose(coch_sig_out, data["coch_sig_out"][0, :], atol=ATOL, rtol=RTOL)
    print(utils.hash_numpy(coch_sig_out), file=regtest)
