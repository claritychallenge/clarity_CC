import hashlib
import numpy as np
import math


def hash_numpy(variable):
    """Utility function used in python regression tests.

    Returns a SHA1 checksum for an arbitrary numpy array.
    """
    try:
        data = variable.copy().view(np.uint8)
    except:
        data = variable.copy()
    return hashlib.sha1(data).hexdigest()


def compute_siSDR(estimated_signal, reference_signal, scaling=True):
    """SI-SDR and SDR, Le Roux et al. arXiv 1811.02508v1. """

    # see https://github.com/sigsep/bsseval/issues/3
    if scaling:
        # get the scaling factor for clean sources
        a = np.dot(reference_signal, estimated_signal) / np.dot(
            reference_signal, reference_signal
        )
    else:
        a = 1

    e_true = a * reference_signal
    e_res = estimated_signal - e_true
    Sss = (e_true ** 2).sum()
    Snn = (e_res ** 2).sum()
    SDR = 10 * math.log10(Sss / Snn) if (Snn != 0.0) else float("inf")

    return SDR
