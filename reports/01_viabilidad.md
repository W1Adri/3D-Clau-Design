# Chequeos de viabilidad

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (14 piezas colocadas)

Comprobaciones que no dependen de donde se coloque cada pieza.

## Volumen total frente a la zona util

**Estado: ATENCION**

Los 13 componentes con envolvente conocida ocupan 1452 cm3 de los 7644 cm3 interiores (19%). Quedan 13 componentes sin envolvente: el dato real sera mayor.

| magnitud | valor |
|---|---|
| interior_cm3 | 7643.68 |
| ocupado_conocido_cm3 | 1451.65 |
| libre_si_nada_mas_creciera_cm3 | 6192.02 |
| fraccion_ocupada | 0.19 |
| componentes_sin_volumen | 13 |

Falta: Envolvente de: antena_quasar_wsant, radio_uhf_pulsar_vutrx, paneles_photon_side, propulsion, telescopio_cassegrain, fsm, dicroico, camara_beacon, laser_beacon_bajada, colimador, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat

## Apertura del telescopio frente a la seccion interior

**Estado: ATENCION**

La apertura de 90 mm deja solo 2.7 mm por lado dentro de los 95 mm interiores. No hay sitio para el barrilete, la celda del espejo ni el ajuste de alineacion. El eje optico NO puede ir paralelo a Y, y en cualquier otra orientacion la seccion util sigue limitada por Y.

| magnitud | valor |
|---|---|
| apertura_libre_mm | 90.00 |
| altura_exterior_mm | 100.00 |
| altura_interior_util_mm | 95.40 |
| holgura_por_lado_mm | 2.70 |

Falta: Diametro exterior del barrilete (la apertura libre no basta)

## Contorno PC104 frente a la seccion interior

**Estado: ATENCION**

La tarjeta de 95.89 x 90.17 mm cabe en 221.7 x 95.4 mm, pero deja solo 5.23 mm de holgura en Y. El espesor de pared no puede pasar de 4.91 mm, cota mas holgada que la que fija el iADCS400. Ademas, la zona util sale de un modelo de CAJA CON PAREDES de espesor uniforme, y el chasis 6U real es un ARMAZON CON RAILES: el hueco util no es un prisma, varia con Z y con la cara. Este chequeo no sera concluyente hasta sustituir el modelo por el STEP del chasis del equipo.

| magnitud | valor |
|---|---|
| contorno_largo_mm | 95.89 |
| contorno_ancho_mm | 90.17 |
| interior_X_mm | 221.70 |
| interior_Y_mm | 95.40 |
| espesor_pared_supuesto_mm | 2.30 |
| espesor_pared_maximo_mm | 4.91 |

Falta: Zona util real del chasis 6U del equipo (STEP o plano con railes)

## Seccion interior frente a todas las piezas

**Estado: NO COMPROBABLE**

NO CONCLUYENTE. El espesor de pared supuesto (2.30 mm) coincide con el maximo compatible (2.30 mm): el margen es de 0.00 mm. Pero esa cota se DEDUJO de 'adcs_iadcs400', asi que decir que 'adcs_iadcs400' cabe con 0.00 mm de holgura no comprueba nada; es la hipotesis devuelta tal cual. El resto de piezas si tienen holgura real frente a esta seccion, pero la pieza que manda no. Ademas, la zona util sale de un modelo de CAJA CON PAREDES de espesor uniforme, y el chasis 6U real es un ARMAZON CON RAILES: el hueco util no es un prisma, varia con Z y con la cara. Este chequeo no sera concluyente hasta sustituir el modelo por el STEP del chasis del equipo.

| magnitud | valor |
|---|---|
| espesor_supuesto_mm | 2.30 |
| espesor_maximo_compatible_mm | 2.30 |
| interior_X_mm | 221.70 |
| interior_Y_mm | 95.40 |
| interior_Z_mm | 361.40 |
| piezas_que_no_caben | 0.00 |
| margen_de_espesor_mm | 0.00 |

Falta: Zona util real del chasis 6U del equipo (STEP o plano con railes)

## Recorrido recto de Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM)

**Estado: OK**

Los 130 mm de recorrido recto solo caben orientados segun X, Z. Esto ya fija la orientacion de la bandeja optica, antes de anadir los bucles de fibra.

| magnitud | valor |
|---|---|
| longitud_con_fibras_mm | 130.00 |
| interior_X_mm | 221.70 |
| interior_Y_mm | 95.40 |
| interior_Z_mm | 361.40 |

## Recorrido recto de Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion)

**Estado: OK**

Los 130 mm de recorrido recto solo caben orientados segun X, Z. Esto ya fija la orientacion de la bandeja optica, antes de anadir los bucles de fibra.

| magnitud | valor |
|---|---|
| longitud_con_fibras_mm | 130.00 |
| interior_X_mm | 221.70 |
| interior_Y_mm | 95.40 |
| interior_Z_mm | 361.40 |

## Longitud de la pila PC104

**Estado: OK**

Con el paso estandar PC/104 de 15.24 mm, las 6 tarjetas de altura conocida ocupan 14 posiciones de separador, o sea 213 mm. Reservando una posicion por cada una de las 4 tarjetas sin altura (61 mm mas), la pila suma 274 mm frente a 361 mm interiores. El paso REAL del chasis sigue siendo TBD: este numero es una estimacion con el paso de la norma, no el del chasis elegido.

| magnitud | valor |
|---|---|
| tarjetas_con_altura | 6.00 |
| suma_alturas_mm | 153.63 |
| interior_Z_mm | 361.40 |
| tarjetas_sin_altura | 4.00 |
| paso_modelado_mm | 15.24 |
| posiciones_de_separador | 14.00 |
| longitud_modelada_mm | 213.36 |
| reserva_tarjetas_sin_altura_mm | 60.96 |

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

## STEP de fabricante frente al manifiesto

**Estado: OK**

4 de 4 CAD de fabricante presentes y con la huella del manifiesto.

| magnitud | valor |
|---|---|
| declarados | 4.00 |
| presentes | 4.00 |
| ausentes | 0.00 |
| huella_distinta | 0.00 |
| sin_declarar | 0.00 |
| esperando_step | 0.00 |
| aparecidos_sin_verificar | 0.00 |

