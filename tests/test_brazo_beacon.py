"""El brazo compartido de los dos beacons: cadena cerrada, y que quepa o no.

Tres cosas, y las tres existen por un fallo concreto que estuvo en el modelo
hasta el 2026-09-20:

1. **La cadena optica tiene que estar CERRADA.** `laser_beacon_bajada` estaba
   en el catalogo y colocado en el layout, y no tenia NI UNA conexion
   declarada: emitia contra la cara trasera de D1, sin camino hacia el
   FSM. No habia ningun test que pudiera cazarlo, porque los que habia miraban
   que los extremos declarados existieran, no que las piezas declaradas
   tuvieran extremos. Este si.

2. **Un chequeo geometrico tiene que fallar de verdad.** `chequeo_brazo_beacon`
   hoy falla con el catalogo del repositorio, pero eso no demuestra nada del
   mecanismo: manana alguien alarga el banco y pasaria a dar OK sin que nadie
   supiera si sigue sabiendo fallar. Se comprueba con geometria inventada, por
   el mismo motivo que `test_interferencias.py` comprueba los detectores con
   solapes inventados.

3. **El renombrado del id viejo a `dicroico_d1` no puede dejar huerfanos.**
   Un id que ya no existe referenciado desde el layout, las conexiones o el
   codigo no da error hasta que alguien mira el sitio exacto.
"""

from __future__ import annotations

import re
from pathlib import Path

from clau3d import assembly
from clau3d.analysis import fit
from clau3d.datamodel import RAIZ, SUPUESTO, Catalogo, Magnitud, _componente
from clau3d.structure import Caja

# Los dos dicroicos son los unicos nodos de cuatro puertos del camino en
# espacio libre, y son justo donde se pierde un beacon si alguien se despista.
DICROICOS = ("dicroico_d1", "dicroico_d2")


def _tramos(catalogo: Catalogo) -> list[dict]:
    return catalogo.conexiones["opticas_espacio_libre"]


# ------------------------------------------- 1. la cadena optica esta cerrada
def test_cada_pieza_del_camino_libre_tiene_conexion_declarada(catalogo):
    """Ninguna pieza del banco se queda sin camino optico.

    Este es EL test que faltaba: 'laser_beacon_bajada' existia, se dibujaba y
    no iba conectado a nada.
    """
    conectadas: set[str] = set()
    for tramo in _tramos(catalogo):
        conectadas.update({tramo["desde"], tramo["hasta"]})

    # Las piezas del terminal optico que viven en espacio libre. La cadena de
    # fibra tiene la suya, y el colimador es la frontera entre las dos.
    en_espacio_libre = {
        c.id
        for c in catalogo.componentes
        if c.subsistema == "terminal_optico"
        and c.cuenta_en_presupuesto
        and c.id != "colimador"
    }
    sueltas = sorted(en_espacio_libre - conectadas)
    assert not sueltas, (
        f"piezas del camino en espacio libre sin ninguna conexion declarada: "
        f"{', '.join(sueltas)}. Una pieza optica que no esta en "
        f"data/connections.yaml no tiene camino: se dibuja, pero no funciona."
    )


def test_los_puertos_declarados_de_cada_divisor_tienen_destino(catalogo):
    """Lo que dice 'puertos' en el catalogo y lo que hay en connections.yaml.

    Un divisor a 45 grados tiene CUATRO puertos, existan o no en el dibujo.
    El catalogo los declara uno a uno con el tramo que va por cada uno; aqui se
    comprueba que ese tramo existe de verdad y toca a esa pieza. Si alguien
    anade un puerto sin conexion, o quita una conexion sin quitar el puerto,
    esto salta.
    """
    por_pieza: dict[str, set[str]] = {}
    for tramo in _tramos(catalogo):
        for extremo in ("desde", "hasta"):
            por_pieza.setdefault(tramo[extremo], set()).add(tramo["id"])

    for cid in DICROICOS:
        puertos = catalogo[cid].extras["puertos"].valor
        declarados = set()
        for puerto in puertos:
            ids = re.findall(r"\be\d{2}\b", puerto)
            assert ids, f"{cid}: el puerto {puerto!r} no nombra ningun tramo"
            declarados.update(ids)
        reales = por_pieza.get(cid, set())
        assert declarados == reales, (
            f"{cid}: 'puertos' declara {sorted(declarados)} y "
            f"data/connections.yaml tiene {sorted(reales)}"
        )


def test_el_beacon_de_bajada_llega_al_exterior(catalogo):
    """Del MODULO al EXTERIOR siguiendo los tramos, fibra incluida.

    Arranca en 'laser_beacon_bajada', que desde el 2026-09-21 es solo el modulo
    y vive en la bandeja, asi que el primer salto ya no es en espacio libre
    sino por fibra (f08). Se recorren las dos familias a proposito: partir la
    pieza en dos no puede romper el camino, y si alguien se dejara f08 sin
    declarar la pieza quedaria suelta en la bandeja y nadie se enteraria.
    """
    salto: dict[str, set[str]] = {}
    for tramo in _tramos(catalogo) + list(catalogo.conexiones["opticas_fibra"]):
        salto.setdefault(tramo["desde"], set()).add(tramo["hasta"])

    vistos = {"laser_beacon_bajada"}
    pendientes = ["laser_beacon_bajada"]
    while pendientes:
        actual = pendientes.pop()
        for siguiente in salto.get(actual, ()):
            if siguiente not in vistos:
                vistos.add(siguiente)
                pendientes.append(siguiente)
    assert "EXTERIOR" in vistos, (
        f"el beacon de bajada no llega a salir del satelite; alcanza {vistos}"
    )
    for eslabon in (
        "colimador_beacon_bajada", "dicroico_d2", "dicroico_d1", "fsm",
        "telescopio_cassegrain",
    ):
        assert eslabon in vistos, f"el beacon de bajada no pasa por {eslabon}"


def test_el_beacon_de_subida_llega_a_la_camara(catalogo):
    tramos = _tramos(catalogo)
    assert any(
        t["desde"] == "dicroico_d1" and t["hasta"] == "dicroico_d2" for t in tramos
    )
    assert any(
        t["desde"] == "dicroico_d2" and t["hasta"] == "camara_beacon" for t in tramos
    )


def test_los_cuartos_puertos_tienen_donde_acabar(catalogo):
    """Fuga del 1550 en D1 y fuga del beacon en D2, cada una a su sitio."""
    destinos = {
        (t["desde"], t["hasta"]) for t in _tramos(catalogo)
    }
    assert ("dicroico_d1", "trampa_luz_d1") in destinos
    assert ("dicroico_d2", "fotodiodo_monitor_beacon") in destinos


def test_el_tramo_de_ida_y_vuelta_no_duplica_su_keep_out(catalogo, layout):
    """El tramo de bajada recorre el mismo tubo que el de subida, y el volumen
    se declara una vez.

    Los ids no se escriben aqui: se buscan por los extremos. El camino en
    espacio libre se renumero el 2026-09-21 al meter el espejo de plegado, y un
    test que fijara 'e04' habria fallado por el motivo equivocado.
    """
    tramos = _tramos(catalogo)
    subida = next(
        t for t in tramos
        if t["desde"] == "dicroico_d1" and t["hasta"] == "dicroico_d2"
    )
    bajada = next(
        t for t in tramos
        if t["desde"] == "dicroico_d2" and t["hasta"] == "dicroico_d1"
    )
    assert bajada.get("keep_out") is False
    assert bajada["keep_out_compartido_con"] == subida["id"]
    assert subida.get("keep_out") is True
    # Y en el layout hay uno, no dos.
    ids = [k.id for k in layout.keep_outs]
    assert f"haz_{subida['id']}" in ids
    assert f"haz_{bajada['id']}" not in ids


def test_la_trampa_de_d2_es_excluyente_con_el_fotodiodo(catalogo, layout):
    """El cuarto puerto de D2 es uno solo: o se instrumenta o se tapa."""
    trampa = catalogo["trampa_luz_d2"]
    assert trampa.alternativa_de == "fotodiodo_monitor_beacon"
    assert not trampa.cuenta_en_presupuesto
    colocadas = {c.componente_id for c in layout.colocaciones}
    assert "trampa_luz_d2" not in colocadas


# --------------------------------- 2. el chequeo sabe fallar de verdad
def _pieza(cid: str, dims: list[float]) -> dict:
    return {
        "id": cid, "nombre": cid, "categoria": "payload_optico",
        "subsistema": "terminal_optico",
        "forma": {
            "tipo": "caja",
            "dimensiones": {
                "valor": dims, "unidad": "mm", "estado": SUPUESTO,
                "fuente": "geometria de prueba", "falta": "la de verdad",
                "pedir_a": "nadie",
            },
        },
        "masa": {
            "valor": None, "estado": "TBD", "falta": "algo", "pedir_a": "alguien",
        },
    }


# La topologia de prueba, con la camara en +Y: NO es la del modelo real, que
# la tiene en -X. Es a proposito -- lo que se comprueba aqui es el mecanismo,
# no el reparto de hoy -- y ademas es lo que hace util
# 'test_el_chequeo_lee_la_topologia_declarada': si el chequeo volviera a tener
# las ramas escritas dentro, mediria la del modelo y no esta.
TOPOLOGIA_DE_PRUEBA = [
    {"estacion": "dicroico_d1", "cara": "+Y",
     "piezas": ["dicroico_d2", "camara_beacon"]},
    {"estacion": "dicroico_d1", "cara": "-Y", "piezas": ["trampa_luz_d1"]},
    {"estacion": "dicroico_d2", "cara": "-X",
     "piezas": ["laser_beacon_bajada"]},
    {"estacion": "dicroico_d2", "cara": "+X",
     "piezas": ["fotodiodo_monitor_beacon"]},
]


def _catalogo_de_brazo(
    camara: float, d2: float = 20.0, topologia=None
) -> Catalogo:
    return Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={}, integracion={},
        componentes=[
            _componente(_pieza("dicroico_d1", [20.0, 20.0, 20.0])),
            _componente(_pieza("dicroico_d2", [d2, d2, d2])),
            _componente(_pieza("camara_beacon", [camara, camara, camara])),
            _componente(_pieza("trampa_luz_d1", [10.0, 10.0, 10.0])),
            _componente(_pieza("laser_beacon_bajada", [20.0, 20.0, 20.0])),
            _componente(_pieza("fotodiodo_monitor_beacon", [10.0, 10.0, 10.0])),
            _componente(_pieza("fsm", [20.0, 20.0, 20.0])),
        ],
        conexiones={
            "meta": {
                "topologia_brazo_beacons": (
                    TOPOLOGIA_DE_PRUEBA if topologia is None else topologia
                )
            }
        },
    )


class _LayoutDePrueba:
    """Lo justo que 'chequeo_brazo_beacon' le pide a un layout."""

    def __init__(self, semi_y: float):
        self.zonas = [
            assembly.Zona(
                id="z_payload_banco", nombre="banco",
                caja=Caja(-100.0, -semi_y, -50.0, 100.0, semi_y, 0.0),
            ),
            assembly.Zona(
                id="z_payload_telescopio", nombre="telescopio",
                caja=Caja(-50.0, -semi_y, 0.0, 50.0, semi_y, 100.0),
            ),
        ]
        self.colocaciones = []


def test_el_chequeo_del_brazo_falla_cuando_no_cabe():
    """Geometria inventada que no entra: el chequeo tiene que decirlo."""
    # 10 (semi D1) + 20 (D2) + 40 (camara) = 70 mm contra 50 de pared.
    chequeo = fit.chequeo_brazo_beacon(
        _catalogo_de_brazo(camara=40.0), _LayoutDePrueba(semi_y=50.0)
    )
    assert chequeo.estado == fit.FALLA, chequeo.mensaje
    assert chequeo.critico
    assert chequeo.numeros["margen_+Y_mm"] < 0
    assert "20.0" in chequeo.mensaje or "NO CABE" in chequeo.mensaje


def test_el_chequeo_del_brazo_pasa_cuando_cabe():
    """Y con sitio de sobra tiene que decir que si: un chequeo que siempre
    falla no informa de nada."""
    # 10 + 20 + 15 = 45 mm contra 100 de pared.
    chequeo = fit.chequeo_brazo_beacon(
        _catalogo_de_brazo(camara=15.0), _LayoutDePrueba(semi_y=100.0)
    )
    assert chequeo.estado == fit.OK, chequeo.mensaje


def test_el_chequeo_del_brazo_se_mueve_con_la_reserva_de_la_camara():
    """Si el margen estuviera escrito a mano en vez de derivado, esto lo caza."""
    layout = _LayoutDePrueba(semi_y=60.0)
    ancha = fit.chequeo_brazo_beacon(_catalogo_de_brazo(camara=40.0), layout)
    estrecha = fit.chequeo_brazo_beacon(_catalogo_de_brazo(camara=20.0), layout)
    assert (
        estrecha.numeros["margen_+Y_mm"] - ancha.numeros["margen_+Y_mm"]
        == 20.0
    )


def _generador():
    """tools/generar_layout.py cargado como modulo.

    No es un paquete instalado -- es un script de la raiz del repositorio --,
    asi que se carga por ruta. Merece la pena: es el unico sitio donde se puede
    comprobar que el generador y el chequeo leen LA MISMA topologia, que es
    justamente lo que fallo el 2026-09-21.
    """
    import importlib.util

    ruta = RAIZ / "tools" / "generar_layout.py"
    spec = importlib.util.spec_from_file_location("_generar_layout", ruta)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_el_chequeo_lee_la_topologia_declarada():
    """Cambiar la topologia en los DATOS tiene que mover el chequeo.

    Es el test que faltaba. Hasta el 2026-09-21 las ramas estaban escritas dos
    veces -- RAMAS_BRAZO en el generador y a mano dentro del chequeo -- y al
    invertir D2 las dos dejaron de decir lo mismo: el generador colocaba la
    camara en -X y el chequeo seguia midiendola en +Y, o sea comprobando una
    geometria que ya no existia. Si alguien vuelve a escribirlas dentro del
    codigo, esto falla.
    """
    layout = _LayoutDePrueba(semi_y=60.0)
    # Con la camara en +Y esa rama pide 10 (semi D1) + 20 (D2) + 40 = 70.
    en_mas_y = fit.chequeo_brazo_beacon(_catalogo_de_brazo(camara=40.0), layout)
    assert en_mas_y.numeros["necesario_+Y_mm"] == 70.0
    assert "camara_beacon_mm" in en_mas_y.numeros

    # Movida a -X desde D2, la rama +Y se queda solo con D2: 10 + 20 = 30.
    movida = [
        {"estacion": "dicroico_d1", "cara": "+Y", "piezas": ["dicroico_d2"]},
        {"estacion": "dicroico_d1", "cara": "-Y", "piezas": ["trampa_luz_d1"]},
        {"estacion": "dicroico_d2", "cara": "-X", "piezas": ["camara_beacon"]},
        {"estacion": "dicroico_d2", "cara": "+X",
         "piezas": ["fotodiodo_monitor_beacon"]},
    ]
    en_menos_x = fit.chequeo_brazo_beacon(
        _catalogo_de_brazo(camara=40.0, topologia=movida), layout
    )
    assert en_menos_x.numeros["necesario_+Y_mm"] == 30.0
    assert en_menos_x.numeros["necesario_-X_mm"] == 50.0
    assert en_menos_x.numeros["margen_+Y_mm"] > en_mas_y.numeros["margen_+Y_mm"]


def test_el_generador_usa_la_misma_topologia_que_el_chequeo():
    """Y no una copia suya: las dos salen de data/connections.yaml.

    Se le da al generador una topologia inventada y se comprueba que coloca por
    ella. Junto con el test de arriba, esto ata los dos lados al mismo dato:
    reescribir las ramas en cualquiera de los dos sitios rompe uno de los dos.
    """
    generar = _generador()

    catalogo = _catalogo_de_brazo(camara=10.0)
    # D1 ya colocado en el origen; el resto cuelga de el.
    colocaciones = [{
        "componente": "dicroico_d1", "instancia": 1,
        "centro": [0.0, 0.0, 0.0], "rotacion": [0, 0, 0],
        "zona": "z_payload_banco",
    }]
    puestas, sin_sitio = generar._ramas_del_brazo(
        catalogo, colocaciones, ([-100.0, -100.0, -50.0], [100.0, 100.0, 0.0])
    )
    assert sin_sitio == []
    por_id = {c["componente"]: c["centro"] for c in puestas}
    # La topologia de prueba pone la camara en +Y detras de D2, no en -X.
    assert por_id["camara_beacon"][1] > 0
    assert por_id["camara_beacon"][0] == 0.0
    # Y el laser en -X desde D2.
    assert por_id["laser_beacon_bajada"][0] < 0


def test_sin_topologia_declarada_el_chequeo_no_es_concluyente():
    """Un chequeo sin datos sale como no comprobable, nunca como ok."""
    catalogo = _catalogo_de_brazo(camara=20.0, topologia=[])
    chequeo = fit.chequeo_brazo_beacon(catalogo, _LayoutDePrueba(semi_y=100.0))
    assert chequeo.estado == fit.NO_COMPROBABLE


def test_sin_dicroicos_el_chequeo_no_es_concluyente():
    catalogo = Catalogo(
        meta={}, norma={}, envolvente={}, zona_util={}, integracion={},
        componentes=[], conexiones={},
    )
    chequeo = fit.chequeo_brazo_beacon(catalogo, _LayoutDePrueba(semi_y=50.0))
    assert chequeo.estado == fit.NO_COMPROBABLE


def test_sin_layout_el_chequeo_no_es_concluyente():
    chequeo = fit.chequeo_brazo_beacon(_catalogo_de_brazo(camara=20.0), None)
    assert chequeo.estado == fit.NO_COMPROBABLE


# -------------------------------------- 3. el renombrado no dejo huerfanos
# Ficheros donde un id de componente significa un id de componente. La
# documentacion en prosa (CLAUDE.md, README) queda fuera a proposito: alli
# el nombre comun no es una referencia a ningun id.
FICHEROS = (
    sorted((RAIZ / "data").glob("*.yaml"))
    + sorted((RAIZ / "src").rglob("*.py"))
    + sorted((RAIZ / "tools").glob("*.py"))
    + sorted((RAIZ / "tests").glob("*.py"))
)


def test_no_queda_ninguna_referencia_al_id_viejo():
    """Ni en los datos, ni en el codigo, ni en los propios tests.

    La regla es dura a proposito: el token a secas no aparece, ni siquiera en
    un comentario. En cuanto hay dos, un id llamado asi deja de ser univoco, y
    una frase que lo use en singular deja de decir cual de los dos. Valen
    'dicroico_d1', 'dicroico_d2', el plural y la palabra 'divisor'.
    """
    # Construido por partes a proposito, para que este fichero no
    # incumpla su propia regla.
    patron = re.compile(r"\b" + "dicro" + "ico" + r"\b")
    culpables = []
    for fichero in FICHEROS:
        for numero, linea in enumerate(
            fichero.read_text().splitlines(), start=1
        ):
            if patron.search(linea):
                culpables.append(
                    f"{fichero.relative_to(RAIZ)}:{numero}: {linea.strip()}"
                )
    assert not culpables, (
        "quedan referencias al id viejo, que ya no existe:\n"
        + "\n".join(culpables)
    )


def test_todo_lo_que_el_layout_coloca_existe_en_el_catalogo(catalogo, layout):
    """Un renombrado a medias deja el layout apuntando a un id inexistente."""
    for colocacion in layout.colocaciones:
        assert catalogo.existe(colocacion.componente_id), colocacion.componente_id
    for keep_out in layout.keep_outs:
        de_pieza = getattr(keep_out, "de_pieza", None)
        if de_pieza:
            assert catalogo.existe(de_pieza), de_pieza
