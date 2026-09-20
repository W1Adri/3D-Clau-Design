# STEP generados

Generados por `uv run clau3d piezas` y `uv run clau3d ensamblar`.
**No editar a mano**: se sobrescriben.

Se reimportan exactamente igual que los de `cad/vendor/`.

## Que se versiona y que no

Los STEP **por pieza** son de unos 15 KB cada uno y se versionan: son cajas
envolventes generadas desde `data/components.yaml`, no contienen nada de nadie.
`escena.json` (~43 KB) tambien.

El **ensamblaje completo** no. Desde que hay geometria de fabricante dentro,
`clau_6u.step` pesa **175 MB** y `clau_6u.glb` **46 MB**, pero el problema no es
el tamano: es que **contienen el CAD de AAC**. Versionarlos seria redistribuirlo
por la puerta de atras, que es justo lo que evita `cad/vendor/.gitignore`. Se
regeneran cuando hagan falta:

```bash
uv run clau3d ensamblar   # clau_6u.step
uv run clau3d ver         # clau_6u.glb + escena.json
```

Una pieza que pasa de caja envolvente a STEP de fabricante **deja de generarse
aqui**, y `exportar_generados()` borra el fichero que hubiera quedado: si no, el
repositorio seguiria ensenando una caja de una pieza que el modelo ya dibuja con
su geometria real.
