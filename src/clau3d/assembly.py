"""Ensamblaje del 6U a partir del catalogo y de ``data/layout.yaml``.

El layout es un dato, no codigo: cambiar la distribucion es editar el YAML.
Mientras el layout este en estado 'propuesta' el ensamblaje se construye igual,
pero los informes lo dicen en cada pagina.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import yaml

from . import parts, structure
from .datamodel import DIR_DATOS, Catalogo, ErrorDeDatos
from .structure import Caja


# Sufijo que este modulo le pone a un STEP de subsistema que lleva CAD de
# fabricante dentro. El .gitignore lo mira, asi que cambiarlo aqui sin cambiarlo
# alli publicaria CAD de AAC en un repositorio publico.
SUFIJO_CAD_DE_FABRICANTE = "_con_cad_de_fabricante"


@dataclass
class Colocacion:
    """Una instancia de un componente situada dentro del 6U."""

    componente_id: str
    instancia: int
    centro: tuple[float, float, float]
    rotacion: tuple[float, float, float]
    zona: str | None
    nombre: str

    @property
    def etiqueta(self) -> str:
        return self.nombre


@dataclass
class Zona:
    id: str
    nombre: str
    caja: Caja
    nota: str | None = None


@dataclass
class KeepOut:
    """Un volumen reservado por el que no puede pasar nada.

    Lleva 'estado' y 'fuente' por el mismo motivo que los lleva un numero: casi
    todos salen de cotas que hoy no existen -- el radio minimo de curvatura de
    la fibra, el del coaxial, el diametro de haz -- y estan dibujados con
    valores SUPUESTOS. Una pieza que invada un keep-out supuesto no es un fallo
    del diseno: es una consecuencia de una hipotesis, y el informe tiene que
    poder decir cual de las dos cosas esta pasando.
    """

    id: str
    tipo: str
    caja: Caja
    nota: str | None = None
    estado: str = "supuesto"
    fuente: str | None = None

    @property
    def es_supuesto(self) -> bool:
        return self.estado == "supuesto"


@dataclass
class Layout:
    estado: str
    meta: dict
    zonas: list[Zona]
    colocaciones: list[Colocacion]
    keep_outs: list[KeepOut]

    @property
    def confirmado(self) -> bool:
        return self.estado == "confirmada"

    @property
    def vacio(self) -> bool:
        return not self.colocaciones


def _caja_desde(bruto: dict, nombre: str) -> Caja:
    try:
        minimo = bruto["min"]
        maximo = bruto["max"]
    except KeyError as exc:
        raise ErrorDeDatos(f"{nombre}: la caja necesita 'min' y 'max'") from exc
    caja = Caja(*[float(v) for v in minimo], *[float(v) for v in maximo])
    dx, dy, dz = caja.dims
    if min(dx, dy, dz) <= 0:
        raise ErrorDeDatos(f"{nombre}: caja de dimensiones no positivas {caja.dims}")
    return caja


def cargar_layout(ruta: Path | None = None) -> Layout:
    ruta = ruta or (DIR_DATOS / "layout.yaml")
    if not ruta.exists():
        return Layout(estado="ausente", meta={}, zonas=[], colocaciones=[], keep_outs=[])
    bruto = yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    meta = bruto.get("meta", {})

    zonas = [
        Zona(
            id=z["id"],
            nombre=z.get("nombre", z["id"]),
            caja=_caja_desde(z["caja"], f"zona {z['id']}"),
            nota=z.get("nota"),
        )
        for z in (bruto.get("zonas") or [])
    ]

    colocaciones: list[Colocacion] = []
    for c in bruto.get("colocaciones") or []:
        instancia = int(c.get("instancia", 1))
        cid = c["componente"]
        colocaciones.append(
            Colocacion(
                componente_id=cid,
                instancia=instancia,
                centro=tuple(float(v) for v in c["centro"]),  # type: ignore[arg-type]
                rotacion=tuple(float(v) for v in c.get("rotacion", (0, 0, 0))),  # type: ignore[arg-type]
                zona=c.get("zona"),
                nombre=c.get("nombre") or (
                    cid if instancia == 1 else f"{cid}_{instancia}"
                ),
            )
        )

    keep_outs = [
        KeepOut(
            id=k["id"],
            tipo=k.get("tipo", "generico"),
            caja=_caja_desde(k["caja"], f"keep_out {k['id']}"),
            nota=k.get("nota"),
            estado=k.get("estado", "supuesto"),
            fuente=k.get("fuente"),
        )
        for k in (bruto.get("keep_out") or [])
    ]

    return Layout(
        estado=meta.get("estado", "propuesta"),
        meta=meta,
        zonas=zonas,
        colocaciones=colocaciones,
        keep_outs=keep_outs,
    )


@dataclass
class PiezaColocada:
    colocacion: Colocacion
    componente: object  # Componente
    solido: cq.Solid | cq.Compound
    caja_mundo: Caja


def _localizar(solido, colocacion: Colocacion):
    rx, ry, rz = colocacion.rotacion
    resultado = solido
    origen = cq.Vector(0, 0, 0)
    if rx:
        resultado = resultado.rotate(origen, cq.Vector(1, 0, 0), rx)
    if ry:
        resultado = resultado.rotate(origen, cq.Vector(0, 1, 0), ry)
    if rz:
        resultado = resultado.rotate(origen, cq.Vector(0, 0, 1), rz)
    return resultado.moved(cq.Location(cq.Vector(*colocacion.centro)))


def construir(catalogo: Catalogo, layout: Layout) -> list[PiezaColocada]:
    """Situa en el mundo cada colocacion del layout."""
    piezas: list[PiezaColocada] = []
    for colocacion in layout.colocaciones:
        if not catalogo.existe(colocacion.componente_id):
            raise ErrorDeDatos(
                f"layout: '{colocacion.componente_id}' no existe en components.yaml"
            )
        componente = catalogo[colocacion.componente_id]
        if not componente.modelable:
            raise ErrorDeDatos(
                f"layout: '{componente.id}' tiene geometria TBD y no se puede colocar. "
                f"Consigue sus dimensiones antes de situarlo."
            )
        solido_mundo = _localizar(parts.solido(componente), colocacion)
        bb = solido_mundo.BoundingBox()
        piezas.append(
            PiezaColocada(
                colocacion=colocacion,
                componente=componente,
                solido=solido_mundo,
                caja_mundo=Caja(bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax),
            )
        )
    return piezas


def ensamblaje(
    catalogo: Catalogo, layout: Layout, con_estructura: bool = True
) -> cq.Assembly:
    """Ensamblaje CadQuery, con nombres y colores, listo para exportar a STEP."""
    raiz = cq.Assembly(name="CLAU_6U")

    if con_estructura:
        raiz.add(
            structure.solido_estructura(catalogo),
            name="estructura_6u_generica",
            color=cq.Color(0.55, 0.55, 0.58, 0.25),
        )
        for nombre, caja in structure.railes(catalogo):
            raiz.add(caja.solido(), name=nombre, color=cq.Color(0.35, 0.35, 0.38, 0.6))

    for pieza in construir(catalogo, layout):
        raiz.add(
            pieza.solido,
            name=pieza.colocacion.etiqueta,
            color=parts.color(pieza.componente),  # type: ignore[arg-type]
        )

    for keep_out in layout.keep_outs:
        raiz.add(
            keep_out.caja.solido(),
            name=f"keepout_{keep_out.id}",
            # Casi transparente si sale de un numero inventado: ocupa sitio en
            # la pantalla, pero no tanto como para que parezca una pieza.
            color=cq.Color(1.0, 0.1, 0.1, 0.10 if keep_out.es_supuesto else 0.22),
        )

    return raiz


def exportar_por_subsistema(
    catalogo: Catalogo, layout: Layout, destino: Path
) -> dict[str, Path]:
    """Un STEP por subsistema, con las piezas en su sitio del ensamblaje.

    No es un despiece: cada fichero lleva las coordenadas del satelite
    completo, asi que abrir dos de ellos a la vez los ensena encajados. Sirve
    para mirar un subsistema sin cargar los 550 solidos del conjunto, y para
    mandarle a alguien SOLO su parte.

    **El nombre del fichero dice si se puede versionar.** Un STEP de subsistema
    que contenga una pieza dibujada con CAD de fabricante CONTIENE ese CAD, y
    el repositorio es publico. Los que salen solo de cajas envolventes propias
    se suben; los otros, no. Para que esa distincion no dependa de que alguien
    mantenga una lista a mano -- y se quede obsoleta en cuanto llegue el
    siguiente STEP de proveedor --, el sufijo lo pone este exportador mirando
    lo que ha metido dentro, y el .gitignore ignora ese sufijo. Hoy son el EPS
    (141 MB, con la bateria de AAC) y el OBC (32 MB); manana seran los que
    sean.
    """
    destino.mkdir(parents=True, exist_ok=True)
    por_subsistema: dict[str, list[PiezaColocada]] = {}
    for pieza in construir(catalogo, layout):
        componente = pieza.componente
        clave = getattr(componente, "subsistema", "") or "sin_subsistema"
        por_subsistema.setdefault(clave, []).append(pieza)

    escritos: dict[str, Path] = {}
    for subsistema, piezas in sorted(por_subsistema.items()):
        montaje = cq.Assembly(name=f"CLAU_{subsistema}")
        con_fabricante = False
        for pieza in piezas:
            con_fabricante = con_fabricante or parts.step_disponible(
                pieza.componente  # type: ignore[arg-type]
            )
            montaje.add(
                pieza.solido,
                name=pieza.colocacion.etiqueta,
                color=parts.color(pieza.componente),  # type: ignore[arg-type]
            )
        sufijo = SUFIJO_CAD_DE_FABRICANTE if con_fabricante else ""
        ruta = destino / f"{subsistema}{sufijo}.step"
        # Si el subsistema cambio de lado (llego un STEP de proveedor, o se
        # quito), el fichero con el otro nombre se queda mintiendo en disco.
        otro = destino / f"{subsistema}{'' if sufijo else SUFIJO_CAD_DE_FABRICANTE}.step"
        otro.unlink(missing_ok=True)
        montaje.export(str(ruta))
        escritos[subsistema] = ruta
    return escritos


def exportar_step(
    catalogo: Catalogo, layout: Layout, destino: Path
) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    ensamblaje(catalogo, layout).export(str(destino))
    return destino
