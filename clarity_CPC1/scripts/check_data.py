import argparse
import json
from tqdm import tqdm
import os
import sys
import logging


def check_files(file_list):
    """Check files in the list are present.

    Return True if any files missing.
    """
    missing = [file for file in tqdm(file_list) if not os.path.isfile(file)]
    if len(missing) != 0:
        logging.error(missing)
    return len(missing) > 0


def check_scenes_data(data_root, dataset):
    """Check existence of all expected scene audio data."""

    print(f"Checking files for {dataset}")
    with open(f"{data_root}/metadata/{dataset}.json") as fp:
        scenes = json.load(fp)

    scenes_dir = f"{data_root}/clarity_data/scenes"

    rooms = {scene["scene"] for scene in scenes}

    scene_files_source = [
        f"{scenes_dir}/{room}_{sig_type}.wav"
        for room in rooms
        for sig_type in ["interferer", "target", "target_anechoic"]
    ]

    scene_files_HA_inputs = [
        f"{scenes_dir}/{room}_{sig_type}_{channel}.wav"
        for room in rooms
        for sig_type in ["interferer", "mixed", "target"]
        for channel in ["CH0", "CH1", "CH2", "CH3"]
    ]

    print("Checking scenes source files")
    missing = check_files(scene_files_source)

    print("Checking scenes HA inputs")
    missing |= check_files(scene_files_HA_inputs)

    return missing


def check_HA_output_data(data_root, dataset):
    """Check existence of all expected HA output signal files."""

    print(f"Checking files for {dataset}")
    with open(f"{data_root}/metadata/CPC1.{dataset}.json") as fp:
        responses = json.load(fp)

    ha_output_dir = f"{data_root}/clarity_data/HA_outputs/{dataset}"

    signals = {response["signal"] for response in responses}

    signal_files = [f"{ha_output_dir}/{signal}.wav" for signal in signals]

    print(f"Checking signal files for {dataset}")
    missing = check_files(signal_files)

    return missing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("data_root", help="clarity data directory")
    args = parser.parse_args()

    missing = False
    missing |= check_scenes_data(args.data_root, "scenes.CPC1_train")
    missing |= check_HA_output_data(args.data_root, "train")
    missing |= check_HA_output_data(args.data_root, "train_indep")

    sys.exit(missing)
