import os
import numpy as np
import copy
import scipy.io as spio

import GHA
from clarity_core.config import CONFIG


def get_gaintable(
    audiogram, noisegatelevels, noisegateslope, cr_level, max_output_level
):
    """Compute a gaintable for a given audiogram.

    Replaces MATLAB GUI interface of original OpenMHA software for
    gaintable_camfit_compr table calculation. Assumes two channels and
    that audiogram frequencies are identical at two ears.

    Args:
        audiogram (Audiogram): the audiogram for which to compute the gain table
        audf (list): audiogram frequencies for fitting
        noisegatelevels (ndarray): compression threshold levels for each frequency band
        noisegateslope (int): determines slope of gains below compression threshold
        cr_level (int): overall input level in dB for calculation of compression ratios
        max_output_level (int): maximum output level in dB

    Returns:
        dict: dim ndarray of gains

    """
    # Initialise parameters
    num_channels = 2  # only configured for two channels
    sFitmodel = {}
    Fs = CONFIG.fs

    # Fixed centre frequencies for amplification bands
    sFitmodel["frequencies"] = [
        177,
        297,
        500,
        841,
        1414,
        2378,
        4.0000e03,
        6.7270e03,
        11314,
    ]
    sFitmodel["edge_frequencies"] = [
        1.0000e-08,
        229.2793,
        385.3570,
        648.4597,
        1.0905e03,
        1.8337e03,
        3.0842e03,
        5.1873e03,
        8.7241e03,
        10000001,
    ]

    # Input levels in SPL for which to compute the gains
    sFitmodel["levels"] = np.arange(-10, 110 + 1)
    sFitmodel["channels"] = num_channels
    sFitmodel["side"] = "lr"

    # Calculate gains and compression ratios
    output = GHA.gainrule_camfit_compr(
        audiogram,
        sFitmodel,
        noisegatelevels,
        noisegateslope,
        cr_level,
        max_output_level,
    )

    sGt = dict()
    sGt["sGt_uncorr"] = copy.deepcopy(output["sGt"])  # sGt without noisegate correction

    output = GHA.multifit_apply_noisegate(
        output["sGt"],
        sFitmodel["frequencies"],
        sFitmodel["levels"],
        output["noisegatelevel"],
        output["noisegateslope"],
    )

    # Reshape sGt here to suit cfg file input
    sGt["sGt"] = np.transpose(np.reshape(output["sGt"], (121, 18), order="F"))

    sGt["noisegatelevel"] = output["noisegatelevel"]
    sGt["noisegateslope"] = output["noisegateslope"]
    sGt["frequencies"] = sFitmodel["frequencies"]
    sGt["levels"] = sFitmodel["levels"]
    sGt["channels"] = num_channels

    return sGt
