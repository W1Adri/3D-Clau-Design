"""El modelo parametrico del telescopio: derivacion, envolvente y estado.

Igual que test_interferencias.py y test_formas.py, la mayor parte de esto se
comprueba con un catalogo INVENTADO. El del repositorio cambia -- manana llega
el STEP de Aperture Optical Sciences y el telescopio deja de dibujarse asi --,
y lo que tiene que seguir comprobado es el mecanismo, no la cifra de hoy.

Lo que si se comprueba contra el catalogo de verdad es lo que no puede cambiar
sin que alguien lo decida: que el telescopio sigue siendo SUPUESTO, que no suma
en los presupuestos y que su envolvente sigue siendo la que el layout le
reserva.
"""

from __future__ import annotations

import math

import pytest

from clau3d import parts
from clau3d.analysis import budgets, fit
from clau3d.datamodel import (
    PARAMETROS_CASSEGRAIN,
    SUPUESTO,
    TBD,
    Catalogo,
    ErrorDeDatos,
    Magnitud,
    _componente,
    validar,
)
from clau3d.optica import cassegrain, parametros


# ---------------------------------------------------------------- utilidades
def _sup(valor, unidad=None):
    bloque = {
        "valor": valor, "estado": SUPUESTO, "fuente": "geometria de prueba",
        "falta": "la de verdad", "pedir_a": "nadie",
    }
    if unidad:
        bloque["unidad"] = unidad
    return bloque


def _tbd(unidad=None):
    bloque = {"valor": None, "estado": TBD, "falta": "algo", "pedir_a": "alguien"}
    if unidad:
        bloque["unidad"] = unidad
    return bloque


# Un telescopio de mentira, con numeros redondos para que las derivaciones se
# puedan comprobar a mano: apertura 100, haz 10 -> M = 10 exacto.
OPTICA = {
    "configuracion": {
        "valor": "afocal_mersenne", "estado": "decision", "fuente": "prueba",
    },
    "focal_primario": _sup(200.0, "mm"),
    "conica_primario": _sup(-1.0),
    "conica_secundario": _sup(-1.0),
    "diametro_haz_comprimido": _tbd("mm"),
    "distancia_focal_trasera": _sup(40.0, "mm"),
    "margen_secundario": _sup(1.5),
    "margen_agujero_primario": _sup(4.0, "mm"),
    "margen_substrato_primario": _sup(1.0, "mm"),
    "estabilidad_despace_primario_secundario": _tbd("um"),
    "seccion_barrilete": _sup([110.0, 110.0], "mm"),
    "espesor_pared_barrilete": _sup(2.0, "mm"),
    "espesor_mamparo": _sup(3.0, "mm"),
    "lado_larguero_esquina": _sup(10.0, "mm"),
    "brida_interfaz_fsm": _sup([40.0, 40.0], "mm"),
    "espesor_brida": _sup(3.0, "mm"),
    "margen_agujero_entrada": _sup(2.0, "mm"),
    "espesor_espejo_primario": _sup(8.0, "mm"),
    "espesor_espejo_secundario": _sup(4.0, "mm"),
    "altura_celda": _sup(3.0, "mm"),
    "flexures": _sup(3),
    "radio_circulo_flexures": _sup(45.0, "mm"),
    "angulo_primer_flexure": _sup(45.0, "deg"),
    "seccion_flexure": _sup([6.0, 6.0], "mm"),
    "margen_buje_secundario": _sup(3.0, "mm"),
    "tornillos_colimacion": _sup(3),
    "diametro_tornillo_colimacion": _sup(3.0, "mm"),
    "vanes": _sup(4),
    "espesor_vane": _sup(0.8, "mm"),
    "ancho_vane": _sup(6.0, "mm"),
    "holgura_baffle": _sup(1.0, "mm"),
    "espesor_baffle": _sup(0.8, "mm"),
    "diafragmas_internos": _sup(3),
    "espesor_diafragma": _sup(1.0, "mm"),
    "angulo_exclusion_solar": _tbd("deg"),
    "angulo_exclusion_solar_modelado": _sup(30.0, "deg"),
}

DIMENSIONES = _sup([110.0, 110.0, 220.0], "mm")


def _telescopio(**cambios) -> dict:
    optica = {**OPTICA, **cambios.pop("optica", {})}
    return {
        "id": "telescopio_de_prueba",
        "nombre": "telescopio de prueba",
        "categoria": "payload_optico",
        "subsistema": "terminal_optico",
        "forma": {"tipo": "cassegrain", "dimensiones": cambios.pop("dimensiones", DIMENSIONES)},
        "apertura_libre": _sup(100.0, "mm"),
        "optica": optica,
        "masa": _tbd("g"),
        **cambios,
    }


def _fsm(diametro_espejo: float | None = 5.0) -> dict:
    espejo = (
        {"valor": diametro_espejo, "unidad": "mm", "estado": "referencia",
         "fuente": "ficha de prueba"}
        if diametro_espejo is not None
        else _tbd("mm")
    )
    return {
        "id": "fsm", "nombre": "fsm", "categoria": "payload_optico",
        "subsistema": "terminal_optico",
        "forma": {"tipo": "caja", "dimensiones": _sup([30.0, 15.0, 2.0], "mm")},
        "diametro_espejo": espejo,
        "masa": _tbd("g"),
    }


def _catalogo(*componentes: dict, haz_modelado: float | None = 10.0) -> Catalogo:
    integracion = {}
    if haz_modelado is not None:
        integracion["optica.diametro_haz_modelado"] = Magnitud(
            nombre="integracion.optica.diametro_haz_modelado",
            valor=haz_modelado, unidad="mm", estado=SUPUESTO,
            fuente="supuesto de prueba", falta="el real", pedir_a="nadie",
        )
    return Catalogo(
        meta={}, norma={},
        envolvente={
            "masa_maxima": Magnitud(
                nombre="masa_maxima", valor=12000, unidad="g",
                estado="confirmado", fuente="CDS Rev 14.1, Tabla 1",
            )
        },
        zona_util={}, integracion=integracion,
        componentes=[_componente(c) for c in componentes],
        conexiones={},
    )


# ------------------------------------------------------- el tipo de forma
def test_el_tipo_cassegrain_valida():
    assert validar(_catalogo(_telescopio())) == []


def test_un_bloque_optica_incompleto_no_pasa():
    """Sin su optica un cassegrain es un nombre, no una pieza."""
    optica = {k: v for k, v in OPTICA.items() if k != "focal_primario"}
    problemas = validar(
        _catalogo(_telescopio(optica={"focal_primario": None}) | {"optica": optica})
    )
    assert problemas, "un cassegrain sin focal_primario deberia fallar"
    assert any("focal_primario" in p for p in problemas), problemas


def test_todos_los_parametros_declarados_son_exigidos():
    """Cada parametro de la lista, quitado de uno en uno, tumba la validacion."""
    for nombre in PARAMETROS_CASSEGRAIN:
        optica = {k: v for k, v in OPTICA.items() if k != nombre}
        bruto = _telescopio()
        bruto["optica"] = optica
        problemas = validar(_catalogo(bruto))
        assert any(nombre in p for p in problemas), (
            f"quitar '{nombre}' tendria que fallar la validacion"
        )


def test_un_cassegrain_sin_dimensiones_no_pasa():
    problemas = validar(_catalogo(_telescopio(dimensiones=_tbd("mm"))))
    assert any("dimensiones" in p for p in problemas), problemas


# ------------------------------------------------------------- derivacion
def test_las_magnitudes_derivadas_salen_de_los_parametros():
    """M, f2, la separacion y la obstruccion NO estan escritas en ningun sitio."""
    catalogo = _catalogo(_telescopio())
    o = parametros.derivar(catalogo["telescopio_de_prueba"], catalogo)

    # apertura 100 / haz 10
    assert o.magnificacion == pytest.approx(10.0)
    # f2 = f1 / M
    assert o.focal_secundario == pytest.approx(20.0)
    # d = f1 - |f2|, que es lo que hace confocal al sistema
    assert o.separacion == pytest.approx(180.0)
    # D2 = haz * margen
    assert o.diametro_secundario == pytest.approx(15.0)
    assert o.diametro_agujero_primario == pytest.approx(19.0)
    assert o.obstruccion_lineal == pytest.approx(0.15)
    # Las DOS perdidas de la obstruccion, que no son la misma con un factor:
    # son dos magnitudes distintas y las dos son de potencia.
    assert o.perdida_potencia_recogida_db == pytest.approx(
        -10 * math.log10(1 - 0.15 ** 2)
    )
    assert o.perdida_intensidad_en_eje_db == pytest.approx(
        -20 * math.log10(1 - 0.15 ** 2)
    )


def test_cambiar_el_haz_cambia_todas_las_derivadas():
    """Si alguna estuviera escrita a mano, esta comprobacion la pillaria."""
    flojo = _catalogo(_telescopio(), haz_modelado=10.0)
    apretado = _catalogo(_telescopio(), haz_modelado=5.0)
    a = parametros.derivar(flojo["telescopio_de_prueba"], flojo)
    b = parametros.derivar(apretado["telescopio_de_prueba"], apretado)
    assert b.magnificacion == pytest.approx(2 * a.magnificacion)
    assert b.focal_secundario == pytest.approx(a.focal_secundario / 2)
    assert b.separacion > a.separacion
    assert b.diametro_secundario == pytest.approx(a.diametro_secundario / 2)


def test_el_haz_con_el_que_se_dibuja_sale_del_supuesto_global():
    """Mientras el haz sea TBD, se usa el mismo numero que los keep-outs del banco."""
    catalogo = _catalogo(_telescopio(), haz_modelado=7.0)
    o = parametros.derivar(catalogo["telescopio_de_prueba"], catalogo)
    assert o.diametro_haz == pytest.approx(7.0)
    assert o.haz_es_supuesto


def test_la_magnificacion_angular_comprime_por_m():
    """theta_salida = theta_FSM / M: es lo que decide el recorrido del FSM."""
    catalogo = _catalogo(_telescopio())
    o = parametros.derivar(catalogo["telescopio_de_prueba"], catalogo)
    assert o.magnificacion_angular(500.0) == pytest.approx(50.0)
    assert o.angulo_en_el_fsm(50.0) == pytest.approx(500.0)


def test_la_sagita_de_una_parabola_es_r2_entre_2r():
    catalogo = _catalogo(_telescopio())
    o = parametros.derivar(catalogo["telescopio_de_prueba"], catalogo)
    # K = -1 -> z = r^2 / (2R), con R = 2 f1 = 400
    assert o.sagita_primario(50.0) == pytest.approx(50.0 ** 2 / (2 * 400.0))


def test_una_seccion_de_barrilete_que_no_es_cuadrada_se_rechaza():
    bruto = _telescopio()
    bruto["optica"] = {**OPTICA, "seccion_barrilete": _sup([110.0, 90.0], "mm")}
    catalogo = _catalogo(bruto)
    with pytest.raises(ErrorDeDatos, match="cuadrada"):
        parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)


def test_la_seccion_tiene_que_coincidir_con_la_envolvente_declarada():
    """Lo que se reserva se mide sobre lo que se dibuja."""
    bruto = _telescopio()
    bruto["optica"] = {**OPTICA, "seccion_barrilete": _sup([100.0, 100.0], "mm")}
    catalogo = _catalogo(bruto)
    with pytest.raises(ErrorDeDatos, match="misma cota"):
        parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)


def test_la_longitud_reservada_tiene_que_coincidir_con_la_envolvente():
    """El mismo motivo que la seccion, y la misma trampa, en el otro eje.

    'longitud_reservada' es con lo que el layout reparte Z entre telescopio,
    banco y bandeja; la tercera cota de 'forma.dimensiones' es lo que se dibuja
    y lo que miden el volumen y las interferencias. Son el mismo numero escrito
    dos veces. Se vio al subir el telescopio de 200 a 227 mm el 2026-09-21: sin
    esta comprobacion, cambiar uno y olvidar el otro deja el layout repartiendo
    227 y el analisis midiendo 200, y nada se queja.
    """
    bruto = _telescopio(longitud_reservada=_sup(300.0, "mm"))
    catalogo = _catalogo(bruto)
    with pytest.raises(ErrorDeDatos, match="longitud_reservada"):
        parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)


def test_sin_longitud_reservada_la_envolvente_manda():
    """Un telescopio que no reserva nada no es un error: es el caso de antes.

    Lo que no puede pasar es que las dos existan y digan cosas distintas.
    """
    catalogo = _catalogo(_telescopio())
    m = parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)
    assert m.longitud == 220.0


def test_la_longitud_reservada_que_coincide_se_acepta():
    bruto = _telescopio(longitud_reservada=_sup(220.0, "mm"))
    catalogo = _catalogo(bruto)
    m = parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)
    assert m.longitud == 220.0


def test_el_catalogo_de_verdad_no_tiene_las_dos_longitudes_divergidas(catalogo):
    """Y esto sobre el catalogo real, que es donde importa."""
    telescopio = catalogo["telescopio_cassegrain"]
    reservada = telescopio.extras["longitud_reservada"].escalar()
    dibujada = telescopio.dimensiones.como_vector()[2]
    assert reservada == dibujada, (reservada, dibujada)


def test_un_haz_mas_fino_alarga_el_telescopio():
    """Lo contrario de lo que uno esperaria, y es lo que decide el reparto.

    Bajar el haz sube la magnificacion (M = apertura / haz) y con ella la
    separacion entre vertices, f1 (1 - 1/M). Por eso apretar el haz a 7 mm para
    que las opticas de Ø12.7 del banco valgan obligo a subir la reserva del
    telescopio: con 200 mm ya no cabia.
    """
    gordo = _catalogo(_telescopio(), haz_modelado=10.0)
    fino = _catalogo(_telescopio(), haz_modelado=5.0)
    sep_gordo = parametros.mecanica(
        gordo["telescopio_de_prueba"], gordo
    ).optica.separacion
    sep_fino = parametros.mecanica(
        fino["telescopio_de_prueba"], fino
    ).optica.separacion
    assert sep_fino > sep_gordo


def test_el_peor_caso_de_haz_se_deriva_del_espejo_del_fsm():
    """No se escribe: es D / raiz(2), el mismo numero que usa 'haz_vs_fsm'."""
    catalogo = _catalogo(_telescopio(), _fsm(5.0), haz_modelado=10.0)
    assert fit._haz_maximo_del_fsm(catalogo) == pytest.approx(5.0 / math.sqrt(2.0))

    m = parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)
    peor = fit._margen_con_otro_haz(m, fit._haz_maximo_del_fsm(catalogo))
    assert peor is not None
    haz, separacion, margen = peor
    # Un haz mas fino pide mas tubo, asi que su margen es MENOR.
    assert separacion > m.optica.separacion
    assert margen < m.margen_longitud


def test_sin_fsm_no_hay_peor_caso_que_informar():
    """Un numero que no se puede derivar no se inventa."""
    catalogo = _catalogo(_telescopio(), haz_modelado=10.0)
    assert fit._haz_maximo_del_fsm(catalogo) is None
    m = parametros.mecanica(catalogo["telescopio_de_prueba"], catalogo)
    assert fit._margen_con_otro_haz(m, None) is None


def test_el_chequeo_de_longitud_del_catalogo_real_trae_el_peor_caso(catalogo):
    chequeo = fit.chequeo_longitud_telescopio(catalogo)
    assert "peor_caso_haz_mm" in chequeo.numeros
    assert (
        chequeo.numeros["peor_caso_margen_mm"] < chequeo.numeros["margen_mm"]
    )


# -------------------------------------------------------------- geometria
def test_el_solido_no_se_sale_de_la_envolvente_declarada():
    catalogo = _catalogo(_telescopio())
    componente = catalogo["telescopio_de_prueba"]
    caja = cassegrain.solido(componente, catalogo).BoundingBox()
    assert (caja.xlen, caja.ylen, caja.zlen) == pytest.approx((110.0, 110.0, 220.0))


def test_una_optica_que_no_cabe_aborta_en_vez_de_encogerse():
    """No se aprieta: una pieza que no cabe se reporta, no se recorta."""
    bruto = _telescopio()
    # Focal mucho mas larga: la separacion entre vertices se pasa del tubo.
    bruto["optica"] = {**OPTICA, "focal_primario": _sup(400.0, "mm")}
    catalogo = _catalogo(bruto)
    with pytest.raises(ErrorDeDatos, match="no cabe"):
        cassegrain.solido(catalogo["telescopio_de_prueba"], catalogo)


def test_la_envolvente_es_maciza_y_el_detalle_no():
    """El interior del tubo no es hueco aprovechable; el analisis usa el prisma."""
    catalogo = _catalogo(_telescopio())
    componente = catalogo["telescopio_de_prueba"]
    detalle = cassegrain.solido(componente, catalogo)
    envolvente = cassegrain.envolvente(componente)
    assert envolvente.Volume() == pytest.approx(110.0 * 110.0 * 220.0)
    assert detalle.Volume() < envolvente.Volume() / 2


def test_parts_devuelve_el_detalle_y_la_envolvente_por_separado():
    catalogo = _catalogo(_telescopio())
    componente = catalogo["telescopio_de_prueba"]
    detalle = parts.solido(componente, catalogo).Volume()
    reservado = parts.solido_envolvente(componente, catalogo).Volume()
    assert detalle < reservado


def test_todas_las_piezas_tienen_nombre_propio_y_son_unicos():
    catalogo = _catalogo(_telescopio())
    nombres = [n for n, _ in cassegrain.piezas(catalogo["telescopio_de_prueba"], catalogo)]
    assert len(nombres) == len(set(nombres))
    for esperado in (
        "mamparo_trasero", "mamparo_frontal", "brida_interfaz_fsm", "barrilete",
        "espejo_primario", "espejo_secundario", "buje_secundario",
        "baffle_principal", "baffle_primario", "baffle_secundario",
        "vane_1", "flexure_1", "larguero_esquina_1", "diafragma_1",
        "tornillo_colimacion_1",
    ):
        assert esperado in nombres, nombres


def test_hay_tantos_vanes_flexures_y_diafragmas_como_dice_el_catalogo():
    catalogo = _catalogo(_telescopio())
    nombres = [n for n, _ in cassegrain.piezas(catalogo["telescopio_de_prueba"], catalogo)]
    assert sum(n.startswith("vane_") for n in nombres) == 4
    assert sum(n.startswith("flexure_") for n in nombres) == 3
    assert sum(n.startswith("diafragma_") for n in nombres) == 3


def test_el_afocal_no_dibuja_ningun_foco():
    """El foco comun de las dos conicas es VIRTUAL: ahi no hay nada que dibujar."""
    catalogo = _catalogo(_telescopio())
    nombres = [n for n, _ in cassegrain.piezas(catalogo["telescopio_de_prueba"], catalogo)]
    assert "foco_real" not in nombres
    assert parametros.resumen(catalogo["telescopio_de_prueba"], catalogo)["foco"][
        "tipo"
    ] == "virtual"


def test_el_focal_clasico_si_dibuja_el_foco_real_y_el_chequeo_avisa():
    bruto = _telescopio()
    bruto["optica"] = {
        **OPTICA,
        "configuracion": {
            "valor": "focal_clasico", "estado": "decision", "fuente": "prueba",
        },
    }
    catalogo = _catalogo(bruto, haz_modelado=10.0)
    componente = catalogo["telescopio_de_prueba"]
    nombres = [n for n, _ in cassegrain.piezas(componente, catalogo)]
    assert "foco_real" in nombres
    foco = parametros.resumen(componente, catalogo)["foco"]
    assert foco["tipo"] == "real"
    # y cae por detras del vertice del primario, o sea fuera del barrilete
    m = parametros.mecanica(componente, catalogo)
    assert foco["z_local_mm"] == pytest.approx(m.z_vertice_primario - 40.0)


# ------------------------------------------------------- haz frente al FSM
def _catalogo_con_fsm(diametro_espejo=5.0, haz_modelado=10.0, haz_declarado=None):
    bruto = _telescopio()
    if haz_declarado is not None:
        bruto["optica"] = {
            **OPTICA,
            "diametro_haz_comprimido": _sup(haz_declarado, "mm"),
        }
    catalogo = _catalogo(bruto, _fsm(diametro_espejo), haz_modelado=haz_modelado)
    # El chequeo busca el telescopio por su id del catalogo de verdad.
    catalogo.componentes[0].id = "telescopio_cassegrain"
    return catalogo


def test_el_chequeo_del_fsm_detecta_de_verdad_un_haz_que_no_cabe():
    """Geometria inventada: con un haz declarado mayor que el espejo, FALLA.

    Es el mismo motivo que en test_interferencias.py. Hoy el haz es TBD, asi
    que el chequeo nunca llega a esta rama con el catalogo de verdad; si no se
    comprobara aqui, podria estar roto sin que nadie se enterara.
    """
    # espejo de 5 mm -> admite 5/raiz(2) = 3.54 mm. Un haz de 8 mm no cabe.
    catalogo = _catalogo_con_fsm(diametro_espejo=5.0, haz_declarado=8.0)
    chequeo = fit.chequeo_haz_vs_fsm(catalogo)
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["haz_maximo_admisible_mm"] == pytest.approx(
        5.0 / math.sqrt(2)
    )


def test_el_chequeo_del_fsm_acepta_un_haz_que_si_cabe():
    catalogo = _catalogo_con_fsm(diametro_espejo=10.0, haz_declarado=5.0)
    chequeo = fit.chequeo_haz_vs_fsm(catalogo)
    assert chequeo.estado == fit.OK, chequeo.mensaje


def test_con_el_haz_TBD_el_chequeo_del_fsm_no_es_comprobable():
    """Nunca 'ok': la cifra con la que se dibuja no valida nada."""
    catalogo = _catalogo_con_fsm(diametro_espejo=10.0, haz_modelado=3.0)
    chequeo = fit.chequeo_haz_vs_fsm(catalogo)
    assert chequeo.estado == fit.NO_COMPROBABLE, chequeo.mensaje
    # ...pero dice lo que la hipotesis implica, y a quien pedirle el dato
    assert "eleccion_de_tecnologia" in (chequeo.falta or "")


def test_sin_espejo_declarado_el_chequeo_del_fsm_no_es_comprobable():
    catalogo = _catalogo_con_fsm(diametro_espejo=None)
    assert fit.chequeo_haz_vs_fsm(catalogo).estado == fit.NO_COMPROBABLE


# ------------------------------------- el catalogo de verdad: lo que no cambia
def test_el_telescopio_sigue_siendo_supuesto(catalogo):
    """Un modelo bonito sigue siendo un numero inventado."""
    telescopio = catalogo["telescopio_cassegrain"]
    assert telescopio.dimensiones.estado == SUPUESTO
    assert parts.estado_geometria(telescopio) == SUPUESTO
    color = parts.color(telescopio)
    assert color.toTuple()[3] == pytest.approx(parts.TRANSPARENCIA_SUPUESTO)


def test_el_telescopio_no_suma_en_el_presupuesto_de_masa(catalogo):
    """Su masa es TBD, asi que cuenta como lo que falta, no como un numero."""
    presupuesto = budgets.masa(catalogo)
    assert "telescopio_cassegrain" not in {f.id for f in presupuesto.filas}
    assert "telescopio_cassegrain" not in {f.id for f in presupuesto.supuestas}
    assert "telescopio_cassegrain" in presupuesto.sin_dato


def test_el_telescopio_sigue_entero_en_la_lista_de_pendientes(catalogo):
    supuestos = {
        f["magnitud"]
        for f in catalogo.supuestos()
        if f["componente"] == "telescopio_cassegrain"
    }
    assert "telescopio_cassegrain.dimensiones" in supuestos
    # y cada parametro optico inventado sale con su nombre
    assert "telescopio_cassegrain.optica.focal_primario" in supuestos
    tbd = {
        f["magnitud"]
        for f in catalogo.tbd()
        if f["componente"] == "telescopio_cassegrain"
    }
    assert "telescopio_cassegrain.optica.diametro_haz_comprimido" in tbd
    assert (
        "telescopio_cassegrain.optica.estabilidad_despace_primario_secundario" in tbd
    )


def test_la_envolvente_sigue_siendo_la_que_reserva_el_layout(catalogo, layout):
    """El modelo detallado sustituye al cilindro SIN cambiar lo que reserva."""
    telescopio = catalogo["telescopio_cassegrain"]
    caja = parts.caja_local(telescopio, catalogo)
    assert caja is not None
    assert caja.dims == pytest.approx(tuple(telescopio.dimensiones.valor))
    zona = next(z for z in layout.zonas if z.id == "z_payload_telescopio")
    colocacion = next(
        c for c in layout.colocaciones if c.componente_id == "telescopio_cassegrain"
    )
    from clau3d.structure import Caja

    assert zona.caja.contiene_a(Caja.centrada(caja.dims, colocacion.centro))


def test_el_telescopio_cabe_en_lo_que_el_layout_le_reserva(catalogo):
    """Si la optica derivada pidiera mas tubo, el chequeo lo dice."""
    chequeo = fit.chequeo_longitud_telescopio(catalogo)
    assert chequeo.estado != fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["margen_mm"] >= 0
