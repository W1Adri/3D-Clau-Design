"""La envolvente 6U sale de la CDS Rev 14.1, no de una constante del codigo."""

import pytest

from clau3d import structure
from clau3d.structure import Caja


def test_envolvente_segun_cds(catalogo):
    dims = structure.envolvente(catalogo).dims
    assert dims == pytest.approx((226.3, 100.0, 366.0))


def test_origen_en_el_centro_geometrico(catalogo):
    """CDS 14.1 req 2.2.1."""
    assert structure.envolvente(catalogo).centro == pytest.approx((0.0, 0.0, 0.0))


def test_zona_util_dentro_de_la_envolvente(catalogo):
    assert structure.envolvente(catalogo).contiene_a(structure.zona_util(catalogo))


def test_cuatro_railes_en_las_esquinas(catalogo):
    railes = structure.railes(catalogo)
    assert len(railes) == 4
    ancho = catalogo.envolvente["ancho_rail_minimo"].escalar()
    for _, caja in railes:
        dx, dy, dz = caja.dims
        assert (dx, dy) == pytest.approx((ancho, ancho))
        assert dz == pytest.approx(catalogo.dims_exteriores[2])


def test_solape_de_cajas():
    a = Caja.centrada((10, 10, 10))
    b = Caja.centrada((10, 10, 10), (5, 0, 0))
    assert a.solapa_con(b)
    assert a.volumen_solape(b) == pytest.approx(500.0)


def test_cajas_que_solo_se_tocan_no_interfieren():
    a = Caja.centrada((10, 10, 10))
    b = Caja.centrada((10, 10, 10), (10, 0, 0))
    assert not a.solapa_con(b)
    assert a.volumen_solape(b) == pytest.approx(0.0)


def test_desbordamiento():
    contenedor = Caja.centrada((100, 100, 100))
    pieza = Caja.centrada((100, 100, 100), (10, 0, 0))
    assert contenedor.desbordamiento(pieza) == pytest.approx((10.0, 0.0, 0.0))
