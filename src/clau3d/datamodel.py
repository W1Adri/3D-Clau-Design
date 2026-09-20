"""Carga y validacion del catalogo de datos de CLAU.

La regla principal del proyecto es que ningun numero vive en el codigo: todos
salen de ``data/components.yaml`` y ``data/connections.yaml``. Este modulo es el
unico punto por el que entran, y valida que cada magnitud lleve estado y fuente.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import yaml

# Estados admitidos para cualquier magnitud del catalogo.
CONFIRMADO = "confirmado"
REFERENCIA = "referencia"
DECISION = "decision"
TBD = "TBD"
# "ausente" no es un estado del catalogo: marca un campo que el componente
# simplemente no declara (p. ej. el consumo de una bateria). No es un hueco
# que haya que perseguir, y por eso no entra en la lista de pendientes.
AUSENTE = "ausente"
ESTADOS = (CONFIRMADO, REFERENCIA, DECISION, TBD)

# Magnitudes que TODO componente debe declarar, aunque sea como TBD.
MAGNITUDES_OBLIGATORIAS = ("dimensiones", "masa")

# Los estados que NO son un dato firme del componente elegido.
ESTADOS_NO_FIRMES = (REFERENCIA, DECISION, TBD)

RAIZ = Path(__file__).resolve().parents[2]
DIR_DATOS = RAIZ / "data"
DIR_CAD = RAIZ / "cad"
DIR_INFORMES = RAIZ / "reports"


class ErrorDeDatos(Exception):
    """El catalogo incumple la regla de 'ningun numero inventado'."""


@dataclass(frozen=True)
class Magnitud:
    """Un valor del catalogo con su procedencia.

    ``valor`` es None exactamente cuando el estado es TBD. Nunca se rellena un
    hueco con un valor razonable: un TBD se propaga hasta el informe.
    """

    nombre: str
    valor: Any
    unidad: str | None = None
    estado: str = TBD
    fuente: str | None = None
    nota: str | None = None
    falta: str | None = None
    pedir_a: str | None = None
    alternativas: tuple[dict, ...] = ()
    rango: tuple[float, ...] | None = None

    @property
    def es_tbd(self) -> bool:
        return self.estado == TBD

    @property
    def esta_declarada(self) -> bool:
        """False si el catalogo no menciona esta magnitud para este componente."""
        return self.estado != AUSENTE

    @property
    def es_firme(self) -> bool:
        """True solo si procede de la ficha del componente realmente elegido."""
        return self.estado == CONFIRMADO

    @property
    def hay_discrepancia(self) -> bool:
        return bool(self.alternativas)

    def como_vector(self) -> tuple[float, float, float] | None:
        if self.valor is None:
            return None
        if not isinstance(self.valor, (list, tuple)) or len(self.valor) != 3:
            raise ErrorDeDatos(
                f"{self.nombre}: se esperaba [dx, dy, dz], hay {self.valor!r}"
            )
        return tuple(float(v) for v in self.valor)  # type: ignore[return-value]

    def escalar(self) -> float | None:
        if self.valor is None:
            return None
        if isinstance(self.valor, (list, tuple)):
            raise ErrorDeDatos(f"{self.nombre}: se esperaba un escalar, hay una lista")
        return float(self.valor)

    def __str__(self) -> str:
        if self.es_tbd:
            return "TBD"
        unidad = f" {self.unidad}" if self.unidad else ""
        return f"{self.valor}{unidad}"


def _magnitud(nombre: str, bruto: Any) -> Magnitud:
    """Convierte un bloque del YAML en Magnitud, sin inventar nada."""
    if bruto is None:
        return Magnitud(nombre=nombre, valor=None, estado=AUSENTE)
    if not isinstance(bruto, dict):
        # Un escalar suelto no lleva procedencia: el catalogo no lo permite.
        raise ErrorDeDatos(
            f"{nombre}: valor suelto {bruto!r}. Toda magnitud necesita "
            f"un bloque con valor/unidad/estado/fuente."
        )
    rango = bruto.get("rango")
    return Magnitud(
        nombre=nombre,
        valor=bruto.get("valor"),
        unidad=bruto.get("unidad"),
        estado=bruto.get("estado", TBD),
        fuente=bruto.get("fuente"),
        nota=bruto.get("nota"),
        falta=bruto.get("falta"),
        pedir_a=bruto.get("pedir_a"),
        alternativas=tuple(bruto.get("alternativas") or ()),
        rango=tuple(rango) if rango else None,
    )


@dataclass(frozen=True)
class FuenteStep:
    """Un STEP de fabricante conectado a un componente, con su procedencia.

    Un STEP no es una magnitud: no tiene valor ni unidad. Pero si tiene estado y
    fuente, y por el mismo motivo que los tiene un numero. Un STEP 'referencia'
    es el modelo de un producto parecido, o de uno cuyo part number todavia no se
    ha verificado contra la ficha; dibujarlo como si fuera el bueno seria
    exactamente el error que este catalogo existe para evitar.

    ``orientacion`` son los grados a girar el solido importado alrededor de X, Y
    y Z, en ese orden, ANTES de recentrarlo. Sirve para deshacer el cambio de
    ejes con el que muchos proveedores exportan: no mueve ninguna cota, solo
    lleva la pieza al sistema de ejes que el catalogo declara en 'dimensiones'.

    ``recentrar`` lleva el centro de la caja envolvente al origen. El ensamblaje
    coloca cada pieza por su centro, asi que un STEP con el origen en una esquina
    aparece desplazado media pieza. Se puede desactivar cuando el origen del STEP
    sea el punto de montaje bueno.
    """

    ruta: str
    estado: str
    fuente: str | None = None
    nota: str | None = None
    orientacion: tuple[float, float, float] = (0.0, 0.0, 0.0)
    recentrar: bool = True

    @property
    def girado(self) -> bool:
        return any(abs(a) > 1e-9 for a in self.orientacion)


def _fuente_step(id_componente: str, bruto: Any) -> FuenteStep | None:
    if bruto is None:
        return None
    if not isinstance(bruto, dict):
        raise ErrorDeDatos(
            f"{id_componente}: forma.step es {bruto!r}. Un STEP de fabricante "
            f"necesita un bloque con ruta/estado/fuente, igual que una magnitud."
        )
    try:
        ruta = bruto["ruta"]
    except KeyError as exc:
        raise ErrorDeDatos(f"{id_componente}: forma.step sin 'ruta'") from exc
    orientacion = bruto.get("orientacion") or (0.0, 0.0, 0.0)
    if len(orientacion) != 3:
        raise ErrorDeDatos(
            f"{id_componente}: forma.step.orientacion se esperaba "
            f"[gx, gy, gz], hay {orientacion!r}"
        )
    return FuenteStep(
        ruta=str(ruta),
        estado=bruto.get("estado", TBD),
        fuente=bruto.get("fuente"),
        nota=bruto.get("nota"),
        orientacion=tuple(float(v) for v in orientacion),  # type: ignore[arg-type]
        recentrar=bool(bruto.get("recentrar", True)),
    )


@dataclass
class Componente:
    id: str
    nombre: str
    categoria: str
    subsistema: str
    cantidad: Magnitud
    dimensiones: Magnitud
    step: FuenteStep | None
    masa: Magnitud
    potencia_nominal: Magnitud
    potencia_pico: Magnitud
    opcional: bool
    requiere_vista_exterior: bool
    montado_en: str | None
    alternativa_de: str | None
    nota: str | None
    extras: dict[str, Magnitud] = field(default_factory=dict)
    bruto: dict = field(default_factory=dict, repr=False)

    # ---- geometria -------------------------------------------------
    @property
    def desde_step(self) -> bool:
        """True si el solido viene de un STEP de fabricante en vez de una caja."""
        return self.step is not None

    @property
    def cuenta_en_presupuesto(self) -> bool:
        """False si la pieza no forma parte de la configuracion actual.

        Un componente con ``alternativa_de`` es un candidato en estudio, no algo
        que vaya a bordo: sumarlo a masa, volumen o la pila contaria dos veces lo
        mismo. Se queda en el catalogo porque su geometria SI es un dato, y
        porque la alternativa hay que poder verla.
        """
        return self.alternativa_de is None

    @property
    def step_ruta(self) -> str | None:
        return self.step.ruta if self.step is not None else None

    @property
    def modelable(self) -> bool:
        """Se puede dibujar: o hay STEP, o hay dimensiones no TBD."""
        return self.desde_step or (
            self.dimensiones.esta_declarada and not self.dimensiones.es_tbd
        )

    @property
    def n_unidades(self) -> int | None:
        """Unidades a modelar. Usa cantidad_modelada si la cantidad real es TBD."""
        if not self.cantidad.es_tbd:
            valor = self.cantidad.valor
            return int(valor) if valor is not None else None
        modelada = self.extras.get("cantidad_modelada")
        if modelada is not None and not modelada.es_tbd:
            return int(modelada.valor)
        return None

    def volumen_mm3(self) -> float | None:
        if not self.dimensiones.esta_declarada or self.dimensiones.es_tbd:
            return None
        dims = self.dimensiones.como_vector()
        if dims is None:
            return None
        n = self.n_unidades
        if n is None:
            return None
        return dims[0] * dims[1] * dims[2] * n

    def masa_total_g(self) -> float | None:
        m = self.masa.escalar() if (self.masa.esta_declarada and not self.masa.es_tbd) else None
        n = self.n_unidades
        if m is None or n is None:
            return None
        return m * n

    # ---- procedencia agregada --------------------------------------
    @property
    def estado_geometria(self) -> str:
        """Procedencia de lo que se DIBUJA, que no siempre es 'dimensiones'.

        Con un STEP conectado, el solido del ensamblaje sale del STEP y no de la
        ficha, asi que el estado que cuenta es el del STEP. Si el STEP es de
        referencia, la pieza se dibuja de color referencia aunque la ficha este
        confirmada.
        """
        if self.step is not None:
            return self.step.estado
        return self.dimensiones.estado

    def magnitudes(self) -> Iterator[Magnitud]:
        yield self.cantidad
        yield self.dimensiones
        yield self.masa
        yield self.potencia_nominal
        yield self.potencia_pico
        yield from self.extras.values()


def _componente(bruto: dict) -> Componente:
    forma = bruto.get("forma") or {}
    dims_brutas = forma.get("dimensiones")
    step = _fuente_step(bruto["id"], forma.get("step"))

    # Campos reservados que ya tienen su propio atributo.
    reservados = {
        "id", "nombre", "categoria", "subsistema", "cantidad", "forma",
        "masa", "potencia_nominal", "potencia_pico", "opcional",
        "requiere_vista_exterior", "nota_vista", "montado_en", "nota",
        "prioridad", "alternativa_de",
    }
    extras: dict[str, Magnitud] = {}
    for clave, valor in bruto.items():
        if clave in reservados:
            continue
        if isinstance(valor, dict) and ("valor" in valor or "estado" in valor):
            extras[clave] = _magnitud(f"{bruto['id']}.{clave}", valor)

    cantidad_bruta = bruto.get("cantidad", 1)
    if not isinstance(cantidad_bruta, dict):
        cantidad_bruta = {
            "valor": cantidad_bruta,
            "estado": DECISION,
            "fuente": "Cantidad implicita del catalogo",
        }

    return Componente(
        id=bruto["id"],
        nombre=bruto["nombre"],
        categoria=bruto["categoria"],
        subsistema=bruto.get("subsistema", ""),
        cantidad=_magnitud(f"{bruto['id']}.cantidad", cantidad_bruta),
        dimensiones=_magnitud(f"{bruto['id']}.dimensiones", dims_brutas),
        step=step,
        masa=_magnitud(f"{bruto['id']}.masa", bruto.get("masa")),
        potencia_nominal=_magnitud(
            f"{bruto['id']}.potencia_nominal", bruto.get("potencia_nominal")
        ),
        potencia_pico=_magnitud(
            f"{bruto['id']}.potencia_pico", bruto.get("potencia_pico")
        ),
        opcional=bool(bruto.get("opcional", False)),
        requiere_vista_exterior=bool(bruto.get("requiere_vista_exterior", False)),
        montado_en=bruto.get("montado_en"),
        alternativa_de=bruto.get("alternativa_de"),
        nota=bruto.get("nota"),
        extras=extras,
        bruto=bruto,
    )


@dataclass
class Catalogo:
    meta: dict
    norma: dict
    envolvente: dict[str, Magnitud]
    zona_util: dict[str, Magnitud]
    integracion: dict[str, Magnitud]
    componentes: list[Componente]
    conexiones: dict[str, list[dict]]

    # ---- acceso ----------------------------------------------------
    def __getitem__(self, id_componente: str) -> Componente:
        for c in self.componentes:
            if c.id == id_componente:
                return c
        raise KeyError(id_componente)

    def existe(self, id_componente: str) -> bool:
        return any(c.id == id_componente for c in self.componentes)

    def por_categoria(self, categoria: str) -> list[Componente]:
        return [c for c in self.componentes if c.categoria == categoria]

    def todas_las_conexiones(self) -> Iterator[tuple[str, dict]]:
        for familia, lista in self.conexiones.items():
            if familia == "meta":
                continue
            for conexion in lista:
                yield familia, conexion

    # ---- geometria de la envolvente --------------------------------
    @property
    def dims_exteriores(self) -> tuple[float, float, float]:
        return self.envolvente["dimensiones"].como_vector()  # type: ignore[return-value]

    @property
    def dims_interiores(self) -> tuple[float, float, float]:
        """Zona util interior segun el espesor de pared declarado."""
        t = self.zona_util["espesor_pared"].escalar()
        if t is None:
            raise ErrorDeDatos("espesor_pared es TBD: no hay zona util definida")
        dx, dy, dz = self.dims_exteriores
        return (dx - 2 * t, dy - 2 * t, dz - 2 * t)

    @property
    def volumen_exterior_mm3(self) -> float:
        return math.prod(self.dims_exteriores)

    @property
    def volumen_interior_mm3(self) -> float:
        return math.prod(self.dims_interiores)

    # ---- pendientes ------------------------------------------------
    def pendientes(self) -> list[dict]:
        """Todos los TBD del catalogo, con que falta y a quien pedirlo."""
        filas: list[dict] = []
        globales = {
            **{f"envolvente_6u.{k}": v for k, v in self.envolvente.items()},
            **{f"zona_util_interior.{k}": v for k, v in self.zona_util.items()},
            **{f"integracion.{k}": v for k, v in self.integracion.items()},
        }
        for clave, magnitud in globales.items():
            if magnitud.es_tbd:
                filas.append(
                    {
                        "componente": clave.split(".")[0],
                        "magnitud": clave,
                        "falta": magnitud.falta or "(sin describir)",
                        "pedir_a": magnitud.pedir_a or "(sin asignar)",
                    }
                )
        for c in self.componentes:
            for magnitud in c.magnitudes():
                if magnitud.es_tbd:
                    filas.append(
                        {
                            "componente": c.id,
                            "magnitud": magnitud.nombre,
                            "falta": magnitud.falta or "(sin describir)",
                            "pedir_a": magnitud.pedir_a or "(sin asignar)",
                        }
                    )
        return filas

    def discrepancias(self) -> list[dict]:
        """Magnitudes con cifras distintas entre fuentes. No se elige ninguna."""
        filas: list[dict] = []
        todas = list(self.envolvente.values()) + list(self.zona_util.values())
        todas += list(self.integracion.values())
        for c in self.componentes:
            todas += list(c.magnitudes())
        for magnitud in todas:
            if magnitud.hay_discrepancia:
                filas.append(
                    {
                        "magnitud": magnitud.nombre,
                        "valor_usado": magnitud.valor,
                        "fuente_usada": magnitud.fuente,
                        "alternativas": magnitud.alternativas,
                    }
                )
        return filas


def _bloque_magnitudes(bruto: dict, prefijo: str) -> dict[str, Magnitud]:
    salida: dict[str, Magnitud] = {}
    for clave, valor in (bruto or {}).items():
        if isinstance(valor, dict) and ("valor" in valor or "estado" in valor):
            salida[clave] = _magnitud(f"{prefijo}.{clave}", valor)
        elif isinstance(valor, dict):
            # Un nivel mas de anidamiento, p. ej. integracion.pila_pc104.*
            for sub, subvalor in valor.items():
                if isinstance(subvalor, dict):
                    salida[f"{clave}.{sub}"] = _magnitud(
                        f"{prefijo}.{clave}.{sub}", subvalor
                    )
    return salida


def cargar(dir_datos: Path | None = None) -> Catalogo:
    """Carga el catalogo completo desde ``data/``."""
    dir_datos = dir_datos or DIR_DATOS
    componentes_brutos = yaml.safe_load(
        (dir_datos / "components.yaml").read_text(encoding="utf-8")
    )
    conexiones = yaml.safe_load(
        (dir_datos / "connections.yaml").read_text(encoding="utf-8")
    )

    catalogo = Catalogo(
        meta=componentes_brutos.get("meta", {}),
        norma=componentes_brutos.get("norma", {}),
        envolvente=_bloque_magnitudes(
            componentes_brutos.get("envolvente_6u", {}), "envolvente_6u"
        ),
        zona_util=_bloque_magnitudes(
            componentes_brutos.get("zona_util_interior", {}), "zona_util_interior"
        ),
        integracion=_bloque_magnitudes(
            componentes_brutos.get("integracion", {}), "integracion"
        ),
        componentes=[_componente(c) for c in componentes_brutos.get("componentes", [])],
        conexiones=conexiones,
    )
    return catalogo


def validar(catalogo: Catalogo) -> list[str]:
    """Comprueba la integridad del catalogo. Devuelve la lista de problemas."""
    problemas: list[str] = []

    vistos: set[str] = set()
    for c in catalogo.componentes:
        if c.id in vistos:
            problemas.append(f"id duplicado: {c.id}")
        vistos.add(c.id)
        if c.montado_en and not catalogo.existe(c.montado_en):
            problemas.append(
                f"{c.id}: montado_en apunta a '{c.montado_en}', que no existe"
            )
        if c.alternativa_de:
            if c.alternativa_de == c.id:
                problemas.append(f"{c.id}: alternativa_de apunta a si mismo")
            elif not catalogo.existe(c.alternativa_de):
                problemas.append(
                    f"{c.id}: alternativa_de apunta a '{c.alternativa_de}', "
                    f"que no existe"
                )

    todas: list[Magnitud] = []
    todas += list(catalogo.envolvente.values())
    todas += list(catalogo.zona_util.values())
    todas += list(catalogo.integracion.values())
    for c in catalogo.componentes:
        todas += list(c.magnitudes())

    for m in todas:
        if m.estado == AUSENTE:
            continue
        if m.estado not in ESTADOS:
            problemas.append(
                f"{m.nombre}: estado '{m.estado}' no valido (admitidos: {ESTADOS})"
            )
            continue
        if m.estado == TBD:
            if m.valor is not None:
                problemas.append(
                    f"{m.nombre}: estado TBD pero tiene valor {m.valor!r}. "
                    f"Un hueco no se rellena."
                )
            if not m.falta:
                problemas.append(f"{m.nombre}: TBD sin decir que falta")
            if not m.pedir_a:
                problemas.append(f"{m.nombre}: TBD sin decir a quien pedirlo")
        else:
            if m.valor is None:
                problemas.append(
                    f"{m.nombre}: estado '{m.estado}' pero sin valor. "
                    f"Si falta el dato, el estado es TBD."
                )
            if not m.fuente:
                problemas.append(f"{m.nombre}: estado '{m.estado}' sin fuente")

    # Toda pieza declara dimensiones y masa, aunque sean TBD: si no, el hueco
    # desaparece del informe en vez de aparecer como pendiente.
    for c in catalogo.componentes:
        for campo in MAGNITUDES_OBLIGATORIAS:
            magnitud = getattr(c, campo)
            if not magnitud.esta_declarada:
                problemas.append(
                    f"{c.id}: no declara '{campo}'. Si el dato falta, "
                    f"declararlo como TBD con falta/pedir_a."
                )

    # Las dimensiones que se van a dibujar tienen que ser un vector positivo.
    for c in catalogo.componentes:
        if c.dimensiones.es_tbd or not c.dimensiones.esta_declarada or c.desde_step:
            continue
        try:
            dims = c.dimensiones.como_vector()
        except ErrorDeDatos as exc:
            problemas.append(str(exc))
            continue
        if dims and any(v <= 0 for v in dims):
            problemas.append(f"{c.id}: dimensiones no positivas {dims}")

    # Un STEP de fabricante lleva procedencia, igual que un numero.
    for c in catalogo.componentes:
        if c.step is None:
            continue
        if c.step.estado not in ESTADOS:
            problemas.append(
                f"{c.id}.step: estado '{c.step.estado}' no valido "
                f"(admitidos: {ESTADOS})"
            )
        elif c.step.estado == TBD:
            problemas.append(
                f"{c.id}.step: estado TBD con un fichero conectado. Un STEP que "
                f"existe no es un hueco; si no se sabe de que producto es, el "
                f"estado es '{REFERENCIA}'."
            )
        if not c.step.fuente:
            problemas.append(
                f"{c.id}.step: sin fuente. Hay que decir de donde salio el fichero."
            )

    # Toda conexion apunta a componentes que existen.
    for familia, conexion in catalogo.todas_las_conexiones():
        for extremo in ("desde", "hasta"):
            destino = conexion.get(extremo)
            if destino is None or destino == "EXTERIOR":
                continue
            if not catalogo.existe(destino):
                problemas.append(
                    f"conexion {conexion.get('id')} ({familia}): "
                    f"{extremo}='{destino}' no existe en components.yaml"
                )

    return problemas
