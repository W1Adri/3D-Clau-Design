"""Modelo parametrico del telescopio Cassegrain.

Dos modulos, a proposito:

* ``parametros``: solo aritmetica. Deriva la configuracion optica del
  catalogo y no importa CadQuery, asi que los chequeos y los tests pueden
  preguntarle sin pagar el coste de OCC.
* ``cassegrain``: la geometria. Construye el solido a partir de lo que
  ``parametros`` derivo, y no decide ningun numero por su cuenta.
"""

from __future__ import annotations

__all__ = ["parametros", "cassegrain"]
