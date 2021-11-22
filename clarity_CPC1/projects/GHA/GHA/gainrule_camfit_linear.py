import numpy as np
import copy

import GHA


def gainrule_camfit_linear(
    audiogram, sFitmodel, noisegatelevels=45, noisegateslope=1, max_output_level=100
):
    """Apply linear Cambridge rule for hearing aid fittings 'CAMFIT'.

    Based on OpenMHA gainrule_camfit_linear.m. Applies linear Cambridge rule for
    hearing aid fittings 'CAMFIT'. Implemented as described in B. Moore and B.
    Glasberg (1998), "Use of a loudness model for hearing-aid fitting. I. Linear
    hearing aids" Brit. J. Audiol. (32) 317-335.

    The gain rule limits the gains so that in each band 100 dB output level
    is not exceeded.
    The Cambridge formula defines intercepts only up to 5 kHz. Because the
    intercepts do not vary much between 1kHz and 5kHz anyway (these are all
    within 0dB +/- 1dB), we extend the last intercept of +1dB at 5kHz to all higher
    frequencies. This function assumes audiogram frequencies are identical for
    two ears.

    The original function is part of the HörTech Open Master Hearing Aid (openMHA)
    Copyright © 2007 2009 2011 2013 2015 2017 2018 HörTech gGmbH
    openMHA is free software: see licencing conditions at http://www.openmha.org/

    Args:
        sAud (dict): contains the subject-specific hearing threshold levels in
            dB HL for the left and right ears, and the audiogram frequencies
        sFitmodel (dict): contains the center frequencies for the amplification
            bands and input levels in SPL for which to compute the gains
        noisegatelevels (ndarray): compression threshold levels for each frequency
            band (default: 45)
        noisegateslope (int): determines slope of gains below compression threshold
            (default: 1)

    Returns:
        dict: dictionary containing gain table, noise gate, and noise
            gate expansion slope fields

    """

    intercept_frequencies = np.array(
        [125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000, 5005]
    )
    intercepts = np.array([-11, -10, -8, -6, 0, -1, 1, -1, 0, 1, 1])
    try:
        if np.size(sFitmodel["frequencies"][0][0]) > 1:
            intercepts = GHA.freq_interp_sh(
                intercept_frequencies, intercepts, sFitmodel["frequencies"][0][0]
            )
    except:
        intercepts = GHA.freq_interp_sh(
            intercept_frequencies, intercepts, sFitmodel["frequencies"]
        )

    sFitmodel_frequencies = sFitmodel["frequencies"]
    sFitmodel_levels = sFitmodel["levels"]
    if np.size(sFitmodel_frequencies) == 1:
        sFitmodel_frequencies = sFitmodel_frequencies[0][0]
        sFitmodel_levels = sFitmodel_levels[0][0]

    if np.shape(sFitmodel_levels)[0] != 1:
        sFitmodel_levels = np.transpose(sFitmodel_levels)

    # Interpolate audiogram
    # num levels x num freqs x L, R
    sGt = np.zeros((np.size(sFitmodel_levels), np.size(sFitmodel_frequencies), 2))

    noisegate_level = np.zeros((np.size(sFitmodel_frequencies), 2))
    noisegate_slope = np.zeros((np.size(sFitmodel_frequencies), 2))
    insertion_gains_out = np.zeros((np.size(sFitmodel_frequencies), 2))

    for i, levels in enumerate([audiogram.levels_l, audiogram.levels_r]):
        htlside = GHA.freq_interp_sh(audiogram.cfs, levels, sFitmodel_frequencies)

        insertion_gains = htlside * 0.48 + intercepts

        # According to B. Moore (1998), "Use of a loudness model for hearing-aid
        # fitting. II. Hearing aids with multi-channel compression" Brit. J.
        # Audiol. (33) 157-170, p. 159, do not permit negative insertion gains in
        # practice.
        insertion_gains[insertion_gains < 0] = 0

        # Set all gains to 0 for 0dB HL flat audiogram
        insertion_gains = insertion_gains * htlside.any()  # any(htlside)

        sGt[:, :, i] = np.tile(insertion_gains, (len(sFitmodel_levels), 1))

        if np.size(insertion_gains[0]) == np.size(htlside):
            insertion_gains = insertion_gains[0]

        insertion_gains_out[:, i] = insertion_gains
        output_levels = np.tile(sFitmodel_levels, (np.size(insertion_gains), 1))
        output_levels = sGt[:, :, i] + np.transpose(output_levels)

        # Where output level is greater than max_output_level, reduce gain
        safe_output_levels = copy.deepcopy(output_levels)
        safe_output_levels[safe_output_levels > max_output_level] = max_output_level

        sGt[:, :, i] = sGt[:, :, i] - (output_levels - safe_output_levels)

        noisegate_level[:, i] = noisegatelevels * np.ones(
            np.size(sFitmodel_frequencies)
        )
        noisegate_slope[:, i] = noisegateslope * np.ones(np.size(sFitmodel_frequencies))

    overall_level = 10 * np.log(np.sum(10 ** (insertion_gains_out / 10), axis=0))

    output = {}
    output["sGt"] = sGt
    output["noisegate_level"] = noisegate_level
    output["noisegate_slope"] = noisegate_slope
    output["insertion_gains"] = insertion_gains_out

    return output
