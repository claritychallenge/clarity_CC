"""Representation of HearingAid and DummyHearingAid example."""

from abc import ABC, abstractmethod
import logging
import numpy as np

from clarity_core.signal import read_signal, write_signal


class HearingAid(ABC):
    """Representation of a hearing aid."""

    def __init__(self, fs, channels=None):
        self.fs = fs
        if channels is None:
            channels = [1]
        self.channels = channels

    def set_listener(self, listener):
        self.listener = listener

    def process_scene(self, scene, input_path, output_path, dry_run):
        """Run baseline HA processing.

        Baseline simply averages the channels.

        Args:
            scene (dict): dictionary defining the scene to be generated
            listener (dict): dictionary containing listener data
            input_path (str): path to the input data
            output_path (str): path to the output data
            fs (float): sampling rate
            dry_run (bool, optional): run in dry-run mode (default: False)
            channels (list, optional): list of HA channels to process (default: 1 channel)

        """
        logging.debug(f"Running HA processing: Listener {self.listener['id']}")
        logging.debug("Listener data")
        logging.debug(self.listener["id"])

        infile_names = [
            f"{input_path}/{scene['scene']}_mixed_CH{channel}.wav"
            for channel in self.channels
        ]
        outfile_name = (
            f"{output_path}/{scene['scene']}_{self.listener['id']}_HA-output.wav"
        )

        # Check infiles exist

        # Run the processing
        if not dry_run:
            self.process_files(infile_names, outfile_name)

    @abstractmethod
    def process_files(self, infile_names, outfile_name):
        pass


class SignalInterfaceMixin(ABC):
    def process_files(self, infile_names, outfile_name):
        """Process signals in infiles and write result to outfile."""
        signals = [read_signal(infile) for infile in infile_names]
        output_signal = self.process_signals(signals)
        write_signal(
            outfile_name,
            output_signal,
            self.fs,
            floating_point=True,
        )

    @abstractmethod
    def process_signals(self, signals):
        pass


class DummyHearingAid(SignalInterfaceMixin, HearingAid):
    def __init__(self, fs, channels=None):
        super().__init__(fs, channels)

    def process_signals(self, signals):
        return np.mean(np.array(signals), axis=0)
