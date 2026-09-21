# Chequeos de viabilidad

Generado automaticamente el 2026-09-21 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (31 piezas colocadas)

Comprobaciones que no dependen de donde se coloque cada pieza.

## Volumen total frente a la zona util

**Estado: ATENCION**

Los 29 componentes con envolvente conocida ocupan 4531 cm3 de los 7644 cm3 interiores (59%). Quedan 3 componentes sin envolvente: el dato real sera mayor.

| magnitud | valor |
|---|---|
| interior_cm3 | 7643.68 |
| ocupado_conocido_cm3 | 4531.20 |
| libre_si_nada_mas_creciera_cm3 | 3112.48 |
| fraccion_ocupada | 0.59 |
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

El FSM va sobre el eje optico del telescopio (X = +36.85 mm) porque es el que dobla el haz de X a Z. Del eje a la pared +X de la columna hay 74.0 mm, y la media anchura del FSM mas el D1 mas el espejo de plegado suman 47.3 mm, sin contar holguras de montaje. Quedan 26.7 mm de margen.

| magnitud | valor |
|---|---|
| fsm | 15.29 |
| dicroico_d1 | 16.00 |
| espejo_plegado_cuantico | 16.00 |
| necesario_mm | 47.29 |
| disponible_mm | 74.00 |
| margen_mm | 26.71 |
| camara_beacon_mm | 30.00 |
| margen_-X_D2_mm | 32.99 |
| fotodiodo_monitor_beacon_mm | 12.00 |
| margen_+X_D2_mm | 30.71 |

## El espejo de plegado frente al borde de la franja

**Estado: OK**

El colimador va coaxial con el espejo, en X = +95.55 mm, y con 6.0 mm de radio su cara -X cae en +89.55. La franja empieza en +84.55. Quedan 5.0 mm de margen.

| magnitud | valor |
|---|---|
| x_espejo_mm | 95.55 |
| x_colimador_mm | 95.55 |
| coaxialidad_mm | 0.00 |
| radio_colimador_mm | 6.00 |
| borde_franja_mm | 84.55 |
| x_minimo_del_colimador_mm | 89.55 |
| margen_mm | 5.00 |

## Brazo compartido de los dos beacons, de D1 a la pared del banco

**Estado: OK**

Los dos beacons comparten el brazo que refleja D1, y dentro de el D2 los separa. El reparto por ramas sale de 'meta.topologia_brazo_beacons' de data/connections.yaml, que es el mismo dato que usa el generador para colocar -- +Y: dicroico_d2 + colimador_beacon_bajada; -Y: trampa_luz_d1; -X: camara_beacon; +X: fotodiodo_monitor_beacon. La rama mas apretada es +Y: pide 36.0 mm desde el centro de su divisor y tiene 47.7 mm, sin contar holguras de montaje. Quedan 11.7 mm de margen. Ojo: es el margen DESNUDO. El generador coloca dejando holgura entre pieza y pieza, asi que lo que de verdad sobra en la rama +Y es menos, y todas las envolventes del brazo siguen siendo SUPUESTAS.

| magnitud | valor |
|---|---|
| dicroico_d2_mm | 16.00 |
| colimador_beacon_bajada_mm | 12.00 |
| necesario_+Y_mm | 36.00 |
| disponible_+Y_mm | 47.70 |
| margen_+Y_mm | 11.70 |
| trampa_luz_d1_mm | 15.00 |
| necesario_-Y_mm | 23.00 |
| disponible_-Y_mm | 47.70 |
| margen_-Y_mm | 24.70 |
| camara_beacon_mm | 30.00 |
| necesario_-X_mm | 38.00 |
| disponible_-X_mm | 70.99 |
| margen_-X_mm | 32.99 |
| fotodiodo_monitor_beacon_mm | 12.00 |
| necesario_+X_mm | 20.00 |
| disponible_+X_mm | 50.71 |
| margen_+X_mm | 30.71 |

## Orden de la cadena de fibra frente a las restricciones declaradas

**Estado: OK**

La cadena laser_dfb_1550 -> aislador -> filtro_espectral -> mod_intensidad_mxer_ln_10 -> acoplador_monitor -> voa -> mod_fase_mpz_ln_10 -> colimador cumple las 7 restricciones declaradas. Todo componente de fibra va antes del codificador de polarizacion, y detras de el solo esta el colimador.

| magnitud | valor |
|---|---|
| restricciones | 7.00 |
| piezas_en_la_cadena | 8.00 |
| violaciones | 0.00 |

## Tramo de fibra posterior al codificador de polarizacion

**Estado: NO COMPROBABLE**

El tramo va en fila segun Z y suma 218.0 mm: 130 mm del codificador (protectores de fibra incluidos), 60 mm de protector de empalme y 28 mm de colimador. Cabe en los 227.0 mm de la franja, con 9.0 mm de margen. PERO SI ESA LONGITUD DE FIBRA ES ACEPTABLE NO SE PUEDE DECIR: los estados diagonales no son autoestados de la fibra PM y acumulan una fase que deriva con la temperatura, y cuanta es esa fase depende de 'integracion.fibra.sensibilidad_termica_fase_pm', que es TBD.

| magnitud | valor |
|---|---|
| codificador_mm | 130.00 |
| protector_empalme_mm | 60.00 |
| colimador_mm | 28.00 |
| necesario_mm | 218.00 |
| disponible_mm | 227.00 |
| margen_mm | 9.00 |

Falta: integracion.fibra.sensibilidad_termica_fase_pm (medida)

## Eje de fibra del codificador frente al plano optico del banco

**Estado: OK**

El eje de fibra del codificador cae en Y = +0.00 mm y el plano optico del banco -- el del colimador, D1, el FSM y el telescopio -- esta en Y = +0.00 mm. Desvio: 0.00 mm, contra una tolerancia SUPUESTA de 0.50 mm. El tramo puede ser recto sin cambiar de altura.

| magnitud | valor |
|---|---|
| eje_codificador_Y_mm | 0.00 |
| plano_optico_Y_mm | 0.00 |
| desvio_mm | 0.00 |
| tolerancia_mm | 0.50 |

## Configuracion optica del telescopio

**Estado: OK**

Afocal tipo Mersenne: dos parabolas confocales, M = 12.86. Entra colimado y sale colimado, asi que NO hay foco real dentro del satelite y no hace falta ninguna lente de enfoque en el banco. El foco comun de las dos conicas es VIRTUAL y por eso el modelo no dibuja ningun marcador ahi: no hay nada. Obstruccion lineal 0.109 (secundario de 9.8 mm sobre 90 mm). Cuesta 0.05 dB de potencia recogida y 0.10 dB de intensidad en el eje en campo lejano. Son DOS magnitudes distintas, las dos en potencia, y para un enlace optico manda la segunda: lo que llega al receptor es la intensidad en el eje.

| magnitud | valor |
|---|---|
| magnificacion | 12.86 |
| focal_primario_mm | 200.00 |
| focal_secundario_mm | 15.56 |
| separacion_mm | 184.44 |
| obstruccion_lineal | 0.11 |
| perdida_potencia_recogida_dB | 0.05 |
| perdida_intensidad_en_eje_dB | 0.10 |

## Longitud del telescopio frente a la reservada

**Estado: OK**

Con f1 = 200 mm y M = 12.86 la separacion entre vertices es 184.4 mm, que no se puede tocar sin cambiar la optica. Para los 227 mm reservados eso deja 42.6 mm para los dos mamparos, la celda y los dos espejos. Quedan 21.6 mm de margen. PEOR CASO EN LONGITUD: si el haz bajara a 3.54 mm -- el maximo que admite el espejo del FSM MEMS, o sea el unico haz con el que ese FSM seguiria en juego -- la separacion subiria a 192.1 mm y el margen quedaria en 13.9 mm. Un haz mas fino no ahorra tubo: lo alarga, porque sube la magnificacion.

| magnitud | valor |
|---|---|
| longitud_reservada_mm | 227.00 |
| separacion_vertices_mm | 184.44 |
| estructura_mm | 42.56 |
| longitud_necesaria_mm | 205.44 |
| margen_mm | 21.56 |
| focal_primario_mm | 200.00 |
| magnificacion | 12.86 |
| peor_caso_haz_mm | 3.54 |
| peor_caso_separacion_mm | 192.14 |
| peor_caso_margen_mm | 13.86 |

## El haz comprimido frente al espejo del FSM

**Estado: NO COMPROBABLE**

El espejo del FSM mide 5.0 mm, y un haz a 45 grados deja una huella de d x d*raiz(2), asi que solo admite un haz de 3.54 mm. Con 90 mm de apertura eso exige una magnificacion de al menos 25.5. Con el haz SUPUESTO con el que se dibuja (7 mm, de integracion.optica.diametro_haz_modelado) la huella seria 7 x 9.9 mm y NO CABRIA en el espejo de 5 mm. Si el equipo de optica confirma un haz de ese orden, el MEMS DIP24 queda descartado y hay que ir al 'fsm_piezo_pi_s331' (que pesa 130 g frente a los gramos del MEMS) o subir la magnificacion de 12.9 a 25.5, lo que reduce el secundario y alarga el tubo. Punto de adelanto: 50.7 urad en el cielo son 652 urad opticos en el haz comprimido (326 urad de giro mecanico del espejo) con M = 12.86, porque un afocal comprime los angulos por M. Es poco para cualquiera de las dos tecnologias -- el piezo S-331 da 3 mrad --, asi que el recorrido NO es lo que decide: lo que decide es el tamano del espejo.

| magnitud | valor |
|---|---|
| diametro_espejo_fsm_mm | 5.00 |
| haz_maximo_admisible_mm | 3.54 |
| magnificacion_minima | 25.46 |
| magnificacion_modelada | 12.86 |
| haz_modelado_mm | 7.00 |
| huella_a_45_mm | 9.90 |
| punto_de_adelanto_urad | 50.70 |
| recorrido_optico_en_el_fsm_urad | 651.86 |
| giro_mecanico_en_el_fsm_urad | 325.93 |

Falta: Diametro del haz comprimido (telescopio_cassegrain.optica.diametro_haz_comprimido y diametro_haz_mm de e01..e05). Es el dato que DECIDE el TBD 'fsm.eleccion_de_tecnologia': sin el no se puede elegir entre el MEMS y el piezo.

## El haz frente a la apertura libre de las opticas del banco

**Estado: NO COMPROBABLE**

D1, D2 y el espejo de plegado estan a 45 grados, y un haz de 7.0 mm deja sobre ellos una huella de 7.0 x 9.9 mm. La apertura libre de la familia con la que se dimensionan sus celdas es 11.4 mm, o sea que admite un haz de hasta 8.06 mm. Con el haz SUPUESTO con el que se dibuja cabe, con 1.5 mm de margen sobre la apertura, PERO ESO NO VALIDA NADA: los dos numeros son supuestos y el de arriba es el que se eligio para que esto saliera bien. Lo que este chequeo dice de verdad es cual es el TECHO: si el diseno optico pide mas de 8.06 mm de haz, las celdas de 16 mm de D1, D2 y el espejo dejan de valer y hay que rehacer el brazo.

| magnitud | valor |
|---|---|
| haz_modelado_mm | 7.00 |
| huella_a_45_mm | 9.90 |
| apertura_libre_optica_mm | 11.40 |
| haz_maximo_admisible_mm | 8.06 |
| margen_mm | 1.50 |
| celda_dicroico_d1_mm | 16.00 |
| celda_dicroico_d2_mm | 16.00 |
| celda_espejo_plegado_cuantico_mm | 16.00 |

Falta: Apertura libre real de las monturas elegidas para D1, D2 y el espejo de plegado, y el diametro de haz de verdad (telescopio_cassegrain.optica.diametro_haz_comprimido)

## Placa de la bandeja frente a su zona

**Estado: OK**

La zona de la bandeja mide 121.7 x 79.4 mm en X y Z, asi que con 2 mm de holgura por lado la placa tiene que medir 117.7 x 75.4. Mide 117.7 x 75.4. Coincide: el contorno de la placa sigue derivado de su zona. El espesor (3 mm) sigue siendo SUPUESTO, y eso no lo arregla este chequeo.

| magnitud | valor |
|---|---|
| placa_X_mm | 117.70 |
| placa_Z_mm | 75.40 |
| zona_X_mm | 121.70 |
| zona_Z_mm | 79.40 |
| holgura_por_lado_mm | 2.00 |
| derivado_X_mm | 117.70 |
| derivado_Z_mm | 75.40 |
| margen_X_mm | -0.00 |
| margen_Z_mm | -0.00 |

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

Masa conocida 846 g de un limite de 12000 g (CDS 14.1). Faltan 30 componentes por pesar, incluido el chasis y el telescopio, que son de los mas pesados.

| magnitud | valor |
|---|---|
| masa_conocida_g | 845.90 |
| limite_g | 12000.00 |
| margen_g | 11154.10 |
| componentes_sin_masa | 30.00 |

Falta: Masa de: estructura_6u, adcs_iadcs400, antena_quasar_wsant, radio_uhf_pulsar_vutrx, paneles_photon_side, propulsion, telescopio_cassegrain, fsm, dicroico_d1, dicroico_d2, camara_beacon, laser_beacon_bajada, colimador_beacon_bajada, fotodiodo_monitor_beacon, trampa_luz_d1, espejo_plegado_cuantico, colimador, bandeja_optica, laser_dfb_1550, mod_intensidad_mxer_ln_10, mod_fase_mpz_ln_10, voa, aislador, filtro_espectral, acoplador_monitor, pcb1_control_qkd, pcb2_drivers_opticos, pcb3_pat, cables_rf_moduladores, qrng_idq20mc1_s3

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

