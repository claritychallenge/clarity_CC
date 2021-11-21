import numpy as np
from scipy.interpolate import interp1d
import logging


def isothr(vsDesF):
    """Calculate conversion factors of HL thresholds to SPL thresholds.

    Translation of OpenMHA isothr.m. Calculates conversion factors of HL
    thresholds to SPL thresholds. Values from 20 Hz to 12500 Hz are taken
    from ISO 226:2003(E). Values from 14000 Hz to 18000 Hz are taken from ISO
    389-7:2005 (reference thresholds of hearing for free field listening).
    Values at 0 and 20000 Hz are not taken from the ISO Threshold contour.

    Args:
        vsDesF (list): centre frequencies for the amplification bands as 177,
            297, 500, 841,  1414,  2378, 4000, 6727, 11314 Hz

    Returns:
        ndarray: conversion factors

    """
    iso226_389 = np.zeros((34, 2))
    iso226_389[:, 0] = [
        0,
        20,
        25,
        31.5,
        40,
        50,
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
        14000,
        16000,
        18000,
        20000,
    ]
    iso226_389[:, 1] = [
        80.0,
        78.5,
        68.7,
        59.5,
        51.1,
        44.0,
        37.5,
        31.5,
        26.5,
        22.1,
        17.9,
        14.4,
        11.4,
        8.6,
        6.2,
        4.4,
        3.0,
        2.2,
        2.4,
        3.5,
        1.7,
        -1.3,
        -4.2,
        -6.0,
        -5.4,
        -1.5,
        6.0,
        12.6,
        13.9,
        12.3,
        18.4,
        40.2,
        73.2,
        70.0,
    ]
    vThr = iso226_389[:, 1]
    vsF = iso226_389[:, 0]

    if isinstance(vsDesF, list):
        vsDesF = np.array(vsDesF)

    if np.size(vsDesF[vsDesF < 50]) > 0:
        logging.warning("Frequency values below 50 Hz set to 50 Hz")
        vsDesF[vsDesF < 50] = 50

    vIsoThrDB = interp1d(vsF, vThr, fill_value="extrapolate")(vsDesF)

    return vIsoThrDB
