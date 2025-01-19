from typing import Self

import numpy as np
import pandas as pd


class StationaryPoint:
    def __init__(self, name: str, energy: float, sptype: str):
        self._name = name
        self._energy = energy
        self._sptype = sptype
        self._rxn_coord = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, energy):
        self._energy = energy

    @property
    def sptype(self):
        return self._sptype

    @sptype.setter
    def sptype(self, sptype):
        self._sptype = sptype

    @property
    def rxn_coord(self) -> float | None:
        return self._rxn_coord

    @rxn_coord.setter
    def rxn_coord(self, rxn_coord: float):
        self._rxn_coord = rxn_coord


class Reaction:
    def __init__(
        self, reac: StationaryPoint, prod: StationaryPoint, ts: StationaryPoint
    ):
        self._reac = reac
        self._prod = prod
        self._ts = ts
        self._x_coords = None
        self._y_coords = None

    @property
    def reac(self):
        return self._reac

    @reac.setter
    def reac(self, reac):
        self._reac = reac

    @property
    def prod(self):
        return self._prod

    @prod.setter
    def prod(self, prod):
        self._prod = prod

    @property
    def ts(self):
        return self._ts

    @ts.setter
    def ts(self, ts):
        self._ts = ts

    @property
    def x_coords(self):
        return self._x_coords

    @x_coords.setter
    def x_coords(self, x_coords):
        self._x_coords = x_coords

    @property
    def y_coords(self) -> np.ndarray:
        return self._y_coords

    @y_coords.setter
    def y_coords(self, y_coords: np.ndarray):
        self._y_coords = y_coords

    def get_stationary_points(self) -> list[StationaryPoint]:
        return [self.reac, self.ts, self.prod]

    def get_name(self) -> str:
        return "<->".join([x.name for x in self.get_stationary_points()])


class PES:
    def __init__(
        self,
        minima: list[StationaryPoint],
        ts: list[StationaryPoint],
        reactions: list[Reaction],
    ):
        self._minima = minima
        self._ts = ts
        self._reactions = reactions

    @property
    def minima(self):
        return self._minima

    @minima.setter
    def minima(self, minima):
        self._minima = minima

    @property
    def ts(self):
        return self._ts

    @ts.setter
    def ts(self, ts):
        self._ts = ts

    @property
    def reactions(self):
        return self._reactions

    @reactions.setter
    def reactions(self, reactions):
        self._reactions = reactions

    @classmethod
    def from_dataframe(cls, data: pd.DataFrame) -> Self:
        minima = []
        ts = []
        rxns = []

        for index, row in data.iterrows():
            sp = StationaryPoint(row["name"], row["energy"], row["type"])
            if sp.sptype == "TS":
                ts.append(sp)
                rxns.append(
                    {"reac": row["reactant"], "prod": row["product"], "ts": sp.name}
                )
            elif sp.sptype == "MIN":
                minima.append(sp)

        reactions = []
        for rxn in rxns:
            reac = list(filter(lambda x: x.name == rxn["reac"], minima))[0]
            prod = list(filter(lambda x: x.name == rxn["prod"], minima))[0]
            tsstate = list(filter(lambda x: x.name == rxn["ts"], ts))[0]
            r = Reaction(reac=reac, prod=prod, ts=tsstate)
            reactions.append(r)

        return PES(minima=minima, ts=ts, reactions=reactions)

    def get_stationary_points(self) -> list[StationaryPoint]:
        return self.minima + self.ts
