"""Los keep-outs: volumen reservado con procedencia, y sin fingir que es dato.

Como en los demas tests de mecanismo, la geometria es inventada. Lo que se
comprueba es que un keep-out dibujado a partir de un numero SUPUESTO no se
confunde nunca con un choque de geometrias: ni en el informe ni en el codigo
de salida. Es la diferencia entre "esto no cabe" y "esto no cabe SI el radio de
curvatura es el que nos hemos inventado".
"""

from __future__ import annotations

import pytest

from clau3d.analysis import interference
from clau3d.assembly import Colocacion, KeepOut, Layout, PiezaColocada
from clau3d.structure import Caja


def _pieza(nombre: str, caja: Caja) -> PiezaColocada:
    return PiezaColocada(
        colocacion=Colocacion(
            componente_id=nombre, instancia=1, centro=caja.centro,
            rotacion=(0, 0, 0), zona=None, nombre=nombre,
        ),
        componente=None,
        solido=caja.solido(),
        caja_mundo=caja,
    )


def _layout(*keep_outs: KeepOut) -> Layout:
    return Layout(estado="propuesta", meta={}, zonas=[], colocaciones=[],
                  keep_outs=list(keep_outs))


def test_un_keep_out_supuesto_marca_su_hallazgo_como_supuesto():
    layout = _layout(KeepOut(
        id="fibra_x", tipo="fibra", caja=Caja.centrada((50, 50, 50)),
        estado="supuesto", fuente="radio de curvatura inventado",
    ))
    hallazgos = interference.invasion_keep_out(layout, [
        _pieza("intrusa", Caja.centrada((20, 20, 20)))
    ])
    assert len(hallazgos) == 1
    assert hallazgos[0].basada_en_supuesto is True
    assert "SUPUESTO" in hallazgos[0].detalle


def test_un_keep_out_con_dato_de_verdad_no_la_marca():
    """El dia que llegue el radio real, el mismo hallazgo pasa a contar."""
    layout = _layout(KeepOut(
        id="fibra_x", tipo="fibra", caja=Caja.centrada((50, 50, 50)),
        estado="confirmado", fuente="ficha de la fibra elegida",
    ))
    hallazgos = interference.invasion_keep_out(layout, [
        _pieza("intrusa", Caja.centrada((20, 20, 20)))
    ])
    assert len(hallazgos) == 1
    assert hallazgos[0].basada_en_supuesto is False
    assert "SUPUESTO" not in hallazgos[0].detalle


def test_un_solape_de_geometria_nunca_es_supuesto():
    """Dos solidos en el mismo sitio es un hecho, no una hipotesis."""
    a = _pieza("a", Caja.centrada((20, 20, 20), (0, 0, 0)))
    b = _pieza("b", Caja.centrada((20, 20, 20), (10, 0, 0)))
    hallazgos = interference.entre_piezas([a, b])
    assert hallazgos and all(not h.basada_en_supuesto for h in hallazgos)


def test_los_keep_outs_del_layout_declaran_estado_y_fuente(layout):
    """Un keep-out lleva procedencia, igual que un numero y que un STEP."""
    for keep_out in layout.keep_outs:
        assert keep_out.estado, keep_out.id
        assert keep_out.fuente, f"{keep_out.id} sin decir de donde sale"
        if keep_out.es_supuesto:
            assert "SUPUESTO" in keep_out.fuente.upper(), keep_out.id


def test_ningun_keep_out_se_sale_de_la_zona_util(catalogo, layout):
    """Reservar sitio fuera del satelite no reserva nada: es ruido."""
    from clau3d import structure

    util = structure.zona_util(catalogo)
    for keep_out in layout.keep_outs:
        assert util.contiene_a(keep_out.caja, tolerancia=1e-6), keep_out.id


def test_ninguna_pieza_invade_su_propio_keep_out(layout, piezas):
    """Un keep-out arranca donde acaba la pieza, no dentro de ella.

    Paso de verdad: el keep-out del coaxial del modulador salia del borde de su
    caja envolvente, y como esa caja ya incluia el conector -- y el centro de
    la pieza sigue siendo el del cuerpo -- se quedaba 5 mm corto y el modulador
    se invadia a si mismo 2.43 cm3.
    """
    for hallazgo in interference.invasion_keep_out(layout, piezas):
        assert hallazgo.a not in hallazgo.b, (
            f"{hallazgo.a} invade un keep-out que sale de si misma: "
            f"{hallazgo.detalle}"
        )
