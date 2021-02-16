import argparse
import json
from tqdm import tqdm
import sys

from clarity_core.config import CONFIG

sys.path.append(r"../projects/GHA")
from GHA import GHAHearingAid as HearingAid

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry_run", action="store_true", help="perform dry run only")
    parser.add_argument(
        "--num_channels",
        nargs="?",
        type=int,
        default=1,
        help="number of HA channels [default: 1]",
    )
    parser.add_argument("scene_list_filename", help="json file containing scene data")
    parser.add_argument("listener_filename", help="json file containing listener data")
    parser.add_argument(
        "scenes_listeners_filename",
        help="json file containing scenes to listeners mapping",
    )

    parser.add_argument("input_path", help="input file names")
    parser.add_argument("output_path", help="path to output data")
    args = parser.parse_args()

    channels = args.num_channels

    scene_list = json.load(open(args.scene_list_filename, "r"))
    listeners = json.load(open(args.listener_filename, "r"))
    scenes_listeners = json.load(open(args.scenes_listeners_filename, "r"))

    hearing_aid = HearingAid(fs=CONFIG.fs, channels=channels)

    for scene in tqdm(scene_list):
        for listener_name in scenes_listeners[scene["scene"]]:
            listener = listeners[listener_name]
            hearing_aid.set_listener(listener)
            hearing_aid.process_files(
                infile_names=[
                    f"{args.input_path}/{scene['scene']}_mixed_CH{ch}.wav"
                    for ch in range(1, channels + 1)
                ],
                outfile_name=(
                    f"{args.output_path}/{scene['scene']}_{listener['name']}_HA-output.wav"
                ),
            )
