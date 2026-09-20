"""Chequeos de viabilidad independientes de la colocacion."""

from clau3d.analysis import fit


def test_ningun_chequeo_falla(catalogo):
    criticos = [c for c in fit.todos(catalogo) if c.critico]
    assert criticos == [], "\n".join(f"{c.titulo}: {c.mensaje}" for c in criticos)


def test_el_volumen_ocupado_cabe_en_la_zona_util(catalogo):
    chequeo = fit.chequeo_volumen_total(catalogo)
    assert chequeo.numeros["fraccion_ocupada"] < 1.0


def test_la_masa_conocida_no_pasa_del_limite_de_la_norma(catalogo):
    chequeo = fit.chequeo_masa(catalogo)
    assert chequeo.numeros["masa_conocida_g"] <= chequeo.numeros["limite_g"]


def test_un_chequeo_sin_datos_no_sale_como_correcto(catalogo):
    """Lo que no se puede comprobar se dice, no se da por bueno."""
    sin_datos = [c for c in fit.todos(catalogo) if c.estado == fit.NO_COMPROBABLE]
    assert sin_datos, "hay magnitudes TBD, deberia haber chequeos no comprobables"
    for chequeo in sin_datos:
        assert chequeo.estado != fit.OK
        assert chequeo.falta, chequeo.titulo


def test_los_moduladores_caben_en_algun_eje(catalogo):
    for chequeo in fit.chequeo_longitud_moduladores(catalogo):
        assert chequeo.estado != fit.FALLA, chequeo.mensaje
