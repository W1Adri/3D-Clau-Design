# CLAUDE.md — Estado, decisiones y razonamiento

Documento de continuidad entre sesiones. El README explica **qué** es el
repositorio; esto explica **por qué** está como está y **qué falta por decidir**.

Última actualización: **2026-09-20**.

---

## 1. Dónde estamos

| | |
|---|---|
| Catálogo | 29 componentes, 0 problemas de integridad |
| Con envolvente conocida | **10 de 29** |
| Datos pendientes (TBD) | **53** |
| Discrepancias entre fuentes | **6** |
| Tests | **78**, todos en verde |
| Distribución | **CONFIRMADA** el 2026-09-20: dos columnas de 3U, moduladores en la franja lateral |
| Piezas colocadas | **8 de 27**. Las otras 19 tienen geometría TBD |
| Geometría real de fabricante | **3 de las 8** piezas colocadas salen ya de un STEP (§9) |
| Riesgos abiertos | **1**: acoplamiento térmico modulador–barrilete (§3.6) |
| Zona útil | 221.7 × 95.4 × 361.4 mm = **7.64 L**, de la que quedan **5.84 L** libres |

Funciona de punta a punta: catálogo validado, layout generado, ensamblaje
exportado a STEP, interferencias, conexiones, volumen, presupuestos, vistas e
informes. Sin interferencias ni desbordes con las 8 piezas colocadas.
Para mirarlo, `uv run clau3d ver` (§8).

La limitación real no es el modelo, son los datos: **19 de 27 componentes no
tienen envolvente**, así que el volumen libre de 5.84 L es un techo, no una
cifra de diseño.

---

## 2. Cómo se trabaja aquí

- **Ningún número en el código.** Todo sale de `data/*.yaml`. Si hace falta un
  número nuevo, va al catálogo con fuente y estado, no a un literal.
- **Un hueco se queda como hueco.** `TBD` obliga a `falta` y `pedir_a`, y el
  valor tiene que ser `null`. Hay un test para cada una de esas tres cosas.
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
         │                      │             │ 26.3 mm · 2 moduladores │
         │                      │             │ tumbados, pegados a −Z  │
  PAYLOAD│ z_payload_bandeja    │ z_payload   ├─────────────────────────┤
  121.7  │ 1.24 L               │  _banco     │ z_payload_telescopio    │
   mm    │ láser DFB (4.1 W),   │ 0.64 L      │ 1.82 L · 95.4 mm de X   │
         │ bucles en los 121.7  │ colimador   │ telescopio →→ +Z        │
         │ mm de ancho enteros  │ dicroico    │ 200 mm RESERVADOS       │
         │                      │ FSM, cámara │ (provisional)           │
  −10.85 ├──────────────────────┴─────────────┴─────────────────────────┤
         │ z_plataforma  3.45 L                                         │
  PLATAF.│ pila PC104 a lo largo de todo Z — 259 mm usados de 361 mm     │
  100 mm │ −Z ← baterías·baterías·PCB-2·PCB-1·PCB-3·radio·EPS·OBC·ADCS → │
 −110.85 └──────────────────────────────────────────────────────────────┘
             106.4 mm             55 mm            200 mm
```

| zona | volumen | libre | contenido |
|---|---|---|---|
| `z_plataforma` | 3.45 L | 2.09 L | Pila PC104 completa |
| `z_payload_telescopio` | 1.82 L | 1.82 L | Telescopio (TBD, sin dibujar) |
| `z_payload_franja` | 0.50 L | 0.47 L | Los 2 moduladores, tumbados |
| `z_payload_banco` | 0.64 L | 0.64 L | Colimador, dicroico, FSM, cámara |
| `z_payload_bandeja` | 1.24 L | 1.24 L | Bandeja de fibra, láser DFB (todo TBD) |

Las cinco zonas **embaldosan exactamente** la zona útil; hay un test que lo
comprueba. La columna de payload se parte en X **solo a lo largo del
telescopio**: 95.4 mm para el barrilete y 26.3 mm de franja.

### Orden de la pila, de +Z a −Z

Con el paso estándar PC/104 de 15.24 mm; una tarjeta más alta ocupa
`ceil(altura / paso)` posiciones de separador.

| # | tarjeta | altura | posiciones | por qué ahí |
|---|---|---|---|---|
| 1 | iADCS400 | 67.3 mm | 5 | En +Z, para que el ST200 mire por la misma cara que el telescopio |
| 2 | Kryten-M3-PLUS | 5.51 mm | 1 | Junto al ADCS y al payload |
| 3 | Starbuck-Nano-PLUS | 20.82 mm | 2 | |
| 4 | Quasar-STRX | 16.9 mm (ref) | 2 | |
| 5 | PCB-3 PAT | TBD | 1 reservada | A la altura del banco de espacio libre |
| 6 | PCB-1 Control QKD | TBD | 1 reservada | |
| 7 | PCB-2 Drivers | TBD | 1 reservada | Lo más cerca posible de la bandeja |
| 8-9 | Optimus-30 ×2 | 21.55 mm | 2 cada una | En −Z, equilibran la masa del telescopio |
| | **total** | | | **259 mm de 361 mm** |

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
- **La pila PC104 deja de ser el problema**: **259 mm usados de 361 mm**, con
  102 mm de margen para que las tres PCBs propias crezcan más de una posición de
  separador. En la otra opción la pila tenía 198 mm y ya iba justa.

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
  6.25 L a **5.84 L**, porque lo que ocupan las tarjetas ya no es su caja de
  ficha.

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
4. **Los tres datos que bloquean más cosas**:
   - **STEP del telescopio** (Óscar / Aperture Optical Sciences): diámetro
     exterior del barrilete **y longitud real**. El diámetro decide si el payload
     cabe; la longitud sustituye a los 200 mm provisionales de
     `longitud_reservada`. Ojo: los «~2U» del brief son ~227 mm, no 200 (la U de
     longitud de la CDS son 113.5 mm).
   - **Radio mínimo de curvatura de la fibra** (equipo de payload). Sin él no se
     puede comprobar ni un bucle de la bandeja, que es justo donde esta
     distribución tiene su punto flojo.
   - **Paso de apilamiento real del chasis** (equipo de estructura). Ahora se usa
     el estándar PC/104; el real puede cambiar los 259 mm de pila.
5. **Alturas de PCB-1, PCB-2 y PCB-3.** Con ellas las tres dejan de ser reservas
   y pasan a ser piezas colocadas.
6. **Declarar los keep-out del haz óptico**, cuando lleguen los diámetros de haz.
   Ahora `keep_out: []` a propósito: inventar medidas daría una falsa sensación
   de comprobación.
7. **Sustituir el chasis genérico por el STEP del equipo**, con lo que desaparece
   la hipótesis de espesor de pared y la zona útil pasa a ser real.
8. **Cerrar el encaminamiento de los 4.1 W del láser**: directo del bus del EPS o
   a través de PCB-2.

## 7. Notas de implementación

- **Python 3.12**, no 3.14: CadQuery/OCP no tiene ruedas para 3.14 todavía.
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
cota y qué falta**. El visor colorea por estado del dato, lista los 19
componentes sin envolvente con a quién pedírselos, marca el volumen libre como
*techo* mientras `resumen.fiable` sea falso y muestra los chequeos con el mismo
criterio que `reports/`. Un visor genérico no puede decir nada de eso.

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
