import os.path
import click
from domain.pes import StationaryPoint, PES
from service.parser import *
from service.grid import PESGridEnhancer
from service.plotter import Plotter
from service.logging import title, Log
from typing import Tuple

logger = Log.get_logger(os.path.basename(__file__))


def configure_io(output_file: str) -> str:
    # input directory/file setup
    output_dir = os.path.join(os.getcwd(), "outputs")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    logger.info("Will write outputs to {}".format(output_dir))
    logger.info("Output file: {}".format(output_file))
    output_file = os.path.join(output_dir, output_file)
    return output_file


def process_inputs(input_file: str) -> Tuple[PES, dict]:
    logger.info("Processing input file {}".format(input_file))
    parser = PESInputFileParser()
    data, fopts = parser.read_input_file(input_file)
    surface = PES.from_dataframe(data)
    for sp in surface.minima + surface.ts:
        sp: StationaryPoint
        logger.info("Stationary point: {} {} {}".format(sp.name, sp.energy, sp.sptype))
    for rxn in surface.reactions:
        logger.info("Reaction: {}".format(rxn.get_name()))
    return surface, fopts


def runner(input_file: str, output_file: str) -> None:
    output_file = configure_io(output_file)

    # run the pes plotter
    surface, fopts = process_inputs(input_file)
    PESGridEnhancer.enhance_surface(surface)
    Plotter(surface, output_file, fopts).plot()


@click.command()
@click.option("-i", "--input-file", default="pes.dat", help="Path to your input file.")
@click.option(
    "-o",
    "--output-file",
    default="pes.png",
    help="Path to your output file.",
)
def run(input_file: str, output_file: str) -> None:
    runner(input_file, output_file)


@click.command()
@click.option(
    "-i",
    "--input-dir",
    default="./inputs/",
    help="Path to a folder containing your input files.",
)
def run_all(input_dir: str) -> None:
    files = PESInputFileParser.get_input_files(input_dir)
    for file in files:
        try:
            runner(file, os.path.split(file)[-1].replace(".dat", ".png"))
        except Exception as e:
            logger.error("Error processing file: {} {}".format(file, e))


@click.group()
def cli() -> None:
    pass


# Add commands to the group
cli.add_command(run_all)
cli.add_command(run)

if __name__ == "__main__":
    title()
    cli()
