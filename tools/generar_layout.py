"""Genera ``data/layout.yaml`` a partir del catalogo.

Ninguna coordenada del layout se escribe a mano: todas salen de las dimensiones
de ``data/components.yaml`` y del paso de apilamiento PC/104. Asi, cuando llegue
una dimension nueva, se regenera la distribucion en vez de recalcularla a ojo:

    uv run python tools/generar_layout.py

Distribucion elegida el 2026-09-20: DOS COLUMNAS a lo largo de todo Z,
plataforma en -X y payload en +X.
"""

from __future__ import annotations

import math
from pathlib import Path

from clau3d.datamodel import RAIZ, cargar

# --- unicas decisiones de reparto, todas justificadas en CLAUDE.md -----
ANCHO_PLATAFORMA = 100.0   # >= 95.9 mm del iADCS400, con holgura de montaje
L_TELESCOPIO = 160.0       # menos que los ~2U del brief: la bandeja necesita Z
L_BANCO = 55.0             # banco de espacio libre
ALTURA_BANDEJA = 5.0       # espesor reservado a la placa de la bandeja
SEPARACION_MODULADORES = 25.0
X_PRIMER_MODULADOR = 20.0

# Orden de la pila, de +Z hacia -Z. El ADCS arriba del todo para que el star
# tracker mire por la misma cara que el telescopio; las baterias al final de -Z
# para equilibrar en Z la masa del telescopio.
ORDEN_PILA = [
    ("adcs_iadcs400", 1),
    ("obc_kryten_m3_plus", 1),
    ("eps_starbuck_nano_plus", 1),
    ("radio_banda_s_quasar_strx", 1),
    ("pcb3_pat", 1),
    ("pcb1_control_qkd", 1),
    ("pcb2_drivers_opticos", 1),
    ("bateria_optimus_30", 2),
]


def generar() -> str:
    catalogo = cargar()
    ix, iy, iz = catalogo.dims_interiores
    X, Y, Z = ix / 2, iy / 2, iz / 2
    paso = catalogo.integracion["pila_pc104.paso_apilamiento_modelado"].escalar()
    assert paso is not None

    x_sep = -X + ANCHO_PLATAFORMA
    x_pila = -X + ANCHO_PLATAFORMA / 2
    z_tel_min = Z - L_TELESCOPIO
    z_banco_min = z_tel_min - L_BANCO

    colocaciones: list[dict] = []
    reservas: list[str] = []
    cursor = Z

    for cid, unidades in ORDEN_PILA:
        componente = catalogo[cid]
        for instancia in range(1, unidades + 1):
            if componente.modelable:
                dx, dy, dz = componente.dimensiones.como_vector()
                # El iADCS400 no es cuadrado: su lado corto va por Y, que es el
                # eje con menos margen de los tres.
                rotacion = [0, 0, 90] if dx < dy else [0, 0, 0]
                ranura = math.ceil(dz / paso) * paso
                colocaciones.append(
                    {
                        "componente": cid,
                        "instancia": instancia,
                        "centro": [round(x_pila, 3), 0.0, round(cursor - ranura / 2, 3)],
                        "rotacion": rotacion,
                        "zona": "z_plataforma",
                    }
                )
            else:
                # Tarjeta de altura TBD: se le reserva una posicion de separador
                # para que ocupe sitio en la pila, pero no se dibuja.
                ranura = paso
                reservas.append(cid)
            cursor -= ranura

    usado = Z - cursor
    z_bandeja_centro = (-Z + z_banco_min) / 2

    for indice, cid in enumerate(
        ("mod_intensidad_mxer_ln_10", "mod_fase_mpz_ln_10")
    ):
        _, _, alto = catalogo[cid].dimensiones.como_vector()
        colocaciones.append(
            {
                "componente": cid,
                "instancia": 1,
                # [0, 90, 90] lleva [110, 15, 9.7] a [15, 9.7, 110]: los 110 mm
                # por Z y el cuerpo plano apoyado sobre la bandeja.
                "centro": [
                    X_PRIMER_MODULADOR + indice * SEPARACION_MODULADORES,
                    round(-Y + ALTURA_BANDEJA + alto / 2, 3),
                    round(z_bandeja_centro, 3),
                ],
                "rotacion": [0, 90, 90],
                "zona": "z_payload_bandeja",
            }
        )

    zonas = [
        (
            "z_plataforma",
            "Columna de plataforma - pila PC104 a lo largo de todo Z",
            (-X, -Y, -Z), (x_sep, Y, Z),
            f"ADCS en +Z, para que el star tracker ST200 mire por la misma cara "
            f"que el telescopio. Despues OBC, EPS, radio banda S, PCB-3, PCB-1 y "
            f"PCB-2, y las baterias al final de -Z, que equilibran en Z la masa "
            f"del telescopio. La pila usa {usado:.0f} mm de los {iz:.0f} mm "
            f"disponibles. Las tres PCBs propias tienen posicion de separador "
            f"reservada pero no se dibujan: su altura es TBD.",
        ),
        (
            "z_payload_telescopio",
            "Telescopio",
            (x_sep, -Y, z_tel_min), (X, Y, Z),
            f"Telescopio Cassegrain apuntando por +Z. {L_TELESCOPIO:.0f} mm de "
            f"longitud reservados, menos que los ~2U del brief: en esta "
            f"distribucion la bandeja necesita recorrido en Z y sale de aqui. "
            f"Su envolvente es TBD y no se dibuja.",
        ),
        (
            "z_payload_banco",
            "Banco optico de espacio libre",
            (x_sep, -Y, z_banco_min), (X, Y, z_tel_min),
            "Colimador, dicroico, FSM y camara de beacon. Camino: colimador -> "
            "dicroico -> FSM -> telescopio, y dicroico -> camara.",
        ),
        (
            "z_payload_bandeja",
            "Bandeja optica de fibra",
            (x_sep, -Y, -Z), (X, Y, z_banco_min),
            f"Los dos moduladores van tumbados a lo largo de Z: con "
            f"{ix - ANCHO_PLATAFORMA:.1f} mm de ancho de columna no caben los "
            f"130 mm de recorrido recto segun X. Zona con control termico "
            f"propio: 0 a +70 C por la extincion del modulador.",
        ),
    ]

    lineas = [
        "# =====================================================================",
        "# CLAU - Distribucion dentro del 6U",
        "# ---------------------------------------------------------------------",
        '# ESTADO: CONFIRMADA (opcion "dos columnas de 3U", elegida el 2026-09-20).',
        "#",
        "# GENERADO por tools/generar_layout.py. No editar a mano: ninguna",
        "# coordenada se escribe, todas salen de data/components.yaml.",
        "#   uv run python tools/generar_layout.py",
        "#",
        "# Coordenadas CDS Rev 14.1: origen en el centro geometrico del 6U.",
        "#   X: +-113.15 mm (ancho, 226.3)",
        "#   Y: +-50.00  mm (alto,  100.0)",
        "#   Z: +-183.00 mm (largo, 366.0). La cara -Z entra primero.",
        f"# Zona util interior: {ix:.1f} x {iy:.1f} x {iz:.1f} mm.",
        "#",
        "# Reparto: dos columnas a lo largo de TODO Z.",
        f"#   X < {x_sep:+.2f} mm -> plataforma ({ANCHO_PLATAFORMA:.1f} mm de ancho)",
        f"#   X > {x_sep:+.2f} mm -> payload ({ix - ANCHO_PLATAFORMA:.1f} mm de ancho)",
        "# =====================================================================",
        "",
        "meta:",
        "  estado: confirmada",
        "  fecha: 2026-09-20",
        "  nota: >-",
        f"    Dos columnas de 3U a lo largo de todo Z. La pila PC104 queda holgada:",
        f"    {usado:.0f} mm usados de {iz:.0f} mm. A cambio la columna de payload mide",
        f"    {ix - ANCHO_PLATAFORMA:.1f} mm de ancho, donde los 130 mm de recorrido recto de",
        "    cada modulador no caben segun X, asi que van segun Z. Y PCB-2 queda",
        "    en la otra columna, con lo que el coaxial RF a los moduladores cruza",
        "    el satelite a lo ancho.",
        "",
        "zonas:",
    ]

    for zid, nombre, minimo, maximo, nota in zonas:
        lineas += [
            f"  - id: {zid}",
            f'    nombre: "{nombre}"',
            "    caja:",
            f"      min: [{minimo[0]:.2f}, {minimo[1]:.2f}, {minimo[2]:.2f}]",
            f"      max: [{maximo[0]:.2f}, {maximo[1]:.2f}, {maximo[2]:.2f}]",
            "    nota: >-",
        ]
        lineas += [f"      {trozo}" for trozo in _envolver(nota, 68)]
        lineas.append("")

    lineas += [
        "# Vacio hasta que lleguen los diametros de haz, el radio de curvatura de",
        "# la fibra y las holguras de conector. Declarar un keep-out con medidas",
        "# inventadas daria una falsa sensacion de comprobacion.",
        "keep_out: []",
        "",
        "colocaciones:",
    ]
    for colocacion in colocaciones:
        cx, cy, cz = colocacion["centro"]
        rx, ry, rz = colocacion["rotacion"]
        lineas += [
            f"  - componente: {colocacion['componente']}",
            f"    instancia: {colocacion['instancia']}",
            f"    centro: [{cx}, {cy}, {cz}]",
            f"    rotacion: [{rx}, {ry}, {rz}]",
            f"    zona: {colocacion['zona']}",
        ]

    return "\n".join(lineas) + "\n"


def _envolver(texto: str, ancho: int) -> list[str]:
    import textwrap

    return textwrap.wrap(" ".join(texto.split()), ancho)


def main() -> None:
    destino = RAIZ / "data" / "layout.yaml"
    destino.write_text(generar(), encoding="utf-8")
    print(f"escrito {destino}")


if __name__ == "__main__":
    main()
