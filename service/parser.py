import os.path
from typing import Tuple

import pandas as pd
from service.logging import Log

logger = Log.get_logger(os.path.basename(__file__))


class PlainTextParser:

    def __init__(self, filename: str | None):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, filename: str):
        self._filename = filename

    def read(self) -> list[str]:
        with open(self.filename, "r") as file:
            content = file.read().splitlines()
        file.close()
        return content


class PESInputFileParser:

    def __init__(self):
        self._parser = PlainTextParser(filename=None)

    @property
    def parser(self):
        return self._parser

    @parser.setter
    def parser(self, parser):
        self._parser = parser

    @classmethod
    def get_input_files(cls, path: str) -> list[str]:
        logger.info("Reading all .dat files in dir {}".format(path))
        files = sorted(
            [
                os.path.join(path, file)
                for file in os.listdir(path)
                if file.endswith(".dat")
            ]
        )
        [logger.info("Found file: {}".format(file)) for file in files]
        return files

    @classmethod
    def process_reaction_format(cls, options: dict[str, any]) -> dict[str, any]:

        fopts = {}
        if "reactionFormat" in options:
            lines = list(
                filter(lambda x: any(y.isalnum() for y in x), options["reactionFormat"])
            )
            for line in lines:
                rxn, *options = line.split()
                options = {
                    options[i]: options[i + 1] for i in range(0, len(options), 2)
                }
                if rxn not in fopts:
                    fopts[rxn] = options
                else:
                    fopts[rxn].update(options)

        for rxn in fopts:
            for opt in fopts[rxn]:
                logger.info(
                    "Custom format specification for reaction {}: {}={}".format(
                        rxn, opt, fopts[rxn][opt]
                    )
                )
        return fopts

    @classmethod
    def process_global_format_options(cls, options: dict[str, any]) -> dict[str, any]:

        fopts = {"global": {}}
        if "global" in options:
            lines = list(
                filter(lambda x: any(y.isalnum() for y in x), options["global"])
            )
            for line in lines:
                options = line.split()
                if options[0] == "label-font":
                    options = {"label-font": " ".join(options[1:])}
                else:
                    options = {
                        options[i]: options[i + 1] for i in range(0, len(options), 2)
                    }
                fopts["global"].update(options)

        for opt in fopts["global"]:
            logger.info(
                "Global format specification: {}={}".format(opt, fopts["global"][opt])
            )
        return fopts

    @classmethod
    def parse_sections(cls, content: list[str]) -> dict:
        sections = {}
        if content is not None:
            section = None
            for line in content:
                if "section:" in line:
                    _, section = line.split(":")
                    section = section.strip()
                    sections[section] = []
                elif any(char.isalnum() for char in line) and line.strip()[0] != "#":
                    sections[section].append(line)
        return sections

    def read_input_file(self, filename: str) -> Tuple[pd.DataFrame, dict[str, any]]:
        if os.path.isfile(filename):
            logger.info("Reading input file {}".format(filename))
            self.parser.filename = filename
            content = self.parser.read()
            sections = self.parse_sections(content)

            df = pd.DataFrame(
                [line.split() for line in sections["pes"][1:]],
                columns=sections["pes"][0].split(),
            )
            df["energy"] = df["energy"].astype(float)
            fopts = PESInputFileParser.process_reaction_format(sections)
            global_opts = PESInputFileParser.process_global_format_options(sections)
            fopts.update(global_opts)
            return df, fopts
        else:
            logger.fatal("Filename {} is not present".format(filename))
            exit()
