import os
import matplotlib.pyplot as plt
import numpy as np
from domain.pes import PES, StationaryPoint, Reaction
from service.logging import Log
from matplotlib import cm

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
    def __init__(self, surface: PES, output_file: str, fopts: dict[str, any]):
        self._surface = surface
        self._output_file = output_file
        self._fopts = fopts
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
    def fopts(self) -> dict[str, any]:
        return self._fopts

    @fopts.setter
    def fopts(self, fopts: dict[str, any]):
        self._fopts = fopts

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

    def get_format_option(self, rxn: Reaction, option: str) -> str | None:
        return (
            self.fopts[rxn.ts.name][option]
            if rxn.ts.name in self.fopts and option in self.fopts[rxn.ts.name]
            else None
        )

    def has_global_option(self, option: str) -> bool:
        return "global" in self.fopts and option in self.fopts["global"]

    def get_global_option(self, option: str) -> str | None:
        if self.has_global_option(option):
            return self.fopts["global"][option]
        return None

    def get_colormap(self):
        cmap = self.get_global_option("colormap")
        logger.info("Plotting with colormap: {}".format(cmap))
        return PlotterUtils.colormap_dictionary_from_array(
            array=self.surface.reactions, mtype=cmap
        )

    def get_line_color(self, rxn: Reaction, cmap: dict) -> str:
        color = self.get_format_option(rxn, "color")
        return cmap[rxn] if color is None else color

    def get_line_style(self, rxn: Reaction) -> str:
        ls = self.get_format_option(rxn, "linestyle")
        return "-" if ls is None else ls

    def get_line_width(self, rxn: Reaction) -> float:
        lw = self.get_format_option(rxn, "linewidth")
        return 1.0 if lw is None else lw

    def show_label(self, sp: StationaryPoint) -> bool:
        label = (
            self.fopts[sp.name]["label"]
            if sp.name in self.fopts and "label" in self.fopts[sp.name]
            else "true"
        )
        return label.strip().lower() == "true"

    def get_label_font(self) -> str:
        if self.has_global_option("label-font"):
            return self.get_global_option("label-font")
        return "DejaVu Sans"

    def get_stationary_point_label(self, sp: StationaryPoint) -> str:

        name = sp.name

        if (
            self.has_global_option("pad-bimolecular")
            and self.get_global_option("pad-bimolecular").lower() == "true"
            and "+" in name
        ):
            reac, prod = name.split("+")
            name = " ".join([reac, "+", prod])

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
            offset = np.abs(0.15 * (range))
            self.vertical_annotation_offset = offset
            logger.info(
                "Vertical annotation offset = {}".format(
                    self.vertical_annotation_offset
                )
            )
        return self.vertical_annotation_offset

    def add_annotation(self, annotation: any):
        annotations = self.annotations
        annotations.append(annotation)
        self.annotations = annotations

    def get_image_resolution(self) -> int:
        res = self.get_global_option("resolution")
        if res is not None:
            return int(res)
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

    def add_minima_labels(self, axis: any) -> None:
        for sp in self.surface.minima:
            sp: StationaryPoint
            if self.show_label(sp):
                annotation = axis.annotate(
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
                self.add_annotation(annotation)

    def add_ts_labels(self, axis: any) -> None:
        for sp in self.surface.ts:
            sp: StationaryPoint
            if self.show_label(sp):
                annotation = axis.annotate(
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
                self.add_annotation(annotation)

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
        self.add_minima_labels(axis)
        self.add_ts_labels(axis)
        self.set_limits(axis)
        self.save_image(fig)
