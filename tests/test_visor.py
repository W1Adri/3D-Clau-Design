"""La escena del visor tiene que decir lo mismo que el catalogo, y decirlo entero.

El visor es la cara visible del modelo: si aqui se pierde un TBD o se redondea
una cifra por su cuenta, se estaria ensenando algo que el catalogo no dice.
"""

import json
import struct

import pytest

from clau3d import parts, viewer
from clau3d.analysis import volume
from clau3d.datamodel import TBD


@pytest.fixture(scope="module")
def escena(catalogo, layout, piezas):
    return viewer.escena(catalogo, layout, piezas)


def test_la_escena_es_json_de_verdad(escena):
    """Nada de objetos del YAML colados: tiene que serializar sin ayuda."""
    json.dumps(escena, ensure_ascii=False)


def test_hay_una_entrada_por_pieza_colocada(escena, piezas):
    assert len(escena["piezas"]) == len(piezas)
    nodos = [p["nodo"] for p in escena["piezas"]]
    assert len(set(nodos)) == len(nodos), "dos piezas con el mismo nodo"


def test_las_zonas_salen_enteras_del_layout(escena, layout):
    assert [z["id"] for z in escena["zonas"]] == [z.id for z in layout.zonas]


def test_los_componentes_sin_envolvente_se_declaran(escena, catalogo):
    """Los 19 sin geometria no pueden desaparecer del visor sin mas."""
    esperados = {c.id for c in parts.no_modelables(catalogo)}
    assert {c["componente"] for c in escena["sin_geometria"]} == esperados


def test_un_tbd_llega_al_visor_como_tbd(escena, catalogo):
    """Ni valor inventado ni hueco silencioso: TBD con valor nulo."""
    vistos = 0
    for fila in escena["piezas"]:
        for nombre, magnitud in fila["magnitudes"].items():
            if magnitud["estado"] == TBD:
                assert magnitud["valor"] is None, f"{fila['nodo']}.{nombre}"
                assert magnitud["falta"], f"{fila['nodo']}.{nombre} sin 'falta'"
                vistos += 1
    assert vistos, "el catalogo tiene TBD; el visor no ensena ninguno"


def test_las_discrepancias_se_ensenan_sin_elegir(escena):
    """Cuando dos fuentes no coinciden, el visor lleva las dos."""
    con_alternativas = [
        m
        for fila in escena["piezas"]
        for m in fila["magnitudes"].values()
        if m["discrepancia"]
    ]
    assert con_alternativas, "el catalogo tiene discrepancias; el visor no las pasa"


def test_el_volumen_libre_se_marca_como_no_fiable(escena):
    """Con envolventes que faltan, el hueco libre es un techo, no una cifra."""
    assert escena["resumen"]["fiable"] is False
    assert escena["resumen"]["sin_envolvente"]


def test_el_volumen_coincide_con_el_analisis(escena, catalogo, piezas):
    resumen = volume.resumen(catalogo, piezas)
    assert escena["resumen"]["volumen_libre_l"] == pytest.approx(
        volume.a_litros(resumen.libre_mm3)
    )
    assert escena["resumen"]["volumen_interior_l"] == pytest.approx(
        volume.a_litros(catalogo.volumen_interior_mm3)
    )


def test_los_chequeos_no_comprobables_siguen_siendolo(escena):
    """El visor no puede ascender un 'no comprobable' a 'ok'."""
    estados = {c["estado"] for c in escena["chequeos"]}
    assert estados <= {"ok", "atencion", "falla", "no comprobable"}
    assert "no comprobable" in estados


def test_exportar_deja_glb_y_json(tmp_path):
    glb, js = viewer.exportar(tmp_path)
    assert glb.exists() and js.exists()
    assert glb.read_bytes()[:4] == b"glTF", "el GLB no tiene cabecera glTF"
    json.loads(js.read_text(encoding="utf-8"))


def test_cada_pieza_tiene_su_nodo_en_el_glb(tmp_path, escena):
    """Si el GLB y el JSON dejan de hablar del mismo nodo, el visor miente.

    Es el fallo que se cuela solo: basta renombrar una colocacion para que la
    lista del panel deje de corresponder con lo que se ve.
    """
    glb, _ = viewer.exportar(tmp_path)
    crudo = glb.read_bytes()
    largo_json = struct.unpack("<I", crudo[12:16])[0]
    gltf = json.loads(crudo[20 : 20 + largo_json])
    nombres = {n.get("name") for n in gltf["nodes"]}
    for pieza in escena["piezas"]:
        assert pieza["nodo"] in nombres, f"{pieza['nodo']} no esta en el GLB"


def test_el_visor_estatico_esta_donde_lo_busca_el_servidor():
    for nombre in ("index.html", "visor.css", "visor.js"):
        assert (viewer.DIR_VISOR / nombre).exists(), nombre


# --- las salidas para el equipo -------------------------------------------

def test_el_csv_de_estado_tiene_una_fila_por_componente(catalogo, layout, piezas):
    """Incluidas las que no tienen geometria: lo que falta tambien es estado."""
    import csv
    import io

    from clau3d import report

    filas = list(csv.DictReader(io.StringIO(
        report.csv_estado(catalogo, layout, piezas)
    )))
    assert len(filas) == len(catalogo.componentes)
    assert {f["id"] for f in filas} == {c.id for c in catalogo.componentes}


def test_el_csv_no_llama_dato_a_un_supuesto(catalogo, layout, piezas):
    import csv
    import io

    from clau3d import report
    from clau3d.datamodel import SUPUESTO

    filas = {
        f["id"]: f
        for f in csv.DictReader(io.StringIO(
            report.csv_estado(catalogo, layout, piezas)
        ))
    }
    for componente in catalogo.componentes:
        assert filas[componente.id]["estado_cotas"] == componente.dimensiones.estado
        if componente.dimensiones.estado == SUPUESTO:
            # Un supuesto siempre dice que falta y a quien pedirselo, tambien
            # en la hoja que va a acabar en Drive.
            assert filas[componente.id]["que_falta"], componente.id
            assert filas[componente.id]["pedir_a"], componente.id


def test_los_id_de_drive_no_se_repiten(catalogo):
    """Dos piezas con el mismo id_drive pisarian la misma fila de la hoja."""
    vistos = [c.id_drive for c in catalogo.componentes if c.id_drive]
    assert len(vistos) == len(set(vistos)), sorted(vistos)


def test_un_step_de_subsistema_con_cad_de_fabricante_se_llama_distinto(
    catalogo, layout, tmp_path
):
    """El repositorio es publico: el nombre tiene que delatar lo que lleva dentro.

    Y el sufijo lo pone el exportador mirando lo que ha metido, no una lista
    escrita a mano que se quedaria obsoleta con el siguiente STEP de proveedor.
    """
    from clau3d import assembly, parts

    escritos = assembly.exportar_por_subsistema(catalogo, layout, tmp_path)
    for subsistema, ruta in escritos.items():
        lleva_fabricante = any(
            parts.step_disponible(p.componente)  # type: ignore[arg-type]
            for p in assembly.construir(catalogo, layout)
            if getattr(p.componente, "subsistema", "") == subsistema
        )
        marcado = assembly.SUFIJO_CAD_DE_FABRICANTE in ruta.name
        assert marcado == lleva_fabricante, ruta.name


def test_el_gitignore_conoce_el_sufijo():
    """Cambiarlo en assembly.py sin cambiarlo aqui publicaria CAD de AAC."""
    from clau3d import assembly
    from clau3d.datamodel import RAIZ

    texto = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert assembly.SUFIJO_CAD_DE_FABRICANTE in texto
