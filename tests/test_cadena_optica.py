"""La cadena de fibra y la frontera de la codificacion.

Existe por un error que estuvo en el modelo hasta el 2026-09-21: la cadena
declarada ponia el aislador, el filtro, el VOA y el acoplador DETRAS del
codificador de polarizacion. Eso no es una cadena peor, es una cadena que no
funciona -- un aislador PM transmite un solo eje y proyecta los cuatro estados
BB84 sobre el mismo --, y ningun test lo cazaba porque los que habia miraban
que la cadena estuviera ENCADENADA, no que estuviera en el orden correcto.

Por eso aqui no basta comprobar que hoy los chequeos dan OK con el catalogo
del repositorio: eso no demuestra nada del mecanismo. **Cada detector se
comprueba con una cadena inventada que TIENE que hacerlo fallar**, igual que
`test_interferencias.py` comprueba los detectores con solapes inventados. Un
detector que no detecta una cadena rota no vale para nada.
"""

from __future__ import annotations

import pytest

from clau3d import assembly
from clau3d.analysis import fit
from clau3d.datamodel import SUPUESTO, Catalogo, _componente, _magnitud
from clau3d.structure import Caja

CODIFICADOR = "codificador_polarizacion"


# ---------------------------------------------------------------- utilidades
def _pieza(cid: str, dims: list[float], **extra) -> dict:
    bruto = {
        "id": cid, "nombre": cid, "categoria": "payload_bandeja",
        "subsistema": "bandeja_optica",
        "montaje": {"cara": "-Z", "eje": "X", "tipo_eje": "fibra"},
        "forma": {
            "tipo": "caja",
            "dimensiones": {
                "valor": dims, "unidad": "mm", "estado": SUPUESTO,
                "fuente": "geometria de prueba", "falta": "la de verdad",
                "pedir_a": "nadie",
            },
        },
        "masa": {
            "valor": None, "estado": "TBD", "falta": "algo", "pedir_a": "alguien",
        },
    }
    bruto.update(extra)
    return bruto


def _bruto(valor, unidad="mm") -> dict:
    return {
        "valor": valor, "unidad": unidad, "estado": SUPUESTO,
        "fuente": "valor de prueba", "falta": "el de verdad", "pedir_a": "nadie",
    }


def _escalar(nombre: str, valor: float):
    return _magnitud(nombre, _bruto(valor))


# Las piezas de una cadena de mentira, con las mismas cotas de orden de
# magnitud que las de verdad para que los numeros signifiquen algo.
def _catalogo(cadena: list[str], *, recto=True, hasta_colimador=True) -> Catalogo:
    piezas = [
        _componente(_pieza("laser_dfb_1550", [37.4, 12.7, 7.8])),
        _componente(_pieza("aislador", [35.0, 5.5, 5.5])),
        _componente(_pieza("filtro_espectral", [40.0, 5.5, 5.5])),
        _componente(_pieza("mod_intensidad_mxer_ln_10", [110.0, 15.0, 9.7])),
        _componente(_pieza("acoplador_monitor", [60.0, 20.0, 12.0])),
        _componente(_pieza("voa", [35.0, 5.5, 5.5])),
        _componente(
            _pieza(
                "mod_fase_mpz_ln_10", [110.0, 15.0, 9.7],
                funcion=CODIFICADOR,
                altura_eje_fibra=_bruto(4.8),
            )
        ),
        _componente(_pieza("colimador", [28.0, 12.0, 12.0])),
    ]
    tramos = []
    for i, (desde, hasta) in enumerate(zip(cadena, cadena[1:]), start=1):
        tramo = {"id": f"f{i:02d}", "desde": desde, "hasta": hasta,
                 "tipo": "fibra_pm", "union": "fusion"}
        if desde == "mod_fase_mpz_ln_10":
            tramo["post_codificacion"] = True
            tramo["recto"] = recto
            tramo["keep_out"] = not recto
        tramos.append(tramo)
    return Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={},
        integracion={
            "fibra.longitud_protector_empalme": _escalar(
                "integracion.fibra.longitud_protector_empalme", 60.0
            ),
        },
        componentes=piezas,
        conexiones={"meta": {"restricciones_orden": RESTRICCIONES},
                    "opticas_fibra": tramos},
    )


# Las mismas restricciones que declara data/connections.yaml, en la forma en
# que las declara: se escriben aqui porque este fichero comprueba el MOTOR que
# las aplica, no las de verdad. Que las de verdad se cumplan lo comprueba
# tests/test_conexiones.py contra el catalogo real.
RESTRICCIONES = [
    {"antes": "aislador", "despues": f"funcion:{CODIFICADOR}",
     "motivo": "un aislador PM borra la codificacion"},
    {"antes": "voa", "despues": f"funcion:{CODIFICADOR}",
     "motivo": "la PDL del VOA deforma los estados"},
    {"antes": "mod_intensidad_mxer_ln_10", "despues": "acoplador_monitor",
     "motivo": "el acoplador monitoriza el MXER"},
    {"antes": f"funcion:{CODIFICADOR}", "despues": "colimador",
     "directamente": True,
     "motivo": "detras del codificador solo puede ir el colimador"},
]

BUENA = [
    "laser_dfb_1550", "aislador", "filtro_espectral",
    "mod_intensidad_mxer_ln_10", "acoplador_monitor", "voa",
    "mod_fase_mpz_ln_10", "colimador",
]


# ------------------------------------------------- 1. el orden de la cadena
def test_la_cadena_buena_pasa():
    """Un detector que siempre falla no informa de nada."""
    chequeo = fit.chequeo_orden_cadena_fibra(_catalogo(BUENA))
    assert chequeo.estado == fit.OK, chequeo.mensaje
    assert chequeo.numeros["violaciones"] == 0


def test_el_aislador_detras_del_codificador_falla():
    """EL ERROR ORIGINAL. Un aislador PM detras del codificador proyecta los
    cuatro estados BB84 sobre el mismo eje: no los degrada, los borra."""
    rota = [
        "laser_dfb_1550", "filtro_espectral", "mod_intensidad_mxer_ln_10",
        "acoplador_monitor", "voa", "mod_fase_mpz_ln_10", "aislador",
        "colimador",
    ]
    chequeo = fit.chequeo_orden_cadena_fibra(_catalogo(rota))
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.critico
    assert "aislador" in chequeo.mensaje


def test_el_voa_detras_del_codificador_falla():
    """La PDL de un atenuador variable atenua unos estados mas que otros."""
    rota = [
        "laser_dfb_1550", "aislador", "filtro_espectral",
        "mod_intensidad_mxer_ln_10", "acoplador_monitor",
        "mod_fase_mpz_ln_10", "voa", "colimador",
    ]
    chequeo = fit.chequeo_orden_cadena_fibra(_catalogo(rota))
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert "voa" in chequeo.mensaje


def test_un_componente_cualquiera_entre_codificador_y_colimador_falla():
    """Aunque respete todas las demas restricciones: 'directamente' existe
    justo para esto. Aqui el intruso es el acoplador, que no viola ninguna
    otra regla por estar ahi."""
    rota = [
        "laser_dfb_1550", "aislador", "filtro_espectral",
        "mod_intensidad_mxer_ln_10", "voa", "mod_fase_mpz_ln_10",
        "acoplador_monitor", "colimador",
    ]
    chequeo = fit.chequeo_orden_cadena_fibra(_catalogo(rota))
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert "acoplador_monitor" in chequeo.mensaje


def test_la_restriccion_se_resuelve_por_el_papel_y_no_por_el_id():
    """Si el codificador fuera otra pieza, la restriccion tiene que seguir
    diciendo lo mismo sin tocar los datos que la declaran."""
    catalogo = _catalogo(BUENA)
    # La pieza que declaraba el papel deja de declararlo: la restriccion se
    # queda sin ancla y el chequeo lo dice, en vez de dar OK por defecto.
    for c in catalogo.componentes:
        if c.funcion == CODIFICADOR:
            c.funcion = None
    chequeo = fit.chequeo_orden_cadena_fibra(catalogo)
    assert chequeo.estado == fit.NO_COMPROBABLE, chequeo.mensaje
    assert chequeo.falta


def test_sin_restricciones_declaradas_no_es_ok():
    """Que nadie haya dicho que tiene que cumplir no es que cumpla."""
    catalogo = _catalogo(BUENA)
    catalogo.conexiones["meta"]["restricciones_orden"] = []
    chequeo = fit.chequeo_orden_cadena_fibra(catalogo)
    assert chequeo.estado == fit.NO_COMPROBABLE


# ------------------------------------------- 2. el tramo post-codificacion
class _LayoutDePrueba:
    """Lo justo que le piden los dos chequeos de la frontera."""

    def __init__(self, largo_franja: float, colocaciones=()):
        self.zonas = [
            assembly.Zona(
                id="z_payload_franja", nombre="franja",
                caja=Caja(80.0, -47.7, 0.0, 110.0, 47.7, largo_franja),
            ),
            assembly.Zona(
                id="z_payload_telescopio", nombre="telescopio",
                caja=Caja(-10.0, -47.7, 0.0, 80.0, 47.7, largo_franja),
            ),
        ]
        self.colocaciones = list(colocaciones)


def _con_empalme(catalogo: Catalogo, mm: float) -> Catalogo:
    catalogo.integracion["fibra.longitud_protector_empalme"] = _escalar(
        "integracion.fibra.longitud_protector_empalme", mm
    )
    return catalogo


class _Colocacion:
    def __init__(self, cid, centro, rotacion):
        self.componente_id = cid
        self.centro = centro
        self.rotacion = rotacion


def test_el_tramo_post_codificacion_que_no_cabe_falla():
    """110 + 60 + 28 = 198 mm en una franja de 150: el deficit es el resultado.

    (En el catalogo de verdad el codificador mide 130 y no 110, porque su
    envolvente incluye los protectores de fibra; aqui la pieza de prueba no
    los lleva. Lo que se comprueba es el detector, no la cifra.)
    """
    catalogo = _catalogo(BUENA)
    chequeo = fit.chequeo_fibra_post_codificacion(
        catalogo, _LayoutDePrueba(largo_franja=150.0)
    )
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["necesario_mm"] == pytest.approx(198.0)
    assert chequeo.numeros["margen_mm"] == pytest.approx(-48.0)
    assert "NO CABE" in chequeo.mensaje


def test_el_tramo_post_codificacion_que_cabe_no_es_ok_sino_no_comprobable():
    """Que quepa es geometria; que la fibra sea tolerable es fisica, y esa
    falta. Un chequeo que dijera OK aqui estaria afirmando lo que no sabe."""
    chequeo = fit.chequeo_fibra_post_codificacion(
        _catalogo(BUENA), _LayoutDePrueba(largo_franja=400.0)
    )
    assert chequeo.estado == fit.NO_COMPROBABLE, chequeo.mensaje
    assert chequeo.numeros["margen_mm"] > 0
    assert "sensibilidad_termica_fase_pm" in (chequeo.falta or "")


def test_el_margen_se_mueve_con_el_protector_de_empalme():
    """Si el numero estuviera escrito a mano en vez de derivado, esto lo caza."""
    layout = _LayoutDePrueba(largo_franja=200.0)
    corto = fit.chequeo_fibra_post_codificacion(
        _con_empalme(_catalogo(BUENA), 20.0), layout
    )
    largo = fit.chequeo_fibra_post_codificacion(
        _con_empalme(_catalogo(BUENA), 60.0), layout
    )
    assert corto.numeros["margen_mm"] - largo.numeros["margen_mm"] == pytest.approx(40.0)


def test_un_tramo_post_codificacion_marcado_con_curva_falla():
    """El tramo que sale del codificador no se puede curvar: si el dato dice
    que lleva keep-out de curvatura, alguien ha declarado una curva ahi."""
    chequeo = fit.chequeo_fibra_post_codificacion(
        _catalogo(BUENA, recto=False), _LayoutDePrueba(largo_franja=400.0)
    )
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert "recto" in chequeo.mensaje or "curvar" in chequeo.mensaje


def test_un_tramo_post_codificacion_que_no_va_al_colimador_falla():
    rota = [
        "laser_dfb_1550", "aislador", "filtro_espectral",
        "mod_intensidad_mxer_ln_10", "voa", "mod_fase_mpz_ln_10",
        "acoplador_monitor", "colimador",
    ]
    chequeo = fit.chequeo_fibra_post_codificacion(
        _catalogo(rota), _LayoutDePrueba(largo_franja=400.0)
    )
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert "colimador" in chequeo.mensaje


# ------------------------------------------- 3. la altura del eje de fibra
def _layout_con_codificador(y_centro: float, largo=400.0):
    return _LayoutDePrueba(
        largo_franja=largo,
        colocaciones=[
            _Colocacion("mod_fase_mpz_ln_10", (95.0, y_centro, 100.0), (0, 90, 0))
        ],
    )


def test_el_eje_del_codificador_en_el_plano_optico_pasa():
    catalogo = _catalogo(BUENA)
    catalogo.integracion["fibra.tolerancia_coaxialidad"] = _escalar(
        "integracion.fibra.tolerancia_coaxialidad", 0.5
    )
    chequeo = fit.chequeo_altura_eje_codificador(
        catalogo, _layout_con_codificador(0.0)
    )
    assert chequeo.estado == fit.OK, chequeo.mensaje


def test_el_eje_del_codificador_a_otra_altura_que_el_banco_falla():
    """Cualquier desfase en Y obliga a una curva en S despues del codificador,
    que es justo donde esta prohibida."""
    catalogo = _catalogo(BUENA)
    catalogo.integracion["fibra.tolerancia_coaxialidad"] = _escalar(
        "integracion.fibra.tolerancia_coaxialidad", 0.5
    )
    chequeo = fit.chequeo_altura_eje_codificador(
        catalogo, _layout_con_codificador(12.0)
    )
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.numeros["desvio_mm"] == pytest.approx(12.0)


def test_sin_codificador_colocado_no_es_ok():
    """La pieza que hoy no cabe no tiene eje que medir, y decir que su altura
    esta bien seria inventarse el resultado."""
    chequeo = fit.chequeo_altura_eje_codificador(
        _catalogo(BUENA), _LayoutDePrueba(largo_franja=200.0)
    )
    assert chequeo.estado == fit.NO_COMPROBABLE, chequeo.mensaje
    assert chequeo.falta


# --------------------------------- 4. lo que el catalogo de verdad declara
def test_solo_una_pieza_declara_ser_el_codificador(catalogo):
    """Dos piezas con el mismo papel dejarian sin saber donde esta la frontera.
    'validar' lo comprueba tambien; aqui se fija como invariante del catalogo."""
    codificadores = [
        c.id for c in catalogo.componentes
        if c.funcion == CODIFICADOR and c.cuenta_en_presupuesto
    ]
    assert codificadores == ["mod_fase_mpz_ln_10"], codificadores


def test_el_tramo_post_codificacion_no_genera_keep_out_de_curvatura(catalogo, layout):
    """No es un ahorro de volumen: es que ahi no hay codo que reservar.

    Antes del 2026-09-21 el colimador tenia keep-out de curvatura en su puerto
    de entrada, y se comia al FSM, a D1, a D2 y al laser de beacon: cuatro de
    las quince invasiones del modelo. Ahora lo alimenta el codificador en linea
    recta y ese keep-out no existe.
    """
    tramo = next(
        t for t in catalogo.conexiones["opticas_fibra"]
        if t.get("post_codificacion")
    )
    assert tramo["recto"] is True
    assert tramo["keep_out"] is False
    ids = {k.id for k in layout.keep_outs}
    for extremo in (tramo["desde"], tramo["hasta"]):
        assert f"fibra_{extremo}_entrada" not in ids or extremo != tramo["hasta"]
    assert "fibra_colimador_entrada" not in ids


def test_la_cadena_cruza_una_sola_vez_entre_bandeja_y_franja(catalogo, layout):
    """El reparto nuevo existe para esto: una sola travesia de fibra.

    Con el orden anterior la cadena iba y volvia entre la bandeja y la franja.
    Ahora la bandeja es solo la fuente y todo lo demas esta en la franja, asi
    que el camino cruza una vez, y esa vez cae en el tramo pre-codificacion,
    que es el que se puede curvar.
    """
    zona = {c.componente_id: c.zona for c in layout.colocaciones}
    cruces = []
    for tramo in catalogo.conexiones["opticas_fibra"]:
        a, b = zona.get(tramo["desde"]), zona.get(tramo["hasta"])
        if a is None or b is None:
            continue   # alguna punta sin colocar: no se cuenta lo que no esta
        if a != b:
            cruces.append(tramo["id"])
    assert len(cruces) <= 1, cruces
