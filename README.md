# CLAU — Modelo 3D y análisis volumétrico

Modelo 3D paramétrico del CubeSat 6U **CLAU** (*CubeSat Làser per a Aplicacions
Ultrasegures*), de la asociación **ACSAR** (EETAC, UPC).

## La misión en pocas líneas

CLAU demostrará **distribución cuántica de claves (QKD)** desde órbita baja hacia
la estación óptica terrestre **ESA OGS Teide** (telescopio de 1 m). Protocolo
**BB84 con estados señuelo (decoy)**, codificación en **polarización**, a
**1550 nm**.

**Arquitectura "opción B"** (19-09-2026): el transmisor BB84 se construye con
componentes de **fibra comerciales** — láser DFB pulsado más moduladores de
niobato de litio —, **sin chip fotónico (PIC) en vuelo** y **sin canal óptico
clásico**. El canal clásico para el post-procesado de la clave va por **radio en
banda S**.

Quedan **fuera** de la arquitectura, y por tanto fuera de este modelo: CubeCAT,
el módulo cuántico integrado tipo QUBE y el PIC.

## Qué hace este repositorio y por qué

La prioridad es el **análisis volumétrico**: responder con números, y no con
intuición, a si el payload cabe en 6U y dónde queda el hueco libre. Sobre esa
base, el repositorio:

1. **Informe de volumen** — tabla por componente (volumen, posición, estado del
   dato), volumen libre en cm³ y en U, y un mapa de dónde está ese hueco.
2. **Test de interferencias** — falla si dos sólidos se solapan, si algo sale de
   la envolvente 6U o si invade un *keep-out*.
3. **Test de conexiones** — falla si una conexión apunta a un componente que no
   existe o sin espacio para el conector.
4. **Presupuestos de masa y potencia** — separando lo confirmado de lo que no lo
   está, sin rellenar huecos.
5. **Vistas renderizadas** — con los TBD a la vista, en su propio color.

Todo se regenera con **un solo comando** (`uv run clau3d todo`). No hay ningún
número escrito a mano en ningún informe.

## Regla principal: ningún número inventado

**Todas** las dimensiones, masas y consumos viven en un único fichero,
`data/components.yaml`. No hay literales repartidos por el código. Cada magnitud
es un bloque con **valor, unidad, fuente y estado**:

| estado | significado |
|---|---|
| `confirmado` | Sale de la ficha técnica o de la norma **del componente elegido**. |
| `referencia` | Sale de un componente **parecido**, no del elegido. Sirve para reservar volumen, no para cerrar el diseño. |
| `decision` | Decisión de diseño de ACSAR. No procede de ninguna ficha. |
| `TBD` | Falta el dato. El valor es `null` y es **obligatorio** decir qué falta y a quién pedirlo. |

Tres consecuencias, y las tres son tests que fallan si se incumplen:

- **Un hueco se queda como hueco.** Una magnitud `TBD` no puede tener valor. No
  se rellena con nada "razonable" sin marcarlo.
- **Si dos fuentes discrepan, se guardan las dos.** El campo `alternativas`
  conserva la cifra que no se usa, con su fuente y el porqué. Hay 4
  discrepancias registradas ahora mismo; están en `reports/06_pendientes.md`.
- **Lo que no se puede comprobar, se dice.** Un chequeo sin datos sale como
  `no comprobable`, nunca como correcto.

En los renders, el **estado manda sobre la categoría**:

| color | significado |
|---|---|
| **magenta** | `TBD` — falta el dato |
| **naranja** | `referencia` — componente parecido, no el elegido |
| **azul** | `decision` — decisión de diseño |
| color de su categoría | `confirmado` |

## Instalación y uso

Requiere [`uv`](https://docs.astral.sh/uv/) (igual que el resto de repos del
proyecto). Python 3.12: **CadQuery/OCP aún no tiene ruedas para 3.14**, y `uv` se
encarga de descargar la versión correcta.

```bash
git clone https://github.com/W1Adri/3D-Clau-Design.git
cd 3D-Clau-Design
uv sync
```

| Orden | Qué hace |
|---|---|
| `uv run python tools/generar_layout.py` | Regenera `data/layout.yaml` desde el catálogo. |
| `uv run clau3d validar` | Comprueba la integridad del catálogo (estados, fuentes, TBD, conexiones). |
| `uv run clau3d piezas` | Exporta cada pieza generada a `cad/generated/*.step`. |
| `uv run clau3d ensamblar` | Exporta el ensamblaje completo a `cad/generated/clau_6u.step`. |
| `uv run clau3d informe` | Regenera todo `reports/`: informes y vistas. |
| **`uv run clau3d todo`** | **Las cuatro anteriores, de una vez.** |
| `uv run pytest` | Tests de datos, estructura, interferencias, conexiones y viabilidad. |

## Cómo se abre el resultado en FreeCAD

1. `uv run clau3d ensamblar` genera `cad/generated/clau_6u.step`.
2. En FreeCAD: **Archivo → Abrir** y elegir ese `.step`.

El ensamblaje se exporta con **nombres y colores por pieza**, así que en el árbol
del modelo aparece cada componente con su `id` del catálogo y su color de estado.
Los sólidos son geometría B-Rep estándar: no hace falta ningún complemento.

Las piezas sueltas de `cad/generated/` se abren igual, y se pueden reimportar en
este repositorio exactamente como los STEP de fabricante.

## Los dos orígenes de geometría

```
cad/vendor/      STEP de fabricante y del equipo — NO se tocan
cad/generated/   STEP generados por este repositorio
```

Cada componente puede estar en **cualquiera de los dos estados** sin que cambie
nada más del ensamblaje.

### Añadir un STEP de fabricante y sustituir una caja envolvente

1. Copiar el fichero a `cad/vendor/`, p. ej. `cad/vendor/iadcs400.step`.
2. En `data/components.yaml`, en el bloque `forma` de ese componente, añadir la
   línea `step:` con la ruta **relativa a la raíz del repositorio**:

   ```yaml
     - id: adcs_iadcs400
       forma:
         tipo: step
         step: cad/vendor/iadcs400.step
         dimensiones:          # se conserva como referencia de ficha
           valor: [95.4, 95.9, 67.3]
           unidad: mm
           estado: confirmado
           fuente: ...
   ```

3. `uv run clau3d todo`.

A partir de ahí la caja desaparece y el modelo usa la geometría real: el
ensamblaje, las interferencias y el volumen se recalculan solos. **No hay que
tocar el código ni la distribución.** Si la ruta no existe, `clau3d validar`
falla y dice que dejes el componente como caja hasta que llegue el STEP.

Cuando llegue el **chasis 6U del equipo**, sustituye al genérico por el mismo
camino, y además desaparece la hipótesis de espesor de pared (ver más abajo).

## Estructura del repositorio

```
data/components.yaml    dimensiones, masas, consumos, fuentes y estado
data/connections.yaml   conexiones ópticas, RF, datos, potencia y térmicas
data/layout.yaml        distribución dentro del 6U (GENERADO, no editar)
tools/generar_layout.py genera data/layout.yaml desde el catálogo
src/clau3d/             modelo de datos, piezas, ensamblaje, análisis, informes
tests/                  interferencias, conexiones, integridad de los datos
cad/vendor/             STEP de fabricante (no se tocan)
cad/generated/          STEP generados por este repositorio
reports/                informes y vistas (generados, no editar)
CLAUDE.md               estado, decisiones y razonamiento de la distribución
```

## Estado actual

- **Norma**: CubeSat Design Specification **Rev. 14.1** (2022-02-09), que
  sustituye a la Rev. 13 y a la 6U CDS Rev 1.0. Envolvente 6U del plano
  CDS-14-007: **226.3 × 100.0 × 366.0 mm**, masa máxima 12.00 kg.
- **28 componentes** en el catálogo. Solo **9 tienen envolvente conocida**: el
  resto está en TBD y no se dibuja.
- **49 datos pendientes** y **4 discrepancias** entre fuentes.
- **Distribución confirmada** (2026-09-20): **dos columnas de 3U** a lo largo de
  todo Z — plataforma en −X, payload en +X. `data/layout.yaml` no se escribe a
  mano: lo genera `tools/generar_layout.py` desde el catálogo.
- **8 piezas colocadas**, sin interferencias, todas dentro de la envolvente.
  Las otras 19 no se pueden colocar porque su geometría es TBD.
- Zona útil interior **221.7 × 95.4 × 361.4 mm = 7.64 U**, de la que hay
  **6.25 U libres** — cifra que bajará conforme lleguen las 19 envolventes que
  faltan.

### Lo que ya aprieta, con números

| Hallazgo | Número |
|---|---|
| La apertura de 90 mm del telescopio contra la altura interior | Deja **2.7 mm por lado**. El eje óptico no puede ir paralelo a Y, y en cualquier otra orientación la sección sigue limitada por Y. Falta el **diámetro exterior del barrilete**, que es lo que decide si cabe. |
| El **iADCS400** (95.4 mm de lado corto) dentro de los 100 mm exteriores | El espesor de pared no puede pasar de **2.30 mm**. Es la pieza que más aprieta, por delante del contorno PC104 desnudo, que daba 4.91 mm. |
| Moduladores Exail de **grado espacial** | **130 mm** de recorrido recto cada uno, protectores de fibra incluidos. Es **45 mm más largo** que la cifra del encapsulado comercial. En la columna de payload, de 121.7 mm de ancho, **no caben según X**: van según Z. |
| Longitud de la pila PC104 | **274 mm de 361 mm**, con el paso estándar PC/104 de 15.24 mm y reservando una posición por cada tarjeta de altura TBD. El paso **real** del chasis sigue siendo TBD. |
| Bucles de fibra | **No comprobable**: falta el radio mínimo de curvatura, que es lo que más área consume de la bandeja. |

## Decisiones de diseño tomadas

- **CadQuery** como núcleo del modelado, con exportación a STEP. No se usa
  build123d: CadQuery cubre todo lo que hace falta aquí y es la dependencia más
  ligera. Nada de Onshape ni Fusion 360.
- **El layout es un dato, no código.** Cambiar la distribución es editar
  `data/layout.yaml`; el modelo, los tests y los informes se recalculan solos.
- **El estado del dato manda sobre la categoría** en el color de los renders: lo
  que falta se ve antes que lo que está.
- **Distribución: dos columnas de 3U** a lo largo de todo Z (2026-09-20).
  Plataforma en −X con la pila PC104 completa; payload en +X repartido en
  telescopio / banco de espacio libre / bandeja de fibra. Razonamiento y
  contrapartidas en `CLAUDE.md` §3.
- **El layout se genera, no se escribe.** `tools/generar_layout.py` calcula cada
  coordenada desde `data/components.yaml` y el paso PC/104. Cuando llegue una
  dimensión nueva, se regenera; no se recalcula a ojo.
- **Espesor de pared = 2.3 mm** como hipótesis única de trabajo, y es el **mayor
  espesor compatible con todas las piezas conocidas**: lo fija el iADCS400, que
  al ser tarjeta apilada no se puede tumbar y necesita 95.4 mm de los 100 mm
  exteriores. Da el **menor volumen útil posible**, así que todo volumen libre
  que salga de aquí **se queda corto, nunca se pasa**. El chequeo
  `seccion_componentes` recalcula esta cota desde el catálogo y avisa si deja de
  ser válida. Desaparece en cuanto llegue el chasis del equipo.
- **Paso de apilamiento modelado = 15.24 mm**, el estándar PC/104 (0.600 in).
  Una tarjeta más alta que el paso ocupa `ceil(altura / paso)` posiciones de
  separador. El paso real del chasis sigue siendo TBD.
- **Para los moduladores se usa la cifra de grado espacial**, no la comercial:
  es el encapsulado que vuela. La comercial queda registrada como alternativa.
- **Se modelan 2 baterías Optimus-30** solo para reservar volumen. El número real
  es TBD y depende del presupuesto de energía.

## Decisiones que siguen abiertas

- **Diámetro exterior y longitud del telescopio.** Decide si el payload cabe.
  La distribución le reserva 160 mm de longitud, menos que los ~2U del brief.
- **Cómo se encamina la potencia del láser** (4.1 W): directa del bus del EPS o
  a través de PCB-2.
- **FSM**: MEMS tipo Mirrorcle (herencia CLICK-A) frente a piezo PI S-331. Las
  dos familias tienen envolventes muy distintas.
- **Formato PC104 para las tres PCBs propias.** Está propuesto, no confirmado.
- **Número de módulos de batería** y **configuración de paneles PHOTON**.
- **Starbuck-Nano-PLUS frente a Starbuck-Nano**: la ficha describe el PLUS para
  plataformas con **paneles desplegables**, y CLAU parte de paneles de montaje en
  cuerpo. A revisar con AAC.
- **Propulsión**: opcional, prioridad baja, entre 0.1U y 1U.
- **Radio UHF Pulsar-VUTRX**: opcional, solo si queda volumen.

## Lista de pendientes

La lista completa y siempre al día está en **`reports/06_pendientes.md`**, que se
regenera con `uv run clau3d informe`. Esta copia es una foto del estado actual
(**49 pendientes**):

### AAC Clyde Space (6)

| componente | magnitud | qué falta |
|---|---|---|
| `adcs_iadcs400` | `masa` | Masa exacta de la configuracion elegida |
| `antena_quasar_wsant` | `dimensiones` | Dimensiones y cara de montaje de la antena |
| `antena_quasar_wsant` | `masa` | Masa |
| `radio_uhf_pulsar_vutrx` | `dimensiones` | Dimensiones |
| `radio_uhf_pulsar_vutrx` | `masa` | Masa |
| `paneles_photon_side` | `dimensiones` | Dimensiones de cada panel segun la cara elegida (1U/2U/3U/6U) |

### ACSAR (decision de mision aun abierta) (2)

| componente | magnitud | qué falta |
|---|---|---|
| `propulsion` | `dimensiones` | Modelo de propulsor y sus dimensiones |
| `propulsion` | `masa` | Masa del propulsor elegido |

### Aperture Optical Sciences (2)

| componente | magnitud | qué falta |
|---|---|---|
| `telescopio_cassegrain` | `masa` | Masa |
| `telescopio_cassegrain` | `longitud_optica` | Longitud del tubo. Interesa distancia focal larga; se admite acortar. |

### Aperture Optical Sciences / equipo de optica de ACSAR (1)

| componente | magnitud | qué falta |
|---|---|---|
| `telescopio_cassegrain` | `dimensiones` | Diametro exterior del barrilete y longitud optica del tubo |

### Equipo de PAT de ACSAR (4)

| componente | magnitud | qué falta |
|---|---|---|
| `camara_beacon` | `dimensiones` | Modelo de sensor y su envolvente |
| `camara_beacon` | `masa` | Masa del sensor elegido |
| `laser_beacon_bajada` | `dimensiones` | Longitud de onda, potencia y envolvente |
| `laser_beacon_bajada` | `masa` | Masa del laser de beacon elegido |

### Equipo de electronica de ACSAR (7)

| componente | magnitud | qué falta |
|---|---|---|
| `integracion` | `holgura_conector` | Holgura de insercion por tipo de conector (coaxial RF, AVIM optico, conectores de datos) |
| `pcb1_control_qkd` | `dimensiones` | Altura de la tarjeta (contorno PC104 propuesto, altura por disenar) |
| `pcb1_control_qkd` | `masa` | Masa de la tarjeta poblada |
| `pcb2_drivers_opticos` | `dimensiones` | Altura de la tarjeta |
| `pcb2_drivers_opticos` | `masa` | Masa de la tarjeta poblada |
| `pcb3_pat` | `dimensiones` | Altura de la tarjeta, y si el driver del FSM es de alta tension |
| `pcb3_pat` | `masa` | Masa de la tarjeta poblada |

### Equipo de estructura de ACSAR (2)

| componente | magnitud | qué falta |
|---|---|---|
| `integracion` | `pila_pc104.paso_apilamiento` | Paso real entre tarjetas (separadores) del chasis elegido |
| `estructura_6u` | `masa` | Masa del chasis 6U elegido |

### Equipo de optica de ACSAR (6)

| componente | magnitud | qué falta |
|---|---|---|
| `fsm` | `dimensiones` | Eleccion entre MEMS (Mirrorcle, herencia CLICK-A, espejo 5 mm) y piezo PI S-331, y su envolvente |
| `fsm` | `masa` | Masa del FSM elegido (MEMS o piezo) |
| `dicroico` | `dimensiones` | Dimensiones del sustrato y del soporte |
| `dicroico` | `masa` | Masa del dicroico y su soporte |
| `colimador` | `dimensiones` | Modelo y envolvente (diametro de haz colimado, longitud) |
| `colimador` | `masa` | Masa del colimador elegido |

### Equipo de payload de ACSAR (9)

| componente | magnitud | qué falta |
|---|---|---|
| `integracion` | `fibra.radio_minimo_curvatura` | Radio minimo de curvatura de la fibra elegida (probablemente PM a 1550 nm) |
| `voa` | `dimensiones` | Modelo y envolvente |
| `voa` | `masa` | Masa del VOA elegido |
| `aislador` | `dimensiones` | Modelo y envolvente |
| `aislador` | `masa` | Masa del aislador elegido |
| `filtro_espectral` | `dimensiones` | Modelo y envolvente |
| `filtro_espectral` | `masa` | Masa del filtro elegido |
| `acoplador_monitor` | `dimensiones` | Modelo y envolvente |
| `acoplador_monitor` | `masa` | Masa del acoplador y el fotodiodo |

### Equipo de potencia de ACSAR (3)

| componente | magnitud | qué falta |
|---|---|---|
| `bateria_optimus_30` | `cantidad` | Numero de modulos de bateria N segun el presupuesto de energia |
| `paneles_photon_side` | `cantidad` | Numero de caras pobladas y tamano de cada una |
| `paneles_photon_side` | `masa` | Masa total segun el numero de caras pobladas (la ficha da 135 g por cara de 3U) |

### Este repositorio, tras fijar el layout (2)

| componente | magnitud | qué falta |
|---|---|---|
| `bandeja_optica` | `dimensiones` | Contorno definitivo, que sale de la distribucion una vez confirmada |
| `bandeja_optica` | `masa` | Masa de la placa, que sale del contorno y el material una vez fijado el layout |

### Exail (2)

| componente | magnitud | qué falta |
|---|---|---|
| `mod_intensidad_mxer_ln_10` | `masa` | Masa del encapsulado de grado espacial |
| `mod_fase_mpz_ln_10` | `masa` | Masa del encapsulado de grado espacial |

### Gooch & Housego (2)

| componente | magnitud | qué falta |
|---|---|---|
| `laser_dfb_1550` | `dimensiones` | Envolvente del encapsulado butterfly con Peltier (y del disipador) |
| `laser_dfb_1550` | `masa` | Masa del modulo butterfly con Peltier |

### ID Quantique (1)

| componente | magnitud | qué falta |
|---|---|---|
| `qrng_idq20mc1_s3` | `masa` | Masa por unidad |

---

<sub>Los informes de `reports/` y los STEP de `cad/generated/` se generan
automáticamente. No editarlos a mano.</sub>
