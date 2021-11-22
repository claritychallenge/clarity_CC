import scipy.io
import os
import numpy.testing as npt
import pytest

import MSBG
import tests.utils as utils

# Test that python src_to_cochlea_filt code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

RTOL = 3e-07  # error tolerance for allclose check
ATOL = 1e-10

MIN_SDR = 60  # Minimum allowable SDR between Python and MATLAB reference


@pytest.mark.parametrize(
    "filename",
    [
        "src_to_cochlea_filt-01f090cb26f6.mat",
        "src_to_cochlea_filt-3eb1eeba730a.mat",
        "src_to_cochlea_filt-4cf1eafbbdcf.mat",
        "src_to_cochlea_filt-9b6221a7a0d0.mat",
        "src_to_cochlea_filt-fed32f8d62fb.mat",
        "src_to_cochlea_filt-2089dc2ead8d.mat",
    ],
)
def test_src_to_cochlea_filt(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=True)
    backward = data["direction"] == -1
    src_correction = MSBG.Ear.get_src_correction(data["src_posn"])
    op_sig = MSBG.Ear.src_to_cochlea_filt(
        data["ip_sig"], src_correction, data["fs"], backward=backward
    )

    sdr = utils.compute_siSDR(op_sig, data["op_sig"])
    assert sdr > MIN_SDR

    npt.assert_allclose(op_sig, data["op_sig"], atol=ATOL, rtol=RTOL)
    # print(utils.hash_numpy(op_sig), file=regtest)
