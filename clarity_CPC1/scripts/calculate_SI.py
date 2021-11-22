import argparse
import csv
import json
import logging
import sys

import numpy as np
from clarity_core.config import CONFIG
from clarity_core.signal import find_delay_impulse, read_signal
from tqdm import tqdm

sys.path.append("../projects/MBSTOI")
from MBSTOI import mbstoi


def calculate_SI(
    scene,
    listener,
    system,
    clean_input_path,
    processed_input_path,
    fs,
    gridcoarseness=1,
):
    """Run baseline speech intelligibility (SI) algorithm. MBSTOI
    requires time alignment of input signals. Here we correct for
    broadband delay introduced by the MSBG hearing loss model.
    Hearing aids also introduce a small delay, but this depends on
    the exact implementation. See projects/MBSTOI/README.md.

    Outputs can be found in text file sii.txt in /scenes folder.

    Args:
        scene (str): dictionary defining the scene to be generated
        listener (str): listener
        system (str): system
        clean_input_path (str): path to the clean speech input data
        processed_input_path (str): path to the processed input data
        fs (float): sampling rate
        gridcoarseness (int): MBSTOI EC search grid coarseness (default: 1)

    """
    logging.info(f"Running SI calculation: scene {scene}, listener {listener}")

    # Get non-reverberant clean signal
    clean = read_signal(f"{clean_input_path}/{scene}_target_anechoic.wav")

    # Get signal processed by HL and HA models
    proc = read_signal(
        f"{processed_input_path}/{scene}_{listener}_{system}_HL-output.wav",
    )

    # Calculate channel-specific unit impulse delay due to HL model and audiograms
    ddf = read_signal(
        f"{processed_input_path}/{scene}_{listener}_{system}_HLddf-output.wav",
    )
    delay = find_delay_impulse(ddf, initial_value=int(CONFIG.fs / 2))

    if delay[0] != delay[1]:
        logging.info(f"Difference in delay of {delay[0] - delay[1]}.")

    maxdelay = int(np.max(delay))

    # Allow for value lower than 1000 samples in case of unimpaired hearing
    if maxdelay > 2000:
        logging.error(f"Error in delay calculation for signal time-alignment.")

    # Correct for delays by padding clean signals
    cleanpad = np.zeros((len(clean) + maxdelay, 2))
    procpad = np.zeros((len(clean) + maxdelay, 2))

    if len(procpad) < len(proc):
        raise ValueError(f"Padded processed signal is too short.")

    cleanpad[int(delay[0]) : int(len(clean) + int(delay[0])), 0] = clean[:, 0]
    cleanpad[int(delay[1]) : int(len(clean) + int(delay[1])), 1] = clean[:, 1]
    procpad[: len(proc)] = proc

    # Calculate intelligibility

    sii = mbstoi(
        cleanpad[:, 0],
        cleanpad[:, 1],
        procpad[:, 0],
        procpad[:, 1],
        gridcoarseness=gridcoarseness,
    )

    return sii


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("signals_filename", help="json file containing signal_metadata")
    parser.add_argument("clean_input_path", help="path to clean input data")
    parser.add_argument("processed_input_path", help="path to processed input data")
    parser.add_argument("output_sii_file", help="path to output sii csv file")
    args = parser.parse_args()

    signals = json.load(open(args.signals_filename, "r"))

    f = open(args.output_sii_file, "a")
    writer = csv.writer(f)
    writer.writerow(["scene", "listener", "system", "MBSTOI"])

    for signal in tqdm(signals):
        listener = signal["listener"]
        scene = signal["scene"]
        system = signal["system"]
        sii = calculate_SI(
            scene,
            listener,
            system,
            args.clean_input_path,
            args.processed_input_path,
            CONFIG.fs,
        )
        writer.writerow([scene, listener, system, sii])
        f.flush()

    f.close()
