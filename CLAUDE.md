# CLAUDE.md — Estado, decisiones y razonamiento

Documento de continuidad entre sesiones. El README explica **qué** es el
repositorio; esto explica **por qué** está como está y **qué falta por decidir**.

Última actualización: **2026-09-21** (cadena óptica reordenada y frontera de la
codificación §3.10; antes: telescopio paramétrico §4.7 y brazo de los beacons
con dos dicroicos §3.9).

---

## 1. Dónde estamos

| | |
|---|---|
| Catálogo | 37 componentes, 0 problemas de integridad |
| Con envolvente | **34 de 37**. Los 3 que faltan, por buenos motivos (§1.1) |
| Huecos sin ninguna aproximación (TBD) | **61**. Los 10 nuevos son de la cadena de fibra (§3.10): si la guía del MPZ es bipolarización —sin eso el esquema de un solo modulador es imposible—, la sensibilidad térmica de la fase en PM, la retardancia del espejo de plegado y qué par de bases usa el enlace |
| Números inventados aquí (SUPUESTO) | **75** — se dibujan, no son datos (§2). 28 → 61 con el telescopio paramétrico (§4.7), → 68 con el brazo de los beacons (§3.9) y → 75 con la cadena de fibra (§3.10), cada uno con su razonamiento y a quién pedirlo |
| Discrepancias entre fuentes | **10** |
| Tests | **180**, todos en verde |
| Distribución | **CONFIRMADA** el 2026-09-20 y **repartida otra vez el 2026-09-21** (§3.10): la bandeja es sólo la fuente y la franja lleva modulación, monitorización, atenuación y codificación, apiladas en Y |
| Piezas colocadas | **28**, y **dos que no caben**: `camara_beacon` (§3.9) y `mod_fase_mpz_ln_10` (§3.10). Una pieza sin sitio no se dibuja en un sitio inventado |
| Geometría real de fabricante | **3** piezas salen de un STEP de AAC (§9); el telescopio tiene sitio reservado para el suyo |
| Keep-outs | **19**, todos dibujados con números supuestos (§3.7, §4.7, §3.9). El del brazo de los beacons lo comparten dos tramos en sentidos contrarios y se declara una sola vez; el tramo post-codificación **no lleva ninguno**, porque no se puede curvar (§3.10) |
| Choques de geometría | **0**. `clau3d informe` devuelve 1 de todas formas, y ahora por **dos** chequeos críticos: `brazo_beacon` (§3.9) y `fibra_post_codificacion` (§3.10) |
| Riesgos abiertos | **5**: térmico modulador–barrilete (§3.6), antena en −Z (§3.8), la longitud del telescopio, que cabe en los 200 mm por 1.2 mm (§4.7), **el brazo de los beacons, que no cabe por 6.8 mm** (§3.9) y **el tramo recto post-codificación, que no cabe por 18.0 mm** (§3.10). El de la fibra del colimador (§3.7.1) **está resuelto** |
| Zona útil | 221.7 × 95.4 × 361.4 mm = **7.64 L**, de la que quedan **2.92 L** libres |

Funciona de punta a punta: catálogo validado, layout generado, ensamblaje
exportado a STEP —completo y por subsistema—, interferencias, conexiones,
volumen, presupuestos, vistas, informes y `components_status.csv` para la hoja
de Drive. Para mirarlo, `uv run clau3d ver` (§8).

**Lo que cambió el 2026-09-20 por la tarde.** Hasta entonces 19 de 27
componentes no tenían envolvente y no se dibujaban, así que el modelo no podía
comprobar nada del payload: ni interferencias, ni recorridos, ni volumen libre
de verdad. Ahora se dibujan todos, con un estado nuevo —`supuesto`— que dice a
las claras cuáles de esos cuerpos están ahí porque alguien se inventó una cota.
El precio de dibujarlo todo es que el volumen libre baja de 5.84 L a **2.88 L**:
la primera cifra no era mejor noticia, era menos información.

### 1.1 Los tres que siguen sin envolvente, y por qué está bien

- **`radio_uhf_pulsar_vutrx`** y **`propulsion`**: opcionales, y la decisión de
  misión está abierta. Reservarles volumen sería decidir por el equipo.
- **`cables_rf_moduladores`** (ELEC-04): un coaxial no tiene envolvente hasta
  que se encamina. Lo que ocupa es el tubo que barre al curvarse, y eso es un
  **keep-out**, no un cuerpo. Está modelado así.

### 1.2 Lo que el modelo encontró al dibujarlo todo

Cuatro cosas que no se veían con 8 piezas colocadas, y que están detalladas más
abajo:

1. **La pila PC104 mide 305 mm, no 259.** Las ranuras se reservaban con la
   altura de ficha y se dibujaban con el STEP, y las fichas de AAC no incluyen
   el conector PC104 pasante. Sigue cabiendo en los 361 mm, con 56 mm de
   margen en vez de 102. Ver §4.6.
2. **El banco óptico es el punto apretado del payload**, y no se ve mirando
   volúmenes: sobra hueco en el banco, pero no *en la línea* que va del eje del
   telescopio a la pared. Ver §3.7.
3. **El colimador no tenía por dónde sacar su latiguillo.** Ver §3.7.
   **Resuelto el 2026-09-21** por la reordenación de la cadena (§3.10): ahora lo
   alimenta el codificador en línea recta y ese keep-out ya no existe.
4. **La antena de banda S no tiene cara libre** y acaba en −Z, apuntando al
   lado contrario que el telescopio. Ver §3.8.

---

## 2. Cómo se trabaja aquí

- **Ningún número en el código.** Todo sale de `data/*.yaml`. Si hace falta un
  número nuevo, va al catálogo con fuente y estado, no a un literal.
- **Un hueco se queda como hueco.** `TBD` obliga a `falta` y `pedir_a`, y el
  valor tiene que ser `null`. Hay un test para cada una de esas tres cosas.
- **Un número inventado se declara como inventado.** `supuesto` es el estado
  para una cota que este repositorio se ha sacado de la manga porque hacía
  falta un número con el que dibujar. Lleva la carga de los dos mundos: exige
  `fuente` como cualquier magnitud —pero ahí va el **razonamiento**, no una
  ficha— y exige además `falta` y `pedir_a` como un TBD, porque el dato de
  verdad sigue sin estar. **No suma en los presupuestos** de masa ni de
  potencia, se dibuja en gris y más transparente, y aparece en
  `reports/06_pendientes.md` con el valor concreto que hay que sustituir.
  La diferencia con TBD no es si el dato está: es si existe una aproximación
  defendible. Con ella la pieza se dibuja; sin ella, no.

  El motivo de abrir esta puerta: con 19 componentes sin dibujar, el análisis
  de interferencias y el de volumen libre no decían nada del payload. Reservar
  un volumen aproximado y marcarlo es más útil que no reservar ninguno. Lo que
  la puerta **no** hace es relajar el TBD: sigue sin poder llevar valor, y el
  mensaje de error ahora enseña la salida buena en vez de solo prohibir.
- **Un keep-out lleva procedencia, igual que un número.** `estado` y `fuente`
  son obligatorios. Hoy los 18 que hay son todos `supuesto`, porque las tres
  cotas que los dimensionan —radio mínimo de curvatura de la fibra, el del
  coaxial y el diámetro de haz— siguen siendo TBD.
- **Un puerto que existe se declara, se dibuje o no.** Un divisor dicroico a
  45° tiene cuatro puertos, y los cuatro reciben luz aunque sólo dos estén en
  el diagrama de nadie. El catálogo los escribe uno a uno en un campo `puertos`
  con el tramo que va por cada uno, y hay un test que comprueba que ese tramo
  existe en `connections.yaml` y toca a esa pieza. Así el cuarto puerto acaba
  en una trampa de luz o en un fotodiodo en vez de acabar en el sitio donde
  acaba de verdad, que es rebotando por dentro del banco.
- **Un tramo que se recorre en los dos sentidos es un tramo, no dos.** El
  keep-out se declara una vez y el otro lo referencia con
  `keep_out_compartido_con`. Duplicar el volumen no reserva nada nuevo:
  reserva lo mismo otra vez, y el detector de interferencias ve dos cajas
  idénticas solapando al 100 % e informa de una invasión que no existe.
- **Una pieza sin sitio no se coloca.** Si una fila del banco no cabe en su
  zona, el generador **no la dibuja** —ni apretada, ni saliéndose del
  satélite—, avisa por stderr y deja que el chequeo lo cuente en milímetros.
  Apretarla esconde el resultado; dibujarla fuera rompe las dos invariantes que
  este repositorio sí defiende con tests, cero solapes y nada fuera de la
  envolvente, y las convierte en ruido. Pasó con la cámara de beacon (§3.9).
- **Una invasión de keep-out supuesto no tumba el código de salida.** Si lo
  hiciera, la manera de poner CI en verde sería bajar el radio de curvatura
  supuesto hasta que las invasiones desaparecieran, que es exactamente lo que
  no se quiere que nadie haga. `clau3d informe` devuelve 1 por choques de
  geometría, no por consecuencias de una hipótesis.
- **La procedencia de un STEP se puede declarar antes que el STEP.** De los
  ficheros que faltan ya se sabe quién los tiene y de qué producto son, así que
  `forma.step_esperado` lo escribe por adelantado: ruta, a quién pedirlo y
  fuente prevista. Dejar el fichero en esa ruta basta para que sustituya al
  modelo aproximado sin tocar el catálogo, y entra como `referencia`, porque
  que aparezca donde se esperaba no verifica su part number. Lo que sigue sin
  existir es la tercera vía: importar cualquier fichero que se llame como el
  componente.
- **Lo no comprobable se declara.** Un chequeo sin datos sale como
  `no comprobable`. Nunca como `ok`.
- **Los tests sintéticos son obligatorios.** Con el layout vacío, un test de
  interferencias pasaría solo. Por eso `tests/test_interferencias.py` comprueba
  además, con geometría inventada, que los detectores detectan de verdad.
- **Verificar contra la fuente primaria.** Las cifras de este repositorio se han
  sacado de los PDF originales, no de agregadores. Dos de ellas contradecían el
  brief de partida (ver §4).
- **La U no es una unidad de volumen.** La U de la CDS es un *formato*: una
  ranura de dispensador de 100 × 100 × 113.5 mm. Usarla además como 1000 cm³
  produce frases sin sentido como «la envolvente 6U mide 8.28 U». Aquí los
  volúmenes van en **cm³ y litros**, las longitudes en **mm**, y «6U» se refiere
  siempre al formato de la envolvente exterior (226.3 × 100 × 366 mm).
- **Un STEP lleva procedencia, igual que un número.** El bloque `forma.step`
  del catálogo exige `estado` y `fuente`, y `validar` falla sin ellos. Un STEP
  `referencia` es el de un producto parecido, o el de uno cuyo part number no se
  ha verificado; se dibuja en naranja y el informe lo dice. La geometría
  dibujada manda sobre la ficha a la hora de colorear: una pieza con ficha
  confirmada y STEP de referencia sale como referencia, porque lo que se está
  viendo es el STEP.
- **El CAD de fabricante no se versiona; su huella sí.** El repositorio es
  público y las condiciones de uso de los CAD de AAC están sin revisar. En git
  va `cad/vendor/MANIFEST.yaml` con el SHA-256 de cada fichero. Quien clone sin
  los CAD lo ejecuta todo igual, con cajas envolventes. Ver §9.
- **Una comprobación circular no es una comprobación.** Si una cota se dedujo de
  una pieza, comprobar esa misma pieza contra esa cota devuelve la hipótesis, no
  un resultado. Sale como `no comprobable`, igual que un chequeo sin datos.
- **Lo que se reserva se mide sobre lo que se dibuja.** Reservar con la cota de
  ficha y dibujar con el STEP hace que los dos números dejen de hablar de lo
  mismo. Pasó con la pila PC104 y costó 46 mm (§4.6).
- **El nombre de un fichero generado dice si se puede publicar.** Un STEP de
  subsistema que lleve dentro una pieza dibujada con CAD de fabricante
  *contiene* ese CAD, y el repositorio es público. El sufijo
  `_con_cad_de_fabricante` lo pone el exportador mirando lo que ha metido, no
  una lista escrita a mano que se quedaría obsoleta con el siguiente STEP de
  proveedor, y el `.gitignore` ignora ese sufijo. Hay un test que comprueba que
  el sufijo del código y el del `.gitignore` siguen siendo el mismo.
- **Los identificadores de Drive conviven con los del repositorio.** `id` dice
  qué es la pieza y es legible; `id_drive` (OPT-01, PLAT-04, ELEC-02…) dice en
  qué fila de la hoja índice del equipo está. `validar` rechaza dos piezas con
  el mismo `id_drive`, porque pisarían la misma fila al actualizar la hoja
  desde `reports/components_status.csv`.

---

## 3. Distribución confirmada (2026-09-20)

Elegida entre dos opciones: **dos columnas de 3U a lo largo de todo Z**.
Revisada el mismo día: los moduladores pasan de la bandeja a la **franja
lateral** que queda junto al telescopio, para desatascar la longitud del
telescopio. Ver §3.6.

### Sistema de coordenadas

Origen en el centro geométrico (CDS 14.1 req 2.2.1).
X = ±113.15 (ancho, 226.3) · Y = ±50.00 (alto, 100.0) · Z = ±183.00 (largo, 366.0).
La cara **−Z entra primero** en el dispensador. Zona útil interior con el espesor
declarado: **221.7 × 95.4 × 361.4 mm** ≈ 7.64 L.

### El reparto

```
        −Z ←────────────────── Z (361.4 mm útiles) ──────────────────→ +Z
        (entra primero)                                    (apunta a tierra)

 +110.85 ┌──────────────────────┬─────────────┬─────────────────────────┐
         │                      │             │ z_payload_franja 0.50 L │
         │                      │             │ 26.3 mm de X, 3 bandas  │
         │                      │             │ en Y: acoplador+VOA /   │
         │                      │             │ colimador+codificador / │
  PAYLOAD│ z_payload_bandeja    │ z_payload   │ MXER. §3.10             │
  121.7  │ 1.24 L               │  _banco     ├─────────────────────────┤
   mm    │ LA FUENTE: láser DFB │ 0.64 L      │ z_payload_telescopio    │
         │ (4.1 W), aislador y  │ espejo de   │ 1.82 L · 95.4 mm de X   │
         │ filtro. Bucles en    │ plegado,    │ telescopio →→ +Z        │
         │ los 121.7 mm de      │ D1, D2      │ 200 mm RESERVADOS       │
         │ ancho enteros        │ FSM, brazo  │ (provisional)           │
  −10.85 ├──────────────────────┴─────────────┴─────────────────────────┤
         │ z_plataforma  3.45 L                                         │
  PLATAF.│ pila PC104 a lo largo de todo Z — 305 mm usados de 361 mm     │
  100 mm │ −Z ← baterías·baterías·PCB-2·PCB-1·PCB-3·radio·EPS·OBC·ADCS → │
 −110.85 └──────────────────────────────────────────────────────────────┘
             106.4 mm             55 mm            200 mm
```

| zona | volumen | libre | contenido |
|---|---|---|---|
| `z_plataforma` | 3.45 L | 1.22 L | Pila PC104 (305 mm) + antena en el extremo −Z |
| `z_payload_telescopio` | 1.82 L | 0.00 L | Telescopio, dibujado **llenando la zona** a propósito (§4.2) |
| `z_payload_franja` | 0.50 L | 0.45 L | Colimador, MXER, acoplador 2×2 y VOA, **apilados en Y**. **El codificador no cabe** (§3.10) |
| `z_payload_banco` | 0.64 L | 0.57 L | Espejo de plegado, D1, FSM y el brazo de los beacons: D2, láser, trampa y fotodiodo. **La cámara no cabe** (§3.9) |
| `z_payload_bandeja` | 1.24 L | 1.18 L | Placa, láser DFB, aislador y filtro — **sólo la fuente** (§3.10) |

Los paneles solares no están en ninguna zona: van **por fuera**, sobre las dos
caras grandes, con la protrusión que concede la CDS 14.1 req 2.2.3. El layout
los marca `zona: exterior`, que no es una de las cinco que embaldosan el hueco
útil, y el detector de desbordes los trata aparte.

Las cinco zonas **embaldosan exactamente** la zona útil; hay un test que lo
comprueba. La columna de payload se parte en X **solo a lo largo del
telescopio**: 95.4 mm para el barrilete y 26.3 mm de franja.

### Orden de la pila, de +Z a −Z

Con el paso estándar PC/104 de 15.24 mm; una tarjeta más alta ocupa
`ceil(altura / paso)` posiciones de separador.

La altura que manda es la **dibujada**, no la de ficha: ver §4.6.

| # | tarjeta | ficha | dibujado | posiciones | por qué ahí |
|---|---|---|---|---|---|
| 1 | iADCS400 | 67.30 mm | 67.30 | 5 | En +Z, para que el ST200 mire por la misma cara que el telescopio |
| 2 | Kryten-M3-PLUS | 5.51 mm | **23.24** | 2 | Junto al ADCS y al payload |
| 3 | Starbuck-Nano-PLUS | 20.82 mm | 20.82 | 2 | |
| 4 | Quasar-STRX | 16.90 mm (ref) | 16.90 | 2 | |
| 5 | PCB-3 PAT | — | 15.00 (sup.) | 1 | Junto al ADCS, de quien recibe la actitud, y a la altura del banco |
| 6 | PCB-1 Control QKD | — | 15.00 (sup.) | 1 | La que más habla con el OBC (bus y PPS del GNSS) |
| 7 | PCB-2 Drivers | — | 15.00 (sup.) | 1 | La más hacia −Z de las tres: lo más cerca posible de la bandeja |
| 8-9 | Optimus-30 ×2 | 21.55 mm | **36.44** | 3 cada una | En −Z, equilibran la masa del telescopio |
| | **total** | | | **20** | **305 mm de 361 mm** |

Detrás de las baterías, contra la pared −Z, va la **antena de banda S** (§3.8).
El hueco que queda entre la pila y la antena es lo que le tocaría al UHF de
respaldo y a la propulsión si se deciden.

### Por qué así

1. **El telescopio manda, y va en +Z.** La apertura necesita vista despejada, y
   poniéndola en +Z se aleja del dispensador (−Z entra primero) y deja libre
   toda la superficie lateral para los paneles.
2. **El ADCS arriba de la pila.** El ST200 también necesita ver fuera, y le
   conviene mirar por la misma cara que el telescopio: cuanto más cerca y más
   rígida la unión, menos error de coalineación en el traspaso grueso a fino.
3. **Las baterías al final de −Z.** Equilibran en Z la masa del telescopio (el
   CdG está limitado a ±70 mm en Z) y quedan lejos del láser: son lo más
   delicado térmicamente de la plataforma, −10 a +50 °C.
4. **La columna de plataforma mide 100 mm** porque el iADCS400 necesita 95.9 mm
   de contorno, más holgura de montaje. El resto, 121.7 mm, es el payload.

### 3.6 Los moduladores van en la franja, no en la bandeja

**El problema que resuelve.** Con los moduladores en la bandeja hacían falta
130 mm de Z solo para su recorrido recto. Con el banco fijo en 55 mm, el
telescopio no podía pasar de **176.4 mm ni vaciando la bandeja**: la distribución
no llegaba a los ~2U del brief por construcción.

**La franja no depende del dato que falta.** El barrilete no puede superar los
95.4 mm de altura interior — es el problema de §4.2 —, luego a su lado siempre
quedan al menos `221.7 − 100 − 95.4 = 26.3 mm` de X, para cualquier diámetro que
permita montar el telescopio. El generador toma ese mínimo, así que la franja no
se recalcula cuando llegue el diámetro real.

**Los moduladores van tumbados**: 9.7 mm por X (el eje escaso), 15 mm por Y
(donde sobra sitio) y 110 mm por Z. Así el conector RF lateral (6.1 × 10 mm)
sobresale hacia ±Y y no hacia la franja. Los dos caben en paralelo: 19.4 mm de
los 26.3. Van **pegados al extremo −Z de la franja**, que es el lado del banco y
de la bandeja, para que los tramos extra de fibra salgan lo más cortos posible.

**El láser DFB se queda en la bandeja.** Con sus 4.1 W es la principal fuente de
calor del payload y no debe acercarse al barrilete.

**La longitud del telescopio es un parámetro, no un dato.** Vive en
`data/components.yaml` como `telescopio_cassegrain.longitud_reservada`, estado
`decision`, valor provisional 200 mm. **Cuidado con «2U»:** la U de longitud de
la CDS son 113.5 mm, no 100, así que los «~2U» del brief son ~227 mm. El reparto
admite ambos:

| L reservada al telescopio | bandeja residual |
|---|---|
| 200 mm (valor actual) | 106.4 mm |
| 227 mm (los «2U» de verdad) | 79.4 mm |
| 306.4 mm (techo, bandeja a cero) | 0 mm |

La longitud real saldrá del STEP del telescopio (Óscar). Cambiar esa magnitud y
regenerar el layout es todo lo que hace falta para reasignar el reparto.

### Lo que cuesta

- **Riesgo térmico abierto, no bloqueante.** Los moduladores quedan acoplados al
  barrilete, que quiere estabilidad térmica, y su extinción solo está garantizada
  entre 0 y +70 °C. A favor: los moduladores de niobato **apenas disipan** — los
  drivers van en PCB-2, en la otra columna — y el láser, que es lo que calienta,
  se queda en la bandeja. Mitigación prevista: soportes de baja conductividad
  térmica y sensor/calefactor propios. **Pendiente de validación del equipo
  térmico.**
- **Dos tramos extra de fibra** de ~100 mm entre la bandeja y los moduladores,
  con sus curvas. Sin el radio mínimo de curvatura **no se puede comprobar**, que
  es el mismo bloqueo de siempre.
- **Acceso.** Los moduladores quedan difíciles de alcanzar una vez montado el
  telescopio.
- **PCB-2 sigue en la otra columna.** El coaxial RF cruza el satélite a lo ancho.
  En distancia de Manhattan la tirada apenas cambia (216/241 mm antes, ~222 mm
  ahora): el acercamiento en Z compensa el alejamiento del extremo −Z.

### Lo bueno que compra

- **El telescopio deja de estar limitado por la bandeja**: de un techo de
  176.4 mm a uno de 306.4 mm.
- **La bandeja se queda sin cuerpos dentro**: 121.7 × 95.4 × 106.4 mm con el
  ancho entero disponible para curvar. Antes los bucles tenían que sortear dos
  cuerpos de 110 mm, que era el punto flojo declarado de la distribución.
- **La pila PC104 deja de ser el problema**: **305 mm usados de 361 mm**, con
  56 mm de margen para que las tres PCBs propias crezcan más de una posición de
  separador. En la otra opción la pila tenía 198 mm y ya iba justa.
  (Este número era 259 mm hasta que se dibujaron las tarjetas propias y salió
  a la luz que las ranuras se reservaban con la altura de ficha; ver §4.6. El
  margen se ha quedado en la mitad, pero la conclusión no cambia: cabe.)

### 3.7 El banco óptico es el punto apretado del payload

Y no se ve mirando volúmenes: en el banco sobra hueco —0.58 L de 0.64— pero no
**en la línea** que importa. Desde el 2026-09-20 por la noche son **dos**
líneas: esta, en X, y la del brazo de los beacons, en Y, que es peor todavía
porque no cabe (§3.9).

**Por qué esa línea no se puede mover.** El FSM dobla el haz que llega según X
hacia el telescopio, que apunta según +Z. Para doblarlo tiene que estar *sobre
el eje óptico del telescopio*, en X = +36.85 mm. Eso deja a D1 y al **espejo de
plegado** en fila con él, hacia +X, y lo que tienen es lo que va del eje a la
pared de la columna: **74.0 mm**.

**Desde el 2026-09-21 el tercero de la fila es el espejo de plegado y no el
colimador** (§3.10), y eso desahoga esta línea: el espejo reserva 20 mm donde el
colimador reservaba 28.

Las reservas iniciales (colimador de 40 mm, D1 de 30) **no cabían**. Están
ahora en 20 y 23, y su `fuente` en el catálogo lo dice: la cota está *acotada
por arriba por el banco*, no solo elegida a ojo. Sumando la media anchura del
FSM a 45°, la línea ocupa 58.3 mm y quedan **15.7 mm** —eran 7.7 antes de que el
colimador saliera de la fila—. El chequeo `banco_optico` lo recalcula desde el catálogo, avisa por
debajo de 5 mm y falla si se pasa. Mira además los dos puertos laterales de D2
—el láser de beacon hacia −X y el fotodiodo hacia +X—, que están dentro del
mismo ancho de banco y hoy tienen 33.0 y 23.7 mm de margen.

**Si las piezas reales son mayores, no es que el modelo esté mal: es que el
banco no da.** La salida sería alargarlo a costa de la bandeja o de la longitud
reservada al telescopio, no apretar las piezas.

### 3.7.1 El colimador no tenía por dónde sacar su latiguillo — RESUELTO

**Lo que pasaba** hasta el 2026-09-21: estaba pegado a la pared +X con 7.7 mm y
su fibra tenía que volver a la bandeja, que está en −Z. Con la reserva supuesta
de fibra (20 mm de tramo recto + 30 mm de radio de curvatura = 50 mm por
puerto), su keep-out se comía al FSM, a D1, a D2 y al láser de beacon: cuatro de
las quince invasiones del modelo.

**Lo resolvió la reordenación de la cadena (§3.10)**, y no por casualidad: el
tramo que alimenta al colimador sale del codificador de polarización y **tiene
prohibido curvarse**, así que ahora el colimador apunta según −Z, lo alimenta el
codificador en línea recta y su tramo lleva `recto: true`. Un tramo que no se
puede curvar no tiene codo que reservar, así que **ya no genera keep-out de
curvatura** y las cuatro invasiones desaparecen.

La alternativa —dejar el colimador según X, como estaba, con la fibra curvada—
no era incómoda, era **imposible**: exigiría un radio de curvatura menor o igual
que el margen que tenía a la pared, 7.7 mm, y el radio modelado es 30.

Lo que el arreglo cuesta está en §3.10: una superficie reflectante más en el
camino cuántico, y un tramo recto de 218 mm que **no cabe por 18.0 mm**.

### 3.7.2 La bandeja tampoco respeta un radio de 30 mm

Mismo origen, mismo dato. Las filas están a 8 mm y cada puerto de fibra querría
50. Con el reparto del 2026-09-21 la bandeja tiene tres piezas en vez de cinco,
así que de las **7** invasiones de keep-out que reporta el modelo —eran 15— 5
son de la bandeja y 2 de la franja. Bajaron porque hay menos puertos de fibra en
la bandeja y porque el colimador ya no tiene keep-out de curvatura (§3.7.1), no
porque el problema esté resuelto: **el dato que falta sigue siendo el mismo**.

`reports/03_interferencias.md` las lista en una sección aparte que empieza
diciendo que **no es una lista de errores**. La manera de resolverlas no es
bajar el radio supuesto hasta que desaparezcan.

### 3.8 La antena de banda S es la pieza que peor lo tiene

Necesita ver la Tierra y **no hay cara libre**:

- **+Z** la ocupan el telescopio y el star tracker del ADCS.
- Contra **±X** y **±Y** la pila PC104 deja 2–3 mm hasta la pared.
- **Por fuera** tampoco: sus 10 mm supuestos de espesor no caben en los 6.5 mm
  de protrusión que permite la CDS 14.1 req 2.2.3.

Queda **−Z**, que es el hueco de detrás de las baterías. Y eso tiene un coste
que hay que decidir: −Z es la cara que entra primero en el dispensador y, sobre
todo, **apunta al lado contrario que el telescopio**. Con el satélite apuntando
+Z a la estación óptica durante un pase de QKD, esta antena mira al cenit.

Puede no ser un problema —el canal clásico de post-procesado no tiene por qué
ser simultáneo al pase óptico— pero es una **decisión de operaciones**, no de
mecánica, y está sin tomar. Si el espesor real de la antena fuera menor de
6.5 mm, podría ir por fuera en cualquier cara y el problema se evapora.

### 3.9 El brazo de los beacons: dos dicroicos, un solo brazo, y no cabe

Añadido el 2026-09-20 por la noche. Es el cambio que hace que el beacon de
bajada **exista** en el modelo, y el que enseña que el banco tiene un segundo
punto apretado además del de §3.7 —y este en el otro eje.

**Lo que estaba mal.** `camara_beacon` en Y = +31.5 y `laser_beacon_bajada` en
Y = −31.5: en lados **opuestos** del dicroico. Un láser que emite hacia +Y
contra la cara trasera de un dicroico a 45° sobre el eje X no tiene camino
hacia el FSM: la luz entra por el puerto equivocado y no sale a ninguna parte.
Y en `connections.yaml` el beacon de bajada **no tenía ni una conexión
declarada**: `e04` era el único tramo del brazo, y sólo cubría la cámara. La
pieza se dibujaba, ocupaba volumen y no funcionaba. Nada lo cazaba porque los
tests de conexiones comprobaban que los extremos declarados existieran, no que
las piezas declaradas tuvieran extremos. Ahora hay un test que va al revés
(`tests/test_brazo_beacon.py`), y es el que habría pillado esto.

**La arquitectura correcta** (decisión de ACSAR, 2026-09-20): los dos beacons
comparten **un único brazo lateral**, el que refleja D1, y dentro de ese brazo
un segundo dicroico D2 los separa.

| | | |
|---|---|---|
| **D1** (`dicroico_d1`, OPT-09) | paso largo, borde ~1300 nm | transmite 1550 → FSM; refleja **los dos** beacons al brazo |
| **D2** (`dicroico_d2`, OPT-15) | paso corto, borde ~1020 nm | transmite 976 → cámara; refleja 1064, inyectado lateralmente |

> **Ojo con los `id_drive`.** La tarea pedía OPT-14 para `dicroico_d2`, pero
> OPT-14 ya lo usa `bandeja_optica` y `validar` rechaza dos piezas con el mismo
> identificador de Drive —pisarían la misma fila al actualizar la hoja desde
> `components_status.csv`—. Las cuatro piezas nuevas van en **OPT-15 a OPT-18**,
> que sí estaban libres. Hay que **dar de alta esas cuatro filas** en la hoja
> índice del equipo.

Los cuatro puertos de cada uno tienen destino declarado, y el catálogo los
escribe uno a uno en un campo `puertos`:

```
       camara_beacon (976 nm, transmision)
             |
  laser --- D2 --- fotodiodo_monitor_beacon   (fuga del beacon en transmision)
             |
            D1 --- FSM --- telescopio         (1550, transmision)
             |
       trampa_luz_d1                          (fuga del 1550 en reflexion)
```

**Los cuartos puertos no son opcionales.** Ningún divisor transmite el 100 %.
Lo que D1 no transmite del 1550 sale por el puerto opuesto al brazo, y sin
trampa se queda rebotando dentro del banco hasta llegar a la cámara de
seguimiento o de vuelta al canal. De ahí `trampa_luz_d1` (OPT-17). El cuarto
puerto de D2 recibe la fuga en transmisión del beacon de bajada, y eso sí se
puede aprovechar: un `fotodiodo_monitor_beacon` (OPT-16) da telemetría de salud
del beacon **sin tocar el haz útil**. Si el equipo de PAT decide no
instrumentarlo, hace falta igualmente taparlo: `trampa_luz_d2` (OPT-18) está en
el catálogo como `alternativa_de` del fotodiodo —**excluyente**, no adicional—,
así que no suma en ningún presupuesto ni se coloca, igual que el FSM piezo.

**El orden dentro de D2 no es intercambiable.** Con la cámara en transmisión y
el beacon en reflexión, los 100 mW del beacon tocan **una sola superficie con
recubrimiento** antes de salir, y lo que se fugue en D2 se va al puerto opuesto
al láser en vez de hacia el sensor. Invertirlo mete el beacon en transmisión
—dos superficies más— y apunta su fuga justo a lo que hay que proteger.

#### Las longitudes de onda: 976 arriba, 1064 abajo

Y el motivo es el **silicio**, no la óptica. Un CMOS de silicio tiene QE decente
a 976 nm y está prácticamente ciego a 1064 nm (<1 %). Esa ceguera regala **dos o
tres órdenes de magnitud de rechazo por encima** del filtro de banda estrecha, y
es lo único que permite que un sensor que mide microvatios de beacon de subida
conviva en el mismo brazo con 100 mW de beacon de bajada. Invertir la asignación
pierde ese aislamiento y obliga a una cámara InGaAs. Abajo no cuesta nada: 1064
es la línea del Nd:YAG, y en tierra se detecta con APD de silicio —que a 1064
todavía responde lo justo, y hay detectores comerciales de sobra— o con InGaAs,
donde el tamaño y el consumo no importan.

**El número que sostiene todo esto no existe.** `aislamiento_camara_a_1064` es
TBD y es del equipo de PAT. Hoy la elección de colores se defiende con un
argumento físico correcto y **ninguna medida**. Si sale corto, las salidas son
separar más los dos colores, apagar el beacon mientras la cámara lee, o volver a
dos brazos separados —y eso último ya se sabe que no cabe.

#### El filtro de banda estrecha no es una pieza

Va declarado **dentro** de la reserva de `camara_beacon` y dicho en su `fuente`.
No es pereza: modelarlo suelto añade una pieza más a la fila del brazo, y el
brazo ya no cabe sin ella.

#### Y no cabe

Aquí está el precio de la arquitectura, y es geométrico. Antes la cámara y el
láser usaban lados **opuestos** de D1, así que cada uno tenía 47.7 mm para él
solo. Compartiendo brazo, D1/2 + D2 + cámara van **en fila hacia un solo lado**:

| | mm |
|---|---|
| semi-D1 | 11.5 |
| D2 | 23.0 |
| cámara (bajada de 30 a 20) | 20.0 |
| **necesario** | **54.5** |
| disponible, del centro de D1 a la pared | 47.7 |
| **falta** | **6.8** |

Y eso ya con la única salida que **no le cuesta volumen a nadie**: bajar la
reserva de `camara_beacon` de 30 a 20 mm, como `supuesto`, con el razonamiento
escrito en el catálogo (sensor pequeño con objetivo corto a 976 nm, filtro
incluido, sin sensor elegido). Las otras dos salidas se pagan y **son decisiones
de ACSAR**, así que están escritas y no aplicadas:

1. **Plegar el brazo hacia −Z** con un espejo de doblado: da unos 27.5 mm más, a
   costa de una superficie reflectante adicional en el camino del beacon.
2. **Alargar el banco**, que se paga con la bandeja o con la longitud reservada
   al telescopio (§3.6), exactamente igual que la salida de §3.7.

`chequeo_brazo_beacon` recalcula el margen desde el catálogo —las cuatro ramas,
incluidas las trampas y el fotodiodo, que son pequeños pero se pagan del mismo
presupuesto— y **falla**, y se queda fallando. Eso es un resultado.

**Y la cámara no está colocada.** Con las holguras de montaje el déficit sube a
16.8 mm, así que el generador **no la coloca** y avisa por stderr. Las otras dos
opciones eran apretarla, que esconde el resultado, o dibujarla saliéndose del
satélite, que además choca con el panel solar y rompe las dos invariantes que
este repositorio sí defiende con tests (cero solapes, nada fuera de la
envolvente). Una pieza sin sitio no se dibuja en un sitio inventado. Consecuencia
visible: `e06` (D2 → cámara) sale como **no comprobable, sin colocar** en
`reports/04_conexiones.md`, que es exactamente lo que está pasando.

#### El beacon de bajada comparte el FSM, y eso tiene cola

Sale por D2, vuelve a D1 y se refleja al mismo espejo que el canal cuántico, así
que recibe el **mismo punto de adelanto**. Es lo que se quiere —el beacon tiene
que llegar adonde *estará* la estación—, pero implica que la cámara ve el beacon
de subida en la dirección de retorno, sin adelantar, mientras el FSM trabaja
adelantado. Ese desfase entre recibido y transmitido está **escrito**, en
`integracion.optica.punto_de_adelanto`, no implementado: el lazo de control del
FSM no está en este repositorio.

#### Un tramo que se recorre en los dos sentidos es un tramo, no dos

`e04` (976 subiendo, D1 → D2) y `e08` (1064 bajando, D2 → D1) son **el mismo
tubo físico**. El keep-out se declara una sola vez, en `e04`, marcado
`bidireccional` y `bicolor`; `e08` lleva `keep_out: false` y
`keep_out_compartido_con: e04`. El generador lo entiende, anota en la nota del
keep-out quién más pasa por ahí y con qué color, y **aborta** si el tramo
compartido no existe, no tiene keep-out propio o une otros extremos. Declararlo
dos veces no reservaría nada nuevo: reservaría lo mismo otra vez, y el detector
de interferencias vería dos cajas idénticas solapando al 100 % e informaría de
una invasión que no existe.

### 3.10 La cadena de fibra y la frontera de la codificación

Añadido el 2026-09-21. Es el cambio que hace que el transmisor BB84 **funcione**,
y el que enseña que la franja tiene su propio punto apretado, esta vez en Z.

**Lo que estaba mal, y no era una degradación.** La cadena declarada era:

```
láser → MXER (intensidad) → MPZ (codificador) → VOA → aislador → filtro → acoplador → colimador
```

El `mod_fase_mpz_ln_10` es el **codificador de polarización** (su propia nota:
esquema ICFO con un solo modulador de fase). Después de él existen los cuatro
estados BB84, incluidos los diagonales. Y detrás de él había esto:

- Un **aislador PM transmite un solo eje de polarización**. Colocado después del
  codificador proyecta los cuatro estados sobre la misma polarización: **borra
  la codificación entera**. No es que el enlace vaya peor; es que no hay enlace.
- Cualquier tramo de **fibra PM** después del codificador tampoco vale. Los
  estados D/A viajan a 45° de los ejes de la fibra, **no son autoestados**, y la
  birrefringencia les mete una fase que deriva con la temperatura. Los H/V
  sobrevivirían y los diagonales no: una base limpia y la otra rota, que es la
  peor forma de fallar porque el enlace *parece* funcionar.
- VOA, filtro y acoplador añaden **PDL**, que atenúa unos estados más que otros
  y deforma el conjunto.

**Por qué no lo cazaba nadie.** `test_la_cadena_de_fibra_esta_completa` fijaba
una lista escrita a mano y comprobaba que la cadena coincidiera con ella. Lo que
hacía no era proteger el orden: era **congelar el equivocado**. Mismo patrón que
§3.9: los tests miraban que la cadena estuviera *encadenada*, no que estuviera
*bien*.

#### La regla que manda

> Todo componente de fibra va **antes** del codificador de polarización. Después
> de él sólo puede ir el colimador, con el tramo de fibra más corto que permita
> la fabricación, **recto y sin curvas**.

Antes del codificador la luz va en polarización lineal fija alineada al eje
lento de la PM, que **sí** es un autoestado: ese tramo puede ser largo y
curvarse libremente. **Esta asimetría es la que decide la distribución física**,
y es la razón de todo lo que viene después.

#### La cadena corregida [decisión de ACSAR, 2026-09-21]

```
láser → aislador → filtro → MXER → acoplador 2×2 → VOA → MPZ → colimador
└──────────── fibra PM, eje lento, empalmes por fusión ────────┘ └ recto ┘
```

| # | pieza | por qué en esa posición |
|---|---|---|
| 1 | `laser_dfb_1550` | origen |
| 2 | `aislador` | pegado al láser: cualquier retrorreflexión de los moduladores desestabiliza el DFB. Primera defensa contra Troya |
| 3 | `filtro_espectral` | antes de los moduladores, para que todo lo que se module ya esté limpio de ASE |
| 4 | `mod_intensidad_mxer_ln_10` | señal / decoy / vacío |
| 5 | `acoplador_monitor` | detrás del MXER, que es lo que monitoriza; **antes** del VOA, donde todavía hay luz que medir |
| 6 | `voa` | antes del codificador por la PDL. La atenuación es lineal: da igual dónde se haga |
| 7 | `mod_fase_mpz_ln_10` | **último elemento de fibra** |
| 8 | `colimador` | pegado al codificador |

**Las restricciones son datos, no código.** Viven en `meta.restricciones_orden`
de `connections.yaml`, cada una con su motivo al lado, y el chequeo
`orden_cadena_fibra` las aplica. Nombran al codificador por su **papel**
(`funcion: codificador_polarizacion`, campo nuevo del catálogo) y no por su
`id`: el día que el codificador sea otra pieza —y puede serlo, ver
`configuracion_esquema_icfo`— la restricción sigue diciendo lo mismo.

#### El acoplador pasa a 2×2, con dos fotodiodos

Por el mismo motivo por el que los divisores declaran sus cuatro puertos: un
acoplador 2×2 tiene cuatro y los cuatro reciben luz, se dibujen o no. El de
delante es el tap de siempre (lazo de bias del MXER —su **punto de trabajo** en
voltaje, no la longitud de onda— y razones decoy/señal). El de atrás es el
**vigía de Troya**: ve la luz que entra desde el canal y que ha recorrido el
codificador y el VOA en sentido inverso. Es el único punto de la cadena donde
se puede ver venir ese ataque sin tocar el haz útil. Los dos van **dentro de la
misma envolvente**: separarlos añade dos cuerpos a la franja, que es donde
aprieta.

#### El reparto físico que sale de la regla

| zona | contenido |
|---|---|
| `z_payload_bandeja` | **la fuente**: láser DFB (4.1 W, lejos del barrilete), aislador, filtro |
| travesía PM | **una sola**, en `f03`, pre-codificación: puede ser larga y curvarse |
| `z_payload_franja` | MXER, acoplador, VOA y codificador, apilados **en Y** |
| `z_payload_banco` | espejo de plegado, D1, FSM, brazo de beacons |

**El reparto en Y no se ha elegido.** La franja tiene 26.3 mm de X y 95.4 de Y,
y la X del codificador **está pinchada**: tiene que quedar coaxial con el
colimador, que está sobre el espejo de plegado, que está donde lo deja la línea
del banco. El único eje libre para apilar es Y. Las bandas salen así:

| banda | Y | margen |
|---|---|---|
| acoplador + VOA | +25.5 … +45.5 | 2.20 mm a la pared |
| codificador (eje de fibra en Y = 0) | −7.5 … +17.5 | — |
| MXER (conector RF hacia −Y) | −40.5 … −15.5 | 7.20 mm a la pared |

Los dos conectores RF apuntan a caras **opuestas**, así que ningún coaxial pasa
por encima del otro modulador. Y los bucles de fibra van en el plano **Y-Z**:
con el radio modelado de 30 mm hacen falta 60 de diámetro, y en Y hay 95.4
(sobran 35.4) mientras que en X hay 26.3 (**faltan 33.7**).

#### El espejo de plegado, y lo que cuesta

Si el codificador alimenta al colimador en línea recta, y el codificador está en
la franja (+Z), entonces **el colimador apunta según −Z**. Pero la línea
D1 → FSM → telescopio va según X y no se mueve. Hace falta doblar el haz de −Z a
−X: `espejo_plegado_cuantico` (OPT-19), un plano metálico a 45° en el banco.

**Lo que compra**, y está verificado con los chequeos, no supuesto:

- **§3.7.1 queda resuelto.** El colimador ya no tiene que sacar un latiguillo
  curvado hacia la pared +X: lo alimenta el codificador en línea recta, y el
  tramo `f07` lleva `recto: true`, así que **no genera keep-out de curvatura** —
  no por ahorrar volumen, sino porque ahí no hay codo que reservar. Las cuatro
  invasiones del colimador desaparecen. La alternativa (colimador según X, como
  antes, con la fibra curvada) era **imposible**, no incómoda: exigiría un radio
  de curvatura ≤ 7.7 mm, que es el margen que el colimador tenía a la pared, y
  el radio modelado es 30.
- **Mejora la línea en X de §3.7**: el colimador (28 mm) sale de esa fila y entra
  el espejo (20 mm). El margen de `banco_optico` pasa de **7.71 a 15.71 mm**.
- **Una sola travesía de fibra** entre zonas, en vez de ir y volver.
- Las invasiones de keep-out bajan de **15 a 7**.

**Lo que cuesta, y hay que escribirlo.** El espejo es una **segunda superficie a
45° en el camino cuántico**, y está en el **mismo plano de incidencia** que el
FSM —los dos pliegan en X-Z—, así que sus retardancias **se suman** en vez de
compensarse. Si estuvieran en planos perpendiculares se cancelarían en primer
orden; no es el caso y no se puede fingir que lo sea.

Aun así no es un problema de fondo: el efecto es **unitario y estático**. Una
retardancia fija no destruye información, sólo gira el marco de referencia de
polarización, y la estación de tierra ya tiene que calibrar ese marco de todas
formas. La diatenuación de un metal protegido a 45° es despreciable. **Por eso
el requisito es de estabilidad, no de valor absoluto**: que no derive con la
temperatura entre calibraciones. Eso es `retardancia_45_1550`, TBD, y hay que
pedir plata u oro protegido **con la curva de fase medida**, que es lo que casi
ningún catálogo publica.

#### Y el tramo recto no cabe, por 18.0 mm

Aquí está el precio, y es geométrico. El codificador, el protector del empalme y
el colimador van **en fila según Z** y ninguno de los tres se puede apretar:

| | mm |
|---|---|
| colimador | 28.0 |
| protector de empalme (`longitud_protector_empalme`) | 60.0 |
| codificador, protectores de fibra incluidos | 130.0 |
| **necesario** | **218.0** |
| disponible: la franja en Z | 200.0 |
| **falta** | **18.0** |

**La longitud de la franja es la longitud reservada al telescopio**, así que
—y esto corrige lo que uno esperaría— **alargar el banco no ayuda**: el banco no
entra en esta cuenta. El colimador está en la franja y no en el banco porque el
banco sólo tiene 27.5 mm por encima del espejo y el colimador mide 28.

Lo que **no** se suma: el boot del colimador. En un tramo recto no hay codo que
iniciar. Si el colimador real necesitara su propio tramo rígido de strain
relief, el déficit sube en esa cantidad. Queda dicho para que nadie lo descubra
después.

**Las tres salidas, todas calculadas, y las tres decisiones de ACSAR:**

1. **Subir `longitud_reservada` del telescopio a ≥ 218 mm.** Con los **«~2U» de
   verdad del brief (227 mm, no 200 — la U de longitud de la CDS son 113.5)**
   sobran **9.0 mm**. Se paga con la bandeja, que baja de 106.4 a 79.4 mm; con
   sólo tres piezas dentro le sobran 16.6 mm. Es la salida más barata y la que
   además arregla el margen de 1.2 mm de §4.7(d).
2. **Codificador con salida colimada de fábrica**, que quitaría el empalme
   entero: `pigtail_salida_minimo`, TBD, es de Exail. Sin los 60 mm del
   protector sobran **42.0 mm**.
3. **Alargar el banco a ≥ 86 mm**, que es lo que hace falta para que el
   colimador quepa *dentro del banco* (10 de semiespejo + 5 de holgura + 28).
   Entonces la franja sólo necesita 190 y sobran 10.0 mm. Cuesta 31 mm de
   bandeja, que se queda en 75.4 y sigue dando.

Lo que **no** es una salida es bajar el protector de empalme hasta que el
chequeo pase: los 60 mm ya son el orden correcto del tramo rígido.

**Y el codificador no está colocado.** Igual que `camara_beacon` en §3.9: una
pieza sin sitio no se dibuja en un sitio inventado. `chequeo_fibra_post_codificacion`
**falla**, y se queda fallando. Consecuencia visible: `altura_eje_codificador`
sale como **no comprobable** porque no hay eje que medir, y lo dice.

#### Lo que se sabría si el codificador cupiera

El generador lo coloca **por su eje de fibra**, no por su caja: el eje pasa a
4.8 mm de la cara de montaje sobre una altura de 9.7, o sea 0.05 mm por debajo
del centro. Con la colocación que le tocaría:

- **coaxialidad con el colimador**: exacta por construcción, y el margen de la
  envolvente contra la pared −X de la franja es de **2.05 mm**;
- **altura del eje**: Y = 0.000, que es el plano óptico del banco. Desvío
  **0.00 mm** contra una tolerancia supuesta de 0.5.

Un plegado en el plano X-Z conserva Y; cualquier desfase en Y obligaría a una
curva en S **después** del codificador, que es donde está prohibida. Por eso el
chequeo existe aunque hoy no pueda concluir.

#### Los empalmes: cero conectores

[Decisión de ACSAR, 2026-09-21] Todos los tramos van por **fusión**, declarado
una sola vez en `integracion.fibra.empalme` en vez de repetido en los siete
tramos. Tres motivos, y los tres son del enlace: un conector es una entrada para
luz de Troya y un punto de retrorreflexión; un conector PM tiene una tolerancia
angular de alineación de ejes que un empalme no tiene, y cada grado es diafonía;
y un conector se puede mover con la vibración, y lo que se mueve en polarización
no vuelve solo a su sitio. **Lo que cuesta**: la cadena deja de ser desmontable
pieza a pieza.

#### Los `id_drive` nuevos

Sólo dos, y hay que **dar de alta esas filas** en la hoja índice del equipo:
**OPT-19** (`espejo_plegado_cuantico`) y **OPT-04-ALT** (`atenuador_fijo`, la
alternativa excluyente al VOA, que no suma en ningún presupuesto ni se coloca).

El `fotodiodo_vigia_troya` **no** es una pieza del catálogo: va dentro de la
reserva del acoplador y se dice en su `fuente`. Y la `lamina_cuarto_onda_fija`
tampoco, a propósito: lo que está en duda es **si la pieza existe**, así que
entra como TBD de decisión en `integracion.optica`, no como componente. Un
componente que quizá no esté en el camino o no tiene conexiones declaradas —y
entonces es una pieza suelta, que es lo que `test_brazo_beacon.py` existe para
cazar— o las tiene, y el modelo afirma un camino óptico que nadie ha decidido.
Si se decide instalarla, se da de alta con su `id_drive`, su envolvente y sus
dos tramos.

### Cómo se regenera

`data/layout.yaml` **no se edita a mano**. Todas las coordenadas salen del
catálogo:

```bash
uv run python tools/generar_layout.py
```

Las únicas decisiones de reparto están en la cabecera de ese script: ancho de la
columna de plataforma, longitud del banco y orden de la pila. La longitud del
telescopio **no** está ahí: es `longitud_reservada` en el catálogo. El ancho de
la franja tampoco: se deriva de la altura interior.

## 4. Hallazgos que contradicen el brief de partida

Los dos salieron de leer las fichas originales. Los dos están registrados en el
catálogo con las dos cifras.

### 4.1 Los moduladores Exail de grado espacial son más grandes

El brief da **85 × 15 × 9.65 mm** para el MXER-LN-10. Esa es la cifra del
**"Housing #A" de la serie comercial** MPX/MPZ. El encapsulado de **grado
espacial** (EM/NS-FM/FM), que es el que vuela, mide según el plano
`03_2026_ED2 / 00025851-B` p.9:

| | mm |
|---|---|
| Cuerpo | 100 |
| Con bridas | **110** ±0.2 |
| Con protectores de fibra | **(130)** |
| Ancho | 15 ±0.2 |
| Alto | 9.7 ±0.2 |
| Altura del eje de fibra | 4.8 |
| Conector RF lateral | 6.1 ancho × 10 alto |

**45 mm más de longitud por modulador** que lo que decía el brief, y son dos.
Esto es lo que fija la orientación de la bandeja óptica.

Exail **no publica** ficha de grado espacial del **MPZ-LN-10** (modulador de
fase). Como referencia se usa el encapsulado de grado espacial del
**NIR-MPX-LN-0.1** (plano `03_2026_ED3 / 00025631-B` p.9), que es idéntico.
**Confirmar con Exail antes de cerrar la bandeja.**

### 4.2 La apertura de 90 mm está en el límite físico del 6U

El 6U mide **100 mm** en Y, y es su dimensión pequeña. Con el espesor supuesto la
altura interior es **95.4 mm**, así que una apertura libre de 90 mm deja
**2.7 mm por lado**. Sin sitio para barrilete, celda de espejo ni ajuste.

Y no se arregla girando el telescopio: si el eje óptico va según Y, la longitud
del tubo (~2U, o sea ~227 mm con la U de longitud de la CDS) tiene que caber en
90 mm, que es peor. En cualquier otra
orientación la sección transversal sigue limitada por Y.

La lectura honesta: **una apertura de 90 mm en un 6U solo funciona si el
barrilete del telescopio es él mismo el elemento estructural de esa cara**, con
el chasis abriéndose a su alrededor en vez de rodearlo. Eso es una decisión de
estructura, no de óptica. **Lo que hace falta para cerrarlo es el diámetro
exterior del barrilete de Aperture Optical Sciences**, no la apertura libre.

Si el diámetro exterior supera los ~96 mm, las salidas son: bajar la apertura,
pasar a un diseño fuera de eje, o aceptar que el telescopio sea estructura.

### 4.3 El iADCS400 aprieta más que el contorno PC104

El contorno PC/104 desnudo son 95.89 × 90.17 mm, y con el lado corto por Y
permitiría paredes de hasta 4.91 mm. Pero el **iADCS400 mide 95.4 × 95.9 mm** de
contorno: su envolvente se sale de la tarjeta. Como es una tarjeta apilada, su
altura (67.3 mm) va obligatoriamente por el eje de la pila y **no se puede
tumbar**, así que su lado corto de 95.4 mm tiene que caber en los 100 mm
exteriores. De ahí sale el espesor máximo de **2.30 mm**, menos de la mitad.

El chequeo `seccion_componentes` recalcula esta cota desde el catálogo y dice qué
componente la fija, así que al añadir una pieza nueva más grande la cota baja
sola en vez de quedarse obsoleta.

**Y por eso mismo ese chequeo sale como `no comprobable`, no como correcto.** El
espesor de trabajo (2.30 mm) *es* la cota que fija el iADCS400, así que el
iADCS400 «cabe» con 0.00 mm de holgura. Eso no valida nada: es la hipótesis
devuelta tal cual. El chequeo lo detecta solo, comparando el espesor supuesto con
el máximo compatible (`margen_de_espesor_mm`), y por debajo de
`fit.HOLGURA_NULA_MM` = 0.5 mm se declara no concluyente.

Hay un segundo motivo, más de fondo: **el chasis 6U real es un armazón con
raíles, no una caja de paredes de espesor uniforme.** El hueco útil no es un
prisma; cambia con Z y con la cara. El modelo de paredes es una cota inferior
conservadora que sirve para no engañarse, no una zona útil. Queda pendiente
sustituirlo por el STEP del chasis del equipo y recalcular con él los dos
chequeos de sección (`seccion_componentes` y `contorno_pc104`).

### 4.4 Otras discrepancias registradas

- **iADCS400, potencia de pico**: 4 W (web AAC) frente a 5 W (satsearch).
- **PHOTON, potencia por cara de 3U**: 9 W (ficha, "up to 9W") frente a 9.25 W
  (brief).
- **PLAT-05 y PLAT-06 en la hoja de Drive están cambiados.** La hoja etiqueta
  PLAT-05 como "Batería Starbuck-Nano-PLUS" y PLAT-06 como "EPS Optimus-30". Es
  al revés: el Starbuck-Nano-PLUS es el EPS y el Optimus-30 es la batería. En
  el catálogo el `id_drive` se asigna **por producto**, no por la etiqueta, y
  los dos componentes llevan una nota diciéndolo. Corregir los nombres en la
  hoja.
- **Láser DFB**: el contorno que se usa es el del encapsulado butterfly de 14
  pines estándar (37.4 × 12.7 × 7.8 mm sin pines, 43.3 mm de ancho con ellos),
  no un plano de Gooch & Housego, que no publica ninguno. Y no incluye el
  disipador, que con 4.1 W no es opcional.
- **FSM**: se modela la opción MEMS porque es la que tiene cota publicada clara
  (encapsulado DIP24 de Mirrorcle, 30.5 × 15.1 × 2.16 mm). **Eso no es
  elegirla.** La opción piezo está en el catálogo como `fsm_piezo_pi_s331`,
  marcada `alternativa_de` para que no sume en nada, con lo que PI sí publica:
  **130 g** de masa (280 g en la variante de 5 mrad), −20 a +80 °C y espejo de
  12.7 × 3 mm. Esos 130 g frente a los gramos de un MEMS son el argumento
  fuerte a favor del MEMS, y ahora están en el catálogo en vez de en la cabeza
  de alguien.

### 4.5 La entrega del equipo trae otro ADCS y otras alturas de tarjeta

Del zip `Preliminar_viability_model.zip` (2026-09-20). Detalle en §9.

- **El ADCS del modelo preliminar es un iADCS4-20, no el iADCS400 del brief.**
  El STEP declara `IADCS420-ASM-ST-1.0-defeatured`. Medido: 95.40 × 93.90 ×
  74.10 mm frente a los 95.4 × 95.9 × 67.3 del 400. AAC **no publica ficha** del
  4-20: el STEP es la única fuente que hay. Está en el catálogo como
  `adcs_iadcs420`, marcado `alternativa_de: adcs_iadcs400`, así que **no suma en
  ningún presupuesto** — habría dos ADCS a bordo.
- **Los 2 mm de menos en Y importan.** El iADCS400 es lo que fija el espesor de
  pared máximo en 2.30 mm (§4.3). Con el 4-20, esa cota pasaría a
  (100.0 − 93.9) / 2 = **3.05 mm** y la zona útil crecería. Mientras el 4-20 sea
  una alternativa en estudio, la cota de trabajo sigue siendo la del 400.
  Los 6.8 mm de más de altura no cuestan nada en la pila:
  `ceil(74.1 / 15.24) = 5` posiciones, las mismas que con 67.3.
- **Las dos tarjetas AAC del zip son más altas que su ficha.** Con el conector
  PC104 pasante (104 pines de 0.64 × 0.64 × 12.45 mm) y sin él:

  | | ficha | STEP sin pines | STEP entero |
  |---|---|---|---|
  | Kryten-M3-PLUS (`3D-25-02929 RevJ`) | 5.51 mm | **16.20** | **23.24** |
  | Optimus-30 (`3D-01-02686 RevA`) | 21.55 mm | **27.35** | **36.44** |

  Las tres cifras están registradas en `alternativas`. La de ficha mide «from
  top PCB to lowest component» (§5) y no incluye el cuerpo de los conectores.
  **Ninguno de los dos part numbers está verificado** como Kryten ni como
  Optimus: por eso los dos STEP van conectados con estado `referencia`.
  Tampoco son dos baterías: el fichero se llamaba «Batteries» en plural, pero
  por dentro es **un solo módulo** con 8 celdas de 35.56 × 57.81 × 5 mm en
  cuatro capas.
- **Lo que no cambia.** Con la geometría real, `data/layout.yaml` sale idéntico
  y siguen sin aparecer interferencias ni desbordes. El par de baterías es el
  caso interesante: sus cajas envolventes solapan **51.6 cm³** por los pines
  pasantes, o sea que el prefiltro las manda a la booleana, y la booleana
  devuelve **0**. Los pines de una pasan limpios por al lado de la otra, que es
  como debe funcionar una pila PC104. Lo que sí baja es el volumen libre: de
  6.25 L a 5.84 L, porque lo que ocupan las tarjetas ya no es su caja de
  ficha. (Hoy el volumen libre es **2.88 L**: lo que cambió no es el modelo de
  las tarjetas, es que ya se dibujan los 19 componentes del payload que antes
  no ocupaban nada. Ver §1.)

### 4.6 La pila PC104 mide 305 mm, no 259

Apareció al dibujar PCB-2: un solape de 2.91 cm³ con los pines pasantes del
Optimus-30. La causa no era la PCB.

**El generador reservaba cada ranura con la altura de FICHA y dibujaba con el
STEP.** Las fichas de AAC miden "from top PCB to lowest component" y no incluyen
el conector PC104 pasante, que baja 12.45 mm por debajo de la tarjeta; el STEP
sí lo trae. Mientras la tarjeta vecina era un hueco TBD, los pines no chocaban
con nada y §4.5 lo daba por bueno. **En cuanto la vecina se dibuja, deja de
serlo.**

Un pin que atraviesa el *conector* de la tarjeta vecina es correcto en una pila
PC104 de verdad. Un pin que atraviesa el *bloque macizo* con el que se modela
una tarjeta cuya altura no se conoce, no. Y como no hay manera de distinguir una
cosa de otra sin conocer las tarjetas propias, se reserva por lo dibujado, que
es conservador y cierto:

| | ficha | dibujado | posiciones antes | ahora |
|---|---|---|---|---|
| Kryten-M3-PLUS | 5.51 mm | 23.24 mm | 1 | **2** |
| Optimus-30 (×2) | 21.55 mm | 36.44 mm | 2 | **3** |

**259 mm → 305 mm de los 361 disponibles.** Sigue cabiendo, con 56 mm de margen
en vez de 102. El chequeo `pila_pc104` usa ahora la misma altura que el
generador, así que los dos números vuelven a hablar de lo mismo.

Esto refuerza el punto 4 de §6: **el paso de apilamiento real del chasis** es
todavía más importante de lo que parecía, porque el margen se ha reducido a la
mitad.

### 4.7 El telescopio deja de ser un cilindro de reserva

Hasta ahora `telescopio_cassegrain` era un cilindro de 95.4 × 95.4 × 200 mm en
estado `supuesto`: un hueco con forma. Ahora es un **modelo paramétrico**
—barrilete, primario, secundario, araña, baffles, celda isostática, brida al
FSM y el camino del haz— construido en `src/clau3d/optica/` a partir de un
bloque `optica` nuevo en el catálogo.

**Lo que no cambia, y es lo importante.** Sigue siendo `supuesto`: gris,
transparente, sin sumar en masa y entero en `reports/06_pendientes.md`, ahora
con 33 filas en vez de una. Sigue siendo el **fallback**: el día que aparezca
`cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step`, lo sustituye
sin tocar el catálogo, exactamente igual que sustituía al cilindro. Y sigue
reservando lo mismo: **el volumen libre y las interferencias no se han movido**
(0 choques, y las invasiones de keep-out siguen siendo sólo del radio de
curvatura de la fibra). Ver más abajo
por qué eso no es casualidad.

#### (a) La sección pasa a ser cuadrada

Un barrilete de **revolución** de Ø95.4 con 90 mm de apertura deja 2.7 mm por
lado, y ahí no caben celda, flexures ni tornillería. Con **sección cuadrada** de
95.4 mm los dos números son distintos y el segundo es el que sirve:

| | mm radiales |
|---|---|
| hasta la cara plana | **2.70** |
| hasta la esquina (semidiagonal 67.46) | **22.46** |

El modelo reparte en consecuencia: en la cara plana solo caben la pared
(1.5 mm), el baffle (0.6 mm) y su holgura (0.5 mm) —es decir, los diafragmas
knife-edge pueden proyectar hacia dentro **medio milímetro y ni uno más**—, y la
carga la llevan cuatro **largueros de esquina**, con la celda del primario
orientada para que el primero de sus tres flexures caiga también en una esquina
(`angulo_primer_flexure` = 45°).

Además es lo único coherente con lo que ya decía §4.2: si el telescopio acaba
siendo el elemento estructural de esa cara, hacen falta caras planas y bridas,
no un tubo redondo.

`chequeo_apertura_telescopio` informa ahora de **los dos márgenes**, no solo del
radial, que daba una imagen más pesimista de la que corresponde.

#### (b) Afocal (Mersenne), no focal

Dos parábolas confocales, primario cóncavo y secundario convexo: entra colimado
y sale colimado. El motivo no es óptico, es **el banco**. Un Cassegrain focal
clásico (f/12, EFL 1080 mm) deja el foco real ~40 mm detrás del vértice del
primario, o sea **dentro de `z_payload_banco`**, y obliga a meter una lente de
enfoque en la línea apretada de §3.7 (15.7 mm de margen desde que el colimador
salió de ella, y eran 7.7). El afocal no
necesita ningún elemento adicional, y en particular **ninguna superficie
transmisiva en el camino del canal cuántico**, donde un refractivo mete
birrefringencia por tensión y se come justo lo que el enlace mide.

Por lo mismo se descarta la **placa correctora** que sostendría el secundario sin
araña: es un refractivo en ese camino. Queda escrito en el catálogo como
alternativa descartada con su motivo.

El foco común de las dos cónicas en el afocal es **virtual**, así que el modelo
**no dibuja ningún marcador** ahí: no hay nada. Si alguien pone
`optica.configuracion: focal_clasico`, el modelo sí dibuja el foco real y
`chequeo_configuracion_telescopio` avisa de dónde cae.

#### (c) El diámetro de haz acopla telescopio, FSM y banco

`diametro_haz_mm` era un TBD más en `e01`–`e03`. Resulta ser **el parámetro que
lo decide todo**, porque de él sale la magnificación y de la magnificación sale
la geometría entera:

```
M  = apertura_libre / diametro_haz_comprimido        f2 = f1 / M
d  = f1 − |f2|   (confocalidad)                      D2 = haz × margen
ε  = D2 / apertura_libre
potencia recogida   = 1 − ε²      →  −10·log₁₀(1 − ε²)
intensidad en eje   = (1 − ε²)²   →  −20·log₁₀(1 − ε²)
```

Ninguno de esos números está escrito en el catálogo: se derivan en
`optica/parametros.py`, y hay un test que comprueba que cambiar el haz los mueve
todos. Con lo que hay hoy (apertura 90, haz supuesto 10): **M = 9.00**,
f2 = 22.22 mm, d = 177.78 mm, secundario Ø14, ε = 0.156, **0.11 dB de potencia
recogida y 0.21 dB de intensidad en el eje**.

**Corregido el 2026-09-20 por la noche.** Hasta entonces el código comentaba
el −20·log₁₀ como «convenio de amplitud» y decía que en potencia la misma
obstrucción costaba la mitad de dB. Es falso. No son dos convenios de la misma
magnitud: son **dos magnitudes distintas y las dos son de potencia**. La
fracción de potencia recogida es (1 − ε²), porque la obstrucción tapa ε² del
área; la intensidad en eje en campo lejano es (1 − ε²)², porque la obstrucción
además **redistribuye energía del lóbulo principal a los anillos**. Para un
enlace óptico manda la segunda: lo que llega al receptor es la intensidad en el
eje, no la potencia total que sale del telescopio. Las dos se derivan y se
publican por separado (`perdida_potencia_recogida_dB` y
`perdida_intensidad_en_eje_dB`), y cuál manda está declarado en el catálogo como
`integracion.optica.perdida_obstruccion_convenio` —sólo cuál, no los números,
que se derivan de ε—.

Y aquí está el acoplamiento: **un haz de d mm sobre un espejo a 45° deja una
huella de d × d·√2**, así que un espejo circular de D mm solo admite
D·cos 45° = D/√2.

| espejo del FSM | haz máximo | M mínima |
|---|---|---|
| **5 mm** (MEMS Mirrorcle, herencia CLICK-A) | **3.54 mm** | **25.5** |
| 12.7 mm (espejo del piezo PI S-331) | 8.98 mm | 10.0 |

Con el haz supuesto de 10 mm con el que hoy se dibuja todo, **el MEMS DIP24 no
vale**: haría falta el `fsm_piezo_pi_s331` —que pesa 130 g frente a los gramos
del MEMS— o subir la magnificación de 9 a 25.5, lo que encoge el secundario y
alarga el tubo. `chequeo_haz_vs_fsm` dice exactamente eso, y sale **`no
comprobable`**, no `ok` ni `falla`: el número con el que se dibuja no valida
nada. **Este es el dato que decide el TBD `fsm.eleccion_de_tecnologia`**, y así
está redactado en el informe.

El **punto de adelanto** no es el problema: un afocal comprime los ángulos por M,
así que los ~51 µrad del cielo son 456 µrad ópticos en el haz comprimido
(228 µrad de giro mecánico del espejo) con M = 9. El piezo da 3 mrad y un MEMS
mucho más. Lo que decide es el **tamaño** del espejo, no su recorrido.

#### (d) La longitud: cabe por 1.2 mm, y eso no es margen

La separación entre vértices de un afocal es `f1·(1 − 1/M)` y no se negocia.
Con f1 = 200 mm y M = 9 son **177.8 mm**, así que de los 200 mm que el layout
reserva quedan **22.2 mm** para los dos mamparos, la celda y los dos espejos:

| | mm |
|---|---|
| mamparos (2 × 3.0) | 6.0 |
| celda del primario | 3.0 |
| espejo primario | 8.0 |
| espejo secundario | 4.0 |
| **margen** | **1.2** |

Todos esos espesores están en su **cota superior**, no elegidos, y su `fuente` en
el catálogo lo dice —el mismo patrón que el espejo de plegado y D1 de §3.7—.
Una celda de 3 mm no es una celda, y un primario de Ø92 × 8 mm tiene una relación
de aspecto de 11.5. `chequeo_longitud_telescopio` sale como **atención** y dice
la salida: con los **~2U de verdad del brief (227 mm, no 200)** la misma óptica
tendría ~28 mm de margen. **Alargar se paga con la bandeja y es decisión de
ACSAR**, así que aquí no se ha tocado `longitud_reservada`.

#### Por qué el volumen y las interferencias no se mueven

Porque el modelo detallado **es hueco**, y meterlo tal cual en el análisis diría
que dentro del tubo cabe algo. No cabe: ahí va el haz. Así que una pieza expone
ahora **dos sólidos**, y quien pide uno dice cuál quiere:

- `parts.solido()` — el detalle. Visor y export STEP.
- `parts.solido_envolvente()` — el prisma macizo. **Volumen e interferencias.**

Para todo lo demás son el mismo objeto. Y el constructor **comprueba que el
detalle no se sale del prisma declarado**: si la óptica derivada pidiera más
tubo, aborta con el número que falta en vez de dibujar una pieza que se sale, que
es lo mismo que hace el generador con una fila de bandeja que no cabe.

El camino del haz dentro del barrilete va como **keep-out**, no como cuerpo:
dos tramos con su diámetro real —`haz_telescopio_colimado` (Ø90, de la apertura
al primario) y `haz_telescopio_comprimido` (Ø10, del secundario a la brida del
FSM)—. Llevan un campo nuevo, `de_pieza`, porque caen enteros dentro de la
envolvente del propio telescopio: sin él el modelo diría que el telescopio invade
su propio haz.

#### Lo que sigue siendo inventado, y quién tiene el dato

- **Aperture Optical Sciences / Óscar** — el STEP, y con él la focal real, las
  cónicas, el contorno del barrilete, los espesores de los espejos, la celda y la
  interfaz al banco. Es la mitad de las 33 filas nuevas.
- **Equipo de óptica de ACSAR** — el **diámetro de haz comprimido** (el que más
  desbloquea, §6.8), el **ángulo de exclusión solar** (con el que los dos baffles
  dejan de dibujarse con una regla de primer orden), la holgura del baffle y el
  número y posición reales de los diafragmas.
- **Equipo de óptica de ACSAR** — la **estabilidad de despace primario–secundario**,
  que es TBD y es **el requisito que dimensiona el tubo y la araña**: la
  sensibilidad a desenfoque escala con m²(1+m), así que unas micras de deriva
  térmica agotan el presupuesto de frente de onda. Hoy el barrilete y los vanes
  se dibujan con espesores supuestos, no con una rigidez calculada.
- **Equipo de estructura de ACSAR** — la sección de los largueros de esquina y el
  espesor de pared, que salen de ese mismo análisis de rigidez.
- **Equipo de PAT / de misión** — el punto de adelanto real, que aquí se ha
  calculado como 2v/c con v = 7.6 km/s.

---

## 5. Avisos sobre los datos

- **Las alturas de las fichas AAC no son el paso de apilamiento.** Dicen "height
  from top PCB to lowest component". El Kryten-M3 mide 5.51 mm y eso **no**
  significa que dos tarjetas queden a 5.51 mm.
- **El 6U exterior son 8.28 L, no 6 L.** 226.3 × 100 × 366. El "6U" cuenta
  unidades de volumen útil, no la envolvente.
- **La ficha del Kryten-M3 cubre la familia**; el sufijo PLUS añade GNSS. Se ha
  supuesto que la SWaP es la misma. Además la propia ficha se contradice: el
  texto dice 8 MB de MRAM y la tabla 16 MB.
- **Starbuck-Nano-PLUS está descrito para plataformas con paneles desplegables**,
  y CLAU parte de PHOTON-SIDE de montaje en cuerpo. La variante coherente sería
  el NANO. Pendiente con AAC.
- **La masa del iADCS400 es un rango** (1150–1700 g) y por eso está como TBD: no
  se elige un punto del rango.

---

## 6. Qué haría falta a continuación

0. **PEDIR A ÓSCAR LOS STEP DE LOS 5 FICHEROS SOLIDWORKS.** Es lo más barato
   de resolver y lo que más desbloquea. La entrega del 2026-09-20 trae en
   formato nativo SolidWorks, que **no hay manera de leer**, justo las dos
   piezas que más bloquean: `Chasis.SLDPRT` + `Chasis_base.SLDPRT` (punto 7 de
   esta lista, y la razón de que los dos chequeos de sección salgan como no
   comprobables) y `Telescopio_concepto.SLDPRT` (el diámetro y la longitud del
   punto 4). Más `Power_control_and_distribution_unit.SLDPRT`, que ni siquiera
   se sabe a qué componente corresponde, `1U_propulsion_module.sldprt` y
   `Ensamblaje_preliminar.SLDASM`, con el que se podría comparar la
   distribución del equipo con la de `data/layout.yaml`. **Formato: STEP AP214
   o AP242.** Huellas y detalle en `cad/vendor/MANIFEST.yaml`, sección
   `sin_convertir`.
1. **Confirmar qué ADCS lleva CLAU**, iADCS400 o iADCS4-20 (§4.5), y por qué el
   modelo preliminar trae el 4-20 cuando el brief cita el 400. Ahora mismo hay
   dos componentes en el catálogo para un solo hueco de la pila.
2. **Verificar los part numbers `3D-25-02929` y `3D-01-02686`** con AAC: si son
   el Kryten-M3-PLUS y el Optimus-30, sus STEP pasan de `referencia` a
   `confirmado` y las alturas de ficha dejan de contradecir la geometría.
3. **Validar el riesgo térmico de §3.6** con el equipo térmico: los moduladores
   acoplados al barrilete del telescopio. No bloquea el layout, pero puede
   obligar a devolverlos a la bandeja, y entonces el telescopio vuelve a tener
   techo de 176.4 mm.
4. **EL RADIO MÍNIMO DE CURVATURA DE LA FIBRA** (equipo de payload). Sigue
   siendo el dato que más desbloquea. De las **7** invasiones de keep-out que
   reporta el modelo —eran 15 antes de §3.10— **las 7** salen de él: 5 en la
   bandeja y 2 en la franja. Mientras no exista, la bandeja no se puede validar
   (§3.7.2). Con él, el chequeo `bucles_fibra` pasa de `no comprobable` a decir
   algo, y los keep-outs pasan de `supuesto` a `confirmado` sin tocar una línea
   de código. Lo que **ya no** depende de él es el encaminamiento del colimador:
   §3.7.1 está resuelto.
5. **Los otros dos datos que bloquean mucho**:
   - **STEP del telescopio** (Óscar / Aperture Optical Sciences): contorno
     exterior del barrilete **y longitud real**. Hay sitio reservado para él en
     `cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step`: dejarlo
     ahí basta para que sustituya al modelo paramétrico (§4.7). Ojo: los «~2U»
     del brief son ~227 mm, no 200 (la U de longitud de la CDS son 113.5 mm), y
     con 200 mm la óptica derivada cabe por **1.2 mm**.
   - **Paso de apilamiento real del chasis** (equipo de estructura). Ahora se usa
     el estándar PC/104; el real puede cambiar los **305 mm** de pila, y el
     margen ya solo es de 56 mm (§4.6).
6. **Alturas reales de PCB-1, PCB-2 y PCB-3.** Ahora se dibujan con 15 mm
   supuestos. Si alguna pasa de 15.24 mm ocupará dos posiciones de separador y
   la pila crecerá 15.24 mm por cada una.
7. **Decidir dónde va la antena de banda S** (§3.8), que es una decisión de
   operaciones: si el canal clásico puede no ser simultáneo al pase óptico,
   −Z vale; si no, hay que buscarle cara y no la hay.
8. **EL DIÁMETRO DEL HAZ COMPRIMIDO** (equipo de óptica). Ha dejado de ser «un
   keep-out mejor dibujado» y es, después del radio de curvatura de la fibra, lo
   que más desbloquea: de él salen la magnificación del telescopio y con ella su
   geometría entera, **y decide el punto 12** (si el MEMS de 5 mm vale o hay que
   irse al piezo). Ver §4.7(c). Con él, `chequeo_haz_vs_fsm` pasa de `no
   comprobable` a decir algo. Hacen falta además el **ángulo de exclusión
   solar**, con el que los dos baffles del telescopio dejan de dibujarse con una
   regla de primer orden, y el semiángulo del cono de la apertura, que hoy no se
   dibuja en absoluto.

8.b **La estabilidad de despace primario–secundario** (equipo de óptica). Es el
   requisito que dimensiona el tubo métrico y la araña —la sensibilidad a
   desenfoque escala con m²(1+m)— y hoy no existe, así que el barrilete se dibuja
   con espesores supuestos y no con una rigidez calculada (§4.7d).
9. **El diámetro y el radio de curvatura del coaxial RF** (equipo de
   electrónica), que es lo que falta de ELEC-04.
10. **Sustituir el chasis genérico por el STEP del equipo**, con lo que
    desaparece la hipótesis de espesor de pared y la zona útil pasa a ser real.
11. **Cerrar el encaminamiento de los 4.1 W del láser**: directo del bus del EPS
    o a través de PCB-2. Y el disipador del láser, que no está modelado.
12. **Elegir FSM**: MEMS o piezo (§4.4). El modelo enseña las tres cifras que
    deciden. Dos son de la pieza —la masa y el volumen del soporte— y ninguna
    está cerrada: del MEMS falta el soporte de vuelo, del piezo faltan las
    cotas. La tercera **no es del FSM**: es el diámetro del haz (punto 8). Con el
    espejo de 5 mm del MEMS el haz máximo son 3.54 mm; si el equipo de óptica
    pide más, el MEMS queda descartado sin discusión (§4.7c).
13. **DECIDIR CÓMO CABE EL BRAZO DE LOS BEACONS** (§3.9). Es la única cosa de
    esta lista que hoy hace **fallar** `clau3d informe`, y la única pieza del
    modelo que no está colocada porque no tiene dónde. Faltan 6.8 mm con las
    envolventes desnudas y 16.8 mm con holguras, y las dos salidas cuestan:
    plegar el brazo hacia −Z con un espejo de doblado (una superficie
    reflectante más en el camino del beacon) o alargar el banco a costa de la
    bandeja o del telescopio. **Es una decisión de ACSAR**, no del modelo.
14. **EL AISLAMIENTO DE LA CÁMARA A 1064 nm** (equipo de PAT). Es el número que
    sostiene toda la elección de longitudes de onda de §3.9 —976 arriba, 1064
    abajo— y hoy no está medido. Lo que decide es si un sensor que mide
    microvatios puede convivir en el mismo brazo con 100 mW del beacon propio.
15. **Confirmar la potencia del beacon de bajada** (100 mW son un supuesto) y
    **si el cuarto puerto de D2 se instrumenta** con el fotodiodo o se tapa con
    `trampa_luz_d2`. Lo segundo no cambia la geometría del brazo; lo primero sí
    cambia el disipador del láser, que es lo que fija su envolvente.

16. **DECIDIR CÓMO CABE EL TRAMO RECTO POST-CODIFICACIÓN** (§3.10). Es la
    segunda cosa que hoy hace **fallar** `clau3d informe`, y por la que
    `mod_fase_mpz_ln_10` no está colocado. Faltan **18.0 mm** de los 218 que
    piden en fila el colimador, el protector del empalme y el codificador. Las
    tres salidas están calculadas en §3.10 y las tres son de ACSAR: subir la
    longitud reservada al telescopio a ≥ 218 mm (con los 227 del brief sobran
    9.0), conseguir de Exail un codificador con salida colimada (sobran 42.0) o
    alargar el banco a ≥ 86 mm (sobran 10.0). Ojo: **alargar el banco a secas no
    sirve** si no llega a 86, porque la cuenta es de la franja, no del banco.
17. **SI LA GUÍA DEL MPZ-LN-10 ES BIPOLARIZACIÓN** (Exail). Es el TBD que más
    riesgo esconde de todos los nuevos: las guías de intercambio protónico
    guían una sola polarización y actúan como polarizador integrado, y con una
    de ésas el esquema de codificación con **un solo modulador de fase es
    imposible**, no peor. Si la respuesta es que no, la arquitectura del
    transmisor cambia entera.
18. **LA SENSIBILIDAD TÉRMICA DE LA FASE EN FIBRA PM** (equipo de payload,
    medida). Es lo que fija cuánta fibra post-codificación es tolerable.
    Mientras falte, `fibra_post_codificacion` no puede decir si la longitud del
    tramo sirve, sólo si cabe.
19. **LA RETARDANCIA s–p DEL ESPEJO DE PLEGADO A 45° Y 1550 nm, CON LA CURVA DE
    FASE MEDIDA** (equipo de óptica). Lo que se pide es **estabilidad**, no
    valor: el efecto es unitario y estático y la estación lo calibra, siempre
    que no derive. Hay que exigirla al fabricante porque casi ningún catálogo
    la publica (§3.10).
20. **QUÉ PAR DE BASES USA EL ENLACE** (equipo de óptica / de estación de
    tierra): D/A + R/L sin lámina, o H/V + D/A con una λ/4 fija después del
    codificador. Los dos pares valen para BB84, así que no es física del
    protocolo: es **compatibilidad con la estación**. Está como TBD en
    `integracion.optica.lamina_cuarto_onda_fija` y no como componente, porque
    lo que está en duda es si la pieza existe.
21. **SI LA EXTINCIÓN DEL MXER BASTA PARA EL ESTADO VACÍO** (Exail / payload).
    Si hacen falta dos en cascada, el tercer modulador **no cabe en la franja**:
    faltan 23.6 mm de Y, y el cálculo está escrito en el catálogo.
22. **EL MOMENTO DIPOLAR MAGNÉTICO DEL AISLADOR** (payload / ADCS). Lleva imán
    permanente —rotador de Faraday—, así que no es un componente pasivo para el
    magnetómetro del ADCS. Y de paso: **comprobar si el butterfly del G&H ya
    integra aislador interno**, que quitaría la pieza y el imán.

> **La lista de supuestos a sustituir, entera y con el valor concreto de cada
> uno, está en `reports/06_pendientes.md` y en `reports/components_status.csv`.**
> No hace falta mantenerla a mano aquí: se regenera con `clau3d informe`.

## 7. Notas de implementación

- **Python 3.12**, no 3.14: CadQuery/OCP no tiene ruedas para 3.14 todavía.
- **Las formas aproximadas no son una sola cosa.** `forma.tipo` admite `caja`
  y `cilindro` —media cadena óptica es cilíndrica, y dibujar un cilindro como
  caja infla su volumen un 27 % sin que nadie lo vea— y cualquiera de las dos
  puede llevar `conectores`, que se pegan a una cara declarada y **agrandan la
  caja envolvente**. Eso último es lo importante: el conector RF del modulador
  sobresale 10 mm y el detector de interferencias tiene que verlo. Un conector
  sin cotas no se dibuja de ningún tamaño y sale como pendiente.
  Y admite `cassegrain`, que no es una envolvente sino un **modelo paramétrico**
  entero (§4.7): exige su bloque `optica` completo igual que un cilindro exige
  su `eje`, y es la única forma que distingue entre el sólido que se **dibuja**
  y el que se **analiza**, porque es hueca por dentro.
- **`montaje` no es geometría.** Declara con qué cara se atornilla la pieza y
  por qué eje entra la señal. De ahí saca el generador la rotación de cada
  colocación, en vez de escribirla a mano: una pieza que cambie de cara de
  montaje se recoloca sola, y el STEP que llegue mañana se orienta por la misma
  regla que el aproximado al que sustituye.
- **El generador mide girando el sólido, no permutando cotas.** Permutar valdría
  mientras todos los giros fueran múltiplos de 90°, y el FSM va a 45° para
  doblar el haz. Una caja a 45° ocupa más que la misma caja recta, y ese «más»
  es justo lo que decide si el banco da de sí (§3.7).
- **Una fila de la bandeja que no quepa aborta el generador.** No se aprieta:
  la primera versión metía tres cilindros de 110 mm en 109.7 y salían solapes de
  décimas de milímetro que el informe marcaba sin que se entendiera por qué.
- **CadQuery 2.8**. `Assembly.save()` está obsoleto; se usa `Assembly.export()`.
- Las interferencias se filtran primero por caja envolvente y solo entonces se
  hace la booleana de OCC, que es cara.
- El mapa de hueco libre es una rejilla de ocupación proyectada sobre el plano
  X-Z. Paso de 10 mm por defecto.
- `clau3d informe` devuelve código de salida **1** si hay chequeos críticos o
  interferencias, para poder engancharlo a CI.
- **Importar un STEP grande es carísimo.** El del iADCS4-20 tarda ~161 s. Se
  cachea en BREP bajo `.cache/step/`, con la clave hecha de ruta + tamaño +
  mtime, y a partir de ahí se lee en menos de un segundo. La caché se rehace
  sola y no se versiona.
- **La geometría real cuesta minutos, no segundos.** Con tres piezas de STEP el
  ensamblaje pasa de 8 sólidos a ~550, y `clau3d todo` se va a **~5 min**:
  ~57 s de booleanas de interferencia y el resto en las vistas SVG y los
  exportes, que proyectan todos los sólidos. Conviene saberlo antes de
  encadenarlo a CI. El importe del STEP ya no es el problema: con la caché son
  0.7 s y 1.7 s.
- **`BoundingBox()` sobre un compound importado puede mentir.** El del
  iADCS4-20 devuelve coordenadas de ~10^97 mm: basta una entidad degenerada
  entre miles para envenenarlo, y sus 210 sólidos están perfectamente. Por eso
  `parts.caja_de_solidos()` la calcula **sólido a sólido** y lanza `ErrorDeDatos`
  por encima de `COORDENADA_ABSURDA_MM`. Si esa caja llegara al prefiltro de
  interferencias, todo solaparía con todo y el informe dejaría de significar
  nada. Es el mismo criterio de siempre: antes un error que un `ok` falso.

---

## 8. El visor web (`clau3d ver`)

Añadido el 2026-09-20. `uv run clau3d ver` exporta el ensamblaje a
`cad/generated/clau_6u.glb`, vuelca todo lo demás a `cad/generated/escena.json`
y sirve `src/clau3d/visor/` en `http://localhost:8000`.

**Por qué un visor propio y no uno de CadQuery.** Los visores genéricos enseñan
sólidos. Aquí lo que hay que ver no es solo la forma: es **de dónde sale cada
cota y qué falta**. El visor colorea por estado del dato, lista los
componentes sin envolvente con a quién pedírselos, marca el volumen libre como
*techo* mientras `resumen.fiable` sea falso y muestra los chequeos con el mismo
criterio que `reports/`. Un visor genérico no puede decir nada de eso.

Desde el 2026-09-20 por la tarde tiene además un panel de **«números
inventados aquí»**: los 68 supuestos, uno a uno, con qué falta y a quién
pedírselo. Es lo único que distingue en pantalla un cuerpo gris que está ahí
porque alguien lo midió de uno que está ahí porque alguien se lo inventó; la
geometría los enseña igual de sólidos a los dos.

**El reparto de responsabilidades.** El GLB lleva geometría, nombres y colores.
El JSON lleva todo lo que la geometría no sabe decir. El JavaScript **no calcula
ninguna cota**: solo formatea lo que viene en el JSON. Si hiciera falta un número
nuevo en pantalla, se añade a `viewer.escena()`, no al JS.

**Se regenera solo, y solo cuando hace falta.** El servidor compara la fecha de
`data/*.yaml`, de los STEP de `cad/vendor/` y del propio código con lo último
servido, y rehace GLB y JSON si algo cambió. Recargar el navegador basta; no
hace falta reiniciar. Al revés también: si nada ha cambiado, `clau3d ver`
**no regenera nada** y arranca al instante. Rehacer la escena cuesta **91 s**
—12 s de teselado y el resto de booleanas de interferencia— y pagarlo en cada
arranque no compraba nada. Y el GLB se sirve con `ETag`, así que una recarga
con la escena intacta responde **304** en vez de mandar 17 MB otra vez.

### Por qué el visor iba lento, y qué se hizo (2026-09-20)

El cuello no era three.js ni el `http.server`: era **cómo entrega la geometría
OpenCASCADE**. Escribe **una primitiva de glTF por cara del BREP**, que es lo
correcto en un traductor de CAD y lo peor posible en un visor. El ensamblaje
salía con **38 738 primitivas para 862 000 triángulos**, y GLTFLoader crea una
malla de three.js por primitiva: 38 738 llamadas de dibujo por fotograma. La
tarjeta gráfica se ríe de 862 000 triángulos; con 38 738 llamadas se atraganta.
Encima el índice de esas primitivas ocupaba **18 MB de JSON** dentro de un
fichero de 46 MB, y el visor construía una `EdgesGeometry` por cada una.

`src/clau3d/gltf.py` funde las primitivas de cada malla en una sola por
material, después de exportar. **No cambia ni un vértice**: son exactamente los
mismos triángulos, agrupados de otra manera, y `tests/test_gltf.py` lo comprueba
con geometría inventada. Aparte, el GLB se tesela a 0.2 mm / 0.3 rad en vez de
los 0.1 / 0.1 de CadQuery —son números de presentación, como los de la cámara;
el STEP sigue saliendo con la precisión por defecto— y el visor deja de dibujar
aristas por encima de `UMBRAL_ARISTAS`: en una caja translúcida son lo que la
hace legible, sobre un STEP de fabricante son una maraña que solo cuesta.

Medido con el `GLTFLoader` de verdad, sobre el mismo ensamblaje:

| | antes | después |
|---|---|---|
| GLB | 45.8 MB (18.2 MB de JSON) | **16.8 MB** (8.2 kB de JSON) |
| `GLTFLoader.parse` | 1670 ms | **48 ms** |
| mallas = llamadas de dibujo | 38 738 | **13** |
| aristas | 4711 ms, 38 732 objetos | **5 ms**, 10 objetos |
| triángulos | 861 906 | 418 310 |
| `clau3d ver` sin cambios | 91 s | **instantáneo** |
| recarga del navegador | 46 MB | **304, 0 B** |

Si algún día 418 000 triángulos volvieran a ser un problema —con el STEP del
chasis y el del telescopio dentro es posible—, lo siguiente sería comprimir con
Draco o meter un BVH para el `raycast`. Ninguna de las dos hace falta hoy.

### Dos trampas que ya costaron un rato

1. **El GLB sale con los ejes girados.** glTF es Y-arriba, así que OpenCASCADE
   rota el modelo al exportar: el Z del CAD acaba siendo el Y del fichero. El
   visor lo deshace con `gltf.scene.rotation.x = Math.PI / 2`. Sin eso, la
   geometría y las cajas de zona dibujadas desde el JSON **no coinciden**, y el
   fallo se ve como un desencaje sutil, no como un error.
2. **Los nombres de malla chocan con los de instancia.** OpenCASCADE partía cada
   sólido en varias mallas y GLTFLoader les ponía sufijo `_1`, `_2`… La segunda
   cara de `bateria_optimus_30` se llamaba igual que la segunda batería,
   `bateria_optimus_30_2`. Por eso el visor **no agrupa por el nombre de la
   malla** sino por el `Group` que las contiene, que lleva el nombre exacto del
   nodo del ensamblaje. `tests/test_visor.py` comprueba que cada nodo del JSON
   existe en el GLB, que es justo lo que se rompe al renombrar una colocación.

   Desde que el GLB se compacta ya no puede pasar: cada nodo trae una sola
   primitiva, y GLTFLoader devuelve un `Mesh` con el nombre exacto. El código de
   agrupación se queda igual porque sigue siendo correcto en los dos casos, y
   porque es lo que protege de que el choque vuelva si alguien exporta sin
   compactar.

---

## 9. El CAD de fabricante (`cad/vendor/`)

### Qué trajo la entrega del 2026-09-20

`Preliminar_viability_model.zip`, del equipo. Diez ficheros, de los que **solo
cuatro son STEP**:

| fichero original | qué es de verdad | dónde está ahora |
|---|---|---|
| `Attitude_determination_and_control_system.step` | `IADCS420-ASM-ST-1.0` — un **4-20**, no el 400 | `aac_clyde_space/iadcs420.step` |
| `Onboard_computer.STEP` | `3D-25-02929 RevJ` (AAC, SolidWorks 2021) | `aac_clyde_space/obc_3d_25_02929.step` |
| `Batteries.STEP` | `3D-01-02686 RevA` — **un** módulo, no dos | `aac_clyde_space/bateria_3d_01_02686.step` |
| `Modulo_optico_clasico_y_PAT_integrado.stp` | **`CubeCAT_IF_20230214`** | `descartados/` — ver abajo |
| `Chasis.SLDPRT`, `Chasis_base.SLDPRT`, `Telescopio_concepto.SLDPRT`, `Power_control_and_distribution_unit.SLDPRT`, `1U_propulsion_module.sldprt`, `Ensamblaje_preliminar.SLDASM` | formato nativo SolidWorks, **ilegible** | pendiente §6.0 |

Lo que las cotas dicen y lo que costó encajarlas está en §4.5.

### Por qué el CubeCAT está en `descartados/`

Es el terminal láser **CubeCAT de AAC Hyperion**: un cubo integrado de
97.6 × 102.6 × 97.6 mm que resuelve telescopio, banco y PAT de una pieza. Eso es
la **arquitectura anterior al 2026-09-19**, no el payload de CLAU, que separa el
Cassegrain de Aperture Optical Sciences, el banco óptico y la bandeja de fibra.

**No se conecta a ningún componente y no entra en el ensamblaje.** Se conserva
solo como registro de lo que se descartó, con su huella en el manifiesto, para
que dentro de seis meses nadie tenga que adivinar por qué había un CubeCAT en el
zip. Si alguien lo conectara al catálogo, la distribución de §3 dejaría de tener
sentido: no hay dónde meter un cubo de 1U en la columna de payload sin vaciar la
bandeja y el banco.

### Los ficheros no van a git; su huella sí

El repositorio es **público** y las condiciones de uso de los CAD de AAC (y de la
mayoría de proveedores) no permiten redistribuirlos, o no se han revisado. Hasta
aclararlo, `cad/vendor/**/*.step`, `*.stp`, `*.sldprt` y `*.zip` están en
`.gitignore`.

Lo que se versiona es **`cad/vendor/MANIFEST.yaml`**: por cada fichero, su ruta,
SHA-256, tamaño, el producto que declara el propio STEP, quién lo pasó y cuándo,
y la copia de referencia en Drive (`MySatNotes/components`). Así se conserva la
trazabilidad commit ↔ fichero sin publicar el CAD.

El chequeo **`step_de_fabricante`** compara disco contra manifiesto:

- fichero **ausente** → `atención`, **no falla**. Quien clone el repositorio sin
  los CAD dibuja esas piezas con su caja envolvente de ficha y puede ejecutarlo
  todo. Es el comportamiento que había antes de que llegara ningún STEP.
- **huella distinta** → `falla`. El modelo se dibujó con una geometría que no es
  la que el manifiesto declara.
- CAD en `cad/vendor/` **sin declarar** → `atención`. Un fichero sin procedencia.

**`cad/generated/` se parte en dos.** Los STEP **por pieza** (unos 15 KB cada
uno) y `escena.json` (43 KB) siguen en git: son cajas envolventes generadas desde
el catálogo y no contienen nada de nadie. El **ensamblaje completo** ya no.
Desde que hay geometría de fabricante dentro, `clau_6u.step` pesa **175 MB** y
`clau_6u.glb` **17 MB** — pero el tamaño es lo de menos: **contienen el CAD de
AAC**, así que versionarlos sería redistribuirlo por la puerta de atrás, justo lo
que evita el `.gitignore` de `cad/vendor/`. Se regeneran con `clau3d ensamblar` y
`clau3d ver`.

Y una pieza que pasa de caja a STEP de fabricante **deja de generarse** ahí:
`exportar_generados()` borra el fichero que hubiera quedado, porque si no el
repositorio seguiría enseñando una caja envolvente de una pieza que el modelo ya
dibuja con su geometría real. Pasó con `obc_kryten_m3_plus.step` y
`bateria_optimus_30.step`.

### El STEP que todavía no ha llegado

`forma.step_esperado` declara por adelantado dónde caerá un fichero y de quién
viene: ruta, `pedir_a` y `fuente_prevista`. Dejar el STEP en esa ruta basta para
que sustituya al modelo aproximado **sin tocar el catálogo**, y entra como
`referencia`, porque que aparezca donde se esperaba no verifica su part number.

Hoy lo usa el telescopio:
`cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step`. El chequeo
`step_de_fabricante` dice qué fichero falta, en qué ruta va y a quién pedírselo,
y avisa de los que han aparecido solos y siguen sin verificar.

Lo que sigue sin existir es la tercera vía, la de importar cualquier fichero que
se llame como el componente: un STEP sin procedencia es lo mismo que un número
sin fuente.

### Los STEP por subsistema y lo que pueden llevar dentro

`clau3d ensamblar` escribe además un STEP por subsistema en
`cad/generated/subsistemas/`. No es un despiece: cada fichero lleva las
coordenadas del satélite completo, así que abrir dos a la vez los enseña
encajados. Sirve para mirar una parte sin cargar los ~550 sólidos del conjunto
y para mandarle a alguien solo lo suyo.

**El nombre del fichero dice si se puede versionar.** Uno que contenga una pieza
dibujada con CAD de fabricante *contiene* ese CAD: hoy `EPS` sale con la batería
de AAC dentro y pesa 141 MB, y `OBC` pesa 32. El sufijo
`_con_cad_de_fabricante` lo pone el exportador **mirando lo que ha metido**, no
una lista escrita a mano, y el `.gitignore` ignora ese sufijo. Así, el día que
llegue el STEP del telescopio, `terminal_optico` pasa solo al lado de los que no
se publican sin que nadie tenga que acordarse. Hay un test que comprueba que el
sufijo del código y el del `.gitignore` siguen siendo el mismo.

### Las dos correcciones que el modelo aplica solo

Un STEP de proveedor casi nunca viene como el modelo lo espera, y la respuesta
**no** es mover coordenadas a mano en el layout. Las dos correcciones viven en el
catálogo, dentro del bloque `forma.step`:

- **`recentrar`** (por defecto `true`) lleva el centro de la caja envolvente al
  origen. El ensamblaje coloca cada pieza por su centro; ninguno de los cuatro
  STEP de esta entrega venía centrado.
- **`orientacion`** gira el sólido alrededor de X, Y y Z, en ese orden, hasta los
  ejes que el catálogo declara en `dimensiones`. **No cambia ninguna cota**, y
  hay un test que lo comprueba. Las tarjetas AAC llegan con X e Y intercambiados
  (`[0, 0, 90]`); sin ese giro el lado de 95.89 mm caería por Y, que solo tiene
  95.4 mm de altura interior, y saldría un desborde que no es real. El iADCS4-20
  llega con el eje de apilamiento por Y (`[90, 0, 0]`).

### Un STEP lleva estado y fuente

`forma.step` exige `estado` y `fuente`, y `validar` falla sin ellos, por el mismo
motivo que lo exige un número. Los tres STEP conectados están como
**`referencia`**, no como `confirmado`: de dos no se ha verificado el part
number, y del tercero AAC no publica ficha. Se dibujan en naranja y el informe lo
dice. El estado del STEP **manda sobre el de la ficha** a la hora de colorear: lo
que se está viendo en pantalla es el STEP.

`tests/test_step_fabricante.py` comprueba el mecanismo con geometría inventada,
por el mismo motivo que `test_interferencias.py`: los STEP reales no se
versionan, así que un test que solo mirara esos ficheros pasaría o fallaría según
quién los tenga descargados.
