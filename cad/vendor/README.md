# CAD de fabricante

Aquí van los STEP de fabricante y el ensamblaje previo del equipo.
**No se modifican**: se importan tal cual.

## Estos ficheros NO están en git

El repositorio es público y las condiciones de uso de los CAD de AAC y de la
mayoría de proveedores no permiten redistribuirlos, o no se han revisado. Hasta
aclararlo, ningún `.step`, `.stp`, `.sldprt` ni `.zip` de esta carpeta sube a
GitHub: están en `.gitignore`.

Lo que **sí** se versiona es [`MANIFEST.yaml`](MANIFEST.yaml): la huella SHA-256
de cada fichero, su tamaño, el producto que declara y de dónde salió. Así cada
commit del layout sigue quedando ligado al fichero exacto que se usó, que era el
objetivo, sin publicar el CAD.

**Copia de referencia: carpeta de Drive `MySatNotes/components`.** (El enlace
exacto está pendiente; ver el bloque `origen` del manifiesto.)

### Clonar el repositorio sin los CAD

Funciona todo. Los componentes con un STEP conectado que no esté en disco se
dibujan con su **caja envolvente de ficha**, que es el comportamiento que había
antes de que llegara ningún STEP. El chequeo `step_de_fabricante` del informe de
viabilidad dice cuáles faltan, pero **no falla por ello**. Lo que sí es un fallo
crítico es tener un fichero cuya huella no coincide con la declarada: entonces el
modelo se ha dibujado con una geometría distinta de la que el manifiesto dice.

```bash
uv run clau3d validar   # integridad del catalogo
uv run clau3d informe   # incluye el chequeo contra el manifiesto
```

## Dónde dejar cada fichero

Una carpeta por proveedor. Si el tuyo no está, crea la carpeta.

| carpeta | qué va dentro |
|---|---|
| `aac_clyde_space/` | iADCS400, Kryten-M3-PLUS, Starbuck-Nano-PLUS, Optimus-30, Quasar-STRX, Quasar-WSANT, Pulsar-VUTRX, PHOTON-SIDE |
| `aperture_optical_sciences/` | telescopio Cassegrain (el que espera Óscar) |
| `exail/` | MXER-LN-10, MPZ-LN-10 |
| `id_quantique/` | IDQ20MC1-S3 |
| `gooch_housego/` | láser DFB 1550 nm |
| `estructura/` | chasis 6U del equipo de estructura |
| `descartados/` | lo que se estudió y ya no va. No se conecta a ningún componente |
| `otros/` | lo que no encaje arriba |

**Nombre del fichero:** el `id` del componente en `data/components.yaml`, o el
producto que declara el STEP si aún no sabes a qué componente corresponde.
Minúsculas y guiones bajos, sin espacios ni acentos: `adcs_iadcs400.step`,
`telescopio_cassegrain.step`.

Formatos: `.step` / `.stp`. **Si te llega un `.sldprt`, un `.sldasm`, un `.ipt` o
un `.f3d`, pide el STEP.** No es pereza: el formato nativo de SolidWorks 2015+ es
un contenedor propietario que ni CadQuery ni FreeCAD abren, y no hay conversor
libre. Pide **STEP AP214 o AP242**.

## Cómo se conecta un STEP al modelo

Añade el bloque `step:` dentro de `forma` en `data/components.yaml`:

```yaml
  - id: obc_kryten_m3_plus
    forma:
      tipo: step
      step:
        ruta: cad/vendor/aac_clyde_space/obc_3d_25_02929.step
        estado: referencia          # confirmado | referencia | decision
        fuente: >-
          De donde salio el fichero y que producto declara.
        orientacion: [0, 0, 90]     # opcional, grados sobre X, Y, Z
        recentrar: true             # opcional, por defecto true
        nota: >-
          Por que el estado es ese, y que se sabe y que no.
```

La ruta es relativa a la raíz del repositorio. A partir de ahí el componente
deja de ser una caja envolvente y pasa a ser el sólido real en **todo**:
ensamblaje, interferencias, volumen, vistas y visor.

**Un STEP lleva procedencia, igual que un número.** `estado` y `fuente` son
obligatorios, y `uv run clau3d validar` falla si no están. Un STEP `referencia`
es el modelo de un producto parecido, o de uno cuyo part number todavía no se ha
verificado contra la ficha; la pieza se dibuja en naranja y el informe lo dice.
Dibujar un STEP de referencia como si fuera el bueno es exactamente el error que
este catálogo existe para evitar.

Y acuérdate de **añadir la entrada al manifiesto**, con
`sha256sum` y `stat -c %s`. Hay un test que comprueba que no queda ningún CAD en
`cad/vendor/` sin declarar.

### Las dos correcciones que el modelo aplica solo

No hace falta tocar el fichero del proveedor ni mover coordenadas a mano:

- **`recentrar`** lleva el centro de la caja envolvente al origen. El ensamblaje
  coloca cada pieza por su centro, así que un STEP con el origen en una esquina
  aparecería desplazado media pieza. Se puede poner a `false` cuando el origen
  del STEP ya sea el punto de montaje bueno.
- **`orientacion`** gira el sólido importado alrededor de X, Y y Z, en ese orden,
  hasta los ejes que el catálogo declara en `dimensiones`. **No cambia ninguna
  cota**, y hay un test que lo comprueba. Los dos casos reales de este
  repositorio: las tarjetas PC104 de AAC llegan con X e Y intercambiados
  (`[0, 0, 90]`), y el iADCS4-20 llega con el eje de apilamiento por Y en vez de
  por Z (`[90, 0, 0]`).

## Antes de dar por bueno un STEP

1. `uv run clau3d validar` — que el catálogo siga íntegro.
2. `uv run clau3d ver` — miradlo en el visor: **comprobad el origen y los ejes**.
   Si la pieza sale torcida o desplazada, es `orientacion` o `recentrar`, no una
   coordenada del layout.
3. `uv run clau3d informe` — que no aparezcan interferencias nuevas.

Y revisad las dimensiones: si el STEP contradice las del catálogo, eso es una
**discrepancia entre fuentes**, y va registrada en `components.yaml` con las dos
cifras en `alternativas`, no corregida en silencio. Las tarjetas AAC llevan tres
cifras de altura cada una: la de ficha, la del STEP sin el conector PC104 y la
del STEP entero.

## Dos cosas que cuestan tiempo

- **Importar un STEP grande es lento.** El del iADCS4-20 tarda del orden de tres
  minutos. Se cachea en BREP bajo `.cache/step/` y a partir de ahí se lee en
  menos de un segundo. La caché se rehace sola cuando cambia el fichero; no hay
  que borrarla nunca a mano.
- **Una caja envolvente puede salir infinita.** `BoundingBox()` sobre el compound
  de un STEP grande puede devolver coordenadas de 10^97 mm porque hay una entidad
  degenerada entre miles. `parts.caja_de_solidos()` la calcula **sólido a
  sólido** y rechaza lo que salga absurdo. Si no, el prefiltro de interferencias
  daría que todo solapa con todo y el informe dejaría de significar nada.
