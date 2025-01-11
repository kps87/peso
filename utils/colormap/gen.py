import os
from service.parser import PlainTextParser
from service.writer import PlainTextWriter
from utils.colormap.list import run as get_cmaps


def run():

    colors = get_cmaps()
    filename = "./utils/colormap/template.dat"
    reader = PlainTextParser(filename)
    contents = reader.read()

    files = {}
    output_directory = os.path.join(os.getcwd(), "inputs")
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    for color in colors:
        lines = contents.copy()
        file = os.path.join(output_directory, "colormap-test-" + color + ".dat")
        lines.append("colormap " + color)
        files[file] = lines

    for file in files:
        w = PlainTextWriter(files[file])
        w.write(file)


if __name__ == "__main__":
    run()
