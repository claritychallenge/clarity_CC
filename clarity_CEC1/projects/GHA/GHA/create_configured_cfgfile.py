import pathlib
from jinja2 import Environment, FileSystemLoader
import logging

from clarity_core.config import CONFIG


def create_configured_cfgfile(
    input_file,
    output_file,
    formatted_sGt,
    cfg_template_file,
    ahr,
):
    """Using Jinja2, generates cfg file for given configuration.

    Creates template output file and configures with correct filenames, peak level
    out and DC gaintable.

    Args:
        input_file (str): file to process
        output_file (str): file in which to store processed file
        formatted_sGt (ndarray): gaintable formatted for input into cfg file
        cfg_template_file: configuration file template
        ahr (int): amplification headroom

    Returns:
        cfg_filename (str): cfg filename
    """

    if CONFIG.fs != 44100:
        logging.error("Current GHA configuration requires 44.1kHz sampling rate.")

    cfg_template_file = pathlib.Path(cfg_template_file)

    # Define cfg filenames
    # Read new file and replace any parameter values necessary
    # Update peaklevel out by adding headroom
    logging.info(f"Adding {ahr} dB headroom")

    peaklevel_in = int(CONFIG.equiv0dBSPL)
    peaklevel_out = int(CONFIG.equiv0dBSPL + ahr)

    # Render jinja2 template
    file_loader = FileSystemLoader(cfg_template_file.parent)
    env = Environment(loader=file_loader)
    template = env.get_template(cfg_template_file.name)
    output = template.render(
        io_in=input_file,
        io_out=output_file,
        peaklevel_in=f"[{peaklevel_in} {peaklevel_in} {peaklevel_in} {peaklevel_in}]",
        peaklevel_out=f"[{peaklevel_out} {peaklevel_out}]",
        gtdata=formatted_sGt,
    )

    return output
