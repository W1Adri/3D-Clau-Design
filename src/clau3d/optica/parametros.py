"""Configuracion optica del Cassegrain, derivada del catalogo.

Aqui no se decide ningun numero: todos salen del bloque ``optica`` de
``telescopio_cassegrain`` en ``data/components.yaml``, y lo unico que este
modulo hace es las cuentas que relacionan unos con otros. Si una cifra se
puede derivar de otra, NO esta en el catalogo: escribirla dos veces es la
manera segura de que las dos dejen de coincidir.

Lo que se deriva, y de que:

    M   = apertura_libre / diametro_haz_comprimido      (magnificacion)
    f2  = focal_primario / M                            (confocalidad)
    d   = focal_primario - |f2|                         (separacion)
    D2  = diametro_haz_comprimido * margen_secundario
    eps = D2 / apertura_libre                           (obstruccion lineal)

La obstruccion da DOS perdidas distintas, y las dos son de potencia: la
fraccion de potencia recogida es (1 - eps^2), o sea -10 log10(1 - eps^2), y la
intensidad en el eje en campo lejano es (1 - eps^2)^2, o sea
-20 log10(1 - eps^2). Para un enlace optico manda la segunda.

El diametro de haz comprimido es el parametro que lo acopla todo, y HOY NO
EXISTE: es TBD en el catalogo (telescopio_cassegrain.optica) y tambien en cada
tramo de ``data/connections.yaml``. Mientras falte, el modelo dibuja con
``integracion.optica.diametro_haz_modelado``, que es el mismo numero SUPUESTO
con el que ya se dibujan los keep-outs de haz libre del banco. Se lee de alli
y no se copia aqui: el haz que sale del FSM y el que entra por la brida del
telescopio son el mismo haz, y tienen que ser el mismo numero.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..datamodel import (
    PARAMETROS_CASSEGRAIN,
    SUPUESTO,
    TBD,
    Catalogo,
    Componente,
    ErrorDeDatos,
    Magnitud,
)

# Las dos configuraciones que el catalogo admite en 'optica.configuracion'.
AFOCAL = "afocal_mersenne"
FOCAL = "focal_clasico"
CONFIGURACIONES = (AFOCAL, FOCAL)

# De donde sale el diametro de haz con el que se dibuja mientras el de verdad
# sea TBD. Es el mismo nodo que dimensiona los keep-outs e01..e04 del banco.
CLAVE_HAZ_MODELADO = "optica.diametro_haz_modelado"


def magnitud(componente: Componente, nombre: str) -> Magnitud:
    """Una magnitud del bloque ``optica``, o error si el catalogo no la trae."""
    clave = f"optica.{nombre}"
    try:
        return componente.extras[clave]
    except KeyError as exc:
        raise ErrorDeDatos(
            f"{componente.id}: forma.tipo es 'cassegrain' pero el bloque "
            f"'optica' no declara '{nombre}'. Un cassegrain necesita su optica "
            f"completa, igual que un cilindro necesita su eje."
        ) from exc


def _escalar(componente: Componente, nombre: str) -> float:
    m = magnitud(componente, nombre)
    valor = m.escalar()
    if valor is None:
        raise ErrorDeDatos(
            f"{componente.id}.optica.{nombre}: es {m.estado} y no tiene valor "
            f"con el que dibujar."
        )
    return valor


def _vector2(componente: Componente, nombre: str) -> tuple[float, float]:
    m = magnitud(componente, nombre)
    valor = m.valor
    if not isinstance(valor, (list, tuple)) or len(valor) != 2:
        raise ErrorDeDatos(
            f"{componente.id}.optica.{nombre}: se esperaban dos cotas, "
            f"hay {valor!r}"
        )
    return (float(valor[0]), float(valor[1]))


def diametro_haz_modelado(catalogo: Catalogo) -> Magnitud:
    """El haz SUPUESTO con el que se dibuja mientras el real sea TBD."""
    try:
        return catalogo.integracion[CLAVE_HAZ_MODELADO]
    except KeyError as exc:
        raise ErrorDeDatos(
            f"El catalogo no declara 'integracion.{CLAVE_HAZ_MODELADO}', que es "
            f"el diametro de haz SUPUESTO con el que se dibujan los keep-outs "
            f"del banco y el interior del telescopio."
        ) from exc


@dataclass(frozen=True)
class Optica:
    """Configuracion optica completa: lo declarado y lo derivado de ello.

    Todo lo que lleva un comentario ``# derivado`` se calcula en
    :func:`derivar` y NO esta escrito en ningun sitio.
    """

    # --- declarado -----------------------------------------------------
    configuracion: str
    apertura_libre: float
    focal_primario: float
    conica_primario: float
    conica_secundario: float
    diametro_haz: float
    haz_es_supuesto: bool
    distancia_focal_trasera: float

    # --- derivado ------------------------------------------------------
    magnificacion: float
    focal_secundario: float
    separacion: float
    diametro_secundario: float
    diametro_agujero_primario: float
    obstruccion_lineal: float
    # Las DOS cifras de la obstruccion central, que no son la misma en dos
    # convenios: son dos magnitudes distintas y las dos son de potencia. Para
    # un enlace optico manda 'perdida_intensidad_en_eje_db'. Ver 'derivar'.
    perdida_potencia_recogida_db: float
    perdida_intensidad_en_eje_db: float
    diametro_substrato_primario: float

    @property
    def radio_curvatura_primario(self) -> float:
        """R1 = 2 f1. Concava hacia donde mira el telescopio."""
        return 2.0 * self.focal_primario

    @property
    def radio_curvatura_secundario(self) -> float:
        """R2 = 2 f2. Convexa: el secundario del Mersenne es un paraboloide convexo."""
        return 2.0 * self.focal_secundario

    @property
    def es_afocal(self) -> bool:
        return self.configuracion == AFOCAL

    @property
    def relacion_focal_primario(self) -> float:
        """f/# del primario. Con 90 mm y 200 mm de focal sale f/2.22."""
        return self.focal_primario / self.apertura_libre

    def magnificacion_angular(self, angulo_en_el_fsm: float) -> float:
        """Angulo en el cielo para un angulo dado en el haz comprimido.

        Un afocal que EXPANDE el haz por M comprime los angulos por M:
        theta_salida = theta_FSM / M. Es lo que decide cuanto recorrido hay que
        pedirle al FSM para cubrir el punto de adelanto (ver
        ``chequeo_haz_vs_fsm``).
        """
        return angulo_en_el_fsm / self.magnificacion

    def angulo_en_el_fsm(self, angulo_en_el_cielo: float) -> float:
        """El inverso: lo que hay que mover el haz comprimido, en optico."""
        return angulo_en_el_cielo * self.magnificacion

    def sagita(self, radio: float, radio_curvatura: float, conica: float) -> float:
        """Flecha de una conica de revolucion a distancia ``radio`` del eje.

            z(r) = r^2 / (R (1 + sqrt(1 - (1+K) r^2 / R^2)))

        Con K = -1 (parabola) el radicando vale 1 y queda z = r^2 / (2R), que
        es la parabola de siempre. La formula general se usa igual para que
        cambiar la conica en el catalogo cambie la superficie dibujada.
        """
        r2 = radio * radio
        rc = abs(radio_curvatura)
        radicando = 1.0 - (1.0 + conica) * r2 / (rc * rc)
        if radicando < 0.0:
            raise ErrorDeDatos(
                f"La conica K={conica} con R={radio_curvatura:.3f} mm no llega "
                f"a r={radio:.3f} mm: la superficie se corta antes del borde."
            )
        return r2 / (rc * (1.0 + math.sqrt(radicando)))

    def sagita_primario(self, radio: float) -> float:
        return self.sagita(radio, self.radio_curvatura_primario, self.conica_primario)

    def sagita_secundario(self, radio: float) -> float:
        return self.sagita(
            radio, self.radio_curvatura_secundario, self.conica_secundario
        )


def derivar(componente: Componente, catalogo: Catalogo) -> Optica:
    """Configuracion optica del telescopio a partir del catalogo."""
    configuracion = magnitud(componente, "configuracion").valor
    if configuracion not in CONFIGURACIONES:
        raise ErrorDeDatos(
            f"{componente.id}.optica.configuracion: '{configuracion}' no es una "
            f"configuracion conocida (admitidas: {CONFIGURACIONES})"
        )

    apertura = componente.extras.get("apertura_libre")
    if apertura is None or apertura.es_tbd:
        raise ErrorDeDatos(
            f"{componente.id}: sin 'apertura_libre' no hay telescopio que dibujar."
        )
    diametro = apertura.escalar()
    assert diametro is not None

    f1 = _escalar(componente, "focal_primario")

    # El haz comprimido de verdad sigue siendo TBD. Mientras falte, se dibuja
    # con el mismo supuesto que los keep-outs del banco, para que el haz que
    # sale del FSM y el que entra por la brida sean el mismo numero.
    declarado = magnitud(componente, "diametro_haz_comprimido")
    if declarado.es_tbd:
        modelado = diametro_haz_modelado(catalogo)
        haz = modelado.escalar()
        haz_es_supuesto = True
    else:
        haz = declarado.escalar()
        haz_es_supuesto = declarado.estado == SUPUESTO
    if haz is None or haz <= 0:
        raise ErrorDeDatos(
            f"{componente.id}: no hay diametro de haz comprimido con el que "
            f"derivar la magnificacion."
        )

    magnificacion = diametro / haz
    focal_secundario = f1 / magnificacion
    # Confocalidad: el foco del primario y el del secundario coinciden, asi que
    # la separacion entre vertices es f1 - |f2|. Es lo que hace que el sistema
    # sea afocal y que no haga falta ninguna lente de enfoque.
    separacion = f1 - abs(focal_secundario)

    d2 = haz * _escalar(componente, "margen_secundario")
    agujero = d2 + _escalar(componente, "margen_agujero_primario")
    epsilon = d2 / diametro
    # DOS CIFRAS DISTINTAS, LAS DOS EN POTENCIA. No son dos convenios de la
    # misma magnitud -- eso decia el comentario que habia aqui, y era falso --
    # sino dos magnitudes que responden a dos preguntas distintas:
    #
    #   * POTENCIA RECOGIDA: la obstruccion tapa una fraccion eps^2 del area,
    #     asi que pasa (1 - eps^2) de la potencia. Son -10 log10(1 - eps^2).
    #     Es la que vale si lo que se pregunta es cuanta luz sale del tubo.
    #
    #   * INTENSIDAD EN EL EJE en campo lejano: la obstruccion no solo quita
    #     area, redistribuye energia del lobulo principal a los anillos. El
    #     campo en el eje es proporcional al area despejada, y la intensidad a
    #     su cuadrado: (1 - eps^2)^2, o sea -20 log10(1 - eps^2).
    #
    # PARA UN ENLACE OPTICO MANDA LA SEGUNDA: lo que llega al receptor es la
    # intensidad en el eje, no la potencia total que sale del telescopio. Cual
    # manda esta declarado en el catalogo como
    # 'integracion.optica.perdida_obstruccion_convenio'; los numeros no, porque
    # se derivan de eps y escribirlos alli seria duplicarlos.
    transmitido = 1.0 - epsilon * epsilon
    perdida_potencia_db = -10.0 * math.log10(transmitido)
    perdida_intensidad_db = -20.0 * math.log10(transmitido)

    substrato = diametro + 2.0 * _escalar(componente, "margen_substrato_primario")

    return Optica(
        configuracion=str(configuracion),
        apertura_libre=diametro,
        focal_primario=f1,
        conica_primario=_escalar(componente, "conica_primario"),
        conica_secundario=_escalar(componente, "conica_secundario"),
        diametro_haz=haz,
        haz_es_supuesto=haz_es_supuesto,
        distancia_focal_trasera=_escalar(componente, "distancia_focal_trasera"),
        magnificacion=magnificacion,
        focal_secundario=focal_secundario,
        separacion=separacion,
        diametro_secundario=d2,
        diametro_agujero_primario=agujero,
        obstruccion_lineal=epsilon,
        perdida_potencia_recogida_db=perdida_potencia_db,
        perdida_intensidad_en_eje_db=perdida_intensidad_db,
        diametro_substrato_primario=substrato,
    )


@dataclass(frozen=True)
class Mecanica:
    """Cotas mecanicas del barrilete y posiciones derivadas de la pila en Z.

    La pila en Z es lo unico que decide si el telescopio cabe en lo que el
    layout le reserva, y no se ve mirando volumenes:

        mamparo trasero + celda + espejo primario
        + separacion(f1, M)
        + espejo secundario + mamparo frontal   <=   longitud_reservada

    La separacion la fija la optica; todo lo demas son espesores. Por eso los
    espesores del catalogo llevan escrito en su 'fuente' que son COTA SUPERIOR
    impuesta por la longitud reservada, igual que el colimador y D1
    del banco (CLAUDE.md 3.7).
    """

    optica: Optica
    lado: float                      # seccion cuadrada del barrilete
    longitud: float                  # la que reserva el layout
    espesor_pared: float
    espesor_mamparo: float
    espesor_brida: float
    brida: tuple[float, float]
    diametro_agujero_entrada: float
    altura_celda: float
    espesor_primario: float
    espesor_secundario: float
    holgura_baffle: float
    espesor_baffle: float
    diafragmas: int
    espesor_diafragma: float
    vanes: int
    espesor_vane: float
    ancho_vane: float
    flexures: int
    radio_flexures: float
    angulo_primer_flexure: float
    seccion_flexure: tuple[float, float]
    margen_buje: float
    tornillos_colimacion: int
    diametro_tornillo: float
    lado_larguero: float
    angulo_exclusion_solar: float

    # --- caras del barrilete, en el eje local Z ------------------------
    @property
    def z_trasero_exterior(self) -> float:
        return -self.longitud / 2.0

    @property
    def z_frontal_exterior(self) -> float:
        return self.longitud / 2.0

    @property
    def z_trasero_interior(self) -> float:
        return self.z_trasero_exterior + self.espesor_mamparo

    @property
    def z_frontal_interior(self) -> float:
        return self.z_frontal_exterior - self.espesor_mamparo

    # --- optica dentro del barrilete -----------------------------------
    @property
    def z_vertice_primario(self) -> float:
        """El primario se apoya en el mamparo trasero a traves de la celda."""
        return (
            self.z_trasero_interior
            + self.altura_celda
            + self.espesor_primario
        )

    @property
    def z_vertice_secundario(self) -> float:
        return self.z_vertice_primario + self.optica.separacion

    @property
    def z_espalda_secundario(self) -> float:
        return self.z_vertice_secundario + self.espesor_secundario

    @property
    def margen_longitud(self) -> float:
        """Lo que sobra entre la espalda del secundario y el mamparo frontal.

        Negativo significa que la optica derivada NO cabe en lo que el layout
        le reserva. No se corrige encogiendo nada: se reporta.
        """
        return self.z_frontal_interior - self.z_espalda_secundario

    @property
    def longitud_necesaria(self) -> float:
        """Longitud minima de barrilete para esta optica y estos espesores."""
        return self.longitud - self.margen_longitud

    # --- radios ---------------------------------------------------------
    @property
    def radio_interior_barrilete(self) -> float:
        """Circulo inscrito en el hueco cuadrado que dejan las cuatro paredes."""
        return self.lado / 2.0 - self.espesor_pared

    @property
    def radio_esquina_barrilete(self) -> float:
        """Semidiagonal: el radio de que se dispone EN LA ESQUINA."""
        return self.lado * math.sqrt(2.0) / 2.0

    @property
    def radio_baffle_interior(self) -> float:
        return self.optica.apertura_libre / 2.0 + self.holgura_baffle

    @property
    def radio_baffle_exterior(self) -> float:
        return self.radio_baffle_interior + self.espesor_baffle

    @property
    def margen_cara_plana(self) -> float:
        """Lo que queda entre el haz y la pared, MIRANDO A LA CARA PLANA."""
        return self.lado / 2.0 - self.optica.apertura_libre / 2.0

    @property
    def margen_esquina(self) -> float:
        """Lo mismo mirando a la ESQUINA. Es el argumento de la seccion cuadrada."""
        return self.radio_esquina_barrilete - self.optica.apertura_libre / 2.0

    @property
    def radio_buje_secundario(self) -> float:
        return self.optica.diametro_secundario / 2.0 + self.margen_buje

    @property
    def radio_tornillos_colimacion(self) -> float:
        """A mitad de camino entre el borde del secundario y el del buje."""
        return (self.optica.diametro_secundario / 2.0 + self.radio_buje_secundario) / 2.0

    @property
    def radio_baffle_primario_exterior(self) -> float:
        return self.optica.diametro_agujero_primario / 2.0 + self.espesor_baffle

    @property
    def radio_baffle_secundario_exterior(self) -> float:
        return self.optica.diametro_secundario / 2.0 + self.espesor_baffle

    def _longitud_baffle(self, radio: float) -> float:
        """Longitud de un baffle para un angulo de exclusion solar dado.

        REGLA DE PRIMER ORDEN, no un analisis de luz parasita: un tubo de radio
        r bloquea la vision directa del agujero para rayos que entren por
        encima de theta cuando su longitud llega a r / tan(theta). El numero de
        verdad sale de un trazado de rayos con el angulo de exclusion real, que
        es TBD en el catalogo ('optica.angulo_exclusion_solar').
        """
        return radio / math.tan(math.radians(self.angulo_exclusion_solar))

    @property
    def longitud_baffle_primario(self) -> float:
        return self._longitud_baffle(self.radio_baffle_primario_exterior)

    @property
    def longitud_baffle_secundario(self) -> float:
        return self._longitud_baffle(self.radio_baffle_secundario_exterior)

    @property
    def z_foco_real(self) -> float:
        """Donde caeria el foco del clasico: detras del vertice del primario."""
        return self.z_vertice_primario - self.optica.distancia_focal_trasera


def mecanica(componente: Componente, catalogo: Catalogo) -> Mecanica:
    """Cotas mecanicas del barrilete, leidas del catalogo."""
    optica = derivar(componente, catalogo)
    dims = componente.dimensiones.como_vector()
    if dims is None:
        raise ErrorDeDatos(f"{componente.id}: sin dimensiones no hay barrilete.")
    seccion = _vector2(componente, "seccion_barrilete")
    if abs(seccion[0] - seccion[1]) > 1e-6:
        raise ErrorDeDatos(
            f"{componente.id}.optica.seccion_barrilete: {seccion} no es "
            f"cuadrada. La seccion cuadrada es lo que da radio en las esquinas; "
            f"si deja de serlo, el razonamiento de CLAUDE.md 4.2 no aplica."
        )
    if abs(seccion[0] - dims[0]) > 1e-6 or abs(seccion[1] - dims[1]) > 1e-6:
        raise ErrorDeDatos(
            f"{componente.id}: 'optica.seccion_barrilete' dice {seccion} y "
            f"'forma.dimensiones' dice {dims[:2]}. Lo que se reserva se mide "
            f"sobre lo que se dibuja: las dos tienen que ser la misma cota."
        )
    # Y lo mismo con la LONGITUD, por el mismo motivo. 'longitud_reservada' es
    # lo que el generador usa para repartir Z entre telescopio, banco y
    # bandeja; la tercera cota de 'forma.dimensiones' es lo que se DIBUJA y lo
    # que miden el volumen y las interferencias. Son el mismo numero escrito
    # dos veces, asi que o coinciden o el modelo esta diciendo dos cosas
    # distintas a la vez. Paso de 200 a 227 el 2026-09-21 (CLAUDE.md 3.11) y
    # fue justo aqui donde se vio que habia dos copias.
    reservada = componente.extras.get("longitud_reservada")
    valor_reservado = None if reservada is None else reservada.escalar()
    if valor_reservado is not None and abs(valor_reservado - dims[2]) > 1e-6:
        raise ErrorDeDatos(
            f"{componente.id}: 'longitud_reservada' dice {valor_reservado} mm y "
            f"la tercera cota de 'forma.dimensiones' dice {dims[2]} mm. El "
            f"layout reparte Z con la primera y el analisis mide con la "
            f"segunda: si divergen, lo reservado y lo dibujado dejan de hablar "
            f"de lo mismo (CLAUDE.md 2, y es lo que costo 46 mm en la pila "
            f"PC104)."
        )

    return Mecanica(
        optica=optica,
        lado=seccion[0],
        longitud=dims[2],
        espesor_pared=_escalar(componente, "espesor_pared_barrilete"),
        espesor_mamparo=_escalar(componente, "espesor_mamparo"),
        espesor_brida=_escalar(componente, "espesor_brida"),
        brida=_vector2(componente, "brida_interfaz_fsm"),
        diametro_agujero_entrada=(
            optica.diametro_haz + 2.0 * _escalar(componente, "margen_agujero_entrada")
        ),
        altura_celda=_escalar(componente, "altura_celda"),
        espesor_primario=_escalar(componente, "espesor_espejo_primario"),
        espesor_secundario=_escalar(componente, "espesor_espejo_secundario"),
        holgura_baffle=_escalar(componente, "holgura_baffle"),
        espesor_baffle=_escalar(componente, "espesor_baffle"),
        diafragmas=int(_escalar(componente, "diafragmas_internos")),
        espesor_diafragma=_escalar(componente, "espesor_diafragma"),
        vanes=int(_escalar(componente, "vanes")),
        espesor_vane=_escalar(componente, "espesor_vane"),
        ancho_vane=_escalar(componente, "ancho_vane"),
        flexures=int(_escalar(componente, "flexures")),
        radio_flexures=_escalar(componente, "radio_circulo_flexures"),
        angulo_primer_flexure=_escalar(componente, "angulo_primer_flexure"),
        seccion_flexure=_vector2(componente, "seccion_flexure"),
        margen_buje=_escalar(componente, "margen_buje_secundario"),
        tornillos_colimacion=int(_escalar(componente, "tornillos_colimacion")),
        diametro_tornillo=_escalar(componente, "diametro_tornillo_colimacion"),
        lado_larguero=_escalar(componente, "lado_larguero_esquina"),
        angulo_exclusion_solar=_escalar(componente, "angulo_exclusion_solar_modelado"),
    )


def es_cassegrain(componente: Componente) -> bool:
    return componente.tipo_forma == "cassegrain"


def faltan_parametros(componente: Componente) -> list[str]:
    """Los parametros de ``optica`` que el catalogo no declara."""
    return [
        nombre
        for nombre in PARAMETROS_CASSEGRAIN
        if f"optica.{nombre}" not in componente.extras
    ]


def resumen(componente: Componente, catalogo: Catalogo) -> dict:
    """Lo derivado, en un diccionario, para el visor y los informes.

    El visor NO calcula ninguna cota (CLAUDE.md 8): lo que ensena sale de aqui.
    """
    m = mecanica(componente, catalogo)
    o = m.optica
    haz = magnitud(componente, "diametro_haz_comprimido")
    return {
        "configuracion": o.configuracion,
        "afocal": o.es_afocal,
        "haz_es_supuesto": o.haz_es_supuesto,
        "haz_estado": SUPUESTO if o.haz_es_supuesto else haz.estado,
        "declarado": {
            "apertura_libre_mm": o.apertura_libre,
            "focal_primario_mm": o.focal_primario,
            "relacion_focal_primario": o.relacion_focal_primario,
            "conica_primario": o.conica_primario,
            "conica_secundario": o.conica_secundario,
            "diametro_haz_comprimido_mm": o.diametro_haz,
            "seccion_barrilete_mm": m.lado,
            "longitud_barrilete_mm": m.longitud,
        },
        "derivado": {
            "magnificacion": o.magnificacion,
            "focal_secundario_mm": o.focal_secundario,
            "separacion_mm": o.separacion,
            "diametro_secundario_mm": o.diametro_secundario,
            "diametro_agujero_primario_mm": o.diametro_agujero_primario,
            "obstruccion_lineal": o.obstruccion_lineal,
            "perdida_potencia_recogida_dB": o.perdida_potencia_recogida_db,
            "perdida_intensidad_en_eje_dB": o.perdida_intensidad_en_eje_db,
            "radio_curvatura_primario_mm": o.radio_curvatura_primario,
            "radio_curvatura_secundario_mm": o.radio_curvatura_secundario,
            "longitud_necesaria_mm": m.longitud_necesaria,
            "margen_longitud_mm": m.margen_longitud,
            "margen_cara_plana_mm": m.margen_cara_plana,
            "margen_esquina_mm": m.margen_esquina,
            "longitud_baffle_primario_mm": m.longitud_baffle_primario,
            "longitud_baffle_secundario_mm": m.longitud_baffle_secundario,
        },
        "foco": (
            {
                "tipo": "virtual",
                "nota": (
                    "En el afocal el foco comun de las dos conicas es VIRTUAL: "
                    "entra colimado y sale colimado, y no hay ningun plano "
                    "donde se forme una imagen real. No se dibuja ningun "
                    "marcador porque ahi no hay nada."
                ),
            }
            if o.es_afocal
            else {
                "tipo": "real",
                "z_local_mm": m.z_foco_real,
                "distancia_focal_trasera_mm": o.distancia_focal_trasera,
                "nota": (
                    "Configuracion focal: el foco real cae detras del vertice "
                    "del primario y por tanto DENTRO de z_payload_banco, que "
                    "solo tiene 7.7 mm de margen en la linea que importa "
                    "(CLAUDE.md 3.7)."
                ),
            }
        ),
    }
