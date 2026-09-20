"""Los STEP de fabricante no vienen como el modelo los espera.

Estos tests usan geometria INVENTADA a proposito. Con el catalogo actual, un
test que solo mirase los STEP reales pasaria o fallaria segun quien tenga los
ficheros descargados, que precisamente no se versionan. Lo que hay que
comprobar es que el mecanismo funciona: que un STEP con el origen en una
esquina acaba centrado, que un STEP con los ejes cambiados acaba girado, y que
una caja envolvente absurda se rechaza en vez de propagarse.
"""

import cadquery as cq
import pytest
import yaml

from clau3d import parts
from clau3d.analysis import fit
from clau3d.datamodel import DIR_CAD, ErrorDeDatos, _componente


def _componente_step(tmp_path, solido, **step_extra):
    """Un componente de mentira cuyo STEP es el solido que se le pase."""
    ruta = tmp_path / "pieza.step"
    cq.exporters.export(solido, str(ruta))
    bruto = {
        "id": "pieza_de_prueba",
        "nombre": "Pieza de prueba",
        "categoria": "plataforma",
        "subsistema": "prueba",
        "cantidad": 1,
        "forma": {
            "tipo": "step",
            "step": {
                "ruta": str(ruta),
                "estado": "referencia",
                "fuente": "Geometria inventada por el test",
                **step_extra,
            },
        },
        "masa": {"valor": None, "estado": "TBD", "falta": "x", "pedir_a": "y"},
    }
    return _componente(bruto)


# --- el origen ------------------------------------------------------------

def test_un_step_con_el_origen_en_una_esquina_acaba_centrado(tmp_path):
    """El ensamblaje coloca por el centro: media pieza de error si no se recentra."""
    caja = cq.Solid.makeBox(10, 20, 30, cq.Vector(100, 200, 300))
    componente = _componente_step(tmp_path, caja)
    local = parts.caja_local(componente)
    assert local is not None
    assert local.centro == pytest.approx((0.0, 0.0, 0.0), abs=1e-6)
    assert local.dims == pytest.approx((10.0, 20.0, 30.0))


def test_recentrar_se_puede_desactivar(tmp_path):
    """Cuando el origen del STEP ya es el punto de montaje bueno."""
    caja = cq.Solid.makeBox(10, 20, 30, cq.Vector(100, 200, 300))
    componente = _componente_step(tmp_path, caja, recentrar=False)
    local = parts.caja_local(componente)
    assert local is not None
    assert local.centro == pytest.approx((105.0, 210.0, 315.0), abs=1e-6)


# --- los ejes -------------------------------------------------------------

def test_la_orientacion_cambia_los_ejes_sin_cambiar_las_cotas(tmp_path):
    """Es el caso real de las tarjetas AAC: llegan con X e Y intercambiados."""
    caja = cq.Solid.makeBox(90.17, 95.89, 23.24)
    derecha = parts.caja_local(_componente_step(tmp_path, caja))
    girada = parts.caja_local(
        _componente_step(tmp_path, caja, orientacion=[0, 0, 90])
    )
    assert derecha is not None and girada is not None
    assert derecha.dims == pytest.approx((90.17, 95.89, 23.24))
    assert girada.dims == pytest.approx((95.89, 90.17, 23.24))
    # Girar no crea ni destruye volumen.
    assert girada.volumen_mm3 == pytest.approx(derecha.volumen_mm3)


def test_la_orientacion_lleva_el_eje_de_pila_a_z(tmp_path):
    """El caso del iADCS4-20: el STEP trae el eje de apilamiento por Y."""
    caja = cq.Solid.makeBox(95.40, 74.10, 93.90)
    girada = parts.caja_local(
        _componente_step(tmp_path, caja, orientacion=[90, 0, 0])
    )
    assert girada is not None
    assert girada.dims == pytest.approx((95.40, 93.90, 74.10))


# --- la caja envolvente ---------------------------------------------------

def test_la_caja_se_calcula_solido_a_solido():
    """Un compound con varios solidos da la union de sus cajas."""
    compound = cq.Compound.makeCompound(
        [
            cq.Solid.makeBox(10, 10, 10, cq.Vector(0, 0, 0)),
            cq.Solid.makeBox(10, 10, 10, cq.Vector(50, 0, 0)),
        ]
    )
    caja = parts.caja_de_solidos(compound)
    assert caja.dims == pytest.approx((60.0, 10.0, 10.0))


def test_una_caja_absurda_se_rechaza_en_vez_de_propagarse():
    """El STEP del ADCS devuelve una caja infinita sobre el compound entero.

    Si eso llega al prefiltro de interferencias, TODO solapa con todo y el
    informe deja de significar nada. Mas vale un error que un 'ok' falso.
    """
    lejos = cq.Solid.makeBox(1, 1, 1, cq.Vector(parts.COORDENADA_ABSURDA_MM * 10, 0, 0))
    with pytest.raises(ErrorDeDatos, match="degenerada"):
        parts.caja_de_solidos(lejos, "pieza_inventada")


# --- sin el fichero -------------------------------------------------------

def test_sin_el_fichero_se_cae_a_la_caja_de_ficha(tmp_path):
    """Quien clone el repositorio sin los CAD tiene que poder ejecutarlo todo."""
    bruto = {
        "id": "pieza_sin_fichero",
        "nombre": "Pieza sin fichero",
        "categoria": "plataforma",
        "subsistema": "prueba",
        "cantidad": 1,
        "forma": {
            "tipo": "step",
            "step": {
                "ruta": "cad/vendor/otros/esto_no_existe.step",
                "estado": "referencia",
                "fuente": "Geometria inventada por el test",
            },
            "dimensiones": {
                "valor": [10.0, 20.0, 30.0],
                "unidad": "mm",
                "estado": "confirmado",
                "fuente": "Inventado por el test",
            },
        },
        "masa": {"valor": None, "estado": "TBD", "falta": "x", "pedir_a": "y"},
    }
    componente = _componente(bruto)
    assert not parts.step_disponible(componente)
    local = parts.caja_local(componente)
    assert local is not None
    assert local.dims == pytest.approx((10.0, 20.0, 30.0))
    # Y se pinta con el estado de la ficha, no con el del STEP ausente.
    assert parts.estado_geometria(componente) == "confirmado"


def test_sin_fichero_y_sin_dimensiones_si_es_un_error():
    bruto = {
        "id": "pieza_sin_nada",
        "nombre": "Pieza sin nada",
        "categoria": "plataforma",
        "subsistema": "prueba",
        "cantidad": 1,
        "forma": {
            "tipo": "step",
            "step": {
                "ruta": "cad/vendor/otros/esto_tampoco_existe.step",
                "estado": "referencia",
                "fuente": "Geometria inventada por el test",
            },
        },
        "masa": {"valor": None, "estado": "TBD", "falta": "x", "pedir_a": "y"},
    }
    with pytest.raises(ErrorDeDatos, match="MANIFEST"):
        parts.solido(_componente(bruto))


# --- el manifiesto --------------------------------------------------------

def test_el_manifiesto_declara_todos_los_cad_presentes():
    """Un CAD en cad/vendor/ sin entrada en el manifiesto no tiene procedencia."""
    manifiesto = yaml.safe_load(
        (DIR_CAD / "vendor" / "MANIFEST.yaml").read_text(encoding="utf-8")
    )
    declarados = {e["ruta"] for e in manifiesto["ficheros"]}
    vendor = DIR_CAD / "vendor"
    en_disco = {
        str(p.relative_to(vendor))
        for p in vendor.rglob("*")
        if p.suffix.lower() in (".step", ".stp")
    }
    assert en_disco <= declarados, f"sin declarar: {sorted(en_disco - declarados)}"


def test_todo_step_del_catalogo_esta_en_el_manifiesto(catalogo):
    manifiesto = yaml.safe_load(
        (DIR_CAD / "vendor" / "MANIFEST.yaml").read_text(encoding="utf-8")
    )
    declarados = {f"cad/vendor/{e['ruta']}" for e in manifiesto["ficheros"]}
    for componente in catalogo.componentes:
        if componente.step is not None:
            assert componente.step.ruta in declarados, componente.id


def test_el_chequeo_del_manifiesto_no_falla_por_un_fichero_ausente(catalogo, tmp_path):
    """Ausente es 'atencion'; huella distinta es 'falla'. No es lo mismo."""
    chequeo = fit.chequeo_step_de_fabricante(catalogo)
    assert chequeo.estado in (fit.OK, fit.ATENCION)
    assert not chequeo.critico


def test_una_huella_distinta_si_es_un_fallo(catalogo, tmp_path, monkeypatch):
    """Con el manifiesto de verdad esto no se puede provocar, asi que se monta
    uno de mentira: un fichero cuyo contenido no es el declarado significa que
    el modelo se dibujo con otra geometria."""
    vendor = tmp_path / "vendor"
    (vendor / "otros").mkdir(parents=True)
    (vendor / "otros" / "falso.step").write_text("no soy el fichero declarado")
    (vendor / "MANIFEST.yaml").write_text(
        "ficheros:\n"
        "  - ruta: otros/falso.step\n"
        "    sha256: " + "0" * 64 + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fit, "DIR_CAD", tmp_path)
    chequeo = fit.chequeo_step_de_fabricante(catalogo)
    assert chequeo.estado == fit.FALLA
    assert chequeo.critico
    assert "HUELLA DISTINTA" in chequeo.mensaje


def test_sin_manifiesto_el_chequeo_no_dice_que_todo_va_bien(catalogo, tmp_path, monkeypatch):
    monkeypatch.setattr(fit, "DIR_CAD", tmp_path)
    chequeo = fit.chequeo_step_de_fabricante(catalogo)
    assert chequeo.estado == fit.NO_COMPROBABLE


def test_el_manifiesto_declara_la_huella_de_cada_cad():
    manifiesto = yaml.safe_load(
        (DIR_CAD / "vendor" / "MANIFEST.yaml").read_text(encoding="utf-8")
    )
    for entrada in manifiesto["ficheros"]:
        assert len(entrada["sha256"]) == 64, entrada["ruta"]
        assert entrada["bytes"] > 0
        assert entrada["origen"]


# --- procedencia ----------------------------------------------------------

def test_un_step_necesita_estado_y_fuente():
    with pytest.raises(ErrorDeDatos, match="ruta"):
        _componente(
            {
                "id": "x",
                "nombre": "x",
                "categoria": "plataforma",
                "subsistema": "x",
                "forma": {"step": {"estado": "referencia"}},
                "masa": {"valor": None, "estado": "TBD", "falta": "a", "pedir_a": "b"},
            }
        )


def test_un_step_suelto_como_cadena_no_vale():
    """Una ruta pelada no dice de donde salio el fichero ni de que producto es."""
    with pytest.raises(ErrorDeDatos, match="procedencia|magnitud"):
        _componente(
            {
                "id": "x",
                "nombre": "x",
                "categoria": "plataforma",
                "subsistema": "x",
                "forma": {"step": "cad/vendor/otros/x.step"},
                "masa": {"valor": None, "estado": "TBD", "falta": "a", "pedir_a": "b"},
            }
        )


def test_el_estado_dibujado_manda_sobre_el_de_la_ficha(catalogo):
    """La bateria tiene ficha confirmada y STEP de referencia: se dibuja el STEP."""
    bateria = catalogo["bateria_optimus_30"]
    assert bateria.dimensiones.estado == "confirmado"
    assert bateria.step is not None
    assert bateria.step.estado == "referencia"
    assert bateria.estado_geometria == "referencia"


def test_una_alternativa_no_suma_en_los_presupuestos(catalogo):
    """El iADCS4-20 es un candidato, no una pieza a bordo: contarlo seria contar
    dos ADCS."""
    alternativa = catalogo["adcs_iadcs420"]
    assert alternativa.alternativa_de == "adcs_iadcs400"
    assert not alternativa.cuenta_en_presupuesto

    from clau3d.analysis import budgets

    ids = {fila.id for fila in budgets.masa(catalogo).filas}
    ids |= set(budgets.masa(catalogo).sin_dato)
    assert "adcs_iadcs420" not in ids
    assert "adcs_iadcs400" in ids


def test_la_discrepancia_de_las_tarjetas_aac_esta_registrada(catalogo):
    """El STEP y la ficha no dicen lo mismo: van las dos cifras, no una."""
    for id_componente in ("bateria_optimus_30", "obc_kryten_m3_plus"):
        dims = catalogo[id_componente].dimensiones
        assert dims.hay_discrepancia, id_componente
        alturas = {dims.valor[2]} | {a["valor"][2] for a in dims.alternativas}
        assert len(alturas) == 3, id_componente
