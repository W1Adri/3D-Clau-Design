"""Interferencias: solapes entre piezas, salidas de la envolvente y keep-outs."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ..assembly import Layout, PiezaColocada
from ..datamodel import Catalogo
from ..structure import Caja, envolvente, zona_util

# Por debajo de esta tolerancia se considera contacto, no interferencia.
TOLERANCIA_MM = 0.05


@dataclass
class Interferencia:
    # solape | fuera_envolvente | fuera_zona_util | fuera_de_zona |
    # protrusion_excesiva | keep_out
    tipo: str
    a: str
    b: str
    volumen_mm3: float
    detalle: str

    @property
    def volumen_cm3(self) -> float:
        return self.volumen_mm3 / 1000.0


def _solape_real(a: PiezaColocada, b: PiezaColocada) -> float:
    """Volumen de interseccion. Filtra por caja antes de la booleana, que es cara."""
    aproximado = a.caja_mundo.volumen_solape(b.caja_mundo)
    if aproximado <= 0:
        return 0.0
    try:
        interseccion = a.solido.intersect(b.solido)
    except Exception:  # pragma: no cover - fallo de OCC en geometrias raras
        return aproximado
    volumen = interseccion.Volume() if interseccion is not None else 0.0
    return volumen if volumen > 1e-6 else 0.0


def entre_piezas(piezas: list[PiezaColocada]) -> list[Interferencia]:
    salida: list[Interferencia] = []
    for a, b in combinations(piezas, 2):
        if not a.caja_mundo.solapa_con(b.caja_mundo, TOLERANCIA_MM):
            continue
        volumen = _solape_real(a, b)
        if volumen <= 0:
            continue
        salida.append(
            Interferencia(
                tipo="solape",
                a=a.colocacion.etiqueta,
                b=b.colocacion.etiqueta,
                volumen_mm3=volumen,
                detalle=(
                    f"{a.colocacion.etiqueta} y {b.colocacion.etiqueta} comparten "
                    f"{volumen / 1000:.2f} cm3"
                ),
            )
        )
    return salida


def fuera_de_envolvente(
    catalogo: Catalogo, piezas: list[PiezaColocada]
) -> list[Interferencia]:
    """Piezas que se salen de la envolvente 6U o invaden la pared del chasis.

    Con una excepcion que SI esta en la norma: una pieza marcada 'exterior' en
    el catalogo -- un panel de cuerpo, una antena de parche -- va montada por
    fuera, y la CDS 14.1 req 2.2.3 le permite sobresalir del plano del rail
    hasta 'protrusion_maxima'. Tratar eso como un desborde daria un fallo que
    no lo es; no tratarlo daria por bueno un panel que se pasa. Lo que se hace
    es comparar contra la envolvente AGRANDADA en esa cota, que es el volumen
    que la norma concede, y decirlo en el mensaje.
    """
    salida: list[Interferencia] = []
    exterior = envolvente(catalogo)
    interior = zona_util(catalogo)
    protrusion = catalogo.envolvente["protrusion_maxima"].escalar() or 0.0
    con_protrusion = Caja(
        exterior.xmin - protrusion, exterior.ymin - protrusion,
        exterior.zmin - protrusion,
        exterior.xmax + protrusion, exterior.ymax + protrusion,
        exterior.zmax + protrusion,
    )
    for pieza in piezas:
        caja = pieza.caja_mundo
        componente = pieza.componente
        if getattr(componente, "exterior", False):
            if con_protrusion.contiene_a(caja):
                continue
            dx, dy, dz = con_protrusion.desbordamiento(caja)
            salida.append(
                Interferencia(
                    tipo="protrusion_excesiva",
                    a=pieza.colocacion.etiqueta,
                    b="protrusion_maxima",
                    volumen_mm3=caja.volumen_mm3
                    - con_protrusion.volumen_solape(caja),
                    detalle=(
                        f"{pieza.colocacion.etiqueta} va montada por fuera, "
                        f"pero se pasa de los {protrusion:.1f} mm de "
                        f"protrusion que permite la CDS 14.1 req 2.2.3: "
                        f"X {dx:.1f} mm, Y {dy:.1f} mm, Z {dz:.1f} mm"
                    ),
                )
            )
            continue
        if not exterior.contiene_a(caja):
            dx, dy, dz = exterior.desbordamiento(caja)
            salida.append(
                Interferencia(
                    tipo="fuera_envolvente",
                    a=pieza.colocacion.etiqueta,
                    b="envolvente_6u",
                    volumen_mm3=caja.volumen_mm3 - exterior.volumen_solape(caja),
                    detalle=(
                        f"{pieza.colocacion.etiqueta} sale de la envolvente 6U: "
                        f"X {dx:.1f} mm, Y {dy:.1f} mm, Z {dz:.1f} mm"
                    ),
                )
            )
        elif not interior.contiene_a(caja):
            dx, dy, dz = interior.desbordamiento(caja)
            salida.append(
                Interferencia(
                    tipo="fuera_zona_util",
                    a=pieza.colocacion.etiqueta,
                    b="zona_util_interior",
                    volumen_mm3=caja.volumen_mm3 - interior.volumen_solape(caja),
                    detalle=(
                        f"{pieza.colocacion.etiqueta} invade la pared del chasis: "
                        f"X {dx:.1f} mm, Y {dy:.1f} mm, Z {dz:.1f} mm"
                    ),
                )
            )
    return salida


def fuera_de_su_zona(
    layout: Layout, piezas: list[PiezaColocada]
) -> list[Interferencia]:
    """Piezas que se salen de la zona a la que el layout dice que pertenecen.

    Las cinco zonas embaldosan la zona util, asi que una pieza que se sale de la
    suya se mete en la de al lado. Eso puede no ser una interferencia todavia
    -- la vecina quiza este vacia -- pero si es un error del reparto, y se ve
    antes de que llegue la pieza que si iba a ocupar ese hueco.

    Es el chequeo que salta cuando cambia la longitud reservada al telescopio:
    la bandeja se estrecha y lo que habia dentro deja de caber.
    """
    por_id = {zona.id: zona for zona in layout.zonas}
    salida: list[Interferencia] = []
    for pieza in piezas:
        zona = por_id.get(pieza.colocacion.zona or "")
        if zona is None:
            continue
        caja = pieza.caja_mundo
        if zona.caja.contiene_a(caja):
            continue
        dx, dy, dz = zona.caja.desbordamiento(caja)
        salida.append(
            Interferencia(
                tipo="fuera_de_zona",
                a=pieza.colocacion.etiqueta,
                b=zona.id,
                volumen_mm3=caja.volumen_mm3 - zona.caja.volumen_solape(caja),
                detalle=(
                    f"{pieza.colocacion.etiqueta} se sale de la zona "
                    f"'{zona.id}' que tiene asignada: X {dx:.1f} mm, "
                    f"Y {dy:.1f} mm, Z {dz:.1f} mm"
                ),
            )
        )
    return salida


def invasion_keep_out(
    layout: Layout, piezas: list[PiezaColocada]
) -> list[Interferencia]:
    """Piezas que invaden un volumen reservado (haz optico, bucle, conector)."""
    salida: list[Interferencia] = []
    for keep_out in layout.keep_outs:
        for pieza in piezas:
            volumen = keep_out.caja.volumen_solape(pieza.caja_mundo)
            if volumen <= TOLERANCIA_MM:
                continue
            salida.append(
                Interferencia(
                    tipo="keep_out",
                    a=pieza.colocacion.etiqueta,
                    b=f"keepout_{keep_out.id}",
                    volumen_mm3=volumen,
                    detalle=(
                        f"{pieza.colocacion.etiqueta} invade el keep-out "
                        f"'{keep_out.id}' ({keep_out.tipo}) en "
                        f"{volumen / 1000:.2f} cm3"
                    ),
                )
            )
    return salida


def todas(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> list[Interferencia]:
    return (
        entre_piezas(piezas)
        + fuera_de_envolvente(catalogo, piezas)
        + fuera_de_su_zona(layout, piezas)
        + invasion_keep_out(layout, piezas)
    )
