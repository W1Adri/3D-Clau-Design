# STEP de fabricante

Aquí van los STEP de fabricante y el ensamblaje previo del equipo.
**No se modifican**: se importan tal cual.

Para que un componente use uno de estos ficheros en vez de su caja envolvente,
añade la línea `step:` en su bloque `forma` de `data/components.yaml`:

```yaml
  - id: adcs_iadcs400
    forma:
      tipo: step
      step: cad/vendor/iadcs400.step
```

La ruta es relativa a la raíz del repositorio. Si el fichero no existe,
`uv run clau3d validar` falla y lo dice.
