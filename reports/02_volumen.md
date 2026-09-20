# Informe de volumen

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **propuesta**

> **La distribucion aun NO esta confirmada.** Las posiciones de este informe son una propuesta pendiente de validar por el equipo. El analisis de interferencias solo es concluyente sobre las piezas realmente colocadas.

## Resumen

| Concepto | cm3 | U |
|---|---|---|
| Envolvente exterior 6U | 8282.6 | 8.28 |
| Zona util interior | 6956.0 | 6.96 |
| Ocupado por piezas colocadas | 0.0 | 0.00 |
| Ocupado segun catalogo (con o sin colocar) | 1394.1 | 1.39 |
| Libre dentro de la zona util | 6956.0 | 6.96 |

> **El volumen libre de arriba NO es el volumen libre real.**

> Sin envolvente conocida (19): `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

> Sin colocar (26): `adcs_iadcs400`, `obc_kryten_m3_plus`, `eps_starbuck_nano_plus`, `bateria_optimus_30`, `radio_banda_s_quasar_strx`, `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `mod_intensidad_mxer_ln_10`, `mod_fase_mpz_ln_10`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

## Por componente

| id | componente | categoria | estado del dato | uds | volumen cm3 | centro (x, y, z) mm | colocado |
|---|---|---|---|---|---|---|---|
| adcs_iadcs400 | AAC Clyde Space iADCS400 | plataforma | confirmado | 1 | 615.7 | - | no |
| bateria_optimus_30 | AAC Clyde Space Optimus-30 | plataforma | confirmado | 2 | 372.7 | - | no |
| eps_starbuck_nano_plus | AAC Clyde Space Starbuck-Nano-PLUS | plataforma | confirmado | 1 | 180.0 | - | no |
| radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | plataforma | referencia | 1 | 146.0 | - | no |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | plataforma | confirmado | 1 | 47.6 | - | no |
| mod_fase_mpz_ln_10 | Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion) | payload_bandeja | referencia | 1 | 16.0 | - | no |
| mod_intensidad_mxer_ln_10 | Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM) | payload_bandeja | confirmado | 1 | 16.0 | - | no |
| qrng_idq20mc1_s3 | QRNG ID Quantique IDQ20MC1-S3 | payload_pcb | confirmado | 4 | 0.1 | - | no |
| acoplador_monitor | Acoplador de monitorizacion + fotodiodo | payload_bandeja | TBD | 1 | - | - | no |
| aislador | Aislador optico | payload_bandeja | TBD | 1 | - | - | no |
| antena_quasar_wsant | AAC Clyde Space Quasar-WSANT (antena banda S) | plataforma | TBD | 1 | - | - | no |
| bandeja_optica | Bandeja optica (placa mecanica, no PCB) | payload_bandeja | TBD | 1 | - | - | no |
| camara_beacon | Camara / sensor de beacon (medida del error de apuntado) | payload_optico | TBD | 1 | - | - | no |
| colimador | Colimador fibra a espacio libre | payload_optico | TBD | 1 | - | - | no |
| dicroico | Espejo dicroico (separacion beacon / canal cuantico) | payload_optico | TBD | 1 | - | - | no |
| filtro_espectral | Filtro espectral | payload_bandeja | TBD | 1 | - | - | no |
| fsm | Espejo de apuntado fino (FSM) | payload_optico | TBD | 1 | - | - | no |
| laser_beacon_bajada | Laser de beacon de bajada | payload_optico | TBD | 1 | - | - | no |
| laser_dfb_1550 | Laser DFB 1550 nm, Gooch & Housego (modulo validado para espacio) | payload_bandeja | TBD | 1 | - | - | no |
| paneles_photon_side | AAC Clyde Space PHOTON-SIDE (paneles de montaje en cuerpo) | plataforma | TBD | - | - | - | no |
| pcb1_control_qkd | PCB-1 Control QKD (FPGA, QRNG, memoria, reloj) | payload_pcb | TBD | 1 | - | - | no |
| pcb2_drivers_opticos | PCB-2 Drivers opticos | payload_pcb | TBD | 1 | - | - | no |
| pcb3_pat | PCB-3 PAT (apuntado, adquisicion y seguimiento) | payload_pcb | TBD | 1 | - | - | no |
| propulsion | Modulo de propulsion (opcional) | plataforma | TBD | 1 | - | - | no |
| radio_uhf_pulsar_vutrx | AAC Clyde Space Pulsar-VUTRX (UHF, TT&C de respaldo) | plataforma | TBD | 1 | - | - | no |
| telescopio_cassegrain | Telescopio Cassegrain on-axis, apertura 90 mm | payload_optico | TBD | 1 | - | - | no |
| voa | Atenuador optico variable (VOA) | payload_bandeja | TBD | 1 | - | - | no |

## Hueco libre por zona

| zona | nombre | total cm3 | ocupado cm3 | libre cm3 | libre U | % ocupado |
|---|---|---|---|---|---|---|
| z_telescopio | Telescopio y apertura de salida | 1786.9 | 0.0 | 1786.9 | 1.79 | 0% |
| z_pila_pc104 | Pila PC104 de plataforma | 1786.9 | 0.0 | 1786.9 | 1.79 | 0% |
| z_mazo_cables | Canal central de cableado | 294.8 | 0.0 | 294.8 | 0.29 | 0% |
| z_banco_libre | Banco optico de espacio libre | 1171.7 | 0.0 | 1171.7 | 1.17 | 0% |
| z_bandeja_optica | Bandeja optica de fibra | 851.7 | 0.0 | 851.7 | 0.85 | 0% |
| z_pcb_payload | Cubierta de electronica del payload | 1064.1 | 0.0 | 1064.1 | 1.06 | 0% |

