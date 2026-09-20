# Informe de volumen

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (14 piezas colocadas)

> **Unidades.** Los volumenes van en **cm3** y en **litros**; las longitudes, en **mm**. La **U** de la CDS es un *formato* (una ranura de dispensador de 100 x 100 x 113.5 mm), no una unidad de volumen, asi que aqui no se usa para medir hueco libre: decir que la envolvente 6U "mide 8.28 U" mezcla las dos cosas. Cuando aparece "6U" se refiere al formato de la envolvente exterior (226.3 x 100 x 366 mm), nunca a un volumen calculado.

## Resumen

| Concepto | cm3 | L |
|---|---|---|
| Envolvente exterior (formato 6U) | 8282.6 | 8.28 |
| Zona util interior | 7643.7 | 7.64 |
| Ocupado por piezas colocadas | 1902.5 | 1.90 |
| Ocupado segun catalogo (con o sin colocar) | 1451.7 | 1.45 |
| Libre dentro de la zona util | 5741.2 | 5.74 |

> **El volumen libre de arriba NO es el volumen libre real.**

> Sin envolvente conocida (13): `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

> Sin colocar (13): `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

## Por componente

| id | componente | categoria | estado del dato | uds | volumen cm3 | centro (x, y, z) mm | colocado |
|---|---|---|---|---|---|---|---|
| adcs_iadcs400 | AAC Clyde Space iADCS400 | plataforma | confirmado | 1 | 615.7 | (-61, 0, 143) | si |
| bateria_optimus_30 | AAC Clyde Space Optimus-30 | plataforma | referencia | 2 | 372.7 | (-61, 0, -33) | si |
| eps_starbuck_nano_plus | AAC Clyde Space Starbuck-Nano-PLUS | plataforma | confirmado | 1 | 180.0 | (-61, 0, 74) | si |
| radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | plataforma | referencia | 1 | 146.0 | (-61, 0, 44) | si |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | plataforma | referencia | 1 | 47.6 | (-61, 0, 97) | si |
| bandeja_optica | Bandeja optica (placa mecanica, no PCB) | payload_bandeja | supuesto | 1 | 36.2 | (50, -46, -127) | si |
| mod_fase_mpz_ln_10 | Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion) | payload_bandeja | referencia | 1 | 16.0 | (104, 5, 46) | si |
| mod_intensidad_mxer_ln_10 | Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM) | payload_bandeja | confirmado | 1 | 16.0 | (91, 5, 46) | si |
| acoplador_monitor | Acoplador de monitorizacion + fotodiodo tap | payload_bandeja | supuesto | 1 | 14.4 | (75, -39, -100) | si |
| laser_dfb_1550 | Laser DFB 1550 nm, Gooch & Housego (modulo validado para espacio) | payload_bandeja | referencia | 1 | 3.7 | (50, -41, -153) | si |
| filtro_espectral | Filtro espectral | payload_bandeja | supuesto | 1 | 1.2 | (15, -42, -100) | si |
| aislador | Aislador optico | payload_bandeja | supuesto | 1 | 1.1 | (87, -42, -121) | si |
| voa | Atenuador optico variable (VOA) | payload_bandeja | supuesto | 1 | 1.1 | (13, -42, -121) | si |
| qrng_idq20mc1_s3 | QRNG ID Quantique IDQ20MC1-S3 | payload_pcb | confirmado | 4 | 0.1 | - | no |
| antena_quasar_wsant | AAC Clyde Space Quasar-WSANT (antena banda S) | plataforma | TBD | 1 | - | - | no |
| camara_beacon | Camara / sensor de beacon (medida del error de apuntado) | payload_optico | TBD | 1 | - | - | no |
| colimador | Colimador fibra a espacio libre | payload_optico | TBD | 1 | - | - | no |
| dicroico | Espejo dicroico (separacion beacon / canal cuantico) | payload_optico | TBD | 1 | - | - | no |
| fsm | Espejo de apuntado fino (FSM) | payload_optico | TBD | 1 | - | - | no |
| laser_beacon_bajada | Laser de beacon de bajada | payload_optico | TBD | 1 | - | - | no |
| paneles_photon_side | AAC Clyde Space PHOTON-SIDE (paneles de montaje en cuerpo) | plataforma | TBD | - | - | - | no |
| pcb1_control_qkd | PCB-1 Control QKD (FPGA, QRNG, memoria, reloj) | payload_pcb | TBD | 1 | - | - | no |
| pcb2_drivers_opticos | PCB-2 Drivers opticos | payload_pcb | TBD | 1 | - | - | no |
| pcb3_pat | PCB-3 PAT (apuntado, adquisicion y seguimiento) | payload_pcb | TBD | 1 | - | - | no |
| propulsion | Modulo de propulsion (opcional) | plataforma | TBD | 1 | - | - | no |
| radio_uhf_pulsar_vutrx | AAC Clyde Space Pulsar-VUTRX (UHF, TT&C de respaldo) | plataforma | TBD | 1 | - | - | no |
| telescopio_cassegrain | Telescopio Cassegrain on-axis, apertura 90 mm | payload_optico | TBD | 1 | - | - | no |

## Hueco libre por zona

| zona | nombre | total cm3 | ocupado cm3 | libre cm3 | libre L | % ocupado |
|---|---|---|---|---|---|---|
| z_plataforma | Columna de plataforma - pila PC104 a lo largo de todo Z | 3447.8 | 1772.9 | 1674.8 | 1.67 | 51% |
| z_payload_telescopio | Telescopio | 1820.2 | 0.0 | 1820.2 | 1.82 | 0% |
| z_payload_franja | Franja lateral - moduladores | 501.8 | 63.1 | 438.8 | 0.44 | 13% |
| z_payload_banco | Banco optico de espacio libre | 638.6 | 0.0 | 638.6 | 0.64 | 0% |
| z_payload_bandeja | Bandeja optica de fibra | 1235.3 | 66.5 | 1168.8 | 1.17 | 5% |

## Mapa del hueco libre

Vista desde +Y (planta). Eje horizontal Z (-Z izquierda, +Z derecha),
eje vertical X (+X arriba). De ` ` (vacio) a `@` (lleno).

```
                :::::::::::::       
       ..       :::::::::::::       
       ..                           
       ..                           
       ..                           
       ..                           
       ..                           
                                    
                                    
                                    
                                    
                                    
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
          @@@@@@@    @@ @@@@@@@@@@@@
```

