"""Global configuration."""

import os
import logging
import configparser
import json


class ClarityConfig(configparser.ConfigParser):
    def getlist(self, section, key, fallback=None):
        value = self.get(section, key, fallback=fallback)
        if isinstance(value, str):
            value = json.loads(value)
        return value

    def __init__(self, config_filename):

        super(ClarityConfig, self).__init__(
            allow_no_value=True, inline_comment_prefixes=("#")
        )
        if config_filename and os.path.exists(config_filename):
            self.clarity_cfg = os.path.abspath(config_filename)
            self.read(self.clarity_cfg)
        else:
            raise Exception(
                "File clarity.cfg not found. Check that CLARITY_ROOT is set correctly."
            )
        FORMAT = "%(levelname)s:%(funcName)s: %(message)s"
        logging_level = self.get("clarity", "LOGGING_LEVEL", fallback="INFO")
        logging.basicConfig(level=logging_level, format=FORMAT)

        self.fs = self.getint("clarity", "CLARITY_FS")
        self.latency = self.getfloat("clarity", "LATENCY")
        self.output_gain_constant = self.getfloat("clarity", "OUTPUT_GAIN_CONSTANT")
        self.pre_duration = self.getfloat("clarity", "PRE_DURATION")
        self.post_duration = self.getfloat("clarity", "POST_DURATION")
        self.tail_duration = self.getfloat("clarity", "TAIL_DURATION")
        self.ramp_duration = self.getfloat("clarity", "RAMP_DURATION")
        self.default_cfs = self.getlist("clarity", "DEFAULT_CFS")
        self.noisegatelevels = self.getlist("clarity", "NOISEGATELEVELS")
        self.noisegateslope = self.getint("clarity", "NOISEGATESLOPE")
        self.cr_level = self.getint("clarity", "CR_LEVEL")
        self.max_output_level = self.getint("clarity", "MAX_OUTPUT_LEVEL")
        self.ahr = self.getint("clarity", "AHR")
        self.cfg_file = self.get("clarity", "CFG_FILE")
        self.calib_dB_SPL = self.getint("clarity", "CALIB_DB_SPL")
        self.ref_RMS_dB = self.getfloat("clarity", "REF_RMS_DB")
        self.equiv0dBSPL = self.getfloat("clarity", "equiv0dBSPL")
        self.calib = self.getboolean("clarity", "CALIB")
        self.N_listeners_scene = self.getint("clarity", "N_LISTENERS_SCENE")
        #        self.speech_SNRS = self.getlist("clarity", "SPEECHINT_SNRS", fallback=[0, 10])
        #        self.nonspeech_SNRS = self.getlist(
        #            "clarity", "NONSPEECHINT_SNRS", fallback=[0, 10]
        #        )
        # self.addnoise = self.getint("clarity", "ADDNOISE", fallback=0)
        # self.norm_lufs = self.getint("clarity", "NORM_LUFS", fallback=-12)
        # self.clip_limit = self.getint("clarity", "CLIP_LIMIT", fallback=1)


config_filename = None
if "CLARITY_ROOT" in os.environ:
    config_filename = f"{os.environ['CLARITY_ROOT']}/clarity.cfg"
CONFIG = ClarityConfig(config_filename)