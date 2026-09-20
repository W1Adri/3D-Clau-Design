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
| Distribución | **PROPUESTA, sin confirmar**. `data/layout.yaml` tiene 6 zonas y `colocaciones: []` |

Lo que funciona de punta a punta: catálogo validado, piezas y ensamblaje
exportados a STEP, chequeos de viabilidad, presupuestos, vistas SVG e informes.
Lo que **no** puede funcionar todavía: interferencias y recorridos reales, porque
no hay ninguna pieza colocada.

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

---

## 3. Distribución propuesta (PENDIENTE DE CONFIRMAR)

### Sistema de coordenadas

Origen en el centro geométrico (CDS 14.1 req 2.2.1).
X = ±113.15 (ancho, 226.3) · Y = ±50.00 (alto, 100.0) · Z = ±183.00 (largo, 366.0).
La cara **−Z entra primero** en el dispensador. Zona útil interior con el espesor
declarado: **216.5 × 90.2 × 356.2 mm** ≈ 6.96 U.

### El reparto

Tres bandas a lo largo de Z; la banda de +Z partida en dos columnas en X.

```
        −Z ←─────────────── Z (366 mm) ───────────────→ +Z
        (entra primero)                          (apunta a tierra)

  +X  ┌──────────────────┬──────────────┬─────────────────────┐
      │                  │              │  z_telescopio       │
      │ z_bandeja_optica │ z_banco      │  telescopio →→ +Z    │
      │   (mitad −Y)     │   _libre     │  (100 × 90 × 198)   │
      │ ──────────────── │              ├─────────────────────┤
      │ z_pcb_payload    │  colimador   │  z_mazo_cables      │
      │   (mitad +Y)     │  dicroico    │  (16.5 mm)          │
      │   PCB-2          │  FSM, cámara ├─────────────────────┤
      │                  │  PCB-3       │  z_pila_pc104       │
  −X  │                  │              │  ADCS·EPS·OBC·radio │
      └──────────────────┴──────────────┴─────────────────────┘
         98.1 mm            60 mm            198.1 mm
```

| zona | volumen | contenido |
|---|---|---|
| `z_telescopio` | 1.79 U | Telescopio Cassegrain, apertura por +Z |
| `z_pila_pc104` | 1.79 U | ADCS, EPS, OBC, radio banda S, baterías, PCB-1 |
| `z_mazo_cables` | 0.29 U | Pasillo central de cableado |
| `z_banco_libre` | 1.17 U | Colimador, dicroico, FSM, cámara, PCB-3 |
| `z_bandeja_optica` | 0.85 U | Bandeja de fibra (mitad −Y de la banda −Z) |
| `z_pcb_payload` | 1.06 U | PCB-2 como cubierta sobre la bandeja (mitad +Y) |
| | **6.96 U** | Las zonas embaldosan exactamente la zona útil (hay un test) |

### Por qué así

1. **El telescopio manda, y va en +Z.** La apertura necesita vista despejada al
   exterior. Poniéndola en la cara +Z se aleja del dispensador (−Z entra primero)
   y se libera toda la superficie lateral para los paneles.
2. **El ADCS va en la misma banda que el telescopio, en la otra columna.** El
   star tracker ST200 también necesita ver fuera, y le conviene mirar por la
   misma cara que el telescopio: cuanto más cerca y más rígida la unión entre los
   dos, menos error de coalineación en el traspaso de apuntado grueso a fino.
3. **La bandeja de fibra va en −Z, y a lo ancho.** Cada modulador de grado
   espacial necesita **130 mm rectos** (§4). En la zona útil solo X (216.5) y Z
   (356.2) los admiten; Y (90.2) no. Poniendo la bandeja en la banda de −Z y los
   moduladores según X caben los dos holgadamente, y queda sitio para bucles.
4. **PCB-2 va justo encima de la bandeja.** Los coaxiales RF a los moduladores
   bajan en vertical, que es el recorrido más corto posible. Si PCB-2 fuera en la
   pila PC104 el coaxial mediría más de 100 mm.
5. **PCB-3 va en el banco de espacio libre**, por lo mismo: el driver del FSM y
   la lectura de la cámara son lazos rápidos y no conviene alargarlos.
6. **Las baterías van en −Z.** Equilibran en Z la masa del telescopio, que está
   en +Z, y quedan lejos del láser: son lo más delicado térmicamente de la
   plataforma (−10 a +50 °C, la ventana más estrecha).
7. **Columna de plataforma en −X, telescopio en +X.** Equilibra el centro de
   gravedad en X, que la norma limita a ±45 mm.

### Lo que hay que decidir antes de fijarla

- **Diámetro exterior del barrilete del telescopio.** Es lo que decide si el
  payload cabe. Ver §4.
- **Paso de apilamiento PC104.** La pila tiene 198.1 mm; las 6 tarjetas con
  altura conocida suman 153.6 mm, pero eso es una **cota inferior**.
- **Radio mínimo de curvatura de la fibra.** Sin él no se puede dimensionar la
  bandeja ni comprobar un solo bucle.

### Alternativas si no cuadra

- **Partir el 6U en dos columnas de 3U a lo largo de todo Z** (payload en +X,
  plataforma en −X). Da 340 mm de pila pero deja solo ~113 mm de ancho para la
  bandeja, y ahí los moduladores de 130 mm ya no caben en X: habría que
  orientarlos según Z y alargar la bandeja.
- **Acortar el telescopio.** El brief lo admite ("se puede acortar un poco si
  hace falta volumen"). Cada 10 mm recortados son 10 mm más de pila PC104.
- **Bajar a un módulo de batería.** Libera 21.55 mm de pila, a costa de 30 Wh.

---

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
altura interior es **90.2 mm**, así que una apertura libre de 90 mm deja
**0.1 mm por lado**. Sin sitio para barrilete, celda de espejo ni ajuste.

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

### 4.3 Otras discrepancias registradas

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

1. **Confirmar la distribución** (§3). Sin eso no hay interferencias ni
   recorridos reales.
2. Rellenar `colocaciones` en `data/layout.yaml` y poner `estado: confirmada`.
3. Conseguir los tres datos que bloquean más cosas: **diámetro exterior del
   telescopio**, **paso de apilamiento PC104** y **radio mínimo de curvatura de
   la fibra**.
4. Declarar los *keep-out* del haz óptico. Ahora `keep_out: []` a propósito:
   inventar medidas de haz daría una falsa sensación de comprobación.
5. Sustituir el chasis genérico por el STEP del equipo, con lo que desaparece la
   hipótesis de espesor de pared.

---

## 7. Notas de implementación

- **Python 3.12**, no 3.14: CadQuery/OCP no tiene ruedas para 3.14 todavía.
- **CadQuery 2.8**. `Assembly.save()` está obsoleto; se usa `Assembly.export()`.
- Las interferencias se filtran primero por caja envolvente y solo entonces se
  hace la booleana de OCC, que es cara.
- El mapa de hueco libre es una rejilla de ocupación proyectada sobre el plano
  X-Z. Paso de 10 mm por defecto.
- `clau3d informe` devuelve código de salida **1** si hay chequeos críticos o
  interferencias, para poder engancharlo a CI.
