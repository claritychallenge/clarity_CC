import sys
import argparse
import json
import numpy as np
import logging
from tqdm import tqdm

from clarity_core.config import CONFIG
from clarity_core.signal import read_signal, find_delay_impulse

sys.path.append("../projects/MBSTOI")
from MBSTOI import mbstoi


def calculate_SI(
    scene,
    listener,
    clean_input_path,
    processed_input_path,
    fs,
    gridcoarseness=1,
    dry_run=False,
):
    """Run baseline speech intelligibility (SI) algorithm. MBSTOI
    requires time alignment of input signals. Here we correct for
    broadband delay introduced by the MSBG hearing loss model.
    Hearing aids also introduce a small delay, but this depends on
    the exact implementation. See projects/MBSTOI/README.md.

    Outputs can be found in text file sii.txt in /scenes folder.

    Args:
        scene (dict): dictionary defining the scene to be generated
        listener (dict): listener
        clean_input_path (str): path to the clean speech input data
        processed_input_path (str): path to the processed input data
        fs (float): sampling rate
        gridcoarseness (int): MBSTOI EC search grid coarseness (default: 1)
        dry_run (bool, optional): run in dry_run mode (default: False)

    """
    logging.info(
        f"Running SI calculation: scene {scene['scene']}, listener {listener['name']}"
    )

    # Get non-reverberant clean signal
    clean = read_signal(f"{clean_input_path}/{scene['scene']}_target_anechoic.wav")

    # Get signal processed by HL and HA models
    proc = read_signal(
        f"{processed_input_path}/{scene['scene']}_{listener['name']}_HL-output.wav",
    )

    # Calculate channel-specific unit impulse delay due to HL model and audiograms
    ddf = read_signal(
        f"{processed_input_path}/{scene['scene']}_{listener['name']}_HLddf-output.wav",
    )
    delay = find_delay_impulse(ddf, initial_value=int(CONFIG.fs / 2))

    if delay[0] != delay[1]:
        logging.info(f"Difference in delay of {delay[0] - delay[1]}.")

    maxdelay = int(np.max(delay))

    # Allow for value lower than 1000 samples in case of unimpaired hearing
    if maxdelay > 2000:
        logging.error(f"Error in delay calculation for signal time-alignment.")

    # # For baseline software test signals, MBSTOI index tends to be higher when
    # # correcting for ddf delay + length difference.
    # diff = len(proc) - len(clean)
    # if diff < 0:
    #     logging.error("Check signal length!")
    #     diff = 0
    # else:
    #     logging.info(
    #         f"Correcting for delay + difference in signal lengths where delay = {delay} and length diff is {diff} samples."
    #     )

    # delay[0] += diff
    # delay[1] += diff

    # Correct for delays by padding clean signals
    cleanpad = np.zeros((len(clean) + maxdelay, 2))
    procpad = np.zeros((len(clean) + maxdelay, 2))

    if len(procpad) < len(proc):
        raise ValueError(f"Padded processed signal is too short.")

    cleanpad[int(delay[0]) : int(len(clean) + int(delay[0])), 0] = clean[:, 0]
    cleanpad[int(delay[1]) : int(len(clean) + int(delay[1])), 1] = clean[:, 1]
    procpad[: len(proc)] = proc

    # Calculate intelligibility
    if dry_run:
        return
    else:
        sii = mbstoi(
            cleanpad[:, 0],
            cleanpad[:, 1],
            procpad[:, 0],
            procpad[:, 1],
            gridcoarseness=gridcoarseness,
        )

        logging.info(f"{sii:3.4f}")
        return sii


# e.g. python calculate_SI.py "../data/scenes/train.json" "../data/listeners.json" "../data/scenes_listeners.json" "../data/output/train" "../data/output/train"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry_run", action="store_true", help="perform dry run only")
    parser.add_argument("scene_list_filename", help="json file containing scene data")
    parser.add_argument("listener_filename", help="json file containing listener data")
    parser.add_argument(
        "scenes_listeners_filename", help="json file containing scene listener mapping"
    )
    parser.add_argument("clean_input_path", help="path to clean input data")
    parser.add_argument("processed_input_path", help="path to processed input data")
    args = parser.parse_args()

    scene_list = json.load(open(args.scene_list_filename, "r"))
    listeners = json.load(open(args.listener_filename, "r"))
    scenes_listeners = json.load(open(args.scenes_listeners_filename, "r"))

    text_filename = args.clean_input_path + "/sii.txt"
    with open(text_filename, "a") as output_file:
        for scene in tqdm(scene_list):
            for listener_name in scenes_listeners[scene["scene"]]:
                listener = listeners[listener_name]
                sii = calculate_SI(
                    scene,
                    listener,
                    args.clean_input_path,
                    args.processed_input_path,
                    CONFIG.fs,
                    dry_run=args.dry_run,
                )
                output_file.write(
                    f"Scene {scene['scene']} listener {listener['name']} sii {round(sii,4)}\n"
                )
