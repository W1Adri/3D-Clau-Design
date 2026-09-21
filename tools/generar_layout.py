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
import sys
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
# la principal fuente de calor del payload; y la salida hacia la franja al
# extremo +Z.
#
# DESDE EL 2026-09-21 LA BANDEJA ES SOLO LA FUENTE: laser, aislador y filtro.
# Todo lo que modula, monitoriza, atenua y codifica esta en la franja, y la
# cadena cruza UNA SOLA VEZ de una zona a la otra, en el tramo f03, que es
# pre-codificacion y por tanto puede curvarse. Con el orden anterior la cadena
# iba y volvia entre bandeja y franja, y ademas ponia el aislador y el filtro
# DETRAS del codificador de polarizacion, que los borra. Ver CLAUDE.md 3.10.
#
# DESDE EL 2026-09-21 EL MODULO DEL BEACON DE BAJADA VA AQUI TAMBIEN, en la
# fila del DFB. No es de la cadena cuantica -- llega por su propia fibra al
# colimador del banco (f08) -- pero es lo otro que disipa del payload, y lo que
# le hace falta es lo mismo que al DFB: placa que le haga de disipador y
# distancia al barrilete. En el banco, donde estaba, su disipador calentaba
# justo lo que tiene que estar estable. Ver CLAUDE.md 3.11.
FILAS_BANDEJA = [
    ("laser_dfb_1550", "laser_beacon_bajada"),
    ("aislador", "filtro_espectral"),
]
# Holgura entre filas y contra los bordes de la zona. No es una cota de nada:
# es sitio para el tramo recto de fibra que sale de cada pieza antes de curvar.
HOLGURA_BANDEJA = 8.0
MARGEN_BANDEJA = 6.0

# --- el banco de espacio libre ----------------------------------------
# El camino es colimador -> espejo de plegado -> D1 -> FSM -> telescopio. El
# FSM es el que dobla hacia el telescopio: el haz llega segun +X y sale segun
# +Z. Eso obliga a dos cosas que no son negociables:
#
#   1. El FSM esta sobre el EJE OPTICO DEL TELESCOPIO. No se puede mover.
#   2. D1 y el espejo de plegado van en linea con el, segun X.
#
# EL ESPEJO DE PLEGADO ES NUEVO (2026-09-21) y ocupa en esa linea el sitio que
# antes ocupaba el colimador. Existe porque el codificador de polarizacion
# tiene que alimentar al colimador EN LINEA RECTA -- nada de fibra curvada
# despues de la codificacion --, el codificador esta en la franja y la franja
# esta en +Z, asi que el colimador apunta segun -Z y hace falta doblar el haz
# de -Z a -X para meterlo en la linea de D1. Ver CLAUDE.md 3.10.
#
# Y de ahi sale el numero que aprieta: entre el eje del telescopio y la pared
# +X de la columna de payload solo hay sitio para esos dos. El chequeo
# 'banco_optico' lo recalcula y dice cuanto margen queda. Si algun dia no da,
# la salida es alargar el banco a costa de la bandeja o del telescopio, no
# apretar las piezas.
#
# EL BRAZO DE LOS BEACONS (arquitectura de dos dicroicos, 2026-09-20). Los dos
# beacons comparten UN SOLO brazo, el que refleja D1 hacia +Y, y dentro de ese
# brazo los separa D2. Cada rama es una fila de piezas que sale de una pieza
# "estacion" por un eje, y se coloca hacia fuera desde ella:
#
#    colimador_beacon        <- +Y, le inyecta a D2 el 1064 en transmision
#            |
#  camara - D2 - fotodiodo   <- -X reflexion del 976, +X fuga del 1064
#            |
#           D1 --- FSM       <- el 1550 sigue recto por X
#            |
#     trampa_luz_d1          <- -Y, fuga del 1550 en reflexion
#
# El orden de las ramas importa: una rama no se puede colocar hasta que su
# estacion esta colocada, y D2 es estacion de dos de ellas.
#
# ESTO YA CABE, desde el 2026-09-21: la rama +Y pide 36 mm de los 47.7 y sobran
# 1.7 mm colocando con holguras. Antes no cabia por 6.8 mm desnudos y 16.8
# colocando, con la camara en +Y. Lo que lo arregla son tres cambios -- celdas
# de 16 mm para Ø12.7, D2 invertido a paso largo con la camara en reflexion, y
# el laser de bajada partido en modulo (bandeja) y colimador (banco) -- y estan
# en CLAUDE.md 3.11. El criterio de siempre sigue en pie: una pieza que no
# quepa NO SE COLOCA y se avisa por stderr.
CADENA_BANCO = ("espejo_plegado_cuantico", "dicroico_d1")  # de +X hacia el FSM
# El colimador ya no esta en esta linea: esta encima del espejo, apuntando -Z.
# Su giro lleva su eje local X (fibra por -X, haz por +X) al -Z del satelite,
# manteniendo la cara de montaje contra el suelo del banco.
GIRO_COLIMADOR = [0, 90, 0]
# Y los moduladores van tumbados con el eje de fibra segun Z, igual que antes.
GIRO_MODULADOR = [0, 90, 0]
# LA TOPOLOGIA DEL BRAZO YA NO ESTA AQUI. Estaba, como RAMAS_BRAZO, y a la vez
# escrita a mano dentro de 'chequeo_brazo_beacon': dos copias del mismo dato.
# Al invertir D2 el 2026-09-21 y mover la camara de +Y a -X, las dos dejaron de
# decir lo mismo. Ahora vive una sola vez, en 'meta.topologia_brazo_beacons' de
# data/connections.yaml, con el motivo de cada rama al lado, y la leen los dos.
HOLGURA_BANCO = 5.0
MARGEN_BANCO = 2.0

# --- la franja lateral -------------------------------------------------
# Desde el 2026-09-21 la franja no es solo "los dos moduladores": es MODULACION,
# MONITORIZACION, ATENUACION Y CODIFICACION, o sea todo lo que va entre la
# fuente y el colimador. La razon es la regla que manda en la cadena: todo
# componente de fibra va ANTES del codificador de polarizacion, y el codificador
# tiene que acabar pegado al banco para alimentar al colimador en linea recta.
# Ver CLAUDE.md 3.10.
#
# EL REPARTO ES EN Y, NO EN X, y no se ha elegido: la franja tiene 26.3 mm de X
# y 95.4 mm de Y, y el codificador ademas tiene la X PINCHADA -- tiene que
# quedar coaxial con el colimador, que esta sobre el espejo de plegado, que esta
# en la linea de D1 --. Asi que el unico eje libre para apilar es Y.
#
#   Y arriba    acoplador 2x2 + VOA        <- sin conectores, lo que mejor se apila
#   Y = 0       COLIMADOR y CODIFICADOR    <- eje de fibra en el plano optico del banco
#   Y abajo     MXER (intensidad)          <- conector RF hacia -Y, lejos del otro
#
# Los bucles de fibra de la franja van en el plano Y-Z, que es el unico donde
# caben: con el radio modelado de 30 mm hacen falta 60 mm de diametro y en X
# solo hay 26.3.
LANES_FRANJA_ARRIBA = ("acoplador_monitor", "voa")
LANES_FRANJA_ABAJO = ("mod_intensidad_mxer_ln_10",)
HOLGURA_FRANJA = 8.0
# El MXER va girado 180 grados alrededor del eje de fibra respecto al
# codificador, para que los dos conectores RF apunten a caras opuestas: asi
# ninguno de los dos coaxiales tiene que pasar por encima del otro modulador.
GIRO_MODULADOR_INVERTIDO = [0, 90, 180]
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


def dims_en_mundo(catalogo, componente, rotacion) -> tuple[float, float, float]:
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

    # El telescopio es un 'cassegrain': su geometria se deriva tambien de
    # 'integracion.optica', asi que hay que pasarle el catalogo. Se mide la
    # ENVOLVENTE porque es lo que la pieza reserva (el modelo detallado es
    # hueco), y es lo mismo que el analisis usa despues.
    solido = parts.solido_envolvente(componente, catalogo)
    origen = cq.Vector(0, 0, 0)
    for eje, angulo in zip(
        (cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1)), rotacion
    ):
        if angulo:
            solido = solido.rotate(origen, eje, angulo)
    return parts.caja_de_solidos(solido, componente.id).dims


def caja_en_mundo(catalogo, componente, rotacion):
    """Caja envolvente YA girada, RELATIVA al origen local de la pieza.

    ``dims_en_mundo`` da solo el tamano, y con eso basta mientras la pieza sea
    simetrica. Una pieza con conector NO lo es: el modulador crece 10 mm hacia
    +Y y nada hacia -Y, asi que colocarla por el centro de su envolvente la
    desplazaria medio conector. Aqui se devuelven los dos extremos para poder
    apilar por el borde de verdad.
    """
    import cadquery as cq

    from clau3d import parts

    solido = parts.solido_envolvente(componente, catalogo)
    origen = cq.Vector(0, 0, 0)
    for eje, angulo in zip(
        (cq.Vector(1, 0, 0), cq.Vector(0, 1, 0), cq.Vector(0, 0, 1)), rotacion
    ):
        if angulo:
            solido = solido.rotate(origen, eje, angulo)
    return parts.caja_de_solidos(solido, componente.id)


# Direcciones de las seis caras, en ejes locales.
_VECTOR_CARA = {
    "+X": (1, 0, 0), "-X": (-1, 0, 0),
    "+Y": (0, 1, 0), "-Y": (0, -1, 0),
    "+Z": (0, 0, 1), "-Z": (0, 0, -1),
}


def _gira_vector(v, rotacion):
    """Gira un vector unitario por los mismos giros que la pieza."""
    import math as _m

    x, y, z = v
    gx, gy, gz = (_m.radians(a) for a in rotacion)
    # X
    y, z = y * _m.cos(gx) - z * _m.sin(gx), y * _m.sin(gx) + z * _m.cos(gx)
    # Y
    z, x = z * _m.cos(gy) - x * _m.sin(gy), z * _m.sin(gy) + x * _m.cos(gy)
    # Z
    x, y = x * _m.cos(gz) - y * _m.sin(gz), x * _m.sin(gz) + y * _m.cos(gz)
    return (x, y, z)


def _caja_saliente(centro, direccion, largo, radio, normal_montaje=None):
    """Volumen que barre un cable al salir de un puerto y dar su primer codo.

    Sale del punto en 'direccion' una longitud 'largo' (tramo recto mas el
    envolvente del codo) y tiene 'radio' a cada lado, porque el codo puede irse
    a un lado o al otro.

    En el eje perpendicular al montaje NO es simetrico: un cable que sale de
    una pieza atornillada a una bandeja puede subir, pero no atravesar la
    bandeja. Con 'normal_montaje' el volumen crece solo hacia ese lado, que es
    la diferencia entre un keep-out util y uno que se hunde en la placa y
    ensucia el informe con invasiones que no significan nada.
    """
    eje = max(range(3), key=lambda i: abs(direccion[i]))
    signo = 1.0 if direccion[eje] >= 0 else -1.0
    eje_normal = (
        max(range(3), key=lambda i: abs(normal_montaje[i]))
        if normal_montaje is not None
        else None
    )
    minimo = [0.0, 0.0, 0.0]
    maximo = [0.0, 0.0, 0.0]
    for i in range(3):
        if i == eje:
            a, b = centro[i], centro[i] + signo * largo
            minimo[i], maximo[i] = min(a, b), max(a, b)
        elif i == eje_normal:
            # Solo hacia fuera de la superficie de montaje.
            if normal_montaje[i] >= 0:
                minimo[i], maximo[i] = centro[i], centro[i] + 2 * radio
            else:
                minimo[i], maximo[i] = centro[i] - 2 * radio, centro[i]
        else:
            minimo[i], maximo[i] = centro[i] - radio, centro[i] + radio
    return minimo, maximo


def _recortado(minimo, maximo, util):
    """Recorta el volumen a la zona util. Devuelve None si se queda en nada.

    Un keep-out no puede reservar sitio fuera del satelite: lo que queda al
    otro lado de la pared no es volumen que nadie vaya a invadir, es ruido en
    el informe.
    """
    caja = (util.xmin, util.ymin, util.zmin, util.xmax, util.ymax, util.zmax)
    nuevo_min = [max(minimo[i], caja[i]) for i in range(3)]
    nuevo_max = [min(maximo[i], caja[i + 3]) for i in range(3)]
    if any(nuevo_max[i] - nuevo_min[i] <= 1e-6 for i in range(3)):
        return None
    return nuevo_min, nuevo_max


def _keep_outs_compartidos(catalogo) -> dict[str, list[dict]]:
    """Tramos que recorren el mismo tubo que otro, por 'keep_out_compartido_con'.

    Un tramo de espacio libre que va y vuelve por el mismo sitio -- el brazo de
    los beacons, donde suben 976 nm y bajan 1064 -- es UN volumen, no dos.
    Declararlo dos veces no reserva nada nuevo: reserva lo mismo otra vez, y el
    detector de interferencias ve dos cajas identicas solapando al 100 % e
    informa de una invasion que no existe.

    Devuelve {id del tramo que SI lleva keep-out: [los tramos que lo comparten]},
    para que la nota del keep-out diga quien mas pasa por ahi y con que color.

    Se comprueba que el tramo compartido exista, que lleve keep-out y que una
    los MISMOS DOS EXTREMOS. Si no, es otro tramo y necesita su propio volumen:
    antes un error que un camino optico sin reservar.
    """
    por_id = {
        con.get("id"): con
        for familia, con in catalogo.todas_las_conexiones()
        if familia == "opticas_espacio_libre"
    }
    salida: dict[str, list[dict]] = {}
    for cid, con in por_id.items():
        destino = con.get("keep_out_compartido_con")
        if destino is None:
            continue
        if con.get("keep_out"):
            raise SystemExit(
                f"conexion {cid}: declara 'keep_out: true' y "
                f"'keep_out_compartido_con: {destino}' a la vez. O tiene "
                f"volumen propio o comparte el de otro."
            )
        otro = por_id.get(destino)
        if otro is None:
            raise SystemExit(
                f"conexion {cid}: 'keep_out_compartido_con' apunta a "
                f"'{destino}', que no es un tramo de opticas_espacio_libre."
            )
        if not otro.get("keep_out"):
            raise SystemExit(
                f"conexion {cid}: comparte el keep-out de '{destino}', que no "
                f"tiene ninguno. Entonces ese tramo no esta reservado por nadie."
            )
        if {con.get("desde"), con.get("hasta")} != {otro.get("desde"), otro.get("hasta")}:
            raise SystemExit(
                f"conexion {cid} ({con.get('desde')} -> {con.get('hasta')}) "
                f"comparte el keep-out de '{destino}' "
                f"({otro.get('desde')} -> {otro.get('hasta')}), que une otros "
                f"extremos. Un tramo compartido es el MISMO tubo recorrido al "
                f"reves, no un tramo parecido."
            )
        salida.setdefault(destino, []).append(
            {
                "id": cid,
                "desde": con.get("desde"),
                "hasta": con.get("hasta"),
                "longitud_onda_nm": con.get("longitud_onda_nm"),
            }
        )
    return salida


def generar_keep_outs(catalogo, colocaciones, zonas_por_id) -> list[dict]:
    """Los volumenes reservados que se pueden dibujar hoy, y solo esos.

    Tres familias, y las tres salen de un numero SUPUESTO, porque las tres
    cotas de verdad -- el radio minimo de curvatura de la fibra, el del
    coaxial y el diametro de haz -- siguen siendo TBD:

    * **fibra**: el tramo recto de salida (boot) mas el envolvente del primer
      codo, en cada puerto QUE TENGA UNA CONEXION DECLARADA. No en los dos
      extremos de todo: el laser solo tiene fibra por un lado y el colimador
      tambien, y dibujarles un keep-out en la cara que no lleva fibra inventa
      un encaminamiento que nadie ha decidido.
    * **coaxial**: lo mismo a la salida del conector RF de cada modulador.
    * **haz libre**: el tubo que queda ENTRE dos piezas del banco, sin contar
      los cuerpos de las dos: un keep-out que se come a sus propios extremos
      genera invasiones que no significan nada.

    Cada volumen se recorta a la zona de su pieza. Un keep-out de la bandeja
    que se cuela en la columna de plataforma no esta diciendo que la fibra
    pase por ahi: esta diciendo que este generador no sabe por donde pasa. Y no
    lo sabe: el encaminamiento es una decision abierta.

    Si alguno de los tres parametros llegara a existir de verdad, el keep-out
    correspondiente pasaria de 'supuesto' a 'confirmado' sin tocar este codigo.

    Lo que NO se genera es el cono de la apertura del telescopio hacia fuera:
    sin semiangulo, un cono es una medida inventada de las gordas.
    """
    from clau3d import parts, structure

    util = structure.zona_util(catalogo)
    puestas = {
        (c["componente"], c["instancia"]): c for c in colocaciones
    }
    radio = catalogo.integracion["fibra.radio_curvatura_modelado"].escalar()
    boot = catalogo.integracion["fibra.longitud_boot_modelada"].escalar()
    radio_coax = catalogo.integracion["coaxial.radio_curvatura_modelado"].escalar()
    haz = catalogo.integracion["optica.diametro_haz_modelado"].escalar()

    def _recinto(colocacion):
        """La zona de la pieza, o la util si esta fuera de toda zona."""
        zona = zonas_por_id.get(colocacion.get("zona"))
        return zona if zona is not None else util

    salida: list[dict] = []

    # --- fibra: solo los puertos con conexion declarada -------------------
    fuente_fibra = (
        f"Tramo recto de {boot:.0f} mm (integracion.fibra.longitud_boot_modelada) "
        f"mas el envolvente de un codo de {radio:.0f} mm "
        f"(integracion.fibra.radio_curvatura_modelado). Los dos son SUPUESTOS: "
        f"el radio de verdad es integracion.fibra.radio_minimo_curvatura, que "
        f"sigue siendo TBD. La DIRECCION tampoco es un dato: se toma el eje de "
        f"fibra que declara 'montaje', porque el encaminamiento real esta sin "
        f"decidir."
    )
    # Un tramo marcado RECTO no genera keep-out de curvatura en sus dos
    # extremos, y no por ahorrar volumen: es que no hay codo que reservar. El
    # tramo que sale del codificador de polarizacion no se puede curvar --
    # los estados diagonales no son autoestados de la fibra PM y cualquier
    # curva les mete una fase que deriva con la temperatura --, asi que
    # dibujarle el envolvente de un codo estaria reservando sitio para algo
    # que tiene prohibido pasar. Lo que ese tramo necesita es longitud RECTA,
    # y eso lo mide el chequeo 'fibra_post_codificacion', no un keep-out.
    puertos: dict[str, set[str]] = {}
    for familia, con in catalogo.todas_las_conexiones():
        if familia != "opticas_fibra":
            continue
        if con.get("recto") or con.get("keep_out") is False:
            continue
        if con.get("desde"):
            puertos.setdefault(con["desde"], set()).add("salida")
        if con.get("hasta"):
            puertos.setdefault(con["hasta"], set()).add("entrada")

    for cid, lados in puertos.items():
        if not catalogo.existe(cid):
            continue
        componente = catalogo[cid]
        colocacion = puestas.get((cid, 1))
        if colocacion is None or componente.montaje is None:
            continue
        if componente.montaje.eje is None:
            continue
        rotacion = colocacion["rotacion"]
        centro = colocacion["centro"]
        dims = dims_en_mundo(catalogo, componente, rotacion)
        eje_local = {"X": "+X", "Y": "+Y", "Z": "+Z"}[componente.montaje.eje]
        normal = None
        if componente.montaje.cara:
            # La cara del catalogo es la que SE APOYA; el cable crece al otro
            # lado, asi que no puede atravesar la placa de montaje.
            normal = tuple(
                -k for k in _gira_vector(
                    _VECTOR_CARA[componente.montaje.cara], rotacion
                )
            )
        for lado in sorted(lados):
            # 'sentido' dice hacia donde viaja la senal por el eje declarado.
            # Casi siempre es +1 -- entra por la cara negativa y sale por la
            # positiva --, pero el colimador del beacon emite hacia -Y, asi que
            # su fibra entra por +Y. Sin esto, su keep-out de entrada salia por
            # la cara del haz y atravesaba medio banco.
            signo = (1 if lado == "salida" else -1) * componente.montaje.sentido
            direccion = _gira_vector(
                tuple(signo * k for k in _VECTOR_CARA[eje_local]), rotacion
            )
            eje_mundo = max(range(3), key=lambda i: abs(direccion[i]))
            punto = list(centro)
            mitad = dims[eje_mundo] / 2
            punto[eje_mundo] += mitad if direccion[eje_mundo] >= 0 else -mitad
            recorte = _recortado(
                *_caja_saliente(punto, direccion, boot + radio, radio, normal),
                _recinto(colocacion),
            )
            if recorte is None:
                continue
            salida.append({
                "id": f"fibra_{cid}_{lado}",
                "tipo": "fibra",
                "estado": "supuesto",
                "fuente": fuente_fibra,
                "min": [round(v, 3) for v in recorte[0]],
                "max": [round(v, 3) for v in recorte[1]],
                "nota": (
                    f"Puerto de {lado} de fibra de {cid}, recortado a la zona "
                    f"{colocacion.get('zona')}."
                ),
            })

    # --- coaxial: el conector RF de cada modulador ------------------------
    fuente_coax = (
        f"Envolvente de un codo de {radio_coax:.0f} mm a la salida del conector "
        f"RF (integracion.coaxial.radio_curvatura_modelado, SUPUESTO). El "
        f"conector SI es dato: 6.1 x 10 mm del plano de Exail."
    )
    for cid in ("mod_intensidad_mxer_ln_10", "mod_fase_mpz_ln_10"):
        colocacion = puestas.get((cid, 1))
        if colocacion is None or not catalogo.existe(cid):
            continue
        componente = catalogo[cid]
        rotacion = colocacion["rotacion"]
        centro = colocacion["centro"]
        dims = dims_en_mundo(catalogo, componente, rotacion)
        for conector in componente.conectores:
            if conector.tipo != "coaxial" or conector.dimensiones.es_tbd:
                continue
            direccion = _gira_vector(_VECTOR_CARA[conector.cara], rotacion)
            eje_mundo = max(range(3), key=lambda i: abs(direccion[i]))
            # El cable sale de la PUNTA del conector, no del borde de la caja
            # envolvente de la pieza. No es lo mismo: la envolvente crece hacia
            # el conector pero el centro de la pieza sigue siendo el del
            # cuerpo, asi que centro + media envolvente se queda CORTO y el
            # keep-out se solapa con su propio conector. Se mide desde el
            # cuerpo, que es simetrico, y se le suma el saliente declarado.
            eje_local = "XYZ".index(conector.cara[1])
            cuerpo = componente.dimensiones.como_vector()
            saliente = conector.dimensiones.como_vector()
            mitad = cuerpo[eje_local] / 2 + saliente[eje_local]
            punto = list(centro)
            punto[eje_mundo] += mitad if direccion[eje_mundo] >= 0 else -mitad
            recorte = _recortado(
                *_caja_saliente(punto, direccion, radio_coax, radio_coax),
                _recinto(colocacion),
            )
            if recorte is None:
                continue
            salida.append({
                "id": f"coaxial_{cid}",
                "tipo": "coaxial",
                "estado": "supuesto",
                "fuente": fuente_coax,
                "min": [round(v, 3) for v in recorte[0]],
                "max": [round(v, 3) for v in recorte[1]],
                "nota": f"Salida del conector RF de {cid} hacia PCB-2.",
            })

    # --- haz libre: el hueco ENTRE dos piezas del banco -------------------
    fuente_haz = (
        f"Tubo de {haz:.0f} mm de lado "
        f"(integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que "
        f"queda entre las dos piezas. El diametro de haz de cada tramo es TBD "
        f"en data/connections.yaml."
    )
    compartidos = _keep_outs_compartidos(catalogo)
    for familia, con in catalogo.todas_las_conexiones():
        if familia != "opticas_espacio_libre" or not con.get("keep_out"):
            continue
        desde, hasta = con.get("desde"), con.get("hasta")
        a, b = puestas.get((desde, 1)), puestas.get((hasta, 1))
        if a is None or b is None:
            continue
        caja_a = _caja_mundo(catalogo, a)
        caja_b = _caja_mundo(catalogo, b)
        # El eje del tramo es aquel en el que las dos cajas NO se solapan: es
        # por donde hay hueco entre ellas.
        tramo = None
        for i in range(3):
            hueco_min = max(caja_a[0][i], caja_b[0][i])
            hueco_max = min(caja_a[1][i], caja_b[1][i])
            if hueco_max < hueco_min:  # separadas en este eje
                bajo, alto = (caja_a, caja_b) if caja_a[1][i] < caja_b[0][i] else (caja_b, caja_a)
                tramo = (i, bajo[1][i], alto[0][i])
                break
        if tramo is None:
            continue
        eje, z0, z1 = tramo
        centro_a = [(caja_a[0][k] + caja_a[1][k]) / 2 for k in range(3)]
        centro_b = [(caja_b[0][k] + caja_b[1][k]) / 2 for k in range(3)]
        minimo = [0.0, 0.0, 0.0]
        maximo = [0.0, 0.0, 0.0]
        for i in range(3):
            if i == eje:
                minimo[i], maximo[i] = z0, z1
            else:
                medio = (centro_a[i] + centro_b[i]) / 2
                minimo[i], maximo[i] = medio - haz / 2, medio + haz / 2
        recorte = _recortado(minimo, maximo, _recinto(a))
        if recorte is None:
            continue
        nota = f"Camino optico {desde} -> {hasta} ({con.get('id')})."
        otros = compartidos.get(con.get("id"), [])
        if otros:
            nota += (
                " TRAMO COMPARTIDO: lo recorren tambien "
                + ", ".join(
                    f"{o['id']} ({o['desde']} -> {o['hasta']}"
                    + (f", {o['longitud_onda_nm']:.0f} nm" if o["longitud_onda_nm"] else "")
                    + ")"
                    for o in otros
                )
                + ". Es el mismo tubo, asi que el volumen se declara una sola "
                "vez: duplicarlo no reservaria nada nuevo y si generaria una "
                "invasion de keep-out que no significa nada."
            )
        salida.append({
            "id": f"haz_{con.get('id')}",
            "tipo": "haz_libre",
            "estado": "supuesto",
            "fuente": fuente_haz,
            "min": [round(v, 3) for v in recorte[0]],
            "max": [round(v, 3) for v in recorte[1]],
            "nota": nota,
        })

    salida += _haz_del_telescopio(catalogo, puestas)
    return salida


def _haz_del_telescopio(catalogo, puestas) -> list[dict]:
    """El camino del haz DENTRO del barrilete, con su diametro en cada tramo.

    Son dos tramos y no uno porque el telescopio es un compresor de haz: por
    delante del primario viaja la apertura entera, y por detras -- entre el
    secundario y la brida del FSM, atravesando el agujero central -- viaja ya
    comprimido. Dibujarlo con un solo tubo perderia justamente el dato que
    importa.

    Van como KEEP-OUT y no como cuerpo solido: ahi no hay material, hay luz. Y
    llevan 'de_pieza', porque caen enteros dentro de la envolvente del propio
    telescopio: sin eso el modelo diria que el telescopio invade su propio haz.
    """
    from clau3d.optica import parametros

    cid = "telescopio_cassegrain"
    colocacion = puestas.get((cid, 1))
    if colocacion is None or not catalogo.existe(cid):
        return []
    componente = catalogo[cid]
    if componente.tipo_forma != "cassegrain":
        return []
    m = parametros.mecanica(componente, catalogo)
    o = m.optica
    cx, cy, cz = colocacion["centro"]

    fuente = (
        f"Envolvente del haz dentro del barrilete, derivada de 'optica' en "
        f"data/components.yaml. SUPUESTO por partida doble: la apertura libre "
        f"es una decision de ACSAR sin diametro de barrilete que la respalde, y "
        f"el haz comprimido se dibuja con "
        f"integracion.optica.diametro_haz_modelado ({o.diametro_haz:.0f} mm) "
        f"porque 'optica.diametro_haz_comprimido' sigue siendo TBD."
    )

    def _tubo(lado: float, z0: float, z1: float, sufijo: str, nota: str) -> dict:
        return {
            "id": f"haz_telescopio_{sufijo}",
            "tipo": "haz_libre",
            "estado": "supuesto",
            "fuente": fuente,
            "de_pieza": cid,
            "min": [round(cx - lado / 2, 3), round(cy - lado / 2, 3), round(cz + z0, 3)],
            "max": [round(cx + lado / 2, 3), round(cy + lado / 2, 3), round(cz + z1, 3)],
            "nota": nota,
        }

    return [
        _tubo(
            o.apertura_libre,
            m.z_vertice_primario,
            m.z_frontal_exterior,
            "colimado",
            f"Haz de entrada, {o.apertura_libre:.0f} mm, de la apertura al "
            f"primario. Es lo que obliga a que nada estructural entre en el "
            f"tubo por delante del espejo.",
        ),
        _tubo(
            o.diametro_haz,
            m.z_trasero_exterior,
            m.z_vertice_secundario,
            "comprimido",
            f"Haz comprimido, {o.diametro_haz:.0f} mm, del secundario a la "
            f"brida del FSM atravesando el agujero central del primario. "
            f"Magnificacion derivada M = {o.magnificacion:.2f}.",
        ),
    ]


def _ramas_del_brazo(catalogo, colocaciones, recinto):
    """Las piezas que cuelgan de D1 y de D2, rama por rama.

    Cada rama sale de una pieza ESTACION ya colocada y crece hacia fuera por un
    eje, dejando ``HOLGURA_BANCO`` entre pieza y pieza. Las estaciones se leen
    de lo que ya hay colocado, asi que D2 -- que es estacion de dos ramas ademas
    de pieza de la primera -- no se situa dos veces ni se escribe su posicion a
    mano en ningun sitio.

    UNA PIEZA QUE NO CABE NO SE COLOCA. Hoy es el caso de la camara: el brazo
    compartido pide mas de lo que hay desde D1 hasta la pared, y no sobra sitio
    en ninguna otra direccion. Las tres salidas posibles son apretarla, dibujarla
    saliendose del satelite o no colocarla, y las dos primeras mienten: la
    primera esconde el resultado y la segunda dibuja una pieza en un sitio en el
    que no puede estar, que ademas choca con el panel solar. Asi que no se
    coloca, se avisa por stderr, y el chequeo 'brazo_beacon' lo cuenta en
    milimetros. Es el mismo criterio que la fila de la bandeja que no cabe
    -- no se aprieta -- sin tumbar el generador entero, porque aqui lo que no
    cabe es la ARQUITECTURA, no el reparto, y el resto del modelo sigue siendo
    valido y hay que poder verlo.
    """
    salida: list[dict] = []
    sin_sitio: list[tuple[str, str, float]] = []
    puestas = {c["componente"]: c for c in colocaciones}

    ramas = catalogo.topologia_brazo_beacons
    if not ramas:
        raise SystemExit(
            "data/connections.yaml no declara 'meta.topologia_brazo_beacons'. "
            "Sin ella no se sabe que cuelga de cada cara de D1 y de D2, y "
            "escribirla otra vez aqui es lo que hizo que el generador y el "
            "chequeo dejaran de decir lo mismo."
        )

    for rama in ramas:
        estacion_id = rama["estacion"]
        cara = rama["cara"]
        fila = tuple(rama.get("piezas") or ())
        estacion = puestas.get(estacion_id)
        if estacion is None:
            # La estacion no se pudo colocar (su envolvente es TBD): la rama
            # entera se queda sin sitio de donde salir. No se inventa uno.
            continue
        eje = "XYZ".index(cara[1])
        signo = 1 if cara[0] == "+" else -1
        dims_estacion = dims_en_mundo(
            catalogo, catalogo[estacion_id], estacion["rotacion"]
        )
        # Desde la cara de la estacion hacia fuera.
        borde = estacion["centro"][eje] + signo * dims_estacion[eje] / 2
        for cid in fila:
            if not catalogo.existe(cid):
                continue
            componente = catalogo[cid]
            # Una alternativa excluyente no se coloca, igual que el FSM piezo:
            # el cuarto puerto de D2 es uno solo.
            if not componente.modelable or not componente.cuenta_en_presupuesto:
                continue
            rotacion = rotacion_de_montaje(componente, "+Y")
            dims = dims_en_mundo(catalogo, componente, rotacion)
            borde += signo * HOLGURA_BANCO
            centro = list(estacion["centro"])
            centro[eje] = borde + signo * dims[eje] / 2
            extremo = borde + signo * dims[eje]
            pared = recinto[1][eje] if signo > 0 else recinto[0][eje]
            if signo * (extremo - pared) > 0:
                sin_sitio.append((cid, cara, abs(extremo - pared)))
                # Y tampoco lo que fuera detras de ella: sin la pieza anterior
                # colocada no hay de donde medir la siguiente.
                break
            colocacion = {
                "componente": cid,
                "instancia": 1,
                "centro": [round(v, 3) for v in centro],
                "rotacion": rotacion,
                "zona": "z_payload_banco",
            }
            salida.append(colocacion)
            puestas[cid] = colocacion
            borde = extremo

    for cid, cara, falta in sin_sitio:
        print(
            f"AVISO: {cid} no cabe en la rama {cara} del brazo de los beacons "
            f"por {falta:.1f} mm y NO se coloca. Ver el chequeo 'brazo_beacon' "
            f"y CLAUDE.md 3.9.",
            file=sys.stderr,
        )
    return salida, sin_sitio


def _franja(catalogo, x_espejo, recinto):
    """Colimador y cadena pre-codificacion en la franja, apilados en Y.

    ``recinto`` es ((xmin, ymin, zmin), (xmax, ymax, zmax)) de la franja, salvo
    que el colimador y el codificador SE SALEN de ella hacia -Z: el colimador
    arranca justo en el limite y el haz baja al banco. El limite en Z que
    manda para lo que hay que reservar es el otro, el +Z, que si es pared del
    6U.

    El orden en Z de la fila optica NO SE ELIGE: es el unico que permite que
    el tramo de fibra post-codificacion sea recto. De -Z a +Z van el colimador,
    el protector del empalme y el codificador, y lo que sobra -- o lo que falta
    -- se ve al final. Si el codificador se sale de la pared +Z, NO SE COLOCA:
    mismo criterio que la camara del brazo de los beacons.

    Devuelve (colocaciones, sin_sitio, datos), donde 'datos' lleva los numeros
    del tramo recto para que la cabecera del layout los pueda contar.
    """
    (xmin, ymin, zmin), (xmax, ymax, zmax) = recinto
    salida: list[dict] = []
    sin_sitio: list[tuple[str, float]] = []
    datos: dict[str, float] = {}

    codificador = next(
        (
            c for c in catalogo.componentes
            if c.funcion == "codificador_polarizacion" and c.cuenta_en_presupuesto
        ),
        None,
    )
    colimador = catalogo["colimador"] if catalogo.existe("colimador") else None

    # --- fila optica: colimador, empalme, codificador, de -Z a +Z ----------
    cursor_z = zmin
    banda_optica: list[tuple[float, float]] = []   # (ymin, ymax) de lo colocado
    if colimador is not None and colimador.modelable and x_espejo is not None:
        caja = caja_en_mundo(catalogo, colimador, GIRO_COLIMADOR)
        # El eje del colimador es el de su cilindro, o sea su propio centro: se
        # pone sobre el eje del espejo de plegado, que es lo que le devuelve el
        # haz a la linea de D1, y a Y = 0, que es el plano optico del banco.
        salida.append({
            "componente": colimador.id,
            "instancia": 1,
            "centro": [
                round(x_espejo, 3), 0.0,
                round(cursor_z - caja.zmin, 3),
            ],
            "rotacion": GIRO_COLIMADOR,
            "zona": "z_payload_franja",
        })
        banda_optica.append((caja.ymin, caja.ymax))
        cursor_z += caja.dims[2]
        datos["colimador_mm"] = caja.dims[2]

    protector = catalogo.integracion.get("fibra.longitud_protector_empalme")
    empalme = protector.escalar() if protector is not None else None
    if empalme is not None:
        cursor_z += empalme
        datos["protector_empalme_mm"] = empalme

    if codificador is not None and codificador.modelable:
        caja = caja_en_mundo(catalogo, codificador, GIRO_MODULADOR)
        datos["codificador_mm"] = caja.dims[2]
        banda_optica.append((caja.ymin, caja.ymax))
        # Coaxial con el colimador: lo que se alinea es el EJE DE FIBRA, que no
        # pasa por el centro del cuerpo.
        from clau3d import parts as _parts

        eje = _parts.eje_de_fibra_en_mundo(codificador, GIRO_MODULADOR)
        dx = 0.0 if eje is None else eje[0]
        dy = 0.0 if eje is None else eje[1]
        centro_z = cursor_z - caja.zmin
        extremo = centro_z + caja.zmax
        datos["necesario_mm"] = extremo - zmin
        datos["disponible_mm"] = zmax - zmin
        if extremo > zmax:
            sin_sitio.append((codificador.id, extremo - zmax))
        elif x_espejo is not None:
            salida.append({
                "componente": codificador.id,
                "instancia": 1,
                "centro": [
                    round(x_espejo - dx, 3), round(-dy, 3), round(centro_z, 3),
                ],
                "rotacion": GIRO_MODULADOR,
                "zona": "z_payload_franja",
            })

    # --- las dos bandas de Y, a partir de lo que ocupa la fila optica -------
    # Se miden sobre la GEOMETRIA del codificador y del colimador, este colocado
    # o no: si el reparto dependiera de que el codificador quepa, el layout
    # cambiaria de forma segun un resultado, que es justo lo que no puede pasar.
    y_alto = max((b[1] for b in banda_optica), default=0.0)
    y_bajo = min((b[0] for b in banda_optica), default=0.0)
    x_centro = (xmin + xmax) / 2

    for piezas, signo, borde in (
        (LANES_FRANJA_ARRIBA, +1, y_alto),
        (LANES_FRANJA_ABAJO, -1, y_bajo),
    ):
        cursor_y = borde + signo * HOLGURA_FRANJA
        cursor_z = zmin
        for cid in piezas:
            if not catalogo.existe(cid):
                continue
            componente = catalogo[cid]
            if not componente.modelable or not componente.cuenta_en_presupuesto:
                continue
            rotacion = (
                GIRO_MODULADOR_INVERTIDO if signo < 0 and componente.conectores
                else GIRO_MODULADOR
            )
            caja = caja_en_mundo(catalogo, componente, rotacion)
            centro_y = cursor_y - (caja.ymin if signo > 0 else caja.ymax)
            extremo_y = centro_y + (caja.ymax if signo > 0 else caja.ymin)
            pared = ymax if signo > 0 else ymin
            if signo * (extremo_y - pared) > 0:
                sin_sitio.append((cid, abs(extremo_y - pared)))
                break
            salida.append({
                "componente": cid,
                "instancia": 1,
                "centro": [
                    round(x_centro, 3), round(centro_y, 3),
                    round(cursor_z - caja.zmin, 3),
                ],
                "rotacion": rotacion,
                "zona": "z_payload_franja",
            })
            cursor_z += caja.dims[2] + HOLGURA_FRANJA
        # Las piezas de una misma banda comparten altura: van en fila segun Z,
        # no apiladas otra vez.

    for cid, falta in sin_sitio:
        print(
            f"AVISO: {cid} no cabe en la franja por {falta:.1f} mm y NO se "
            f"coloca. Ver el chequeo 'fibra_post_codificacion' y CLAUDE.md "
            f"3.10.",
            file=sys.stderr,
        )
    return salida, sin_sitio, datos


def _caja_mundo(catalogo, colocacion):
    """(min, max) de la pieza ya girada y situada."""
    componente = catalogo[colocacion["componente"]]
    dims = dims_en_mundo(catalogo, componente, colocacion["rotacion"])
    centro = colocacion["centro"]
    return (
        [centro[i] - dims[i] / 2 for i in range(3)],
        [centro[i] + dims[i] / 2 for i in range(3)],
    )


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
                _, _, dz = dims_en_mundo(catalogo, componente, rotacion)
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
        ancho_placa, espesor_placa, fondo_placa = bandeja.dimensiones.como_vector()
        # EL CONTORNO DE LA PLACA NO SE ESCRIBE, SE DERIVA: es su zona menos la
        # holgura de montaje por lado. Aqui se recalcula y se compara con lo
        # que el catalogo trae, porque una cota derivada escrita a mano deja de
        # estar derivada en cuanto cambia el reparto. Paso el 2026-09-21: al
        # subir el telescopio de 200 a 227 mm la bandeja se estrecho 27 mm y la
        # placa, con sus 102.4 mm de antes, se salia del 6U por 11.5 mm por
        # cada lado -- o sea rompiendo la invariante de "nada fuera de la
        # envolvente", que es de las dos que este repositorio defiende con
        # tests. Se aborta en vez de dibujarla mal, y se dice el numero.
        holgura_placa = catalogo.integracion["bandeja.holgura_montaje"].escalar()
        assert holgura_placa is not None
        derivado = (
            round(ancho_payload - 2 * holgura_placa, 3),
            round((z_banco_min - (-Z)) - 2 * holgura_placa, 3),
        )
        if (
            abs(ancho_placa - derivado[0]) > 1e-6
            or abs(fondo_placa - derivado[1]) > 1e-6
        ):
            raise SystemExit(
                f"bandeja_optica: la placa mide {ancho_placa} x {fondo_placa} mm "
                f"en X y Z y su zona pide {derivado[0]} x {derivado[1]} "
                f"(z_payload_bandeja menos {holgura_placa:.0f} mm por lado). "
                f"El contorno de la placa se DERIVA de la zona, no se elige: "
                f"escribe [{derivado[0]}, {espesor_placa}, {derivado[1]}] en "
                f"forma.dimensiones y vuelve a generar. El espesor si es una "
                f"decision y no se toca."
            )
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
    sin_sitio_bandeja: list[tuple[str, float]] = []
    for fila in FILAS_BANDEJA:
        piezas = []
        for cid in fila:
            componente = catalogo[cid]
            if not componente.modelable:
                continue
            rotacion = rotacion_de_montaje(componente, "+Y")
            piezas.append((componente, rotacion, dims_en_mundo(catalogo, componente, rotacion)))
        if not piezas:
            continue
        # UNA PIEZA QUE NO CABE NO SE COLOCA, y no se aprieta la fila para que
        # entre: apretando saldrian solapes de decimas de milimetro que el
        # informe marcaria sin que se entendiera por que. Se van soltando
        # piezas por el final -- la fila esta en el orden de la cadena, asi que
        # la ultima es la que menos ata -- y se avisa por stderr, que es el
        # mismo criterio que el brazo de los beacons y que la franja. Antes
        # esto tumbaba el generador entero; con el modulo del beacon metido en
        # la fila del DFB eso habria escondido todo el resto del modelo por una
        # pieza.
        while piezas and sum(dims[0] for _, _, dims in piezas) > ancho_util:
            fuera, _, dims_fuera = piezas.pop()
            sin_sitio_bandeja.append(
                (fuera.id, sum(d[2][0] for d in piezas) + dims_fuera[0] - ancho_util)
            )
        if not piezas:
            continue
        fondo = max(dims[2] for _, _, dims in piezas)
        ancho_total = sum(dims[0] for _, _, dims in piezas)
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
    for cid, falta in sin_sitio_bandeja:
        print(
            f"AVISO: {cid} no cabe en su fila de la bandeja por {falta:.1f} mm "
            f"y NO se coloca. Parte la fila en dos en FILAS_BANDEJA o revisa "
            f"su envolvente.",
            file=sys.stderr,
        )
    z_libre_bandeja = z_banco_min - (cursor_z - HOLGURA_BANDEJA)

    # ----------------------------------------------------------------- banco
    x_eje_telescopio = (x_sep + x_franja_min) / 2
    z_eje_banco = (z_banco_min + z_tel_min) / 2

    fsm = catalogo["fsm"]
    margen_banco = None
    x_espejo = None
    sin_sitio_brazo: list[tuple[str, str, float]] = []
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
        # Hacia +X desde el FSM: D1 y el espejo de plegado, en orden inverso
        # al de la cadena porque la cadena viene de fuera hacia el espejo del
        # FSM. El colimador YA NO ESTA EN ESTA LINEA: esta encima del espejo de
        # plegado, apuntando -Z, y se coloca con la franja.
        cursor_x = x_eje_telescopio + dims_en_mundo(catalogo, fsm, GIRO_FSM)[0] / 2
        x_d1 = None
        # EL ESPEJO DE PLEGADO NO SE COMPACTA CONTRA D1: va ANCLADO bajo la
        # franja. Encima de el, apuntando -Z, esta el colimador, y el colimador
        # tiene que caer entero dentro de la franja -- si se sale hacia -X
        # entra en la zona del telescopio, donde esta el barrilete, y choca.
        # Mientras las piezas del banco eran gordas la linea compactada ya
        # dejaba al espejo bastante hacia +X y no se veia; al bajar las celdas
        # de 23 y 20 a 16 mm la linea se encoge 11 mm hacia el FSM y el
        # colimador se mete en el barrilete. Asi que el espejo tiene un minimo:
        # que el colimador quepa en la franja con su holgura. El chequeo
        # 'espejo_bajo_la_franja' lo vuelve a comprobar sobre el layout.
        x_minimo_espejo = None
        if catalogo.existe("colimador") and catalogo["colimador"].modelable:
            radio_colimador = (
                caja_en_mundo(catalogo, catalogo["colimador"], GIRO_COLIMADOR).dims[0]
                / 2
            )
            x_minimo_espejo = x_franja_min + radio_colimador + HOLGURA_BANCO
        for cid in reversed(CADENA_BANCO):
            componente = catalogo[cid]
            if not componente.modelable:
                continue
            rotacion = rotacion_de_montaje(componente, "+Y")
            dx, dy, dz = dims_en_mundo(catalogo, componente, rotacion)
            cursor_x += HOLGURA_BANCO
            centro_x = cursor_x + dx / 2
            if cid == "espejo_plegado_cuantico" and x_minimo_espejo is not None:
                centro_x = max(centro_x, x_minimo_espejo)
                cursor_x = centro_x - dx / 2
            colocaciones.append(
                {
                    "componente": cid,
                    "instancia": 1,
                    "centro": [round(centro_x, 3), 0.0, round(z_eje_banco, 3)],
                    "rotacion": rotacion,
                    "zona": "z_payload_banco",
                }
            )
            if cid == "dicroico_d1":
                x_d1 = centro_x
            if cid == "espejo_plegado_cuantico":
                x_espejo = centro_x
            cursor_x += dx
        margen_banco = X - MARGEN_BANCO - cursor_x

        # El brazo de los beacons. Cada rama sale de una pieza ya colocada,
        # asi que se recorren en orden y se lee el centro y la envolvente de la
        # estacion del propio acumulador de colocaciones: asi D2, que es
        # estacion de dos ramas, no hay que situarlo dos veces.
        if x_d1 is not None:
            del_brazo, sin_sitio_brazo = _ramas_del_brazo(
                catalogo,
                colocaciones,
                ([x_sep, -Y, z_banco_min], [X, Y, z_tel_min]),
            )
            colocaciones += del_brazo

    # --------------------------------------------------------------- franja
    # Va DESPUES del banco a proposito: la X del codificador y la del colimador
    # no son libres, salen de donde cae el espejo de plegado, y el espejo cae
    # donde lo deja la linea del banco.
    del_franja, sin_sitio_franja, franja = _franja(
        catalogo,
        x_espejo,
        ([x_franja_min, -Y, z_tel_min], [X, Y, Z]),
    )
    colocaciones += del_franja

    # ------------------------------------------------------------ telescopio
    # El barrilete llena su zona: su envolvente es la COTA SUPERIOR (el
    # diametro es la altura interior del 6U) y la longitud es la reservada. Si
    # llega el STEP con un diametro menor, la zona se queda igual y sobra sitio
    # alrededor, que es lo que se quiere ver.
    telescopio = catalogo["telescopio_cassegrain"]
    if telescopio.modelable:
        _, _, l_tubo = dims_en_mundo(catalogo, telescopio, [0, 0, 0])
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
        _, _, espesor = dims_en_mundo(catalogo, antena, [0, 0, 0])
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

    # ----------------------------------------------------------- keep-outs
    # Las zonas se construyen mas abajo, pero los keep-outs se recortan a
    # ellas, asi que aqui hace falta su geometria. Es la misma que usa la
    # tabla 'zonas'.
    from clau3d.structure import Caja as _Caja

    recintos = {
        "z_plataforma": _Caja(-X, -Y, -Z, x_sep, Y, Z),
        "z_payload_telescopio": _Caja(x_sep, -Y, z_tel_min, x_franja_min, Y, Z),
        "z_payload_franja": _Caja(x_franja_min, -Y, z_tel_min, X, Y, Z),
        "z_payload_banco": _Caja(x_sep, -Y, z_banco_min, X, Y, z_tel_min),
        "z_payload_bandeja": _Caja(x_sep, -Y, -Z, X, Y, z_banco_min),
    }
    keep_outs = generar_keep_outs(catalogo, colocaciones, recintos)

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
            "Franja lateral - modulacion, monitorizacion, atenuacion y codificacion",
            (x_franja_min, -Y, z_tel_min), (X, Y, Z),
            f"Los {ancho_franja:.1f} mm de X que quedan al lado del telescopio, "
            f"a lo largo de toda su longitud. El ancho no se ha elegido: el "
            f"barrilete no puede pasar de los {iy:.1f} mm de altura interior, "
            f"asi que esta franja existe para cualquier diametro que permita "
            f"montar el telescopio. Desde el 2026-09-21 aqui va TODO lo que hay "
            f"entre la fuente y el colimador -- MXER, acoplador 2x2, VOA y el "
            f"codificador de polarizacion -- mas el propio colimador, porque "
            f"todo componente de fibra tiene que ir ANTES del codificador y el "
            f"codificador tiene que alimentar al colimador en linea recta. "
            f"EL REPARTO ES EN BANDAS DE Y, y no se ha elegido: la franja tiene "
            f"{ancho_franja:.1f} mm de X contra {iy:.1f} mm de Y, y la X del "
            f"codificador esta PINCHADA por la coaxialidad con el colimador. "
            f"Los bucles de fibra van en el plano Y-Z por el mismo motivo: con "
            f"el radio modelado hacen falta 60 mm de diametro y en X no caben. "
            + (
                "EL TRAMO RECTO NO CABE: "
                + "; ".join(
                    f"{cid} se sale por {falta:.1f} mm y NO esta colocado"
                    for cid, falta in sin_sitio_franja
                )
                + ". Ver el chequeo 'fibra_post_codificacion' y CLAUDE.md 3.10."
                if sin_sitio_franja
                else f"El tramo recto del codificador al colimador cabe: pide "
                     f"{franja.get('necesario_mm', 0):.1f} mm de los "
                     f"{franja.get('disponible_mm', 0):.1f} que hay."
            ),
        ),
        (
            "z_payload_banco",
            "Banco optico de espacio libre",
            (x_sep, -Y, z_banco_min), (X, Y, z_tel_min),
            f"Canal cuantico: el colimador baja el haz segun -Z desde la "
            f"franja, el espejo de plegado lo dobla hacia -X y de ahi "
            f"D1 -> FSM -> telescopio. De D1 "
            f"sale hacia +Y UN SOLO brazo para los dos beacons, y dentro de el "
            f"D2 los separa: la camara en transmision (976 nm) y el laser de "
            f"bajada inyectando lateralmente en reflexion (1064 nm). Los dos "
            f"cuartos puertos llevan su trampa y su fotodiodo. El FSM esta "
            f"sobre el eje optico del telescopio (X = {x_eje_telescopio:+.2f}) "
            f"porque es el que dobla el haz de X a Z, y eso deja D1 y el "
            f"espejo de plegado en linea hacia +X. Margen contra la pared +X: "
            + (f"{margen_banco:.1f} mm." if margen_banco is not None
               else "no calculable, faltan envolventes.")
            + (
                " EL BRAZO NO CABE: "
                + "; ".join(
                    f"{cid} se sale por la rama {cara} en {falta:.1f} mm y NO "
                    f"esta colocado"
                    for cid, cara, falta in sin_sitio_brazo
                )
                + ". Apretarlo hasta que entrara, o dibujarlo saliendose del "
                  "satelite, seria esconder el resultado. Ver el chequeo "
                  "'brazo_beacon' y CLAUDE.md 3.9."
                if sin_sitio_brazo
                else " El brazo de los beacons cabe entero."
            ),
        ),
        (
            "z_payload_bandeja",
            "Bandeja optica de fibra",
            (x_sep, -Y, -Z), (X, Y, z_banco_min),
            f"{iz - l_telescopio - L_BANCO:.1f} mm de Z con los "
            f"{ancho_payload:.1f} mm de ancho enteros. Desde el 2026-09-21 "
            f"aqui esta SOLO LA FUENTE: el laser DFB, el aislador y el filtro. "
            f"Todo lo que modula, monitoriza, atenua y codifica esta en la "
            f"franja, asi que la cadena cruza de zona UNA SOLA VEZ, y esa vez "
            f"cae en el tramo pre-codificacion, que es el que se puede curvar. "
            f"Las filas avanzan segun Z en el orden y el sentido de la cadena: "
            f"el laser al extremo -Z, lo mas lejos posible del barrilete porque "
            f"con sus 4.1 W es la principal fuente de calor del payload, y la "
            f"salida hacia la franja en +Z. Quedan {z_libre_bandeja:.1f} mm de "
            f"Z libres al final para los bucles, mas los huecos entre filas. "
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
        "  fecha: 2026-09-21",
        "  nota: >-",
        f"    Dos columnas de 3U a lo largo de todo Z. La pila PC104 queda holgada:",
        f"    {usado:.0f} mm usados de {iz:.0f} mm. La columna de payload mide",
        f"    {ancho_payload:.1f} mm de ancho y se parte en dos a lo largo del telescopio:",
        f"    {iy:.1f} mm para el barrilete y {ancho_franja:.1f} mm de franja lateral.",
        "    REPARTO REVISADO EL 2026-09-21 (CLAUDE.md 3.10): la bandeja se queda",
        "    con la FUENTE -- laser, aislador y filtro -- y la franja lleva todo lo",
        "    que modula, monitoriza, atenua y codifica, apilado en BANDAS DE Y,",
        "    porque todo componente de fibra tiene que ir antes del codificador de",
        "    polarizacion y despues de el la fibra no se puede curvar. Asi la",
        "    cadena cruza de zona una sola vez, y esa vez es pre-codificacion.",
        f"    El telescopio reserva {l_telescopio:.0f} mm. PCB-2 sigue",
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
        "# Volumenes reservados. TODOS salen de numeros SUPUESTOS: el radio",
        "# minimo de curvatura de la fibra, el del coaxial y el diametro de haz",
        "# siguen siendo TBD. Por eso cada uno lleva su estado y su fuente, y",
        "# por eso invadir uno NO tumba el codigo de salida de `clau3d informe`:",
        "# no es un choque de geometrias, es la consecuencia de una hipotesis.",
        "keep_out:" if keep_outs else "keep_out: []",
    ]
    for k in keep_outs:
        lineas += [
            f"  - id: {k['id']}",
            f"    tipo: {k['tipo']}",
            f"    estado: {k['estado']}",
        ]
        if k.get("de_pieza"):
            lineas.append(f"    de_pieza: {k['de_pieza']}")
        lineas += ["    fuente: >-"]
        lineas += [f"      {t}" for t in _envolver(k["fuente"], 66)]
        lineas += [
            "    caja:",
            f"      min: [{k['min'][0]}, {k['min'][1]}, {k['min'][2]}]",
            f"      max: [{k['max'][0]}, {k['max'][1]}, {k['max'][2]}]",
            "    nota: >-",
        ]
        lineas += [f"      {t}" for t in _envolver(k["nota"], 66)]
    lineas += [
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
