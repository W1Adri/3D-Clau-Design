"""Integridad del catalogo: la regla de 'ningun numero inventado' es un test."""

import pytest

from clau3d.datamodel import ESTADOS, TBD, validar


def test_catalogo_sin_problemas(catalogo):
    problemas = validar(catalogo)
    assert problemas == [], "\n".join(problemas)


def test_todo_tbd_dice_que_falta_y_a_quien(catalogo):
    for fila in catalogo.pendientes():
        assert fila["falta"] != "(sin describir)", fila
        assert fila["pedir_a"] != "(sin asignar)", fila


def test_ninguna_magnitud_tbd_tiene_valor(catalogo):
    """Un hueco se queda como hueco: nunca se rellena con algo razonable."""
    for componente in catalogo.componentes:
        for magnitud in componente.magnitudes():
            if magnitud.estado == TBD:
                assert magnitud.valor is None, magnitud


def test_toda_magnitud_con_valor_tiene_fuente(catalogo):
    for componente in catalogo.componentes:
        for magnitud in componente.magnitudes():
            if magnitud.esta_declarada and magnitud.valor is not None:
                assert magnitud.fuente, f"{magnitud.nombre} sin fuente"
                assert magnitud.estado in ESTADOS


def test_las_discrepancias_se_conservan(catalogo):
    """Si dos fuentes discrepan se guardan las dos, no se elige una en silencio."""
    discrepancias = catalogo.discrepancias()
    assert discrepancias, "el catalogo declara discrepancias conocidas"
    for d in discrepancias:
        assert d["fuente_usada"], d
        for alternativa in d["alternativas"]:
            assert alternativa.get("fuente"), alternativa
            assert alternativa.get("valor") is not None, alternativa


def test_modulador_de_intensidad_usa_la_cifra_de_grado_espacial(catalogo):
    """El encapsulado que vuela es el de grado espacial, no el comercial."""
    modulador = catalogo["mod_intensidad_mxer_ln_10"]
    dims = modulador.dimensiones.como_vector()
    assert dims[0] == pytest.approx(110.0)
    # y la cifra comercial sigue registrada como alternativa
    alternativas = [a["valor"][0] for a in modulador.dimensiones.alternativas]
    assert 85.0 in alternativas


def test_no_quedan_componentes_eliminados(catalogo):
    """CubeCAT, modulo QUBE y PIC quedaron fuera de la arquitectura opcion B."""
    prohibidos = ("cubecat", "qube", "pic")
    for componente in catalogo.componentes:
        texto = f"{componente.id} {componente.nombre}".lower()
        for prohibido in prohibidos:
            assert prohibido not in texto.split(), componente.id
