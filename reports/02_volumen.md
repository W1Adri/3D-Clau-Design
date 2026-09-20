# Informe de volumen

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (26 piezas colocadas)

> **Unidades.** Los volumenes van en **cm3** y en **litros**; las longitudes, en **mm**. La **U** de la CDS es un *formato* (una ranura de dispensador de 100 x 100 x 113.5 mm), no una unidad de volumen, asi que aqui no se usa para medir hueco libre: decir que la envolvente 6U "mide 8.28 U" mezcla las dos cosas. Cuando aparece "6U" se refiere al formato de la envolvente exterior (226.3 x 100 x 366 mm), nunca a un volumen calculado.

## Resumen

| Concepto | cm3 | L |
|---|---|---|
| Envolvente exterior (formato 6U) | 8282.6 | 8.28 |
| Zona util interior | 7643.7 | 7.64 |
| Ocupado por piezas colocadas | 4760.4 | 4.76 |
| Ocupado segun catalogo (con o sin colocar) | 4302.5 | 4.30 |
| Libre dentro de la zona util | 2883.3 | 2.88 |

> **El volumen libre de arriba NO es el volumen libre real.**

> Sin envolvente conocida (3): `radio_uhf_pulsar_vutrx`, `propulsion`, `cables_rf_moduladores`.

> Sin colocar (3): `radio_uhf_pulsar_vutrx`, `propulsion`, `cables_rf_moduladores`.

## Por componente

`fuente` dice de donde sale el solido que se dibuja; `estado` de donde salen sus cotas. No siempre coinciden: una pieza con ficha confirmada y STEP de referencia se dibuja como referencia, porque lo que se esta viendo es el STEP. `envolvente` es la caja que ocupa YA GIRADA Y COLOCADA, conectores incluidos, que es lo que ve el detector de interferencias.

| id drive | id | componente | fuente | estado | uds | volumen cm3 | envolvente mm | keep-outs | centro mm | colocado |
|---|---|---|---|---|---|---|---|---|---|---|
| OPT-13 | telescopio_cassegrain | Telescopio Cassegrain on-axis, apertura 90 mm | aproximado propio: cassegrain (esperando STEP) | supuesto | 1 | 1820.2 | 95 x 95 x 200 | 0 | (37, 0, 81) | si |
| PLAT-04 | adcs_iadcs400 | AAC Clyde Space iADCS400 | aproximado propio: caja | confirmado | 1 | 615.7 | 96 x 95 x 67 | 0 | (-61, 0, 143) | si |
| PLAT-07 | paneles_photon_side | AAC Clyde Space PHOTON-SIDE (paneles de montaje en cuerpo) | aproximado propio: caja | supuesto | 2 | 511.3 | 209 x 4 x 349 | 0 | (0, 52, 0) | si |
| PLAT-06 | bateria_optimus_30 | AAC Clyde Space Optimus-30 (bateria) | STEP de fabricante | referencia | 2 | 372.7 | 96 x 90 x 36 | 0 | (-61, 0, -56) | si |
| PLAT-05 | eps_starbuck_nano_plus | AAC Clyde Space Starbuck-Nano-PLUS (EPS) | aproximado propio: caja | confirmado | 1 | 180.0 | 96 x 90 x 21 | 0 | (-61, 0, 59) | si |
| PLAT-02 | radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | aproximado propio: caja | referencia | 1 | 146.0 | 96 x 90 x 17 | 0 | (-61, 0, 28) | si |
| ELEC-01 | pcb1_control_qkd | PCB-1 Control QKD (FPGA, QRNG, memoria, reloj) | aproximado propio: caja | supuesto | 1 | 129.7 | 96 x 90 x 15 | 0 | (-61, 0, -10) | si |
| ELEC-02 | pcb2_drivers_opticos | PCB-2 Drivers opticos | aproximado propio: caja | supuesto | 1 | 129.7 | 96 x 90 x 15 | 0 | (-61, 0, -25) | si |
| ELEC-03 | pcb3_pat | PCB-3 PAT (apuntado, adquisicion y seguimiento) | aproximado propio: caja | supuesto | 1 | 129.7 | 96 x 90 x 15 | 0 | (-61, 0, 5) | si |
| PLAT-03 | antena_quasar_wsant | AAC Clyde Space Quasar-WSANT (antena banda S) | aproximado propio: caja | supuesto | 1 | 67.2 | 82 x 82 x 10 | 0 | (-61, 0, -176) | si |
| PLAT-01 | obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | STEP de fabricante | referencia | 1 | 47.6 | 96 x 90 x 23 | 0 | (-61, 0, 89) | si |
| OPT-14 | bandeja_optica | Bandeja optica (placa mecanica, no PCB) | aproximado propio: caja | supuesto | 1 | 36.2 | 118 x 3 x 102 | 0 | (50, -46, -127) | si |
| OPT-11 | camara_beacon | Camara / sensor de beacon (medida del error de apuntado) | aproximado propio: caja | supuesto | 1 | 27.0 | 30 x 30 x 30 | 0 | (65, 32, -47) | si |
| OPT-12 | laser_beacon_bajada | Laser de beacon de bajada | aproximado propio: caja | supuesto | 1 | 18.8 | 25 x 30 x 25 | 0 | (65, -32, -47) | si |
| OPT-03 | mod_fase_mpz_ln_10 | Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion) | aproximado propio: caja | referencia | 1 | 16.0 | 10 x 25 x 130 | 2 | (104, 5, 46) | si |
| OPT-02 | mod_intensidad_mxer_ln_10 | Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM) | aproximado propio: caja | confirmado | 1 | 16.0 | 10 x 25 x 130 | 2 | (91, 5, 46) | si |
| OPT-07 | acoplador_monitor | Acoplador de monitorizacion + fotodiodo tap | aproximado propio: caja | supuesto | 1 | 14.4 | 60 x 12 x 20 | 2 | (75, -39, -100) | si |
| OPT-09 | dicroico | Espejo dicroico (separacion beacon / canal cuantico) | aproximado propio: caja | supuesto | 1 | 12.2 | 23 x 23 x 23 | 0 | (65, 0, -47) | si |
| OPT-08 | colimador | Colimador fibra a espacio libre | aproximado propio: cilindro | supuesto | 1 | 4.0 | 28 x 12 x 12 | 1 | (95, 0, -47) | si |
| OPT-01 | laser_dfb_1550 | Laser DFB 1550 nm, Gooch & Housego (modulo validado para espacio) | aproximado propio: caja | referencia | 1 | 3.7 | 37 x 8 x 43 | 1 | (50, -41, -153) | si |
| OPT-06 | filtro_espectral | Filtro espectral | aproximado propio: cilindro | supuesto | 1 | 1.2 | 40 x 6 x 6 | 2 | (15, -42, -100) | si |
| OPT-05 | aislador | Aislador optico | aproximado propio: cilindro | supuesto | 1 | 1.1 | 35 x 6 x 6 | 2 | (87, -42, -121) | si |
| OPT-04 | voa | Atenuador optico variable (VOA) | aproximado propio: cilindro | supuesto | 1 | 1.1 | 35 x 6 x 6 | 2 | (13, -42, -121) | si |
| OPT-10 | fsm | Espejo de apuntado fino (FSM) - opcion MEMS | aproximado propio: caja | referencia | 1 | 1.0 | 23 x 15 x 23 | 0 | (37, 0, -47) | si |
| ELEC-01.1 | qrng_idq20mc1_s3 | QRNG ID Quantique IDQ20MC1-S3 | aproximado propio: caja | confirmado | 4 | 0.1 | - | 0 | - | no |
| ELEC-04 | cables_rf_moduladores | Coaxiales RF de PCB-2 a los dos moduladores | sin geometria | TBD | 2 | - | - | 0 | - | no |
| - | propulsion | Modulo de propulsion (opcional) | sin geometria | TBD | 1 | - | - | 0 | - | no |
| - | radio_uhf_pulsar_vutrx | AAC Clyde Space Pulsar-VUTRX (UHF, TT&C de respaldo) | sin geometria | TBD | 1 | - | - | 0 | - | no |

## Hueco libre por columna

| columna | total cm3 | ocupado cm3 | libre cm3 | libre L | % ocupado |
|---|---|---|---|---|---|
| Plataforma (pila PC104) | 3447.8 | 2229.2 | 1218.5 | 1.22 | 65% |
| Payload (telescopio, franja, banco y bandeja) | 4195.9 | 2019.8 | 2176.1 | 2.18 | 48% |

> El **ocupado** son cajas envolventes, no volumen de material: un cilindro cuenta por su cilindro, pero una caja con un conector cuenta el hueco entero. Y el **libre** es un techo mientras quede un solo componente sin colocar o sin envolvente.

## Hueco libre por zona

| zona | nombre | total cm3 | ocupado cm3 | libre cm3 | libre L | % ocupado |
|---|---|---|---|---|---|---|
| z_plataforma | Columna de plataforma - pila PC104 a lo largo de todo Z | 3447.8 | 2229.2 | 1218.5 | 1.22 | 65% |
| z_payload_telescopio | Telescopio | 1820.2 | 1820.2 | 0.0 | 0.00 | 100% |
| z_payload_franja | Franja lateral - moduladores | 501.8 | 63.1 | 438.8 | 0.44 | 13% |
| z_payload_banco | Banco optico de espacio libre | 638.6 | 70.0 | 568.6 | 0.57 | 11% |
| z_payload_bandeja | Bandeja optica de fibra | 1235.3 | 66.5 | 1168.8 | 1.17 | 5% |

## Supuestos pendientes de sustituir (61)

Cada fila es un numero que este repositorio se ha inventado para poder dibujar algo. Ninguno suma en los presupuestos de masa ni de potencia, y todos se dibujan en gris. Sustituir cualquiera de ellos por una cifra con fuente es, literalmente, todo lo que hay que hacer para que esta parte del modelo deje de ser una reserva y pase a ser un dato.

| componente | magnitud | valor modelado | que falta | pedir a |
|---|---|---|---|---|
| integracion | integracion.fibra.radio_curvatura_modelado | `30.0` | Radio minimo de curvatura real, que es 'radio_minimo_curvatura' | Equipo de payload de ACSAR |
| integracion | integracion.fibra.longitud_boot_modelada | `20.0` | Tipo de conector o protector y su tramo recto de salida | Equipo de payload de ACSAR |
| integracion | integracion.coaxial.radio_curvatura_modelado | `25.0` | Radio minimo de curvatura del coaxial elegido. Es el mismo hueco que 'cables_rf_moduladores.radio_minimo_curvatura'. | Equipo de electronica de ACSAR |
| integracion | integracion.optica.diametro_haz_modelado | `10.0` | Diametro de haz de cada tramo (e01 a e05 en data/connections.yaml) y el semiangulo del cono de la apertura | Equipo de optica de ACSAR |
| integracion | integracion.optica.punto_de_adelanto | `50.7` | Punto de adelanto maximo del enlace, del analisis de mision (orbita y geometria de los pases) | Equipo de PAT / de mision de ACSAR |
| antena_quasar_wsant | antena_quasar_wsant.dimensiones | `[82.0, 82.0, 10.0]` | Dimensiones reales, ganancia, diagrama de radiacion y cara de montaje | AAC Clyde Space |
| paneles_photon_side | paneles_photon_side.dimensiones | `[209.3, 3.5, 349.0]` | Contorno real de cada tamano de PHOTON-SIDE (1U/2U/3U/6U) y cual de ellos se monta en cada cara | AAC Clyde Space / Equipo de potencia de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.dimensiones | `[95.4, 95.4, 200.0]` | Diametro exterior del barrilete y longitud optica real. YA EXISTE un concepto en formato nativo SolidWorks (Telescopio_concepto.SLDPRT, entrega "Preliminar viability model" del 2026-09-20), ilegible. Hace falta reexportarlo a STEP AP214 o AP242 y dejarlo en la ruta de 'step_esperado'. Ver cad/vendor/MANIFEST.yaml, seccion 'sin_convertir'. | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.focal_primario | `200.0` | Focal real del primario, del diseno optico de Aperture Optical Sciences | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.conica_primario | `-1.0` | Constante conica real del primario del diseno optico | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.conica_secundario | `-1.0` | Constante conica real del secundario del diseno optico | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.distancia_focal_trasera | `40.0` | Distancia focal trasera del diseno focal, si se eligiera esa configuracion | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_secundario | `1.4` | Sobredimensionado real del secundario (campo de vista y alineacion) | Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_agujero_primario | `4.0` | Diametro real del agujero central del primario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_substrato_primario | `1.0` | Diametro exterior real del sustrato del primario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.seccion_barrilete | `[95.4, 95.4]` | Contorno exterior real del barrilete | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_pared_barrilete | `1.5` | Espesor y material reales de la pared del barrilete | Equipo de estructura de ACSAR / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_mamparo | `3.0` | Espesor real de los mamparos | Equipo de estructura de ACSAR / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.lado_larguero_esquina | `12.0` | Seccion real de los largueros, del analisis de rigidez del tubo | Equipo de estructura de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.brida_interfaz_fsm | `[40.0, 40.0]` | Interfaz mecanica real telescopio-banco (patron de taladros y plano de referencia) | Oscar (ACSAR) / Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_brida | `3.0` | Espesor real de la brida de interfaz | Oscar (ACSAR) / Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_agujero_entrada | `2.0` | Diametro real del agujero de entrada | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_espejo_primario | `8.0` | Espesor y material reales del sustrato del primario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_espejo_secundario | `4.0` | Espesor y material reales del sustrato del secundario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.altura_celda | `3.0` | Altura real de la celda isostatica del primario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.flexures | `3` | Numero y tipo reales de flexures de la celda | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.radio_circulo_flexures | `40.0` | Radio real del circulo de apoyo de la celda | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.angulo_primer_flexure | `45.0` | Orientacion real de la celda respecto al barrilete | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.seccion_flexure | `[6.0, 6.0]` | Seccion real de los flexures | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_buje_secundario | `3.0` | Montura real del secundario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.tornillos_colimacion | `3` | Mecanismo real de colimacion del secundario | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.diametro_tornillo_colimacion | `3.0` | Tornilleria real de colimacion | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.vanes | `4` | Numero real de vanes de la arana | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_vane | `0.8` | Espesor real de los vanes | Equipo de estructura de ACSAR / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.ancho_vane | `6.0` | Geometria real de la arana | Oscar (ACSAR) / Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.holgura_baffle | `0.5` | Holgura real entre el haz y el baffle, del analisis de luz parasita | Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_baffle | `0.6` | Espesor real de los baffles | Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.diafragmas_internos | `4` | Numero y posicion reales de los diafragmas, del analisis de luz parasita | Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_diafragma | `1.0` | Espesor real de los diafragmas | Equipo de optica de ACSAR |
| telescopio_cassegrain | telescopio_cassegrain.optica.angulo_exclusion_solar_modelado | `30.0` | El angulo de verdad, que es 'angulo_exclusion_solar' | Equipo de optica de ACSAR |
| fsm_piezo_pi_s331 | fsm_piezo_pi_s331.dimensiones | `[50.0, 50.0, 22.0]` | Cotas exteriores del S-331 (plano acotado o STEP) | Physik Instrumente |
| dicroico | dicroico.dimensiones | `[23.0, 23.0, 23.0]` | Diametro del haz colimado (del que sale el tamano del sustrato), longitudes de onda de corte y envolvente del soporte | Equipo de optica de ACSAR |
| camara_beacon | camara_beacon.dimensiones | `[30.0, 30.0, 30.0]` | Modelo de sensor, distancia focal del objetivo y campo de vision exigido por el lazo de apuntado | Equipo de PAT de ACSAR |
| laser_beacon_bajada | laser_beacon_bajada.dimensiones | `[25.0, 30.0, 25.0]` | Longitud de onda, potencia optica y envolvente del modulo elegido | Equipo de PAT de ACSAR |
| colimador | colimador.dimensiones | `[28.0, 12.0, 12.0]` | Diametro del haz colimado y modelo de colimador. Es el mismo dato que bloquea los keep-outs del camino optico. | Equipo de optica de ACSAR |
| bandeja_optica | bandeja_optica.dimensiones | `[117.7, 3.0, 102.4]` | Material, espesor y patron de taladros de la placa, del analisis estructural y termico | Equipo de estructura de ACSAR |
| laser_dfb_1550 | laser_dfb_1550.pines_btf14.dimensiones | `[30.0, 15.3, 4.0]` | Cotas de la fila de pines del modulo elegido | Gooch & Housego |
| laser_dfb_1550 | laser_dfb_1550.pines_btf14_b.dimensiones | `[30.0, 15.3, 4.0]` | Cotas de la fila de pines del modulo elegido | Gooch & Housego |
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.rf.dimensiones | `[6.1, 10.0, 6.1]` | Profundidad del conector RF, y holgura de insercion del coaxial | Exail / Equipo de electronica de ACSAR |
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.fibra_entrada.dimensiones | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial | Exail |
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.fibra_salida.dimensiones | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial | Exail |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.rf.dimensiones | `[6.1, 10.0, 6.1]` | Profundidad del conector RF, y holgura de insercion del coaxial | Exail / Equipo de electronica de ACSAR |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.fibra_entrada.dimensiones | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial | Exail |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.fibra_salida.dimensiones | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial | Exail |
| voa | voa.dimensiones | `[35.0, 5.5, 5.5]` | Modelo de VOA elegido y su envolvente | Equipo de payload de ACSAR |
| aislador | aislador.dimensiones | `[35.0, 5.5, 5.5]` | Modelo de aislador elegido y su envolvente | Equipo de payload de ACSAR |
| filtro_espectral | filtro_espectral.dimensiones | `[40.0, 5.5, 5.5]` | Modelo de filtro elegido, su ancho de banda y su envolvente | Equipo de payload de ACSAR |
| acoplador_monitor | acoplador_monitor.dimensiones | `[60.0, 20.0, 12.0]` | Modelo de acoplador y de fotodiodo, y si el fotodiodo va en la bandeja o montado en PCB-2 | Equipo de payload de ACSAR |
| pcb1_control_qkd | pcb1_control_qkd.dimensiones | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta, que la fija el componente mas alto (la FPGA y su disipador, si lleva). Y confirmar el contorno PC104. | Equipo de electronica de ACSAR |
| pcb2_drivers_opticos | pcb2_drivers_opticos.dimensiones | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta. Los drivers RF y el del Peltier son los candidatos a componente mas alto. Y confirmar el contorno PC104. | Equipo de electronica de ACSAR |
| pcb3_pat | pcb3_pat.dimensiones | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta, y si el driver del FSM es de alta tension (un driver piezo de 120 V ocupa bastante mas que uno de MEMS). Es el mismo dato que bloquea la eleccion del FSM. Y confirmar el contorno. | Equipo de electronica de ACSAR |

## Mapa del hueco libre

Vista desde +Y (planta). Eje horizontal Z (-Z izquierda, +Z derecha),
eje vertical X (+X arriba). De ` ` (vacio) a `@` (lleno).

```
             .  :::::::::::::       
       ..    .  :::::::::::::       
       ..    .                      
       ..   ##+ @@@@@@@@@@@@@@@@@@@@
       ..   ##+ @@@@@@@@@@@@@@@@@@@@
       ..   ##+ @@@@@@@@@@@@@@@@@@@@
       ..   ..  @@@@@@@@@@@@@@@@@@@@
            ..  @@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@
                @@@@@@@@@@@@@@@@@@@@
      @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
#     @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
      @@@@ @@@ @@@@ @@ @@ @@ @@@@@@@
```

