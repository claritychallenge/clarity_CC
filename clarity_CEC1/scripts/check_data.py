import argparse
import json
from tqdm import tqdm
import os
import sys
import logging

from clarity_core.config import CONFIG


def check_files(file_list):
    """Check files in the list are present.

    Return True if any files missing.
    """
    missing = [file for file in tqdm(file_list) if not os.path.isfile(file)]
    if len(missing) != 0:
        logging.error(missing)
    return len(missing) > 0


def check_data(data_root, dataset):

    print(f"Checking files for {dataset}")
    with open(f"{data_root}/metadata/scenes.{dataset}.json") as fp:
        scenes = json.load(fp)

    brir_dir = f"{data_root}/{dataset}/rooms/brir"
    masker_dir = f"{data_root}/{dataset}/interferers"
    target_dir = f"{data_root}/{dataset}/targets"
    hrir_dir = f"{data_root}/hrir/HRIRs_MAT"

    rooms = {scene["room"]["name"] for scene in scenes}
    hrirs = {scene["hrirfilename"] for scene in scenes}
    targets = {scene["target"]["name"] for scene in scenes}
    maskers = {
        (scene["interferer"]["name"], scene["interferer"]["type"]) for scene in scenes
    }

    brir_files = [
        f"{brir_dir}/brir_{room}_{source}_{channel}.wav"
        for room in rooms
        for source in ["t", "i1"]
        for channel in ["CH0", "CH1", "CH2", "CH3"]
    ]

    anech_brir_files = [
        f"{brir_dir}/anech_brir_{room}_t_CH1.wav"
        for room in rooms
    ]  

    hrir_files = [f"{hrir_dir}/{hrir}.mat" for hrir in hrirs]
    target_files = [f"{target_dir}/{target}.wav" for target in targets]
    masker_files = [f"{masker_dir}/{type}/{name}.wav" for name, type in maskers]

    print("Checking brir files")
    missing = check_files(brir_files)

    print("Checking anechoic brir files")
    missing = check_files(anech_brir_files)

    print("Checking hrir files")
    missing |= check_files(hrir_files)

    print("Checking target files")
    missing |= check_files(target_files)

    print("Checking masker files")
    missing |= check_files(masker_files)

    return missing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("data_root", help="clarity data directory")
    parser.add_argument("dataset", help="dataset to check")
    args = parser.parse_args()

    missing = check_data(args.data_root, args.dataset)

    sys.exit(missing)
