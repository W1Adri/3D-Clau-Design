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


def test_sin_invasion_de_keep_outs_que_salgan_de_un_dato(layout, piezas):
    """Los keep-outs SUPUESTOS si se invaden, y eso no es un fallo del reparto.

    Hoy los tres parametros que dimensionan un keep-out -- el radio minimo de
    curvatura de la fibra, el del coaxial y el diametro de haz -- son TBD, asi
    que TODOS los keep-outs se dibujan con numeros inventados y varios se
    invaden. Lo que dicen esas invasiones es "con la hipotesis de hoy, aqui no
    cabe", y la manera de quitarlas no es bajar el radio supuesto: es conseguir
    el dato.

    Lo que este test si vigila es que no haya invasiones de un keep-out que SI
    salga de un dato. El dia que llegue el radio de verdad, este test empieza a
    exigir de verdad sin que nadie lo toque.
    """
    hallazgos = [
        h for h in interference.invasion_keep_out(layout, piezas)
        if not h.basada_en_supuesto
    ]
    assert hallazgos == [], "\n".join(h.detalle for h in hallazgos)


def test_toda_invasion_de_keep_out_de_hoy_sale_de_un_supuesto(layout, piezas):
    """Contrapartida del anterior: que nada se cuele como 'supuesto' sin serlo."""
    for hallazgo in interference.invasion_keep_out(layout, piezas):
        assert hallazgo.basada_en_supuesto, hallazgo.detalle


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
    local = parts.caja_local(modulador)
    assert local is not None
    girada = assembly._localizar(
        parts.solido(modulador),
        Colocacion("m", 1, (0, 0, 0), (0, 0, 90), None, "m"),
    )
    bb = girada.BoundingBox()
    assert bb.xlen == pytest.approx(local.dims[1], abs=1e-6)
    assert bb.ylen == pytest.approx(local.dims[0], abs=1e-6)


def test_la_caja_del_modulador_es_mayor_que_su_cuerpo_de_ficha(catalogo):
    """El conector RF sobresale 10 mm, y esos 10 mm deciden la franja.

    La ficha de Exail acota el CUERPO (110 x 15 x 9.7 mm). Lo que tiene que ver
    el detector de interferencias no es el cuerpo: es la pieza con el conector
    puesto, porque el coaxial va a estar ahi.
    """
    from clau3d import parts

    modulador = catalogo["mod_intensidad_mxer_ln_10"]
    cuerpo = modulador.dimensiones.como_vector()
    caja = parts.caja_local(modulador)
    assert caja is not None
    # +10 mm por Y: el conector RF, que es dato del plano.
    assert caja.dims[1] == pytest.approx(cuerpo[1] + 10.0, abs=1e-6)
    # +20 mm por X: los protectores de fibra, (130 - 110) del mismo plano.
    assert caja.dims[0] == pytest.approx(
        modulador.extras["longitud_con_fibras"].escalar(), abs=1e-6
    )


# --- salirse de la zona asignada -------------------------------------------
#
# Las cinco zonas embaldosan la zona util, asi que salirse de la propia es
# meterse en la de al lado. Con la vecina vacia no hay solape todavia, y por eso
# el detector tiene que existir aparte: si no, el reparto se rompe en silencio
# hasta el dia que llegue la pieza que iba en ese hueco.

def test_una_pieza_fuera_de_su_zona_se_detecta_aunque_no_choque_con_nada(catalogo):
    from clau3d.analysis import interference
    from clau3d.assembly import Colocacion, Layout, PiezaColocada, Zona
    from clau3d.structure import Caja

    zona = Zona(id="z_prueba", nombre="Zona de prueba",
                caja=Caja(0, 0, 0, 50, 50, 50))
    vecina = Zona(id="z_vecina", nombre="Vecina",
                  caja=Caja(50, 0, 0, 100, 50, 50))
    layout = Layout(estado="propuesta", meta={}, zonas=[zona, vecina],
                    colocaciones=[], keep_outs=[])

    # Una caja de 20 mm centrada en x=45: asoma 15 mm en la zona vecina.
    caja = Caja.centrada((20.0, 20.0, 20.0), (45.0, 25.0, 25.0))
    pieza = PiezaColocada(
        colocacion=Colocacion(
            componente_id="x", instancia=1, centro=(45.0, 25.0, 25.0),
            rotacion=(0, 0, 0), zona="z_prueba", nombre="x",
        ),
        componente=None,
        solido=caja.solido(),
        caja_mundo=caja,
    )

    hallazgos = interference.fuera_de_su_zona(layout, [pieza])
    assert len(hallazgos) == 1, hallazgos
    assert hallazgos[0].tipo == "fuera_de_zona"
    assert hallazgos[0].b == "z_prueba"
    assert "5.0 mm" in hallazgos[0].detalle  # 45 + 10 = 55, o sea 5 mm fuera

    # Y una pieza que si cabe en su zona no da ningun hallazgo.
    dentro = Caja.centrada((20.0, 20.0, 20.0), (25.0, 25.0, 25.0))
    pieza_buena = PiezaColocada(
        colocacion=Colocacion(
            componente_id="y", instancia=1, centro=(25.0, 25.0, 25.0),
            rotacion=(0, 0, 0), zona="z_prueba", nombre="y",
        ),
        componente=None, solido=dentro.solido(), caja_mundo=dentro,
    )
    assert interference.fuera_de_su_zona(layout, [pieza_buena]) == []
