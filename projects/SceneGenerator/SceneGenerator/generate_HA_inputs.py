import json
import logging
import numpy as np
from scipy.signal import resample
import argparse
from tqdm import tqdm
from os.path import exists

import clarity_core.signal as ccs
from clarity_core.loadmat import loadmat
from clarity_core.config import CONFIG


def get_hrir(hrir_filename, azimuth):
    """Generate an HRIR for a given azimuth using an hrir file."""

    # Flip sign of azimuth to get change in coordinate system
    azimuth = round(-azimuth, 1)
    target_hrir = loadmat(hrir_filename)
    directions = target_hrir["M_directions"]
    idx = (directions[1, :] == 0) & (directions[0, :] == azimuth)
    if any(idx) == False:
        azimuth_degrees = np.zeros(48)
        azimuth_degrees[:24] = np.arange(0, 180, 7.5)
        azimuth_degrees[24:] = np.arange(-180, 0, 7.5)
        idx = np.where(
            np.abs(azimuth_degrees - azimuth)
            == np.min(np.abs(azimuth_degrees - azimuth))
        )
        azimuth = azimuth_degrees[idx]
        idx = (directions[1, :] == 0) & (directions[0, :] == azimuth)
    target_hrir = np.squeeze(target_hrir["M_data"][:, idx, :])

    # Downsample HRIR from 48000 to 44100
    l = len(target_hrir)
    target_hrir = resample(target_hrir, int(l * (CONFIG.fs / 48000) + 1))
    return target_hrir


def generate_HA_inputs(scene, input_path, output_path, fs, channels, tail_duration):

    """Generate all HA input signals for a given scene.

    Args:
        scene (dict): dictionary defining the scene to be generated
        input_path (str): path to the input data
        output_path (str): path to the output data
        fs (int): sample frequency
        channels (list, optional): list of HA channels to process (default: 1)
        tail_duration (float, optional): length in seconds to append
            for reverberation tail
    """
    logging.debug("In generate_HA_inputs")
    logging.debug(scene)

    n_tail = int(tail_duration * fs)

    pre_samples = scene["pre_samples"]
    post_samples = scene["post_samples"]
    dataset = scene["dataset"]
    target = scene["target"]["name"]
    noise_type = scene["interferer"]["type"]
    interferer = scene["interferer"]["name"]
    room = scene["room"]["name"]
    brir_stem = f"{input_path}/{dataset}/rooms/brir/brir_{room}"

    target_fn = f"{input_path}/{dataset}/targets/{target}.wav"
    interferer_fn = f"{input_path}/{dataset}/interferers/{noise_type}/{interferer}.wav"

    target = ccs.read_signal(target_fn)
    target = np.pad(target, [(pre_samples, post_samples)])

    offset = scene["interferer"]["offset"]  # Offset in samples
    interferer = ccs.read_signal(
        interferer_fn, offset=offset, nsamples=len(target), offset_is_samples=True
    )

    if len(target) != len(interferer):
        logging.debug("Target and interferer have different lengths")

    # Apply 500ms half-cosine ramp
    interferer = ccs.apply_ramp(interferer, dur=CONFIG.ramp_duration)

    prefix = f"{output_path}/{scene['scene']}"
    outputs = [
        (f"{prefix}_target.wav", target),
        (f"{prefix}_interferer.wav", interferer),
    ]

    snr_ref = None
    for channel in channels:
        # Load scene BRIRs
        target_brir_fn = f"{brir_stem}_t_CH{channel}.wav"
        interferer_brir_fn = f"{brir_stem}_i1_CH{channel}.wav"
        target_brir = ccs.read_signal(target_brir_fn)
        interferer_brir = ccs.read_signal(interferer_brir_fn)

        # Apply the BRIRs
        target_at_ear = ccs.apply_brir(target, target_brir, n_tail=n_tail)
        interferer_at_ear = ccs.apply_brir(interferer, interferer_brir, n_tail=n_tail)

        # Scale interferer to obtain SNR specified in scene description
        snr_dB = scene["SNR"]
        logging.info(f"Scaling interferer to obtain mixture SNR = {snr_dB} dB.")

        if snr_ref is None:
            # snr_ref computed for first channel in the list and then
            # same scaling applied to all
            snr_ref = ccs.compute_snr(
                target_at_ear,
                interferer_at_ear,
                pre_samples=pre_samples,
                post_samples=post_samples,
            )
            logging.debug(f"Using channel {channel} as reference.")

        # Apply snr_ref reference scaling to get 0 dB and then scale to target snr_dB
        interferer_at_ear = interferer_at_ear * snr_ref
        interferer_at_ear = interferer_at_ear * 10 ** ((-snr_dB) / 20)

        # Sum target and scaled and ramped interferer
        signal_at_ear = ccs.sum_signals([target_at_ear, interferer_at_ear])
        outputs.extend(
            [
                (f"{prefix}_mixed_CH{channel}.wav", signal_at_ear),
                (f"{prefix}_target_CH{channel}.wav", target_at_ear),
                (f"{prefix}_interferer_CH{channel}.wav", interferer_at_ear),
            ]
        )

    if channels == []:
        target_brir_fn = f"{brir_stem}_t_CH0.wav"
        target_brir = ccs.read_signal(target_brir_fn)

    # Construct the anechoic target reference signal
    hrir_filename = f"{input_path}/hrir/HRIRs_MAT/{scene['hrirfilename']}.mat"
    azimuth = scene["azimuth_target_listener"]
    target_hrir = get_hrir(hrir_filename, azimuth)
    target_hrir_pad = ccs.pad(target_hrir, len(target_brir))
    target_anechoic = ccs.apply_brir(target, target_hrir_pad, n_tail=n_tail)

    outputs.append((f"{prefix}_target_anechoic.wav", target_anechoic))

    # Write all output files
    for (filename, signal) in outputs:
        ccs.write_signal(filename, signal, CONFIG.fs)


def check_scene_exists(scene, output_path):
    """Checks correct dataset directory for full set of pre-existing files.

    Args:
        scene (dict): dictionary defining the scene to be generated.

    Returns:
        status: boolean value indicating whether scene signals exist
            or do not exist.

    """

    pattern = f"{output_path}/{scene['scene']}"
    files_to_check = [
        f"{pattern}_target.wav",
        f"{pattern}_target_anechoic.wav",
        f"{pattern}_interferer.wav",
    ]
    for ch in channels:
        files_to_check.extend(
            [
                f"{pattern}_mixed_CH{ch}.wav",
                f"{pattern}_interferer_CH{ch}.wav",
                f"{pattern}_target_CH{ch}.wav",
            ]
        )

    scene_exists = True
    for filename in files_to_check:
        scene_exists = scene_exists and exists(filename)
    return scene_exists


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num_channels",
        nargs="?",
        type=int,
        default=1,
        help="number of HA channels [default: 1]",
    )

    parser.add_argument("scene_list_filename", help="json file contain scene data")
    parser.add_argument("input_path", help="path to input data")
    parser.add_argument("output_path", help="path to output data")

    args = parser.parse_args()

    if args.num_channels == 0:
        # This will only generate the initial target, masker and anechoic target signal
        channels = []
    else:
        # ... as above plus N hearing aid input channels plus 'channel 0' (the eardrum signal).
        # e.g. num_channel = 2  => channels [1, 2, 0]
        channels = list(range(1, args.num_channels + 1)) + [0]
    scene_list = json.load(open(args.scene_list_filename, "r"))
    for scene in tqdm(scene_list):
        if check_scene_exists(scene, args.output_path):
            logging.info(f"Skipping processed scene {scene['scene']}.")
        else:
            generate_HA_inputs(
                scene,
                args.input_path,
                args.output_path,
                CONFIG.fs,
                channels,
                CONFIG.tail_duration,
            )
