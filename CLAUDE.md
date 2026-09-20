# CLAUDE.md — Estado, decisiones y razonamiento

Documento de continuidad entre sesiones. El README explica **qué** es el
repositorio; esto explica **por qué** está como está y **qué falta por decidir**.

Última actualización: **2026-09-20**.

---

## 1. Dónde estamos

| | |
|---|---|
| Catálogo | 28 componentes, 0 problemas de integridad |
| Con envolvente conocida | **9 de 28** |
| Datos pendientes (TBD) | **49** |
| Discrepancias entre fuentes | **4** |
| Tests | **40**, todos en verde |
| Distribución | **CONFIRMADA** el 2026-09-20: dos columnas de 3U |
| Piezas colocadas | **8 de 27**. Las otras 19 tienen geometría TBD |
| Zona útil | 221.7 × 95.4 × 361.4 mm = **7.64 L**, de la que quedan **6.25 L** libres |

Funciona de punta a punta: catálogo validado, layout generado, ensamblaje
exportado a STEP, interferencias, conexiones, volumen, presupuestos, vistas e
informes. Sin interferencias ni desbordes con las 8 piezas colocadas.

La limitación real no es el modelo, son los datos: **19 de 27 componentes no
tienen envolvente**, así que el volumen libre de 6.25 L es un techo, no una
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
- **Una comprobación circular no es una comprobación.** Si una cota se dedujo de
  una pieza, comprobar esa misma pieza contra esa cota devuelve la hipótesis, no
  un resultado. Sale como `no comprobable`, igual que un chequeo sin datos.

---

## 3. Distribución confirmada (2026-09-20)

Elegida entre dos opciones: **dos columnas de 3U a lo largo de todo Z**.

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
         │ z_payload_bandeja    │ z_payload   │ z_payload_telescopio    │
         │ 1.70 L               │  _banco     │ 1.86 L                  │
  PAYLOAD│ moduladores según Z  │ 0.64 L      │ telescopio →→ +Z        │
  121.7  │ (130 mm no caben     │ colimador   │ 160 mm reservados       │
   mm    │  en 121.7 mm de X)   │ dicroico    │                         │
         │                      │ FSM, cámara │                         │
  −10.85 ├──────────────────────┴─────────────┴─────────────────────────┤
         │ z_plataforma  3.45 L                                         │
  PLATAF.│ pila PC104 a lo largo de todo Z — 259 mm usados de 361 mm     │
  100 mm │ −Z ← baterías·baterías·PCB-2·PCB-1·PCB-3·radio·EPS·OBC·ADCS → │
 −110.85 └──────────────────────────────────────────────────────────────┘
             146.4 mm             55 mm            160 mm
```

| zona | volumen | libre | contenido |
|---|---|---|---|
| `z_plataforma` | 3.45 L | 2.09 L | Pila PC104 completa |
| `z_payload_telescopio` | 1.86 L | 1.86 L | Telescopio (TBD, sin dibujar) |
| `z_payload_banco` | 0.64 L | 0.64 L | Colimador, dicroico, FSM, cámara |
| `z_payload_bandeja` | 1.70 L | 1.67 L | Bandeja de fibra, 2 moduladores colocados |

Las cuatro zonas **embaldosan exactamente** la zona útil; hay un test que lo
comprueba.

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

### Las dos contrapartidas, asumidas al elegir esta opción

- **Los moduladores van según Z, no según X.** Sus 130 mm de recorrido recto no
  caben en los 121.7 mm de ancho de la columna de payload. Funciona, pero los
  bucles de fibra tienen que girar hacia los lados, y eso **no se puede
  comprobar** hasta tener el radio mínimo de curvatura.
- **PCB-2 queda en la otra columna que los moduladores.** El coaxial RF cruza el
  satélite a lo ancho, unos 100 mm. Es el precio de tener toda la pila junta.

### Lo bueno que compra

La pila PC104 deja de ser el problema: **259 mm usados de 361 mm**, con 102 mm de
margen para que las tres PCBs propias crezcan más de una posición de separador.
En la otra opción la pila tenía 198 mm y ya iba justa.

### Cómo se regenera

`data/layout.yaml` **no se edita a mano**. Todas las coordenadas salen del
catálogo:

```bash
uv run python tools/generar_layout.py
```

Las únicas decisiones de reparto están en la cabecera de ese script:
ancho de la columna de plataforma, longitud del telescopio y del banco, y el
orden de la pila.

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
del tubo (~2U) tiene que caber en 90 mm, que es peor. En cualquier otra
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

0. **DECISIÓN ABIERTA (2026-09-20): dónde van los moduladores.** La distribución
   confirmada los pone en la bandeja, según Z, y eso le cuesta 146.4 mm de Z al
   payload. Con el banco fijo en 55 mm, el telescopio no puede pasar de
   **176.4 mm** ni vaciando la bandeja: **la opción confirmada no llega a los
   ~2U (200 mm) del brief.** La alternativa es meter los moduladores en la franja
   de 121.7 − Ø_barrilete mm que queda al lado del telescopio, a lo largo de Z.
   Evaluada, cabe y sube el techo del telescopio a 306.4 mm; ver el detalle en la
   propuesta. **Pendiente de que el equipo la acepte antes de tocar
   `tools/generar_layout.py`.**
1. **Los tres datos que bloquean más cosas**:
   - **Diámetro exterior del barrilete del telescopio** (Aperture Optical
     Sciences). Decide si el payload cabe, y si los 160 mm reservados bastan.
   - **Radio mínimo de curvatura de la fibra** (equipo de payload). Sin él no se
     puede comprobar ni un bucle de la bandeja, que es justo donde esta
     distribución tiene su punto flojo.
   - **Paso de apilamiento real del chasis** (equipo de estructura). Ahora se usa
     el estándar PC/104; el real puede cambiar los 259 mm de pila.
2. **Alturas de PCB-1, PCB-2 y PCB-3.** Con ellas las tres dejan de ser reservas
   y pasan a ser piezas colocadas.
3. **Declarar los keep-out del haz óptico**, cuando lleguen los diámetros de haz.
   Ahora `keep_out: []` a propósito: inventar medidas daría una falsa sensación
   de comprobación.
4. **Sustituir el chasis genérico por el STEP del equipo**, con lo que desaparece
   la hipótesis de espesor de pared y la zona útil pasa a ser real.
5. **Cerrar el encaminamiento de los 4.1 W del láser**: directo del bus del EPS o
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
