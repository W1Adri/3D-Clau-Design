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
servidor mira la fecha de los YAML de ``data/`` y de los STEP de ``cad/vendor/``.
Si algo ha cambiado, rehace la escena. Recargar el navegador basta.
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

from . import assembly, parts, structure
from .analysis import fit, interference, volume
from .assembly import Layout, PiezaColocada
from .datamodel import DIR_CAD, DIR_DATOS, RAIZ, Catalogo, Componente, cargar

DIR_VISOR = Path(__file__).resolve().parent / "visor"
DIR_SALIDA = DIR_CAD / "generated"
NOMBRE_GLB = "clau_6u.glb"
NOMBRE_ESCENA = "escena.json"

# Ficheros que, al cambiar, obligan a rehacer la escena.
def _fuentes() -> list[Path]:
    rutas = sorted(DIR_DATOS.glob("*.yaml"))
    vendor = DIR_CAD / "vendor"
    if vendor.exists():
        rutas += sorted(p for p in vendor.rglob("*") if p.suffix.lower() in (".step", ".stp"))
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
        "estado_dato": componente.estado_geometria,
        "desde_step": componente.desde_step,
        "step": componente.step,
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
    chequeos = fit.todos(catalogo)
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
            "pendientes_tbd": len(catalogo.pendientes()),
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
    assembly.ensamblaje(catalogo, layout).export(str(ruta_glb))

    ruta_json = destino / NOMBRE_ESCENA
    ruta_json.write_text(
        json.dumps(escena(catalogo, layout, piezas), ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return ruta_glb, ruta_json


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
            cuerpo = ruta.read_bytes()
            tipo = "model/gltf-binary" if nombre.endswith(".glb") else "application/json"
            self.send_response(200)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
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
    exportar(salida)
    _Manejador._sello_servido = _sello()

    puerto = _puerto_libre(puerto)
    manejador = partial(_Manejador, salida=salida)
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), manejador)
    url = f"http://localhost:{puerto}"

    print(f"Visor en {url}")
    print(f"  escena   : {(salida / NOMBRE_ESCENA).relative_to(RAIZ)}")
    print(f"  geometria: {(salida / NOMBRE_GLB).relative_to(RAIZ)}")
    print("  se regenera sola al cambiar data/*.yaml o cad/vendor/*.step;")
    print("  recarga el navegador para verlo. Ctrl-C para parar.")
    if abrir:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nVisor parado.")
    finally:
        servidor.server_close()
