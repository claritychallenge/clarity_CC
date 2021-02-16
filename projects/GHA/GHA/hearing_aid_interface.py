import logging
import subprocess
import tempfile
import numpy as np
import os
from scipy.io import wavfile

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

        # Merge CH1 and CH3 files
        merged_filename = tempfile.gettempdir() + "/merged.wav"
        if (infile_names[0][-7:-4] in "CH1" == False) or (
            infile_names[2][-7:-4] in "CH3" == False
        ):
            logging.error("GHA infile_names are incorrect.")
        cmd = f"sox -M -V1 -v 1 {infile_names[0]} -v 1 {infile_names[2]} {merged_filename}"
        subprocess.call(cmd, shell=True)

        cfg_filename = GHA.create_configured_cfgfile(
            merged_filename,
            outfile_name,
            formatted_sGt,
            self.cfg_file,
            self.ahr,
        )

        # Start setting up command for subprocess and OpenMHA
        # Create read command with correct cfg filename
        cfg_filename = dirname + "/cfg_files/" + cfg_filename
        maincmd = f"?read:{cfg_filename}"
        # # Save configuration and contents of monitor variables to text file
        # logcmd_config = (
        #     "?save:"
        #     + dirname
        #     + "/cfg_files/log/"
        #     + outfile_name.split("/")[-1][:-4]
        #     + "_config.txt"
        # )
        # logcmd_mons = (
        #     "?savemons:"
        #     + dirname
        #     + "/cfg_files/log/"
        #     + outfile_name.split("/")[-1][:-4]
        #     + "_mons.txt"
        # )

        # Process file using configured cfg file
        # Suppressing OpenMHA output with -q - comment out when testing
        # Append log of OpenMHA commands to /cfg_files/logfile
        subprocess.run(
            [
                "mha",
                "-q",
                "--log=logfile.txt",
                maincmd,
                "cmd=start",
                "cmd=stop",
                # logcmd_config,
                # logcmd_mons,
                "cmd=quit",
            ]
        )

        # Delete temporary signals created by sox.
        subprocess.call(["rm", "-r", merged_filename])

        # Check output signal has energy in every channel
        sig = ccs.read_signal(outfile_name)

        if len(np.shape(sig)) == 1:
            sig = np.expand_dims(sig, axis=1)

        if not np.all(np.sum(abs(sig), axis=0)):
            raise ValueError(f"Channel empty.")

        ccs.write_signal(outfile_name, sig, CONFIG.fs, floating_point=True)

        logging.info("OpenMHA processing complete")
