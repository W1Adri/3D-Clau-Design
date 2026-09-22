"""Conexiones: extremos existentes y holgura declarada."""

from clau3d.analysis import connections


def test_ninguna_conexion_apunta_a_un_componente_inexistente(catalogo, layout, piezas):
    fallos = [
        r for r in connections.comprobar(catalogo, layout, piezas) if r.critico
    ]
    assert fallos == [], "\n".join(f"{r.id}: {r.mensaje}" for r in fallos)


def test_la_cadena_de_fibra_esta_encadenada(catalogo):
    """Cada tramo empieza donde acaba el anterior, del laser al colimador.

    Solo eso: que este ENCADENADA. Que este en el ORDEN CORRECTO es otra cosa,
    y la comprueba 'orden_cadena_fibra' contra 'meta.restricciones_orden' --
    ver tests/test_cadena_optica.py. Fijar aqui una lista a mano es lo que hubo
    hasta el 2026-09-21, y lo que hacia era CONGELAR el orden equivocado: la
    lista decia que el aislador iba detras del codificador de polarizacion, que
    es donde borra la codificacion entera, y el test pasaba.
    """
    tramos = catalogo.tramos_de_fibra()
    for anterior, siguiente in zip(tramos, tramos[1:]):
        assert anterior["hasta"] == siguiente["desde"], (anterior, siguiente)
    assert tramos[0]["desde"] == "laser_dfb_1550"
    assert tramos[-1]["hasta"] == "colimador"


def test_la_fibra_del_beacon_es_una_cadena_aparte(catalogo):
    """Y tiene que estarlo declarada, no deducida de que no encaje.

    El beacon de bajada tiene fibra desde el 2026-09-21 -- su modulo esta en la
    bandeja y su colimador en el banco -- y esa fibra esta en 'opticas_fibra'
    como todo lo demas. Si no llevara 'cadena', los chequeos de orden la
    pegarian al final de la cadena del transmisor y diriamos que detras del
    colimador hay un modulo de beacon, que no es que sea falso: es que seria la
    clase de error que 3.10 existe para no repetir.
    """
    beacon = catalogo.tramos_de_fibra("beacon_bajada")
    assert [t["id"] for t in beacon] == ["f08"]
    assert beacon[0]["desde"] == "laser_beacon_bajada"
    assert beacon[0]["hasta"] == "colimador_beacon_bajada"
    # Y no se cuela en la del transmisor.
    assert "f08" not in {t["id"] for t in catalogo.tramos_de_fibra()}
    # Las dos juntas son todo lo que hay: ninguna cadena se queda sin declarar.
    todas = catalogo.conexiones["opticas_fibra"]
    assert len(catalogo.tramos_de_fibra()) + len(beacon) == len(todas)


def test_la_cadena_de_fibra_cumple_las_restricciones_declaradas(catalogo):
    """El orden, derivado de los datos y no de una lista escrita aqui."""
    from clau3d.analysis import fit

    chequeo = fit.chequeo_orden_cadena_fibra(catalogo)
    assert chequeo.estado == fit.OK, chequeo.mensaje


def test_el_camino_en_espacio_libre_llega_al_exterior(catalogo):
    tramos = catalogo.conexiones["opticas_espacio_libre"]
    assert any(t["hasta"] == "EXTERIOR" for t in tramos)
    # El brazo de los beacons y sus dos dicroicos estan en
    # tests/test_brazo_beacon.py, que es donde se comprueba entero.
    # El canal cuantico sale del colimador segun -Z y un espejo plano lo dobla
    # hacia la linea de D1: el colimador ya no apunta a D1 directamente.
    assert any(
        t["desde"] == "colimador" and t["hasta"] == "espejo_plegado_cuantico"
        for t in tramos
    )
    assert any(
        t["desde"] == "espejo_plegado_cuantico" and t["hasta"] == "dicroico_d1"
        for t in tramos
    )


def test_los_drivers_rf_salen_de_pcb2(catalogo):
    for tramo in catalogo.conexiones["rf_coaxial"]:
        assert tramo["desde"] == "pcb2_drivers_opticos", tramo


def test_el_eps_alimenta_a_todos_los_consumidores(catalogo):
    alimentados = {
        t["hasta"] for t in catalogo.conexiones["potencia"]
        if t["desde"] == "eps_starbuck_nano_plus"
    }
    consumidores = {
        c.id for c in catalogo.componentes
        if c.potencia_nominal.esta_declarada or c.potencia_pico.esta_declarada
    } - {"eps_starbuck_nano_plus", "paneles_photon_side", "qrng_idq20mc1_s3"}
    assert consumidores <= alimentados, consumidores - alimentados


def test_una_conexion_rota_se_detecta(catalogo, layout, piezas):
    catalogo.conexiones["datos"].append(
        {"id": "roto", "desde": "obc_kryten_m3_plus", "hasta": "no_existe", "tipo": "bus_datos"}
    )
    try:
        fallos = [r for r in connections.comprobar(catalogo, layout, piezas) if r.critico]
        assert any(r.id == "roto" for r in fallos)
    finally:
        catalogo.conexiones["datos"].pop()
