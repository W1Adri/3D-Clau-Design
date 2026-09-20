"""Visor web del ensamblaje: exporta la escena y la sirve en localhost.

Dos ficheros y un servidor:

* ``clau_6u.glb``  — la geometria, exportada por CadQuery con nombres y colores.
* ``escena.json``  — todo lo que la geometria no sabe decir: a que zona
  pertenece cada pieza, de donde sale cada cota, que falta por saber.
* un ``http.server`` de la biblioteca estandar que sirve ambos junto a la
  pagina estatica de ``src/clau3d/visor/``.

Aqui tampoco hay ningun numero del modelo: todo sale del catalogo, del layout y
de los modulos de analisis. Los unicos numeros del visor son de presentacion
(posicion inicial de la camara, tamanos de letra) y viven en el JavaScript.

La pagina se regenera sola: antes de servir ``escena.json`` o el GLB, el
servidor mira la fecha de los YAML de ``data/``, de los STEP de ``cad/vendor/``
y del propio codigo. Si algo ha cambiado, rehace la escena. Recargar el
navegador basta.

Y **solo** entonces. Rehacer la escena cuesta cerca de un minuto y medio: medio
por teselar el ensamblaje y otro medio por las booleanas de interferencia. No
tiene ningun sentido pagarlo al arrancar cuando no ha cambiado nada, asi que si
los dos ficheros de salida son mas nuevos que todas las fuentes, se sirven tal
cual. Lo mismo hacia el navegador: se responde con ``ETag``, de modo que una
recarga con la escena intacta se salta los 17 MB del GLB con un 304.
"""

from __future__ import annotations

import json
import socket
import threading
import webbrowser
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import assembly, gltf, parts, structure
from .analysis import fit, interference, volume
from .assembly import Layout, PiezaColocada
from .datamodel import DIR_CAD, DIR_DATOS, RAIZ, Catalogo, Componente, cargar

DIR_VISOR = Path(__file__).resolve().parent / "visor"
DIR_SALIDA = DIR_CAD / "generated"
NOMBRE_GLB = "clau_6u.glb"
NOMBRE_ESCENA = "escena.json"

# Teselado del GLB. Son numeros de presentacion, como los de la camara: solo
# deciden con cuantos triangulos se *dibuja* una superficie curva, no lo que
# mide. El STEP del ensamblaje no los usa y sigue saliendo con la precision por
# defecto de CadQuery; ninguna cota ni ningun chequeo pasa por aqui.
#
# CadQuery teselaria a 0.1 mm y 0.1 rad, que para un visor es tirar el dinero:
# 862 000 triangulos y 33 MB para que el pin de un conector tenga una decima de
# milimetro mejor la curva. A 0.2 mm son 418 000 triangulos y 17 MB, y en
# pantalla no se distingue.
TOLERANCIA_MALLA_MM = 0.2
TOLERANCIA_ANGULAR_RAD = 0.3

# Ficheros que, al cambiar, obligan a rehacer la escena. El codigo del paquete
# entra tambien: si cambia un color de parts.py o una cota de structure.py, el
# GLB que hay en disco ya no es el que describe el repositorio.
def _fuentes() -> list[Path]:
    rutas = sorted(DIR_DATOS.glob("*.yaml"))
    vendor = DIR_CAD / "vendor"
    if vendor.exists():
        rutas += sorted(p for p in vendor.rglob("*") if p.suffix.lower() in (".step", ".stp"))
    rutas += sorted(Path(__file__).resolve().parent.rglob("*.py"))
    return rutas


def _sello() -> float:
    """Fecha de la fuente modificada mas tarde."""
    return max((p.stat().st_mtime for p in _fuentes()), default=0.0)


# ---------------------------------------------------------------- escena ----

def _texto(valor) -> str | None:
    """Pasa a texto lo que el YAML entrega como fecha u otro objeto suyo."""
    return None if valor is None else str(valor)


def _caja(caja: structure.Caja) -> dict:
    return {
        "min": [caja.xmin, caja.ymin, caja.zmin],
        "max": [caja.xmax, caja.ymax, caja.zmax],
        "centro": list(caja.centro),
        "dims": list(caja.dims),
    }


def _color(componente: Componente) -> list[float]:
    r, g, b, _ = parts.color(componente).toTuple()
    return [r, g, b]


def _magnitud(magnitud) -> dict:
    """Una magnitud del catalogo tal cual, con su procedencia."""
    return {
        "valor": magnitud.valor,
        "unidad": magnitud.unidad,
        "estado": magnitud.estado,
        "fuente": magnitud.fuente,
        "nota": magnitud.nota,
        "falta": magnitud.falta,
        "pedir_a": magnitud.pedir_a,
        "discrepancia": [dict(a) for a in magnitud.alternativas],
    }


def _pieza(pieza: PiezaColocada) -> dict:
    componente: Componente = pieza.componente  # type: ignore[assignment]
    return {
        "nodo": pieza.colocacion.etiqueta,
        "componente": componente.id,
        "nombre": componente.nombre,
        "categoria": componente.categoria,
        "subsistema": componente.subsistema,
        "zona": pieza.colocacion.zona,
        "id_drive": componente.id_drive,
        "referencia_comercial": componente.referencia_comercial,
        "estado_dato": parts.estado_geometria(componente),
        "desde_step": parts.step_disponible(componente),
        "step": fuente.ruta if (fuente := parts.fuente_step(componente)) else None,
        "step_estado": fuente.estado if fuente else None,
        "step_nota": fuente.nota if fuente else None,
        "step_esperado": (
            None
            if componente.step_esperado is None
            else {
                "ruta": componente.step_esperado.ruta,
                "pedir_a": componente.step_esperado.pedir_a,
                "fuente_prevista": componente.step_esperado.fuente_prevista,
            }
        ),
        "forma": componente.tipo_forma,
        "montaje": (
            None
            if componente.montaje is None
            else {
                "cara": componente.montaje.cara,
                "eje": componente.montaje.eje,
                "tipo_eje": componente.montaje.tipo_eje,
                "nota": componente.montaje.nota,
            }
        ),
        "conectores": [
            {
                "id": k.id,
                "tipo": k.tipo,
                "cara": k.cara,
                "dimensiones": _magnitud(k.dimensiones),
                "nota": k.nota,
            }
            for k in componente.conectores
        ],
        "centro": list(pieza.colocacion.centro),
        "rotacion": list(pieza.colocacion.rotacion),
        "caja": _caja(pieza.caja_mundo),
        "volumen_cm3": volume.a_cm3(pieza.caja_mundo.volumen_mm3),
        "requiere_vista_exterior": componente.requiere_vista_exterior,
        "nota": componente.nota,
        "color": _color(componente),
        "magnitudes": {
            "dimensiones": _magnitud(componente.dimensiones),
            "masa": _magnitud(componente.masa),
            "potencia_nominal": _magnitud(componente.potencia_nominal),
            "potencia_pico": _magnitud(componente.potencia_pico),
        },
    }


def _sin_geometria(catalogo: Catalogo) -> list[dict]:
    """Los componentes que no se pueden dibujar, y por que."""
    filas = []
    for componente in parts.no_modelables(catalogo):
        filas.append(
            {
                "componente": componente.id,
                "nombre": componente.nombre,
                "categoria": componente.categoria,
                "subsistema": componente.subsistema,
                "falta": componente.dimensiones.falta,
                "pedir_a": componente.dimensiones.pedir_a,
                "nota": componente.nota,
                "color": _color(componente),
            }
        )
    return filas


def escena(catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]) -> dict:
    """Todo lo que el GLB no sabe decir, en un solo diccionario."""
    envolvente = structure.envolvente(catalogo)
    util = structure.zona_util(catalogo)
    resumen = volume.resumen(catalogo, piezas)
    libre_zona = {f["zona"]: f for f in volume.libre_por_zona(layout, piezas)}
    chequeos = fit.todos(catalogo, layout)
    hallazgos = interference.todas(catalogo, layout, piezas)

    colocados = {p.colocacion.componente_id for p in piezas}

    return {
        "generado": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "glb": NOMBRE_GLB,
        "proyecto": _texto(catalogo.meta.get("proyecto")) or "CLAU",
        "layout": {
            "estado": layout.estado,
            "confirmado": layout.confirmado,
            "nota": _texto(layout.meta.get("nota")),
            # El YAML devuelve datetime.date para las fechas; el JSON no lo sabe.
            "decidido": _texto(layout.meta.get("fecha") or layout.meta.get("decidido")),
        },
        "envolvente": _caja(envolvente),
        "zona_util": _caja(util),
        "resumen": {
            "volumen_exterior_l": volume.a_litros(resumen.exterior_mm3),
            "volumen_interior_l": volume.a_litros(resumen.interior_mm3),
            "volumen_ocupado_l": volume.a_litros(resumen.ocupado_colocado_mm3),
            "volumen_libre_l": volume.a_litros(resumen.libre_mm3),
            "fiable": resumen.fiable,
            "piezas_colocadas": len(piezas),
            "componentes": len(catalogo.componentes),
            "sin_envolvente": resumen.sin_envolvente,
            "no_colocados": resumen.no_colocados,
            "pendientes_tbd": len(catalogo.tbd()),
            "pendientes_supuestos": len(catalogo.supuestos()),
            "discrepancias": len(catalogo.discrepancias()),
        },
        "zonas": [
            {
                "id": zona.id,
                "nombre": zona.nombre,
                "nota": zona.nota,
                "caja": _caja(zona.caja),
                "volumen_l": volume.a_litros(zona.caja.volumen_mm3),
                "libre_l": libre_zona.get(zona.id, {}).get("libre_L"),
                "fraccion_ocupada": libre_zona.get(zona.id, {}).get("fraccion_ocupada"),
            }
            for zona in layout.zonas
        ],
        "keep_outs": [
            {
                "id": k.id,
                "tipo": k.tipo,
                "nota": k.nota,
                "caja": _caja(k.caja),
            }
            for k in layout.keep_outs
        ],
        "railes": [
            {"id": nombre, "caja": _caja(caja)}
            for nombre, caja in structure.railes(catalogo)
        ],
        "piezas": [_pieza(p) for p in piezas],
        "sin_geometria": _sin_geometria(catalogo),
        # Los numeros inventados, uno a uno. El visor los ensena como lista de
        # "esto hay que preguntarlo", que es lo unico que un visor generico no
        # puede decir de un solido que se ve igual de solido que los demas.
        "supuestos": catalogo.supuestos(),
        "chequeos": [
            {
                "id": c.id,
                "titulo": c.titulo,
                "estado": c.estado,
                "mensaje": c.mensaje,
                "falta": c.falta,
            }
            for c in chequeos
        ],
        "interferencias": [
            {
                "tipo": i.tipo,
                "a": i.a,
                "b": i.b,
                "volumen_cm3": i.volumen_cm3,
                "detalle": i.detalle,
            }
            for i in hallazgos
        ],
        "colores": {
            "por_estado": {k: list(v) for k, v in parts.COLOR_POR_ESTADO.items()},
            "por_categoria": {k: list(v) for k, v in parts.COLOR_POR_CATEGORIA.items()},
        },
        "no_colocados_con_geometria": sorted(
            c.id
            for c in parts.modelables(catalogo)
            if c.id not in colocados and c.categoria != "estructura"
        ),
    }


def exportar(destino: Path | None = None) -> tuple[Path, Path]:
    """Rehace ``clau_6u.glb`` y ``escena.json``. Devuelve ambas rutas."""
    destino = destino or DIR_SALIDA
    destino.mkdir(parents=True, exist_ok=True)

    catalogo = cargar()
    layout = assembly.cargar_layout()
    piezas = assembly.construir(catalogo, layout)

    ruta_glb = destino / NOMBRE_GLB
    assembly.ensamblaje(catalogo, layout).export(
        str(ruta_glb),
        tolerance=TOLERANCIA_MALLA_MM,
        angularTolerance=TOLERANCIA_ANGULAR_RAD,
    )
    # OpenCASCADE escribe una primitiva de glTF por cara del BREP, que es lo
    # correcto para un traductor de CAD y lo peor posible para un visor. Ver
    # el modulo gltf: son los mismos triangulos, agrupados de otra manera.
    gltf.compactar(ruta_glb)

    ruta_json = destino / NOMBRE_ESCENA
    ruta_json.write_text(
        json.dumps(escena(catalogo, layout, piezas), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return ruta_glb, ruta_json


def _al_dia(salida: Path) -> bool:
    """Cierto si lo generado es mas nuevo que todas las fuentes."""
    salidas = [salida / NOMBRE_GLB, salida / NOMBRE_ESCENA]
    if not all(p.exists() for p in salidas):
        return False
    return min(p.stat().st_mtime for p in salidas) >= _sello()


# -------------------------------------------------------------- servidor ----

class _Manejador(SimpleHTTPRequestHandler):
    """Sirve la pagina desde el paquete y la escena desde ``cad/generated/``.

    Regenera la escena cuando algun YAML o STEP es mas nuevo que lo servido.
    """

    generados = (NOMBRE_GLB, NOMBRE_ESCENA)
    _cerrojo = threading.Lock()
    _sello_servido = -1.0

    def __init__(self, *args, salida: Path, **kwargs):
        self.salida = salida
        super().__init__(*args, directory=str(DIR_VISOR), **kwargs)

    def _refrescar(self) -> None:
        with _Manejador._cerrojo:
            actual = _sello()
            if actual <= _Manejador._sello_servido:
                return
            try:
                exportar(self.salida)
            except Exception as exc:  # los datos mandan: decirlo, no adivinar
                self.log_message("no se pudo regenerar la escena: %s", exc)
                raise
            _Manejador._sello_servido = actual
            self.log_message("escena regenerada")

    def do_GET(self):  # noqa: N802 (nombre impuesto por la biblioteca)
        nombre = self.path.lstrip("/").split("?")[0]
        if nombre in self.generados:
            try:
                self._refrescar()
            except Exception as exc:
                self.send_error(500, "error al regenerar la escena", str(exc))
                return
            ruta = self.salida / nombre
            if not ruta.exists():
                self.send_error(404, f"falta {nombre}")
                return
            info = ruta.stat()
            # Etiqueta de version: mientras no se regenere la escena, el
            # navegador se ahorra volver a bajar el GLB entero.
            etiqueta = f'"{int(info.st_mtime)}-{info.st_size}"'
            if self.headers.get("If-None-Match") == etiqueta:
                self.send_response(304)
                self.send_header("ETag", etiqueta)
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                return
            cuerpo = ruta.read_bytes()
            tipo = "model/gltf-binary" if nombre.endswith(".glb") else "application/json"
            self.send_response(200)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("ETag", etiqueta)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(cuerpo)
            return
        super().do_GET()

    def log_message(self, formato, *args):  # menos ruido en la consola
        if "GET" in str(formato % args) and " 200 " in str(formato % args):
            return
        super().log_message(formato, *args)


def _puerto_libre(inicial: int, intentos: int = 20) -> int:
    for puerto in range(inicial, inicial + intentos):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", puerto))
                return puerto
            except OSError:
                continue
    raise OSError(f"no hay puerto libre entre {inicial} y {inicial + intentos}")


def servir(
    puerto: int = 8000,
    salida: Path | None = None,
    abrir: bool = True,
) -> None:
    """Deja el visor en http://localhost:<puerto> hasta Ctrl-C."""
    salida = salida or DIR_SALIDA
    if _al_dia(salida):
        print("Escena al dia; no se regenera.")
    else:
        print("Regenerando la escena (teselado e interferencias, ~1 min)...")
        exportar(salida)
    _Manejador._sello_servido = _sello()

    puerto = _puerto_libre(puerto)
    manejador = partial(_Manejador, salida=salida)
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), manejador)
    url = f"http://localhost:{puerto}"

    print(f"Visor en {url}")
    print(f"  escena   : {(salida / NOMBRE_ESCENA).relative_to(RAIZ)}")
    print(f"  geometria: {(salida / NOMBRE_GLB).relative_to(RAIZ)}")
    print("  se regenera sola al cambiar data/*.yaml, cad/vendor/*.step o el codigo;")
    print("  recarga el navegador para verlo. Ctrl-C para parar.")
    if abrir:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nVisor parado.")
    finally:
        servidor.server_close()
