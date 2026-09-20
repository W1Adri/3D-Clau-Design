# Presupuestos de masa y potencia

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (20 piezas colocadas)

## Masa (g)

| estado del dato | total g |
|---|---|
| confirmado | 745.90 |
| referencia | 100.00 |
| **contabilizado** | **845.90** |

Limite de la norma: **12000 g**. Margen sobre lo contabilizado: **11154 g**.

> **Incompleto.** Sin dato (24): `estructura_6u`, `adcs_iadcs400`, `antena_quasar_wsant`, `radio_uhf_pulsar_vutrx`, `paneles_photon_side`, `propulsion`, `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `mod_intensidad_mxer_ln_10`, `mod_fase_mpz_ln_10`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`, `qrng_idq20mc1_s3`. El total real sera mayor; no se rellena ningun hueco.

| id | componente | subsistema | uds | unitario g | total g | estado | fuente |
|---|---|---|---|---|---|---|---|
| bateria_optimus_30 | AAC Clyde Space Optimus-30 | EPS | 2 | 268.00 | 536.00 | confirmado | https://www.aac-clyde.space/wp-content/uploads/2021/11/AAC_DataSheet_Optimus.pdf |
| eps_starbuck_nano_plus | AAC Clyde Space Starbuck-Nano-PLUS | EPS | 1 | 148.00 | 148.00 | confirmado | https://www.aac-clyde.space/wp-content/uploads/2021/11/AAC_DataSheet_Starbuck-Na |
| radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | comunicaciones | 1 | 100.00 | 100.00 | referencia | Ficha AAC Pulsar-STX (via brief ACSAR 2026-09-19) |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | OBC | 1 | 61.90 | 61.90 | confirmado | https://www.aac-clyde.space/wp-content/uploads/2021/10/AAC_DataSheet_Kryten.pdf |

## Potencia nominal (W)

| estado del dato | total W |
|---|---|
| confirmado | 6.83 |
| **contabilizado** | **6.83** |

> **Incompleto.** Sin dato (16): `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `mod_intensidad_mxer_ln_10`, `mod_fase_mpz_ln_10`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`. El total real sera mayor; no se rellena ningun hueco.

| id | componente | subsistema | uds | unitario W | total W | estado | fuente |
|---|---|---|---|---|---|---|---|
| laser_dfb_1550 | Laser DFB 1550 nm, Gooch & Housego (modulo validado para espacio) | bandeja_optica | 1 | 4.10 | 4.10 | confirmado | Brief ACSAR 2026-09-19 (cita ficha Gooch & Housego) |
| adcs_iadcs400 | AAC Clyde Space iADCS400 | ADCS | 1 | 2.00 | 2.00 | confirmado | Brief ACSAR 2026-09-19 (cita ficha AAC Clyde Space) |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | OBC | 1 | 0.40 | 0.40 | confirmado | https://www.aac-clyde.space/wp-content/uploads/2021/10/AAC_DataSheet_Kryten.pdf |
| qrng_idq20mc1_s3 | QRNG ID Quantique IDQ20MC1-S3 | control_qkd | 4 | 0.08 | 0.33 | confirmado | Brief ACSAR 2026-09-19 (cita ficha ID Quantique) |

## Potencia de pico (W)

| estado del dato | total W |
|---|---|
| confirmado | 5.00 |
| referencia | 5.00 |
| **contabilizado** | **10.00** |

> **Incompleto.** Sin dato (18): `telescopio_cassegrain`, `fsm`, `dicroico`, `camara_beacon`, `laser_beacon_bajada`, `colimador`, `bandeja_optica`, `laser_dfb_1550`, `mod_intensidad_mxer_ln_10`, `mod_fase_mpz_ln_10`, `voa`, `aislador`, `filtro_espectral`, `acoplador_monitor`, `pcb1_control_qkd`, `pcb2_drivers_opticos`, `pcb3_pat`, `qrng_idq20mc1_s3`. El total real sera mayor; no se rellena ningun hueco.

| id | componente | subsistema | uds | unitario W | total W | estado | fuente |
|---|---|---|---|---|---|---|---|
| radio_banda_s_quasar_strx | AAC Clyde Space Quasar-STRX (transceptor banda S) | comunicaciones | 1 | 5.00 | 5.00 | referencia | Ficha AAC Pulsar-STX (via brief ACSAR 2026-09-19) |
| adcs_iadcs400 | AAC Clyde Space iADCS400 | ADCS | 1 | 4.00 | 4.00 | confirmado | Web AAC Clyde Space (via brief ACSAR 2026-09-19) |
| obc_kryten_m3_plus | AAC Clyde Space Kryten-M3-PLUS (OBC con GNSS) | OBC | 1 | 1.00 | 1.00 | confirmado | https://www.aac-clyde.space/wp-content/uploads/2021/10/AAC_DataSheet_Kryten.pdf |

## Energia almacenada

- Modulos modelados: **2** (estado de la cantidad real: **TBD**)
- Capacidad por modulo: 30.0 Wh
- Total modelado: 60.0 Wh

> El numero de modulos es una hipotesis de trabajo para reservar volumen, no una decision cerrada.

