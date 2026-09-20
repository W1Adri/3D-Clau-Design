"""La compactacion del GLB no puede perder ni mover un triangulo.

Se comprueba con geometria inventada, por el mismo motivo que
``test_interferencias.py``: un test que solo mirase el ``clau_6u.glb`` de disco
pasaria o fallaria segun quien lo tenga generado, y el ensamblaje completo
tarda medio minuto en exportarse.

Lo que se verifica es lo unico que importa aqui: que salgan **los mismos
triangulos** — mismos vertices, en el mismo orden, con el mismo material — en
muchas menos primitivas.
"""

import numpy as np
import pytest

import cadquery as cq

from clau3d import gltf


def _triangulos(cabecera: dict, binario: bytes) -> dict[str, np.ndarray]:
    """Los triangulos de cada malla, ya resueltos a coordenadas."""
    salida = {}
    for malla in cabecera["meshes"]:
        trozos = []
        for prim in malla["primitives"]:
            pos = gltf._accesor(cabecera, binario, prim["attributes"]["POSITION"])
            idx = gltf._accesor(cabecera, binario, prim["indices"]).ravel()
            assert idx.max() < len(pos), "indice fuera de rango"
            trozos.append(pos[idx])
        salida[malla["name"]] = np.concatenate(trozos)
    return salida


@pytest.fixture(scope="module")
def original(tmp_path_factory):
    """Un ensamblaje de mentira, con una esfera para que haya caras curvas."""
    conjunto = cq.Assembly(name="prueba")
    conjunto.add(cq.Workplane().box(10, 20, 30), name="caja", color=cq.Color(1, 0, 0))
    conjunto.add(cq.Workplane().sphere(7), name="esfera", color=cq.Color(0, 1, 0))
    conjunto.add(
        cq.Workplane().cylinder(12, 4).translate((30, 0, 0)),
        name="cilindro",
        color=cq.Color(0, 0, 1),
    )
    ruta = tmp_path_factory.mktemp("gltf") / "prueba.glb"
    conjunto.export(str(ruta))
    return ruta


@pytest.fixture
def glb(original, tmp_path):
    """Copia intacta para cada test: ``compactar`` reescribe el fichero."""
    copia = tmp_path / original.name
    copia.write_bytes(original.read_bytes())
    return copia


def test_compactar_conserva_los_triangulos(glb):
    antes = _triangulos(*gltf._leer_glb(glb))
    parte = gltf.compactar(glb)
    despues = _triangulos(*gltf._leer_glb(glb))

    assert antes.keys() == despues.keys(), "se ha perdido o inventado una malla"
    for nombre in antes:
        np.testing.assert_allclose(antes[nombre], despues[nombre])
    assert parte["triangulos"] == sum(len(v) for v in antes.values()) // 3


def test_compactar_deja_una_primitiva_por_malla(glb):
    """Es todo el proposito: una llamada de dibujo por pieza, no una por cara."""
    cabecera, _ = gltf._leer_glb(glb)
    antes = {m["name"]: len(m["primitives"]) for m in cabecera["meshes"]}
    assert max(antes.values()) > 1, "el GLB de prueba ya venia con una sola cara"

    gltf.compactar(glb)
    cabecera, _ = gltf._leer_glb(glb)
    for malla in cabecera["meshes"]:
        materiales = {p.get("material") for p in malla["primitives"]}
        assert len(malla["primitives"]) == len(materiales)


def test_los_colores_siguen_donde_estaban(glb):
    """Fundir primitivas no puede mezclar dos materiales en uno."""
    antes, _ = gltf._leer_glb(glb)
    por_malla_antes = {
        m["name"]: {p.get("material") for p in m["primitives"]} for m in antes["meshes"]
    }
    colores_antes = [tuple(m["pbrMetallicRoughness"]["baseColorFactor"]) for m in antes["materials"]]

    gltf.compactar(glb)
    despues, _ = gltf._leer_glb(glb)
    por_malla_despues = {
        m["name"]: {p.get("material") for p in m["primitives"]} for m in despues["meshes"]
    }
    colores_despues = [
        tuple(m["pbrMetallicRoughness"]["baseColorFactor"]) for m in despues["materials"]
    ]

    assert por_malla_antes == por_malla_despues
    assert colores_antes == colores_despues


def test_position_lleva_min_y_max(glb):
    """glTF los exige en POSITION, y three.js los usa para la caja envolvente."""
    gltf.compactar(glb)
    cabecera, binario = gltf._leer_glb(glb)
    for malla in cabecera["meshes"]:
        for prim in malla["primitives"]:
            acc = cabecera["accessors"][prim["attributes"]["POSITION"]]
            pos = gltf._accesor(cabecera, binario, prim["attributes"]["POSITION"])
            np.testing.assert_allclose(acc["min"], pos.min(axis=0), rtol=1e-6)
            np.testing.assert_allclose(acc["max"], pos.max(axis=0), rtol=1e-6)


def test_el_glb_compactado_sigue_siendo_valido(glb):
    """Las bufferViews tienen que cubrir lo que los accesores dicen leer."""
    gltf.compactar(glb)
    cabecera, binario = gltf._leer_glb(glb)
    assert len(binario) >= cabecera["buffers"][0]["byteLength"]
    for acc in cabecera["accessors"]:
        vista = cabecera["bufferViews"][acc["bufferView"]]
        ancho = gltf._COMPONENTES[acc["type"]] * np.dtype(
            gltf._DTYPE[acc["componentType"]]
        ).itemsize
        fin = acc.get("byteOffset", 0) + acc["count"] * ancho
        assert fin <= vista["byteLength"], "accesor que se sale de su bufferView"
        # glTF exige que el desplazamiento respete el tamano del componente.
        assert acc.get("byteOffset", 0) % 4 == 0
