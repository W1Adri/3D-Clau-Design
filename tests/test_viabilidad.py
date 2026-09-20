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


def test_la_seccion_con_holgura_nula_no_se_da_por_buena(catalogo):
    """El espesor de pared se dedujo de la pieza mas apretada.

    Con ese espesor, esa misma pieza "cabe" con 0 mm de holgura. Eso no es un
    resultado, es la hipotesis devuelta: tiene que salir como no comprobable.
    """
    chequeo = fit.chequeo_seccion_componentes(catalogo)
    margen = chequeo.numeros["margen_de_espesor_mm"]
    if margen < fit.HOLGURA_NULA_MM:
        assert chequeo.estado == fit.NO_COMPROBABLE, chequeo.mensaje
        assert chequeo.falta
    else:
        assert chequeo.estado in (fit.OK, fit.ATENCION), chequeo.mensaje


def test_con_holgura_real_la_seccion_si_es_concluyente(catalogo):
    """Test sintetico: si el chasis deja margen, el chequeo deja de ser mudo.

    Sin esto, el test de arriba pasaria igual con un chequeo que siempre
    devolviera 'no comprobable'.
    """
    import copy
    import dataclasses

    holgado = copy.deepcopy(catalogo)
    holgado.zona_util["espesor_pared"] = dataclasses.replace(
        catalogo.zona_util["espesor_pared"], valor=0.5
    )
    chequeo = fit.chequeo_seccion_componentes(holgado)
    assert chequeo.numeros["margen_de_espesor_mm"] >= fit.HOLGURA_NULA_MM
    assert chequeo.estado == fit.ATENCION, chequeo.mensaje
