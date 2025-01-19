import os

from service.logging import Log
from service.plotter import PlotterUtils
from service.writer import PlainTextWriter

logger = Log.get_logger(os.path.basename(__file__))


def run():
    colors = PlotterUtils.get_supported_colormaps()
    for color in colors:
        logger.info("Available colormap: {}".format(color))
    w = PlainTextWriter(colors)
    w.write("colormaps.txt")
    return colors


if __name__ == "__main__":
    run()
