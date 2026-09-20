"""Conexiones: extremos existentes y holgura declarada."""

from clau3d.analysis import connections


def test_ninguna_conexion_apunta_a_un_componente_inexistente(catalogo, layout, piezas):
    fallos = [
        r for r in connections.comprobar(catalogo, layout, piezas) if r.critico
    ]
    assert fallos == [], "\n".join(f"{r.id}: {r.mensaje}" for r in fallos)


def test_la_cadena_de_fibra_esta_completa(catalogo):
    """El camino laser -> ... -> colimador tiene que estar encadenado."""
    tramos = catalogo.conexiones["opticas_fibra"]
    esperado = [
        "laser_dfb_1550", "mod_intensidad_mxer_ln_10", "mod_fase_mpz_ln_10",
        "voa", "aislador", "filtro_espectral", "acoplador_monitor", "colimador",
    ]
    cadena = [tramos[0]["desde"]] + [t["hasta"] for t in tramos]
    assert cadena == esperado


def test_el_camino_en_espacio_libre_llega_al_exterior(catalogo):
    tramos = catalogo.conexiones["opticas_espacio_libre"]
    assert any(t["hasta"] == "EXTERIOR" for t in tramos)
    assert any(
        t["desde"] == "dicroico" and t["hasta"] == "camara_beacon" for t in tramos
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
