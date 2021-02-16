import json
import numpy as np
from scipy.io import wavfile
import os

import MSBG


def read_gtf_file(gtf_file):
    """Read a gammatone filterbank file.

    List data is converted into numpy arrays.

    """

    # Fix filename if necessary
    dirname = os.getcwd()
    if dirname[-4:] in "MSBG":
        gtf_file = gtf_file
    elif dirname[-4:] in "rity":
        gtf_file = "projects/MSBG/" + gtf_file
    else:
        gtf_file = "../projects/MSBG/" + gtf_file

    with open(gtf_file, "r") as fp:
        data = json.load(fp)
    for key in data:
        if type(data[key]) == list:
            data[key] = np.array(data[key])
    return data
