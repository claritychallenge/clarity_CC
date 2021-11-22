import sys
import json
from tqdm import tqdm

from clarity_core.config import CONFIG
import GHA

from GHA import GHAHearingAid as HearingAid


def run_demo(
    scene_list,
    listeners,
    scenes_listeners,
    input_path,
    output_path,
    channels=[1, 2, 3],
    dry_run=False,
):
    """
    Demo of using GHA to process a signal with the Generic Hearing
    Aid, as specified by audiograms.

    Arguments:
        scene_list {str}: path to scene specifications
        listeners {str}: path to listener json file
        scenes_listeners {str}: path to scene-listener pairing information
        input_path {str}: input signal path
        output_path {str}: path for GHA-processed signals
        channels {list}: list of channels to process, default is [1, 2, 3]
        dry_run {bool}: default: False
    """

    scene_list = json.load(open(scene_list, "r"))
    listeners = json.load(open(listeners, "r"))
    scenes_listeners = json.load(open(scenes_listeners, "r"))

    hearing_aid = HearingAid(fs=CONFIG.fs, channels=channels)

    for scene in tqdm(scene_list):
        for listener_name in scenes_listeners[scene["scene"]]:
            listener = listeners[listener_name]
            listener["id"] = listener_name
            hearing_aid.set_listener(listener)
            hearing_aid.process_scene(
                scene,
                input_path,
                output_path,
                dry_run=dry_run,
            )


if __name__ == "__main__":
    n_args = len(sys.argv)

    # Get parent directory
    import os

    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    tmp = dirname.split("/")
    dirname = "/".join(tmp[:-1])

    scenes_filename = (
        sys.argv[1] if n_args >= 2 else dirname + "/data/scenes/train.json"
    )
    listeners_filename = (
        sys.argv[2] if n_args >= 3 else dirname + "/data/listeners.json"
    )
    scenes_listeners_filename = (
        sys.argv[3] if n_args >= 4 else dirname + "/data/scenes_listeners.json"
    )
    scenes_listeners_filename = (
        sys.argv[4] if n_args >= 5 else dirname + "/data/scenes_listeners.json"
    )
    input_path = (
        sys.argv[5] if n_args >= 6 else dirname + "/projects/GHA/cfg_files/inputsignals"
    )
    output_path = (
        sys.argv[5]
        if n_args >= 6
        else dirname + "/projects/GHA/cfg_files/outputsignals"
    )

    channels = [1, 2, 3]  # note 2 must be present
    run_demo(
        scenes_filename,
        listeners_filename,
        scenes_listeners_filename,
        input_path,
        output_path,
        channels,
    )

    # python run_demo.py <scenes_filename> <listeners_filename> <scenes_listeners_filename> <input_path> <output_path>