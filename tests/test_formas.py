"""Formas aproximadas: cilindros y conectores, con geometria inventada.

Igual que test_interferencias.py y test_step_fabricante.py, estos tests NO
miran el catalogo de verdad. Si manana no quedara ni un cilindro en
data/components.yaml, el mecanismo tiene que seguir comprobado: el dia que
alguien anada el primero, el test ya estaba ahi.
"""

from __future__ import annotations

import math

import pytest

from clau3d import parts
from clau3d.datamodel import SUPUESTO, TBD, Catalogo, _componente, validar


def _pieza(bruto: dict):
    return _componente({
        "id": "x", "nombre": "x", "categoria": "payload_bandeja",
        "subsistema": "bandeja_optica",
        "masa": {"valor": None, "unidad": "g", "estado": TBD,
                 "falta": "masa", "pedir_a": "alguien"},
        **bruto,
    })


def _dims(valor):
    return {
        "valor": valor, "unidad": "mm", "estado": SUPUESTO,
        "fuente": "geometria de prueba", "falta": "la de verdad",
        "pedir_a": "nadie",
    }


CAJA = {"forma": {"tipo": "caja", "dimensiones": _dims([20.0, 10.0, 30.0])}}


# --- cilindros --------------------------------------------------------
@pytest.mark.parametrize(
    "eje, dims",
    [
        ("X", [40.0, 6.0, 6.0]),
        ("Y", [6.0, 40.0, 6.0]),
        ("Z", [6.0, 6.0, 40.0]),
    ],
)
def test_el_cilindro_gira_al_eje_declarado(eje, dims):
    pieza = _pieza({"forma": {"tipo": "cilindro", "eje": eje, "dimensiones": _dims(dims)}})
    caja = parts.caja_local(pieza)
    assert caja is not None
    for medido, declarado in zip(caja.dims, dims):
        assert medido == pytest.approx(declarado, abs=1e-6)


def test_el_cilindro_tiene_volumen_de_cilindro_no_de_caja():
    """Si saliera una caja, el volumen seria 4/pi veces mayor y nadie lo veria."""
    pieza = _pieza({
        "forma": {"tipo": "cilindro", "eje": "X", "dimensiones": _dims([40.0, 6.0, 6.0])}
    })
    esperado = math.pi * 3.0 ** 2 * 40.0
    assert parts.solido(pieza).Volume() == pytest.approx(esperado, rel=1e-3)


def test_un_cilindro_de_seccion_ovalada_no_pasa_la_validacion():
    catalogo = Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={}, integracion={},
        componentes=[_pieza({
            "forma": {"tipo": "cilindro", "eje": "X",
                      "dimensiones": _dims([40.0, 6.0, 8.0])},
        })],
        conexiones={},
    )
    problemas = validar(catalogo)
    assert any("diametro" in p for p in problemas), problemas


# --- conectores -------------------------------------------------------
def _con_conector(**extra):
    return _pieza({
        "forma": {
            "tipo": "caja",
            "dimensiones": _dims([20.0, 10.0, 30.0]),
            "conectores": [{
                "id": "rf", "tipo": "coaxial", "cara": "+Y",
                "dimensiones": _dims([6.0, 12.0, 6.0]),
                **extra,
            }],
        },
    })


def test_el_conector_agranda_la_caja_envolvente():
    """Lo que decide si una pieza cabe con el cable puesto es el conector."""
    sin = parts.caja_local(_pieza(CAJA))
    con = parts.caja_local(_con_conector())
    assert sin is not None and con is not None
    assert sin.dims == pytest.approx((20.0, 10.0, 30.0))
    # +12 mm por Y: el conector arranca en la cara y sobresale entero.
    assert con.dims == pytest.approx((20.0, 22.0, 30.0))
    assert con.ymax == pytest.approx(5.0 + 12.0)
    assert con.ymin == pytest.approx(-5.0)


def test_el_conector_no_se_mete_dentro_del_cuerpo():
    """Sobresale hacia fuera; si se solapara, el volumen se contaria dos veces."""
    solido = parts.solido(_con_conector())
    assert solido.Volume() == pytest.approx(20 * 10 * 30 + 6 * 12 * 6, rel=1e-6)


def test_el_desplazamiento_recorre_el_plano_de_la_cara():
    con = parts.caja_local(_con_conector(desplazamiento=[4.0, -9.0]))
    assert con is not None
    # cara +Y: el plano es (X, Z), en ese orden.
    assert con.xmax == pytest.approx(10.0 + 0.0)   # 4 + 3 = 7 < 10, no asoma
    assert con.zmin == pytest.approx(-15.0)


def test_un_conector_sin_cotas_no_se_dibuja_de_ningun_tamano():
    pieza = _pieza({
        "forma": {
            "tipo": "caja", "dimensiones": _dims([20.0, 10.0, 30.0]),
            "conectores": [{
                "id": "rf", "tipo": "coaxial", "cara": "+Y",
                "dimensiones": {"valor": None, "unidad": "mm", "estado": TBD,
                                "falta": "cotas del conector", "pedir_a": "alguien"},
            }],
        },
    })
    caja = parts.caja_local(pieza)
    assert caja is not None
    assert caja.dims == pytest.approx((20.0, 10.0, 30.0))
    # ...pero el hueco no desaparece: sale como pendiente.
    assert any(m.es_tbd for m in pieza.magnitudes() if "rf" in m.nombre)


def test_una_cara_inventada_se_rechaza_al_cargar():
    from clau3d.datamodel import ErrorDeDatos

    with pytest.raises(ErrorDeDatos, match="cara"):
        _pieza({
            "forma": {
                "tipo": "caja", "dimensiones": _dims([20.0, 10.0, 30.0]),
                "conectores": [{"id": "rf", "cara": "arriba",
                                "dimensiones": _dims([1.0, 1.0, 1.0])}],
            },
        })
