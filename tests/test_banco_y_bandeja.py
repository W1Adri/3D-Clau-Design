"""Las tres cotas nuevas del 2026-09-21, con geometria inventada.

Igual que test_interferencias.py y test_cassegrain.py: el catalogo de verdad
cambia -- manana el haz sera otro y las celdas del banco tambien -- y lo que
tiene que seguir comprobado es el MECANISMO, no la cifra de hoy. Un chequeo que
solo se probara contra el catalogo real pasaria o fallaria segun el reparto de
esta semana.

Las tres cosas que se comprueban salen del mismo cambio (CLAUDE.md 3.11):

1. **El espejo de plegado anclado bajo la franja.** El colimador va encima del
   espejo y tiene que caber DENTRO de la franja; si el espejo se queda hacia
   -X, el colimador se mete en la zona del telescopio, donde esta el barrilete.
   Al bajar las celdas del banco de 23 y 20 mm a 16, la linea se compacto 11 mm
   hacia el FSM y eso paso de verdad.
2. **El haz frente a la apertura libre de las opticas del banco.** Un haz de
   d mm a 45 grados deja una huella de d x d*raiz(2), asi que la familia Ø12.7
   pone un techo al haz. Es el mismo razonamiento de 'haz_vs_fsm', aplicado a
   D1, D2 y el espejo.
3. **La placa de la bandeja dentro de su zona.** Su contorno se DERIVA de la
   zona, y la zona se encoge cuando el telescopio crece. Con los 102.4 mm que
   la placa tenia escritos y el telescopio en 227, la placa se salia del 6U.
"""

from __future__ import annotations

import pytest

from clau3d import assembly
from clau3d.analysis import fit
from clau3d.datamodel import SUPUESTO, Catalogo, Magnitud, _componente
from clau3d.structure import Caja


# ---------------------------------------------------------------- utilidades
def _sup(valor, unidad=None):
    bloque = {
        "valor": valor, "estado": SUPUESTO, "fuente": "geometria de prueba",
        "falta": "la de verdad", "pedir_a": "nadie",
    }
    if unidad:
        bloque["unidad"] = unidad
    return bloque


def _magnitud(nombre: str, valor: float) -> Magnitud:
    return Magnitud(
        nombre=nombre, valor=valor, unidad="mm", estado=SUPUESTO,
        fuente="geometria de prueba", falta="la de verdad", pedir_a="nadie",
    )


def _caja(cid: str, dims: list[float], tipo: str = "caja", eje: str | None = None):
    forma: dict = {"tipo": tipo, "dimensiones": _sup(dims, "mm")}
    if eje:
        forma["eje"] = eje
    return _componente({
        "id": cid, "nombre": cid, "categoria": "payload_optico",
        "subsistema": "terminal_optico", "forma": forma,
        "masa": {"valor": None, "estado": "TBD", "falta": "x", "pedir_a": "y"},
    })


class _Colocacion:
    def __init__(self, cid, centro, rotacion=(0, 0, 0), zona="z_payload_banco"):
        self.componente_id = cid
        self.centro = list(centro)
        self.rotacion = list(rotacion)
        self.zona = zona


class _Layout:
    def __init__(self, zonas, colocaciones):
        self.zonas = zonas
        self.colocaciones = colocaciones


# ------------------------------------- 1. el espejo anclado bajo la franja
def _escena_del_espejo(x_espejo: float, x_colimador: float | None = None):
    """Banco con el espejo en X y el colimador encima, coaxial con el.

    La franja empieza en X = +50: a la izquierda esta la zona del telescopio,
    donde el barrilete ocupa todo el hueco.
    """
    catalogo = Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={}, integracion={},
        componentes=[
            _caja("espejo_plegado_cuantico", [16.0, 16.0, 16.0]),
            # Cilindro con el eje en X, como el del catalogo: colocado gira
            # para que su eje vaya por Z y lo que ocupa en X sean 12 mm, no 28.
            _caja("colimador", [28.0, 12.0, 12.0], tipo="cilindro", eje="X"),
        ],
        conexiones={},
    )
    zonas = [
        assembly.Zona(
            id="z_payload_franja", nombre="franja",
            caja=Caja(50.0, -20.0, 0.0, 80.0, 20.0, 100.0),
        ),
    ]
    colocaciones = [
        _Colocacion("espejo_plegado_cuantico", [x_espejo, 0.0, -10.0]),
        _Colocacion(
            "colimador",
            [x_espejo if x_colimador is None else x_colimador, 0.0, 20.0],
            rotacion=(0, 90, 0), zona="z_payload_franja",
        ),
    ]
    return catalogo, _Layout(zonas, colocaciones)


def test_el_espejo_demasiado_hacia_menos_x_hace_fallar_el_chequeo():
    """SINTETICO OBLIGATORIO: si no detectara esto no detectaria nada.

    Con el espejo en X = +52 el colimador (Ø12) llega a +46, o sea 4 mm dentro
    de la zona del telescopio. No es que quede justo: es que choca con el
    barrilete, que llena su zona entera.
    """
    catalogo, layout = _escena_del_espejo(x_espejo=52.0)
    chequeo = fit.chequeo_espejo_bajo_la_franja(catalogo, layout)
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["margen_mm"] < 0


def test_el_espejo_anclado_donde_toca_pasa_el_chequeo():
    """Y con sitio dice que si: un chequeo que siempre falla no informa."""
    catalogo, layout = _escena_del_espejo(x_espejo=65.0)
    chequeo = fit.chequeo_espejo_bajo_la_franja(catalogo, layout)
    assert chequeo.estado == fit.OK, chequeo.mensaje
    assert chequeo.numeros["margen_mm"] == pytest.approx(9.0)


def test_el_colimador_se_mide_girado_como_lo_coloca_el_layout():
    """28 mm de largo por 12 de diametro: lo que ocupa en X son 12.

    Si se leyera la cota local en vez de girar el solido, el chequeo creeria
    que el colimador ocupa 28 mm en X y fallaria donde no hay problema. Es la
    misma regla por la que el generador gira en vez de permutar cotas.
    """
    catalogo, layout = _escena_del_espejo(x_espejo=65.0)
    chequeo = fit.chequeo_espejo_bajo_la_franja(catalogo, layout)
    assert chequeo.numeros["radio_colimador_mm"] == pytest.approx(6.0)


def test_un_colimador_descentrado_del_espejo_falla():
    """No son dos piezas vecinas: son coaxiales o el haz no da en el espejo."""
    catalogo, layout = _escena_del_espejo(x_espejo=65.0, x_colimador=70.0)
    chequeo = fit.chequeo_espejo_bajo_la_franja(catalogo, layout)
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["coaxialidad_mm"] == 5.0


def test_sin_espejo_colocado_el_chequeo_no_es_concluyente():
    catalogo, layout = _escena_del_espejo(x_espejo=65.0)
    layout.colocaciones = [
        c for c in layout.colocaciones if c.componente_id != "espejo_plegado_cuantico"
    ]
    chequeo = fit.chequeo_espejo_bajo_la_franja(catalogo, layout)
    assert chequeo.estado == fit.NO_COMPROBABLE


def test_sin_layout_el_chequeo_del_espejo_no_es_concluyente():
    catalogo, _ = _escena_del_espejo(x_espejo=65.0)
    assert (
        fit.chequeo_espejo_bajo_la_franja(catalogo, None).estado
        == fit.NO_COMPROBABLE
    )


# ------------------------------------- 2. el haz contra la apertura libre
def _catalogo_de_haz(haz: float, apertura: float) -> Catalogo:
    return Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={},
        integracion={
            "optica.diametro_haz_modelado": _magnitud("haz", haz),
            "optica.apertura_libre_optica_banco": _magnitud("apertura", apertura),
        },
        componentes=[
            _caja("dicroico_d1", [16.0, 16.0, 16.0]),
            _caja("dicroico_d2", [16.0, 16.0, 16.0]),
            _caja("espejo_plegado_cuantico", [16.0, 16.0, 16.0]),
        ],
        conexiones={},
    )


def test_un_haz_cuya_huella_a_45_no_cabe_en_la_optica_falla():
    """SINTETICO OBLIGATORIO: haz * raiz(2) > apertura libre.

    10 mm de haz dejan una huella de 14.1 mm, que no cabe en los 11.4 mm de
    apertura libre de un Ø12.7. Es exactamente lo que obligo a bajar el haz a
    7 mm al fijar esa familia de opticas.
    """
    chequeo = fit.chequeo_haz_vs_optica_banco(_catalogo_de_haz(10.0, 11.4))
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["margen_mm"] < 0
    assert chequeo.numeros["huella_a_45_mm"] > chequeo.numeros[
        "apertura_libre_optica_mm"
    ]


def test_un_haz_que_si_cabe_no_valida_nada_pero_da_el_techo():
    """Cabe, pero sale NO COMPROBABLE: los dos numeros son supuestos.

    Y uno de los dos se eligio precisamente para que esto saliera bien, asi que
    decir 'ok' seria devolver la hipotesis. Lo util es el techo.
    """
    chequeo = fit.chequeo_haz_vs_optica_banco(_catalogo_de_haz(7.0, 11.4))
    assert chequeo.estado == fit.NO_COMPROBABLE
    assert chequeo.numeros["haz_maximo_admisible_mm"] > 7.0
    assert chequeo.falta


def test_el_techo_del_haz_se_mueve_con_la_apertura():
    """Si estuviera escrito en vez de derivado, esto lo caza."""
    estrecha = fit.chequeo_haz_vs_optica_banco(_catalogo_de_haz(7.0, 11.4))
    ancha = fit.chequeo_haz_vs_optica_banco(_catalogo_de_haz(7.0, 22.9))
    assert (
        ancha.numeros["haz_maximo_admisible_mm"]
        > estrecha.numeros["haz_maximo_admisible_mm"]
    )


def test_sin_apertura_declarada_el_chequeo_del_haz_no_es_concluyente():
    catalogo = Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={},
        integracion={"optica.diametro_haz_modelado": _magnitud("haz", 7.0)},
        componentes=[], conexiones={},
    )
    assert (
        fit.chequeo_haz_vs_optica_banco(catalogo).estado == fit.NO_COMPROBABLE
    )


# ------------------------------------- 3. la placa de la bandeja en su zona
def _escena_de_bandeja(placa_x: float, placa_z: float, zona_z: float = 79.4):
    catalogo = Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={},
        integracion={"bandeja.holgura_montaje": _magnitud("holgura", 2.0)},
        componentes=[_caja("bandeja_optica", [placa_x, 3.0, placa_z])],
        conexiones={},
    )
    zonas = [
        assembly.Zona(
            id="z_payload_bandeja", nombre="bandeja",
            caja=Caja(0.0, 0.0, 0.0, 121.7, 95.4, zona_z),
        ),
    ]
    return catalogo, _Layout(zonas, [])


def test_una_placa_mas_grande_que_su_zona_falla():
    """SINTETICO OBLIGATORIO, y no hipotetico: es lo que paso el 2026-09-21.

    Al subir el telescopio de 200 a 227 mm la zona de la bandeja bajo de 106.4
    a 79.4 mm, y la placa seguia con los 102.4 que tenia escritos. Como la
    bandeja llega hasta la cara -Z del 6U, eso no es una placa apretada: es una
    placa que atraviesa la pared.
    """
    catalogo, layout = _escena_de_bandeja(placa_x=117.7, placa_z=102.4)
    chequeo = fit.chequeo_bandeja_en_su_zona(catalogo, layout)
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["margen_Z_mm"] < 0
    assert chequeo.numeros["derivado_Z_mm"] == 75.4


def test_una_placa_derivada_de_su_zona_pasa():
    catalogo, layout = _escena_de_bandeja(placa_x=117.7, placa_z=75.4)
    chequeo = fit.chequeo_bandeja_en_su_zona(catalogo, layout)
    assert chequeo.estado == fit.OK, chequeo.mensaje


def test_una_placa_mas_pequena_de_la_cuenta_avisa_pero_no_falla():
    """Cabe, pero esta dejando sitio sin usar justo donde aprieta el reparto."""
    catalogo, layout = _escena_de_bandeja(placa_x=117.7, placa_z=50.0)
    chequeo = fit.chequeo_bandeja_en_su_zona(catalogo, layout)
    assert chequeo.estado == fit.ATENCION, chequeo.mensaje


def test_el_contorno_derivado_se_mueve_con_la_zona():
    """Si estuviera escrito en vez de derivado, esto lo caza."""
    _, corta = _escena_de_bandeja(117.7, 75.4, zona_z=79.4)
    catalogo_largo, larga = _escena_de_bandeja(117.7, 75.4, zona_z=106.4)
    catalogo_corto, _ = _escena_de_bandeja(117.7, 75.4, zona_z=79.4)
    a = fit.chequeo_bandeja_en_su_zona(catalogo_corto, corta)
    b = fit.chequeo_bandeja_en_su_zona(catalogo_largo, larga)
    assert b.numeros["derivado_Z_mm"] - a.numeros["derivado_Z_mm"] == 27.0


def test_sin_holgura_declarada_el_chequeo_de_la_bandeja_no_es_concluyente():
    catalogo, layout = _escena_de_bandeja(117.7, 75.4)
    catalogo.integracion = {}
    assert (
        fit.chequeo_bandeja_en_su_zona(catalogo, layout).estado
        == fit.NO_COMPROBABLE
    )


# ------------------------------------- 4. y sobre el catalogo de verdad
def test_los_tres_chequeos_estan_registrados(catalogo, layout):
    ids = {c.id for c in fit.todos(catalogo, layout)}
    for cid in (
        "espejo_bajo_la_franja", "haz_vs_optica_banco", "bandeja_en_su_zona"
    ):
        assert cid in ids, cid


def test_la_placa_real_sigue_derivada_de_su_zona(catalogo, layout):
    chequeo = fit.chequeo_bandeja_en_su_zona(catalogo, layout)
    assert chequeo.estado == fit.OK, chequeo.mensaje
