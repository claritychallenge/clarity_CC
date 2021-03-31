import logging
import subprocess
import tempfile
import numpy as np
import os

import GHA
from clarity_core.HearingAid import HearingAid
import clarity_core.signal as ccs
from clarity_core.config import CONFIG


class GHAHearingAid(HearingAid):
    def __init__(self, fs, channels=None):
        super().__init__(fs, channels)
        self.ahr = CONFIG.ahr
        self.audf = CONFIG.default_cfs
        self.cfg_file = CONFIG.cfg_file
        self.noisegatelevels = CONFIG.noisegatelevels
        self.noisegateslope = CONFIG.noisegateslope
        self.cr_level = CONFIG.cr_level
        self.max_output_level = CONFIG.max_output_level

    def set_listener(self, listener):
        self.listener = listener

    def set_ahr(self, ahr):
        self.ahr = ahr

    def set_cfg_file(self, cfg_file):
        self.cfg_file = cfg_file

    def set_audf(self, audf):
        self.audf = audf

    def set_noisegatelevels(self, noisegatelevels):
        self.noisegatelevels = noisegatelevels

    def set_noisegateslope(self, noisegateslope):
        self.noisegateslope = noisegateslope

    def set_cr_level(self, cr_level):
        self.cr_level = cr_level

    def set_max_output_level(self, max_output_level):
        self.max_output_level = max_output_level

    def process_files(self, infile_names, outfile_name):
        """Process a set of input signals and generate an output.

        Args:
            infile_names (list[str]): List of input wav files. One stereo wav
                file for each hearing device channel
            outfile_name (str): File in which to store output wav files
            dry_run (bool): perform dry run only
        """
        dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

        logging.info(f"Processing {outfile_name} with listener {self.listener}")
        audiogram = GHA.audiogram(self.listener)
        logging.info(f"Audiogram severity is {audiogram.severity}")
        audiogram = audiogram.select_subset_of_cfs(self.audf)

        # Get gain table with noisegate correction
        gaintable = GHA.get_gaintable(
            audiogram,
            self.noisegatelevels,
            self.noisegateslope,
            self.cr_level,
            self.max_output_level,
        )
        formatted_sGt = GHA.format_gaintable(gaintable, noisegate_corr=True)

        cfg_template = f"{dirname}/cfg_files/{self.cfg_file}_template.cfg"

        # Merge CH1 and CH3 files. This is the baseline configuration.
        # CH2 is ignored.
        merged_filename = tempfile.mkstemp(prefix="clarity-merged-", suffix=".wav")[1]
        ccs.create_HA_inputs(infile_names, merged_filename)

        # Create the openMHA config file from the template
        cfg_filename = tempfile.mkstemp(prefix="clarity-openmha-", suffix=".cfg")[1]
        with open(cfg_filename, "w") as f:
            f.write(
                GHA.create_configured_cfgfile(
                    merged_filename,
                    outfile_name,
                    formatted_sGt,
                    cfg_template,
                    self.ahr,
                )
            )

        # Process file using configured cfg file
        # Suppressing OpenMHA output with -q - comment out when testing
        # Append log of OpenMHA commands to /cfg_files/logfile
        subprocess.run(
            [
                "mha",
                "-q",
                "--log=logfile.txt",
                f"?read:{cfg_filename}",
                "cmd=start",
                "cmd=stop",
                "cmd=quit",
            ]
        )

        # Delete temporary files.
        os.remove(merged_filename)
        os.remove(cfg_filename)

        # Check output signal has energy in every channel
        sig = ccs.read_signal(outfile_name)

        if len(np.shape(sig)) == 1:
            sig = np.expand_dims(sig, axis=1)

        if not np.all(np.sum(abs(sig), axis=0)):
            raise ValueError(f"Channel empty.")

        ccs.write_signal(outfile_name, sig, CONFIG.fs, floating_point=True)

        logging.info("OpenMHA processing complete")
