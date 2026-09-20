"""Chequeos de viabilidad, casi todos independientes de la distribucion.

Sirven para decidir la distribucion con numeros por delante, antes de fijarla.
Un chequeo que no se puede hacer por falta de datos sale como 'no comprobable',
nunca como correcto.

La excepcion es 'banco_optico', que si necesita el layout: la pregunta que hace
-- si el colimador y el dicroico caben entre el eje del telescopio y la pared --
solo tiene sentido una vez decidido donde cae ese eje. Se le pasa el layout
cuando lo hay, y sin el sale como no comprobable, igual que cualquier otro
chequeo al que le falte un dato.
"""

from __future__ import annotations

import math

from dataclasses import dataclass, field

import hashlib

import yaml

from ..datamodel import DIR_CAD, RAIZ, Catalogo

OK = "ok"
ATENCION = "atencion"
FALLA = "falla"
NO_COMPROBABLE = "no comprobable"

# Por debajo de esta holgura, decir que una pieza "cabe" no significa nada: el
# espesor de pared supuesto SE DEDUJO de la pieza mas apretada, asi que el
# chequeo se estaria comprobando a si mismo.
HOLGURA_NULA_MM = 0.5

MODELO_DE_PAREDES = (
    "Ademas, la zona util sale de un modelo de CAJA CON PAREDES de espesor "
    "uniforme, y el chasis 6U real es un ARMAZON CON RAILES: el hueco util no "
    "es un prisma, varia con Z y con la cara. Este chequeo no sera concluyente "
    "hasta sustituir el modelo por el STEP del chasis del equipo."
)


@dataclass
class Chequeo:
    id: str
    titulo: str
    estado: str
    mensaje: str
    numeros: dict[str, float] = field(default_factory=dict)
    falta: str | None = None

    @property
    def critico(self) -> bool:
        return self.estado == FALLA


def _seccion_interior(catalogo: Catalogo) -> tuple[float, float, float]:
    return catalogo.dims_interiores


def chequeo_volumen_total(catalogo: Catalogo) -> Chequeo:
    """Suma de volumenes conocidos frente al volumen interior util."""
    interior = catalogo.volumen_interior_mm3
    conocido = 0.0
    sin_dato: list[str] = []
    for componente in catalogo.componentes:
        if componente.categoria == "estructura":
            continue
        if componente.montado_en:  # ya cuenta dentro de su tarjeta
            continue
        if not componente.cuenta_en_presupuesto:  # alternativa en estudio
            continue
        volumen = componente.volumen_mm3()
        if volumen is None:
            sin_dato.append(componente.id)
        else:
            conocido += volumen

    fraccion = conocido / interior
    numeros = {
        "interior_cm3": interior / 1000,
        "ocupado_conocido_cm3": conocido / 1000,
        "libre_si_nada_mas_creciera_cm3": (interior - conocido) / 1000,
        "fraccion_ocupada": fraccion,
        "componentes_sin_volumen": len(sin_dato),
    }
    con_volumen = sum(
        1
        for c in catalogo.componentes
        if c.categoria != "estructura" and not c.montado_en
        and c.cuenta_en_presupuesto and c.volumen_mm3() is not None
    )
    mensaje = (
        f"Los {con_volumen} componentes con "
        f"envolvente conocida ocupan {conocido / 1000:.0f} cm3 de los "
        f"{interior / 1000:.0f} cm3 interiores ({fraccion:.0%}). "
        f"Quedan {len(sin_dato)} componentes sin envolvente: el dato real sera mayor."
    )
    estado = ATENCION if sin_dato else (OK if fraccion < 1 else FALLA)
    return Chequeo(
        id="volumen_total",
        titulo="Volumen total frente a la zona util",
        estado=estado,
        mensaje=mensaje,
        numeros=numeros,
        falta=(
            f"Envolvente de: {', '.join(sin_dato)}" if sin_dato else None
        ),
    )


def chequeo_apertura_telescopio(catalogo: Catalogo) -> Chequeo:
    """La apertura libre de 90 mm frente a la altura interior del 6U.

    Es el chequeo mas restrictivo del satelite: Y = 100 mm exteriores es la
    dimension pequena del 6U y la apertura tiene que caber en su seccion.
    """
    telescopio = catalogo["telescopio_cassegrain"]
    apertura = telescopio.extras.get("apertura_libre")
    if apertura is None or apertura.es_tbd:
        return Chequeo(
            id="apertura_telescopio",
            titulo="Apertura del telescopio frente a la seccion interior",
            estado=NO_COMPROBABLE,
            mensaje="No hay apertura declarada.",
            falta="Apertura libre del telescopio",
        )
    diametro = apertura.escalar()
    assert diametro is not None
    _, interior_y, _ = _seccion_interior(catalogo)
    exterior_y = catalogo.dims_exteriores[1]
    holgura_radial = (interior_y - diametro) / 2

    numeros = {
        "apertura_libre_mm": diametro,
        "altura_exterior_mm": exterior_y,
        "altura_interior_util_mm": interior_y,
        "holgura_por_lado_mm": holgura_radial,
    }

    if holgura_radial < 0:
        estado, mensaje = FALLA, (
            f"La apertura de {diametro:.0f} mm NO cabe en los {interior_y:.0f} mm "
            f"de altura interior: faltan {-holgura_radial * 2:.1f} mm de diametro."
        )
    elif holgura_radial < 5:
        estado, mensaje = ATENCION, (
            f"La apertura de {diametro:.0f} mm deja solo {holgura_radial:.1f} mm por "
            f"lado dentro de los {interior_y:.0f} mm interiores. No hay sitio para "
            f"el barrilete, la celda del espejo ni el ajuste de alineacion. "
            f"El eje optico NO puede ir paralelo a Y, y en cualquier otra "
            f"orientacion la seccion util sigue limitada por Y."
        )
    else:
        estado, mensaje = OK, (
            f"La apertura deja {holgura_radial:.1f} mm por lado."
        )

    return Chequeo(
        id="apertura_telescopio",
        titulo="Apertura del telescopio frente a la seccion interior",
        estado=estado,
        mensaje=mensaje,
        numeros=numeros,
        falta="Diametro exterior del barrilete (la apertura libre no basta)",
    )


def chequeo_contorno_pc104(catalogo: Catalogo) -> Chequeo:
    """El contorno de tarjeta PC104 frente a la seccion interior del 6U.

    Es la comprobacion que mas aprieta al espesor de pared supuesto: el contorno
    de tarjeta es un dato confirmado, y el espesor solo una hipotesis.
    """
    contorno = catalogo.integracion.get("pila_pc104.contorno")
    if contorno is None or contorno.es_tbd:
        return Chequeo(
            id="contorno_pc104",
            titulo="Contorno PC104 frente a la seccion interior",
            estado=NO_COMPROBABLE,
            mensaje="Sin contorno de tarjeta declarado.",
            falta="Contorno de la tarjeta PC104",
        )
    largo, ancho = contorno.valor[0], contorno.valor[1]
    interior_x, interior_y, _ = _seccion_interior(catalogo)
    exterior_y = catalogo.dims_exteriores[1]
    espesor_max = (exterior_y - ancho) / 2
    espesor = catalogo.zona_util["espesor_pared"].escalar()

    numeros = {
        "contorno_largo_mm": largo,
        "contorno_ancho_mm": ancho,
        "interior_X_mm": interior_x,
        "interior_Y_mm": interior_y,
        "espesor_pared_supuesto_mm": espesor if espesor is not None else float("nan"),
        "espesor_pared_maximo_mm": espesor_max,
    }

    if ancho > interior_y or largo > interior_x:
        estado = FALLA
        mensaje = (
            f"La tarjeta de {largo:.2f} x {ancho:.2f} mm NO cabe en la seccion "
            f"interior de {interior_x:.1f} x {interior_y:.1f} mm. El espesor de "
            f"pared supuesto no puede pasar de {espesor_max:.2f} mm."
        )
    else:
        estado = ATENCION
        mensaje = (
            f"La tarjeta de {largo:.2f} x {ancho:.2f} mm cabe en {interior_x:.1f} x "
            f"{interior_y:.1f} mm, pero deja solo {interior_y - ancho:.2f} mm de "
            f"holgura en Y. El espesor de pared no puede pasar de "
            f"{espesor_max:.2f} mm, cota mas holgada que la que fija el iADCS400. "
            + MODELO_DE_PAREDES
        )
    return Chequeo(
        id="contorno_pc104",
        titulo="Contorno PC104 frente a la seccion interior",
        estado=estado,
        mensaje=mensaje,
        numeros=numeros,
        falta="Zona util real del chasis 6U del equipo (STEP o plano con railes)",
    )


def chequeo_seccion_componentes(catalogo: Catalogo) -> Chequeo:
    """Cada pieza con envolvente conocida tiene que caber en la seccion interior.

    Recalcula desde el catalogo el mayor espesor de pared compatible con TODAS
    las piezas. Es la comprobacion que mantiene honesta la hipotesis de espesor:
    al anadir una pieza nueva mas grande, esta cota baja sola.
    """
    exterior = catalogo.dims_exteriores
    interior = _seccion_interior(catalogo)
    espesor = catalogo.zona_util["espesor_pared"].escalar()

    no_caben: list[str] = []
    espesor_maximo = float("inf")
    critico = None

    for componente in catalogo.componentes:
        if componente.categoria == "estructura" or componente.montado_en:
            continue
        if not componente.cuenta_en_presupuesto:
            continue
        # Este chequeo va sobre las cotas de ficha, no sobre la geometria: lo
        # que necesita es un vector de dimensiones. Que ademas haya un STEP
        # conectado no le quita ni le anade nada.
        dims = (
            componente.dimensiones.como_vector()
            if componente.dimensiones.esta_declarada and not componente.dimensiones.es_tbd
            else None
        )
        if dims is None:
            continue
        dx, dy, dz = dims

        if componente.bruto.get("formato") == "pc104":
            # Una tarjeta apilada no se puede tumbar: su altura va por el eje de
            # la pila (Z) y el contorno ocupa la seccion transversal. Se le deja
            # elegir cual de los dos lados del contorno va por Y.
            transversal = sorted((dx, dy))
            hueco = sorted((interior[0], interior[1]))
            exterior_transversal = sorted((exterior[0], exterior[1]))
            cabe = (
                all(d <= h + 1e-9 for d, h in zip(transversal, hueco))
                and dz <= interior[2] + 1e-9
            )
            cota = min(
                (e - d) / 2 for d, e in zip(transversal, exterior_transversal)
            )
        else:
            # El resto puede orientarse libremente: ordenando ambas ternas se
            # comprueba la mejor orientacion posible.
            dims = sorted((dx, dy, dz))
            cabe = all(d <= h + 1e-9 for d, h in zip(dims, sorted(interior)))
            cota = min((e - d) / 2 for d, e in zip(dims, sorted(exterior)))

        if not cabe:
            no_caben.append(componente.id)
        if cota < espesor_maximo:
            espesor_maximo = cota
            critico = componente.id

    numeros = {
        "espesor_supuesto_mm": espesor if espesor is not None else float("nan"),
        "espesor_maximo_compatible_mm": espesor_maximo,
        "interior_X_mm": interior[0],
        "interior_Y_mm": interior[1],
        "interior_Z_mm": interior[2],
        "piezas_que_no_caben": float(len(no_caben)),
    }

    margen = None if espesor is None else espesor_maximo - espesor
    if margen is not None and abs(margen) < 1e-9:
        margen = 0.0  # evita que la coma flotante saque un "-0.00 mm"
    if margen is not None:
        numeros["margen_de_espesor_mm"] = margen

    if no_caben:
        estado = FALLA
        mensaje = (
            f"No caben en la seccion interior: {', '.join(no_caben)}. "
            f"El espesor de pared no puede pasar de {espesor_maximo:.2f} mm, "
            f"y el que manda es '{critico}'."
        )
    elif espesor is not None and espesor > espesor_maximo + 1e-9:
        estado = FALLA
        mensaje = (
            f"El espesor supuesto ({espesor:.2f} mm) es mayor que el maximo "
            f"compatible ({espesor_maximo:.2f} mm), que fija '{critico}'."
        )
    elif margen is not None and margen < HOLGURA_NULA_MM:
        # Caso circular: el espesor supuesto ES la cota que fija '{critico}'.
        # '{critico}' entonces "cabe" con {margen} mm de holgura, que es
        # exactamente lo que se le impuso al elegir el espesor. No es un
        # resultado: es la hipotesis devuelta.
        estado = NO_COMPROBABLE
        mensaje = (
            f"NO CONCLUYENTE. El espesor de pared supuesto ({espesor:.2f} mm) "
            f"coincide con el maximo compatible ({espesor_maximo:.2f} mm): el "
            f"margen es de {margen:.2f} mm. Pero esa cota se DEDUJO de "
            f"'{critico}', asi que decir que '{critico}' cabe con "
            f"{margen:.2f} mm de holgura no comprueba nada; es la hipotesis "
            f"devuelta tal cual. El resto de piezas si tienen holgura real "
            f"frente a esta seccion, pero la pieza que manda no. "
            + MODELO_DE_PAREDES
        )
    else:
        estado = ATENCION
        mensaje = (
            f"Todas las piezas con envolvente conocida caben, y la mas apretada "
            f"('{critico}') deja {margen:.2f} mm de margen sobre el espesor "
            f"supuesto de {espesor:.2f} mm. Las tarjetas PC104 se cuentan sin "
            f"poder tumbarse: su altura va por el eje de la pila. "
            + MODELO_DE_PAREDES
        )
    return Chequeo(
        id="seccion_componentes",
        titulo="Seccion interior frente a todas las piezas",
        estado=estado,
        mensaje=mensaje,
        numeros=numeros,
        falta="Zona util real del chasis 6U del equipo (STEP o plano con railes)",
    )


def chequeo_longitud_moduladores(catalogo: Catalogo) -> list[Chequeo]:
    """Cada modulador necesita un recorrido recto largo dentro de la bandeja."""
    salida: list[Chequeo] = []
    interior = _seccion_interior(catalogo)
    ejes = dict(zip("XYZ", interior))

    for cid in ("mod_intensidad_mxer_ln_10", "mod_fase_mpz_ln_10"):
        componente = catalogo[cid]
        longitud = componente.extras.get("longitud_con_fibras")
        if longitud is None or longitud.es_tbd:
            salida.append(
                Chequeo(
                    id=f"longitud_{cid}",
                    titulo=f"Recorrido recto de {componente.nombre}",
                    estado=NO_COMPROBABLE,
                    mensaje="Sin longitud con fibras declarada.",
                    falta="Longitud total con protectores de fibra",
                )
            )
            continue
        largo = longitud.escalar()
        assert largo is not None
        caben = [eje for eje, disponible in ejes.items() if disponible >= largo]
        numeros = {"longitud_con_fibras_mm": largo}
        numeros.update({f"interior_{eje}_mm": v for eje, v in ejes.items()})
        if not caben:
            estado = FALLA
            mensaje = f"Los {largo:.0f} mm no caben en ningun eje interior."
        else:
            estado = OK if len(caben) > 1 else ATENCION
            mensaje = (
                f"Los {largo:.0f} mm de recorrido recto solo caben orientados "
                f"segun {', '.join(caben)}. Esto ya fija la orientacion de la "
                f"bandeja optica, antes de anadir los bucles de fibra."
            )
        salida.append(
            Chequeo(
                id=f"longitud_{cid}",
                titulo=f"Recorrido recto de {componente.nombre}",
                estado=estado,
                mensaje=mensaje,
                numeros=numeros,
            )
        )
    return salida


def chequeo_pila_pc104(catalogo: Catalogo) -> Chequeo:
    """Longitud de la pila PC104. Sin el paso de apilamiento solo hay una cota.

    La altura de cada tarjeta se mide sobre LO QUE SE DIBUJA, no sobre la ficha.
    Las fichas de AAC dan la altura "from top PCB to lowest component" y no
    incluyen el conector PC104 pasante, que baja 12.45 mm por debajo de la
    tarjeta; el STEP de fabricante si lo trae. Si la pila se reserva por la
    ficha y se dibuja por el STEP, los dos numeros dejan de hablar de lo mismo,
    y la diferencia no es pequena: 259 mm contra 305 mm.
    """
    from .. import parts

    paso = catalogo.integracion.get("pila_pc104.paso_apilamiento")
    tarjetas: list[tuple[str, float, int]] = []
    sin_altura: list[str] = []

    for componente in catalogo.componentes:
        dims = componente.dimensiones
        if not componente.cuenta_en_presupuesto:
            continue
        if componente.montado_en or componente.categoria == "estructura":
            continue
        if componente.bruto.get("formato") != "pc104":
            continue
        n = componente.n_unidades
        caja = parts.caja_local(componente) if componente.modelable else None
        if caja is None or n is None:
            sin_altura.append(componente.id)
            continue
        altura = caja.dims[2]
        tarjetas.append((componente.id, altura, n))

    suma = sum(altura * n for _, altura, n in tarjetas)
    n_tarjetas = sum(n for _, _, n in tarjetas)
    _, _, interior_z = _seccion_interior(catalogo)

    numeros = {
        "tarjetas_con_altura": float(n_tarjetas),
        "suma_alturas_mm": suma,
        "interior_Z_mm": interior_z,
        "tarjetas_sin_altura": float(len(sin_altura)),
    }

    modelado = catalogo.integracion.get("pila_pc104.paso_apilamiento_modelado")
    if (paso is None or paso.es_tbd) and modelado is not None and not modelado.es_tbd:
        paso_mm = modelado.escalar()
        assert paso_mm is not None
        posiciones = sum(math.ceil(altura / paso_mm) * n for _, altura, n in tarjetas)
        total = posiciones * paso_mm
        numeros["paso_modelado_mm"] = paso_mm
        numeros["posiciones_de_separador"] = float(posiciones)
        numeros["longitud_modelada_mm"] = total
        reserva = len(sin_altura) * paso_mm
        numeros["reserva_tarjetas_sin_altura_mm"] = reserva
        estado = OK if total + reserva <= interior_z else FALLA
        return Chequeo(
            id="pila_pc104",
            titulo="Longitud de la pila PC104",
            estado=estado,
            mensaje=(
                f"Con el paso estandar PC/104 de {paso_mm:.2f} mm, las "
                f"{n_tarjetas} tarjetas de altura conocida ocupan {posiciones} "
                f"posiciones de separador, o sea {total:.0f} mm. Reservando una "
                f"posicion por cada una de las {len(sin_altura)} tarjetas sin "
                f"altura ({reserva:.0f} mm mas), la pila suma "
                f"{total + reserva:.0f} mm frente a {interior_z:.0f} mm "
                f"interiores. El paso REAL del chasis sigue siendo TBD: este "
                f"numero es una estimacion con el paso de la norma, no el del "
                f"chasis elegido."
            ),
            numeros=numeros,
            falta="Paso de apilamiento PC104 del chasis elegido",
        )

    if paso is None or paso.es_tbd:
        return Chequeo(
            id="pila_pc104",
            titulo="Longitud de la pila PC104",
            estado=NO_COMPROBABLE,
            mensaje=(
                f"Las {n_tarjetas} tarjetas con altura conocida suman {suma:.0f} mm, "
                f"pero eso es una COTA INFERIOR: las fichas AAC dan la altura "
                f"'from top PCB to lowest component', no el paso entre tarjetas. "
                f"Faltan ademas {len(sin_altura)} tarjetas sin altura "
                f"({', '.join(sin_altura) or 'ninguna'})."
            ),
            numeros=numeros,
            falta="Paso de apilamiento PC104 del chasis elegido",
        )

    paso_mm = paso.escalar()
    assert paso_mm is not None
    total = sum(max(altura, paso_mm) * n for _, altura, n in tarjetas)
    numeros["longitud_estimada_mm"] = total
    estado = OK if total <= interior_z else FALLA
    return Chequeo(
        id="pila_pc104",
        titulo="Longitud de la pila PC104",
        estado=estado,
        mensaje=f"La pila mide {total:.0f} mm frente a {interior_z:.0f} mm interiores.",
        numeros=numeros,
    )


def chequeo_bucles_fibra(catalogo: Catalogo) -> Chequeo:
    radio = catalogo.integracion.get("fibra.radio_minimo_curvatura")
    if radio is None or radio.es_tbd:
        return Chequeo(
            id="bucles_fibra",
            titulo="Radio minimo de curvatura de la fibra",
            estado=NO_COMPROBABLE,
            mensaje=(
                "Sin radio minimo de curvatura no se puede dimensionar la bandeja "
                "optica ni comprobar ningun bucle. Es el parametro que mas area "
                "consume de toda la bandeja."
            ),
            falta="Radio minimo de curvatura de la fibra elegida",
        )
    r = radio.escalar()
    assert r is not None
    return Chequeo(
        id="bucles_fibra",
        titulo="Radio minimo de curvatura de la fibra",
        estado=OK,
        mensaje=f"Radio minimo {r:.0f} mm. Cada bucle completo ocupa {2 * r:.0f} mm.",
        numeros={"radio_minimo_mm": r, "diametro_bucle_mm": 2 * r},
    )


def chequeo_masa(catalogo: Catalogo) -> Chequeo:
    limite = catalogo.envolvente["masa_maxima"].escalar()
    assert limite is not None
    conocida = 0.0
    sin_dato: list[str] = []
    for componente in catalogo.componentes:
        if not componente.cuenta_en_presupuesto:
            continue
        masa = componente.masa_total_g()
        if masa is None:
            sin_dato.append(componente.id)
        else:
            conocida += masa
    numeros = {
        "masa_conocida_g": conocida,
        "limite_g": limite,
        "margen_g": limite - conocida,
        "componentes_sin_masa": float(len(sin_dato)),
    }
    return Chequeo(
        id="masa",
        titulo="Presupuesto de masa",
        estado=ATENCION if sin_dato else (OK if conocida <= limite else FALLA),
        mensaje=(
            f"Masa conocida {conocida:.0f} g de un limite de {limite:.0f} g "
            f"(CDS 14.1). Faltan {len(sin_dato)} componentes por pesar, "
            f"incluido el chasis y el telescopio, que son de los mas pesados."
        ),
        numeros=numeros,
        falta=f"Masa de: {', '.join(sin_dato)}" if sin_dato else None,
    )


def chequeo_banco_optico(catalogo: Catalogo, layout=None) -> Chequeo:
    """Cabe la cadena de espacio libre entre el eje del telescopio y la pared.

    El FSM dobla el haz de X a Z, asi que tiene que estar SOBRE el eje optico
    del telescopio: no se puede mover. Eso deja al colimador y al dicroico en
    linea con el, hacia +X, y el sitio que tienen es el que va del eje a la
    pared de la columna de payload. Es el punto mas apretado del payload y el
    que no se ve mirando volumenes: sobra hueco en el banco, pero no EN ESA
    LINEA.

    Si el margen sale negativo la salida no es apretar las piezas: es alargar
    el banco a costa de la bandeja o de la longitud reservada al telescopio.
    """
    titulo = "Cadena de espacio libre entre el eje del telescopio y la pared"
    if layout is None:
        return Chequeo(
            id="banco_optico", titulo=titulo, estado=NO_COMPROBABLE,
            mensaje="Sin layout no se sabe donde cae el eje optico.",
            falta="Distribucion (data/layout.yaml)",
        )
    zonas = {z.id: z for z in layout.zonas}
    banco = zonas.get("z_payload_banco")
    telescopio = zonas.get("z_payload_telescopio")
    if banco is None or telescopio is None:
        return Chequeo(
            id="banco_optico", titulo=titulo, estado=NO_COMPROBABLE,
            mensaje="El layout no declara las zonas del banco y del telescopio.",
            falta="Zonas z_payload_banco y z_payload_telescopio",
        )

    from .. import parts

    eje_x = telescopio.caja.centro[0]
    disponible = banco.caja.xmax - eje_x

    piezas = ("fsm", "dicroico", "colimador")
    necesario = 0.0
    sin_envolvente: list[str] = []
    detalle: dict[str, float] = {}
    for cid in piezas:
        if not catalogo.existe(cid):
            continue
        componente = catalogo[cid]
        caja = parts.caja_local(componente) if componente.modelable else None
        if caja is None:
            sin_envolvente.append(cid)
            continue
        # El FSM esta centrado en el eje, asi que solo cuenta su mitad. Y va a
        # 45 grados, que es lo que lo hace ancho: su lado largo se proyecta
        # sobre X.
        if cid == "fsm":
            ancho = math.hypot(caja.dims[0], caja.dims[2]) / 2
        else:
            ancho = caja.dims[0]
        detalle[cid] = ancho
        necesario += ancho

    if sin_envolvente:
        return Chequeo(
            id="banco_optico", titulo=titulo, estado=NO_COMPROBABLE,
            mensaje=(
                f"Sin envolvente: {', '.join(sin_envolvente)}. No se puede "
                f"sumar la linea."
            ),
            numeros={"disponible_mm": disponible},
            falta=f"Envolvente de {', '.join(sin_envolvente)}",
        )

    margen = disponible - necesario
    numeros = {**detalle, "necesario_mm": necesario, "disponible_mm": disponible,
               "margen_mm": margen}
    comun = (
        f"El FSM va sobre el eje optico del telescopio (X = {eje_x:+.2f} mm) "
        f"porque es el que dobla el haz de X a Z. Del eje a la pared +X de la "
        f"columna hay {disponible:.1f} mm, y la media anchura del FSM mas el "
        f"dicroico mas el colimador suman {necesario:.1f} mm, sin contar "
        f"holguras de montaje."
    )
    if margen < 0:
        return Chequeo(
            id="banco_optico", titulo=titulo, estado=FALLA,
            mensaje=(
                comun + f" NO CABE por {abs(margen):.1f} mm. La salida no es "
                f"apretar las piezas: es alargar el banco a costa de la "
                f"bandeja o de la longitud reservada al telescopio."
            ),
            numeros=numeros,
        )
    if margen < HOLGURA_NULA_MM * 10:
        return Chequeo(
            id="banco_optico", titulo=titulo, estado=ATENCION,
            mensaje=(
                comun + f" Quedan {margen:.1f} mm, que no dan para holguras de "
                f"montaje ni para que ninguna de las dos envolventes crezca. "
                f"Las dos son SUPUESTAS; cualquier pieza real mayor rompe la "
                f"linea."
            ),
            numeros=numeros,
        )
    return Chequeo(
        id="banco_optico", titulo=titulo, estado=OK,
        mensaje=comun + f" Quedan {margen:.1f} mm de margen.",
        numeros=numeros,
    )


def chequeo_step_de_fabricante(catalogo: Catalogo) -> Chequeo:
    """Los STEP de fabricante presentes frente a cad/vendor/MANIFEST.yaml.

    Los CAD de fabricante no se versionan: el repositorio es publico y sus
    condiciones de uso estan sin revisar. Lo que se versiona es la huella. Este
    chequeo dice si lo que hay en disco es lo mismo que se uso al fijar el
    layout.

    **No falla porque falte un fichero.** Quien clone el repositorio sin ellos
    tiene que poder ejecutarlo todo con las cajas envolventes. Lo que si es un
    fallo es tener un fichero con la huella cambiada: entonces el modelo se ha
    dibujado con una geometria que no es la que el manifiesto declara.
    """
    manifiesto = DIR_CAD / "vendor" / "MANIFEST.yaml"
    if not manifiesto.exists():
        return Chequeo(
            id="step_de_fabricante",
            titulo="STEP de fabricante frente al manifiesto",
            estado=NO_COMPROBABLE,
            mensaje="No hay cad/vendor/MANIFEST.yaml.",
            falta="Manifiesto de los CAD de fabricante",
        )
    bruto = yaml.safe_load(manifiesto.read_text(encoding="utf-8")) or {}
    declarados = bruto.get("ficheros") or []

    presentes: list[str] = []
    ausentes: list[str] = []
    corruptos: list[str] = []
    for entrada in declarados:
        ruta = DIR_CAD / "vendor" / entrada["ruta"]
        if not ruta.exists():
            ausentes.append(entrada["ruta"])
            continue
        huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
        if huella != entrada.get("sha256"):
            corruptos.append(f"{entrada['ruta']} (sha256 {huella[:12]}...)")
        else:
            presentes.append(entrada["ruta"])

    # Ficheros en disco que el manifiesto no menciona: no se sabe de donde
    # salieron ni si se pueden redistribuir.
    conocidos = {e["ruta"] for e in declarados}
    vendor = DIR_CAD / "vendor"
    sueltos = sorted(
        str(p.relative_to(vendor))
        for p in vendor.rglob("*")
        if p.suffix.lower() in (".step", ".stp") and str(p.relative_to(vendor)) not in conocidos
    )

    # Un STEP conectado a un componente y que no esta en disco: el componente
    # se dibuja con su caja, que es el comportamiento correcto, pero conviene
    # saberlo.
    conectados_sin_fichero = [
        c.id
        for c in catalogo.componentes
        if c.step is not None and not (RAIZ / c.step.ruta).exists()
    ]

    # Piezas que esperan un STEP que todavia no ha llegado. Se dibujan con su
    # envolvente aproximada, y el dia que el fichero aparezca en la ruta que el
    # catalogo declara se dibujan con el sin tocar nada. Lo util del chequeo es
    # decir EXACTAMENTE que fichero falta y en que ruta va, para poder pedirlo.
    esperando = [
        (c.id, c.step_esperado)
        for c in catalogo.componentes
        if c.step_esperado is not None
        and not (RAIZ / c.step_esperado.ruta).exists()
    ]
    aparecidos = [
        c.id
        for c in catalogo.componentes
        if c.step_esperado is not None and (RAIZ / c.step_esperado.ruta).exists()
    ]

    numeros = {
        "declarados": float(len(declarados)),
        "presentes": float(len(presentes)),
        "ausentes": float(len(ausentes)),
        "huella_distinta": float(len(corruptos)),
        "sin_declarar": float(len(sueltos)),
        "esperando_step": float(len(esperando)),
        "aparecidos_sin_verificar": float(len(aparecidos)),
    }

    partes = [
        f"{len(presentes)} de {len(declarados)} CAD de fabricante presentes "
        f"y con la huella del manifiesto."
    ]
    if ausentes:
        partes.append(
            f"No estan en disco: {', '.join(ausentes)}. Se bajan de la carpeta "
            f"de Drive del manifiesto; sin ellos el modelo usa cajas envolventes."
        )
    if corruptos:
        partes.append(
            f"HUELLA DISTINTA a la declarada: {', '.join(corruptos)}. El modelo "
            f"no se ha dibujado con el fichero que dice el manifiesto."
        )
    if sueltos:
        partes.append(
            f"En cad/vendor/ sin declarar en el manifiesto: {', '.join(sueltos)}."
        )
    if conectados_sin_fichero:
        partes.append(
            f"Componentes con STEP conectado pero sin fichero: "
            f"{', '.join(conectados_sin_fichero)}."
        )
    if esperando:
        partes.append(
            f"{len(esperando)} piezas esperan un STEP que aun no ha llegado; "
            f"mientras tanto se dibujan con su envolvente aproximada. Dejar el "
            f"fichero en la ruta indicada basta para que el modelo lo use: "
            + "; ".join(
                f"{cid} -> {esp.ruta} (a {esp.pedir_a})" for cid, esp in esperando
            )
            + "."
        )
    if aparecidos:
        partes.append(
            f"STEP aparecidos en su ruta y conectados automaticamente, como "
            f"REFERENCIA hasta verificar su part number: {', '.join(aparecidos)}. "
            f"Al verificarlos, sustituir 'forma.step_esperado' por 'forma.step' "
            f"con estado 'confirmado' y anotar la huella en el manifiesto."
        )

    if corruptos:
        estado = FALLA
    elif ausentes or sueltos or esperando or aparecidos:
        estado = ATENCION
    else:
        estado = OK

    return Chequeo(
        id="step_de_fabricante",
        titulo="STEP de fabricante frente al manifiesto",
        estado=estado,
        mensaje=" ".join(partes),
        numeros=numeros,
        falta=_falta_de_step(ausentes, esperando, aparecidos),
    )


def _falta_de_step(ausentes, esperando, aparecidos) -> str | None:
    trozos = []
    if ausentes:
        trozos.append(f"Descargar de Drive: {', '.join(ausentes)}")
    if esperando:
        trozos.append(
            "STEP por recibir: "
            + ", ".join(f"{cid} (a {esp.pedir_a})" for cid, esp in esperando)
        )
    if aparecidos:
        trozos.append(
            "Verificar el part number de: " + ", ".join(aparecidos)
        )
    return ". ".join(trozos) if trozos else None


def todos(catalogo: Catalogo, layout=None) -> list[Chequeo]:
    salida = [
        chequeo_volumen_total(catalogo),
        chequeo_apertura_telescopio(catalogo),
        chequeo_contorno_pc104(catalogo),
        chequeo_seccion_componentes(catalogo),
    ]
    salida += chequeo_longitud_moduladores(catalogo)
    salida += [
        chequeo_pila_pc104(catalogo),
        chequeo_banco_optico(catalogo, layout),
        chequeo_bucles_fibra(catalogo),
        chequeo_masa(catalogo),
        chequeo_step_de_fabricante(catalogo),
    ]
    return salida
