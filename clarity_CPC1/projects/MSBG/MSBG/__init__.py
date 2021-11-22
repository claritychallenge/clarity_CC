import logging
import numpy as np

MASTER_FS = 44100  # Expected sampling rate of input signal

from MSBG.audiogram import Audiogram
from MSBG.ear import Ear
from MSBG.file import read_gtf_file  # read_wav,
from MSBG.gen_signal import gen_eh2008_speech_noise, gen_tone
from MSBG.measure_rms import generate_key_percent, measure_rms
from MSBG.smearing import Smearer, make_smear_mat3, audfilt, smear3
from MSBG.cochlea import (
    Cochlea,
    gammatone_filterbank,
    recruitment,
    compute_envelope,
)
from MSBG.firwin2 import firwin2

__all__ = [
    "Audiogram",
    "Cochlea",
    "Ear",
    "Smearer",
    "audfilt",
    "compute_envelope",
    "firwin2",
    "gammatone_filterbank",
    "gen_eh2008_speech_noise",
    "gen_tone",
    "generate_key_percent",
    "make_smear_mat3",
    "measure_rms",
    "read_gtf_file",
    # "read_wav",
    "recruitment",
    "smear3",
]
