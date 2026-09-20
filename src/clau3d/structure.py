"""Envolvente 6U, railes y zona util interior, segun CDS Rev 14.1.

Toda la geometria sale de ``data/components.yaml``; aqui no hay ningun numero.
"""

from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

from .datamodel import Catalogo


@dataclass(frozen=True)
class Caja:
    """Caja alineada con los ejes, en coordenadas CDS (origen en el centro)."""

    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float

    @classmethod
    def centrada(cls, dims: tuple[float, float, float], centro=(0.0, 0.0, 0.0)) -> "Caja":
        dx, dy, dz = dims
        cx, cy, cz = centro
        return cls(
            cx - dx / 2, cy - dy / 2, cz - dz / 2,
            cx + dx / 2, cy + dy / 2, cz + dz / 2,
        )

    @property
    def dims(self) -> tuple[float, float, float]:
        return (self.xmax - self.xmin, self.ymax - self.ymin, self.zmax - self.zmin)

    @property
    def centro(self) -> tuple[float, float, float]:
        return (
            (self.xmin + self.xmax) / 2,
            (self.ymin + self.ymax) / 2,
            (self.zmin + self.zmax) / 2,
        )

    @property
    def volumen_mm3(self) -> float:
        dx, dy, dz = self.dims
        return dx * dy * dz

    def solapa_con(self, otra: "Caja", tolerancia: float = 0.0) -> bool:
        """Solapamiento de volumen. Tocarse cara con cara no cuenta."""
        return (
            self.xmin < otra.xmax - tolerancia
            and otra.xmin < self.xmax - tolerancia
            and self.ymin < otra.ymax - tolerancia
            and otra.ymin < self.ymax - tolerancia
            and self.zmin < otra.zmax - tolerancia
            and otra.zmin < self.zmax - tolerancia
        )

    def volumen_solape(self, otra: "Caja") -> float:
        dx = max(0.0, min(self.xmax, otra.xmax) - max(self.xmin, otra.xmin))
        dy = max(0.0, min(self.ymax, otra.ymax) - max(self.ymin, otra.ymin))
        dz = max(0.0, min(self.zmax, otra.zmax) - max(self.zmin, otra.zmin))
        return dx * dy * dz

    def contiene_a(self, otra: "Caja", tolerancia: float = 1e-6) -> bool:
        return (
            otra.xmin >= self.xmin - tolerancia
            and otra.xmax <= self.xmax + tolerancia
            and otra.ymin >= self.ymin - tolerancia
            and otra.ymax <= self.ymax + tolerancia
            and otra.zmin >= self.zmin - tolerancia
            and otra.zmax <= self.zmax + tolerancia
        )

    def desbordamiento(self, otra: "Caja") -> tuple[float, float, float]:
        """Cuanto se sale ``otra`` de ``self`` en cada eje, en mm."""
        return (
            max(0.0, self.xmin - otra.xmin, otra.xmax - self.xmax),
            max(0.0, self.ymin - otra.ymin, otra.ymax - self.ymax),
            max(0.0, self.zmin - otra.zmin, otra.zmax - self.zmax),
        )

    def solido(self) -> cq.Solid:
        dx, dy, dz = self.dims
        return cq.Solid.makeBox(dx, dy, dz, cq.Vector(self.xmin, self.ymin, self.zmin))


def envolvente(catalogo: Catalogo) -> Caja:
    """Envolvente exterior 6U, centrada en el origen (CDS 14.1 req 2.2.1)."""
    return Caja.centrada(catalogo.dims_exteriores)


def zona_util(catalogo: Catalogo) -> Caja:
    """Volumen interior disponible segun el espesor de pared declarado."""
    return Caja.centrada(catalogo.dims_interiores)


def railes(catalogo: Catalogo) -> list[tuple[str, Caja]]:
    """Los cuatro railes que corren a lo largo de Z en las esquinas."""
    dx, dy, dz = catalogo.dims_exteriores
    ancho = catalogo.envolvente["ancho_rail_minimo"].escalar()
    if ancho is None:
        return []
    salida: list[tuple[str, Caja]] = []
    for signo_x, etiqueta_x in ((-1, "-X"), (1, "+X")):
        for signo_y, etiqueta_y in ((-1, "-Y"), (1, "+Y")):
            cx = signo_x * (dx / 2 - ancho / 2)
            cy = signo_y * (dy / 2 - ancho / 2)
            salida.append(
                (
                    f"rail_{etiqueta_x}{etiqueta_y}",
                    Caja.centrada((ancho, ancho, dz), (cx, cy, 0.0)),
                )
            )
    return salida


def solido_estructura(catalogo: Catalogo) -> cq.Solid:
    """Chasis generico: envolvente exterior hueca hasta la zona util."""
    externo = envolvente(catalogo).solido()
    interno = zona_util(catalogo).solido()
    return externo.cut(interno)
