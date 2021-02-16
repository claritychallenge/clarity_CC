import os
import shutil
from jinja2 import Environment, FileSystemLoader
import logging

from clarity_core.config import CONFIG


def create_configured_cfgfile(
    input_file,
    output_file,
    formatted_sGt,
    cfg_file,
    ahr,
):
    """Using Jinja2, generates cfg file for given configuration.

    Creates template output file and configures with correct filenames, peak level
    out and DC gaintable.

    Args:
        input_file (str): file to process
        output_file (str): file in which to store processed file
        formatted_sGt (ndarray): gaintable formatted for input into cfg file
        ahr (int): amplification headroom

    Returns:
        cfg_filename (str): cfg filename
    """

    if CONFIG.fs != 44100:
        logging.error("Current GHA configuration requires 44.1kHz sampling rate.")

    # Get path to GHA
    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    # Define cfg filenames
    input_cfg_filename = cfg_file + "_template.cfg"
    output_cfg_filename = f"{dirname}/cfg_files/{cfg_file}_templatemod.cfg"
    cfg_filename = output_cfg_filename.split("/")[-1]

    # Read new file and replace any parameter values necessary
    # Update peaklevel out by adding headroom
    logging.info(f"Adding {ahr} dB headroom")

    peaklevel_in = int(CONFIG.equiv0dBSPL)
    peaklevel_out = int(CONFIG.equiv0dBSPL + ahr)

    # Render jinja2 template
    file_loader = FileSystemLoader(dirname + "/cfg_files")
    env = Environment(loader=file_loader)
    template = env.get_template(input_cfg_filename)
    output = template.render(
        io_in=input_file,
        io_out=output_file,
        peaklevel_in=f"[{peaklevel_in} {peaklevel_in} {peaklevel_in} {peaklevel_in}]",
        peaklevel_out=f"[{peaklevel_out} {peaklevel_out}]",
        gtdata=formatted_sGt,
    )

    with open(output_cfg_filename, "w") as fo:
        fo.write(output)

    return cfg_filename
