import numpy as np
import re
import logging

# import GHA


def format_gaintable(gaintable, noisegate_corr=True):
    """
    Format gaintable for insertion into cfg file as long string.

    Args:
        gaintable (ndarray): The gaintable to format
        noisegate_corr (boolean, optional): apply noisegate correction or do not
            (default: True)

    Returns:
        str: gaintable formatted for insertion into OpenMHA
            cfg file

    """
    if noisegate_corr:
        sGt = gaintable["sGt"]
    else:
        logging.warning("Noise gate correction not being applied to gain table.")
        sGt = gaintable["sGt_uncorr"]

    # Do not apply gains to 9th and 18th row
    logging.info("No application of gains to 9th and 18th row of table.")
    sGt[[8, -1], :] = 0

    # Format for inclusion in cfg file
    v = "["
    for k in range(0, np.shape(sGt)[0]):
        v += f"{sGt[k, :]};"
    v += "]"
    v = v.replace("\n", "")
    v = re.sub(" +", " ", v)  # remove extra white spaces
    # v = re.sub(". ", " ", v)  # remove point after integers

    formatted_sGt = v

    return formatted_sGt
