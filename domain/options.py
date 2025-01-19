import os
from enum import Enum
from typing import Optional

from service.logging import Log

logger = Log.get_logger(os.path.basename(__file__))


class OptionType(Enum):
    KEYWORD = "keyword"
    GLOBAL = "global"


class Option(Enum):
    COLOR = "color"
    LINESTYLE = "linestyle"
    LINEWIDTH = "linewidth"
    LABEL = "label"
    LABEL_FONT = "label-font"
    PAD_BIMOLECULAR = "pad-bimolecular"
    RESOLUTION = "resolution"
    FONT = "label-font"
    COLORMAP = "colormap"
    SHOW_LABELS = "show-labels"
    LABEL_LOCATION = "label-loc"


class OptionDefinition:

    def __init__(
        self, type: OptionType, option: Option, key: Optional[str], value: any
    ):
        self._type = type
        self._option = option
        self._key = key
        self._value = value

    @property
    def type(self) -> OptionType:
        return self._type

    @type.setter
    def type(self, type: OptionType):
        self._type = type

    @property
    def option(self) -> Option:
        return self._option

    @option.setter
    def option(self, option: Option):
        self._option = option

    @property
    def key(self) -> any:
        return self._key

    @key.setter
    def key(self, key: any):
        self._key = key

    @property
    def value(self) -> any:
        return self._value

    @value.setter
    def value(self, value: any):
        self._value = value


class OptionsManager:

    def __init__(self, options: list[OptionDefinition]):
        if options is not None:
            self._options = options
        else:
            self._options = []

    @property
    def options(self) -> list[OptionDefinition]:
        return self._options

    @options.setter
    def options(self, options: list[OptionDefinition]):
        self._options = options

    def option_from_string(self, option: str) -> Option:
        try:
            return Option(option.lower())
        except:
            logger.fatal("Unknown option {}".format(option))
            exit()

    def has_option(self, option: OptionDefinition) -> bool:
        options = list(
            filter(
                lambda x: x.type == option.type and x.key == option.key, self.options
            )
        )
        return True if len(options) > 0 else False

    def get_option(self, option: OptionDefinition) -> Optional[OptionDefinition]:
        options = list(
            filter(
                lambda x: x.type == option.type
                and x.option == option.option
                and x.key == option.key,
                self.options,
            )
        )
        return options[0] if len(options) > 0 else None

    def get_keyword_option(
        self, key: str, option: Option
    ) -> Optional[OptionDefinition]:
        options = list(
            filter(
                lambda x: x.type == OptionType.KEYWORD
                and x.option == option
                and x.key == key,
                self.options,
            )
        )
        return options[0] if len(options) > 0 else None

    def get_global_option(self, option: Option) -> Optional[OptionDefinition]:
        options = list(
            filter(
                lambda x: x.type == OptionType.GLOBAL and x.option == option,
                self.options,
            )
        )
        return options[0] if len(options) > 0 else None

    def get_option_type(self, option_type: OptionType) -> list[OptionDefinition]:
        return list(filter(lambda x: x.type == option_type, self.options))

    def add_option(self, option: OptionDefinition) -> None:
        if self.get_option(option) is None:
            self._options.append(option)

    def keyword_options_from_list(self, lines: list[str]) -> None:
        for line in lines:
            key, *options = line.split()
            options = {options[i]: options[i + 1] for i in range(0, len(options), 2)}
            for option, value in options.items():
                self.add_option(
                    OptionDefinition(
                        type=OptionType.KEYWORD,
                        option=self.option_from_string(option),
                        key=key,
                        value=value,
                    )
                )

    def global_options_from_list(self, lines: list[str]) -> None:
        for line in lines:
            options = line.split()
            if options[0] == "label-font":
                options = {"label-font": " ".join(options[1:])}
            else:
                options = {
                    options[i]: options[i + 1] for i in range(0, len(options), 2)
                }

            for option, value in options.items():
                self.add_option(
                    OptionDefinition(
                        type=OptionType.GLOBAL,
                        option=self.option_from_string(option),
                        key=None,
                        value=value,
                    )
                )

    def log(self) -> None:
        [
            logger.info(
                "{} option for {}: {}={}".format(
                    x.type.value, x.key, x.option.value, x.value
                )
            )
            for x in self.get_option_type(OptionType.KEYWORD)
        ]
        [
            logger.info("{} option {}={}".format(x.value, x.option.value, x.value))
            for x in self.get_option_type(OptionType.GLOBAL)
        ]
