# Lista de pendientes

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (28 piezas colocadas)

Total de huecos abiertos: **119**, de los cuales **51** son TBD sin ninguna aproximacion y **68** son SUPUESTOS: numeros que se ha inventado este repositorio para poder dibujar y colocar la pieza.

> **Un supuesto no es un dato.** No suma en los presupuestos de masa ni de potencia, se dibuja en gris y aparece aqui hasta que alguien lo sustituya por una cifra con fuente. La lista de abajo es, literalmente, lo que hay que preguntar.

## AAC Clyde Space (6)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| adcs_iadcs400 | adcs_iadcs400.masa | TBD | - | Masa exacta de la configuracion elegida |
| adcs_iadcs420 | adcs_iadcs420.masa | TBD | - | Masa del iADCS4-20. No hay ficha publica de este producto. |
| antena_quasar_wsant | antena_quasar_wsant.dimensiones | supuesto | `[82.0, 82.0, 10.0]` | Dimensiones reales, ganancia, diagrama de radiacion y cara de montaje |
| antena_quasar_wsant | antena_quasar_wsant.masa | TBD | - | Masa |
| radio_uhf_pulsar_vutrx | radio_uhf_pulsar_vutrx.dimensiones | TBD | - | Dimensiones |
| radio_uhf_pulsar_vutrx | radio_uhf_pulsar_vutrx.masa | TBD | - | Masa |

## AAC Clyde Space / Equipo de potencia de ACSAR (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| paneles_photon_side | paneles_photon_side.dimensiones | supuesto | `[209.3, 3.5, 349.0]` | Contorno real de cada tamano de PHOTON-SIDE (1U/2U/3U/6U) y cual de ellos se monta en cada cara |

## ACSAR (decision de mision aun abierta) (2)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| propulsion | propulsion.dimensiones | TBD | - | Modelo de propulsor y sus dimensiones |
| propulsion | propulsion.masa | TBD | - | Masa del propulsor elegido |

## ACSAR (mecanica y optica) (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.optica.geometria_del_brazo_de_beacons | TBD | - | DECIDIR COMO CABE EL BRAZO. Con los dos beacons compartiendo brazo, la fila D1/2 + D2 + camara pide 54.5 mm desde el centro de D1 y solo hay 47.7 mm hasta la pared del banco: FALTAN 6.8 mm con las envolventes desnudas y 16.8 mm con holguras de montaje, y por eso 'camara_beacon' no esta colocada en data/layout.yaml. Ya esta aplicada la unica salida que no le cuesta volumen a nadie (bajar la reserva de la camara de 30 a 20 mm). Quedan dos, y las dos se pagan: (1) PLEGAR EL BRAZO HACIA -Z con un espejo de doblado. Da unos 27.5 mm mas -- la mitad de los 55 mm de banco en Z -- a costa de una superficie reflectante adicional en el camino del beacon y de una pieza mas que alinear. (2) ALARGAR EL BANCO, que hoy mide 55 mm en Z. Se paga con la bandeja de fibra o con 'telescopio_cassegrain.longitud_reservada', exactamente igual que la salida de la linea en X (CLAUDE.md 3.7). Lo que NO es una salida es seguir bajando reservas hasta que el chequeo pase: las del brazo ya son todas cotas superiores. |

## Aperture Optical Sciences (2)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.masa | TBD | - | Masa |
| telescopio_cassegrain | telescopio_cassegrain.longitud_optica | TBD | - | Longitud del tubo. Interesa distancia focal larga; se admite acortar. |

## Equipo de PAT / de mision de ACSAR (2)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.optica.punto_de_adelanto | supuesto | `50.7` | Punto de adelanto maximo del enlace, del analisis de mision (orbita y geometria de los pases) |
| integracion | integracion.optica.potencia_beacon_bajada | supuesto | `100.0` | Potencia optica de bajada del presupuesto de enlace (divergencia, distancia, sensibilidad del receptor de la estacion) |

## Equipo de PAT de ACSAR (7)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.optica.aislamiento_camara_a_1064 | TBD | - | Aislamiento total medido del beacon de bajada (1064 nm, 100 mW) en el sensor de la camara de seguimiento: la suma de la reflexion de D2, el filtro de banda estrecha de 976 nm y la ceguera del silicio a 1064. |
| camara_beacon | camara_beacon.dimensiones | supuesto | `[20.0, 20.0, 20.0]` | Modelo de sensor, distancia focal del objetivo, campo de vision exigido por el lazo de apuntado y espesor del filtro de banda estrecha de 976 nm |
| camara_beacon | camara_beacon.masa | TBD | - | Masa del sensor elegido |
| laser_beacon_bajada | laser_beacon_bajada.dimensiones | supuesto | `[30.0, 25.0, 25.0]` | Modelo del laser elegido, potencia optica real y su disipador |
| laser_beacon_bajada | laser_beacon_bajada.masa | TBD | - | Masa del laser de beacon elegido |
| fotodiodo_monitor_beacon | fotodiodo_monitor_beacon.dimensiones | supuesto | `[12.0, 12.0, 12.0]` | Modelo de fotodiodo, encapsulado y electronica de acondicionamiento |
| fotodiodo_monitor_beacon | fotodiodo_monitor_beacon.masa | TBD | - | Masa del fotodiodo con su soporte y su acondicionamiento |

## Equipo de electronica de ACSAR (12)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.coaxial.radio_curvatura_modelado | supuesto | `25.0` | Radio minimo de curvatura del coaxial elegido. Es el mismo hueco que 'cables_rf_moduladores.radio_minimo_curvatura'. |
| integracion | integracion.holgura_conector | TBD | - | Holgura de insercion por tipo de conector (coaxial RF, AVIM optico, conectores de datos) |
| pcb1_control_qkd | pcb1_control_qkd.dimensiones | supuesto | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta, que la fija el componente mas alto (la FPGA y su disipador, si lleva). Y confirmar el contorno PC104. |
| pcb1_control_qkd | pcb1_control_qkd.masa | TBD | - | Masa de la tarjeta poblada |
| pcb2_drivers_opticos | pcb2_drivers_opticos.dimensiones | supuesto | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta. Los drivers RF y el del Peltier son los candidatos a componente mas alto. Y confirmar el contorno PC104. |
| pcb2_drivers_opticos | pcb2_drivers_opticos.masa | TBD | - | Masa de la tarjeta poblada |
| pcb3_pat | pcb3_pat.dimensiones | supuesto | `[95.89, 90.17, 15.0]` | Altura real de la tarjeta, y si el driver del FSM es de alta tension (un driver piezo de 120 V ocupa bastante mas que uno de MEMS). Es el mismo dato que bloquea la eleccion del FSM. Y confirmar el contorno. |
| pcb3_pat | pcb3_pat.masa | TBD | - | Masa de la tarjeta poblada |
| cables_rf_moduladores | cables_rf_moduladores.dimensiones | TBD | - | Un cable no tiene envolvente hasta que se encamina. Lo que hace falta es el diametro del coaxial elegido y su radio minimo de curvatura; con esos dos, el recorrido se dibuja como KEEP-OUT entre PCB-2 y cada modulador, no como un cuerpo. |
| cables_rf_moduladores | cables_rf_moduladores.masa | TBD | - | Masa por metro del coaxial elegido, y longitud una vez encaminado |
| cables_rf_moduladores | cables_rf_moduladores.diametro_coaxial | TBD | - | Diametro exterior del coaxial elegido (con su cubierta) |
| cables_rf_moduladores | cables_rf_moduladores.radio_minimo_curvatura | TBD | - | Radio minimo de curvatura del coaxial. Es lo que fija el volumen que hay que reservar, y para un coaxial semirrigido no es pequeno. |

## Equipo de estructura de ACSAR (4)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.pila_pc104.paso_apilamiento | TBD | - | Paso real entre tarjetas (separadores) del chasis elegido |
| estructura_6u | estructura_6u.masa | TBD | - | Masa del chasis 6U elegido |
| telescopio_cassegrain | telescopio_cassegrain.optica.lado_larguero_esquina | supuesto | `12.0` | Seccion real de los largueros, del analisis de rigidez del tubo |
| bandeja_optica | bandeja_optica.dimensiones | supuesto | `[117.7, 3.0, 102.4]` | Material, espesor y patron de taladros de la placa, del analisis estructural y termico |

## Equipo de estructura de ACSAR / Aperture Optical Sciences (3)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_pared_barrilete | supuesto | `1.5` | Espesor y material reales de la pared del barrilete |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_mamparo | supuesto | `3.0` | Espesor real de los mamparos |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_vane | supuesto | `0.8` | Espesor real de los vanes |

## Equipo de optica de ACSAR (24)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.optica.diametro_haz_modelado | supuesto | `10.0` | Diametro de haz de cada tramo (e01 a e05 en data/connections.yaml) y el semiangulo del cono de la apertura |
| integracion | integracion.optica.borde_dicroico_d1 | supuesto | `1300.0` | Longitud de onda de corte, anchura de la transicion y curvas de transmision y reflexion del divisor elegido |
| integracion | integracion.optica.borde_dicroico_d2 | supuesto | `1020.0` | Longitud de onda de corte, anchura de la transicion y curvas de transmision y reflexion del divisor elegido |
| telescopio_cassegrain | telescopio_cassegrain.optica.diametro_haz_comprimido | TBD | - | Diametro del haz colimado a la salida del telescopio, que es el mismo que entra por la brida trasera desde el FSM. ES EL PARAMETRO QUE LO ACOPLA TODO: fija la magnificacion (M = apertura_libre / este diametro), y con ella la focal del secundario, la separacion entre vertices y el diametro del secundario; y decide si el FSM elegido vale, porque un haz de d mm sobre un espejo a 45 grados deja una huella de d x d*raiz(2). Es el mismo hueco que 'diametro_haz_mm' en e01..e05 de data/connections.yaml. |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_secundario | supuesto | `1.4` | Sobredimensionado real del secundario (campo de vista y alineacion) |
| telescopio_cassegrain | telescopio_cassegrain.optica.estabilidad_despace_primario_secundario | TBD | - | Estabilidad exigida a la separacion entre el vertice del primario y el del secundario a lo largo de la orbita, en micras. La sensibilidad a desenfoque de un Cassegrain escala con m^2 (1+m), o sea con el cuadrado de la magnificacion del secundario, asi que unas pocas micras de deriva termica entre los dos espejos se comen el presupuesto de frente de onda entero. ES EL REQUISITO QUE DIMENSIONA el tubo metrico (material, seccion, si hace falta invar o CFRP) y la arana, y hoy no existe: el barrilete y los vanes de este modelo estan dibujados con espesores supuestos, no con una rigidez calculada. |
| telescopio_cassegrain | telescopio_cassegrain.optica.holgura_baffle | supuesto | `0.5` | Holgura real entre el haz y el baffle, del analisis de luz parasita |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_baffle | supuesto | `0.6` | Espesor real de los baffles |
| telescopio_cassegrain | telescopio_cassegrain.optica.diafragmas_internos | supuesto | `4` | Numero y posicion reales de los diafragmas, del analisis de luz parasita |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_diafragma | supuesto | `1.0` | Espesor real de los diafragmas |
| telescopio_cassegrain | telescopio_cassegrain.optica.angulo_exclusion_solar | TBD | - | Angulo de exclusion solar del terminal: a que separacion angular del Sol tiene que seguir funcionando el enlace. Es lo que DIMENSIONA el baffle del primario y el del secundario, y con ellos la obstruccion y el presupuesto de luz parasita. Sin el, los dos baffles de este modelo estan dibujados con un angulo supuesto. |
| telescopio_cassegrain | telescopio_cassegrain.optica.angulo_exclusion_solar_modelado | supuesto | `30.0` | El angulo de verdad, que es 'angulo_exclusion_solar' |
| fsm | fsm.eleccion_de_tecnologia | TBD | - | Elegir entre MEMS (Mirrorcle, herencia CLICK-A, espejo de 5 mm) y piezo (PI S-331). Se modela el MEMS porque es el que tiene cota publicada clara; eso NO es la eleccion. La alternativa piezo esta en el catalogo como 'fsm_piezo_pi_s331'. |
| fsm | fsm.soporte | TBD | - | Soporte de vuelo del MEMS: el encapsulado DIP24 no se atornilla solo a un banco optico. Es lo que decide el volumen real de esta pieza. |
| dicroico_d1 | dicroico_d1.dimensiones | supuesto | `[23.0, 23.0, 23.0]` | Diametro del haz colimado (del que sale el tamano del sustrato), longitudes de onda de corte y envolvente del soporte |
| dicroico_d1 | dicroico_d1.masa | TBD | - | Masa del divisor y su soporte |
| dicroico_d2 | dicroico_d2.dimensiones | supuesto | `[23.0, 23.0, 23.0]` | Diametro de los dos haces de beacon, longitud de onda de corte y envolvente del soporte |
| dicroico_d2 | dicroico_d2.masa | TBD | - | Masa del divisor y su soporte |
| trampa_luz_d1 | trampa_luz_d1.dimensiones | supuesto | `[15.0, 15.0, 15.0]` | Tipo de absorbedor, su envolvente y el rechazo exigido |
| trampa_luz_d1 | trampa_luz_d1.masa | TBD | - | Masa de la trampa elegida |
| trampa_luz_d2 | trampa_luz_d2.dimensiones | supuesto | `[15.0, 15.0, 15.0]` | Tipo de absorbedor, su envolvente y el rechazo exigido |
| trampa_luz_d2 | trampa_luz_d2.masa | TBD | - | Masa de la trampa elegida |
| colimador | colimador.dimensiones | supuesto | `[28.0, 12.0, 12.0]` | Diametro del haz colimado y modelo de colimador. Es el mismo dato que bloquea los keep-outs del camino optico. |
| colimador | colimador.masa | TBD | - | Masa del colimador elegido |

## Equipo de payload de ACSAR (11)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| integracion | integracion.fibra.radio_minimo_curvatura | TBD | - | Radio minimo de curvatura de la fibra elegida (probablemente PM a 1550 nm) |
| integracion | integracion.fibra.radio_curvatura_modelado | supuesto | `30.0` | Radio minimo de curvatura real, que es 'radio_minimo_curvatura' |
| integracion | integracion.fibra.longitud_boot_modelada | supuesto | `20.0` | Tipo de conector o protector y su tramo recto de salida |
| voa | voa.dimensiones | supuesto | `[35.0, 5.5, 5.5]` | Modelo de VOA elegido y su envolvente |
| voa | voa.masa | TBD | - | Masa del VOA elegido |
| aislador | aislador.dimensiones | supuesto | `[35.0, 5.5, 5.5]` | Modelo de aislador elegido y su envolvente |
| aislador | aislador.masa | TBD | - | Masa del aislador elegido |
| filtro_espectral | filtro_espectral.dimensiones | supuesto | `[40.0, 5.5, 5.5]` | Modelo de filtro elegido, su ancho de banda y su envolvente |
| filtro_espectral | filtro_espectral.masa | TBD | - | Masa del filtro elegido |
| acoplador_monitor | acoplador_monitor.dimensiones | supuesto | `[60.0, 20.0, 12.0]` | Modelo de acoplador y de fotodiodo, y si el fotodiodo va en la bandeja o montado en PCB-2 |
| acoplador_monitor | acoplador_monitor.masa | TBD | - | Masa del acoplador y el fotodiodo |

## Equipo de potencia de ACSAR (3)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| bateria_optimus_30 | bateria_optimus_30.cantidad | TBD | - | Numero de modulos de bateria N segun el presupuesto de energia |
| paneles_photon_side | paneles_photon_side.cantidad | TBD | - | Numero de caras pobladas y tamano de cada una |
| paneles_photon_side | paneles_photon_side.masa | TBD | - | Masa total segun el numero de caras pobladas (la ficha da 135 g por cara de 3U) |

## Este repositorio, tras fijar el layout (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| bandeja_optica | bandeja_optica.masa | TBD | - | Masa de la placa, que sale del contorno y el material una vez fijado el layout |

## Exail (6)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.masa | TBD | - | Masa del encapsulado de grado espacial |
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.fibra_entrada.dimensiones | supuesto | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial |
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.fibra_salida.dimensiones | supuesto | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.masa | TBD | - | Masa del encapsulado de grado espacial |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.fibra_entrada.dimensiones | supuesto | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.fibra_salida.dimensiones | supuesto | `[10.0, 3.0, 3.0]` | Diametro del protector de fibra del encapsulado de grado espacial |

## Exail / Equipo de electronica de ACSAR (2)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.rf.dimensiones | supuesto | `[6.1, 10.0, 6.1]` | Profundidad del conector RF, y holgura de insercion del coaxial |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.rf.dimensiones | supuesto | `[6.1, 10.0, 6.1]` | Profundidad del conector RF, y holgura de insercion del coaxial |

## Gooch & Housego (3)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| laser_dfb_1550 | laser_dfb_1550.masa | TBD | - | Masa del modulo butterfly con Peltier |
| laser_dfb_1550 | laser_dfb_1550.pines_btf14.dimensiones | supuesto | `[30.0, 15.3, 4.0]` | Cotas de la fila de pines del modulo elegido |
| laser_dfb_1550 | laser_dfb_1550.pines_btf14_b.dimensiones | supuesto | `[30.0, 15.3, 4.0]` | Cotas de la fila de pines del modulo elegido |

## ID Quantique (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| qrng_idq20mc1_s3 | qrng_idq20mc1_s3.masa | TBD | - | Masa por unidad |

## Mirrorcle Technologies / Equipo de optica de ACSAR (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| fsm | fsm.masa | TBD | - | Masa del MEMS con su soporte de vuelo |

## Oscar (ACSAR) / AAC Clyde Space (3)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| adcs_iadcs420 | adcs_iadcs420.modelo_confirmado | TBD | - | Confirmar QUE ADCS lleva CLAU, iADCS400 o iADCS4-20, y por que el modelo preliminar trae el 4-20 cuando el brief cita el 400. Hasta saberlo hay dos componentes en el catalogo para un solo hueco de la pila. |
| obc_kryten_m3_plus | obc_kryten_m3_plus.part_number_verificado | TBD | - | Confirmar que el STEP 3D-25-02929 RevJ es el Kryten-M3-PLUS. Hasta entonces la geometria dibujada es de referencia, no de ficha. |
| bateria_optimus_30 | bateria_optimus_30.part_number_verificado | TBD | - | Confirmar que el STEP 3D-01-02686 RevA es el Optimus-30, y cuantos Wh da: el STEP trae 8 celdas, y de ahi no se deduce la capacidad. |

## Oscar (ACSAR) / Aperture Optical Sciences (21)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.dimensiones | supuesto | `[95.4, 95.4, 200.0]` | Diametro exterior del barrilete y longitud optica real. YA EXISTE un concepto en formato nativo SolidWorks (Telescopio_concepto.SLDPRT, entrega "Preliminar viability model" del 2026-09-20), ilegible. Hace falta reexportarlo a STEP AP214 o AP242 y dejarlo en la ruta de 'step_esperado'. Ver cad/vendor/MANIFEST.yaml, seccion 'sin_convertir'. |
| telescopio_cassegrain | telescopio_cassegrain.optica.focal_primario | supuesto | `200.0` | Focal real del primario, del diseno optico de Aperture Optical Sciences |
| telescopio_cassegrain | telescopio_cassegrain.optica.conica_primario | supuesto | `-1.0` | Constante conica real del primario del diseno optico |
| telescopio_cassegrain | telescopio_cassegrain.optica.conica_secundario | supuesto | `-1.0` | Constante conica real del secundario del diseno optico |
| telescopio_cassegrain | telescopio_cassegrain.optica.distancia_focal_trasera | supuesto | `40.0` | Distancia focal trasera del diseno focal, si se eligiera esa configuracion |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_agujero_primario | supuesto | `4.0` | Diametro real del agujero central del primario |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_substrato_primario | supuesto | `1.0` | Diametro exterior real del sustrato del primario |
| telescopio_cassegrain | telescopio_cassegrain.optica.seccion_barrilete | supuesto | `[95.4, 95.4]` | Contorno exterior real del barrilete |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_agujero_entrada | supuesto | `2.0` | Diametro real del agujero de entrada |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_espejo_primario | supuesto | `8.0` | Espesor y material reales del sustrato del primario |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_espejo_secundario | supuesto | `4.0` | Espesor y material reales del sustrato del secundario |
| telescopio_cassegrain | telescopio_cassegrain.optica.altura_celda | supuesto | `3.0` | Altura real de la celda isostatica del primario |
| telescopio_cassegrain | telescopio_cassegrain.optica.flexures | supuesto | `3` | Numero y tipo reales de flexures de la celda |
| telescopio_cassegrain | telescopio_cassegrain.optica.radio_circulo_flexures | supuesto | `40.0` | Radio real del circulo de apoyo de la celda |
| telescopio_cassegrain | telescopio_cassegrain.optica.angulo_primer_flexure | supuesto | `45.0` | Orientacion real de la celda respecto al barrilete |
| telescopio_cassegrain | telescopio_cassegrain.optica.seccion_flexure | supuesto | `[6.0, 6.0]` | Seccion real de los flexures |
| telescopio_cassegrain | telescopio_cassegrain.optica.margen_buje_secundario | supuesto | `3.0` | Montura real del secundario |
| telescopio_cassegrain | telescopio_cassegrain.optica.tornillos_colimacion | supuesto | `3` | Mecanismo real de colimacion del secundario |
| telescopio_cassegrain | telescopio_cassegrain.optica.diametro_tornillo_colimacion | supuesto | `3.0` | Tornilleria real de colimacion |
| telescopio_cassegrain | telescopio_cassegrain.optica.vanes | supuesto | `4` | Numero real de vanes de la arana |
| telescopio_cassegrain | telescopio_cassegrain.optica.ancho_vane | supuesto | `6.0` | Geometria real de la arana |

## Oscar (ACSAR) / Equipo de optica de ACSAR (2)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.optica.brida_interfaz_fsm | supuesto | `[40.0, 40.0]` | Interfaz mecanica real telescopio-banco (patron de taladros y plano de referencia) |
| telescopio_cassegrain | telescopio_cassegrain.optica.espesor_brida | supuesto | `3.0` | Espesor real de la brida de interfaz |

## Physik Instrumente (1)

| componente | magnitud | estado | valor modelado | que falta |
|---|---|---|---|---|
| fsm_piezo_pi_s331 | fsm_piezo_pi_s331.dimensiones | supuesto | `[50.0, 50.0, 22.0]` | Cotas exteriores del S-331 (plano acotado o STEP) |

## Solo los supuestos, para sustituirlos (68)

Cada fila es un numero que hoy sostiene el modelo sin sostenerse en nada.

| componente | magnitud | valor modelado | que falta | pedir a |
|---|---|---|---|---|
| integracion | integracion.fibra.radio_curvatura_modelado | `30.0` | Radio minimo de curvatura real, que es 'radio_minimo_curvatura' | Equipo de payload de ACSAR |
| integracion | integracion.fibra.longitud_boot_modelada | `20.0` | Tipo de conector o protector y su tramo recto de salida | Equipo de payload de ACSAR |
| integracion | integracion.coaxial.radio_curvatura_modelado | `25.0` | Radio minimo de curvatura del coaxial elegido. Es el mismo hueco que 'cables_rf_moduladores.radio_minimo_curvatura'. | Equipo de electronica de ACSAR |
| integracion | integracion.optica.diametro_haz_modelado | `10.0` | Diametro de haz de cada tramo (e01 a e05 en data/connections.yaml) y el semiangulo del cono de la apertura | Equipo de optica de ACSAR |
| integracion | integracion.optica.punto_de_adelanto | `50.7` | Punto de adelanto maximo del enlace, del analisis de mision (orbita y geometria de los pases) | Equipo de PAT / de mision de ACSAR |
| integracion | integracion.optica.potencia_beacon_bajada | `100.0` | Potencia optica de bajada del presupuesto de enlace (divergencia, distancia, sensibilidad del receptor de la estacion) | Equipo de PAT / de mision de ACSAR |
| integracion | integracion.optica.borde_dicroico_d1 | `1300.0` | Longitud de onda de corte, anchura de la transicion y curvas de transmision y reflexion del divisor elegido | Equipo de optica de ACSAR |
| integracion | integracion.optica.borde_dicroico_d2 | `1020.0` | Longitud de onda de corte, anchura de la transicion y curvas de transmision y reflexion del divisor elegido | Equipo de optica de ACSAR |
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
| dicroico_d1 | dicroico_d1.dimensiones | `[23.0, 23.0, 23.0]` | Diametro del haz colimado (del que sale el tamano del sustrato), longitudes de onda de corte y envolvente del soporte | Equipo de optica de ACSAR |
| dicroico_d2 | dicroico_d2.dimensiones | `[23.0, 23.0, 23.0]` | Diametro de los dos haces de beacon, longitud de onda de corte y envolvente del soporte | Equipo de optica de ACSAR |
| camara_beacon | camara_beacon.dimensiones | `[20.0, 20.0, 20.0]` | Modelo de sensor, distancia focal del objetivo, campo de vision exigido por el lazo de apuntado y espesor del filtro de banda estrecha de 976 nm | Equipo de PAT de ACSAR |
| laser_beacon_bajada | laser_beacon_bajada.dimensiones | `[30.0, 25.0, 25.0]` | Modelo del laser elegido, potencia optica real y su disipador | Equipo de PAT de ACSAR |
| fotodiodo_monitor_beacon | fotodiodo_monitor_beacon.dimensiones | `[12.0, 12.0, 12.0]` | Modelo de fotodiodo, encapsulado y electronica de acondicionamiento | Equipo de PAT de ACSAR |
| trampa_luz_d1 | trampa_luz_d1.dimensiones | `[15.0, 15.0, 15.0]` | Tipo de absorbedor, su envolvente y el rechazo exigido | Equipo de optica de ACSAR |
| trampa_luz_d2 | trampa_luz_d2.dimensiones | `[15.0, 15.0, 15.0]` | Tipo de absorbedor, su envolvente y el rechazo exigido | Equipo de optica de ACSAR |
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

## Discrepancias entre fuentes (10)

### adcs_iadcs400.potencia_pico

- Valor usado: `4.0` - fuente: Web AAC Clyde Space (via brief ACSAR 2026-09-19)
- Alternativa: `5.0` - fuente: satsearch.co (via brief ACSAR 2026-09-19) - satsearch publica 5 W de pico para el mismo producto.

### obc_kryten_m3_plus.dimensiones

- Valor usado: `[95.89, 90.17, 5.51]` - fuente: https://www.aac-clyde.space/wp-content/uploads/2021/10/AAC_DataSheet_Kryten.pdf
- Alternativa: `[95.89, 90.17, 16.2]` - fuente: Medido sobre cad/vendor/aac_clyde_space/obc_3d_25_02929.step, excluidos los 104 pines del conector PC104 pasante. - Casi 11 mm mas de altura que la ficha. La ficha mide "from top PCB to lowest component" y el STEP incluye el cuerpo de los conectores.
- Alternativa: `[95.89, 90.17, 23.24]` - fuente: Medido sobre el mismo STEP, envolvente completa. - Con los 104 pines del conector PC104, que bajan 12.45 mm por debajo de la tarjeta. En una pila PC104 esos pines atraviesan la tarjeta de abajo por diseno, asi que este solape es real y esperado, no una interferencia.

### bateria_optimus_30.dimensiones

- Valor usado: `[95.89, 90.17, 21.55]` - fuente: https://www.aac-clyde.space/wp-content/uploads/2021/11/AAC_DataSheet_Optimus.pdf
- Alternativa: `[95.89, 90.17, 27.35]` - fuente: Medido sobre cad/vendor/aac_clyde_space/bateria_3d_01_02686.step, excluidos los 104 pines del conector PC104 pasante. - 5.80 mm mas alto que la ficha. Es la diferencia que mas puede doler de las dos tarjetas: ceil(27.35 / 15.24) = 2 posiciones de separador, las mismas que con 21.55, asi que la pila no crece, pero el margen dentro de esas dos posiciones se queda en 3.1 mm.
- Alternativa: `[95.89, 90.17, 36.44]` - fuente: Medido sobre el mismo STEP, envolvente completa. - Con los 104 pines del conector PC104, que bajan 12.45 mm por debajo de la tarjeta y atraviesan la tarjeta vecina por diseno.

### paneles_photon_side.potencia_por_cara_3u

- Valor usado: `9.0` - fuente: https://www.aac-clyde.space/wp-content/uploads/2021/11/AAC_DataSheet_Photon.pdf
- Alternativa: `9.25` - fuente: Brief ACSAR 2026-09-19 - El brief indica 9.25 W por cara de 3U.

### telescopio_cassegrain.optica.configuracion

- Valor usado: `afocal_mersenne` - fuente: DECISION DE ARQUITECTURA de este modelo, no de ACSAR todavia. Afocal tipo Mersenne: primario parabolico concavo y secundario parabolico convexo, confocales, de manera que el telescopio entra colimado y sale colimado y es un puro compresor de haz. El motivo es el banco optico. Un Cassegrain FOCAL clasico (f/12, EFL 1080 mm) pone el foco real a unos 40 mm por detras del vertice del primario, o sea DENTRO de z_payload_banco, y obliga a meter una lente de enfoque en un banco que solo tiene 7.7 mm de margen en la linea que importa (ver 3.7 de CLAUDE.md). El afocal no necesita ningun elemento adicional: cero superficies transmisivas en el camino del canal cuantico, donde cualquier refractivo mete birrefringencia por tension y se come la pureza de polarizacion, que es justamente lo que el enlace mide.
- Alternativa: `focal_clasico` - fuente: Arquitectura de partida del brief (Cassegrain f/12, EFL 1080 mm) - Descartada en este modelo por lo de arriba. Tiene a favor que es la configuracion de catalogo de un Cassegrain comercial; tiene en contra el foco dentro del banco y la lente de enfoque.

### fsm.dimensiones

- Valor usado: `[30.5, 15.1, 2.16]` - fuente: https://mirrorcletech.com/pdf/Mirrorcle_MEMS_Packages_and_Mounts_Guide.pdf
- Alternativa: `[66.04, 25.4, 14.07]` - fuente: https://mirrorcletech.com/pdf/Mirrorcle_MEMS_Packages_and_Mounts_Guide.pdf - MOUNT-DIP.5-KMS: "PCB Dimensions: 66.04mm x 25.40mm x 1.57mm, ZIF Socket Height: ~12.5mm". Es el soporte de laboratorio, no de vuelo, pero da el orden de magnitud de lo que hay que reservar de verdad alrededor del encapsulado.

### fsm_piezo_pi_s331.masa

- Valor usado: `130.0` - fuente: PI, manual S-331 PZ256E (7/29/2026), tabla "Mechanical properties": "Overall mass ... 130 g" para S-331.2SB / .2SH / .2SL.
- Alternativa: `280.0` - fuente: PI, manual S-331 PZ256E, misma tabla, columna S-331.5SH / .5SL - Variante de 5 mrad de recorrido. Mas del doble de masa.

### laser_dfb_1550.dimensiones

- Valor usado: `[37.4, 12.7, 7.8]` - fuente: https://www.phix.com/wp-content/uploads/2025/10/PHIX-BTF14-Design-Guidelines.pdf
- Alternativa: `[37.4, 43.3, 7.8]` - fuente: https://www.phix.com/wp-content/uploads/2025/10/PHIX-BTF14-Design-Guidelines.pdf - "Envelope external dimensions (with pins and ports)". Los pines salen por los dos lados y llevan el ancho de 12.7 a 43.3 mm. Es la cota que manda para el hueco en la bandeja, no para el cuerpo.

### mod_intensidad_mxer_ln_10.dimensiones

- Valor usado: `[110.0, 15.0, 9.7]` - fuente: https://www.exail.com/media-file/7854/exail-datasheet-em-ns-fm-fm-mxer-ln-10-space-grade-components.pdf
- Alternativa: `[85.0, 15.0, 9.65]` - fuente: https://www.exail.com/media-file/7739/datasheet-mpxmpz-ln-series.pdf - "Housing #A" de la serie comercial MPX/MPZ, que es la cifra que recoge el brief. El encapsulado de GRADO ESPACIAL es mas largo. Para el analisis se usa el de grado espacial, que es el que vuela.

### mod_fase_mpz_ln_10.dimensiones

- Valor usado: `[110.0, 15.0, 9.7]` - fuente: https://www.exail.com/media-file/7855/exail-datasheet-em-ns-fm-fm-nir-mpx-ln-01-space-grade-components.pdf
- Alternativa: `[85.0, 15.0, 9.65]` - fuente: https://www.exail.com/media-file/7739/datasheet-mpxmpz-ln-series.pdf - Housing #A comercial. El MPZ-LN-10-LVP usa el Housing #C, de 105 mm.

