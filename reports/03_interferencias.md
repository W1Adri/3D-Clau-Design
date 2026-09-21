# Interferencias

Generado automaticamente el 2026-09-20 por `clau3d informe`.
No editar a mano: los numeros salen de `data/components.yaml`.

- Mision: CLAU - CubeSat Laser per a Aplicacions Ultrasegures
- Norma: CubeSat Design Specification Rev. 14.1, The CubeSat Program, Cal Poly SLO
- Estado del layout: **confirmada** (28 piezas colocadas)

Piezas colocadas: **28**. Choques de geometria: **0**. Invasiones de keep-outs dibujados con numeros SUPUESTOS: **15**.

## Choques de geometria

Dos solidos que ocupan el mismo sitio, o una pieza que se sale de donde tiene que estar. Esto si es un error del modelo o del reparto, y hace que `clau3d informe` devuelva codigo 1.

_(sin filas)_

## Invasiones de keep-outs SUPUESTOS (15)

> **Esto no es una lista de errores.** Son piezas que se meten en un volumen reservado que esta dibujado a partir de un numero que se ha inventado este repositorio: el radio minimo de curvatura de la fibra, el del coaxial y el diametro de haz siguen siendo **TBD**. Lo que dicen estas filas es *con la hipotesis de hoy, aqui no cabe*, y la manera de resolverlas NO es bajar el radio supuesto hasta que desaparezcan: es conseguir el dato. Por eso no tumban el codigo de salida.

Lo que estas filas estan diciendo, en una frase: **la bandeja de fibra, tal y como esta repartida, no respeta un radio de curvatura de 30 mm**, y el colimador no tiene por donde sacar su latiguillo. Las dos cosas se deciden con el mismo dato.

| tipo | pieza | keep-out | volumen cm3 | detalle |
|---|---|---|---|---|
| keep_out | aislador | keepout_fibra_laser_dfb_1550_salida | 0.02 | aislador invade el keep-out 'fibra_laser_dfb_1550_salida' (fibra) en 0.02 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | laser_dfb_1550 | keepout_fibra_voa_salida | 3.64 | laser_dfb_1550 invade el keep-out 'fibra_voa_salida' (fibra) en 3.64 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | aislador | keepout_fibra_voa_salida | 0.16 | aislador invade el keep-out 'fibra_voa_salida' (fibra) en 0.16 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | filtro_espectral | keepout_fibra_voa_salida | 0.08 | filtro_espectral invade el keep-out 'fibra_voa_salida' (fibra) en 0.08 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | acoplador_monitor | keepout_fibra_voa_salida | 6.29 | acoplador_monitor invade el keep-out 'fibra_voa_salida' (fibra) en 6.29 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | laser_dfb_1550 | keepout_fibra_aislador_entrada | 3.64 | laser_dfb_1550 invade el keep-out 'fibra_aislador_entrada' (fibra) en 3.64 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | voa | keepout_fibra_aislador_entrada | 0.16 | voa invade el keep-out 'fibra_aislador_entrada' (fibra) en 0.16 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | filtro_espectral | keepout_fibra_aislador_entrada | 0.23 | filtro_espectral invade el keep-out 'fibra_aislador_entrada' (fibra) en 0.23 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | acoplador_monitor | keepout_fibra_aislador_entrada | 4.45 | acoplador_monitor invade el keep-out 'fibra_aislador_entrada' (fibra) en 4.45 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | aislador | keepout_fibra_filtro_espectral_salida | 0.23 | aislador invade el keep-out 'fibra_filtro_espectral_salida' (fibra) en 0.23 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | acoplador_monitor | keepout_fibra_filtro_espectral_salida | 7.46 | acoplador_monitor invade el keep-out 'fibra_filtro_espectral_salida' (fibra) en 7.46 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | fsm | keepout_fibra_colimador_entrada | 2.96 | fsm invade el keep-out 'fibra_colimador_entrada' (fibra) en 2.96 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | dicroico_d1 | keepout_fibra_colimador_entrada | 6.08 | dicroico_d1 invade el keep-out 'fibra_colimador_entrada' (fibra) en 6.08 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | dicroico_d2 | keepout_fibra_colimador_entrada | 12.17 | dicroico_d2 invade el keep-out 'fibra_colimador_entrada' (fibra) en 12.17 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |
| keep_out | laser_beacon_bajada | keepout_fibra_colimador_entrada | 10.62 | laser_beacon_bajada invade el keep-out 'fibra_colimador_entrada' (fibra) en 10.62 cm3, con el keep-out dibujado a partir de un valor SUPUESTO |

## Los keep-outs que hay (23)

| id | tipo | estado | dims mm | en que se basa |
|---|---|---|---|---|
| fibra_laser_dfb_1550_salida | fibra | supuesto | 42 x 60 x 58 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_mod_intensidad_mxer_ln_10_entrada | fibra | supuesto | 20 x 60 x 50 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_mod_fase_mpz_ln_10_entrada | fibra | supuesto | 7 x 60 x 50 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_voa_entrada | fibra | supuesto | 6 x 60 x 60 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_voa_salida | fibra | supuesto | 50 x 60 x 60 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_aislador_entrada | fibra | supuesto | 50 x 60 x 60 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_aislador_salida | fibra | supuesto | 6 x 60 x 60 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_filtro_espectral_entrada | fibra | supuesto | 6 x 60 x 56 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_filtro_espectral_salida | fibra | supuesto | 50 x 60 x 56 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_acoplador_monitor_entrada | fibra | supuesto | 50 x 60 x 56 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_acoplador_monitor_salida | fibra | supuesto | 6 x 60 x 56 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| fibra_colimador_entrada | fibra | supuesto | 50 x 48 x 55 | Tramo recto de 20 mm (integracion.fibra.longitud_boot_modelada) mas el envolvente de un codo de 30 mm (integracion.fibra.radio_curvatura_modelado). Lo |
| coaxial_mod_intensidad_mxer_ln_10 | coaxial | supuesto | 26 x 25 x 50 | Envolvente de un codo de 25 mm a la salida del conector RF (integracion.coaxial.radio_curvatura_modelado, SUPUESTO). El conector SI es dato: 6.1 x 10  |
| coaxial_mod_fase_mpz_ln_10 | coaxial | supuesto | 26 x 25 x 50 | Envolvente de un codo de 25 mm a la salida del conector RF (integracion.coaxial.radio_curvatura_modelado, SUPUESTO). El conector SI es dato: 6.1 x 10  |
| haz_e01 | haz_libre | supuesto | 5 x 10 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e02 | haz_libre | supuesto | 5 x 10 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e03 | haz_libre | supuesto | 10 x 10 x 16 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e04 | haz_libre | supuesto | 10 x 5 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e07 | haz_libre | supuesto | 5 x 10 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e09 | haz_libre | supuesto | 10 x 5 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_e10 | haz_libre | supuesto | 5 x 10 x 10 | Tubo de 10 mm de lado (integracion.optica.diametro_haz_modelado, SUPUESTO) en el hueco que queda entre las dos piezas. El diametro de haz de cada tram |
| haz_telescopio_colimado | haz_libre | supuesto | 90 x 90 x 186 | Envolvente del haz dentro del barrilete, derivada de 'optica' en data/components.yaml. SUPUESTO por partida doble: la apertura libre es una decision d |
| haz_telescopio_comprimido | haz_libre | supuesto | 10 x 10 x 192 | Envolvente del haz dentro del barrilete, derivada de 'optica' en data/components.yaml. SUPUESTO por partida doble: la apertura libre es una decision d |

