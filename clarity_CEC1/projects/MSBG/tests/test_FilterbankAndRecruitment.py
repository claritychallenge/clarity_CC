import scipy.io
import os
import numpy.testing as npt
import pytest
import numpy as np

import MSBG
import tests.utils as utils


# Test that python FilterbankAndRecruitment code reproduces MATLAB outputs.
# MATLAB inputs and outputs stored in mat files in data

MIN_SDR = 60  # Minimum allowable SDR between Python and MATLAB reference


def filterbank_and_recruitment(
    coch_sig,
    SPL_equiv_0dB,
    nchans,
    erbn_cf,
    fs,
    ngamma,
    gtn_denoms,
    gtn_nums,
    gtn_delays,
    start2poleHP,
    hp_denoms,
    hp_nums,
    expnsn_ratios,
    eq_loud_db,
    recombination_dB,
):
    coch_sig = coch_sig[0, :]

    start2poleHP = int(start2poleHP)

    coch_sig_out = MSBG.gammatone_filterbank(
        coch_sig,
        ngamma,
        gtn_denoms,
        gtn_nums,
        gtn_delays,
        start2poleHP,
        hp_denoms,
        hp_nums,
    )

    envelope = MSBG.compute_envelope(coch_sig_out, erbn_cf, fs)

    coch_sig_out = MSBG.recruitment(
        coch_sig_out,
        envelope,
        SPL_equiv_0dB,
        expnsn_ratios,
        eq_loud_db,
    )

    coch_sig_out = np.sum(coch_sig_out, axis=0) * np.power(
        10, (-0.05 * recombination_dB)
    )

    return coch_sig_out


@pytest.mark.parametrize(
    "filename",
    [
        "FilterbankAndRecruitment-180ae98b8e90.mat",
        "FilterbankAndRecruitment-6f349d167ecc.mat",
        "FilterbankAndRecruitment-9762d5690fa3.mat",
        "FilterbankAndRecruitment-3666487848e0.mat",
    ],
)
def test_FilterbankAndRecruitment(filename, regtest):
    filename = os.path.dirname(os.path.abspath(__file__)) + "/data/" + filename
    data = scipy.io.loadmat(filename, squeeze_me=False)
    filtrecruited = filterbank_and_recruitment(
        data["coch_sig"],
        data["SPLequiv0dBfile"][0],
        data["nchans"],
        data["erbn_centfrq"][0],
        data["fs"],
        data["ngamma"],
        data["gtn_denoms"],
        data["gtn_nums"],
        data["gtn_delays"][0],
        data["start2poleHP"],
        data["hp_denoms"],
        data["hp_nums"],
        data["expnsn_ratios"][0],
        data["eq_loud_db"][0],
        data["recombination_dB"],
    )

    sdr = utils.compute_siSDR(filtrecruited.flatten(), data["coch_sig_out"].flatten())
    assert sdr > MIN_SDR

    if all(x == 1.0 for x in data["expnsn_ratios"][0]):
        # No recruitment, results should be very, very close
        npt.assert_allclose(filtrecruited, data["coch_sig_out"])
    else:
        # With recruitment, small diffs between MATLAB and Python
        # due to differences in low pass filter design.
        npt.assert_allclose(filtrecruited, data["coch_sig_out"], atol=1e-8, rtol=0.02)
    print(utils.hash_numpy(filtrecruited), file=regtest)
