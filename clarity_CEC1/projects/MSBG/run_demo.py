#!/usr/bin/env python
import sys
from pathlib import Path
from scipy.io import wavfile
import logging

import MSBG
import clarity_core.signal as ccs
from clarity_core.config import CONFIG


def run_demo(input_filename, outputfilename):
    """Demo of using MSBG to process a signal according to various
    levels of hearing impairment, as specified by audiograms.

    Arguments:
        input_filename {str} -- Name of the input wav file
        output_filename {str} -- Stem name of output wav files
    """

    signal = ccs.read_signal(input_filename)
    logging.info(f"Signal shape is {signal.shape}")
    # Make the list of ears. Each has a different audiogram.
    audiograms = MSBG.audiogram.standard_audiograms()
    ears = [MSBG.Ear(audiogram=audiogram, src_pos="ff") for audiogram in audiograms]

    # process the signal with each ear in the list of ears
    outputs = [ear.process(signal, add_calibration=True) for ear in ears]

    # Output the signals
    for i, output in enumerate(outputs):
        outfile = Path(outputfilename)
        ccs.write_signal(
            f"{outfile.parent}/{outfile.stem}_{i}.wav",
            output[0],
            CONFIG.fs,
            floating_point=True,
        )


if __name__ == "__main__":
    n_args = len(sys.argv)
    infile = sys.argv[1] if n_args >= 2 else "MATLAB/male_01_44d1k.wav"
    outfile = sys.argv[2] if n_args >= 3 else "tmp/demo.wav"
    run_demo(infile, outfile)

# python run_demo.py <input_filename> <output_filename>
#
# e.g. python run_demo.py MATLAB/male_01_44d1k.wav tmp/demo.wav
#
# pycallgraph -e "__main__" -i "MSBG*" -i "Audiogram*" --max-depth 7 graphviz  -f dot -- ./run_demo.py
# mv pycallgraph.png pycallgraph.dot; dot -Tpdf pycallgraph.dot -o pycallgraph.pdf
# http://graphviz.it/#/gallery/abstract.gv
