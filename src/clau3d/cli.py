"""Linea de ordenes de clau3d.

    uv run clau3d validar     comprueba la integridad del catalogo
    uv run clau3d piezas      exporta cada pieza generada a cad/generated/
    uv run clau3d ensamblar   exporta el ensamblaje a cad/generated/clau_6u.step
    uv run clau3d informe     regenera todo reports/
    uv run clau3d ver         abre el visor interactivo en localhost
    uv run clau3d todo        validar + piezas + ensamblar + informe
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import assembly, parts
from .analysis import fit, interference
from .datamodel import DIR_CAD, DIR_INFORMES, cargar, validar


def _cargar_todo():
    catalogo = cargar()
    layout = assembly.cargar_layout()
    piezas = assembly.construir(catalogo, layout)
    return catalogo, layout, piezas


def cmd_validar(_: argparse.Namespace) -> int:
    catalogo = cargar()
    problemas = validar(catalogo)
    if problemas:
        print(f"{len(problemas)} problemas de integridad:")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("Catalogo integro.")
    print(f"  componentes: {len(catalogo.componentes)}")
    print(f"  modelables : {len(parts.modelables(catalogo))}")
    print(f"  TBD        : {len(catalogo.tbd())} (sin dato y sin aproximacion)")
    print(f"  supuestos  : {len(catalogo.supuestos())} (dibujados, pero inventados)")
    print(f"  discrepancias entre fuentes: {len(catalogo.discrepancias())}")
    return 0


def cmd_piezas(_: argparse.Namespace) -> int:
    catalogo = cargar()
    escritos = parts.exportar_generados(catalogo)
    print(f"{len(escritos)} piezas exportadas a {DIR_CAD / 'generated'}")
    for ruta in escritos:
        print(f"  - {ruta.name}")
    sin_geometria = parts.no_modelables(catalogo)
    if sin_geometria:
        print(f"\n{len(sin_geometria)} componentes sin geometria (TBD), no exportados:")
        for componente in sin_geometria:
            print(f"  - {componente.id}")
    return 0


def cmd_ensamblar(args: argparse.Namespace) -> int:
    catalogo, layout, piezas = _cargar_todo()
    destino = Path(args.salida) if args.salida else DIR_CAD / "generated" / "clau_6u.step"
    assembly.exportar_step(catalogo, layout, destino)
    print(f"Ensamblaje escrito en {destino}")
    print(f"  estado del layout: {layout.estado}")
    print(f"  piezas colocadas : {len(piezas)}")
    if not layout.confirmado:
        print("  AVISO: la distribucion aun no esta confirmada.")
    return 0


def cmd_informe(_: argparse.Namespace) -> int:
    catalogo, layout, piezas = _cargar_todo()
    from . import report

    escritos = report.generar_todos(catalogo, layout, piezas, DIR_INFORMES)
    print(f"{len(escritos)} ficheros escritos en {DIR_INFORMES}")
    for ruta in escritos:
        print(f"  - {ruta.relative_to(DIR_INFORMES.parent)}")

    criticos = [c for c in fit.todos(catalogo, layout) if c.critico]
    hallazgos = interference.todas(catalogo, layout, piezas)
    # Una invasion de keep-out dibujado con un numero inventado NO tumba el
    # codigo de salida. Es informacion util -- dice que con esa hipotesis la
    # cosa no cabe -- pero no es un choque de geometrias, y si hiciera fallar a
    # CI, la manera de arreglarlo seria bajar el radio de curvatura supuesto,
    # que es exactamente lo que no se quiere que nadie haga.
    duros = [h for h in hallazgos if not h.basada_en_supuesto]
    blandos = len(hallazgos) - len(duros)
    if criticos or duros:
        print(f"\n{len(criticos)} chequeos fallidos, {len(duros)} interferencias.")
        if blandos:
            print(f"(y {blandos} invasiones de keep-outs SUPUESTOS, que no cuentan)")
        return 1
    if blandos:
        print(
            f"\nSin interferencias reales. {blandos} invasiones de keep-outs "
            f"dibujados con numeros SUPUESTOS: ver reports/03_interferencias.md."
        )
    return 0


def cmd_ver(args: argparse.Namespace) -> int:
    from . import viewer

    catalogo = cargar()
    problemas = validar(catalogo)
    if problemas:
        print(f"{len(problemas)} problemas de integridad; corrigelos antes de mirar nada:")
        for p in problemas:
            print(f"  - {p}")
        return 1
    viewer.servir(puerto=args.puerto, abrir=not args.sin_abrir)
    return 0


def cmd_todo(args: argparse.Namespace) -> int:
    codigo = cmd_validar(args)
    if codigo:
        return codigo
    print()
    cmd_piezas(args)
    print()
    cmd_ensamblar(args)
    print()
    return cmd_informe(args)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="clau3d",
        description="Modelo 3D y analisis volumetrico del CubeSat 6U CLAU",
    )
    sub = parser.add_subparsers(dest="orden", required=True)

    sub.add_parser("validar", help="comprueba la integridad del catalogo").set_defaults(
        func=cmd_validar
    )
    sub.add_parser("piezas", help="exporta las piezas a cad/generated/").set_defaults(
        func=cmd_piezas
    )
    p_ens = sub.add_parser("ensamblar", help="exporta el ensamblaje a STEP")
    p_ens.add_argument("--salida", help="ruta del STEP de salida")
    p_ens.set_defaults(func=cmd_ensamblar)
    sub.add_parser("informe", help="regenera reports/").set_defaults(func=cmd_informe)
    p_ver = sub.add_parser("ver", help="visor interactivo en localhost")
    p_ver.add_argument(
        "--puerto", type=int, default=8000,
        help="puerto de escucha (si esta ocupado, coge el siguiente libre)",
    )
    p_ver.add_argument(
        "--sin-abrir", action="store_true", dest="sin_abrir",
        help="no abrir el navegador, solo imprimir la direccion",
    )
    p_ver.set_defaults(func=cmd_ver)
    p_todo = sub.add_parser("todo", help="validar + piezas + ensamblar + informe")
    p_todo.add_argument("--salida", help="ruta del STEP de salida")
    p_todo.set_defaults(func=cmd_todo)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
