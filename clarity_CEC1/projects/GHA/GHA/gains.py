import numpy as np


def gains(compr_thr_inputs, compr_thr_gains, compression_ratios, levels):
    """Based on OpenMHA gains subfunction of gainrule_camfit_compr.

    Args:
        compr_thr_inputs (ndarray): levels for speech in dynamic compression (dc)
            bands minus minima distance (38 dB)
        compr_thr_gains (ndarray): interpolated audiogram levels plus conversion
            factors of HL thresholds to SPL thresholds (output of isothr.py) minus
            compr_thr_inputs
        compression_ratios (ndarray): compression ratios according to CAMFIT compressive
        levels (ndarray): set of levels over which to calculate gains e.g. -10:110 dB

    Returns:
        ndarray: set of uncorrected gains as 2-d numpy array

    """
    levels = np.transpose(np.tile(levels, (np.size(compr_thr_inputs), 1)))
    compr_thr_inputs = np.tile(compr_thr_inputs, (np.shape(levels)[0], 1))
    compr_thr_gains = np.tile(compr_thr_gains, (np.shape(levels)[0], 1))
    compression_ratios = np.tile(compression_ratios, (np.shape(levels)[0], 1))

    compr_thr_outputs = compr_thr_inputs + compr_thr_gains
    outputs = (levels - compr_thr_inputs) / compression_ratios + compr_thr_outputs
    g = outputs - levels

    return g
