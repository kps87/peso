import os.path
from typing import Tuple

import pandas as pd

from domain.options import OptionDefinition, OptionsManager
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
    def process_reaction_format(cls, options: dict[str, any]) -> list[OptionDefinition]:

        opt_mgr = OptionsManager(options=[])
        if "reactionFormat" in options:
            lines = list(
                filter(lambda x: any(y.isalnum() for y in x), options["reactionFormat"])
            )

            opt_mgr.keyword_options_from_list(lines)
        return opt_mgr.options

    @classmethod
    def process_global_format_options(
        cls, options: dict[str, any]
    ) -> list[OptionDefinition]:

        opt_mgr = OptionsManager(options=[])
        if "global" in options:
            lines = list(
                filter(lambda x: any(y.isalnum() for y in x), options["global"])
            )
            opt_mgr.global_options_from_list(lines)
        return opt_mgr.options

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

    def read_input_file(self, filename: str) -> Tuple[pd.DataFrame, OptionsManager]:
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
            reac_opts = PESInputFileParser.process_reaction_format(sections)
            global_opts = PESInputFileParser.process_global_format_options(sections)
            opt_mgr = OptionsManager(options=reac_opts + global_opts)
            opt_mgr.log()
            return df, opt_mgr
        else:
            logger.fatal("Filename {} is not present".format(filename))
            exit()
