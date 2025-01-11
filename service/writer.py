import os
from service.logging import Log

logger = Log.get_logger(os.path.basename(__file__))


class PlainTextWriter:

    def __init__(self, contents):
        self._contents = contents

    def write(self, filename: str):
        logger.info("Writing file: {}".format(filename))
        with open(filename, "w") as file:
            for line in self._contents:
                file.write(line)
                file.write("\n")
        file.close()
