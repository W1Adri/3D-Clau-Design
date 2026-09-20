"""Modelo 3D parametrico y analisis volumetrico del CubeSat 6U CLAU (ACSAR, EETAC-UPC).

Regla principal del proyecto: ningun numero vive en el codigo. Todas las
dimensiones, masas y consumos salen de ``data/components.yaml``, cada uno con
su fuente y su estado.
"""

from .datamodel import cargar, validar  # noqa: F401

__version__ = "0.1.0"
