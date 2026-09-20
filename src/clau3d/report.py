"""Generacion de los informes de ``reports/``. Un solo comando, cero numeros a mano."""

from __future__ import annotations

import csv
import io
from datetime import date
from pathlib import Path

from . import parts, render
from .analysis import budgets, connections, fit, interference, volume
from .assembly import Layout, PiezaColocada
from .datamodel import CONFIRMADO, SUPUESTO, TBD, Catalogo, Componente, validar
from .structure import zona_util

NOTA_UNIDADES = (
    "> **Unidades.** Los volumenes van en **cm3** y en **litros**; las longitudes, "
    "en **mm**. La **U** de la CDS es un *formato* (una ranura de dispensador de "
    "100 x 100 x 113.5 mm), no una unidad de volumen, asi que aqui no se usa para "
    "medir hueco libre: decir que la envolvente 6U \"mide 8.28 U\" mezcla las dos "
    "cosas. Cuando aparece \"6U\" se refiere al formato de la envolvente exterior "
    "(226.3 x 100 x 366 mm), nunca a un volumen calculado."
)

AVISO_LAYOUT = (
    "> **La distribucion aun NO esta confirmada.** Las posiciones de este "
    "informe son una propuesta pendiente de validar por el equipo. El analisis "
    "de interferencias solo es concluyente sobre las piezas realmente colocadas."
)


def _cabecera(titulo: str, catalogo: Catalogo, layout: Layout) -> list[str]:
    lineas = [
        f"# {titulo}",
        "",
        f"Generado automaticamente el {date.today().isoformat()} por `clau3d informe`.",
        "No editar a mano: los numeros salen de `data/components.yaml`.",
        "",
        f"- Mision: {catalogo.meta.get('mision', '?')}",
        f"- Norma: {catalogo.norma.get('documento', '?')}",
        f"- Estado del layout: **{layout.estado}**"
        + (f" ({len(layout.colocaciones)} piezas colocadas)" if layout.colocaciones else ""),
        "",
    ]
    if not layout.confirmado:
        lineas += [AVISO_LAYOUT, ""]
    return lineas


def _tabla(cabeceras: list[str], filas: list[list[str]]) -> list[str]:
    if not filas:
        return ["_(sin filas)_", ""]
    salida = ["| " + " | ".join(cabeceras) + " |"]
    salida.append("|" + "|".join(["---"] * len(cabeceras)) + "|")
    for fila in filas:
        salida.append("| " + " | ".join(fila) + " |")
    salida.append("")
    return salida


def _n(valor: float | None, decimales: int = 1) -> str:
    return "-" if valor is None else f"{valor:.{decimales}f}"


# ---------------------------------------------------------------------
def informe_volumen(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> str:
    resumen = volume.resumen(catalogo, piezas)
    lineas = _cabecera("Informe de volumen", catalogo, layout)

    lineas += [
        NOTA_UNIDADES,
        "",
        "## Resumen",
        "",
        *_tabla(
            ["Concepto", "cm3", "L"],
            [
                ["Envolvente exterior (formato 6U)", _n(volume.a_cm3(resumen.exterior_mm3)),
                 _n(volume.a_litros(resumen.exterior_mm3), 2)],
                ["Zona util interior", _n(volume.a_cm3(resumen.interior_mm3)),
                 _n(volume.a_litros(resumen.interior_mm3), 2)],
                ["Ocupado por piezas colocadas", _n(volume.a_cm3(resumen.ocupado_colocado_mm3)),
                 _n(volume.a_litros(resumen.ocupado_colocado_mm3), 2)],
                ["Ocupado segun catalogo (con o sin colocar)",
                 _n(volume.a_cm3(resumen.ocupado_catalogo_mm3)),
                 _n(volume.a_litros(resumen.ocupado_catalogo_mm3), 2)],
                ["Libre dentro de la zona util", _n(volume.a_cm3(resumen.libre_mm3)),
                 _n(volume.a_litros(resumen.libre_mm3), 2)],
            ],
        ),
    ]

    if not resumen.fiable:
        lineas += [
            "> **El volumen libre de arriba NO es el volumen libre real.**",
            "",
        ]
        if resumen.sin_envolvente:
            lineas += [
                f"> Sin envolvente conocida ({len(resumen.sin_envolvente)}): "
                f"`{'`, `'.join(resumen.sin_envolvente)}`.",
                "",
            ]
        if resumen.no_colocados:
            lineas += [
                f"> Sin colocar ({len(resumen.no_colocados)}): "
                f"`{'`, `'.join(resumen.no_colocados)}`.",
                "",
            ]

    cajas_mundo = {
        p.colocacion.componente_id: p.caja_mundo for p in piezas
    }
    keep_outs_por_pieza: dict[str, int] = {}
    for keep_out in layout.keep_outs:
        for cid in cajas_mundo:
            if cid in keep_out.id:
                keep_outs_por_pieza[cid] = keep_outs_por_pieza.get(cid, 0) + 1

    lineas += ["## Por componente", ""]
    lineas += [
        "`fuente` dice de donde sale el solido que se dibuja; `estado` de donde "
        "salen sus cotas. No siempre coinciden: una pieza con ficha confirmada "
        "y STEP de referencia se dibuja como referencia, porque lo que se esta "
        "viendo es el STEP. `envolvente` es la caja que ocupa YA GIRADA Y "
        "COLOCADA, conectores incluidos, que es lo que ve el detector de "
        "interferencias.",
        "",
    ]
    lineas += _tabla(
        ["id drive", "id", "componente", "fuente", "estado", "uds",
         "volumen cm3", "envolvente mm", "keep-outs", "centro mm", "colocado"],
        [
            [
                catalogo[fila.id].id_drive or "-",
                fila.id,
                fila.nombre,
                _origen_geometria(catalogo[fila.id]),
                fila.estado_dato,
                "-" if fila.unidades is None else str(fila.unidades),
                _n(fila.volumen_cm3),
                " x ".join(f"{v:.0f}" for v in cajas_mundo[fila.id].dims)
                if fila.id in cajas_mundo else "-",
                str(keep_outs_por_pieza.get(fila.id, 0)),
                "-" if fila.centro is None
                else "(" + ", ".join(f"{v:.0f}" for v in fila.centro) + ")",
                "si" if fila.colocado else "no",
            ]
            for fila in volume.tabla(catalogo, piezas)
        ],
    )

    if layout.zonas:
        por_zona = volume.libre_por_zona(layout, piezas)

        # --- por columna ---------------------------------------------
        # Las cinco zonas se agrupan en las dos columnas de 3U de la
        # distribucion. Es la cifra que se mira para decidir que hacer con el
        # reparto, y no sale de ninguna zona por separado.
        columnas = {
            "Plataforma (pila PC104)": ["z_plataforma"],
            "Payload (telescopio, franja, banco y bandeja)": [
                "z_payload_telescopio", "z_payload_franja",
                "z_payload_banco", "z_payload_bandeja",
            ],
        }
        filas = []
        for nombre, ids in columnas.items():
            trozos = [f for f in por_zona if f["zona"] in ids]
            if not trozos:
                continue
            total = sum(f["total_cm3"] for f in trozos)
            ocupado = sum(f["ocupado_cm3"] for f in trozos)
            filas.append([
                nombre, _n(total), _n(ocupado), _n(total - ocupado),
                _n((total - ocupado) / 1000, 2),
                f"{ocupado / total:.0%}" if total else "-",
            ])
        lineas += ["## Hueco libre por columna", ""]
        lineas += _tabla(
            ["columna", "total cm3", "ocupado cm3", "libre cm3", "libre L",
             "% ocupado"],
            filas,
        )
        lineas += [
            "> El **ocupado** son cajas envolventes, no volumen de material: "
            "un cilindro cuenta por su cilindro, pero una caja con un conector "
            "cuenta el hueco entero. Y el **libre** es un techo mientras quede "
            "un solo componente sin colocar o sin envolvente.",
            "",
        ]

        lineas += ["## Hueco libre por zona", ""]
        lineas += _tabla(
            ["zona", "nombre", "total cm3", "ocupado cm3", "libre cm3", "libre L", "% ocupado"],
            [
                [f["zona"], f["nombre"], _n(f["total_cm3"]), _n(f["ocupado_cm3"]),
                 _n(f["libre_cm3"]), _n(f["libre_L"], 2), f"{f['fraccion_ocupada']:.0%}"]
                for f in por_zona
            ],
        )

    # --- lo que sostiene el modelo sin sostenerse en nada -------------
    supuestos = catalogo.supuestos()
    lineas += [
        f"## Supuestos pendientes de sustituir ({len(supuestos)})",
        "",
        "Cada fila es un numero que este repositorio se ha inventado para poder "
        "dibujar algo. Ninguno suma en los presupuestos de masa ni de potencia, "
        "y todos se dibujan en gris. Sustituir cualquiera de ellos por una cifra "
        "con fuente es, literalmente, todo lo que hay que hacer para que esta "
        "parte del modelo deje de ser una reserva y pase a ser un dato.",
        "",
    ]
    lineas += _tabla(
        ["componente", "magnitud", "valor modelado", "que falta", "pedir a"],
        [
            [f["componente"], f["magnitud"], f"`{f['valor_modelado']}`",
             f["falta"], f["pedir_a"]]
            for f in supuestos
        ],
    )

    if piezas:
        lineas += [
            "## Mapa del hueco libre",
            "",
            "Vista desde +Y (planta). Eje horizontal Z (-Z izquierda, +Z derecha),",
            "eje vertical X (+X arriba). De ` ` (vacio) a `@` (lleno).",
            "",
            "```",
            *volume.mapa_libre_xz(zona_util(catalogo), piezas),
            "```",
            "",
        ]
    return "\n".join(lineas)


def informe_viabilidad(catalogo: Catalogo, layout: Layout) -> str:
    lineas = _cabecera("Chequeos de viabilidad", catalogo, layout)
    lineas += [
        "Comprobaciones que no dependen de donde se coloque cada pieza.",
        "",
    ]
    for chequeo in fit.todos(catalogo, layout):
        lineas += [
            f"## {chequeo.titulo}",
            "",
            f"**Estado: {chequeo.estado.upper()}**",
            "",
            chequeo.mensaje,
            "",
        ]
        if chequeo.numeros:
            lineas += _tabla(
                ["magnitud", "valor"],
                [[k, _n(v, 2) if isinstance(v, float) else str(v)]
                 for k, v in chequeo.numeros.items()],
            )
        if chequeo.falta:
            lineas += [f"Falta: {chequeo.falta}", ""]
    return "\n".join(lineas)


def informe_interferencias(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> str:
    lineas = _cabecera("Interferencias", catalogo, layout)
    hallazgos = interference.todas(catalogo, layout, piezas)
    duros = [h for h in hallazgos if not h.basada_en_supuesto]
    blandos = [h for h in hallazgos if h.basada_en_supuesto]
    lineas += [
        f"Piezas colocadas: **{len(piezas)}**. Choques de geometria: "
        f"**{len(duros)}**. Invasiones de keep-outs dibujados con numeros "
        f"SUPUESTOS: **{len(blandos)}**.",
        "",
    ]
    if not piezas:
        lineas += [
            "> No hay ninguna pieza colocada, asi que este analisis no dice nada.",
            "> Confirma la distribucion y rellena `data/layout.yaml`.",
            "",
        ]

    lineas += [
        "## Choques de geometria",
        "",
        "Dos solidos que ocupan el mismo sitio, o una pieza que se sale de "
        "donde tiene que estar. Esto si es un error del modelo o del reparto, y "
        "hace que `clau3d informe` devuelva codigo 1.",
        "",
    ]
    lineas += _tabla(
        ["tipo", "a", "b", "volumen cm3", "detalle"],
        [[h.tipo, h.a, h.b, _n(h.volumen_cm3, 2), h.detalle] for h in duros],
    )

    lineas += [
        f"## Invasiones de keep-outs SUPUESTOS ({len(blandos)})",
        "",
        "> **Esto no es una lista de errores.** Son piezas que se meten en un "
        "volumen reservado que esta dibujado a partir de un numero que se ha "
        "inventado este repositorio: el radio minimo de curvatura de la fibra, "
        "el del coaxial y el diametro de haz siguen siendo **TBD**. Lo que "
        "dicen estas filas es *con la hipotesis de hoy, aqui no cabe*, y la "
        "manera de resolverlas NO es bajar el radio supuesto hasta que "
        "desaparezcan: es conseguir el dato. Por eso no tumban el codigo de "
        "salida.",
        "",
    ]
    if blandos:
        lineas += [
            "Lo que estas filas estan diciendo, en una frase: **la bandeja de "
            "fibra, tal y como esta repartida, no respeta un radio de "
            "curvatura de 30 mm**, y el colimador no tiene por donde sacar su "
            "latiguillo. Las dos cosas se deciden con el mismo dato.",
            "",
        ]
    lineas += _tabla(
        ["tipo", "pieza", "keep-out", "volumen cm3", "detalle"],
        [[h.tipo, h.a, h.b, _n(h.volumen_cm3, 2), h.detalle] for h in blandos],
    )

    if layout.keep_outs:
        lineas += [
            f"## Los keep-outs que hay ({len(layout.keep_outs)})",
            "",
        ]
        lineas += _tabla(
            ["id", "tipo", "estado", "dims mm", "en que se basa"],
            [
                [
                    k.id, k.tipo, k.estado,
                    " x ".join(f"{v:.0f}" for v in k.caja.dims),
                    (k.fuente or "-")[:150],
                ]
                for k in layout.keep_outs
            ],
        )
    return "\n".join(lineas)


def informe_conexiones(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> str:
    lineas = _cabecera("Conexiones", catalogo, layout)
    resultados = connections.comprobar(catalogo, layout, piezas)
    por_estado: dict[str, int] = {}
    for r in resultados:
        por_estado[r.estado] = por_estado.get(r.estado, 0) + 1
    lineas += [
        "Resumen: "
        + ", ".join(f"**{n}** {estado}" for estado, n in sorted(por_estado.items())),
        "",
    ]
    lineas += _tabla(
        ["id", "familia", "desde", "hasta", "tipo", "estado", "recorrido mm", "detalle"],
        [
            [r.id, r.familia, r.desde, r.hasta, r.tipo, r.estado,
             _n(r.longitud_mm, 0), r.mensaje]
            for r in resultados
        ],
    )
    return "\n".join(lineas)


def informe_presupuestos(catalogo: Catalogo, layout: Layout) -> str:
    lineas = _cabecera("Presupuestos de masa y potencia", catalogo, layout)

    for presupuesto in (budgets.masa(catalogo),
                        budgets.potencia(catalogo, pico=False),
                        budgets.potencia(catalogo, pico=True)):
        lineas += [f"## {presupuesto.titulo} ({presupuesto.unidad})", ""]
        por_estado = presupuesto.total_por_estado()
        lineas += _tabla(
            ["estado del dato", f"total {presupuesto.unidad}"],
            [[estado, _n(valor, 2)] for estado, valor in sorted(por_estado.items())]
            + [["**contabilizado**", f"**{presupuesto.total_contabilizado:.2f}**"]],
        )
        if presupuesto.limite is not None:
            lineas += [
                f"Limite de la norma: **{presupuesto.limite:.0f} "
                f"{presupuesto.unidad}**. Margen sobre lo contabilizado: "
                f"**{presupuesto.limite - presupuesto.total_contabilizado:.0f} "
                f"{presupuesto.unidad}**.",
                "",
            ]
        if presupuesto.sin_dato:
            lineas += [
                f"> **Incompleto.** Sin dato ({len(presupuesto.sin_dato)}): "
                f"`{'`, `'.join(presupuesto.sin_dato)}`. "
                f"El total real sera mayor; no se rellena ningun hueco.",
                "",
            ]
        if presupuesto.supuestas:
            lineas += [
                f"### Supuestos, FUERA del total ({len(presupuesto.supuestas)})",
                "",
                f"Suman **{presupuesto.total_supuesto:.2f} {presupuesto.unidad}**, "
                f"que NO estan en la cifra contabilizada de arriba: son numeros "
                f"inventados por este repositorio para poder dibujar la pieza, no "
                f"cifras de ninguna ficha. Se listan porque saber cuanto ocupa lo "
                f"que falta por saber tambien sirve para decidir.",
                "",
            ]
            lineas += _tabla(
                ["id", "componente", "uds", f"unitario {presupuesto.unidad}",
                 f"total {presupuesto.unidad}", "en que se basa"],
                [
                    [f.id, f.nombre, "-" if f.unidades is None else str(f.unidades),
                     _n(f.valor_unitario, 2), _n(f.total, 2), (f.fuente or "-")[:110]]
                    for f in presupuesto.supuestas
                ],
            )
        lineas += _tabla(
            ["id", "componente", "subsistema", "uds", f"unitario {presupuesto.unidad}",
             f"total {presupuesto.unidad}", "estado", "fuente"],
            [
                [f.id, f.nombre, f.subsistema,
                 "-" if f.unidades is None else str(f.unidades),
                 _n(f.valor_unitario, 2), _n(f.total, 2), f.estado,
                 (f.fuente or "-")[:80]]
                for f in presupuesto.filas
            ],
        )

    energia = budgets.energia_disponible(catalogo)
    lineas += [
        "## Energia almacenada",
        "",
        f"- Modulos modelados: **{energia['modulos_modelados']}** "
        f"(estado de la cantidad real: **{energia['estado_cantidad']}**)",
        f"- Capacidad por modulo: {_n(energia['capacidad_por_modulo_Wh'])} Wh",
        f"- Total modelado: {_n(energia['total_Wh'])} Wh",
        "",
        "> El numero de modulos es una hipotesis de trabajo para reservar volumen, "
        "no una decision cerrada.",
        "",
    ]
    return "\n".join(lineas)


def informe_pendientes(catalogo: Catalogo, layout: Layout) -> str:
    lineas = _cabecera("Lista de pendientes", catalogo, layout)
    pendientes = catalogo.pendientes()
    tbd = catalogo.tbd()
    supuestos = catalogo.supuestos()
    lineas += [
        f"Total de huecos abiertos: **{len(pendientes)}**, de los cuales "
        f"**{len(tbd)}** son TBD sin ninguna aproximacion y **{len(supuestos)}** "
        f"son SUPUESTOS: numeros que se ha inventado este repositorio para poder "
        f"dibujar y colocar la pieza.",
        "",
        "> **Un supuesto no es un dato.** No suma en los presupuestos de masa ni "
        "de potencia, se dibuja en gris y aparece aqui hasta que alguien lo "
        "sustituya por una cifra con fuente. La lista de abajo es, literalmente, "
        "lo que hay que preguntar.",
        "",
    ]

    por_responsable: dict[str, list[dict]] = {}
    for fila in pendientes:
        por_responsable.setdefault(fila["pedir_a"], []).append(fila)

    for responsable in sorted(por_responsable):
        filas = por_responsable[responsable]
        lineas += [f"## {responsable} ({len(filas)})", ""]
        lineas += _tabla(
            ["componente", "magnitud", "estado", "valor modelado", "que falta"],
            [
                [
                    f["componente"],
                    f["magnitud"],
                    f["estado"],
                    "-" if f["valor_modelado"] is None else f"`{f['valor_modelado']}`",
                    f["falta"],
                ]
                for f in filas
            ],
        )

    lineas += [
        f"## Solo los supuestos, para sustituirlos ({len(supuestos)})",
        "",
        "Cada fila es un numero que hoy sostiene el modelo sin sostenerse en nada.",
        "",
    ]
    lineas += _tabla(
        ["componente", "magnitud", "valor modelado", "que falta", "pedir a"],
        [
            [f["componente"], f["magnitud"], f"`{f['valor_modelado']}`",
             f["falta"], f["pedir_a"]]
            for f in supuestos
        ],
    )

    discrepancias = catalogo.discrepancias()
    lineas += [f"## Discrepancias entre fuentes ({len(discrepancias)})", ""]
    for d in discrepancias:
        lineas += [
            f"### {d['magnitud']}",
            "",
            f"- Valor usado: `{d['valor_usado']}` - fuente: {d['fuente_usada']}",
        ]
        for alternativa in d["alternativas"]:
            lineas += [
                f"- Alternativa: `{alternativa.get('valor')}` - "
                f"fuente: {alternativa.get('fuente')} - "
                f"{alternativa.get('nota', '')}"
            ]
        lineas += [""]
    return "\n".join(lineas)


# ---------------------------------------------------------------------
def _origen_geometria(componente: Componente) -> str:
    """De donde sale el solido que se dibuja. Es la columna 'fuente' del CSV."""
    fuente = parts.fuente_step(componente)
    if fuente is not None:
        if componente.step is not None:
            return "STEP de fabricante"
        return "STEP de fabricante (aparecido en step_esperado)"
    if not componente.modelable:
        return "sin geometria"
    esperado = componente.step_esperado
    pendiente = " (esperando STEP)" if esperado is not None else ""
    return f"aproximado propio: {componente.tipo_forma}{pendiente}"


def csv_estado(
    catalogo: Catalogo, layout: Layout, piezas: list[PiezaColocada]
) -> str:
    """Estado de cada componente, en CSV, para actualizar la hoja de Drive.

    Una fila por componente del catalogo, incluidas las alternativas en estudio
    y las piezas sin geometria: lo que falta tambien es estado. La columna
    'id_drive' vacia significa que esa pieza NO esta en la hoja y hay que
    anadirla.
    """
    colocadas: dict[str, list[PiezaColocada]] = {}
    for pieza in piezas:
        colocadas.setdefault(pieza.colocacion.componente_id, []).append(pieza)

    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\n")
    escritor.writerow([
        "id_drive", "id", "nombre", "categoria", "subsistema",
        "referencia_comercial", "fuente_geometria", "estado_cotas",
        "dimensiones_mm", "fuente_cotas", "uds", "masa_g", "estado_masa",
        "colocado", "zona", "centro_mm", "conectores", "keep_outs",
        "que_falta", "pedir_a",
    ])

    keep_outs_por_pieza: dict[str, list[str]] = {}
    for keep_out in layout.keep_outs:
        for pieza in piezas:
            cid = pieza.colocacion.componente_id
            if cid in keep_out.id:
                keep_outs_por_pieza.setdefault(cid, []).append(keep_out.id)

    for componente in catalogo.componentes:
        dims = componente.dimensiones
        instancias = colocadas.get(componente.id, [])
        centro = instancias[0].caja_mundo.centro if instancias else None
        escritor.writerow([
            componente.id_drive or "",
            componente.id,
            componente.nombre,
            componente.categoria,
            componente.subsistema,
            componente.referencia_comercial or "",
            _origen_geometria(componente),
            dims.estado,
            "" if dims.valor is None else " x ".join(str(v) for v in dims.valor)
            if isinstance(dims.valor, list) else str(dims.valor),
            (dims.fuente or "").replace("\n", " ")[:300],
            "" if componente.n_unidades is None else componente.n_unidades,
            "" if componente.masa.valor is None else componente.masa.valor,
            componente.masa.estado,
            "si" if instancias else "no",
            instancias[0].colocacion.zona if instancias else "",
            "" if centro is None
            else ", ".join(f"{v:.1f}" for v in centro),
            "; ".join(
                f"{k.id}({k.tipo}, {k.dimensiones.estado})"
                for k in componente.conectores
            ),
            "; ".join(keep_outs_por_pieza.get(componente.id, [])),
            (dims.falta or "").replace("\n", " ")[:300],
            dims.pedir_a or "",
        ])
    return salida.getvalue()


def generar_todos(
    catalogo: Catalogo,
    layout: Layout,
    piezas: list[PiezaColocada],
    dir_destino: Path,
) -> list[Path]:
    dir_destino.mkdir(parents=True, exist_ok=True)
    escritos: list[Path] = []

    documentos = {
        "01_viabilidad.md": informe_viabilidad(catalogo, layout),
        "02_volumen.md": informe_volumen(catalogo, layout, piezas),
        "03_interferencias.md": informe_interferencias(catalogo, layout, piezas),
        "04_conexiones.md": informe_conexiones(catalogo, layout, piezas),
        "05_presupuestos.md": informe_presupuestos(catalogo, layout),
        "06_pendientes.md": informe_pendientes(catalogo, layout),
    }
    for nombre, contenido in documentos.items():
        ruta = dir_destino / nombre
        ruta.write_text(contenido + "\n", encoding="utf-8")
        escritos.append(ruta)

    problemas = validar(catalogo)
    integridad = ["# Integridad del catalogo", ""]
    if problemas:
        integridad += [f"**{len(problemas)} problemas:**", ""]
        integridad += [f"- {p}" for p in problemas]
    else:
        integridad += [
            "Sin problemas: toda magnitud lleva estado y fuente, todo TBD dice "
            "que falta y a quien pedirlo, y toda conexion apunta a componentes "
            "que existen.",
        ]
    ruta = dir_destino / "00_integridad.md"
    ruta.write_text("\n".join(integridad) + "\n", encoding="utf-8")
    escritos.append(ruta)

    ruta = dir_destino / "components_status.csv"
    ruta.write_text(csv_estado(catalogo, layout, piezas), encoding="utf-8")
    escritos.append(ruta)

    escritos += render.todas_las_vistas(catalogo, layout, dir_destino / "vistas")
    return escritos
