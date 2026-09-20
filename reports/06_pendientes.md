# Lista de pendientes (TBD)

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (8 piezas colocadas)

Total de datos pendientes: **53**.

## AAC Clyde Space (7)

| componente | magnitud | que falta |
|---|---|---|
| adcs_iadcs400 | adcs_iadcs400.masa | Masa exacta de la configuracion elegida |
| adcs_iadcs420 | adcs_iadcs420.masa | Masa del iADCS4-20. No hay ficha publica de este producto. |
| antena_quasar_wsant | antena_quasar_wsant.dimensiones | Dimensiones y cara de montaje de la antena |
| antena_quasar_wsant | antena_quasar_wsant.masa | Masa |
| radio_uhf_pulsar_vutrx | radio_uhf_pulsar_vutrx.dimensiones | Dimensiones |
| radio_uhf_pulsar_vutrx | radio_uhf_pulsar_vutrx.masa | Masa |
| paneles_photon_side | paneles_photon_side.dimensiones | Dimensiones de cada panel segun la cara elegida (1U/2U/3U/6U) |

## ACSAR (decision de mision aun abierta) (2)

| componente | magnitud | que falta |
|---|---|---|
| propulsion | propulsion.dimensiones | Modelo de propulsor y sus dimensiones |
| propulsion | propulsion.masa | Masa del propulsor elegido |

## Aperture Optical Sciences (2)

| componente | magnitud | que falta |
|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.masa | Masa |
| telescopio_cassegrain | telescopio_cassegrain.longitud_optica | Longitud del tubo. Interesa distancia focal larga; se admite acortar. |

## Equipo de PAT de ACSAR (4)

| componente | magnitud | que falta |
|---|---|---|
| camara_beacon | camara_beacon.dimensiones | Modelo de sensor y su envolvente |
| camara_beacon | camara_beacon.masa | Masa del sensor elegido |
| laser_beacon_bajada | laser_beacon_bajada.dimensiones | Longitud de onda, potencia y envolvente |
| laser_beacon_bajada | laser_beacon_bajada.masa | Masa del laser de beacon elegido |

## Equipo de electronica de ACSAR (7)

| componente | magnitud | que falta |
|---|---|---|
| integracion | integracion.holgura_conector | Holgura de insercion por tipo de conector (coaxial RF, AVIM optico, conectores de datos) |
| pcb1_control_qkd | pcb1_control_qkd.dimensiones | Altura de la tarjeta (contorno PC104 propuesto, altura por disenar) |
| pcb1_control_qkd | pcb1_control_qkd.masa | Masa de la tarjeta poblada |
| pcb2_drivers_opticos | pcb2_drivers_opticos.dimensiones | Altura de la tarjeta |
| pcb2_drivers_opticos | pcb2_drivers_opticos.masa | Masa de la tarjeta poblada |
| pcb3_pat | pcb3_pat.dimensiones | Altura de la tarjeta, y si el driver del FSM es de alta tension |
| pcb3_pat | pcb3_pat.masa | Masa de la tarjeta poblada |

## Equipo de estructura de ACSAR (2)

| componente | magnitud | que falta |
|---|---|---|
| integracion | integracion.pila_pc104.paso_apilamiento | Paso real entre tarjetas (separadores) del chasis elegido |
| estructura_6u | estructura_6u.masa | Masa del chasis 6U elegido |

## Equipo de optica de ACSAR (6)

| componente | magnitud | que falta |
|---|---|---|
| fsm | fsm.dimensiones | Eleccion entre MEMS (Mirrorcle, herencia CLICK-A, espejo 5 mm) y piezo PI S-331, y su envolvente |
| fsm | fsm.masa | Masa del FSM elegido (MEMS o piezo) |
| dicroico | dicroico.dimensiones | Dimensiones del sustrato y del soporte |
| dicroico | dicroico.masa | Masa del dicroico y su soporte |
| colimador | colimador.dimensiones | Modelo y envolvente (diametro de haz colimado, longitud) |
| colimador | colimador.masa | Masa del colimador elegido |

## Equipo de payload de ACSAR (9)

| componente | magnitud | que falta |
|---|---|---|
| integracion | integracion.fibra.radio_minimo_curvatura | Radio minimo de curvatura de la fibra elegida (probablemente PM a 1550 nm) |
| voa | voa.dimensiones | Modelo y envolvente |
| voa | voa.masa | Masa del VOA elegido |
| aislador | aislador.dimensiones | Modelo y envolvente |
| aislador | aislador.masa | Masa del aislador elegido |
| filtro_espectral | filtro_espectral.dimensiones | Modelo y envolvente |
| filtro_espectral | filtro_espectral.masa | Masa del filtro elegido |
| acoplador_monitor | acoplador_monitor.dimensiones | Modelo y envolvente |
| acoplador_monitor | acoplador_monitor.masa | Masa del acoplador y el fotodiodo |

## Equipo de potencia de ACSAR (3)

| componente | magnitud | que falta |
|---|---|---|
| bateria_optimus_30 | bateria_optimus_30.cantidad | Numero de modulos de bateria N segun el presupuesto de energia |
| paneles_photon_side | paneles_photon_side.cantidad | Numero de caras pobladas y tamano de cada una |
| paneles_photon_side | paneles_photon_side.masa | Masa total segun el numero de caras pobladas (la ficha da 135 g por cara de 3U) |

## Este repositorio, tras fijar el layout (2)

| componente | magnitud | que falta |
|---|---|---|
| bandeja_optica | bandeja_optica.dimensiones | Contorno definitivo, que sale de la distribucion una vez confirmada |
| bandeja_optica | bandeja_optica.masa | Masa de la placa, que sale del contorno y el material una vez fijado el layout |

## Exail (2)

| componente | magnitud | que falta |
|---|---|---|
| mod_intensidad_mxer_ln_10 | mod_intensidad_mxer_ln_10.masa | Masa del encapsulado de grado espacial |
| mod_fase_mpz_ln_10 | mod_fase_mpz_ln_10.masa | Masa del encapsulado de grado espacial |

## Gooch & Housego (2)

| componente | magnitud | que falta |
|---|---|---|
| laser_dfb_1550 | laser_dfb_1550.dimensiones | Envolvente del encapsulado butterfly con Peltier (y del disipador) |
| laser_dfb_1550 | laser_dfb_1550.masa | Masa del modulo butterfly con Peltier |

## ID Quantique (1)

| componente | magnitud | que falta |
|---|---|---|
| qrng_idq20mc1_s3 | qrng_idq20mc1_s3.masa | Masa por unidad |

## Oscar (ACSAR) / AAC Clyde Space (3)

| componente | magnitud | que falta |
|---|---|---|
| adcs_iadcs420 | adcs_iadcs420.modelo_confirmado | Confirmar QUE ADCS lleva CLAU, iADCS400 o iADCS4-20, y por que el modelo preliminar trae el 4-20 cuando el brief cita el 400. Hasta saberlo hay dos componentes en el catalogo para un solo hueco de la pila. |
| obc_kryten_m3_plus | obc_kryten_m3_plus.part_number_verificado | Confirmar que el STEP 3D-25-02929 RevJ es el Kryten-M3-PLUS. Hasta entonces la geometria dibujada es de referencia, no de ficha. |
| bateria_optimus_30 | bateria_optimus_30.part_number_verificado | Confirmar que el STEP 3D-01-02686 RevA es el Optimus-30, y cuantos Wh da: el STEP trae 8 celdas, y de ahi no se deduce la capacidad. |

## Oscar (ACSAR) / Aperture Optical Sciences (1)

| componente | magnitud | que falta |
|---|---|---|
| telescopio_cassegrain | telescopio_cassegrain.dimensiones | Diametro exterior del barrilete y longitud optica del tubo. YA EXISTE un concepto en formato nativo SolidWorks (Telescopio_concepto.SLDPRT, entrega 'Preliminar viability model' del 2026-09-20), ilegible. Hace falta reexportarlo a STEP AP214 o AP242. Ver cad/vendor/MANIFEST.yaml, seccion 'sin_convertir'. |

## Discrepancias entre fuentes (6)

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

### mod_intensidad_mxer_ln_10.dimensiones

- Valor usado: `[110.0, 15.0, 9.7]` - fuente: https://www.exail.com/media-file/7854/exail-datasheet-em-ns-fm-fm-mxer-ln-10-space-grade-components.pdf
- Alternativa: `[85.0, 15.0, 9.65]` - fuente: https://www.exail.com/media-file/7739/datasheet-mpxmpz-ln-series.pdf - "Housing #A" de la serie comercial MPX/MPZ, que es la cifra que recoge el brief. El encapsulado de GRADO ESPACIAL es mas largo. Para el analisis se usa el de grado espacial, que es el que vuela.

### mod_fase_mpz_ln_10.dimensiones

- Valor usado: `[110.0, 15.0, 9.7]` - fuente: https://www.exail.com/media-file/7855/exail-datasheet-em-ns-fm-fm-nir-mpx-ln-01-space-grade-components.pdf
- Alternativa: `[85.0, 15.0, 9.65]` - fuente: https://www.exail.com/media-file/7739/datasheet-mpxmpz-ln-series.pdf - Housing #A comercial. El MPZ-LN-10-LVP usa el Housing #C, de 105 mm.

