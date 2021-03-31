import argparse
import json
import logging
import numpy as np
import pyloudnorm as pyln
from tqdm import tqdm

from clarity_core.config import CONFIG
import clarity_core.signal as ccs

def run_HA_postprocessing(
    scene, listener_name, input_path, output_path, fs, latency=0, dry_run=False
):
    """Postprocess the hearing aid outputs. In round one, does not correct for
    headphones or add direct path. Normalises level according to ITU-R BS.1770
    and applies a compressor and hard clipper if necessary.

    Args:
        scene (dict): dictionary defining the scene to be generated
        listener_name (string): id for the listener
        input_path (str): path to the input data
        output_path (str): path to the output data
        fs (float): sampling rate
        latency (float, optional): latency for HA outputs versus direct path (default: 0)
        dry_run (bool, optional): run in dry-run mode (default: False)

    """
    logging.debug("In process_HA_outputs")

    signal_ha = ccs.read_signal(
        f"{input_path}/{scene['scene']}_{listener_name}_HA-output.wav"
    )

        # signal_at_ear = ccs.read_signal(f"{input_path}/{scene['scene']}_mixed_CH0.wav")

    # # HA processed and direct path signal must have the same length
    # minlen = min(signal_ha.shape[0], signal_at_ear.shape[0])
    # signal_ha = signal_ha[0:minlen, :]
    # signal_at_ear = signal_at_ear[0:minlen, :]

    # if dry_run:
    #     return

    # latent_silence = np.zeros((int(latency * fs), 2))

    # signal = np.sum(
    #     np.array(
    #         [
    #             np.vstack([latent_silence, signal_ha]),
    #             np.vstack([signal_at_ear, latent_silence]),
    #         ]
    #     ),
    #     axis=0,
    # )

    # Do loudness normalisation
    meter = pyln.Meter(CONFIG.fs)  # create ITU-R BS.1770 meter
    loudness = meter.integrated_loudness(signal_ha)  # measure loudness
    # Loudness normalise audio to CONFIG.norm_lufs dB LUFS
    signal_norm = pyln.normalize.loudness(signal_ha, loudness, CONFIG.norm_lufs)

    # Should compressor be applied?
    T = CONFIG.comp_thresh # threshold relative to 0 dB FS
    xn = np.max(abs(signal_norm))
    with np.errstate(divide='ignore'):
        x_dB = 20 * np.log10(np.divide(xn, 1))
    if x_dB > T:
        # Apply compressor
        R = CONFIG.comp_CR # compression ratio
        # Use openMHA default softclipper attack and release time parameters
        attackTime = CONFIG.comp_AT
        releaseTime = CONFIG.comp_RT

        signal_sc = ccs.compressor_twochannel(signal_norm, CONFIG.fs, T, R, attackTime, releaseTime)
        numCompressedSamples = sum(signal_norm.flatten() != signal_sc.flatten()) # over two channels
        if numCompressedSamples > 0:
            logging.debug(f"Warning: compression has been applied to {scene['scene']} {listener_name}, {numCompressedSamples} samples.") 

        # Do hard clipping if necessary
        if np.max(abs(signal_sc)) > CONFIG.clip_limit:
            numClippedSamples = sum(abs(signal_sc.flatten()) > CONFIG.clip_limit) # over two channels
            if numClippedSamples > 0:
                output = np.clip(signal_sc,-CONFIG.clip_limit, CONFIG.clip_limit)    
                logging.debug(f"Warning: {numClippedSamples} samples clipped.")
        else:
            output = signal_sc
    else:
        output = signal_norm

    # Write signal to output directory
    ccs.write_signal(
        f"{output_path}/{scene['scene']}_{listener_name}_HA-postprocessed.wav",
        output,
        fs,
        floating_point=True,
    )
                      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry_run", action="store_true", help="perform dry run only")
    parser.add_argument("scene_list_filename", help="json file contain scene data")
    parser.add_argument(
        "scenes_listeners_filename",
        help="json file containing scenes to listeners mapping",
    )
    parser.add_argument("input_path", help="path to input data")
    parser.add_argument("output_path", help="path to output data")
    args = parser.parse_args()

    scene_list = json.load(open(args.scene_list_filename, "r"))
    scenes_listeners = json.load(open(args.scenes_listeners_filename, "r"))

    for scene in tqdm(scene_list):
        for listener_name in scenes_listeners[scene["scene"]]:
            run_HA_postprocessing(
                scene,
                listener_name,
                args.input_path,
                args.output_path,
                CONFIG.fs,
                CONFIG.latency,
                dry_run=args.dry_run,
            )



  