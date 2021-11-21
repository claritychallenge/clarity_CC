from scipy.interpolate import interp1d


def multifit_apply_noisegate(
    sGt, sFit_model_frequencies, sFit_model_levels, noisegate_level, noisegate_slope
):
    """Apply noisegate.

    Based on OpenMHA subfunction of libmultifit.m.

    Args:
        sGt (ndarray): gain array
        sFit_model_frequencies (list): FFT filterbank frequencies
        sFit_model_levels (ndarray): levels at which to calculate gains
        noisegate_level (ndarray): chosen compression threshold
        noisegate_slope (ndarray): determines slope below compression threshold

    Returns:
        ndarray: Noise signal

    """

    for i in [0, 1]:
        for kf in range(len(sFit_model_frequencies)):
            gain_noisegate = interp1d(
                sFit_model_levels, sGt[:, kf, i], fill_value="extrapolate"
            )(noisegate_level[kf, i])
            idx = [
                i for i, x in enumerate(sFit_model_levels < noisegate_level[kf, i]) if x
            ]
            sGt[idx, kf, i] = (
                sFit_model_levels[idx] - noisegate_level[kf, i]
            ) * noisegate_slope[kf, i] + gain_noisegate

    output = {}
    output["sGt"] = {}
    output["sGt"] = sGt
    output["noisegatelevel"] = noisegate_level
    output["noisegateslope"] = noisegate_slope

    return output
