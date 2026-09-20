"""Geometria del Cassegrain: barrilete, espejos, arana, baffles y celda.

Sustituye al cilindro de reserva de 95.4 x 95.4 x 200 mm, pero **no cambia de
estado**: sigue siendo una pieza SUPUESTA. Un modelo detallado no es un dato de
fabricante; es el mismo hueco reservado, dibujado con mas detalle. Se sigue
pintando en gris y con TRANSPARENCIA_SUPUESTO, sigue sin sumar en los
presupuestos y sigue saliendo en reports/06_pendientes.md.

Y sigue siendo el FALLBACK: el dia que aparezca
``cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step``,
``parts.ruta_step`` lo elige a el y esto no se llega a construir. El STEP manda
sobre el modelo aproximado igual que mandaba sobre el cilindro.

Dos invariantes que este modulo se comprueba a si mismo:

1. **La caja envolvente es la declarada.** Lo que se reserva se mide sobre lo
   que se dibuja (CLAUDE.md 2). Si la optica derivada no cupiera dentro de
   ``forma.dimensiones``, el constructor ABORTA en vez de dibujar una pieza que
   se sale: igual que una fila de la bandeja que no cabe aborta el generador.
2. **El interior no es hueco aprovechable.** El solido detallado tiene el tubo
   vacio por dentro, y meterlo tal cual en el analisis de volumen diria que ahi
   cabe algo. Por eso existe :func:`envolvente`, que es el prisma macizo, y es
   lo que usan volumen e interferencias. Ver ``parts.solido_envolvente``.
"""

from __future__ import annotations

import math

import cadquery as cq

from ..datamodel import Catalogo, Componente, ErrorDeDatos
from ..structure import Caja
from .parametros import FOCAL, Mecanica, mecanica

# Segmentos rectos con los que se aproxima el perfil de una conica antes de
# revolucionarlo. NO es una cota del telescopio y por eso no esta en el
# catalogo: es fidelidad de dibujo, del mismo tipo que la tolerancia de
# teselado del visor (CLAUDE.md 8). Con 24 segmentos el error de flecha de un
# paraboloide de 90 mm es del orden de la centesima de milimetro, muy por
# debajo de lo que significa cualquier cota SUPUESTA de esta pieza.
SEGMENTOS_PERFIL_CONICA = 24

# Tolerancia con la que se comprueba que el solido construido no se sale de la
# envolvente declarada.
TOLERANCIA_ENVOLVENTE_MM = 1e-6


def _caja(dx: float, dy: float, dz: float, centro=(0.0, 0.0, 0.0)) -> cq.Solid:
    return Caja.centrada((dx, dy, dz), centro).solido()


def _prisma_z(lado: float, z0: float, z1: float) -> cq.Solid:
    return _caja(lado, lado, z1 - z0, (0.0, 0.0, (z0 + z1) / 2.0))


def _tubo(r_ext: float, r_int: float, z0: float, z1: float) -> cq.Solid:
    fuera = cq.Solid.makeCylinder(r_ext, z1 - z0, cq.Vector(0, 0, z0))
    dentro = cq.Solid.makeCylinder(r_int, (z1 - z0) + 2.0, cq.Vector(0, 0, z0 - 1.0))
    return fuera.cut(dentro)


def _cilindro(radio: float, z0: float, z1: float) -> cq.Solid:
    return cq.Solid.makeCylinder(radio, z1 - z0, cq.Vector(0, 0, z0))


def _perfil_conico(
    r_int: float,
    r_ext: float,
    z_vertice: float,
    espesor: float,
    sagita,
    lado_del_sustrato: float,
) -> cq.Solid:
    """Revoluciona el perfil de un espejo conico anular alrededor del eje Z.

    La cara reflectante SIEMPRE esta en ``z_vertice + sagita(r)``: tanto el
    primario (concavo hacia +Z) como el secundario (convexo hacia -Z) tienen su
    vertice en el punto mas -Z de la superficie y suben con el radio. Lo que
    distingue a uno de otro es hacia donde queda el material:
    ``lado_del_sustrato`` vale -1 para el primario y +1 para el secundario.

    Se revoluciona un perfil de verdad, NO se aproxima con un casquete
    esferico: a f/2.2 la diferencia entre la parabola y la esfera del mismo
    radio es de decimas de milimetro en el borde, que es mas que cualquiera de
    las holguras de las que habla este modelo.
    """
    radios = [
        r_int + (r_ext - r_int) * i / SEGMENTOS_PERFIL_CONICA
        for i in range(SEGMENTOS_PERFIL_CONICA + 1)
    ]
    cara = [(r, z_vertice + sagita(r)) for r in radios]
    z_espalda = z_vertice + lado_del_sustrato * espesor
    puntos = cara + [(r_ext, z_espalda), (r_int, z_espalda)]
    if lado_del_sustrato > 0:
        # Con el sustrato hacia +Z el contorno sale en sentido horario; se
        # invierte para que la cara y la espalda no se crucen.
        puntos = list(reversed(puntos))

    perfil = cq.Workplane("XZ").polyline(puntos).close()
    # Eje de revolucion en coordenadas del plano de trabajo: en "XZ" el eje
    # local Y es el Z global, que es el eje optico.
    return perfil.revolve(360.0, (0, 0), (0, 1)).val()


def _arana(m: Mecanica) -> list[tuple[str, cq.Solid]]:
    """Los vanes que sujetan el secundario, cada uno en su plano axial.

    Van del buje a la pared interior del baffle, en planos que contienen el eje
    optico, que es la unica orientacion que no anade area obstruida: un vane
    visto de canto por el haz colimado solo tapa su espesor.
    """
    largo = m.radio_baffle_interior - m.radio_buje_secundario
    if largo <= 0:
        raise ErrorDeDatos(
            "El buje del secundario llega hasta el baffle: no queda sitio para "
            "la arana. Revisa 'margen_buje_secundario'."
        )
    centro_z = m.z_vertice_secundario + m.espesor_secundario / 2.0
    radio_medio = (m.radio_buje_secundario + m.radio_baffle_interior) / 2.0

    # Un vane es una chapa recta, y sus esquinas se saldrian del cilindro del
    # baffle por unas milesimas. Se recorta contra el en vez de acortarlo a ojo.
    hueco = _cilindro(
        m.radio_baffle_interior,
        centro_z - m.ancho_vane,
        centro_z + m.ancho_vane,
    )
    piezas: list[tuple[str, cq.Solid]] = []
    for i in range(m.vanes):
        angulo = 360.0 * i / m.vanes
        hoja = _caja(largo, m.espesor_vane, m.ancho_vane, (radio_medio, 0.0, centro_z))
        hoja = hoja.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), angulo)
        piezas.append((f"vane_{i + 1}", hoja.intersect(hueco)))
    return piezas


def _celda_primario(m: Mecanica) -> list[tuple[str, cq.Solid]]:
    """Montura isostatica de flexures entre el mamparo trasero y el primario.

    Tres puntos a 120 grados es lo que hace la montura isostatica -- tres
    puntos definen un plano y no introducen esfuerzos al dilatar --, y el
    primero se pone a 45 grados para que caiga en una ESQUINA del barrilete,
    que es donde hay radio: en la esquina quedan ``margen_esquina`` mm y en la
    cara plana solo ``margen_cara_plana``. Esa diferencia es todo el argumento
    de la seccion cuadrada (CLAUDE.md 4.2).
    """
    ancho, largo = m.seccion_flexure
    z0 = m.z_trasero_interior
    z1 = m.z_vertice_primario - m.espesor_primario
    if z1 <= z0:
        raise ErrorDeDatos(
            "La celda del primario tiene altura nula o negativa: revisa "
            "'altura_celda'."
        )
    piezas: list[tuple[str, cq.Solid]] = []
    for i in range(m.flexures):
        angulo = m.angulo_primer_flexure + 360.0 * i / m.flexures
        bloque = _caja(largo, ancho, z1 - z0, (m.radio_flexures, 0.0, (z0 + z1) / 2.0))
        bloque = bloque.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), angulo)
        piezas.append((f"flexure_{i + 1}", bloque))
    return piezas


def _largueros(m: Mecanica) -> list[tuple[str, cq.Solid]]:
    """Los cuatro largueros de esquina: el camino de carga del barrilete.

    En la cara plana no cabe nada (el haz deja ``margen_cara_plana`` mm), asi
    que la seccion resistente tiene que estar en las esquinas. Se recortan
    contra el hueco interior para no solapar con las paredes.
    """
    hueco = m.lado / 2.0 - m.espesor_pared
    interior = _prisma_z(
        2.0 * hueco, m.z_trasero_interior, m.z_frontal_interior
    )
    centro = hueco - m.lado_larguero / 2.0
    piezas: list[tuple[str, cq.Solid]] = []
    for i, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        bloque = _caja(
            m.lado_larguero,
            m.lado_larguero,
            m.z_frontal_interior - m.z_trasero_interior,
            (
                sx * centro,
                sy * centro,
                (m.z_trasero_interior + m.z_frontal_interior) / 2.0,
            ),
        )
        piezas.append((f"larguero_esquina_{i + 1}", bloque.intersect(interior)))
    return piezas


def piezas(componente: Componente, catalogo: Catalogo) -> list[tuple[str, cq.Solid]]:
    """Las piezas del telescopio, cada una con su nombre, en ejes locales.

    Eje optico segun Z. **+Z es la apertura** (mira al cielo) y **-Z es la cara
    de montaje**, que es la brida por la que le entra el haz desde el FSM. Es lo
    que declara 'montaje' en el catalogo, y es lo mismo que declaraba el
    cilindro al que sustituye, asi que la colocacion del layout no cambia.
    """
    m = mecanica(componente, catalogo)
    o = m.optica
    salida: list[tuple[str, cq.Solid]] = []

    r_apertura = o.apertura_libre / 2.0
    r_entrada = m.diametro_agujero_entrada / 2.0
    r_agujero = o.diametro_agujero_primario / 2.0
    r_substrato = o.diametro_substrato_primario / 2.0
    r_secundario = o.diametro_secundario / 2.0

    # --- mamparo trasero: la cara de montaje y la brida al FSM ------------
    placa = _prisma_z(m.lado, m.z_trasero_exterior, m.z_trasero_interior)
    salida.append(
        (
            "mamparo_trasero",
            placa.cut(
                _cilindro(
                    r_entrada,
                    m.z_trasero_exterior - 1.0,
                    m.z_trasero_interior + 1.0,
                )
            ),
        )
    )
    # La brida es un resalte HACIA DENTRO. Hacia fuera invadiria el hueco que
    # el layout le da al banco optico, y la envolvente declarada dejaria de ser
    # la que se dibuja.
    brida = _caja(
        m.brida[0],
        m.brida[1],
        m.espesor_brida,
        (0.0, 0.0, m.z_trasero_interior + m.espesor_brida / 2.0),
    )
    salida.append(
        (
            "brida_interfaz_fsm",
            brida.cut(
                _cilindro(
                    r_entrada,
                    m.z_trasero_interior - 1.0,
                    m.z_trasero_interior + m.espesor_brida + 1.0,
                )
            ),
        )
    )

    # --- mamparo frontal: la apertura libre --------------------------------
    placa = _prisma_z(m.lado, m.z_frontal_interior, m.z_frontal_exterior)
    salida.append(
        (
            "mamparo_frontal",
            placa.cut(
                _cilindro(
                    r_apertura,
                    m.z_frontal_interior - 1.0,
                    m.z_frontal_exterior + 1.0,
                )
            ),
        )
    )

    # --- barrilete: cuatro paredes planas entre los dos mamparos -----------
    fuera = _prisma_z(m.lado, m.z_trasero_interior, m.z_frontal_interior)
    dentro = _prisma_z(
        m.lado - 2.0 * m.espesor_pared,
        m.z_trasero_interior - 1.0,
        m.z_frontal_interior + 1.0,
    )
    salida.append(("barrilete", fuera.cut(dentro)))
    salida += _largueros(m)

    # --- espejos ------------------------------------------------------------
    salida.append(
        (
            "espejo_primario",
            _perfil_conico(
                r_agujero,
                r_substrato,
                m.z_vertice_primario,
                m.espesor_primario,
                o.sagita_primario,
                -1.0,
            ),
        )
    )
    salida.append(
        (
            "espejo_secundario",
            _perfil_conico(
                0.0,
                r_secundario,
                m.z_vertice_secundario,
                m.espesor_secundario,
                o.sagita_secundario,
                +1.0,
            ),
        )
    )

    # --- buje y tornillos de colimacion ------------------------------------
    buje = _tubo(
        m.radio_buje_secundario,
        r_secundario,
        m.z_vertice_secundario,
        m.z_espalda_secundario,
    )
    tornillos: list[tuple[str, cq.Solid]] = []
    for i in range(m.tornillos_colimacion):
        angulo = math.radians(360.0 * i / m.tornillos_colimacion)
        tornillo = _cilindro(
            m.diametro_tornillo / 2.0,
            m.z_vertice_secundario,
            m.z_espalda_secundario,
        ).moved(
            cq.Location(
                cq.Vector(
                    m.radio_tornillos_colimacion * math.cos(angulo),
                    m.radio_tornillos_colimacion * math.sin(angulo),
                    0.0,
                )
            )
        )
        # El tornillo va en SU agujero: se vacia del buje en vez de meterse
        # dentro del material, que contaria dos veces el mismo volumen.
        buje = buje.cut(tornillo)
        tornillos.append((f"tornillo_colimacion_{i + 1}", tornillo))
    salida.append(("buje_secundario", buje))
    salida += tornillos

    salida += _arana(m)
    salida += _celda_primario(m)

    # --- baffles ------------------------------------------------------------
    z_baffle_0 = m.z_vertice_primario + o.sagita_primario(r_substrato)
    salida.append(
        (
            "baffle_principal",
            _tubo(
                m.radio_baffle_exterior,
                m.radio_baffle_interior,
                z_baffle_0,
                m.z_frontal_interior,
            ),
        )
    )
    # Los diafragmas knife-edge proyectan hacia dentro del baffle hasta el
    # borde del haz. Con 90 mm de apertura en 95.4 mm de seccion lo que
    # proyectan es 'holgura_baffle', y no hay mas: ese numero tan pequeno es la
    # medida exacta de lo apretado que va el barrilete.
    tramo = (m.z_frontal_interior - z_baffle_0) / (m.diafragmas + 1)
    for i in range(m.diafragmas):
        z = z_baffle_0 + tramo * (i + 1)
        salida.append(
            (
                f"diafragma_{i + 1}",
                _tubo(
                    m.radio_baffle_interior,
                    r_apertura,
                    z - m.espesor_diafragma / 2.0,
                    z + m.espesor_diafragma / 2.0,
                ),
            )
        )
    salida.append(
        (
            "baffle_primario",
            _tubo(
                m.radio_baffle_primario_exterior,
                r_agujero,
                # Arranca en la SUPERFICIE del espejo, no en el plano del
                # vertice: la conica ya ha subido su flecha a ese radio.
                m.z_vertice_primario
                + o.sagita_primario(m.radio_baffle_primario_exterior),
                m.z_vertice_primario + m.longitud_baffle_primario,
            ),
        )
    )
    salida.append(
        (
            "baffle_secundario",
            _tubo(
                m.radio_baffle_secundario_exterior,
                r_secundario,
                m.z_vertice_secundario - m.longitud_baffle_secundario,
                m.z_vertice_secundario,
            ),
        )
    )

    # --- el foco ------------------------------------------------------------
    # En el afocal NO se dibuja nada: el foco comun de las dos conicas es
    # virtual y poner un marcador ahi seria ensenar un plano imagen que no
    # existe. En el clasico si hay un foco real, y lo interesante es
    # justamente que cae fuera del barrilete, dentro del banco optico.
    if o.configuracion == FOCAL:
        salida.append(
            (
                "foco_real",
                _cilindro(
                    r_entrada / 2.0,
                    m.z_foco_real - m.espesor_diafragma / 2.0,
                    m.z_foco_real + m.espesor_diafragma / 2.0,
                ),
            )
        )

    return salida


def envolvente(componente: Componente) -> cq.Solid:
    """El prisma macizo: lo que el telescopio RESERVA, no lo que ocupa.

    El modelo detallado es hueco. Si el analisis de volumen usara ese hueco,
    el interior del tubo saldria como sitio libre donde meter algo, que es
    falso: ahi dentro va el haz. Los analisis usan esto.
    """
    dims = componente.dimensiones.como_vector()
    if dims is None:
        raise ErrorDeDatos(f"{componente.id}: sin dimensiones no hay envolvente.")
    return Caja.centrada(dims).solido()


def solido(componente: Componente, catalogo: Catalogo) -> cq.Compound:
    """El telescopio entero, comprobado contra su envolvente declarada."""
    partes = piezas(componente, catalogo)
    compuesto = cq.Compound.makeCompound([p for _, p in partes])

    dims = componente.dimensiones.como_vector()
    assert dims is not None
    caja = compuesto.BoundingBox()
    medido = (caja.xlen, caja.ylen, caja.zlen)
    if any(med > dec + TOLERANCIA_ENVOLVENTE_MM for med, dec in zip(medido, dims)):
        m = mecanica(componente, catalogo)
        raise ErrorDeDatos(
            f"{componente.id}: el modelo parametrico mide "
            f"{medido[0]:.2f} x {medido[1]:.2f} x {medido[2]:.2f} mm y no cabe "
            f"en los {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm que "
            f"declara 'forma.dimensiones'. La optica derivada necesita "
            f"{m.longitud_necesaria:.1f} mm de barrilete y el layout le reserva "
            f"{m.longitud:.1f} mm ('longitud_reservada'). No se aprieta: o "
            f"baja la focal del primario, o ACSAR alarga la reserva a costa de "
            f"la bandeja. Ver el chequeo 'longitud_telescopio'."
        )
    return compuesto
