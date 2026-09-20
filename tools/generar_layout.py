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

# --- el banco de espacio libre ----------------------------------------
# El camino es colimador -> dicroico -> FSM -> telescopio, y el FSM es el que
# dobla: el haz llega segun +X y sale segun +Z hacia el telescopio. Eso obliga
# a dos cosas que no son negociables:
#
#   1. El FSM esta sobre el EJE OPTICO DEL TELESCOPIO. No se puede mover.
#   2. El colimador y el dicroico van en linea con el, segun X.
#
# Y de ahi sale el numero que aprieta: entre el eje del telescopio y la pared
# +X de la columna de payload solo hay sitio para esos dos. El chequeo
# 'banco_optico' lo recalcula y dice cuanto margen queda. Si algun dia no da,
# la salida es alargar el banco a costa de la bandeja o del telescopio, no
# apretar las piezas.
#
# El brazo del beacon sale del dicroico segun +-Y: la camara arriba, el laser
# de beacon de bajada abajo.
CADENA_BANCO = ("colimador", "dicroico")   # de +X hacia el FSM
BRAZO_BEACON = (("camara_beacon", +1), ("laser_beacon_bajada", -1))
HOLGURA_BANCO = 5.0
MARGEN_BANCO = 2.0
# El FSM a 45 grados alrededor de Y: lleva la normal del espejo del +Z local a
# la bisectriz entre +X y +Z, que es lo que dobla el haz de X a Z.
GIRO_FSM = [0, 45, 0]


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
    # El telescopio no se atornilla a un suelo: se atornilla por su brida
    # trasera a un mamparo que mira a +Z, que es por donde le entra el haz.
    ("-Z", "+Z"): [0, 0, 0],
    # La antena de parche: se sujeta por +Z local y radia por -Z local, hacia
    # fuera del satelite por la cara -Z.
    ("+Z", "-Z"): [0, 0, 0],
    # Los paneles de cuerpo, uno por cada cara grande. El de -Y va del reves.
    ("-Y", "-Y"): [180, 0, 0],
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


def dims_en_mundo(componente, rotacion) -> tuple[float, float, float]:
    """Caja envolvente de la pieza YA girada, conectores incluidos.

    Se gira el solido de verdad en vez de permutar cotas. Permutar valdria
    mientras todos los giros fueran multiplos de 90 grados, y el FSM no lo es:
    va a 45 para doblar el haz que llega segun X hacia el telescopio, que
    apunta segun +Z. Una caja a 45 grados ocupa mas que la misma caja recta, y
    ese "mas" es justo lo que decide si el banco da de si.

    Ademas se pide a parts.caja_local y no a 'dimensiones', porque una pieza
    con conectores ocupa mas que su cuerpo y colocarla por el cuerpo la haria
    chocar con la vecina justo por donde sale el cable.
    """
    import cadquery as cq

    from clau3d import parts

    solido = parts.solido(componente)
    origen = cq.Vector(0, 0, 0)
    for eje, angulo in zip(
        (cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1)), rotacion
    ):
        if angulo:
            solido = solido.rotate(origen, eje, angulo)
    return parts.caja_de_solidos(solido, componente.id).dims


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
                fx, fy, _ = componente.dimensiones.como_vector()
                # El iADCS400 no es cuadrado: su lado corto va por Y, que es el
                # eje con menos margen de los tres.
                rotacion = [0, 0, 90] if fx < fy else [0, 0, 0]
                # La ranura se mide sobre lo que SE DIBUJA, no sobre la altura
                # de ficha. No es lo mismo: las fichas de AAC miden "from top
                # PCB to lowest component" y no incluyen el conector PC104
                # pasante, que baja 12.45 mm por debajo de la tarjeta. Mientras
                # la tarjeta vecina era un hueco TBD daba igual -- los pines no
                # chocaban con nada --, pero en cuanto la vecina se dibuja, sus
                # 2.91 cm3 de solape aparecen en el informe. Un pin que
                # atraviesa el conector de la vecina es correcto en una pila
                # PC104 de verdad; un pin que atraviesa el BLOQUE MACIZO con el
                # que se modela una tarjeta cuya altura no se conoce, no. Se
                # reserva por lo dibujado, que es conservador y cierto.
                _, _, dz = dims_en_mundo(componente, rotacion)
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

    # ----------------------------------------------------------------- banco
    x_eje_telescopio = (x_sep + x_franja_min) / 2
    z_eje_banco = (z_banco_min + z_tel_min) / 2

    fsm = catalogo["fsm"]
    margen_banco = None
    if fsm.modelable:
        colocaciones.append(
            {
                "componente": "fsm",
                "instancia": 1,
                "centro": [
                    round(x_eje_telescopio, 3), 0.0, round(z_eje_banco, 3),
                ],
                "rotacion": GIRO_FSM,
                "zona": "z_payload_banco",
            }
        )
        # Hacia +X desde el FSM: dicroico y colimador, en orden inverso al de
        # la cadena porque la cadena viene de fuera hacia el espejo.
        cursor_x = x_eje_telescopio + dims_en_mundo(fsm, GIRO_FSM)[0] / 2
        x_dicroico = None
        for cid in reversed(CADENA_BANCO):
            componente = catalogo[cid]
            if not componente.modelable:
                continue
            rotacion = rotacion_de_montaje(componente, "+Y")
            dx, dy, dz = dims_en_mundo(componente, rotacion)
            cursor_x += HOLGURA_BANCO
            centro_x = cursor_x + dx / 2
            colocaciones.append(
                {
                    "componente": cid,
                    "instancia": 1,
                    "centro": [round(centro_x, 3), 0.0, round(z_eje_banco, 3)],
                    "rotacion": rotacion,
                    "zona": "z_payload_banco",
                }
            )
            if cid == "dicroico":
                x_dicroico = centro_x
                ancho_dicroico = dy
            cursor_x += dx
        margen_banco = X - MARGEN_BANCO - cursor_x

        # El brazo del beacon, a +-Y del dicroico.
        if x_dicroico is not None:
            for cid, signo in BRAZO_BEACON:
                componente = catalogo[cid]
                if not componente.modelable:
                    continue
                rotacion = rotacion_de_montaje(componente, "+Y")
                dx, dy, dz = dims_en_mundo(componente, rotacion)
                centro_y = signo * (ancho_dicroico / 2 + HOLGURA_BANCO + dy / 2)
                colocaciones.append(
                    {
                        "componente": cid,
                        "instancia": 1,
                        "centro": [
                            round(x_dicroico, 3), round(centro_y, 3),
                            round(z_eje_banco, 3),
                        ],
                        "rotacion": rotacion,
                        "zona": "z_payload_banco",
                    }
                )

    # ------------------------------------------------------------ telescopio
    # El barrilete llena su zona: su envolvente es la COTA SUPERIOR (el
    # diametro es la altura interior del 6U) y la longitud es la reservada. Si
    # llega el STEP con un diametro menor, la zona se queda igual y sobra sitio
    # alrededor, que es lo que se quiere ver.
    telescopio = catalogo["telescopio_cassegrain"]
    if telescopio.modelable:
        _, _, l_tubo = dims_en_mundo(telescopio, [0, 0, 0])
        colocaciones.append(
            {
                "componente": "telescopio_cassegrain",
                "instancia": 1,
                "centro": [
                    round(x_eje_telescopio, 3), 0.0, round(Z - l_tubo / 2, 3),
                ],
                "rotacion": rotacion_de_montaje(telescopio, "+Z"),
                "zona": "z_payload_telescopio",
            }
        )

    # ------------------------------------------------------------ antena
    # Es la pieza que peor lo tiene: necesita ver la Tierra y no hay cara
    # libre. +Z la ocupan el telescopio y el star tracker; contra las caras
    # +-X y +-Y la pila PC104 deja 2-3 mm; y sus 10 mm de espesor no caben en
    # los 6.5 mm de protrusion que permite la CDS, asi que tampoco puede ir
    # pegada por fuera. Queda -Z, que es el hueco que dejan las baterias, con
    # el coste de que apunta al lado contrario que el telescopio.
    antena = catalogo["antena_quasar_wsant"]
    if antena.modelable:
        _, _, espesor = dims_en_mundo(antena, [0, 0, 0])
        colocaciones.append(
            {
                "componente": "antena_quasar_wsant",
                "instancia": 1,
                "centro": [round(x_pila, 3), 0.0, round(-Z + espesor / 2, 3)],
                "rotacion": rotacion_de_montaje(antena, "-Z"),
                "zona": "z_plataforma",
            }
        )

    # ------------------------------------------------------- paneles solares
    # Van POR FUERA, sobre las dos caras grandes. Se salen de la envolvente a
    # proposito: la CDS 14.1 req 2.2.3 concede 6.5 mm de protrusion y el panel
    # mide 3.5. El detector de desbordes lo sabe porque el catalogo los marca
    # 'exterior'. No pertenecen a ninguna zona interior: llevan zona
    # 'exterior', que no es una de las cinco que embaldosan el hueco util.
    paneles = catalogo["paneles_photon_side"]
    if paneles.modelable and paneles.n_unidades:
        ex, ey, ez = catalogo.dims_exteriores
        _, espesor_panel, _ = paneles.dimensiones.como_vector()
        for instancia, (signo, normal) in enumerate(
            ((+1, "+Y"), (-1, "-Y"))[: paneles.n_unidades], start=1
        ):
            colocaciones.append(
                {
                    "componente": "paneles_photon_side",
                    "instancia": instancia,
                    "centro": [
                        0.0,
                        round(signo * (ey / 2 + espesor_panel / 2), 3),
                        0.0,
                    ],
                    "rotacion": rotacion_de_montaje(paneles, normal),
                    "zona": "exterior",
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
            f"del telescopio, y la antena de banda S detras de ellas, contra "
            f"la pared -Z, que es la unica cara con hueco. La pila usa "
            f"{usado:.0f} mm de los {iz:.0f} mm disponibles. Cada ranura se "
            f"mide sobre la geometria DIBUJADA, no sobre la altura de ficha: "
            f"las fichas AAC no incluyen el conector PC104 pasante y los STEP "
            f"si. Las tres PCBs propias se dibujan con una altura SUPUESTA de "
            f"15 mm.",
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
            f"en la altura interior. El barrilete se dibuja LLENANDO la "
            f"zona, porque su envolvente es una cota superior y no una medida: "
            f"asi se ve que con 90 mm de apertura libre no queda sitio para "
            f"barrilete, celda ni ajuste. En cuanto llegue el STEP, sustituye "
            f"al cilindro sin tocar nada.",
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
            f"Camino: colimador -> dicroico -> FSM -> telescopio, y del "
            f"dicroico sale el brazo del beacon hacia +-Y (camara arriba, "
            f"laser de beacon de bajada abajo). El FSM esta sobre el eje "
            f"optico del telescopio (X = {x_eje_telescopio:+.2f}) porque es el "
            f"que dobla el haz de X a Z, y eso deja el colimador y el dicroico "
            f"en linea hacia +X. Margen contra la pared +X: "
            + (f"{margen_banco:.1f} mm." if margen_banco is not None
               else "no calculable, faltan envolventes.")
            + " Los haces NO estan dibujados: sin diametro de haz, un "
              "keep-out optico seria una medida inventada.",
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
