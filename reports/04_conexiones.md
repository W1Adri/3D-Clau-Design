# Conexiones

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (20 piezas colocadas)

Resumen: **25** no comprobable, **7** ok

| id | familia | desde | hasta | tipo | estado | recorrido mm | detalle |
|---|---|---|---|---|---|---|---|
| f01 | opticas_fibra | laser_dfb_1550 | mod_intensidad_mxer_ln_10 | fibra_pm | no comprobable | 208 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f02 | opticas_fibra | mod_intensidad_mxer_ln_10 | mod_fase_mpz_ln_10 | fibra_pm | no comprobable | 13 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f03 | opticas_fibra | mod_fase_mpz_ln_10 | voa | fibra_pm | no comprobable | 196 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f04 | opticas_fibra | voa | aislador | fibra_pm | no comprobable | 75 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f05 | opticas_fibra | aislador | filtro_espectral | fibra_pm | no comprobable | 75 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f06 | opticas_fibra | filtro_espectral | acoplador_monitor | fibra_pm | no comprobable | 60 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| f07 | opticas_fibra | acoplador_monitor | colimador | fibra_pm | no comprobable | 69 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| e01 | opticas_espacio_libre | colimador | dicroico | haz_libre | no comprobable | 30 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| e02 | opticas_espacio_libre | dicroico | fsm | haz_libre | no comprobable | 28 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| e03 | opticas_espacio_libre | fsm | telescopio_cassegrain | haz_libre | no comprobable | 127 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| e04 | opticas_espacio_libre | dicroico | camara_beacon | haz_libre | no comprobable | 32 | Extremos colocados, pero sin holgura de conector declarada: no se puede afirmar que quepa. |
| e05 | opticas_espacio_libre | telescopio_cassegrain | EXTERIOR | apertura | ok | - | Extremos colocados y holgura declarada |
| r01 | rf_coaxial | pcb2_drivers_opticos | laser_dfb_1550 | coaxial | no comprobable | - | Sin colocar: pcb2_drivers_opticos. No se puede medir el recorrido ni comprobar la holgura. |
| r02 | rf_coaxial | pcb2_drivers_opticos | mod_intensidad_mxer_ln_10 | coaxial | no comprobable | - | Sin colocar: pcb2_drivers_opticos. No se puede medir el recorrido ni comprobar la holgura. |
| r03 | rf_coaxial | pcb2_drivers_opticos | mod_fase_mpz_ln_10 | coaxial | no comprobable | - | Sin colocar: pcb2_drivers_opticos. No se puede medir el recorrido ni comprobar la holgura. |
| d01 | datos | obc_kryten_m3_plus | pcb1_control_qkd | bus_datos | no comprobable | - | Sin colocar: pcb1_control_qkd. No se puede medir el recorrido ni comprobar la holgura. |
| d02 | datos | obc_kryten_m3_plus | radio_banda_s_quasar_strx | bus_datos | ok | 53 | Extremos colocados y holgura declarada, recorrido 53 mm |
| d03 | datos | obc_kryten_m3_plus | pcb1_control_qkd | pps | no comprobable | - | Sin colocar: pcb1_control_qkd. No se puede medir el recorrido ni comprobar la holgura. |
| d04 | datos | pcb1_control_qkd | pcb2_drivers_opticos | bus_datos | no comprobable | - | Sin colocar: pcb1_control_qkd, pcb2_drivers_opticos. No se puede medir el recorrido ni comprobar la holgura. |
| d05 | datos | pcb1_control_qkd | pcb3_pat | bus_datos | no comprobable | - | Sin colocar: pcb1_control_qkd, pcb3_pat. No se puede medir el recorrido ni comprobar la holgura. |
| d06 | datos | adcs_iadcs400 | pcb3_pat | bus_datos | no comprobable | - | Sin colocar: pcb3_pat. No se puede medir el recorrido ni comprobar la holgura. |
| p01 | potencia | bateria_optimus_30 | eps_starbuck_nano_plus | potencia | ok | 107 | Extremos colocados y holgura declarada, recorrido 107 mm |
| p02 | potencia | paneles_photon_side | eps_starbuck_nano_plus | potencia | no comprobable | - | Sin colocar: paneles_photon_side. No se puede medir el recorrido ni comprobar la holgura. |
| p03 | potencia | eps_starbuck_nano_plus | obc_kryten_m3_plus | potencia | ok | 23 | Extremos colocados y holgura declarada, recorrido 23 mm |
| p04 | potencia | eps_starbuck_nano_plus | adcs_iadcs400 | potencia | ok | 69 | Extremos colocados y holgura declarada, recorrido 69 mm |
| p05 | potencia | eps_starbuck_nano_plus | radio_banda_s_quasar_strx | potencia | ok | 30 | Extremos colocados y holgura declarada, recorrido 30 mm |
| p06 | potencia | eps_starbuck_nano_plus | pcb1_control_qkd | potencia | no comprobable | - | Sin colocar: pcb1_control_qkd. No se puede medir el recorrido ni comprobar la holgura. |
| p07 | potencia | eps_starbuck_nano_plus | pcb2_drivers_opticos | potencia | no comprobable | - | Sin colocar: pcb2_drivers_opticos. No se puede medir el recorrido ni comprobar la holgura. |
| p08 | potencia | eps_starbuck_nano_plus | pcb3_pat | potencia | no comprobable | - | Sin colocar: pcb3_pat. No se puede medir el recorrido ni comprobar la holgura. |
| p09 | potencia | eps_starbuck_nano_plus | laser_dfb_1550 | potencia | ok | 256 | Extremos colocados y holgura declarada, recorrido 256 mm |
| t01 | termico | bandeja_optica | pcb2_drivers_opticos | termico | no comprobable | - | Zona termica declarada pero sin ubicacion de sensores ni calefactores. |
| t02 | termico | baterias | eps_starbuck_nano_plus | termico | no comprobable | - | Zona termica declarada pero sin ubicacion de sensores ni calefactores. |

