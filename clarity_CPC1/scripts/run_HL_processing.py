import argparse
import json
import numpy as np
import logging
from tqdm import tqdm
import sys
from scipy.signal import unit_impulse, resample
from soundfile import SoundFile

from clarity_core.config import CONFIG

from clarity_core.signal import read_signal, write_signal, pad

sys.path.append("../projects/MSBG")
import MSBG


def listen(signal, ears):
    outputs = [
        ear.process(
            signal[:, i],
            add_calibration=CONFIG.calib,
        )
        for i, ear in enumerate(ears)
    ]

    # Fix length difference if no smearing on one of two ears
    if len(outputs[0][0]) != len(outputs[1][0]):
        diff = len(outputs[0][0]) - len(outputs[1][0])
        if diff > 0:
            outputs[1][0] = np.flipud(pad(np.flipud(outputs[1][0]), len(outputs[0][0])))
        else:
            outputs[0][0] = np.flipud(pad(np.flipud(outputs[0][0]), len(outputs[1][0])))

    return np.squeeze(outputs).T


def run_HL_processing(scene, listener, system, scenes_input_path, ha_input_path, output_path, fs):
    """Run baseline HL processing.

    Applies the MSBG model of hearing loss.

    Args:
        scene (dict): dictionary defining the scene to be generated
        listener (dict): dictionary containing listener data
        scenes_input_path (str): path to the scenes input data
        ha_input_path (str): path to the ha input data
        output_path (str): path to the output data
        fs (float): sampling rate
    """
    logging.debug(f"Running HL processing: Listener {listener['name']}")
    logging.debug("Listener data")
    logging.debug(listener)

    # Get audiogram centre frequencies
    cfs = np.array(listener["audiogram_cfs"])

    # Read HA output and mixed signals
    # Hearing loss model assumes a 44.1 (CONFIG.fs) sampling rate.
    # Signals provided used in the listening tests were sampled at 32 kHz.
    filename = f"{ha_input_path}/{scene}_{listener['name']}_{system}.wav"
    wave_file = SoundFile(filename)
    signal = wave_file.read()
    signal = resample(signal, int(CONFIG.fs * signal.shape[0] / wave_file.samplerate))

    mixture_signal = read_signal(f"{scenes_input_path}/{scene}_mixed_CH0.wav")

    # Create discrete delta function (DDF) signal for time alignment
    ddf_signal = np.zeros((np.shape(signal)))
    ddf_signal[:, 0] = unit_impulse(len(signal), int(fs / 2))
    ddf_signal[:, 1] = unit_impulse(len(signal), int(fs / 2))

    # Get flat-0dB ear audiograms
    flat0dB_audiogram = MSBG.Audiogram(cfs=cfs, levels=np.zeros((np.shape(cfs))))
    flat0dB_ear = MSBG.Ear(audiogram=flat0dB_audiogram, src_pos="ff")

    # For flat-0dB audiograms, process the signal with each ear in the list of ears
    flat0dB_HL_outputs = listen(signal, [flat0dB_ear, flat0dB_ear])

    # Get listener audiograms and build a pair of ears
    audiogram_left = np.array(listener["audiogram_levels_l"])
    left_audiogram = MSBG.Audiogram(cfs=cfs, levels=audiogram_left)
    audiogram_right = np.array(listener["audiogram_levels_r"])
    right_audiogram = MSBG.Audiogram(cfs=cfs, levels=audiogram_right)
    audiograms = [left_audiogram, right_audiogram]
    ears = [MSBG.Ear(audiogram=audiogram, src_pos="ff") for audiogram in audiograms]

    # Process the HA output signal, the raw mixed signal, and the ddf signal
    outputs = listen(signal, ears)
    mixture_outputs = listen(mixture_signal, ears)
    ddf_outputs = listen(ddf_signal, ears)

    # Write the outputs
    outfile_stem = f"{output_path}/{scene}_{listener['name']}_{system}"
    signals_to_write = [
        (
            flat0dB_HL_outputs,
            f"{output_path}/{scene}_flat0dB_HL-output.wav",
        ),
        (outputs, f"{outfile_stem}_HL-output.wav"),
        (ddf_outputs, f"{outfile_stem}_HLddf-output.wav"),
        (mixture_outputs, f"{outfile_stem}_HL-mixoutput.wav"),
    ]
    for signal, filename in signals_to_write:
        write_signal(filename, signal, CONFIG.fs, floating_point=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--nsignals", type=int, default=None)
    parser.add_argument("scene_list_filename", help="json file containing scene data")
    parser.add_argument("listener_filename", help="json file containing listener data")
    parser.add_argument("signals_filename", help="json file containing signal_metadata")

    parser.add_argument("scenes_input_path", help="path to unprocessed scene input data")
    parser.add_argument("ha_input_path", help="path to processed HA input data")
    parser.add_argument("output_path", help="path to output data")
    args = parser.parse_args()

    scene_list = json.load(open(args.scene_list_filename, "r"))
    listeners = json.load(open(args.listener_filename, "r"))
    signals = json.load(open(args.signals_filename, "r"))

    # Process the first n signals if the nsignals parameter is set
    if args.nsignals and args.nsignals > 0:
        signals = signals[0 : args.nsignals]

    for signal in tqdm(signals):
        scene = signal["scene"]
        listener = listeners[signal["listener"]]
        system = signal["system"]

        run_HL_processing(
            scene,
            listener,
            system,
            args.scenes_input_path,
            args.ha_input_path,
            args.output_path,
            CONFIG.fs,
        )
