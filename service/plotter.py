import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from domain.options import Option, OptionsManager
from domain.pes import PES, Reaction, StationaryPoint
from service.logging import Log

logger = Log.get_logger(os.path.basename(__file__))


class PlotterUtils:
    @classmethod
    def create_figure(cls, xlabel: str = "x", ylabel: str = "y", title: str = "title"):
        figure, axis = plt.subplots()
        axis.set_ylabel(ylabel)
        axis.set_xlabel(xlabel)
        plt.title(title)
        plt.tight_layout()
        return figure, axis

    @classmethod
    def save_image(
        cls, output_filename: str, figure: any, img_frmt="png", dpi: int = 400
    ):
        logger.info("Saving image {}".format(output_filename))
        plt.savefig(output_filename, bbox_inches="tight", format=img_frmt, dpi=dpi)
        plt.close(figure)
        cls.close_image(figure)

    @classmethod
    def close_image(cls, figure) -> None:
        figure.clf()

    @classmethod
    def close_all(cls) -> None:
        plt.close("all")
        plt.close(plt.gcf())

    @classmethod
    def get_supported_colormaps(cls) -> list[str]:
        return ["brg", "winter", "spring", "viridis", "hsv"]

    @classmethod
    def colormap_dictionary_from_array(
        cls, array: list[any], mtype: str = "brg"
    ) -> dict[any, any]:
        colors = [(0, 0, 0)] * len(array)
        if mtype in cls.get_supported_colormaps():
            if mtype == "brg":
                colors = cm.brg(np.linspace(0, 1, len(array)))
            elif mtype == "winter":
                colors = cm.winter(np.linspace(0.5, 1, len(array)))
            elif mtype == "spring":
                colors = cm.spring(np.linspace(0, 1, len(array)))
            elif mtype == "viridis":
                colors = cm.viridis(np.linspace(0, 1, len(array)))
            elif mtype == "hsv":
                colors = cm.hsv(np.linspace(0.2, 0.8, len(array)))
        cmap = {}
        i = 0
        for element in array:
            cmap[element] = colors[i]
            i += 1
        return cmap

    @classmethod
    def set_title(cls, title: str) -> None:
        plt.title(title)

    @classmethod
    def show_grid(cls) -> None:
        plt.grid(color="0.25")

    @classmethod
    def show(cls) -> None:
        plt.show()


class Plotter:
    def __init__(self, surface: PES, output_file: str, options: OptionsManager):
        self._surface = surface
        self._output_file = output_file
        self._options = options
        self._energy_range = None
        self._vertical_annotation_offset = None
        self._annotations = []

    @property
    def surface(self) -> PES:
        return self._surface

    @surface.setter
    def surface(self, surface: PES):
        self._surface = surface

    @property
    def output_file(self) -> str:
        return self._output_file

    @output_file.setter
    def output_file(self, output_file: str):
        self._output_file = output_file

    @property
    def options(self) -> OptionsManager:
        return self._options

    @options.setter
    def options(self, options: OptionsManager):
        self._options = options

    @property
    def energy_range(self) -> int:
        return self._energy_range

    @energy_range.setter
    def energy_range(self, energy_range: int):
        self._energy_range = energy_range

    @property
    def vertical_annotation_offset(self):
        return self._vertical_annotation_offset

    @vertical_annotation_offset.setter
    def vertical_annotation_offset(self, vertical_annotation_offset: float):
        self._vertical_annotation_offset = vertical_annotation_offset

    @property
    def annotations(self) -> list[any]:
        return self._annotations

    @annotations.setter
    def annotations(self, annotations: list[any]):
        self._annotations = annotations

    def get_colormap(self):
        cmap = self.options.get_global_option(Option.COLORMAP)
        cmap = cmap.value.lower() if cmap is not None else None
        logger.info("Plotting with colormap: {}".format(cmap))
        return PlotterUtils.colormap_dictionary_from_array(
            array=self.surface.reactions, mtype=cmap
        )

    def get_line_color(self, rxn: Reaction, cmap: dict) -> str:
        color = self.options.get_keyword_option(rxn.ts.name, Option.COLOR)
        return cmap[rxn] if color is None else color.value

    def get_line_style(self, rxn: Reaction) -> str:
        ls = self.options.get_keyword_option(rxn.ts.name, Option.LINESTYLE)
        return "-" if ls is None else ls.value

    def get_line_width(self, rxn: Reaction) -> float:
        lw = self.options.get_keyword_option(rxn.ts.name, Option.LINEWIDTH)
        return 1.0 if lw is None else lw.value

    def show_label(self, sp: StationaryPoint) -> bool:
        label = self.options.get_keyword_option(sp.name, Option.LABEL)
        label = label.value.strip().lower() if label is not None else "true"
        return False if label == "false" else True

    def get_label_font(self) -> str:
        font = self.options.get_global_option(Option.LABEL_FONT)
        return font.value if font is not None else "DejaVu Sans"

    def get_stationary_point_label(self, sp: StationaryPoint) -> str:

        name = sp.name

        pad_bimol = self.options.get_global_option(Option.PAD_BIMOLECULAR)
        pad_bimol = (
            True
            if pad_bimol is not None and pad_bimol.value.lower() == "true"
            else False
        )

        if pad_bimol and "+" in name:
            species = name.split("+")
            name = " ".join(species)

        return " ".join([name, "(" + str(np.round(sp.energy, 1)) + ")"])

    def get_energy_range(self):
        if self.energy_range is None:
            sps = self.surface.get_stationary_points()
            min = np.min([sp.energy for sp in sps])
            max = np.max([sp.energy for sp in sps])
            range = 25 * round((max - min) / 25)
            self.energy_range = 25 if range == 0 else range
            logger.info("Energy range = {}".format(self.energy_range))
        return self.energy_range

    def get_vertical_annotation_offset(self):
        if self.vertical_annotation_offset is None:
            range = self.get_energy_range()
            offset = np.abs(0.15 * range)
            self.vertical_annotation_offset = offset
            logger.info(
                "Vertical annotation offset = {}".format(
                    self.vertical_annotation_offset
                )
            )
        return self.vertical_annotation_offset

    def get_image_resolution(self) -> int:
        res = self.options.get_global_option(Option.RESOLUTION)
        if res is not None:
            return int(res.value)
        return 1200

    def plot_reactions(self, axis: any) -> None:
        cmap = self.get_colormap()
        for rxn in self.surface.reactions:
            logger.info("Plotting reaction: {}".format(rxn.get_name()))
            axis.plot(
                rxn.x_coords,
                rxn.y_coords,
                color=self.get_line_color(rxn, cmap),
                linestyle=self.get_line_style(rxn),
                linewidth=self.get_line_width(rxn),
            )

    def add_labels(self, axis: any) -> None:

        show_labels = self.options.get_global_option(Option.SHOW_LABELS)
        show_labels = (
            True
            if show_labels is None or show_labels.value.lower() != "false"
            else False
        )
        if show_labels is False:
            return None

        label_loc = self.options.get_global_option(Option.LABEL_LOCATION)

        if label_loc is not None and label_loc.value.lower() == "inline":
            self.add_inline_labels(axis)
        else:
            self.add_offset_minima_labels(axis)
            self.add_offset_ts_labels(axis)

    def add_offset_minima_labels(self, axis: any) -> None:
        for sp in self.surface.minima:
            sp: StationaryPoint
            if self.show_label(sp):
                axis.annotate(
                    self.get_stationary_point_label(sp),
                    (sp.rxn_coord, sp.energy),
                    xytext=(
                        sp.rxn_coord,
                        sp.energy - self.get_vertical_annotation_offset(),
                    ),
                    textcoords="data",
                    ha="center",
                    va="bottom",
                    arrowprops=dict(arrowstyle="->", color="k"),
                    fontfamily=self.get_label_font(),
                )

    def add_offset_ts_labels(self, axis: any) -> None:
        for sp in self.surface.ts:
            sp: StationaryPoint
            if self.show_label(sp):
                axis.annotate(
                    self.get_stationary_point_label(sp),
                    (sp.rxn_coord, sp.energy),
                    xytext=(
                        sp.rxn_coord,
                        sp.energy + self.get_vertical_annotation_offset(),
                    ),
                    textcoords="data",
                    ha="center",
                    va="top",
                    arrowprops=dict(arrowstyle="->", color="k"),  # Arrow properties
                    fontfamily=self.get_label_font(),
                )

    def add_inline_labels(self, axis: any):
        name_pos_map = {}
        cmap = self.get_colormap()
        ts_cmap = {}
        for species in self.surface.minima + self.surface.ts:
            name_pos_map[species.name] = (species.rxn_coord, species.energy)
        for rxn in self.surface.reactions:
            ts_cmap[rxn.ts.name] = cmap[rxn]

        for species in name_pos_map:

            color = ts_cmap[species] if species in ts_cmap else "k"

            axis.annotate(
                species,
                name_pos_map[species],
                fontsize=8,
                color=color,
                ha="center",
                va="center",
                bbox=dict(facecolor="white", edgecolor=color, boxstyle="round,pad=0.1"),
            )

    def set_limits(self, axis: any) -> None:
        xcoords = [s.rxn_coord for s in self.surface.get_stationary_points()]
        ycoords = [s.energy for s in self.surface.get_stationary_points()]
        labels = [text.get_position() for text in axis.texts]
        if labels is not None:
            xcoords += [i[0] for i in labels]
            ycoords += [i[1] for i in labels]
        ymin = np.min(ycoords) - 0.1 * self.get_energy_range()
        ymax = np.max(ycoords) + 0.1 * self.get_energy_range()
        axis.set_xlim([np.min(xcoords) - 0.5, np.max(xcoords) + 0.5])
        axis.set_ylim([ymin, ymax])

    def save_image(self, fig: any) -> None:
        PlotterUtils.save_image(
            output_filename=self.output_file,
            figure=fig,
            dpi=self.get_image_resolution(),
        )

    def plot(self) -> None:
        logger.info("Plotting surface")
        fig, axis = PlotterUtils.create_figure(
            xlabel="Reaction Coordinate / arb. units",
            ylabel="Energy / kJ mol$^{-1}$",
            title="",
        )

        self.plot_reactions(axis)
        self.add_labels(axis)
        self.set_limits(axis)
        self.save_image(fig)
