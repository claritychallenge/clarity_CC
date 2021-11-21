import numpy as np

"""Audiometric data used at various points in the hearing loss simulation
"""

# fmt:off
# (Comment above disables autoformatting)
# ------------------------------------------------------------------------------

# AES paper midear correction with slight increases in the corrections of 80 Hz & below.
# USED TO CALC FILES ff.32k, df.32k, hd580.32k; Killion JASA 63 1501-1509 (1978)

HZ = np.array(
    [
        0.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 125.0, 160.0, 200.0, 250.0,
        315.0, 400.0, 500.0, 630.0, 750.0, 800.0, 1000.0, 1250.0, 1500.0, 1600.0, 2000.0,
        2500.0, 3000.0, 3150.0, 4000.0, 5000.0, 6000.0, 6300.0, 8000.0, 9000.0, 10000.0,
        11200.0, 12500.0, 14000.0, 15000.0, 16000.0, 20000.0, 48000
    ]
)

MIDEAR = np.array(
    [
        50.0, 39.6, 32.0, 25.85, 21.4, 18.5, 15.9, 14.1, 12.4, 11.0, 9.6, 8.3, 7.4, 6.2,
        4.8, 3.8, 3.3, 2.9, 2.6, 2.6, 4.5, 5.4, 6.1, 8.5, 10.4, 7.3, 7.0, 6.6, 7.0, 9.2,
        10.2, 12.2, 10.8, 10.1, 12.7, 15.0, 18.2, 23.8, 32.3, 50.0, 50.0,
    ]
)

# ------------------------------------------------------------------------------

# Free field (frontal)FF_ED correction for threshold (was ISO std Table 1 - 4.2 dB)
# i.e. relative to 0.0 dB at 1000 Hz, Shaw 1974

FF_ED = np.array(
    [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.5, 0.9, 1.4, 1.6, 1.7,
        2.5, 2.7, 2.6, 2.6, 3.2, 5.2, 6.6, 12.0, 16.8, 15.3, 15.2, 14.2, 10.7, 7.1, 6.4,
        1.8, -0.9, -1.6, 1.9, 4.9, 2.0, -2.0, 2.5, 2.5, 2.5,
    ]
)

# ------------------------------------------------------------------------------

# DIFFUSE field ( relative to 0.0 dB at 1000Hz)
# from 2008 file [corrections08.m] used in Samsung collaboration

DF_ED = np.array(
    [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.3, 0.4, 0.5, 1.0, 1.6, 1.7,
        2.2, 2.7, 2.9, 3.8, 5.3, 6.8, 7.2, 10.2, 14.9, 14.5, 14.4, 12.7, 10.8, 8.9, 8.7,
        8.5, 6.2, 5.0, 4.5, 4.0, 3.3, 2.6, 2.0, 2.0, 2.0
    ]
)


# ------------------------------------------------------------------------------

# ITU Rec P 58 08/96 Head and Torso Simulator transfer fns. from Peter Hugher BTRL,
# 4-June-2001. Negative of values in Table 14a of ITU P58 (05/2013), accessible at
# http://www.itu.int/rec/T-REC-P.58-201305-I/en
# Freely available. Converts from ear reference point (ERP) to eardrum reference
# point (DRP). EXCEPT extra 2 points added for 20k & 48k by MAS, MAr 2012

ITU_HZ = np.array(
    [
        0, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
        2500, 3150, 4000, 5000, 6300, 8000, 10000, 20000, 48000,
    ]
)

# Ear Reference Point to Drum Reference Point (ERP-DRP) transfer function,
# Table 14A/P.58, sect 6.2. NB negative of table since defined other way round.

ITU_ERP_DRP = np.array(
    [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.3, 0.2, 0.5, 0.6, 0.7, 1.1, 1.7, 2.6, 4.2, 6.5, 9.4,
        10.3, 6.6, 3.2, 3.3, 16, 14.4, 14.4, 14.4,
    ]
)

# fmt: on
