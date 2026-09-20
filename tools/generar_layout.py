"""Genera ``data/layout.yaml`` a partir del catalogo.

Ninguna coordenada del layout se escribe a mano: todas salen de las dimensiones
de ``data/components.yaml`` y del paso de apilamiento PC/104. Asi, cuando llegue
una dimension nueva, se regenera la distribucion en vez de recalcularla a ojo:

    uv run python tools/generar_layout.py

Distribucion elegida el 2026-09-20: DOS COLUMNAS a lo largo de todo Z,
plataforma en -X y payload en +X. Revisada el mismo dia: los moduladores pasan
de la bandeja a la FRANJA lateral que queda junto al telescopio, para que el
telescopio pueda crecer en Z.
"""

from __future__ import annotations

import math
from pathlib import Path

from clau3d.datamodel import RAIZ, cargar

# --- unicas decisiones de reparto, todas justificadas en CLAUDE.md -----
# La longitud del telescopio NO esta aqui: es 'longitud_reservada' del
# telescopio en data/components.yaml, con estado 'decision' y valor provisional.
ANCHO_PLATAFORMA = 100.0   # >= 95.9 mm del iADCS400, con holgura de montaje
L_BANCO = 55.0             # banco de espacio libre

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

# --- la bandeja de fibra ----------------------------------------------
# Las piezas de la bandeja se montan sobre una placa horizontal, en filas que
# avanzan segun Z. Dentro de cada fila van en hilera segun X, que es la
# direccion ancha (121.7 mm) y la del eje de fibra de todas ellas.
#
# El ORDEN ES EL DE LA CADENA OPTICA, y el sentido tambien: el laser al extremo
# -Z, lo mas lejos posible del barrilete del telescopio, porque con sus 4.1 W es
# la principal fuente de calor del payload; y la salida hacia el colimador al
# extremo +Z, que es por donde se sale al banco. Los dos moduladores NO estan
# aqui: van en la franja lateral (ver CLAUDE.md 3.6), asi que la fibra sale de
# la bandeja hacia la franja y vuelve.
FILAS_BANDEJA = [
    ("laser_dfb_1550",),
    ("voa", "aislador"),
    ("filtro_espectral", "acoplador_monitor"),
]
# Holgura entre filas y contra los bordes de la zona. No es una cota de nada:
# es sitio para el tramo recto de fibra que sale de cada pieza antes de curvar.
HOLGURA_BANDEJA = 8.0
MARGEN_BANDEJA = 6.0


# La cara de montaje de cada pieza (montaje.cara, en sus ejes locales) contra la
# normal de la superficie sobre la que se atornilla. De aqui sale la rotacion, en
# vez de escribirla a mano colocacion por colocacion: asi una pieza que cambie de
# cara de montaje en el catalogo se recoloca sola, y el STEP que llegue manana se
# orienta por la misma regla que el aproximado al que sustituye.
_ROTACION_DE_MONTAJE = {
    # (cara local que se atornilla, normal de la superficie) -> giros [gx, gy, gz]
    ("-Y", "+Y"): [0, 0, 0],
    ("-Z", "+Y"): [-90, 0, 0],
    ("+Z", "+Y"): [90, 0, 0],
    ("-X", "+Y"): [0, 0, 90],
    ("-Y", "+X"): [0, 0, -90],
    ("-Z", "+X"): [0, 90, 0],
}


def rotacion_de_montaje(componente, normal: str) -> list[int]:
    """Giros que llevan la cara de montaje de la pieza contra la superficie."""
    montaje = componente.montaje
    if montaje is None or montaje.cara is None:
        return [0, 0, 0]
    try:
        return _ROTACION_DE_MONTAJE[(montaje.cara, normal)]
    except KeyError:
        raise SystemExit(
            f"{componente.id}: no se sabe como montar la cara {montaje.cara} "
            f"contra una superficie {normal}. Anade el caso a "
            f"_ROTACION_DE_MONTAJE en tools/generar_layout.py."
        )


def dims_en_mundo(componente, rotacion: list[int]) -> tuple[float, float, float]:
    """Caja envolvente de la pieza YA girada, conectores incluidos.

    Se pide a parts.caja_local, no a 'dimensiones': una pieza con conectores
    ocupa mas que su cuerpo, y colocarla por el cuerpo la haria chocar con la
    vecina justo por donde sale el cable.
    """
    from clau3d import parts

    caja = parts.caja_local(componente)
    assert caja is not None, componente.id
    dx, dy, dz = caja.dims
    # Los tres giros del diccionario son multiplos de 90 grados, asi que girar
    # es permutar cotas. Se hace a mano para no tener que construir el solido.
    if rotacion[0] in (90, -90):
        dy, dz = dz, dy
    if rotacion[1] in (90, -90):
        dx, dz = dz, dx
    if rotacion[2] in (90, -90):
        dx, dy = dy, dx
    return dx, dy, dz


def generar() -> str:
    catalogo = cargar()
    ix, iy, iz = catalogo.dims_interiores
    X, Y, Z = ix / 2, iy / 2, iz / 2
    paso = catalogo.integracion["pila_pc104.paso_apilamiento_modelado"].escalar()
    assert paso is not None

    l_telescopio = catalogo["telescopio_cassegrain"].extras[
        "longitud_reservada"
    ].escalar()
    assert l_telescopio is not None

    x_sep = -X + ANCHO_PLATAFORMA
    x_pila = -X + ANCHO_PLATAFORMA / 2
    z_tel_min = Z - l_telescopio
    z_banco_min = z_tel_min - L_BANCO

    # Ancho de la franja lateral. NO se elige: el barrilete no puede pasar de
    # la altura interior (iy), que es la dimension pequena del 6U, asi que lo
    # que queda al lado del telescopio es al menos ancho_payload - iy. Tomar
    # ese minimo hace que la franja no dependa del diametro, que es TBD.
    ancho_payload = ix - ANCHO_PLATAFORMA
    ancho_franja = ancho_payload - iy
    x_franja_min = X - ancho_franja

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

    # Los moduladores van TUMBADOS en la franja: el lado de 9.7 mm por X, que es
    # el eje escaso, y el de 15 mm por Y, donde sobra sitio. Asi el conector RF
    # lateral (6.1 x 10 mm) sobresale hacia +-Y y no hacia la franja. Los dos
    # caben en paralelo, y se reparten el ancho de la franja a partes iguales.
    #
    # En Z se pegan al extremo -Z de la franja: es el lado del banco y de la
    # bandeja, y asi los tramos extra de fibra salen lo mas cortos posible.
    moduladores = ("mod_intensidad_mxer_ln_10", "mod_fase_mpz_ln_10")
    for indice, cid in enumerate(moduladores):
        recorrido = catalogo[cid].extras["longitud_con_fibras"].escalar()
        assert recorrido is not None
        colocaciones.append(
            {
                "componente": cid,
                "instancia": 1,
                # [0, 90, 0] lleva [110, 15, 9.7] a [9.7, 15, 110].
                "centro": [
                    round(
                        x_franja_min
                        + ancho_franja * (indice + 0.5) / len(moduladores),
                        3,
                    ),
                    0.0,
                    round(z_tel_min + recorrido / 2, 3),
                ],
                "rotacion": [0, 90, 0],
                "zona": "z_payload_franja",
            }
        )

    # ---------------------------------------------------------------- bandeja
    # La placa, al fondo de la zona, y encima las piezas de la cadena de fibra.
    # Todo se mide desde los limites de la zona, no desde numeros escritos: al
    # cambiar la longitud reservada al telescopio, la bandeja se estrecha y las
    # filas se recolocan solas (o el chequeo avisa de que ya no caben).
    bandeja = catalogo["bandeja_optica"]
    x_bandeja = (x_sep + X) / 2
    z_bandeja = (-Z + z_banco_min) / 2
    y_placa = -Y
    if bandeja.modelable:
        _, espesor_placa, _ = bandeja.dimensiones.como_vector()
        colocaciones.append(
            {
                "componente": "bandeja_optica",
                "instancia": 1,
                "centro": [
                    round(x_bandeja, 3), round(-Y + espesor_placa / 2, 3),
                    round(z_bandeja, 3),
                ],
                "rotacion": rotacion_de_montaje(bandeja, "+Y"),
                "zona": "z_payload_bandeja",
            }
        )
        y_placa = -Y + espesor_placa

    # Las filas avanzan segun Z desde el extremo -Z de la zona. Dentro de cada
    # fila, las piezas se reparten el ancho util en hilera segun X, que es el eje
    # de fibra de todas ellas.
    ancho_util = ancho_payload - 2 * MARGEN_BANDEJA
    cursor_z = -Z + MARGEN_BANDEJA
    for fila in FILAS_BANDEJA:
        piezas = []
        for cid in fila:
            componente = catalogo[cid]
            if not componente.modelable:
                continue
            rotacion = rotacion_de_montaje(componente, "+Y")
            piezas.append((componente, rotacion, dims_en_mundo(componente, rotacion)))
        if not piezas:
            continue
        fondo = max(dims[2] for _, _, dims in piezas)
        ancho_total = sum(dims[0] for _, _, dims in piezas)
        if ancho_total > ancho_util:
            # Antes un error que un layout que se apana. Apretando las piezas
            # hasta que entren saldrian solapes de decimas de milimetro, que el
            # informe de interferencias marcaria sin que se entendiera por que.
            raise SystemExit(
                f"la fila {fila} de la bandeja suma {ancho_total:.1f} mm y solo "
                f"hay {ancho_util:.1f} mm utiles. Parte la fila en dos en "
                f"FILAS_BANDEJA, o baja MARGEN_BANDEJA."
            )
        hueco = (
            (ancho_util - ancho_total) / (len(piezas) - 1) if len(piezas) > 1 else 0.0
        )
        # Una fila de una sola pieza se centra; varias se reparten el ancho.
        cursor_x = x_sep + MARGEN_BANDEJA + (
            (ancho_util - ancho_total) / 2 if len(piezas) == 1 else 0.0
        )
        for componente, rotacion, (dx, dy, dz) in piezas:
            colocaciones.append(
                {
                    "componente": componente.id,
                    "instancia": 1,
                    "centro": [
                        round(cursor_x + dx / 2, 3),
                        round(y_placa + dy / 2, 3),
                        round(cursor_z + fondo / 2, 3),
                    ],
                    "rotacion": rotacion,
                    "zona": "z_payload_bandeja",
                }
            )
            cursor_x += dx + hueco
        cursor_z += fondo + HOLGURA_BANDEJA
    z_libre_bandeja = z_banco_min - (cursor_z - HOLGURA_BANDEJA)

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
            (x_sep, -Y, z_tel_min), (x_franja_min, Y, Z),
            f"Telescopio Cassegrain apuntando por +Z. {l_telescopio:.0f} mm "
            f"RESERVADOS en Z (dato 'longitud_reservada', estado decision, "
            f"provisional hasta el STEP). OJO: los \"~2U\" del brief son ~227 mm "
            f"con la U de longitud de la CDS (113.5 mm), no 200. Esta zona mide "
            f"{iy:.1f} mm en X, que es el mayor diametro de barrilete que cabe "
            f"en la altura interior. Su envolvente es TBD y no se dibuja.",
        ),
        (
            "z_payload_franja",
            "Franja lateral - moduladores",
            (x_franja_min, -Y, z_tel_min), (X, Y, Z),
            f"Los {ancho_franja:.1f} mm de X que quedan al lado del telescopio, "
            f"a lo largo de toda su longitud. Aqui van los dos moduladores "
            f"tumbados (9.7 mm por X, 15 mm por Y, 110 mm por Z), pegados al "
            f"extremo -Z para acortar la fibra hasta la bandeja. El ancho no se "
            f"ha elegido: el barrilete no puede pasar de los {iy:.1f} mm de "
            f"altura interior, asi que esta franja existe para cualquier "
            f"diametro que permita montar el telescopio.",
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
            f"{iz - l_telescopio - L_BANCO:.1f} mm de Z con los "
            f"{ancho_payload:.1f} mm de ancho enteros, ya sin cuerpos de "
            f"modulador dentro. La cadena va en filas que avanzan segun Z, en "
            f"el orden y el sentido de la cadena optica: el laser DFB al "
            f"extremo -Z, lo mas lejos posible del barrilete porque con sus "
            f"4.1 W es la principal fuente de calor del payload, y la salida "
            f"hacia el colimador en +Z. Quedan {z_libre_bandeja:.1f} mm de Z "
            f"libres al final para los bucles, mas los huecos entre filas. "
            f"Cuanta fibra cabe ahi NO se puede decir: falta el radio minimo de "
            f"curvatura. Zona con control termico propio.",
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
        f"#   X > {x_sep:+.2f} mm -> payload ({ancho_payload:.1f} mm de ancho)",
        f"# En la zona del telescopio el payload se parte otra vez en X:",
        f"#   X > {x_franja_min:+.2f} mm -> franja de moduladores ({ancho_franja:.1f} mm)",
        "# =====================================================================",
        "",
        "meta:",
        "  estado: confirmada",
        "  fecha: 2026-09-20",
        "  nota: >-",
        f"    Dos columnas de 3U a lo largo de todo Z. La pila PC104 queda holgada:",
        f"    {usado:.0f} mm usados de {iz:.0f} mm. La columna de payload mide",
        f"    {ancho_payload:.1f} mm de ancho y se parte en dos a lo largo del telescopio:",
        f"    {iy:.1f} mm para el barrilete y {ancho_franja:.1f} mm de franja lateral, donde van",
        "    los dos moduladores tumbados segun Z. Asi la bandeja se queda sin",
        f"    cuerpos dentro y el telescopio puede reservar {l_telescopio:.0f} mm. PCB-2 sigue",
        "    en la otra columna, con lo que el coaxial RF cruza el satelite a lo",
        "    ancho.",
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
