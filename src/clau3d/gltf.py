"""Compactacion del GLB que exporta CadQuery, para que el navegador lo aguante.

OpenCASCADE escribe **una primitiva de glTF por cara del BREP**. Es correcto y
es lo que quiere un traductor de CAD, pero para un visor de tiempo real es la
peor forma posible de entregar la geometria: GLTFLoader crea una malla de
three.js por primitiva, y cada malla es una llamada de dibujo por fotograma.

El ensamblaje de CLAU sale con **38 738 primitivas** para solo 862 000
triangulos. La tarjeta grafica se rie de 862 000 triangulos; con 38 738 llamadas
de dibujo se atraganta. Y el indice de esas primitivas ocupa **18 MB de JSON**
en un fichero de 46 MB: antes de dibujar nada, el navegador ya ha tenido que
analizar 116 000 accesores.

Aqui se funden las primitivas de cada malla en una sola por material. No cambia
ni un vertice: son exactamente los mismos triangulos, agrupados de otra manera.

Es puro transporte, no modelo. El STEP del ensamblaje se exporta aparte y se
queda como esta: ahi cada cara *debe* seguir siendo una cara.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

# Tipos de componente de glTF que aparecen en lo que escribe OpenCASCADE.
_DTYPE = {
    5120: np.int8, 5121: np.uint8, 5122: np.int16,
    5123: np.uint16, 5125: np.uint32, 5126: np.float32,
}
_COMPONENTES = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
# Lo unico que escribe OpenCASCADE para un ensamblaje sin texturas. Si algun dia
# apareciera otro atributo (UV, color por vertice), fundir a ciegas lo perderia
# sin decir nada, asi que se para: antes un error que una pieza mal dibujada.
_ATRIBUTOS = {"POSITION", "NORMAL"}
_FLOAT = 5126
_UINT32 = 5125
_ARRAY_BUFFER = 34962
_ELEMENT_ARRAY_BUFFER = 34963
_JSON = 0x4E4F534A
_BIN = 0x004E4942


class ErrorDeGLB(Exception):
    """El GLB no tiene la forma que este modulo sabe compactar."""


def _leer_glb(ruta: Path) -> tuple[dict, bytes]:
    datos = ruta.read_bytes()
    magico, version, _total = struct.unpack("<III", datos[:12])
    if magico != 0x46546C67:
        raise ErrorDeGLB(f"{ruta}: no es un GLB")
    if version != 2:
        raise ErrorDeGLB(f"{ruta}: version de glTF {version}, se esperaba 2")

    cabecera: dict | None = None
    binario = b""
    pos = 12
    while pos < len(datos):
        largo, clase = struct.unpack("<II", datos[pos:pos + 8])
        cuerpo = datos[pos + 8:pos + 8 + largo]
        if clase == _JSON:
            cabecera = json.loads(cuerpo)
        elif clase == _BIN:
            binario = cuerpo
        pos += 8 + largo + (-largo % 4)
    if cabecera is None:
        raise ErrorDeGLB(f"{ruta}: sin bloque JSON")
    return cabecera, binario


def _escribir_glb(ruta: Path, cabecera: dict, binario: bytes) -> None:
    texto = json.dumps(cabecera, separators=(",", ":")).encode("utf-8")
    texto += b" " * (-len(texto) % 4)
    binario += b"\0" * (-len(binario) % 4)
    total = 12 + 8 + len(texto) + 8 + len(binario)
    with ruta.open("wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(texto), _JSON))
        f.write(texto)
        f.write(struct.pack("<II", len(binario), _BIN))
        f.write(binario)


def _accesor(cabecera: dict, binario: bytes, indice: int) -> np.ndarray:
    """Lee un accesor entero como array de numpy, respetando byteStride."""
    acc = cabecera["accessors"][indice]
    if "bufferView" not in acc:
        raise ErrorDeGLB("accesor sin bufferView: no se sabe compactar")
    if acc.get("sparse"):
        raise ErrorDeGLB("accesor disperso: no se sabe compactar")

    vista = cabecera["bufferViews"][acc["bufferView"]]
    dtype = np.dtype(_DTYPE[acc["componentType"]]).newbyteorder("<")
    ancho = _COMPONENTES[acc["type"]]
    inicio = vista.get("byteOffset", 0) + acc.get("byteOffset", 0)
    paso = vista.get("byteStride") or dtype.itemsize * ancho

    if paso == dtype.itemsize * ancho:  # compacto: una lectura y ya
        n = acc["count"] * ancho
        plano = np.frombuffer(binario, dtype=dtype, count=n, offset=inicio)
        return plano.reshape(acc["count"], ancho)

    bruto = np.frombuffer(binario, dtype=np.uint8, count=paso * acc["count"], offset=inicio)
    util = bruto.reshape(acc["count"], paso)[:, : dtype.itemsize * ancho]
    return np.ascontiguousarray(util).view(dtype).reshape(acc["count"], ancho)


def compactar(ruta: Path) -> dict:
    """Funde en sitio las primitivas de cada malla por material.

    Devuelve un pequeno parte de lo que ha cambiado, para poder decirlo por
    pantalla en vez de que el ahorro sea invisible.
    """
    cabecera, binario = _leer_glb(ruta)
    antes = {
        "bytes": ruta.stat().st_size,
        "primitivas": sum(len(m.get("primitives", [])) for m in cabecera.get("meshes", [])),
        "accesores": len(cabecera.get("accessors", [])),
    }

    posiciones: list[np.ndarray] = []
    normales: list[np.ndarray] = []
    indices: list[np.ndarray] = []
    accesores: list[dict] = []
    mallas: list[dict] = []

    # Se acumulan por separado para que cada atributo acabe en su propia
    # bufferView, que es lo que esperan los cargadores.
    n_pos = n_nor = n_idx = 0

    for malla in cabecera.get("meshes", []):
        grupos: dict[int | None, list[dict]] = {}
        for prim in malla.get("primitives", []):
            if prim.get("mode", 4) != 4:
                raise ErrorDeGLB(f"{malla.get('name')}: primitiva que no es de triangulos")
            grupos.setdefault(prim.get("material"), []).append(prim)

        nuevas = []
        for material, prims in grupos.items():
            atributos = {tuple(sorted(p["attributes"])) for p in prims}
            if len(atributos) != 1:
                raise ErrorDeGLB(f"{malla.get('name')}: primitivas con atributos distintos")
            sobra = set(next(iter(atributos))) - _ATRIBUTOS
            if sobra:
                raise ErrorDeGLB(
                    f"{malla.get('name')}: atributos que no se saben fundir: {sorted(sobra)}"
                )

            vertices: list[np.ndarray] = []
            vector_n: list[np.ndarray] = []
            triangulos: list[np.ndarray] = []
            desplazamiento = 0
            for prim in prims:
                pos = _accesor(cabecera, binario, prim["attributes"]["POSITION"])
                vertices.append(pos)
                if "NORMAL" in prim["attributes"]:
                    vector_n.append(_accesor(cabecera, binario, prim["attributes"]["NORMAL"]))
                if "indices" in prim:
                    idx = _accesor(cabecera, binario, prim["indices"]).ravel()
                else:  # sin indices: los triangulos van en orden
                    idx = np.arange(len(pos), dtype=np.uint32)
                triangulos.append(idx.astype(np.uint32) + desplazamiento)
                desplazamiento += len(pos)

            pos = np.concatenate(vertices).astype(np.float32, copy=False)
            idx = np.concatenate(triangulos)

            atributos_nuevos = {"POSITION": len(accesores)}
            accesores.append({
                "bufferView": 0,
                "byteOffset": n_pos * 12,
                "componentType": _FLOAT,
                "count": len(pos),
                "type": "VEC3",
                # POSITION exige min/max; three.js los usa para la caja envolvente.
                "min": [float(v) for v in pos.min(axis=0)],
                "max": [float(v) for v in pos.max(axis=0)],
            })
            posiciones.append(pos)

            if vector_n:
                nor = np.concatenate(vector_n).astype(np.float32, copy=False)
                if len(nor) != len(pos):
                    raise ErrorDeGLB(f"{malla.get('name')}: normales y vertices no cuadran")
                atributos_nuevos["NORMAL"] = len(accesores)
                accesores.append({
                    "bufferView": 1,
                    "byteOffset": n_nor * 12,
                    "componentType": _FLOAT,
                    "count": len(nor),
                    "type": "VEC3",
                })
                normales.append(nor)
                n_nor += len(nor)

            nueva = {"attributes": atributos_nuevos, "indices": len(accesores), "mode": 4}
            accesores.append({
                "bufferView": 2,
                "byteOffset": n_idx * 4,
                "componentType": _UINT32,
                "count": len(idx),
                "type": "SCALAR",
            })
            indices.append(idx)
            n_pos += len(pos)
            n_idx += len(idx)

            if material is not None:
                nueva["material"] = material
            nuevas.append(nueva)

        nueva_malla = dict(malla)
        nueva_malla["primitives"] = nuevas
        mallas.append(nueva_malla)

    trozos = [
        np.concatenate(posiciones) if posiciones else np.empty((0, 3), np.float32),
        np.concatenate(normales) if normales else np.empty((0, 3), np.float32),
        np.concatenate(indices) if indices else np.empty(0, np.uint32),
    ]
    vistas = []
    nuevo_binario = bytearray()
    for trozo, destino in zip(trozos, (_ARRAY_BUFFER, _ARRAY_BUFFER, _ELEMENT_ARRAY_BUFFER)):
        crudo = trozo.tobytes()
        vista = {
            "buffer": 0,
            "byteOffset": len(nuevo_binario),
            "byteLength": len(crudo),
            "target": destino,
        }
        if destino == _ARRAY_BUFFER:
            vista["byteStride"] = 12
        vistas.append(vista)
        nuevo_binario += crudo
        nuevo_binario += b"\0" * (-len(nuevo_binario) % 4)

    cabecera["meshes"] = mallas
    cabecera["accessors"] = accesores
    cabecera["bufferViews"] = vistas
    cabecera["buffers"] = [{"byteLength": len(nuevo_binario)}]

    _escribir_glb(ruta, cabecera, bytes(nuevo_binario))

    return {
        "bytes_antes": antes["bytes"],
        "bytes_despues": ruta.stat().st_size,
        "primitivas_antes": antes["primitivas"],
        "primitivas_despues": sum(len(m["primitives"]) for m in mallas),
        "accesores_antes": antes["accesores"],
        "accesores_despues": len(accesores),
        "triangulos": int(sum(len(i) for i in indices) // 3),
    }
