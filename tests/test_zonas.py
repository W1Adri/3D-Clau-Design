"""Las zonas propuestas tienen que ser coherentes entre si y con el 6U."""

import pytest
from itertools import combinations

from clau3d import structure


def test_hay_zonas_propuestas(layout):
    assert layout.zonas, "data/layout.yaml debe proponer zonas"


def test_cada_zona_cabe_en_la_zona_util(catalogo, layout):
    interior = structure.zona_util(catalogo)
    for zona in layout.zonas:
        assert interior.contiene_a(zona.caja, tolerancia=1e-6), zona.id


def test_las_zonas_no_se_solapan(layout):
    for a, b in combinations(layout.zonas, 2):
        assert not a.caja.solapa_con(b.caja, tolerancia=1e-6), f"{a.id} y {b.id}"


def test_las_zonas_cubren_toda_la_zona_util(catalogo, layout):
    """Si sobra volumen sin asignar, es que falta una zona por declarar."""
    total = sum(z.caja.volumen_mm3 for z in layout.zonas)
    assert total == pytest.approx(catalogo.volumen_interior_mm3, rel=1e-6)


def test_toda_colocacion_apunta_a_una_zona_declarada(layout):
    """...o a 'exterior', que es lo de fuera del chasis y no es una zona.

    Las cinco zonas embaldosan el hueco util INTERIOR. Un panel de cuerpo o una
    antena montada por fuera no estan en ninguna de ellas, y meterlos en una
    romperia el embaldosado. 'exterior' los marca sin fingir que son una zona
    mas: el detector de desbordes los trata aparte, con la protrusion que
    permite la CDS.
    """
    ids = {z.id for z in layout.zonas} | {"exterior"}
    for colocacion in layout.colocaciones:
        assert colocacion.zona in ids, colocacion


def test_lo_marcado_exterior_esta_fuera_y_lo_demas_dentro(catalogo, layout):
    """La zona 'exterior' del layout y la marca 'exterior' del catalogo cuadran."""
    for colocacion in layout.colocaciones:
        componente = catalogo[colocacion.componente_id]
        if colocacion.zona == "exterior":
            assert componente.exterior, (
                f"{componente.id} esta colocado fuera pero el catalogo no lo "
                f"marca 'exterior', asi que el detector de desbordes lo dara "
                f"por fallo"
            )


def test_el_layout_declara_su_estado(layout):
    assert layout.estado in ("propuesta", "confirmada"), layout.estado
