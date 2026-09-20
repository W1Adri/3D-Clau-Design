import pytest

from clau3d import assembly
from clau3d.datamodel import cargar


@pytest.fixture(scope="session")
def catalogo():
    return cargar()


@pytest.fixture(scope="session")
def layout():
    return assembly.cargar_layout()


@pytest.fixture(scope="session")
def piezas(catalogo, layout):
    return assembly.construir(catalogo, layout)
