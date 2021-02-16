import numpy as np
import copy
import logging

import GHA


def compute_proportion_overlap(a1, a2, b1, b2):
    """Compute proportion of overlap of two ranges.

    For ranges (a1, a2) and (b1, b2), express the extent of the overlap
    in the range as a proportion of the extent of range (b1, b2).add()

    e.g (4, 9) and (6, 15) -> overlap (6,9), so proportion is (9-6)/(15-6)

    """
    left = max(a1, b1)
    right = min(a2, b2)
    if left > right:
        overlap = 0.0
    else:
        overlap = float(right - left) / (b2 - b1)
    return overlap


def gainrule_camfit_compr(
    audiogram,
    sFitmodel,
    noisegatelevels=45,
    noisegateslope=1,
    level=0,
    max_output_level=100,
):
    """Applies compressive Cambridge rule for hearing aid fittings 'CAMFIT'.

    Translation of OpenMHA gainrule_camfit_compr.m.
    Applies compressive Cambridge rule for
    hearing aid fittings 'CAMFIT'. Computes gains for compression according to Moore
    et al. (1999) "Use of a loudness model for hearing aid fitting: II. Hearing aids
    with multi-channel compression." Brit. J. Audiol. (33) 157-170

    The gain rule limits the gains so that in each band 100 dB output level is
    not exceeded. This function assumes audiogram frequencies are identical for the
    two ears. In this implementation, any negative gains are set to 0 dB.

    The original function is part of the HörTech Open Master Hearing Aid (openMHA)
    Copyright © 2007 2009 2011 2013 2015 2017 2018 HörTech gGmbH
    openMHA is free software: see licencing conditions at http://www.openmha.org/

    Args:
        audiogram (Audiogram): the audiogram for which to make the fit
        sFitmodel (dict): contains the center frequencies for the amplification
            bands and input levels in SPL for which to compute the gains
        noisegatelevels (ndarray): compression threshold levels for each frequency
            band (default: 45)
        noisegateslope (int): determines slope of gains below compression threshold
        level (int): input level in each band for compression rate calculation
            (default: 0 for variable level depending on insertion gains)
        max_output_level (int): maximum output level in dB

    Returns:
        dict: dictionary containing gain table, noise gate, and noise
            gate expansion slope fields

    """

    # International long-term average speech spectrum for speech with an overall
    # level of 70dB in third-octave frequency bands, taken from Byrne et al.
    # (1994) J. Acoust. Soc. Am. 96(4) 2108-2120
    # Average across males and females SG
    LTASS_freq = np.array(
        [
            63,
            80,
            100,
            125,
            160,
            200,
            250,
            315,
            400,
            500,
            630,
            800,
            1000,
            1250,
            1600,
            2000,
            2500,
            3150,
            4000,
            5000,
            6300,
            8000,
            10000,
            12500,
            16000,
        ]
    )
    LTASS_edge_freq = np.zeros((26))
    LTASS_edge_freq[1:-1] = np.sqrt(LTASS_freq[0:-1] * LTASS_freq[1:])
    LTASS_edge_freq[-1] = 16000 * np.power(2, (1 / 6))
    LTASS_lev = np.array(
        [
            38.6,
            43.5,
            54.4,
            57.7,
            56.8,
            60.2,
            60.3,
            59.0,
            62.1,
            62.1,
            60.5,
            56.8,
            53.7,
            53.0,
            52.0,
            48.7,
            48.1,
            46.8,
            45.6,
            44.5,
            44.3,
            43.7,
            43.4,
            41.3,
            40.7,
        ]
    )
    LTASS_intensity = np.power(10, LTASS_lev / 10)

    frequencies = np.array(sFitmodel["frequencies"])
    edge_freq = np.array(sFitmodel["edge_frequencies"])

    sFitmodel_frequencies = np.array(sFitmodel["frequencies"])
    sFitmodel_levels = np.array(sFitmodel["levels"])

    speech_level_65_in_dc_bands = np.zeros(np.shape(frequencies))

    for band, (f_range_a, f_range_b) in enumerate(zip(edge_freq[:-1], edge_freq[1:])):
        portion = [
            compute_proportion_overlap(f_range_a, f_range_b, ltass_a, ltass_b)
            for (ltass_a, ltass_b) in zip(LTASS_edge_freq[:-1], LTASS_edge_freq[1:])
        ]
        intensity_sum = np.inner(LTASS_intensity, portion)  # weighted sum
        speech_level_70_in_dc_band = 10 * np.log10(intensity_sum)
        speech_level_65_in_dc_bands[band] = speech_level_70_in_dc_band - 5

    # minima in lowest level speech that needs to be understood is 38 dB below
    # speech_level_65_in_dc_bands
    minima_distance = 38

    # Conversion factors of HL thresholds to SPL thresholds
    Conv = GHA.isothr(frequencies)

    # Get speech minima
    Lmin = speech_level_65_in_dc_bands - minima_distance

    # Interpolate audiogram and get absolute thresholds in dB HL at centre frequencies
    # and gains required for speech minima
    htl = np.zeros((np.size(frequencies), 2))
    Gmin = np.zeros(np.shape(htl))

    for i, levels in enumerate([audiogram.levels_l, audiogram.levels_r]):
        htl[:, i] = GHA.freq_interp_sh(audiogram.cfs, levels, frequencies)
        Gmin[:, i] = htl[:, i] + Conv - Lmin

    # Get input levels
    Lmid = speech_level_65_in_dc_bands

    # Calculate gains at centre frequencies
    Gmid = GHA.gainrule_camfit_linear(
        audiogram, sFitmodel, noisegatelevels, noisegateslope, max_output_level
    )
    insertion_gains = Gmid["insertion_gains"]
    Gmid = Gmid["sGt"]

    # Calculate compression ratios
    compression_ratio = np.zeros((np.size(frequencies), 2))
    sGt = np.zeros((len(sFitmodel_levels), len(sFitmodel_frequencies), 2))

    noisegate_level = np.zeros((np.size(sFitmodel_frequencies), 2))
    noisegate_slope = np.zeros((np.size(sFitmodel_frequencies), 2))

    # Find index corresponding to input level in dB for compression rate calculation
    if level != 0:
        cr_idx = [i for (i, val) in enumerate(sFitmodel_levels) if val == level]

    for i, levels in enumerate([audiogram.levels_l, audiogram.levels_r]):
        if level != 0:
            tmp = Lmid + Gmid[cr_idx, :, i].flatten() - Lmin - Gmin[:, i]
        else:
            tmp = Lmid + insertion_gains[:, i] - Lmin - Gmin[:, i]
        idx = [i for i, x in enumerate(tmp < 13) if x]
        tmp[idx] = 13
        compression_ratio[:, i] = minima_distance / tmp
        compression_ratio[:, i][compression_ratio[:, i] < 1] = 1

        sGt[:, :, i] = GHA.gains(
            Lmin, Gmin[:, i], compression_ratio[:, i], sFitmodel_levels
        )
        # Set negative gains to zero
        sGt[:, :, i][sGt[:, :, i] < 0] = 0
        # where output level is greater than max_output_level, reduce gain
        tmp = np.tile(sFitmodel_levels, (len(Gmin[:, i]), 1))
        tmp = np.transpose(tmp)
        output_levels = sGt[:, :, i] + tmp

        safe_output_levels = copy.deepcopy(output_levels)
        safe_output_levels[safe_output_levels > max_output_level] = max_output_level
        sGt[:, :, i] = sGt[:, :, i] - (output_levels - safe_output_levels)

        # set all gains to 0 for 0dB HL flat audiogram
        sGt[:, :, i] = sGt[:, :, i] * levels.any()

        noisegate_level[:, i] = noisegatelevels * np.ones(
            np.size(sFitmodel_frequencies)
        )
        noisegate_slope[:, i] = noisegateslope * np.ones(np.size(sFitmodel_frequencies))

    logging.info(f"Noisegate levels are {noisegate_level}")

    output = {}
    output["sGt"] = sGt
    output["noisegatelevel"] = noisegate_level
    output["noisegateslope"] = noisegate_slope

    return output
