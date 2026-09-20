# Informe de volumen

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (8 piezas colocadas)

> **Unidades.** Los volumenes van en **cm3** y en **litros**; las longitudes, en **mm**. La **U** de la CDS es un *formato* (una ranura de dispensador de 100 x 100 x 113.5 mm), no una unidad de volumen, asi que aqui no se usa para medir hueco libre: decir que la envolvente 6U "mide 8.28 U" mezcla las dos cosas. Cuando aparece "6U" se refiere al formato de la envolvente exterior (226.3 x 100 x 366 mm), nunca a un volumen calculado.

## Resumen

| Concepto | cm3 | L |
|---|---|---|
| Envolvente exterior (formato 6U) | 8282.6 | 8.28 |
| Zona util interior | 7643.7 | 7.64 |
| Ocupado por piezas colocadas | 1394.1 | 1.39 |
| Ocupado segun catalogo (con o sin colocar) | 1394.1 | 1.39 |
| Libre dentro de la zona util | 6249.6 | 6.25 |

> **El volumen libre de arriba NO es el volumen libre real.**

> Sin envolvente conocida (19): `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

> Sin colocar (19): `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`.

## Por componente

| id | componente | categoria | estado del dato | uds | volumen cm3 | centro (x, y, z) mm | colocado |
|---|---|---|---|---|---|---|---|
| adcs_iadcs400 | AAC Clyde Space iADCS400 | plataforma | confirmado | 1 | 615.7 | (-61, 0, 143) | si |
| bateria_optimus_30 | AAC Clyde Space Optimus-30 | plataforma | confirmado | 2 | 372.7 | (-61, 0, -33) | si |
| eps_starbuck_nano_plus | AAC Clyde Space Starbuck-Nano-PLUS | plataforma | confirmado | 1 | 180.0 | (-61, 0, 74) | si |
| radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | plataforma | referencia | 1 | 146.0 | (-61, 0, 44) | si |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | plataforma | confirmado | 1 | 47.6 | (-61, 0, 97) | si |
| mod_fase_mpz_ln_10 | Exail MPZ-LN-10 (modulador de fase, codificador de polarizacion) | payload_bandeja | referencia | 1 | 16.0 | (45, -38, -108) | si |
| mod_intensidad_mxer_ln_10 | Exail MXER-LN-10 (modulador de intensidad, grado espacial EM/NS-FM/FM) | payload_bandeja | confirmado | 1 | 16.0 | (20, -38, -108) | si |
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

| zona | nombre | total cm3 | ocupado cm3 | libre cm3 | libre L | % ocupado |
|---|---|---|---|---|---|---|
| z_plataforma | Columna de plataforma - pila PC104 a lo largo de todo Z | 3447.8 | 1362.1 | 2085.7 | 2.09 | 40% |
| z_payload_telescopio | Telescopio | 1857.6 | 0.0 | 1857.6 | 1.86 | 0% |
| z_payload_banco | Banco optico de espacio libre | 638.6 | 0.0 | 638.6 | 0.64 | 0% |
| z_payload_bandeja | Bandeja optica de fibra | 1699.7 | 32.0 | 1667.7 | 1.67 | 2% |

## Mapa del hueco libre

Vista desde +Y (planta). Eje horizontal Z (-Z izquierda, +Z derecha),
eje vertical X (+X arriba). De ` ` (vacio) a `@` (lleno).

```
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
           @@ @@     @@ @@ @ @@@@@@@
```

