# Descartados

CAD de arquitecturas o productos que se estudiaron y **ya no van**. Nada de aquí
se conecta a `data/components.yaml` ni entra en el ensamblaje.

Se guardan por un solo motivo: que dentro de seis meses nadie tenga que adivinar
por qué había ese fichero en una entrega. La huella y el motivo están en
`cad/vendor/MANIFEST.yaml`, que sí se versiona; los ficheros no.

| fichero | qué era | por qué está aquí |
|---|---|---|
| `cubecat_terminal_optico.stp` | Terminal láser **CubeCAT** de AAC Hyperion (`CubeCAT_IF_20230214`), un cubo integrado de 97.6 × 102.6 × 97.6 mm | Es la arquitectura anterior al **2026-09-19**, que resolvía telescopio, banco y PAT de una pieza. CLAU los separa: Cassegrain de Aperture Optical Sciences, banco óptico y bandeja de fibra. Llegó en el zip `Preliminar viability model` con el nombre `Modulo_optico_clasico_y_PAT_integrado.stp`. |
