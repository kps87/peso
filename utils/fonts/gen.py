import os

from matplotlib import font_manager

from service.logging import Log
from service.parser import PlainTextParser
from service.writer import PlainTextWriter

logger = Log.get_logger(os.path.basename(__file__))


def run():

    available_fonts = sorted([f for f in font_manager.fontManager.get_font_names()])
    filename = "./utils/fonts/template.dat"
    reader = PlainTextParser(filename)
    contents = reader.read()

    files = {}
    output_directory = os.path.join(os.getcwd(), "inputs")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    for font in available_fonts:
        lines = contents.copy()
        file = os.path.join(output_directory, "font-test-" + font + ".dat")
        lines.append("label-font " + font)
        files[file] = lines

    for file in files:
        w = PlainTextWriter(files[file])
        w.write(file)


if __name__ == "__main__":
    run()
