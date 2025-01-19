import os

from matplotlib import font_manager

from service.logging import Log
from service.writer import PlainTextWriter

logger = Log.get_logger(os.path.basename(__file__))


def run():
    available_fonts = sorted([f for f in font_manager.fontManager.get_font_names()])
    for font in available_fonts:
        logger.info("Font: {}".format(font))
    w = PlainTextWriter(available_fonts)
    w.write("fonts.txt")


if __name__ == "__main__":
    run()
