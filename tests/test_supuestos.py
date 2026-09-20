"""El estado 'supuesto': un numero inventado que no puede pasar por dato.

Estos tests son la contrapartida de haber abierto la puerta a dibujar piezas
cuya envolvente nadie ha medido. La puerta se abre para que el ensamblaje deje
de tener 19 huecos, no para que el catalogo se llene de cifras sin procedencia,
asi que cada cosa que impide lo segundo esta aqui como test.

Se comprueban con un catalogo de mentira, igual que test_interferencias.py, y no
solo con el de verdad: si manana no quedara ningun supuesto en
data/components.yaml, estos tests seguirian comprobando el mecanismo.
"""

from __future__ import annotations

import pytest

from clau3d.analysis import budgets
from clau3d.datamodel import (
    ESTADOS,
    SUPUESTO,
    TBD,
    Catalogo,
    Magnitud,
    _componente,
    validar,
)


def _catalogo(*componentes: dict) -> Catalogo:
    return Catalogo(
        meta={}, norma={},
        envolvente={
            "masa_maxima": Magnitud(
                nombre="masa_maxima", valor=12000, unidad="g",
                estado="confirmado", fuente="CDS Rev 14.1, Tabla 1",
            )
        },
        zona_util={}, integracion={},
        componentes=[_componente(c) for c in componentes],
        conexiones={},
    )


def _pieza(id_: str, dims: dict, masa: dict | None = None) -> dict:
    return {
        "id": id_,
        "nombre": id_,
        "categoria": "payload_bandeja",
        "subsistema": "bandeja_optica",
        "forma": {"tipo": "caja", "dimensiones": dims},
        "masa": masa or {
            "valor": None, "unidad": "g", "estado": TBD,
            "falta": "masa", "pedir_a": "alguien",
        },
    }


SUPUESTO_COMPLETO = {
    "valor": [10.0, 10.0, 30.0],
    "unidad": "mm",
    "estado": SUPUESTO,
    "fuente": "Tamano generico de un componente en linea de fibra.",
    "falta": "Envolvente del modelo que se elija",
    "pedir_a": "Equipo de payload",
}


def test_el_estado_existe():
    assert SUPUESTO in ESTADOS


def test_un_supuesto_bien_declarado_pasa_la_validacion():
    assert validar(_catalogo(_pieza("x", SUPUESTO_COMPLETO))) == []


@pytest.mark.parametrize(
    "campo, esperado",
    [
        ("fuente", "sin fuente"),
        ("falta", "sin decir que falta"),
        ("pedir_a", "a quien pedir"),
    ],
)
def test_un_supuesto_sin_su_papeleo_no_pasa(campo, esperado):
    """Sin 'fuente' no se sabe de donde sale; sin 'falta'/'pedir_a' se vuelve dato."""
    dims = {k: v for k, v in SUPUESTO_COMPLETO.items() if k != campo}
    problemas = validar(_catalogo(_pieza("x", dims)))
    assert problemas, f"un supuesto sin '{campo}' deberia fallar"
    assert any(esperado in p for p in problemas), problemas


def test_un_supuesto_sin_valor_no_es_un_supuesto():
    """Si no hay ni numero, el estado es TBD, no supuesto."""
    dims = {**SUPUESTO_COMPLETO, "valor": None}
    problemas = validar(_catalogo(_pieza("x", dims)))
    assert any("sin valor" in p for p in problemas), problemas


def test_un_tbd_sigue_sin_poder_llevar_valor():
    """La regla vieja no se ha relajado: abrir 'supuesto' no abre el TBD."""
    dims = {
        "valor": [1.0, 2.0, 3.0], "unidad": "mm", "estado": TBD,
        "falta": "algo", "pedir_a": "alguien",
    }
    problemas = validar(_catalogo(_pieza("x", dims)))
    assert any("Un hueco no se rellena" in p for p in problemas), problemas
    # y el mensaje tiene que ensenar la salida buena
    assert any(SUPUESTO in p for p in problemas), problemas


def test_un_supuesto_sale_en_pendientes_igual_que_un_tbd():
    catalogo = _catalogo(_pieza("x", SUPUESTO_COMPLETO))
    pendientes = catalogo.pendientes()
    assert [f["magnitud"] for f in pendientes if f["estado"] == SUPUESTO] == [
        "x.dimensiones"
    ]
    # y se puede separar de los TBD sin mirar el estado a mano
    assert len(catalogo.supuestos()) == 1
    assert catalogo.tbd(), "la masa TBD de la pieza sigue contando"


def test_la_fila_de_pendientes_lleva_el_valor_que_se_esta_dibujando():
    """Quien lee el informe tiene que ver QUE numero hay que sustituir."""
    fila = _catalogo(_pieza("x", SUPUESTO_COMPLETO)).supuestos()[0]
    assert fila["valor_modelado"] == [10.0, 10.0, 30.0]


def test_una_masa_supuesta_no_suma_en_el_presupuesto():
    """Sumar una masa inventada a una de ficha da un total que no se puede ensenar."""
    catalogo = _catalogo(
        _pieza("real", SUPUESTO_COMPLETO, masa={
            "valor": 100.0, "unidad": "g", "estado": "confirmado",
            "fuente": "ficha",
        }),
        _pieza("inventada", SUPUESTO_COMPLETO, masa={
            "valor": 50.0, "unidad": "g", "estado": SUPUESTO,
            "fuente": "razonamiento", "falta": "masa real", "pedir_a": "alguien",
        }),
    )
    presupuesto = budgets.masa(catalogo)
    assert presupuesto.total_contabilizado == pytest.approx(100.0)
    assert presupuesto.total_supuesto == pytest.approx(50.0)
    assert [f.id for f in presupuesto.supuestas] == ["inventada"]


def test_un_supuesto_se_imprime_marcado():
    """Alla donde salga el numero sale tambien que es inventado."""
    magnitud = Magnitud(
        nombre="x", valor=12.0, unidad="mm", estado=SUPUESTO, fuente="porque si"
    )
    assert "SUPUESTO" in str(magnitud)
