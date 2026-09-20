"""Informe de volumen: que ocupa cada pieza y donde queda el hueco libre."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..assembly import Layout, PiezaColocada
from ..datamodel import Catalogo
from ..structure import Caja

MM3_POR_U = 100.0 * 100.0 * 100.0  # 1U = 10 x 10 x 10 cm


def a_u(mm3: float) -> float:
    return mm3 / MM3_POR_U


def a_cm3(mm3: float) -> float:
    return mm3 / 1000.0


@dataclass
class FilaVolumen:
    id: str
    nombre: str
    categoria: str
    estado_dato: str
    unidades: int | None
    volumen_mm3: float | None
    centro: tuple[float, float, float] | None
    colocado: bool

    @property
    def volumen_cm3(self) -> float | None:
        return None if self.volumen_mm3 is None else a_cm3(self.volumen_mm3)


def tabla(
    catalogo: Catalogo, piezas: list[PiezaColocada]
) -> list[FilaVolumen]:
    """Una fila por componente, este colocado o no."""
    por_id: dict[str, list[PiezaColocada]] = {}
    for pieza in piezas:
        por_id.setdefault(pieza.colocacion.componente_id, []).append(pieza)

    filas: list[FilaVolumen] = []
    for componente in catalogo.componentes:
        if componente.categoria == "estructura":
            continue
        colocadas = por_id.get(componente.id, [])
        centro = colocadas[0].caja_mundo.centro if colocadas else None
        filas.append(
            FilaVolumen(
                id=componente.id,
                nombre=componente.nombre,
                categoria=componente.categoria,
                estado_dato=componente.estado_geometria,
                unidades=componente.n_unidades,
                volumen_mm3=componente.volumen_mm3(),
                centro=centro,
                colocado=bool(colocadas),
            )
        )
    filas.sort(key=lambda f: (-(f.volumen_mm3 or -1), f.id))
    return filas


@dataclass
class ResumenVolumen:
    exterior_mm3: float
    interior_mm3: float
    ocupado_colocado_mm3: float
    ocupado_catalogo_mm3: float
    sin_envolvente: list[str]
    no_colocados: list[str]

    @property
    def libre_mm3(self) -> float:
        return self.interior_mm3 - self.ocupado_colocado_mm3

    @property
    def fiable(self) -> bool:
        """El volumen libre solo es real si no falta geometria ni colocaciones."""
        return not self.sin_envolvente and not self.no_colocados


def resumen(catalogo: Catalogo, piezas: list[PiezaColocada]) -> ResumenVolumen:
    ocupado_colocado = sum(p.caja_mundo.volumen_mm3 for p in piezas)
    ocupado_catalogo = 0.0
    sin_envolvente: list[str] = []
    colocados = {p.colocacion.componente_id for p in piezas}
    no_colocados: list[str] = []

    for componente in catalogo.componentes:
        if componente.categoria == "estructura" or componente.montado_en:
            continue
        volumen = componente.volumen_mm3()
        if volumen is None:
            sin_envolvente.append(componente.id)
        else:
            ocupado_catalogo += volumen
        if componente.id not in colocados:
            no_colocados.append(componente.id)

    return ResumenVolumen(
        exterior_mm3=catalogo.volumen_exterior_mm3,
        interior_mm3=catalogo.volumen_interior_mm3,
        ocupado_colocado_mm3=ocupado_colocado,
        ocupado_catalogo_mm3=ocupado_catalogo,
        sin_envolvente=sin_envolvente,
        no_colocados=no_colocados,
    )


def rejilla_ocupacion(
    interior: Caja, piezas: list[PiezaColocada], paso: float = 5.0
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Rejilla booleana de ocupacion sobre la zona util (True = ocupado)."""
    dx, dy, dz = interior.dims
    nx, ny, nz = (max(1, int(round(d / paso))) for d in (dx, dy, dz))
    ejes = (
        interior.xmin + (np.arange(nx) + 0.5) * dx / nx,
        interior.ymin + (np.arange(ny) + 0.5) * dy / ny,
        interior.zmin + (np.arange(nz) + 0.5) * dz / nz,
    )
    ocupado = np.zeros((nx, ny, nz), dtype=bool)
    for pieza in piezas:
        caja = pieza.caja_mundo
        mx = (ejes[0] >= caja.xmin) & (ejes[0] <= caja.xmax)
        my = (ejes[1] >= caja.ymin) & (ejes[1] <= caja.ymax)
        mz = (ejes[2] >= caja.zmin) & (ejes[2] <= caja.zmax)
        ocupado |= mx[:, None, None] & my[None, :, None] & mz[None, None, :]
    return ocupado, ejes


def mapa_libre_xz(
    interior: Caja, piezas: list[PiezaColocada], paso: float = 10.0
) -> list[str]:
    """Mapa de texto del hueco libre, mirando el 6U desde +Y.

    Cada caracter es la fraccion de altura (Y) libre en esa columna.
    """
    ocupado, _ = rejilla_ocupacion(interior, piezas, paso)
    libre = ~ocupado
    fraccion = libre.mean(axis=1)  # promedio en Y -> plano X-Z
    escala = " .:-=+*#%@"  # de vacio a lleno de material
    lineas: list[str] = []
    nx, nz = fraccion.shape
    for ix in range(nx - 1, -1, -1):  # +X arriba
        fila = "".join(
            escala[min(len(escala) - 1, int((1.0 - fraccion[ix, iz]) * (len(escala) - 1)))]
            for iz in range(nz)
        )
        lineas.append(fila)
    return lineas


def libre_por_zona(layout: Layout, piezas: list[PiezaColocada]) -> list[dict]:
    """Volumen libre dentro de cada zona declarada en el layout."""
    salida: list[dict] = []
    for zona in layout.zonas:
        ocupado = sum(
            zona.caja.volumen_solape(p.caja_mundo) for p in piezas
        )
        total = zona.caja.volumen_mm3
        salida.append(
            {
                "zona": zona.id,
                "nombre": zona.nombre,
                "total_cm3": a_cm3(total),
                "ocupado_cm3": a_cm3(ocupado),
                "libre_cm3": a_cm3(total - ocupado),
                "libre_U": a_u(total - ocupado),
                "fraccion_ocupada": ocupado / total if total else 0.0,
            }
        )
    return salida
