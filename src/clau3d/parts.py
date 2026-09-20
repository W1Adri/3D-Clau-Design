"""Solidos de cada componente: caja envolvente o STEP de fabricante.

Un componente puede estar en cualquiera de los dos estados sin que cambie nada
mas del ensamblaje. Para pasar de caja a STEP basta anadir el bloque
``forma.step`` en ``data/components.yaml``.

Tres cosas que un STEP de fabricante casi nunca trae como el modelo las espera,
y que por eso se arreglan aqui y no a mano:

1. **El origen.** El ensamblaje coloca cada pieza por su centro. Muchos STEP
   vienen con el origen en una esquina o en un punto de montaje, asi que la
   pieza aparece desplazada media pieza. ``FuenteStep.recentrar`` lleva el
   centro de la caja envolvente al origen.
2. **Los ejes.** El proveedor exporta con el eje que le conviene.
   ``FuenteStep.orientacion`` gira el solido hasta los ejes que el catalogo
   declara en ``dimensiones``. No cambia ninguna cota.
3. **La caja envolvente.** ``Shape.BoundingBox()`` sobre el compound de un STEP
   grande puede devolver una caja infinita: basta una entidad degenerada entre
   miles. Aqui la caja se calcula **solido a solido**, que es lo unico que se va
   a dibujar, y se rechaza lo que salga absurdo en vez de propagarlo al
   prefiltro de interferencias y al mapa de hueco libre.

Importar un STEP de fabricante es caro (el del ADCS tarda del orden de tres
minutos). Se cachea en BREP, que se lee en menos de un segundo.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import cadquery as cq
from cadquery.occ_impl.shapes import Shape

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

# Por encima de esto una coordenada no es una pieza de un cubesat, es basura
# geometrica del STEP. Un 6U mide 366 mm; un metro ya seria absurdo.
COORDENADA_ABSURDA_MM = 1e6

# Los STEP de fabricante no se tocan, asi que el BREP cacheado vale mientras el
# fichero no cambie. Fuera de cad/generated/, que si se versiona.
DIR_CACHE = RAIZ / ".cache" / "step"

_EN_MEMORIA: dict[tuple, Shape] = {}


def estado_geometria(componente: Componente) -> str:
    """Procedencia de la geometria que REALMENTE se dibuja.

    ``Componente.estado_geometria`` no mira el disco, y no debe: el catalogo no
    sabe que ficheros hay. Pero un componente con un STEP de referencia que no
    esta descargado se dibuja con su caja de ficha, y entonces pintarlo de color
    referencia enganaria.
    """
    if step_disponible(componente):
        assert componente.step is not None
        return componente.step.estado
    return componente.dimensiones.estado


def color(componente: Componente) -> cq.Color:
    estado = estado_geometria(componente)
    if estado == CONFIRMADO:
        rgb = COLOR_POR_CATEGORIA.get(componente.categoria, (0.7, 0.7, 0.7))
    else:
        rgb = COLOR_POR_ESTADO.get(estado, (0.7, 0.7, 0.7))
    return cq.Color(*rgb, TRANSPARENCIA)


def ruta_step(componente: Componente) -> Path | None:
    """Ruta del STEP de fabricante, o None si no esta disponible.

    Los CAD de fabricante no se versionan (ver cad/vendor/MANIFEST.yaml), asi
    que un clon recien hecho no los tiene. Eso NO es un error: el componente se
    dibuja con su caja envolvente y el chequeo 'step_de_fabricante' lo dice.
    Solo es un error cuando no hay caja a la que caer.
    """
    if componente.step is None:
        return None
    ruta = RAIZ / componente.step.ruta
    if ruta.exists():
        return ruta
    if componente.dimensiones.esta_declarada and not componente.dimensiones.es_tbd:
        return None
    raise ErrorDeDatos(
        f"{componente.id}: forma.step apunta a '{componente.step.ruta}', que no "
        f"esta, y el componente no declara dimensiones con las que dibujar una "
        f"caja. Baja el fichero (ver cad/vendor/MANIFEST.yaml) o declara sus "
        f"dimensiones."
    )


def step_disponible(componente: Componente) -> bool:
    """True si el solido va a salir realmente del STEP y no de la caja."""
    return componente.step is not None and (RAIZ / componente.step.ruta).exists()


def caja_de_solidos(forma: Shape, origen: str = "solido") -> Caja:
    """Caja envolvente de un solido o compound, calculada solido a solido.

    ``Shape.BoundingBox()`` sobre un compound importado de un STEP grande puede
    devolver una caja infinita por una sola entidad degenerada. Como lo unico
    que se dibuja son los solidos, la caja se construye desde ellos.
    """
    cajas = [s.BoundingBox() for s in forma.Solids()]
    if not cajas:
        # Sin solidos no hay nada que dibujar, pero puede haber caras sueltas:
        # se usa la caja del conjunto y se comprueba igual.
        cajas = [forma.BoundingBox()]
    caja = Caja(
        min(b.xmin for b in cajas), min(b.ymin for b in cajas), min(b.zmin for b in cajas),
        max(b.xmax for b in cajas), max(b.ymax for b in cajas), max(b.zmax for b in cajas),
    )
    extremo = max(abs(v) for v in (caja.xmin, caja.ymin, caja.zmin,
                                   caja.xmax, caja.ymax, caja.zmax))
    if extremo > COORDENADA_ABSURDA_MM:
        raise ErrorDeDatos(
            f"{origen}: la caja envolvente llega a {extremo:.3g} mm. El fichero "
            f"trae geometria degenerada y no se puede usar para comprobar nada."
        )
    return caja


def _huella(ruta: Path) -> str:
    est = ruta.stat()
    crudo = f"{ruta.resolve()}|{est.st_size}|{est.st_mtime_ns}"
    return hashlib.sha1(crudo.encode("utf-8")).hexdigest()[:16]


def importar_step(ruta: Path) -> Shape:
    """Importa un STEP de fabricante, con cache en BREP.

    El STEP se lee tal cual viene, sin girar ni mover: eso lo hace ``solido()``,
    que es barato y depende del catalogo. La cache guarda solo lo caro.
    """
    clave = (str(ruta.resolve()), _huella(ruta))
    en_memoria = _EN_MEMORIA.get(clave)
    if en_memoria is not None:
        return en_memoria

    cacheado = DIR_CACHE / f"{ruta.stem}-{clave[1]}.brep"
    if cacheado.exists():
        forma = Shape.importBrep(str(cacheado))
    else:
        forma = cq.importers.importStep(str(ruta)).val()
        DIR_CACHE.mkdir(parents=True, exist_ok=True)
        forma.exportBrep(str(cacheado))
    _EN_MEMORIA[clave] = forma
    return forma


def solido(componente: Componente) -> cq.Solid | cq.Compound:
    """Solido del componente en su propio sistema de ejes, centrado en el origen."""
    ruta = ruta_step(componente)
    if ruta is not None:
        fuente = componente.step
        assert fuente is not None
        forma = importar_step(ruta)
        if fuente.girado:
            forma = _girado(forma, fuente.orientacion)
        if fuente.recentrar:
            cx, cy, cz = caja_de_solidos(forma, componente.id).centro
            forma = forma.translate(cq.Vector(-cx, -cy, -cz))
        return forma
    if not componente.modelable:
        raise ErrorDeDatos(
            f"{componente.id}: sin dimensiones y sin STEP. No se puede dibujar."
        )
    dims = componente.dimensiones.como_vector()
    assert dims is not None
    return Caja.centrada(dims).solido()


def _girado(forma: Shape, grados: tuple[float, float, float]) -> Shape:
    """Gira alrededor de X, Y y Z en ese orden, sobre el origen del STEP."""
    ejes = (cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1))
    for eje, angulo in zip(ejes, grados):
        if abs(angulo) > 1e-9:
            forma = forma.rotate(cq.Vector(0, 0, 0), eje, angulo)
    return forma


def caja_local(componente: Componente) -> Caja | None:
    """Caja envolvente del componente en sus ejes locales."""
    if step_disponible(componente):
        return caja_de_solidos(solido(componente), componente.id)
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
        ruta = destino / f"{componente.id}.step"
        if step_disponible(componente):
            # Ya viene de cad/vendor. Si antes era una caja, el STEP generado
            # que quedo en disco es una mentira: ensena una caja envolvente de
            # una pieza que el modelo ya dibuja con su geometria real.
            ruta.unlink(missing_ok=True)
            continue
        cq.exporters.export(solido(componente), str(ruta))
        escritos.append(ruta)
    return escritos
