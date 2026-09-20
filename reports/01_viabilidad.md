# Chequeos de viabilidad

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (26 piezas colocadas)

Comprobaciones que no dependen de donde se coloque cada pieza.

## Volumen total frente a la zona util

**Estado: ATENCION**

Los 24 componentes con envolvente conocida ocupan 4302 cm3 de los 7644 cm3 interiores (56%). Quedan 3 componentes sin envolvente: el dato real sera mayor.

| magnitud | valor |
|---|---|
| interior_cm3 | 7643.68 |
| ocupado_conocido_cm3 | 4302.48 |
| libre_si_nada_mas_creciera_cm3 | 3341.20 |
| fraccion_ocupada | 0.56 |
| componentes_sin_volumen | 3 |

Falta: Envolvente de: radio_uhf_pulsar_vutrx, propulsion, cables_rf_moduladores

## Apertura del telescopio frente a la seccion interior

**Estado: ATENCION**

Con seccion CUADRADA de 95.4 mm y 90 mm de apertura quedan 2.7 mm hasta la cara plana y 22.5 mm hasta la esquina. Los dos numeros son el mismo problema visto por dos lados: en la cara plana no cabe nada (pared, baffle y holgura ya se comen esos 2.7 mm), y la celda del primario, los flexures y los largueros estructurales tienen que ir en las esquinas. Con un barrilete de REVOLUCION solo existiria el primer numero, en todas las direcciones. El eje optico NO puede ir paralelo a Y, y en cualquier otra orientacion la seccion util sigue limitada por Y. Si la esquina tampoco bastara, la salida es que el barrilete sea el elemento estructural de esa cara.

| magnitud | valor |
|---|---|
| apertura_libre_mm | 90.00 |
| altura_exterior_mm | 100.00 |
| altura_interior_util_mm | 95.40 |
| holgura_por_lado_mm | 2.70 |
| holgura_cara_plana_mm | 2.70 |
| holgura_esquina_mm | 22.46 |

Falta: Contorno exterior del barrilete (la apertura libre no basta)

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

Con el paso estandar PC/104 de 15.24 mm, las 9 tarjetas de altura conocida ocupan 20 posiciones de separador, o sea 305 mm. Reservando una posicion por cada una de las 1 tarjetas sin altura (15 mm mas), la pila suma 320 mm frente a 361 mm interiores. El paso REAL del chasis sigue siendo TBD: este numero es una estimacion con el paso de la norma, no el del chasis elegido.

| magnitud | valor |
|---|---|
| tarjetas_con_altura | 9.00 |
| suma_alturas_mm | 246.15 |
| interior_Z_mm | 361.40 |
| tarjetas_sin_altura | 1.00 |
| paso_modelado_mm | 15.24 |
| posiciones_de_separador | 20.00 |
| longitud_modelada_mm | 304.80 |
| reserva_tarjetas_sin_altura_mm | 15.24 |

Falta: Paso de apilamiento PC104 del chasis elegido

## Cadena de espacio libre entre el eje del telescopio y la pared

**Estado: OK**

El FSM va sobre el eje optico del telescopio (X = +36.85 mm) porque es el que dobla el haz de X a Z. Del eje a la pared +X de la columna hay 74.0 mm, y la media anchura del FSM mas el dicroico mas el colimador suman 66.3 mm, sin contar holguras de montaje. Quedan 7.7 mm de margen.

| magnitud | valor |
|---|---|
| fsm | 15.29 |
| dicroico | 23.00 |
| colimador | 28.00 |
| necesario_mm | 66.29 |
| disponible_mm | 74.00 |
| margen_mm | 7.71 |

## Configuracion optica del telescopio

**Estado: OK**

Afocal tipo Mersenne: dos parabolas confocales, M = 9.00. Entra colimado y sale colimado, asi que NO hay foco real dentro del satelite y no hace falta ninguna lente de enfoque en el banco. El foco comun de las dos conicas es VIRTUAL y por eso el modelo no dibuja ningun marcador ahi: no hay nada. Obstruccion lineal 0.156 (secundario de 14.0 mm sobre 90 mm), o sea 0.21 dB en amplitud de campo (0.11 dB en potencia).

| magnitud | valor |
|---|---|
| magnificacion | 9.00 |
| focal_primario_mm | 200.00 |
| focal_secundario_mm | 22.22 |
| separacion_mm | 177.78 |
| obstruccion_lineal | 0.16 |
| perdida_obstruccion_dB_amplitud | 0.21 |

## Longitud del telescopio frente a la reservada

**Estado: ATENCION**

Con f1 = 200 mm y M = 9.00 la separacion entre vertices es 177.8 mm, que no se puede tocar sin cambiar la optica. Para los 200 mm reservados eso deja 22.2 mm para los dos mamparos, la celda y los dos espejos. Cabe por 1.2 mm, que no es margen: los espesores con los que se dibuja (mamparos de 3 mm, celda de 3 mm, primario de 8 mm) estan todos en su COTA SUPERIOR, no elegidos. Cualquiera de ellos que crezca deja de caber. Con los ~2U de verdad del brief (227 mm, no 200: la U de longitud de la CDS son 113.5 mm) la misma optica tendria 28 mm de margen. Alargar se paga con la bandeja y es decision de ACSAR.

| magnitud | valor |
|---|---|
| longitud_reservada_mm | 200.00 |
| separacion_vertices_mm | 177.78 |
| estructura_mm | 22.22 |
| longitud_necesaria_mm | 198.78 |
| margen_mm | 1.22 |
| focal_primario_mm | 200.00 |
| magnificacion | 9.00 |

Falta: Longitud real del telescopio (STEP de Aperture Optical Sciences)

## El haz comprimido frente al espejo del FSM

**Estado: NO COMPROBABLE**

El espejo del FSM mide 5.0 mm, y un haz a 45 grados deja una huella de d x d*raiz(2), asi que solo admite un haz de 3.54 mm. Con 90 mm de apertura eso exige una magnificacion de al menos 25.5. Con el haz SUPUESTO con el que se dibuja (10 mm, de integracion.optica.diametro_haz_modelado) la huella seria 10 x 14.1 mm y NO CABRIA en el espejo de 5 mm. Si el equipo de optica confirma un haz de ese orden, el MEMS DIP24 queda descartado y hay que ir al 'fsm_piezo_pi_s331' (que pesa 130 g frente a los gramos del MEMS) o subir la magnificacion de 9.0 a 25.5, lo que reduce el secundario y alarga el tubo. Punto de adelanto: 50.7 urad en el cielo son 456 urad opticos en el haz comprimido (228 urad de giro mecanico del espejo) con M = 9.00, porque un afocal comprime los angulos por M. Es poco para cualquiera de las dos tecnologias -- el piezo S-331 da 3 mrad --, asi que el recorrido NO es lo que decide: lo que decide es el tamano del espejo.

| magnitud | valor |
|---|---|
| diametro_espejo_fsm_mm | 5.00 |
| haz_maximo_admisible_mm | 3.54 |
| magnificacion_minima | 25.46 |
| magnificacion_modelada | 9.00 |
| haz_modelado_mm | 10.00 |
| huella_a_45_mm | 14.14 |
| punto_de_adelanto_urad | 50.70 |
| recorrido_optico_en_el_fsm_urad | 456.30 |
| giro_mecanico_en_el_fsm_urad | 228.15 |

Falta: Diametro del haz comprimido (telescopio_cassegrain.optica.diametro_haz_comprimido y diametro_haz_mm de e01..e05). Es el dato que DECIDE el TBD 'fsm.eleccion_de_tecnologia': sin el no se puede elegir entre el MEMS y el piezo.

## Radio minimo de curvatura de la fibra

**Estado: NO COMPROBABLE**

Sin radio minimo de curvatura no se puede dimensionar la bandeja optica ni comprobar ningun bucle. Es el parametro que mas area consume de toda la bandeja. Mientras tanto, los keep-outs se dibujan con un radio SUPUESTO de 30 mm y un tramo recto de 20 mm, o sea 50 mm reservados por puerto. Con esa hipotesis la bandeja NO cumple: ver las invasiones de keep-out en el informe de interferencias. Eso no es un fallo del reparto, es lo que cuesta no tener el dato: si el radio real resulta ser la mitad, la mayoria de esas invasiones desaparecen solas.

| magnitud | valor |
|---|---|
| radio_supuesto_mm | 30.00 |
| boot_supuesto_mm | 20.00 |
| reserva_por_puerto_mm | 50.00 |

Falta: Radio minimo de curvatura de la fibra elegida

## Presupuesto de masa

**Estado: ATENCION**

Masa conocida 846 g de un limite de 12000 g (CDS 14.1). Faltan 25 componentes por pesar, incluido el chasis y el telescopio, que son de los mas pesados.

| magnitud | valor |
|---|---|
| masa_conocida_g | 845.90 |
| limite_g | 12000.00 |
| margen_g | 11154.10 |
| componentes_sin_masa | 25.00 |

Falta: Masa de: estructura_6u, adcs_iadcs400, antena_quasar_wsant, radio_uhf_pulsar_vutrx, paneles_photon_side, propulsion, telescopio_cassegrain, fsm, dicroico, camara_beacon, laser_beacon_bajada, colimador, bandeja_optica, laser_dfb_1550, mod_intensidad_mxer_ln_10, mod_fase_mpz_ln_10, voa, aislador, filtro_espectral, acoplador_monitor, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat, cables_rf_moduladores, qrng_idq20mc1_s3

## STEP de fabricante frente al manifiesto

**Estado: ATENCION**

4 de 4 CAD de fabricante presentes y con la huella del manifiesto. 1 pieza espera un STEP que aun no ha llegado; mientras tanto se dibuja con su envolvente aproximada. Dejar el fichero en la ruta indicada basta para que el modelo lo use: telescopio_cassegrain -> cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step (a Oscar (ACSAR) / Aperture Optical Sciences).

| magnitud | valor |
|---|---|
| declarados | 4.00 |
| presentes | 4.00 |
| ausentes | 0.00 |
| huella_distinta | 0.00 |
| sin_declarar | 0.00 |
| esperando_step | 1.00 |
| aparecidos_sin_verificar | 0.00 |

Falta: STEP por recibir: telescopio_cassegrain (a Oscar (ACSAR) / Aperture Optical Sciences)

