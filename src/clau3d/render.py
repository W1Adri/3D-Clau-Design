"""Vistas del ensamblaje en SVG y PNG, con los TBD a la vista."""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

from . import parts, structure
from .assembly import Layout, construir
from .datamodel import Catalogo

# (nombre, direccion de vista, direccion "arriba")
VISTAS = {
    "isometrica": ((1, 1, 1), (0, 1, 0)),
    "planta_XZ": ((0, 1, 0), (0, 0, 1)),
    "alzado_XY": ((0, 0, 1), (0, 1, 0)),
    "perfil_YZ": ((1, 0, 0), (0, 1, 0)),
}


def _compuesto(catalogo: Catalogo, layout: Layout) -> cq.Compound:
    solidos: list = [structure.solido_estructura(catalogo)]
    for _, caja in structure.railes(catalogo):
        solidos.append(caja.solido())
    for pieza in construir(catalogo, layout):
        solidos.append(pieza.solido)
    for keep_out in layout.keep_outs:
        solidos.append(keep_out.caja.solido())
    return cq.Compound.makeCompound(solidos)


def svg(
    catalogo: Catalogo,
    layout: Layout,
    destino: Path,
    vista: str = "isometrica",
) -> Path:
    direccion, arriba = VISTAS[vista]
    destino.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(
        _compuesto(catalogo, layout),
        str(destino),
        opt={
            "width": 1100,
            "height": 700,
            "marginLeft": 20,
            "marginTop": 20,
            "projectionDir": direccion,
            "showAxes": True,
            "showHidden": False,
            "strokeWidth": 0.4,
        },
    )
    return destino


def todas_las_vistas(
    catalogo: Catalogo, layout: Layout, dir_destino: Path
) -> list[Path]:
    salida: list[Path] = []
    for nombre in VISTAS:
        salida.append(svg(catalogo, layout, dir_destino / f"vista_{nombre}.svg", nombre))
    return salida


def leyenda() -> list[tuple[str, str]]:
    """Codigo de color por estado del dato, para acompanar a las vistas."""
    return [
        ("confirmado", "color propio de su categoria"),
        ("referencia", "naranja - dato de un componente parecido, no el elegido"),
        ("decision", "azul - decision de diseno de ACSAR"),
        ("TBD", "magenta - falta el dato"),
    ] + [
        (f"categoria {nombre}", str(rgb))
        for nombre, rgb in parts.COLOR_POR_CATEGORIA.items()
    ]
