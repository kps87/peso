import os
from typing import Tuple

import numpy as np
from scipy.interpolate import interp1d

from domain.pes import PES, Reaction, StationaryPoint
from service.logging import Log

logger = Log.get_logger(os.path.basename(__file__))


class PESGridEnhancer:

    def __init__(self):
        pass

    @classmethod
    def enhance_surface(cls, surface: PES) -> None:
        cls.assign_stationary_point_rxn_coordinates(surface)
        [cls.generate_reaction_curve(rxn) for rxn in surface.reactions]

    @classmethod
    def assign_stationary_point_rxn_coordinates(cls, surface: PES):
        stationary_points = surface.minima + surface.ts
        logger.info(
            "Assigning reaction coordinates for surface with {} stationary points and {} reactions".format(
                len(stationary_points), len(surface.reactions)
            )
        )
        x_grid: dict[str, float] = {}

        [cls.add_minima_to_grid(x_grid, species) for species in surface.minima]
        [cls.add_ts_to_grid(x_grid, rxn) for rxn in surface.reactions]

        stationary_points = set()
        [
            stationary_points.add(x)
            for rxn in surface.reactions
            for x in rxn.get_stationary_points()
        ]
        for sp in stationary_points:
            sp.rxn_coord = x_grid[sp.name]

    @classmethod
    def add_minima_to_grid(cls, x_grid: dict[str, float], species: StationaryPoint):
        if species.name not in x_grid:
            x_grid[species.name] = len(x_grid.keys()) + 1

    @classmethod
    def add_ts_to_grid(cls, x_grid: dict[str, float], rxn: Reaction):
        x_grid[rxn.ts.name] = 0.5 * (x_grid[rxn.reac.name] + x_grid[rxn.prod.name])

    @classmethod
    def generate_reaction_curve(cls, rxn: Reaction):
        logger.info(
            "Generating potential energy curves for reaction {}".format(rxn.get_name())
        )
        xi, vi = cls.generate_reaction_curve_component(rxn.reac, rxn.ts)
        xj, vj = cls.generate_reaction_curve_component(rxn.prod, rxn.ts)

        x, v = np.concatenate((xi, xj)), np.concatenate((vi, vj))
        isort = np.argsort(x)
        x, v = x[isort], v[isort]
        x, v = cls.remove_duplicates(x, v)

        # interpolate
        f_interp = interp1d(x, v, kind="cubic", fill_value="extrapolate")
        x = np.linspace(np.min(x), np.max(x), 100)
        v = f_interp(x)

        rxn.x_coords = x
        rxn.y_coords = v

    @classmethod
    def generate_reaction_curve_component(
        cls, i: StationaryPoint, j: StationaryPoint
    ) -> Tuple[np.ndarray, np.ndarray]:
        def generate_component(
            xi: float, yi: float, xj: float, yj: float
        ) -> Tuple[np.ndarray, np.ndarray]:

            # Solve for quadratic coefficients: V(x) = ax^2 + bx + c
            a = np.array([[xi**2, xi, 1], [xj**2, xj, 1], [(2 * xi), 1, 0]])
            b = np.array([yi, yj, 0])
            coeff = np.linalg.solve(a, b)

            # Generate the smooth potential
            x = np.linspace(xi, xj, 25)
            v = coeff[0] * x**2 + coeff[1] * x + coeff[2]
            return x, v

        # generate two harmonic curves, from reac to midpoint, and midpoint to ts
        xa, va = generate_component(
            i.rxn_coord,
            i.energy,
            0.5 * (i.rxn_coord + j.rxn_coord),
            0.5 * (i.energy + j.energy),
        )
        xb, vb = generate_component(
            j.rxn_coord,
            j.energy,
            0.5 * (i.rxn_coord + j.rxn_coord),
            0.5 * (i.energy + j.energy),
        )
        return np.concatenate((xa, xb)), np.concatenate((va, vb))

    @classmethod
    def remove_duplicates(cls, x: np.ndarray, y: np.ndarray):
        found = set()
        xunique, yunique = [], []
        for i, j in zip(x, y):
            if i not in found:
                found.add(i)
                xunique.append(i)
                yunique.append(j)
        return np.array(xunique), np.array(yunique)
