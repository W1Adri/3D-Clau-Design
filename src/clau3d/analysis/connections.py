"""Comprobacion de las conexiones declaradas en ``data/connections.yaml``.

Una conexion es correcta solo si sus dos extremos existen, estan colocados y
hay espacio declarado para el conector. Si falta un dato, el resultado es
'no comprobable': nunca se da por buena.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..assembly import Layout, PiezaColocada
from ..datamodel import TBD, Catalogo

OK = "ok"
FALLA = "falla"
NO_COMPROBABLE = "no comprobable"

EXTERIOR = "EXTERIOR"


@dataclass
class ResultadoConexion:
    id: str
    familia: str
    desde: str
    hasta: str
    tipo: str
    estado: str
    mensaje: str
    longitud_mm: float | None = None
    falta: str | None = None

    @property
    def critico(self) -> bool:
        return self.estado == FALLA


def _centro(piezas_por_id: dict, cid: str) -> tuple[float, float, float] | None:
    piezas = piezas_por_id.get(cid)
    if not piezas:
        return None
    return piezas[0].caja_mundo.centro


def _holgura_declarada(conexion: dict) -> tuple[bool, str | None]:
    """(hay_dato, que_falta) para la holgura del conector."""
    for clave in ("holgura_mm", "conector", "diametro_haz_mm"):
        bloque = conexion.get(clave)
        if isinstance(bloque, dict):
            if bloque.get("estado") == TBD or bloque.get("valor") is None:
                return False, bloque.get("falta") or f"{clave} sin declarar"
    return True, None


def comprobar(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> list[ResultadoConexion]:
    piezas_por_id: dict[str, list[PiezaColocada]] = {}
    for pieza in piezas:
        piezas_por_id.setdefault(pieza.colocacion.componente_id, []).append(pieza)

    resultados: list[ResultadoConexion] = []
    for familia, conexion in catalogo.todas_las_conexiones():
        desde = conexion.get("desde")
        hasta = conexion.get("hasta")
        cid = conexion.get("id", "?")
        tipo = conexion.get("tipo", familia)

        if familia == "termico":
            resultados.append(_comprobar_termico(catalogo, conexion, piezas_por_id))
            continue

        # 1. Los dos extremos tienen que existir en el catalogo.
        faltan = [
            extremo
            for extremo, valor in (("desde", desde), ("hasta", hasta))
            if valor != EXTERIOR and not catalogo.existe(valor or "")
        ]
        if faltan:
            resultados.append(
                ResultadoConexion(
                    id=cid, familia=familia, desde=desde or "?", hasta=hasta or "?",
                    tipo=tipo, estado=FALLA,
                    mensaje=(
                        f"Extremo inexistente en components.yaml: "
                        f"{', '.join(faltan)}"
                    ),
                )
            )
            continue

        # 2. Los dos extremos tienen que estar colocados para medir el recorrido.
        sin_colocar = [
            valor
            for valor in (desde, hasta)
            if valor != EXTERIOR and valor not in piezas_por_id
        ]
        if sin_colocar:
            resultados.append(
                ResultadoConexion(
                    id=cid, familia=familia, desde=desde or "?", hasta=hasta or "?",
                    tipo=tipo, estado=NO_COMPROBABLE,
                    mensaje=(
                        f"Sin colocar: {', '.join(sin_colocar)}. No se puede medir "
                        f"el recorrido ni comprobar la holgura."
                    ),
                    falta=f"Colocacion de {', '.join(sin_colocar)}",
                )
            )
            continue

        longitud = None
        if desde != EXTERIOR and hasta != EXTERIOR:
            a = _centro(piezas_por_id, desde)  # type: ignore[arg-type]
            b = _centro(piezas_por_id, hasta)  # type: ignore[arg-type]
            if a and b:
                longitud = math.dist(a, b)

        # 3. Tiene que haber holgura declarada para el conector.
        hay_holgura, que_falta = _holgura_declarada(conexion)
        if not hay_holgura:
            resultados.append(
                ResultadoConexion(
                    id=cid, familia=familia, desde=desde or "?", hasta=hasta or "?",
                    tipo=tipo, estado=NO_COMPROBABLE,
                    mensaje=(
                        "Extremos colocados, pero sin holgura de conector declarada: "
                        "no se puede afirmar que quepa."
                    ),
                    longitud_mm=longitud,
                    falta=que_falta,
                )
            )
            continue

        resultados.append(
            ResultadoConexion(
                id=cid, familia=familia, desde=desde or "?", hasta=hasta or "?",
                tipo=tipo, estado=OK,
                mensaje=(
                    f"Extremos colocados y holgura declarada"
                    + (f", recorrido {longitud:.0f} mm" if longitud else "")
                ),
                longitud_mm=longitud,
            )
        )
    return resultados


def _comprobar_termico(
    catalogo: Catalogo, zona: dict, piezas_por_id: dict
) -> ResultadoConexion:
    cid = zona.get("id", "?")
    componentes = zona.get("componentes", [])
    inexistentes = [c for c in componentes if not catalogo.existe(c)]
    if inexistentes:
        return ResultadoConexion(
            id=cid, familia="termico", desde=zona.get("zona", "?"),
            hasta=zona.get("controlado_por", "?"), tipo="termico", estado=FALLA,
            mensaje=f"Componentes inexistentes: {', '.join(inexistentes)}",
        )
    if zona.get("estado_ubicacion") == TBD:
        return ResultadoConexion(
            id=cid, familia="termico", desde=zona.get("zona", "?"),
            hasta=zona.get("controlado_por", "?"), tipo="termico",
            estado=NO_COMPROBABLE,
            mensaje=(
                "Zona termica declarada pero sin ubicacion de sensores ni "
                "calefactores."
            ),
            falta="Ubicacion de sensores y calefactores",
        )
    return ResultadoConexion(
        id=cid, familia="termico", desde=zona.get("zona", "?"),
        hasta=zona.get("controlado_por", "?"), tipo="termico", estado=OK,
        mensaje="Zona termica definida.",
    )
