import scipy.io
import os
import numpy.testing as npt
import numpy as np
import pytest
import scipy.io as spio

import GHA
import tests.utils as utils

# Test that python get_gain_table code reproduces MATLAB GUI outputs.
# MATLAB inputs and outputs stored in mat files in auddata

RTOL = 1e-07  # error tolerance for allclose check
ATOL = 2e-04  # error tolerance for allclose check


@pytest.mark.parametrize(
    "filename",
    [
        "refflat40.mat",
        "refflat40ex.mat",
        "refflat50.mat",
        "refflat50ex.mat",
        "refN3based.mat",
        "refN3basedex.mat",
        "refN4based.mat",
        "refN4basedex.mat",
        "refS3based.mat",
        "refS3basedex.mat",
        "refslope.mat",
        "refslopeex.mat",
    ],
)
def test_get_gaintable(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/auddata/" + filename
    data = scipy.io.loadmat(filename)

    audfn = filename.split("/")[-1]
    audfn = "aud" + audfn[3:]
    audfilename = os.path.dirname(filename) + "/" + audfn

    # Set audiogram frequencies
    if "ex" in audfilename:
        audf = [125, 250, 500, 1000, 2000, 4000, 6000, 8000]
    else:
        audf = [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000]

    # If importing audiogram from mat file
    dirname = os.path.dirname(__file__)
    dirname = os.path.split(dirname)[0]  # go to parent folder GHA
    filename = os.path.join(dirname, audfilename)
    auddata = spio.loadmat(filename)

    audiogram = GHA.Audiogram(
        levels_l=auddata["L"], levels_r=auddata["R"], cfs=np.array(audf)
    )
    noisegatelevels = 45
    noisegateslope = 1
    output = GHA.get_gaintable(
        audiogram, noisegatelevels, noisegateslope, cr_level=110, max_output_level=100
    )

    npt.assert_allclose(
        output["sGt"][0:9, :], data["gaintable1"][0:9, :], atol=ATOL, rtol=RTOL
    )
    npt.assert_allclose(
        output["sGt"][9:, :], data["gaintable1"][9:, :], atol=ATOL, rtol=RTOL
    )
    print(utils.hash_numpy(output["sGt"]), file=regtest)
