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
# "supuesto" es un numero que NO viene de ninguna fuente: se lo ha inventado
# este repositorio para poder dibujar y colocar una pieza cuya envolvente real
# todavia no se conoce. Existe porque un modelo con 19 huecos no se puede
# comprobar contra nada, y reservar un volumen aproximado es mas util que no
# reservar ninguno. No es un dato, y el catalogo no deja que lo parezca:
#
#   - Exige 'fuente', igual que los demas, pero ahi va el RAZONAMIENTO del que
#     sale el numero, no una ficha. Y exige ademas 'falta' y 'pedir_a', igual
#     que un TBD, porque el dato de verdad sigue sin estar.
#   - No suma en los presupuestos de masa ni de potencia: se cuenta aparte.
#   - Sale en la lista de pendientes junto a los TBD.
#   - Se dibuja en su propio color, distinto del de 'referencia', que SI es la
#     cifra de la ficha de un producto real aunque no sea el elegido.
#
# La diferencia con TBD esta solo en si la pieza se puede dibujar. Un TBD no
# tiene ni una aproximacion defendible; un supuesto, si.
SUPUESTO = "supuesto"
TBD = "TBD"
# "ausente" no es un estado del catalogo: marca un campo que el componente
# simplemente no declara (p. ej. el consumo de una bateria). No es un hueco
# que haya que perseguir, y por eso no entra en la lista de pendientes.
AUSENTE = "ausente"
ESTADOS = (CONFIRMADO, REFERENCIA, DECISION, SUPUESTO, TBD)

# Magnitudes que TODO componente debe declarar, aunque sea como TBD.
MAGNITUDES_OBLIGATORIAS = ("dimensiones", "masa")

# Los estados que NO son un dato firme del componente elegido.
ESTADOS_NO_FIRMES = (REFERENCIA, DECISION, SUPUESTO, TBD)

# Los estados que dejan un hueco por rellenar, y que por tanto obligan a decir
# que falta y a quien pedirselo.
ESTADOS_CON_HUECO = (SUPUESTO, TBD)

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
    hueco con un valor razonable *en silencio*: un TBD se propaga hasta el
    informe. Cuando hace falta un numero con el que dibujar y no hay fuente
    ninguna, el estado es SUPUESTO, que obliga a declarar el razonamiento en
    'fuente' y a seguir diciendo que falta y a quien pedirlo.
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
    def es_supuesto(self) -> bool:
        """Numero inventado por este repositorio para poder dibujar la pieza."""
        return self.estado == SUPUESTO

    @property
    def deja_hueco(self) -> bool:
        """El dato de verdad sigue faltando, haya o no un valor con el que dibujar."""
        return self.estado in ESTADOS_CON_HUECO

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
        # Un supuesto no se imprime nunca pelado: alla donde salga el numero
        # sale tambien que es inventado.
        sufijo = " (SUPUESTO)" if self.es_supuesto else ""
        return f"{self.valor}{unidad}{sufijo}"


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


EJES = ("X", "Y", "Z")
CARAS = ("+X", "-X", "+Y", "-Y", "+Z", "-Z")


@dataclass(frozen=True)
class Conector:
    """Un conector que sobresale de la envolvente del cuerpo.

    El cuerpo de una pieza de fibra no es lo que decide si cabe: lo que decide
    es por donde sale el cable. El conector RF del modulador Exail mide
    6.1 x 10 mm y sobresale lateralmente; esos 10 mm son los que obligan a
    tumbar el modulador para que salgan hacia +-Y, donde sobra sitio, y no
    hacia la franja, que tiene 26.3 mm para dos moduladores.

    Se pega a una cara de la envolvente del cuerpo y sobresale hacia fuera, asi
    que la caja envolvente de la pieza CRECE con el. Eso es lo que se quiere:
    el analisis de interferencias tiene que ver el conector.
    """

    id: str
    tipo: str                      # coaxial | fibra | electrico | optico | termico
    cara: str                      # +X, -X, +Y, ...
    dimensiones: Magnitud
    desplazamiento: tuple[float, float] = (0.0, 0.0)
    nota: str | None = None


@dataclass(frozen=True)
class Montaje:
    """Origen y ejes de la pieza, iguales los dibuje una caja o un STEP.

    El punto de esta declaracion es que al dejar el STEP del fabricante en su
    sitio sustituya al modelo aproximado SIN mover nada del layout. Para eso las
    dos geometrias tienen que compartir dos cosas:

    * ``cara``: con que cara se atornilla la pieza. Fija su orientacion.
    * ``eje``: por donde entra y sale la senal -- el eje de fibra en la bandeja,
      el eje optico en el banco. Es lo que hay que alinear con el vecino.

    Ninguna de las dos es geometria: son la declaracion contra la que se
    comprueba el ``forma.step.orientacion`` de un STEP nuevo. Un STEP que llegue
    con otros ejes se gira hasta estos, y si no se puede, se ve.
    """

    cara: str | None = None
    eje: str | None = None
    tipo_eje: str | None = None    # fibra | optico
    nota: str | None = None


@dataclass(frozen=True)
class StepEsperado:
    """Donde caera el STEP que todavia no ha llegado, y de quien viene.

    Un STEP entra al modelo solo con procedencia declarada. Pero esa
    procedencia se puede declarar ANTES de tener el fichero: de los STEP que
    faltan ya se sabe quien los tiene y de que producto son. Declarandolo aqui,
    dejar el fichero en la ruta indicada basta para que el modelo lo dibuje, sin
    editar el catalogo y sin que ningun STEP anonimo se cuele.

    Se conecta siempre como 'referencia', nunca como 'confirmado': que el
    fichero haya aparecido donde se esperaba no verifica su part number.
    """

    ruta: str
    pedir_a: str
    fuente_prevista: str
    orientacion: tuple[float, float, float] = (0.0, 0.0, 0.0)
    recentrar: bool = True
    nota: str | None = None


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


def _conectores(id_componente: str, bruto: Any) -> tuple[Conector, ...]:
    if not bruto:
        return ()
    salida: list[Conector] = []
    for i, crudo in enumerate(bruto):
        cid = crudo.get("id") or f"conector_{i + 1}"
        cara = crudo.get("cara")
        if cara not in CARAS:
            raise ErrorDeDatos(
                f"{id_componente}.{cid}: cara '{cara}' no valida "
                f"(admitidas: {CARAS})"
            )
        desplazamiento = crudo.get("desplazamiento") or (0.0, 0.0)
        salida.append(
            Conector(
                id=cid,
                tipo=crudo.get("tipo", "generico"),
                cara=cara,
                dimensiones=_magnitud(
                    f"{id_componente}.{cid}.dimensiones", crudo.get("dimensiones")
                ),
                desplazamiento=tuple(float(v) for v in desplazamiento),  # type: ignore[arg-type]
                nota=crudo.get("nota"),
            )
        )
    return tuple(salida)


def _montaje(id_componente: str, bruto: Any) -> Montaje | None:
    if not bruto:
        return None
    cara = bruto.get("cara")
    eje = bruto.get("eje")
    if cara is not None and cara not in CARAS:
        raise ErrorDeDatos(
            f"{id_componente}.montaje: cara '{cara}' no valida (admitidas: {CARAS})"
        )
    if eje is not None and eje not in EJES:
        raise ErrorDeDatos(
            f"{id_componente}.montaje: eje '{eje}' no valido (admitidos: {EJES})"
        )
    return Montaje(
        cara=cara, eje=eje, tipo_eje=bruto.get("tipo_eje"), nota=bruto.get("nota")
    )


def _step_esperado(id_componente: str, bruto: Any) -> StepEsperado | None:
    if not bruto:
        return None
    for obligatorio in ("ruta", "pedir_a", "fuente_prevista"):
        if not bruto.get(obligatorio):
            raise ErrorDeDatos(
                f"{id_componente}.forma.step_esperado: sin '{obligatorio}'. Un "
                f"STEP que se conecta solo necesita su procedencia declarada de "
                f"antemano, o seria un fichero anonimo entrando al modelo."
            )
    orientacion = bruto.get("orientacion") or (0.0, 0.0, 0.0)
    if len(orientacion) != 3:
        raise ErrorDeDatos(
            f"{id_componente}.forma.step_esperado.orientacion: se esperaba "
            f"[gx, gy, gz], hay {orientacion!r}"
        )
    return StepEsperado(
        ruta=str(bruto["ruta"]),
        pedir_a=str(bruto["pedir_a"]),
        fuente_prevista=str(bruto["fuente_prevista"]),
        orientacion=tuple(float(v) for v in orientacion),  # type: ignore[arg-type]
        recentrar=bool(bruto.get("recentrar", True)),
        nota=bruto.get("nota"),
    )


@dataclass
class Componente:
    id: str
    nombre: str
    categoria: str
    subsistema: str
    # Identificador de la hoja indice de Drive (OPT-01, PLAT-04, ELEC-02...).
    # No sustituye al 'id': el id es legible y dice que es la pieza, y el de
    # Drive dice en que fila de la hoja esta. Los dos tienen que existir para
    # poder actualizar la hoja desde reports/components_status.csv sin cruzar
    # nombres a mano.
    id_drive: str | None
    # Fabricante y part number del producto elegido o candidato, tal cual se
    # pide. Cuando no hay candidato, None: escribir uno seria inventarlo.
    referencia_comercial: str | None
    cantidad: Magnitud
    dimensiones: Magnitud
    tipo_forma: str
    eje_revolucion: str | None
    conectores: tuple[Conector, ...]
    montaje: Montaje | None
    step: FuenteStep | None
    step_esperado: StepEsperado | None
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
        # Las cotas de los conectores cuentan como cualquier otra: un conector
        # sin medidas no se dibuja, y tiene que salir en la lista de pendientes
        # en vez de desaparecer.
        for conector in self.conectores:
            yield conector.dimensiones


TIPOS_DE_FORMA = ("caja", "cilindro", "step")


def _componente(bruto: dict) -> Componente:
    cid = bruto["id"]
    forma = bruto.get("forma") or {}
    dims_brutas = forma.get("dimensiones")
    step = _fuente_step(cid, forma.get("step"))
    tipo_forma = forma.get("tipo", "caja")
    if tipo_forma not in TIPOS_DE_FORMA:
        raise ErrorDeDatos(
            f"{cid}: forma.tipo '{tipo_forma}' no valido "
            f"(admitidos: {TIPOS_DE_FORMA})"
        )
    eje = forma.get("eje")
    if eje is not None and eje not in EJES:
        raise ErrorDeDatos(f"{cid}: forma.eje '{eje}' no valido (admitidos: {EJES})")

    # Campos reservados que ya tienen su propio atributo.
    reservados = {
        "id", "id_drive", "referencia_comercial", "nombre", "categoria",
        "subsistema", "cantidad", "forma",
        "masa", "potencia_nominal", "potencia_pico", "opcional",
        "requiere_vista_exterior", "nota_vista", "montado_en", "nota",
        "prioridad", "alternativa_de", "montaje",
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
        id_drive=bruto.get("id_drive"),
        referencia_comercial=bruto.get("referencia_comercial"),
        cantidad=_magnitud(f"{bruto['id']}.cantidad", cantidad_bruta),
        dimensiones=_magnitud(f"{cid}.dimensiones", dims_brutas),
        tipo_forma=tipo_forma,
        eje_revolucion=eje,
        conectores=_conectores(cid, forma.get("conectores")),
        montaje=_montaje(cid, bruto.get("montaje")),
        step=step,
        step_esperado=_step_esperado(cid, forma.get("step_esperado")),
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
        """Todo hueco del catalogo, con que falta y a quien pedirlo.

        Incluye los TBD y tambien los SUPUESTO: que se haya inventado un numero
        para poder dibujar la pieza no cierra el hueco. La fila lleva su
        'estado' para que el informe pueda separarlos.
        """
        filas: list[dict] = []
        globales = {
            **{f"envolvente_6u.{k}": v for k, v in self.envolvente.items()},
            **{f"zona_util_interior.{k}": v for k, v in self.zona_util.items()},
            **{f"integracion.{k}": v for k, v in self.integracion.items()},
        }

        def _fila(componente: str, magnitud: Magnitud, nombre: str) -> dict:
            return {
                "componente": componente,
                "magnitud": nombre,
                "estado": magnitud.estado,
                "valor_modelado": magnitud.valor if magnitud.es_supuesto else None,
                "falta": magnitud.falta or "(sin describir)",
                "pedir_a": magnitud.pedir_a or "(sin asignar)",
            }

        for clave, magnitud in globales.items():
            if magnitud.deja_hueco:
                filas.append(_fila(clave.split(".")[0], magnitud, clave))
        for c in self.componentes:
            for magnitud in c.magnitudes():
                if magnitud.deja_hueco:
                    filas.append(_fila(c.id, magnitud, magnitud.nombre))
        return filas

    def supuestos(self) -> list[dict]:
        """Solo los numeros inventados por este repositorio, para sustituirlos."""
        return [f for f in self.pendientes() if f["estado"] == SUPUESTO]

    def tbd(self) -> list[dict]:
        """Solo los huecos sin ninguna aproximacion: no se pueden ni dibujar."""
        return [f for f in self.pendientes() if f["estado"] == TBD]

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
    vistos_drive: dict[str, str] = {}
    for c in catalogo.componentes:
        if c.id in vistos:
            problemas.append(f"id duplicado: {c.id}")
        vistos.add(c.id)
        if c.id_drive is not None:
            # La hoja de Drive es la lista maestra del equipo. Dos piezas con el
            # mismo identificador ahi significan que reports/components_status.csv
            # pisaria una fila con la otra al actualizarla.
            if c.id_drive in vistos_drive:
                problemas.append(
                    f"{c.id}: id_drive '{c.id_drive}' ya lo usa "
                    f"'{vistos_drive[c.id_drive]}'"
                )
            vistos_drive[c.id_drive] = c.id
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
                    f"Un hueco no se rellena. Si ese numero es una aproximacion "
                    f"defendible con la que dibujar, el estado es "
                    f"'{SUPUESTO}', que ademas exige decir de donde sale."
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
            # Un supuesto lleva la carga de los dos mundos: el razonamiento del
            # que sale el numero Y el hueco que sigue abierto. Sin 'falta' y
            # 'pedir_a' se convertiria en un dato mas con el paso del tiempo,
            # que es exactamente lo que este catalogo existe para impedir.
            if m.estado == SUPUESTO:
                if not m.falta:
                    problemas.append(
                        f"{m.nombre}: {SUPUESTO} sin decir que falta. Un numero "
                        f"inventado no cierra el hueco, solo permite dibujar."
                    )
                if not m.pedir_a:
                    problemas.append(
                        f"{m.nombre}: {SUPUESTO} sin decir a quien pedir el dato real"
                    )

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

    # Un cilindro se declara con su caja envolvente y su eje de revolucion. Las
    # dos cotas que no son el eje son el diametro, asi que tienen que coincidir:
    # si no, es una cota mal copiada, no una pieza.
    for c in catalogo.componentes:
        if c.tipo_forma != "cilindro":
            continue
        if c.eje_revolucion is None:
            problemas.append(
                f"{c.id}: forma.tipo es cilindro pero no dice 'eje'. Sin el no "
                f"se sabe cual de las tres cotas es la longitud."
            )
            continue
        if c.dimensiones.es_tbd or not c.dimensiones.esta_declarada:
            continue
        dims = c.dimensiones.como_vector()
        if dims is None:
            continue
        indice = EJES.index(c.eje_revolucion)
        seccion = [d for i, d in enumerate(dims) if i != indice]
        if abs(seccion[0] - seccion[1]) > 1e-6:
            problemas.append(
                f"{c.id}: cilindro de eje {c.eje_revolucion} con seccion "
                f"{seccion[0]} x {seccion[1]} mm. Las dos cotas que no son el "
                f"eje son el diametro y tienen que ser iguales."
            )

    # Un conector sobresale de la envolvente del cuerpo, asi que sin cuerpo no
    # hay donde pegarlo.
    for c in catalogo.componentes:
        if not c.conectores:
            continue
        if c.dimensiones.es_tbd or not c.dimensiones.esta_declarada:
            problemas.append(
                f"{c.id}: declara conectores pero su envolvente es "
                f"{c.dimensiones.estado}. Un conector se pega a una cara del "
                f"cuerpo; sin cuerpo no hay cara."
            )

    # 'step' y 'step_esperado' son la misma cosa en dos momentos distintos:
    # declarar los dos deja sin saber cual manda.
    for c in catalogo.componentes:
        if c.step is not None and c.step_esperado is not None:
            problemas.append(
                f"{c.id}: declara 'forma.step' y 'forma.step_esperado' a la vez. "
                f"El segundo es para cuando el fichero todavia no ha llegado; "
                f"cuando llega y se verifica, se sustituye por el primero."
            )

    # El eje de montaje solo significa algo si la pieza tiene ejes que declarar.
    for c in catalogo.componentes:
        if c.montaje is None or c.montaje.eje is None:
            continue
        if c.montaje.tipo_eje not in ("fibra", "optico"):
            problemas.append(
                f"{c.id}: montaje.eje es '{c.montaje.eje}' pero montaje.tipo_eje "
                f"es {c.montaje.tipo_eje!r}. Decir por que eje entra la senal "
                f"sin decir que senal es no alinea nada."
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
