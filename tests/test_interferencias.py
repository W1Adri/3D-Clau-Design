"""Interferencias.

Con el layout aun sin confirmar no hay piezas colocadas, asi que los tests
sobre el ensamblaje real pasarian solos. Por eso aqui se comprueban ademas,
con geometria sintetica, que los detectores DETECTAN de verdad.
"""

import cadquery as cq
import pytest

from clau3d.analysis import interference
from clau3d.assembly import Colocacion, KeepOut, Layout, PiezaColocada
from clau3d.structure import Caja


def _pieza(nombre, dims, centro):
    caja = Caja.centrada(dims, centro)
    colocacion = Colocacion(
        componente_id=nombre, instancia=1, centro=centro,
        rotacion=(0, 0, 0), zona=None, nombre=nombre,
    )
    return PiezaColocada(
        colocacion=colocacion, componente=None,
        solido=caja.solido(), caja_mundo=caja,
    )


# --- el ensamblaje real ------------------------------------------------
def test_sin_solapes_entre_piezas_colocadas(piezas):
    hallazgos = interference.entre_piezas(piezas)
    assert hallazgos == [], "\n".join(h.detalle for h in hallazgos)


def test_todo_dentro_de_la_envolvente(catalogo, piezas):
    hallazgos = interference.fuera_de_envolvente(catalogo, piezas)
    assert hallazgos == [], "\n".join(h.detalle for h in hallazgos)


def test_sin_invasion_de_keep_outs(layout, piezas):
    hallazgos = interference.invasion_keep_out(layout, piezas)
    assert hallazgos == [], "\n".join(h.detalle for h in hallazgos)


# --- que el detector detecta -------------------------------------------
def test_detecta_un_solape_real():
    a = _pieza("a", (20, 20, 20), (0, 0, 0))
    b = _pieza("b", (20, 20, 20), (10, 0, 0))
    hallazgos = interference.entre_piezas([a, b])
    assert len(hallazgos) == 1
    assert hallazgos[0].volumen_mm3 == pytest.approx(10 * 20 * 20, rel=1e-3)


def test_dos_piezas_que_se_tocan_no_son_interferencia():
    a = _pieza("a", (20, 20, 20), (0, 0, 0))
    b = _pieza("b", (20, 20, 20), (20, 0, 0))
    assert interference.entre_piezas([a, b]) == []


def test_detecta_pieza_fuera_de_la_envolvente(catalogo):
    dx, _, _ = catalogo.dims_exteriores
    fuera = _pieza("fuera", (20, 20, 20), (dx / 2 + 50, 0, 0))
    hallazgos = interference.fuera_de_envolvente(catalogo, [fuera])
    assert len(hallazgos) == 1
    assert hallazgos[0].tipo == "fuera_envolvente"


def test_detecta_pieza_que_invade_la_pared(catalogo):
    """Dentro de la envolvente pero fuera de la zona util: tambien falla.

    La banda de pared es estrecha, asi que la pieza de prueba se dimensiona a
    partir de ella en vez de con un tamano fijo.
    """
    borde_exterior = catalogo.dims_exteriores[1] / 2
    borde_interior = catalogo.dims_interiores[1] / 2
    espesor = borde_exterior - borde_interior
    assert espesor > 0, "sin pared no hay nada que invadir"
    pieza = _pieza(
        "en_la_pared",
        (10, espesor / 2, 10),
        (0, (borde_interior + borde_exterior) / 2, 0),
    )
    hallazgos = interference.fuera_de_envolvente(catalogo, [pieza])
    assert len(hallazgos) == 1
    assert hallazgos[0].tipo == "fuera_zona_util"


def test_detecta_invasion_de_keep_out():
    layout = Layout(
        estado="propuesta", meta={}, zonas=[], colocaciones=[],
        keep_outs=[KeepOut(id="haz", tipo="haz", caja=Caja.centrada((50, 50, 50)))],
    )
    intrusa = _pieza("intrusa", (20, 20, 20), (0, 0, 0))
    hallazgos = interference.invasion_keep_out(layout, [intrusa])
    assert len(hallazgos) == 1
    assert hallazgos[0].tipo == "keep_out"


def test_rotacion_de_90_grados_cambia_la_caja_en_el_mundo(catalogo):
    """Una pieza girada ocupa otra caja: el detector trabaja con la real."""
    from clau3d import assembly, parts

    modulador = catalogo["mod_intensidad_mxer_ln_10"]
    dims = modulador.dimensiones.como_vector()
    girada = assembly._localizar(
        parts.solido(modulador),
        Colocacion("m", 1, (0, 0, 0), (0, 0, 90), None, "m"),
    )
    bb = girada.BoundingBox()
    assert bb.xlen == pytest.approx(dims[1], abs=1e-6)
    assert bb.ylen == pytest.approx(dims[0], abs=1e-6)
