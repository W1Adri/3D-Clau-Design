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
    SUPUESTO,
    TBD,
    Catalogo,
    Componente,
    Conector,
    ErrorDeDatos,
    FuenteStep,
    RAIZ,
)
from .structure import Caja

# El estado del dato manda sobre la categoria: un TBD se ve a la legua.
COLOR_POR_ESTADO = {
    REFERENCIA: (1.00, 0.55, 0.00),   # naranja: dato de un componente parecido
    DECISION: (0.20, 0.45, 0.90),     # azul: decision de diseno de ACSAR
    SUPUESTO: (0.62, 0.62, 0.66),     # gris: numero inventado, solo reserva sitio
    TBD: (1.00, 0.00, 0.80),          # magenta: falta el dato
}

# Un supuesto se dibuja MAS transparente que lo demas. No es decoracion: es la
# unica pista que tiene quien mira el visor de que ese cuerpo no esta ahi porque
# nadie haya medido nada, sino para que el hueco no parezca vacio.
TRANSPARENCIA_SUPUESTO = 0.78

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
    fuente = fuente_step(componente)
    if fuente is not None:
        return fuente.estado
    return componente.dimensiones.estado


def color(componente: Componente) -> cq.Color:
    estado = estado_geometria(componente)
    if estado == CONFIRMADO:
        rgb = COLOR_POR_CATEGORIA.get(componente.categoria, (0.7, 0.7, 0.7))
    else:
        rgb = COLOR_POR_ESTADO.get(estado, (0.7, 0.7, 0.7))
    alfa = TRANSPARENCIA_SUPUESTO if estado == SUPUESTO else TRANSPARENCIA
    return cq.Color(*rgb, alfa)


def fuente_step(componente: Componente) -> FuenteStep | None:
    """El STEP que se va a dibujar, venga de donde venga, o None.

    Hay dos maneras de que un componente tenga STEP, y las dos exigen
    procedencia declarada:

    1. ``forma.step``: el fichero ya llego y alguien escribio de donde salio.
    2. ``forma.step_esperado``: el fichero TODAVIA no ha llegado, pero ya se
       sabe quien lo tiene y de que producto es, asi que la procedencia esta
       escrita por adelantado. Dejarlo en la ruta indicada basta para que el
       modelo lo dibuje en lugar del aproximado, sin tocar el catalogo. Se
       conecta siempre como 'referencia': que el fichero haya aparecido donde
       se esperaba no verifica su part number.

    Lo que NO existe es la tercera manera, la de coger cualquier fichero que se
    llame como el componente. Un STEP sin procedencia es lo mismo que un numero
    sin fuente, y este repositorio no admite ninguno de los dos.
    """
    if componente.step is not None and (RAIZ / componente.step.ruta).exists():
        return componente.step
    esperado = componente.step_esperado
    if esperado is not None and (RAIZ / esperado.ruta).exists():
        return FuenteStep(
            ruta=esperado.ruta,
            estado=REFERENCIA,
            fuente=esperado.fuente_prevista,
            nota=(
                f"Conectado automaticamente al aparecer en {esperado.ruta} "
                f"(forma.step_esperado). Procedencia prevista: "
                f"{esperado.pedir_a}. Estado 'referencia' hasta verificar el "
                f"part number contra la ficha."
            ),
            orientacion=esperado.orientacion,
            recentrar=esperado.recentrar,
        )
    return None


def ruta_step(componente: Componente) -> Path | None:
    """Ruta del STEP a dibujar, o None si hay que caer a la caja envolvente.

    Los CAD de fabricante no se versionan (ver cad/vendor/MANIFEST.yaml), asi
    que un clon recien hecho no los tiene. Eso NO es un error: el componente se
    dibuja con su caja envolvente y el chequeo 'step_de_fabricante' lo dice.
    Solo es un error cuando no hay caja a la que caer.
    """
    fuente = fuente_step(componente)
    if fuente is not None:
        return RAIZ / fuente.ruta
    if componente.step is None:
        return None
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
    return fuente_step(componente) is not None


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


# Indice de eje por nombre, para pasar de "X" a la componente 0 del vector.
_INDICE_EJE = {"X": 0, "Y": 1, "Z": 2}
_DIRECCION_CARA = {
    "+X": (0, 1.0), "-X": (0, -1.0),
    "+Y": (1, 1.0), "-Y": (1, -1.0),
    "+Z": (2, 1.0), "-Z": (2, -1.0),
}


def _cuerpo(componente: Componente) -> cq.Solid:
    """Envolvente del cuerpo, sin conectores: caja o cilindro."""
    dims = componente.dimensiones.como_vector()
    assert dims is not None
    if componente.tipo_forma != "cilindro":
        return Caja.centrada(dims).solido()

    # Un cilindro se declara con su caja envolvente igual que todo lo demas
    # -- asi los presupuestos, el chequeo de seccion y el prefiltro de
    # interferencias no tienen que saber que forma tiene --, y 'forma.eje' dice
    # cual de las tres cotas es la longitud. Las otras dos son el diametro, y
    # 'validar' comprueba que coinciden: un "cilindro" de seccion ovalada seria
    # una cota mal copiada, no una pieza.
    eje = componente.eje_revolucion or "Z"
    indice = _INDICE_EJE[eje]
    longitud = dims[indice]
    diametro = max(d for i, d in enumerate(dims) if i != indice)
    cilindro = cq.Solid.makeCylinder(
        diametro / 2, longitud, cq.Vector(0, 0, -longitud / 2)
    )
    # makeCylinder crece por Z; se lleva al eje declarado.
    if eje == "X":
        cilindro = cilindro.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), 90)
    elif eje == "Y":
        cilindro = cilindro.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)
    return cilindro


def _solido_conector(componente: Componente, conector: Conector) -> cq.Solid | None:
    """Caja del conector, pegada por fuera a la cara que declara.

    Devuelve None si sus cotas son TBD: un conector sin medidas no se dibuja de
    ningun tamano, igual que una pieza sin envolvente. El cuerpo se dibuja
    igual, y el hueco sale en la lista de pendientes.
    """
    if conector.dimensiones.es_tbd or not conector.dimensiones.esta_declarada:
        return None
    cuerpo = componente.dimensiones.como_vector()
    assert cuerpo is not None
    dims = conector.dimensiones.como_vector()
    assert dims is not None

    indice, signo = _DIRECCION_CARA[conector.cara]
    # El conector arranca en la cara del cuerpo y sobresale hacia fuera, asi que
    # su centro queda a media altura del conector mas alla de esa cara.
    centro = [0.0, 0.0, 0.0]
    centro[indice] = signo * (cuerpo[indice] / 2 + dims[indice] / 2)
    # El desplazamiento recorre el plano de la cara, en los otros dos ejes y en
    # su orden natural (para +-X: Y y luego Z).
    otros = [i for i in range(3) if i != indice]
    for eje_plano, delta in zip(otros, conector.desplazamiento):
        centro[eje_plano] += delta
    return Caja.centrada(dims, tuple(centro)).solido()


def solido(
    componente: Componente, catalogo: Catalogo | None = None
) -> cq.Solid | cq.Compound:
    """Solido del componente en su propio sistema de ejes, centrado en el origen.

    Con STEP de fabricante, el STEP. Sin el, la envolvente declarada -- caja,
    cilindro o el modelo parametrico del Cassegrain -- mas los conectores que
    sobresalgan de ella. Los conectores no son decoracion: son lo que decide si
    la pieza cabe con el cable puesto.

    ``catalogo`` solo hace falta para las formas que se derivan de mas de un
    componente. Hoy es el ``cassegrain``, que necesita el diametro de haz
    SUPUESTO de ``integracion.optica`` -- el mismo con el que se dibujan los
    keep-outs del banco, porque es el mismo haz.
    """
    ruta = ruta_step(componente)
    if ruta is not None:
        fuente = fuente_step(componente)
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
    if componente.tipo_forma == "cassegrain":
        from .optica import cassegrain

        if catalogo is None:
            raise ErrorDeDatos(
                f"{componente.id}: es un 'cassegrain' y su geometria se deriva "
                f"tambien de 'integracion.optica' del catalogo. Llama a "
                f"parts.solido(componente, catalogo)."
            )
        return cassegrain.solido(componente, catalogo)
    cuerpo = _cuerpo(componente)
    conectores = [
        solido_conector
        for conector in componente.conectores
        if (solido_conector := _solido_conector(componente, conector)) is not None
    ]
    if not conectores:
        return cuerpo
    return cq.Compound.makeCompound([cuerpo, *conectores])


def tiene_envolvente_propia(componente: Componente) -> bool:
    """True si lo que se analiza NO es lo mismo que lo que se dibuja.

    Solo el modelo parametrico del Cassegrain, y solo mientras se dibuje con el:
    en cuanto llega el STEP del fabricante, el solido vuelve a ser uno solo.
    """
    return componente.tipo_forma == "cassegrain" and not step_disponible(componente)


def solido_envolvente(
    componente: Componente, catalogo: Catalogo | None = None
) -> cq.Solid | cq.Compound:
    """El solido con el que se ANALIZA, que no siempre es el que se dibuja.

    Para casi todas las piezas es el mismo: una caja es maciza y un STEP de
    fabricante trae la pieza entera. La excepcion es el modelo parametrico del
    Cassegrain, que es HUECO: un barrilete con dos espejos dentro y aire en
    medio. Si ese hueco entrara en el analisis de volumen, el interior del tubo
    saldria como sitio libre donde meter algo, y no lo es -- ahi va el haz --;
    y si entrara en la booleana de interferencias, una pieza vecina podria
    meterse dentro del tubo sin que nadie se quejara.

    Lo que se reserva se mide sobre lo que se dibuja (CLAUDE.md 2), y lo que el
    telescopio reserva es el prisma entero. Quien pide un solido dice cual de
    los dos quiere: el visor y el export STEP piden ``solido``, el analisis
    pide este.
    """
    if tiene_envolvente_propia(componente):
        from .optica import cassegrain

        return cassegrain.envolvente(componente)
    return solido(componente, catalogo)


def _girado(forma: Shape, grados: tuple[float, float, float]) -> Shape:
    """Gira alrededor de X, Y y Z en ese orden, sobre el origen del STEP."""
    ejes = (cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1))
    for eje, angulo in zip(ejes, grados):
        if abs(angulo) > 1e-9:
            forma = forma.rotate(cq.Vector(0, 0, 0), eje, angulo)
    return forma


def caja_local(
    componente: Componente, catalogo: Catalogo | None = None
) -> Caja | None:
    """Caja envolvente del componente en sus ejes locales, conectores incluidos."""
    if not componente.modelable:
        return None
    if step_disponible(componente) or componente.conectores:
        return caja_de_solidos(solido(componente, catalogo), componente.id)
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
        cq.exporters.export(solido(componente, catalogo), str(ruta))
        escritos.append(ruta)
    return escritos
