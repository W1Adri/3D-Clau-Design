"""Solidos de cada componente: caja envolvente o STEP de fabricante.

Un componente puede estar en cualquiera de los dos estados sin que cambie nada
mas del ensamblaje. Para pasar de caja a STEP basta anadir ``forma.step`` en
``data/components.yaml``.
"""

from __future__ import annotations

from pathlib import Path

import cadquery as cq

from .datamodel import (
    CONFIRMADO,
    DECISION,
    REFERENCIA,
    TBD,
    Catalogo,
    Componente,
    ErrorDeDatos,
    RAIZ,
)
from .structure import Caja

# El estado del dato manda sobre la categoria: un TBD se ve a la legua.
COLOR_POR_ESTADO = {
    REFERENCIA: (1.00, 0.55, 0.00),   # naranja: dato de un componente parecido
    DECISION: (0.20, 0.45, 0.90),     # azul: decision de diseno de ACSAR
    TBD: (1.00, 0.00, 0.80),          # magenta: falta el dato
}

# Solo se aplica cuando el dato esta confirmado.
COLOR_POR_CATEGORIA = {
    "estructura": (0.55, 0.55, 0.58),
    "plataforma": (0.30, 0.70, 0.45),
    "payload_optico": (0.92, 0.85, 0.20),
    "payload_bandeja": (0.20, 0.75, 0.82),
    "payload_pcb": (0.12, 0.50, 0.35),
}

TRANSPARENCIA = 0.55


def color(componente: Componente) -> cq.Color:
    estado = componente.estado_geometria
    if estado == CONFIRMADO:
        rgb = COLOR_POR_CATEGORIA.get(componente.categoria, (0.7, 0.7, 0.7))
    else:
        rgb = COLOR_POR_ESTADO.get(estado, (0.7, 0.7, 0.7))
    return cq.Color(*rgb, TRANSPARENCIA)


def ruta_step(componente: Componente) -> Path | None:
    if not componente.step:
        return None
    ruta = RAIZ / componente.step
    if not ruta.exists():
        raise ErrorDeDatos(
            f"{componente.id}: forma.step apunta a '{componente.step}', "
            f"que no existe. Deja el componente como caja hasta que llegue el STEP."
        )
    return ruta


def solido(componente: Componente) -> cq.Solid | cq.Compound:
    """Solido del componente en su propio sistema de ejes, centrado en el origen."""
    ruta = ruta_step(componente)
    if ruta is not None:
        importado = cq.importers.importStep(str(ruta))
        return importado.val()
    if not componente.modelable:
        raise ErrorDeDatos(
            f"{componente.id}: sin dimensiones y sin STEP. No se puede dibujar."
        )
    dims = componente.dimensiones.como_vector()
    assert dims is not None
    return Caja.centrada(dims).solido()


def caja_local(componente: Componente) -> Caja | None:
    """Caja envolvente del componente en sus ejes locales."""
    if componente.desde_step:
        bb = solido(componente).BoundingBox()
        return Caja(bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)
    if not componente.modelable:
        return None
    dims = componente.dimensiones.como_vector()
    assert dims is not None
    return Caja.centrada(dims)


def modelables(catalogo: Catalogo) -> list[Componente]:
    return [c for c in catalogo.componentes if c.modelable]


def no_modelables(catalogo: Catalogo) -> list[Componente]:
    """Componentes que no se pueden dibujar porque su geometria es TBD."""
    return [c for c in catalogo.componentes if not c.modelable]


def exportar_generados(catalogo: Catalogo, destino: Path | None = None) -> list[Path]:
    """Exporta a ``cad/generated/`` un STEP por pieza generada por este repo.

    Los STEP resultantes se reimportan igual que los de fabricante.
    """
    destino = destino or (RAIZ / "cad" / "generated")
    destino.mkdir(parents=True, exist_ok=True)
    escritos: list[Path] = []
    for componente in modelables(catalogo):
        if componente.desde_step:
            continue  # ya viene de cad/vendor, no se toca
        ruta = destino / f"{componente.id}.step"
        cq.exporters.export(solido(componente), str(ruta))
        escritos.append(ruta)
    return escritos
