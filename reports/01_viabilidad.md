# Chequeos de viabilidad

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **propuesta**

> **La distribucion aun NO esta confirmada.** Las posiciones de este informe son una propuesta pendiente de validar por el equipo. El analisis de interferencias solo es concluyente sobre las piezas realmente colocadas.

Comprobaciones que no dependen de donde se coloque cada pieza.

## Volumen total frente a la zona util

**Estado: ATENCION**

Los 7 componentes con envolvente conocida ocupan 1394 cm3 de los 6956 cm3 interiores (20%). Quedan 19 componentes sin envolvente: el dato real sera mayor.

| magnitud | valor |
|---|---|
| interior_cm3 | 6955.98 |
| ocupado_conocido_cm3 | 1394.06 |
| libre_si_nada_mas_creciera_cm3 | 5561.92 |
| fraccion_ocupada | 0.20 |
| componentes_sin_volumen | 19 |

Falta: Envolvente de: antena_quasar_wsant, radio_uhf_pulsar_vutrx, paneles_photon_side, propulsion, telescopio_cassegrain, fsm, dicroico, camara_beacon, laser_beacon_bajada, colimador, bandeja_optica, laser_dfb_1550, voa, aislador, filtro_espectral, acoplador_monitor, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat

## Apertura del telescopio frente a la seccion interior

**Estado: ATENCION**

La apertura de 90 mm deja solo 0.1 mm por lado dentro de los 90 mm interiores. No hay sitio para el barrilete, la celda del espejo ni el ajuste de alineacion. El eje optico NO puede ir paralelo a Y, y en cualquier otra orientacion la seccion util sigue limitada por Y.

| magnitud | valor |
|---|---|
| apertura_libre_mm | 90.00 |
| altura_exterior_mm | 100.00 |
| altura_interior_util_mm | 90.20 |
| holgura_por_lado_mm | 0.10 |

Falta: Diametro exterior del barrilete (la apertura libre no basta)

## Contorno PC104 frente a la seccion interior

**Estado: ATENCION**

La tarjeta de 95.89 x 90.17 mm cabe en 216.5 x 90.2 mm, pero deja solo 0.03 mm de holgura en Y. El espesor de pared no puede pasar de 4.91 mm: es el chasis quien decide, y aun es una hipotesis.

| magnitud | valor |
|---|---|
| contorno_largo_mm | 95.89 |
| contorno_ancho_mm | 90.17 |
| interior_X_mm | 216.50 |
| interior_Y_mm | 90.20 |
| espesor_pared_supuesto_mm | 4.90 |
| espesor_pared_maximo_mm | 4.91 |

Falta: Zona util real del chasis 6U del equipo

## Recorrido recto de Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM)

**Estado: OK**

Los 130 mm de recorrido recto solo caben orientados segun X, Z. Esto ya fija la orientacion de la bandeja optica, antes de anadir los bucles de fibra.

| magnitud | valor |
|---|---|
| longitud_con_fibras_mm | 130.00 |
| interior_X_mm | 216.50 |
| interior_Y_mm | 90.20 |
| interior_Z_mm | 356.20 |

## Recorrido recto de Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion)

**Estado: OK**

Los 130 mm de recorrido recto solo caben orientados segun X, Z. Esto ya fija la orientacion de la bandeja optica, antes de anadir los bucles de fibra.

| magnitud | valor |
|---|---|
| longitud_con_fibras_mm | 130.00 |
| interior_X_mm | 216.50 |
| interior_Y_mm | 90.20 |
| interior_Z_mm | 356.20 |

## Longitud de la pila PC104

**Estado: NO COMPROBABLE**

Las 6 tarjetas con altura conocida suman 154 mm, pero eso es una COTA INFERIOR: las fichas AAC dan la altura 'from top PCB to lowest component', no el paso entre tarjetas. Faltan ademas 4 tarjetas sin altura (radio_uhf_pulsar_vutrx, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat).

| magnitud | valor |
|---|---|
| tarjetas_con_altura | 6.00 |
| suma_alturas_mm | 153.63 |
| interior_Z_mm | 356.20 |
| tarjetas_sin_altura | 4.00 |

Falta: Paso de apilamiento PC104 del chasis elegido

## Radio minimo de curvatura de la fibra

**Estado: NO COMPROBABLE**

Sin radio minimo de curvatura no se puede dimensionar la bandeja optica ni comprobar ningun bucle. Es el parametro que mas area consume de toda la bandeja.

Falta: Radio minimo de curvatura de la fibra elegida

## Presupuesto de masa

**Estado: ATENCION**

Masa conocida 846 g de un limite de 12000 g (CDS 14.1). Faltan 24 componentes por pesar, incluido el chasis y el telescopio, que son de los mas pesados.

| magnitud | valor |
|---|---|
| masa_conocida_g | 845.90 |
| limite_g | 12000.00 |
| margen_g | 11154.10 |
| componentes_sin_masa | 24.00 |

Falta: Masa de: estructura_6u, adcs_iadcs400, antena_quasar_wsant, radio_uhf_pulsar_vutrx, paneles_photon_side, propulsion, telescopio_cassegrain, fsm, dicroico, camara_beacon, laser_beacon_bajada, colimador, bandeja_optica, laser_dfb_1550, mod_intensidad_mxer_ln_10, mod_fase_mpz_ln_10, voa, aislador, filtro_espectral, acoplador_monitor, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat, qrng_idq20mc1_s3

