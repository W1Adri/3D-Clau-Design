# STEP de fabricante

Aquí van los STEP de fabricante y el ensamblaje previo del equipo.
**No se modifican**: se importan tal cual. Se versionan en git, para que cada
commit del layout quede ligado al fichero exacto que se usó.

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
| `otros/` | lo que no encaje arriba |

**Nombre del fichero:** el `id` del componente en `data/components.yaml`, o el
nombre del proveedor si aún no sabes a qué componente corresponde. Minúsculas y
guiones bajos, sin espacios ni acentos: `adcs_iadcs400.step`,
`telescopio_cassegrain.step`.

Formatos: `.step` / `.stp`. Si te llega un `.sldprt`, `.ipt` o `.f3d`, pide el
STEP: CadQuery solo lee STEP y no vamos a convertir a ojo.

## Cómo se conecta un STEP al modelo

Añade la línea `step:` en el bloque `forma` del componente en
`data/components.yaml`:

```yaml
  - id: adcs_iadcs400
    forma:
      tipo: step
      step: cad/vendor/aac_clyde_space/adcs_iadcs400.step
```

La ruta es relativa a la raíz del repositorio. A partir de ahí el componente
deja de ser una caja envolvente y pasa a ser el sólido real en **todo**:
ensamblaje, interferencias, volumen, vistas y visor.

Si el fichero no existe, `uv run clau3d validar` falla y lo dice.

## Antes de dar por bueno un STEP

1. `uv run clau3d validar` — que el catálogo siga íntegro.
2. `uv run clau3d ver` — miradlo en el visor: **comprueba el origen y los ejes**.
   El modelo espera cada pieza **centrada en su propio origen**; muchos STEP de
   proveedor vienen con el origen en una esquina o en un punto de montaje, y
   entonces la pieza aparece desplazada. Si pasa eso, dilo en la nota del
   componente en vez de mover números a mano.
3. `uv run clau3d informe` — que no aparezcan interferencias nuevas.

Y revisa las dimensiones: si el STEP contradice las del catálogo, eso es una
**discrepancia entre fuentes**, y va registrada en `components.yaml` con las dos
cifras, no corregida en silencio.
