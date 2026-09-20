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
| `supuesto` | Número **inventado aquí** para poder dibujar la pieza. No sale de ninguna fuente: `fuente` lleva el razonamiento. Exige además `falta` y `pedir_a`, como un TBD. |
| `TBD` | Falta el dato **y no hay aproximación defendible**. El valor es `null` y es **obligatorio** decir qué falta y a quién pedirlo. |

Cuatro consecuencias, y las cuatro son tests que fallan si se incumplen:

- **Un hueco se queda como hueco.** Una magnitud `TBD` no puede tener valor. No
  se rellena con nada "razonable" **sin marcarlo**.
- **Un número inventado se declara como inventado.** Eso es `supuesto`, y tiene
  precio: **no suma** en los presupuestos de masa ni de potencia, se dibuja en
  gris y sale en la lista de pendientes junto a los TBD, con el valor concreto
  que hay que sustituir. La diferencia con TBD no es si el dato está, es si la
  pieza se puede dibujar.
- **Si dos fuentes discrepan, se guardan las dos.** El campo `alternativas`
  conserva la cifra que no se usa, con su fuente y el porqué. Están en
  `reports/06_pendientes.md`.
- **Lo que no se puede comprobar, se dice.** Un chequeo sin datos sale como
  `no comprobable`, nunca como correcto.

En los renders, el **estado manda sobre la categoría**:

| color | significado |
|---|---|
| **magenta** | `TBD` — falta el dato |
| **naranja** | `referencia` — componente parecido, no el elegido |
| **azul** | `decision` — decisión de diseño |
| **gris**, más transparente | `supuesto` — número inventado aquí, solo reserva sitio |
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
| `uv run clau3d ensamblar` | Exporta el ensamblaje completo a `cad/generated/clau_6u.step` y **un STEP por subsistema** en `cad/generated/subsistemas/`. |
| `uv run clau3d informe` | Regenera todo `reports/`: informes, vistas y `components_status.csv`. Devuelve **1** si hay choques de geometría o chequeos críticos; una invasión de keep-out supuesto **no** cuenta. |
| **`uv run clau3d ver`** | **Abre el visor interactivo en `http://localhost:8000`.** |
| **`uv run clau3d todo`** | **Las cuatro primeras, de una vez.** |
| `uv run pytest` | Tests de datos, estructura, interferencias, conexiones y viabilidad. |

## Cómo se mira el modelo: `clau3d ver`

```bash
uv run clau3d ver
```

Levanta un servidor en `http://localhost:8000` y abre el navegador. Es la forma
normal de mirar el satélite: órbita con el botón izquierdo, *pan* con el
derecho, zoom con la rueda.

| Panel | Qué da |
|---|---|
| **Modelo** | Capas (estructura, raíles, zonas, keep-outs, ejes, aristas), plano de **corte** por X, Y o Z, y el árbol de piezas agrupado por zona, con el volumen libre de cada una. |
| **Datos** | De la pieza seleccionada: cada cota **con su estado y su fuente**, los TBD con a quién hay que pedirlos, y las discrepancias con las dos cifras. Debajo, volumen por zona y totales. |
| **Avisos** | Los quince chequeos de viabilidad y las interferencias, con el mismo criterio que `reports/`: *no comprobable* nunca sale como *ok*. |

Los botones **ISO / Planta / Alzado / Perfil** encuadran las mismas vistas que
`reports/vistas/`. Al pinchar una pieza se resalta y se abre su ficha.

Dos cosas que el visor deja claras a propósito:

- El color dice **de dónde sale el dato**, no qué es la pieza: magenta = falta el
  dato, naranja = dato de un componente parecido, azul = decisión de ACSAR. Solo
  las cotas confirmadas se colorean por categoría.
- La lista **Sin geometría** enseña los componentes que no se pueden dibujar,
  con a quién hay que pedirles la envolvente. Por eso el hueco libre aparece
  marcado como *(techo)*: no es una cifra de diseño.

Mientras el visor está levantado **se regenera solo**. Si editas
`data/*.yaml` o dejas un STEP nuevo en `cad/vendor/`, basta recargar el
navegador: el servidor rehace el GLB y la escena antes de servirlos.

Opciones: `--puerto N` (si está ocupado coge el siguiente libre) y `--sin-abrir`
(no lanza el navegador, solo imprime la dirección).

> El visor necesita conexión a internet la primera vez de cada sesión: carga
> three.js desde un CDN. Todo lo demás —geometría, cotas, informes— sale del
> repositorio.

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

1. Copiar el fichero a la carpeta de su proveedor dentro de `cad/vendor/`,
   p. ej. `cad/vendor/aac_clyde_space/adcs_iadcs400.step`. Hay una carpeta por
   proveedor y `cad/vendor/README.md` dice cuál es cuál.
2. En `data/components.yaml`, en el bloque `forma` de ese componente, añadir el
   bloque `step:`. **Un STEP lleva procedencia, igual que un número**: sin
   `estado` y `fuente`, `clau3d validar` falla.

   ```yaml
     - id: adcs_iadcs400
       forma:
         tipo: step
         step:
           ruta: cad/vendor/aac_clyde_space/adcs_iadcs400.step
           estado: referencia      # 'confirmado' solo con el part number verificado
           fuente: De donde salio el fichero y quien lo paso
           orientacion: [0, 0, 90] # si viene con otros ejes; no cambia ninguna cota
         dimensiones:              # se conserva como referencia de ficha
           valor: [95.4, 95.9, 67.3]
           unidad: mm
           estado: confirmado
           fuente: ...
   ```

3. Anotar su SHA-256 en `cad/vendor/MANIFEST.yaml` y `uv run clau3d todo`.

A partir de ahí la caja desaparece y el modelo usa la geometría real: el
ensamblaje, las interferencias y el volumen se recalculan solos. **No hay que
tocar el código ni la distribución.**

### Reservar el sitio de un STEP que todavía no ha llegado

De los ficheros que faltan ya se sabe **quién los tiene y de qué producto son**,
así que la procedencia se puede escribir por adelantado con `step_esperado`:

```yaml
  - id: telescopio_cassegrain
    forma:
      tipo: cassegrain
      step_esperado:
        ruta: cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step
        pedir_a: Oscar (ACSAR) / Aperture Optical Sciences
        fuente_prevista: Telescopio Cassegrain de Aperture Optical Sciences
      dimensiones:            # la reserva, mientras tanto
        valor: [95.4, 95.4, 200.0]
        estado: supuesto
        ...
```

**Dejar el fichero en esa ruta basta**: sustituye al modelo aproximado sin tocar
el catálogo. Entra como `referencia`, porque que aparezca donde se esperaba no
verifica su part number, y el chequeo `step_de_fabricante` recuerda que hay que
verificarlo. Lo que **no** existe es importar cualquier fichero que se llame
como el componente: un STEP sin procedencia es lo mismo que un número sin
fuente.

Cuando llegue el **chasis 6U del equipo**, sustituye al genérico por el mismo
camino, y además desaparece la hipótesis de espesor de pared (ver más abajo).

## Estructura del repositorio

```
data/components.yaml    dimensiones, masas, consumos, fuentes y estado
data/connections.yaml   conexiones ópticas, RF, datos, potencia y térmicas
data/layout.yaml        distribución dentro del 6U (GENERADO, no editar)
tools/generar_layout.py genera data/layout.yaml desde el catálogo
src/clau3d/             modelo de datos, piezas, ensamblaje, análisis, informes
src/clau3d/optica/      modelo parametrico del telescopio Cassegrain
src/clau3d/visor/       pagina del visor web (clau3d ver)
tests/                  162 tests: datos, formas, supuestos, keep-outs, STEP, visor, telescopio, beacons
cad/vendor/             STEP de fabricante, una carpeta por proveedor (no se tocan)
cad/generated/          STEP generados: uno por pieza, mas el ensamblaje completo
cad/generated/subsistemas/  un STEP por subsistema, con las coordenadas del conjunto
reports/                informes, vistas y components_status.csv (generados)
CLAUDE.md               estado, decisiones y razonamiento de la distribución
```

**Un STEP de subsistema que lleve dentro una pieza dibujada con CAD de
fabricante *contiene* ese CAD**, y este repositorio es público. El sufijo
`_con_cad_de_fabricante` lo pone el exportador mirando lo que ha metido —no una
lista a mano, que se quedaría obsoleta con el siguiente STEP de proveedor— y el
`.gitignore` ignora ese sufijo.

## Estado actual

- **Norma**: CubeSat Design Specification **Rev. 14.1** (2022-02-09), que
  sustituye a la Rev. 13 y a la 6U CDS Rev 1.0. Envolvente 6U del plano
  CDS-14-007: **226.3 × 100.0 × 366.0 mm**, masa máxima 12.00 kg.
- **35 componentes** en el catálogo, **32 con envolvente**. Los tres que no la
  tienen son el UHF de respaldo y el módulo de propulsión (los dos opcionales y
  sin decidir) y los coaxiales RF, que no son un cuerpo sino un keep-out.
- **51 huecos sin aproximación** (`TBD`), **68 números inventados aquí**
  (`supuesto`) y **10 discrepancias** entre fuentes.
- **Distribución confirmada** (2026-09-20): **dos columnas de 3U** a lo largo de
  todo Z — plataforma en −X, payload en +X. `data/layout.yaml` no se escribe a
  mano: lo genera `tools/generar_layout.py` desde el catálogo.
- **28 piezas colocadas** y **0 choques de geometría**. Falta una por colocar
  que no es un olvido: `camara_beacon` **no cabe** en el brazo de los beacons y
  no se dibuja en un sitio inventado. `clau3d informe` devuelve 1 por eso.
- **23 keep-outs**, todos dibujados con números supuestos, porque las tres cotas
  que los dimensionan —radio de curvatura de la fibra, el del coaxial y el
  diámetro de haz— siguen siendo TBD. Hay 15 invasiones, y el informe las
  separa de los choques de geometría porque **no son lo mismo**: dicen "con la
  hipótesis de hoy, aquí no cabe".
- Zona útil interior **221.7 × 95.4 × 361.4 mm = 7.64 L**, de la que quedan
  **2.89 L libres**. Era 5.84 L cuando 19 componentes no ocupaban nada; la
  cifra de antes no era mejor noticia, era menos información.

### Lo que ya aprieta, con números

| Hallazgo | Número |
|---|---|
| La apertura de 90 mm del telescopio contra la altura interior | Deja **2.7 mm hasta la cara plana** y **22.5 mm hasta la esquina**. Por eso el barrilete se modela de sección **cuadrada**: en la cara plana solo caben pared, baffle y holgura, y la celda del primario y los largueros estructurales tienen que ir en las esquinas. El eje óptico no puede ir paralelo a Y. Falta el **contorno exterior del barrilete**. |
| La longitud del telescopio contra los 200 mm reservados | La separación entre vértices del afocal (`f1·(1−1/M)`) son **177.8 mm**, así que quedan **22.2 mm** para los dos mamparos, la celda y los dos espejos, y el modelo cabe por **1.2 mm**. Todos esos espesores están en su cota superior, no elegidos. Con los **~2U de verdad** del brief (227 mm, no 200) habría ~28 mm de margen. Alargar se paga con la bandeja: es decisión de ACSAR. |
| El haz comprimido contra el espejo del FSM | Un haz de *d* mm a 45° deja una huella de *d* × *d*·√2, así que el espejo de **5 mm** del MEMS solo admite **3.54 mm** de haz, o sea magnificación ≥ 25.5. Con el haz supuesto de 10 mm el MEMS **no vale** y habría que ir al piezo (130 g) o subir la magnificación de 9 a 25.5. El diámetro de haz real es TBD, y es **el dato que decide qué FSM se elige**. |
| El **iADCS400** (95.4 mm de lado corto) dentro de los 100 mm exteriores | El espesor de pared no puede pasar de **2.30 mm**. Es la pieza que más aprieta, por delante del contorno PC104 desnudo, que daba 4.91 mm. |
| Moduladores Exail de **grado espacial** | **130 mm** de recorrido recto cada uno, protectores de fibra incluidos. Es **45 mm más largo** que la cifra del encapsulado comercial. En la columna de payload, de 121.7 mm de ancho, **no caben según X**: van según Z. |
| Longitud de la pila PC104 | **305 mm de 361 mm**, con el paso estándar PC/104 de 15.24 mm. Eran 274 hasta descubrir que las ranuras se reservaban con la altura de **ficha** y se dibujaban con el **STEP**: las fichas de AAC no incluyen el conector PC104 pasante, que baja 12.45 mm. El paso **real** del chasis sigue siendo TBD, y ahora el margen es la mitad. |
| El banco óptico, en la línea que va del eje del telescopio a la pared | **7.7 mm** de margen. El FSM tiene que estar sobre el eje óptico porque es el que dobla el haz, y eso deja al colimador y a D1 en fila con él: 74.0 mm para 66.3 mm de piezas. No se ve mirando volúmenes —en el banco sobra hueco— y las dos envolventes que lo llenan son **supuestas**. |
| El brazo de los beacons, en la línea que va de D1 a la pared en Y | **NO CABE por 6.8 mm**, y es lo único que hoy hace fallar `clau3d informe`. Los dos beacons comparten un brazo y dentro de él un segundo dicroico los separa: semi-D1 (11.5) + D2 (23) + cámara (20, ya bajada de 30) = 54.5 mm para 47.7 mm. Con holguras de montaje faltan 16.8, así que la cámara **no está colocada**. Las salidas —plegar el brazo hacia −Z o alargar el banco— se pagan y son decisiones de ACSAR. |
| Bucles de fibra | **No comprobable**: falta el radio mínimo de curvatura. Con el valor supuesto de 30 mm, la bandeja **no cumple** y el colimador no tiene por dónde sacar su latiguillo. Es el dato que más desbloquea del proyecto. |
| La antena de banda S | **No hay cara libre**. +Z la ocupan el telescopio y el star tracker, contra ±X y ±Y la pila deja 2–3 mm, y sus 10 mm de espesor no caben en los 6.5 mm de protrusión que permite la CDS. Acaba en −Z, apuntando al lado contrario que el telescopio: es una decisión de operaciones sin tomar. |

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
- **Cómo cabe el brazo de los beacons.** Los dos beacons comparten un brazo y
  dentro de él un segundo dicroico los separa, y eso **no cabe por 6.8 mm**.
  Plegarlo hacia −Z con un espejo de doblado o alargar el banco: las dos se
  pagan, las dos son de ACSAR, y hasta entonces la cámara no está colocada.
- **El aislamiento de la cámara a 1064 nm.** Es el número que sostiene la
  elección de longitudes de onda (976 arriba, 1064 abajo, por la ceguera del
  silicio a 1064) y hoy no está medido.
- **Si el cuarto puerto de D2 se instrumenta** con un fotodiodo de monitor del
  beacon o se tapa con una trampa de luz. Lo que no es opción es dejarlo
  abierto.
- **Formato PC104 para las tres PCBs propias.** Está propuesto, no confirmado.
- **Número de módulos de batería** y **configuración de paneles PHOTON**.
- **Starbuck-Nano-PLUS frente a Starbuck-Nano**: la ficha describe el PLUS para
  plataformas con **paneles desplegables**, y CLAU parte de paneles de montaje en
  cuerpo. A revisar con AAC.
- **Propulsión**: opcional, prioridad baja, entre 0.1U y 1U.
- **Radio UHF Pulsar-VUTRX**: opcional, solo si queda volumen.

## Lista de pendientes

No hay copia aquí, a propósito: se quedaba obsoleta en cuanto cambiaba el
catálogo, que es cada commit. Lo que hay es dónde está, siempre al día:

| dónde | qué lleva |
|---|---|
| `reports/06_pendientes.md` | Todos los huecos, agrupados **por a quién hay que pedírselos**. Separa los `TBD` (sin aproximación) de los `supuesto` (dibujados, pero inventados), y de cada supuesto dice el valor concreto que hay que sustituir. |
| `reports/components_status.csv` | Una fila por componente, para **actualizar la hoja índice de Drive**: `id_drive`, de dónde sale el sólido que se dibuja, el estado y la fuente de las cotas, los conectores, los keep-outs, qué falta y a quién. Un `id_drive` vacío significa que esa pieza no está en la hoja. |
| `reports/01_viabilidad.md` | Los chequeos, con los `no comprobable` diciendo qué dato les falta. |

Se regeneran con `uv run clau3d informe`.

### Los que más desbloquean

1. **El radio mínimo de curvatura de la fibra** (equipo de payload). 14 de las
   15 invasiones de keep-out del modelo salen de él.
2. **El diámetro del haz comprimido** (equipo de óptica). De él salen la
   magnificación del telescopio y con ella su geometría entera, y decide si el
   FSM puede ser el MEMS de 5 mm o tiene que ser el piezo.
3. **El STEP del telescopio** (Óscar / Aperture Optical Sciences). Hay sitio
   reservado: dejarlo en `cad/vendor/aperture_optical_sciences/telescopio_cassegrain.step`
   basta para que sustituya al modelo paramétrico, sin tocar el catálogo.
4. **El paso de apilamiento real del chasis** (equipo de estructura). El margen
   de la pila se ha quedado en 56 mm.
5. **Las alturas reales de PCB-1, PCB-2 y PCB-3** (equipo de electrónica).
   Ahora se dibujan con 15 mm supuestos.
6. **La decisión sobre el brazo de los beacons** (ACSAR). Es lo único que hoy
   hace que `clau3d informe` devuelva 1.

---

<sub>Los informes de `reports/` y los STEP de `cad/generated/` se generan
automáticamente. No editarlos a mano.</sub>
