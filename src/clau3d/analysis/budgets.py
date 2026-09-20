"""Presupuestos de masa y de potencia, separando lo confirmado de lo que no.

No se rellena ningun hueco: lo que falta se cuenta aparte, como lo que falta.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..datamodel import (
    CONFIRMADO,
    DECISION,
    REFERENCIA,
    SUPUESTO,
    Catalogo,
    Magnitud,
)


@dataclass
class FilaPresupuesto:
    id: str
    nombre: str
    subsistema: str
    unidades: int | None
    valor_unitario: float | None
    total: float | None
    estado: str
    fuente: str | None


@dataclass
class Presupuesto:
    titulo: str
    unidad: str
    filas: list[FilaPresupuesto]
    sin_dato: list[str] = field(default_factory=list)
    limite: float | None = None
    # Las filas cuyo valor se ha inventado este repositorio. Van APARTE de
    # 'filas' y no entran en ningun total: sumar una masa supuesta a una masa de
    # ficha da un numero que no se puede ensenar a nadie. Se listan igual porque
    # saber cuanto pesa lo que falta por saber tambien es informacion.
    supuestas: list[FilaPresupuesto] = field(default_factory=list)

    @property
    def total_supuesto(self) -> float:
        return sum(f.total for f in self.supuestas if f.total is not None)

    def total_por_estado(self) -> dict[str, float]:
        salida: dict[str, float] = {}
        for fila in self.filas:
            if fila.total is None:
                continue
            salida[fila.estado] = salida.get(fila.estado, 0.0) + fila.total
        return salida

    @property
    def total_confirmado(self) -> float:
        return self.total_por_estado().get(CONFIRMADO, 0.0)

    @property
    def total_no_confirmado(self) -> float:
        por_estado = self.total_por_estado()
        return por_estado.get(REFERENCIA, 0.0) + por_estado.get(DECISION, 0.0)

    @property
    def total_contabilizado(self) -> float:
        return sum(self.total_por_estado().values())

    @property
    def completo(self) -> bool:
        return not self.sin_dato


def _fila(componente, magnitud: Magnitud) -> FilaPresupuesto | None:
    if not magnitud.esta_declarada or magnitud.es_tbd:
        return None
    unitario = magnitud.escalar()
    n = componente.n_unidades
    total = None if (unitario is None or n is None) else unitario * n
    return FilaPresupuesto(
        id=componente.id,
        nombre=componente.nombre,
        subsistema=componente.subsistema,
        unidades=n,
        valor_unitario=unitario,
        total=total,
        estado=magnitud.estado,
        fuente=magnitud.fuente,
    )


def masa(catalogo: Catalogo) -> Presupuesto:
    filas: list[FilaPresupuesto] = []
    supuestas: list[FilaPresupuesto] = []
    sin_dato: list[str] = []
    for componente in catalogo.componentes:
        if not componente.cuenta_en_presupuesto:  # alternativa en estudio
            continue
        fila = _fila(componente, componente.masa)
        if fila is None or fila.total is None:
            sin_dato.append(componente.id)
        elif fila.estado == SUPUESTO:
            supuestas.append(fila)
        else:
            filas.append(fila)
    filas.sort(key=lambda f: -(f.total or 0))
    supuestas.sort(key=lambda f: -(f.total or 0))
    return Presupuesto(
        titulo="Masa",
        unidad="g",
        filas=filas,
        sin_dato=sin_dato,
        supuestas=supuestas,
        limite=catalogo.envolvente["masa_maxima"].escalar(),
    )


def potencia(catalogo: Catalogo, pico: bool = False) -> Presupuesto:
    filas: list[FilaPresupuesto] = []
    supuestas: list[FilaPresupuesto] = []
    sin_dato: list[str] = []
    for componente in catalogo.componentes:
        if componente.categoria == "estructura":
            continue
        if not componente.cuenta_en_presupuesto:  # alternativa en estudio
            continue
        magnitud = componente.potencia_pico if pico else componente.potencia_nominal
        if not magnitud.esta_declarada:
            # La pieza no consume (bateria, optica pasiva, estructura) o aun no
            # se sabe si consume. Se distingue del TBD explicito.
            if componente.subsistema in ("bandeja_optica", "terminal_optico") or \
               componente.categoria in ("payload_pcb",):
                sin_dato.append(componente.id)
            continue
        fila = _fila(componente, magnitud)
        if fila is None or fila.total is None:
            sin_dato.append(componente.id)
        elif fila.estado == SUPUESTO:
            supuestas.append(fila)
        else:
            filas.append(fila)
    filas.sort(key=lambda f: -(f.total or 0))
    supuestas.sort(key=lambda f: -(f.total or 0))
    return Presupuesto(
        titulo="Potencia de pico" if pico else "Potencia nominal",
        unidad="W",
        filas=filas,
        sin_dato=sin_dato,
        supuestas=supuestas,
    )


def energia_disponible(catalogo: Catalogo) -> dict:
    """Energia de bateria modelada. Deja claro que N es una hipotesis."""
    bateria = catalogo["bateria_optimus_30"]
    capacidad = bateria.extras.get("capacidad")
    n = bateria.n_unidades
    return {
        "modulos_modelados": n,
        "estado_cantidad": bateria.cantidad.estado,
        "capacidad_por_modulo_Wh": None if capacidad is None else capacidad.escalar(),
        "total_Wh": (
            None
            if (capacidad is None or n is None or capacidad.escalar() is None)
            else capacidad.escalar() * n
        ),
    }
