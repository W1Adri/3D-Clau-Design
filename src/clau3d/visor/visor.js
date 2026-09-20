// Visor del ensamblaje CLAU 6U.
//
// La geometria llega en clau_6u.glb y todo lo demas en escena.json. Aqui no se
// calcula ninguna cota del satelite: los numeros que aparecen en pantalla se
// leen del JSON, que a su vez sale del catalogo. Los unicos numeros de este
// fichero son de presentacion (camara, luces, colores de la interfaz).

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const $ = (sel) => document.querySelector(sel);
const crear = (tag, clase, texto) => {
  const el = document.createElement(tag);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  return el;
};
const num = (v, dec = 1) => (v === null || v === undefined ? '—' : v.toFixed(dec));

const CLASE_ESTADO = {
  ok: 'est-ok', atencion: 'est-atencion', falla: 'est-falla', 'no comprobable': 'est-nada',
};
const COLOR_ZONA = [0x4ea3ff, 0x4ccf7d, 0xffb84d, 0xc98bff, 0x4fd8d0, 0xff8fa3];

// ------------------------------------------------------------ escena 3D ----
const contenedor = $('#lienzo');
const escena3d = new THREE.Scene();
escena3d.background = new THREE.Color(0x10131a);

const camara = new THREE.PerspectiveCamera(38, 1, 1, 20000);
const render = new THREE.WebGLRenderer({ antialias: true });
render.setPixelRatio(Math.min(devicePixelRatio, 2));
contenedor.appendChild(render.domElement);

const controles = new OrbitControls(camara, render.domElement);
controles.enableDamping = true;
controles.dampingFactor = 0.08;

escena3d.add(new THREE.AmbientLight(0xffffff, 1.6));
const luz = new THREE.DirectionalLight(0xffffff, 2.2);
luz.position.set(1, 1.4, 1);
escena3d.add(luz);
const contraluz = new THREE.DirectionalLight(0xffffff, 0.9);
contraluz.position.set(-1, -0.6, -1);
escena3d.add(contraluz);

const gModelo = new THREE.Group();   // lo que viene del GLB
const gZonas = new THREE.Group();    // alambres de las zonas del layout
const gEjes = new THREE.Group();     // triedro CDS
escena3d.add(gModelo, gZonas, gEjes);

const planoCorte = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);

function redimensionar() {
  const ancho = contenedor.clientWidth;
  const alto = contenedor.clientHeight;
  camara.aspect = ancho / alto;
  camara.updateProjectionMatrix();
  render.setSize(ancho, alto);
}
addEventListener('resize', redimensionar);

function bucle() {
  requestAnimationFrame(bucle);
  controles.update();
  render.render(escena3d, camara);
}

// --------------------------------------------------------------- estado ---
let escena = null;              // escena.json
const cuerpos = new Map();      // clave logica -> { mallas[], tipo, pieza }
const porMalla = new Map();     // malla de three -> clave logica
let seleccion = null;

// ---------------------------------------------------------------- carga ---
async function arrancar() {
  try {
    escena = await (await fetch('escena.json', { cache: 'no-store' })).json();
  } catch (e) {
    return fallo('No se pudo leer escena.json. ¿Sigue vivo `uv run clau3d ver`?');
  }
  let gltf;
  try {
    gltf = await new GLTFLoader().loadAsync(escena.glb + '?t=' + Date.now());
  } catch (e) {
    return fallo('No se pudo leer ' + escena.glb + ': ' + e.message);
  }

  // glTF es Y-arriba, y OpenCASCADE gira el modelo al exportar: el eje Z del
  // CAD acaba siendo el Y del fichero. Se deshace aqui, para que lo que se ve
  // este en coordenadas CDS y encaje con las cajas que dibujamos del JSON.
  gltf.scene.rotation.x = Math.PI / 2;
  gModelo.add(gltf.scene);
  gModelo.updateMatrixWorld(true);

  indexarCuerpos(gltf.scene);
  dibujarZonas();
  dibujarEjes();
  construirInterfaz();
  redimensionar();
  // Enganche de depuracion: desde la consola del navegador se puede inspeccionar
  // la escena sin tocar el codigo (window.clau.cuerpos, window.clau.escena, ...).
  window.clau = { THREE, escena3d, camara, controles, cuerpos, escena, vista };
  vista('iso');
  bucle();
  $('#cargando').style.display = 'none';
}

function fallo(mensaje) {
  const el = $('#cargando');
  el.className = 'error';
  el.textContent = mensaje;
}

function tipoDe(clave, pieza) {
  if (pieza) return 'pieza';
  if (clave.startsWith('rail')) return 'railes';
  if (clave.startsWith('estructura')) return 'estructura';
  if (clave.startsWith('keepout')) return 'keepout';
  return 'otro';
}

// El nodo raiz del ensamblaje: se baja mientras solo haya un hijo que no sea
// una malla, que es como CadQuery envuelve el conjunto (Scene > CLAU_6U > ...).
function raizDelEnsamblaje(raiz) {
  let nodo = raiz;
  while (nodo.children.length === 1 && !nodo.children[0].isMesh) nodo = nodo.children[0];
  return nodo;
}

// OpenCASCADE parte cada solido en varias mallas, y GLTFLoader les pone sufijo
// (_1, _2...). Los sufijos CHOCAN con nuestros nombres de instancia: la segunda
// cara de 'bateria_optimus_30' se llama igual que la segunda bateria. Por eso
// no se agrupa por el nombre de la malla, sino por el Group que las contiene,
// que lleva el nombre exacto del nodo del ensamblaje.
function indexarCuerpos(raiz) {
  const piezas = new Map(escena.piezas.map((p) => [p.nodo, p]));
  for (const cuerpo of raizDelEnsamblaje(raiz).children) {
    const clave = cuerpo.name;
    const pieza = piezas.get(clave) || null;
    const tipo = tipoDe(clave, pieza);
    const mallas = [];

    cuerpo.traverse((obj) => {
      if (!obj.isMesh) return;
      obj.material = obj.material.clone();
      obj.material.side = THREE.DoubleSide;
      obj.userData.opacidadBase = obj.material.opacity;
      obj.userData.colorBase = obj.material.color.clone();

      // Aristas: sin ellas una caja translucida no se lee.
      const aristas = new THREE.LineSegments(
        new THREE.EdgesGeometry(obj.geometry, 25),
        new THREE.LineBasicMaterial({
          color: obj.material.color.clone().multiplyScalar(1.8),
          transparent: true,
          opacity: tipo === 'pieza' ? 0.8 : 0.3,
        }),
      );
      obj.add(aristas);
      obj.userData.aristas = aristas;

      mallas.push(obj);
      porMalla.set(obj, clave);
    });

    cuerpos.set(clave, { mallas, tipo, pieza });
  }
}

function verCuerpo(clave, visible) {
  const c = cuerpos.get(clave);
  if (c) c.mallas.forEach((m) => { m.visible = visible; });
}

function porTipo(tipo, visible) {
  for (const [clave, c] of cuerpos) if (c.tipo === tipo) verCuerpo(clave, visible);
}

function caja3(caja) {
  return new THREE.Box3(new THREE.Vector3(...caja.min), new THREE.Vector3(...caja.max));
}

function dibujarZonas() {
  escena.zonas.forEach((zona, i) => {
    const color = COLOR_ZONA[i % COLOR_ZONA.length];
    const ayuda = new THREE.Box3Helper(caja3(zona.caja), color);
    ayuda.material.transparent = true;
    ayuda.material.opacity = 0.7;
    ayuda.material.depthTest = false;
    ayuda.name = 'zona_' + zona.id;
    zona._color = color;
    gZonas.add(ayuda);
  });
}

// Triedro en el origen: el origen del 6U es su centro geometrico (CDS 2.2.1).
// Se dimensiona con el lado corto para no tapar el modelo.
function dibujarEjes() {
  const largo = Math.min(...escena.envolvente.dims) * 0.85;
  gEjes.add(new THREE.AxesHelper(largo));
  for (const [texto, pos] of [['X', [largo, 0, 0]], ['Y', [0, largo, 0]], ['Z', [0, 0, largo]]]) {
    const lienzo = document.createElement('canvas');
    lienzo.width = lienzo.height = 64;
    const ctx = lienzo.getContext('2d');
    ctx.fillStyle = '#dfe4ee';
    ctx.font = 'bold 44px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(texto, 32, 32);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(lienzo), depthTest: false, transparent: true,
    }));
    sprite.position.set(...pos);
    sprite.scale.setScalar(largo * 0.2);
    gEjes.add(sprite);
  }
}

// ---------------------------------------------------------------- vistas --
// La cara -Z entra primero en el dispensador; +Z es la que apunta a tierra.
const VISTAS = {
  iso:    { dir: [1, 0.75, 1.3], up: [0, 1, 0] },
  planta: { dir: [0, 1, 0], up: [1, 0, 0] },   // X-Z, desde +Y
  alzado: { dir: [0, 0, 1], up: [0, 1, 0] },   // X-Y, desde +Z
  perfil: { dir: [-1, 0, 0], up: [0, 1, 0] },  // Y-Z, desde -X
};

function vista(cual) {
  const caja = caja3(escena.envolvente);
  const centro = caja.getCenter(new THREE.Vector3());
  const radio = caja.getSize(new THREE.Vector3()).length() / 2;
  const distancia = (radio / Math.sin((camara.fov * Math.PI) / 360)) * 1.1;

  if (cual === 'ajustar') {
    const dir = camara.position.clone().sub(controles.target).normalize();
    camara.position.copy(centro).addScaledVector(dir, distancia);
  } else {
    const v = VISTAS[cual];
    camara.up.set(...v.up);
    camara.position.copy(centro)
      .addScaledVector(new THREE.Vector3(...v.dir).normalize(), distancia);
  }
  controles.target.copy(centro);
  controles.update();
}

// ------------------------------------------------------------- interfaz ---
function construirInterfaz() {
  const l = escena.layout;
  const pastilla = $('#estado-layout');
  pastilla.textContent = 'layout ' + l.estado;
  pastilla.classList.add(l.confirmado ? 'confirmada' : 'propuesta');
  if (l.nota) pastilla.title = l.nota;

  const r = escena.resumen;
  const dibujables = r.piezas_colocadas + escena.no_colocados_con_geometria.length;
  $('#resumen-barra').innerHTML =
    `zona útil <b>${num(r.volumen_interior_l, 2)} L</b> · ` +
    `libre <b>${num(r.volumen_libre_l, 2)} L</b>${r.fiable ? '' : ' (techo)'} · ` +
    `piezas <b>${r.piezas_colocadas}</b>/${dibujables + escena.sin_geometria.length} · ` +
    `<b>${r.pendientes_tbd}</b> TBD`;
  $('#generado').textContent = 'generado ' + escena.generado.replace('T', ' ').slice(0, 16);

  capas();
  arbol();
  sinGeometria();
  leyenda();
  tablaZonas();
  tablaResumen();
  avisos();
  corte();
  pestanas();

  document.querySelectorAll('#vistas button').forEach((b) => {
    b.onclick = () => vista(b.dataset.vista);
  });
  render.domElement.addEventListener('pointerdown', alPinchar);
  render.domElement.addEventListener('pointermove', alMover);
}

function conmutador(etiqueta, inicial, alCambiar) {
  const li = crear('li');
  const lab = crear('label');
  const chk = crear('input');
  chk.type = 'checkbox';
  chk.checked = inicial;
  chk.onchange = () => alCambiar(chk.checked);
  lab.append(chk, crear('span', null, etiqueta));
  li.append(lab);
  alCambiar(inicial);
  return li;
}

function capas() {
  $('#capas').append(
    conmutador('estructura (chasis genérico)', true, (v) => porTipo('estructura', v)),
    conmutador('raíles', true, (v) => porTipo('railes', v)),
    conmutador(`zonas del layout (${escena.zonas.length})`, true, (v) => { gZonas.visible = v; }),
    conmutador(`keep-outs (${escena.keep_outs.length})`, escena.keep_outs.length > 0,
      (v) => porTipo('keepout', v)),
    conmutador('ejes CDS', true, (v) => { gEjes.visible = v; }),
    conmutador('aristas', true, (v) => {
      for (const c of cuerpos.values()) c.mallas.forEach((m) => { m.userData.aristas.visible = v; });
    }),
  );
}

function marcaEstado(estado) {
  const m = crear('span', 'marca', estado === 'confirmado' ? 'ok' : estado);
  const rgb = escena.colores.por_estado[estado];
  m.style.color = rgb
    ? `rgb(${rgb.map((c) => Math.round(c * 255)).join(',')})`
    : 'var(--sutil)';
  return m;
}

function arbol() {
  const cont = $('#arbol');
  const porZona = new Map();
  for (const p of escena.piezas) {
    const clave = p.zona || '(sin zona)';
    if (!porZona.has(clave)) porZona.set(clave, []);
    porZona.get(clave).push(p);
  }

  // Todas las zonas, tambien las que aun no tienen nada dentro: que una zona
  // este vacia es justo lo que hay que ver.
  const orden = [...escena.zonas.map((z) => z.id), '(sin zona)'];
  for (const clave of orden) {
    const piezas = porZona.get(clave) || [];
    const zona = escena.zonas.find((z) => z.id === clave);
    if (!zona && !piezas.length) continue;

    const grupo = crear('div', 'grupo');
    const cab = crear('div', 'cabecera');
    const chk = crear('input');
    chk.type = 'checkbox';
    chk.checked = true;
    chk.disabled = !piezas.length;
    chk.onchange = () => piezas.forEach((p) => {
      verCuerpo(p.nodo, chk.checked);
      const fila = document.querySelector(`[data-nodo="${p.nodo}"] input`);
      if (fila) fila.checked = chk.checked;
    });
    cab.append(chk);
    if (zona) {
      const m = crear('span', 'muestra');
      m.style.background = '#' + zona._color.toString(16).padStart(6, '0');
      cab.append(m);
    }
    cab.append(crear('span', 'nombre', zona ? zona.nombre : clave));
    if (zona) {
      cab.append(crear('span', 'dato', `${num(zona.libre_l, 2)} L libres`));
      cab.title = zona.nota || '';
    }
    grupo.append(cab);

    const ul = crear('ul');
    if (!piezas.length) {
      ul.append(crear('li', 'pieza sutil', 'vacía — nada colocado todavía'));
    }
    for (const p of piezas) {
      const li = crear('li', 'pieza');
      li.dataset.nodo = p.nodo;
      const c = crear('input');
      c.type = 'checkbox';
      c.checked = true;
      c.onchange = () => verCuerpo(p.nodo, c.checked);
      const et = crear('span', 'etiqueta', p.nombre);
      et.title = p.nodo;
      et.onclick = () => seleccionar(p.nodo, true);
      li.append(c, et, marcaEstado(p.estado_dato));
      ul.append(li);
    }
    grupo.append(ul);
    cont.append(grupo);
  }
  $('#cuenta-piezas').textContent = escena.piezas.length + ' colocadas';
}

function sinGeometria() {
  const ul = $('#sin-geometria');
  for (const c of escena.sin_geometria) {
    const li = crear('li');
    li.append(crear('span', 'id', c.nombre));
    li.append(crear('span', 'pedir', c.pedir_a ? '→ ' + c.pedir_a : '→ sin asignar'));
    li.title = c.falta || 'sin describir';
    ul.append(li);
  }
  $('#cuenta-sin').textContent = escena.sin_geometria.length + ' componentes';
}

function leyenda() {
  const ul = $('#leyenda');
  const nombres = {
    confirmado: 'dato confirmado', referencia: 'dato de un componente parecido',
    decision: 'decisión de diseño de ACSAR', TBD: 'falta el dato',
  };
  const filas = [
    ...Object.entries(escena.colores.por_estado).map(([k, v]) => [nombres[k] || k, v]),
    ...Object.entries(escena.colores.por_categoria)
      .map(([k, v]) => [k.replace(/_/g, ' ') + ' (confirmado)', v]),
  ];
  for (const [texto, rgb] of filas) {
    const li = crear('li');
    const m = crear('span', 'muestra');
    m.style.background = `rgb(${rgb.map((c) => Math.round(c * 255)).join(',')})`;
    li.append(m, crear('span', null, texto));
    ul.append(li);
  }
}

// ---------------------------------------------------------------- corte ---
function corte() {
  const sel = $('#corte-eje');
  const pos = $('#corte-pos');
  const inv = $('#corte-invertir');
  const caja = caja3(escena.envolvente);

  const aplicar = () => {
    const eje = sel.value;
    pos.disabled = eje === 'ninguno';
    if (eje === 'ninguno') { render.clippingPlanes = []; return; }
    const normal = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] }[eje];
    const min = caja.min[eje];
    const max = caja.max[eje];
    const corte = min + (max - min) * parseFloat(pos.value);
    const signo = inv.checked ? 1 : -1;
    planoCorte.normal.set(...normal).multiplyScalar(signo);
    planoCorte.constant = -signo * corte;
    render.clippingPlanes = [planoCorte];
  };
  sel.onchange = () => { pos.value = inv.checked ? '0' : '1'; aplicar(); };
  pos.oninput = aplicar;
  inv.onchange = aplicar;
  aplicar();
}

// ------------------------------------------------------------ seleccion ---
const rayo = new THREE.Raycaster();
const puntero = new THREE.Vector2();
const etiquetaFlotante = crear('div');
etiquetaFlotante.id = 'etiqueta-pieza';
document.body.append(etiquetaFlotante);

function bajoPuntero(ev) {
  const r = render.domElement.getBoundingClientRect();
  puntero.set(((ev.clientX - r.left) / r.width) * 2 - 1,
    -((ev.clientY - r.top) / r.height) * 2 + 1);
  rayo.setFromCamera(puntero, camara);
  const visibles = [];
  for (const c of cuerpos.values()) {
    if (!c.pieza) continue;
    for (const m of c.mallas) if (m.visible) visibles.push(m);
  }
  const golpes = rayo.intersectObjects(visibles, false);
  return golpes.length ? porMalla.get(golpes[0].object) : null;
}

function alMover(ev) {
  const clave = bajoPuntero(ev);
  if (!clave) { etiquetaFlotante.style.display = 'none'; return; }
  etiquetaFlotante.style.display = 'block';
  etiquetaFlotante.style.left = ev.clientX + 'px';
  etiquetaFlotante.style.top = ev.clientY + 'px';
  etiquetaFlotante.textContent = cuerpos.get(clave).pieza.nombre;
}

let arrastre = null;
function alPinchar(ev) {
  arrastre = { x: ev.clientX, y: ev.clientY };
  const alSoltar = (e2) => {
    render.domElement.removeEventListener('pointerup', alSoltar);
    if (Math.hypot(e2.clientX - arrastre.x, e2.clientY - arrastre.y) > 4) return;
    seleccionar(bajoPuntero(e2), false);
  };
  render.domElement.addEventListener('pointerup', alSoltar);
}

function resaltar(clave, activo) {
  const c = cuerpos.get(clave);
  if (!c) return;
  for (const m of c.mallas) {
    if (activo) {
      m.material.emissive.setHex(0x2a4a7a);
      m.material.opacity = Math.min(1, m.userData.opacidadBase + 0.35);
    } else {
      m.material.emissive.setHex(0x000000);
      m.material.opacity = m.userData.opacidadBase;
      m.material.color.copy(m.userData.colorBase);
    }
  }
}

function seleccionar(clave, desdeLista) {
  if (seleccion) resaltar(seleccion, false);
  document.querySelectorAll('.pieza.sel').forEach((el) => el.classList.remove('sel'));
  seleccion = clave;
  if (!clave || !cuerpos.has(clave)) { seleccion = null; detalle(null); return; }

  resaltar(clave, true);
  const fila = document.querySelector(`[data-nodo="${clave}"]`);
  if (fila) {
    fila.classList.add('sel');
    if (!desdeLista) fila.scrollIntoView({ block: 'nearest' });
  }
  detalle(cuerpos.get(clave).pieza);
  if (desdeLista) hojaActiva('datos');
}

function filaMagnitud(tabla, etiqueta, magnitud) {
  const tr = crear('tr');
  tr.append(crear('th', null, etiqueta));
  const td = crear('td');
  const valor = magnitud.valor === null
    ? (magnitud.estado === 'ausente' ? 'no declarada' : 'TBD')
    : (Array.isArray(magnitud.valor) ? magnitud.valor.join(' × ') : magnitud.valor) +
      (magnitud.unidad ? ' ' + magnitud.unidad : '');
  td.append(crear('div', null, String(valor)));
  td.append(crear('div', 'proc', magnitud.estado + (magnitud.fuente ? ' · ' + magnitud.fuente : '')));
  if (magnitud.falta) {
    td.append(crear('div', 'falta est-atencion', 'falta: ' + magnitud.falta +
      (magnitud.pedir_a ? ' — pedir a ' + magnitud.pedir_a : '')));
  }
  for (const alt of magnitud.discrepancia || []) {
    td.append(crear('div', 'proc est-atencion',
      'otra fuente: ' + (alt.valor ?? '?') + (alt.fuente ? ' (' + alt.fuente + ')' : '')));
  }
  tr.append(td);
  tabla.append(tr);
}

function detalle(p) {
  const cont = $('#detalle');
  cont.textContent = '';
  if (!p) {
    cont.append(crear('p', 'sutil', 'Haz clic en una pieza para ver de dónde sale cada cota.'));
    return;
  }
  cont.append(crear('h3', null, p.nombre));
  cont.append(crear('div', 'id-comp', p.componente + (p.nodo !== p.componente ? ' · ' + p.nodo : '')));
  if (p.nota) cont.append(crear('div', 'nota', p.nota));

  const t = crear('table', 'tabla');
  filaMagnitud(t, 'dimensiones', p.magnitudes.dimensiones);
  filaMagnitud(t, 'masa', p.magnitudes.masa);
  filaMagnitud(t, 'potencia nominal', p.magnitudes.potencia_nominal);
  filaMagnitud(t, 'potencia pico', p.magnitudes.potencia_pico);

  const simple = (etiqueta, valor) => {
    const tr = crear('tr');
    tr.append(crear('th', null, etiqueta), crear('td', null, valor));
    t.append(tr);
  };
  simple('zona', p.zona || '(sin zona)');
  simple('categoría', p.categoria);
  simple('subsistema', p.subsistema);
  simple('centro (mm)', p.centro.map((v) => v.toFixed(1)).join(' , '));
  simple('rotación (°)', p.rotacion.join(' , '));
  simple('envolvente (mm)', p.caja.dims.map((v) => v.toFixed(1)).join(' × '));
  simple('volumen', num(p.volumen_cm3, 1) + ' cm³');
  simple('sólido', p.desde_step ? 'STEP de fabricante: ' + p.step : 'caja envolvente del catálogo');
  if (p.requiere_vista_exterior) simple('atención', 'necesita vista despejada al exterior');
  cont.append(t);
}

// ------------------------------------------------------- tablas y avisos --
function tablaZonas() {
  const t = $('#tabla-zonas');
  const cab = crear('tr');
  ['zona', 'total', 'libre'].forEach((x) => cab.append(crear('th', null, x)));
  t.append(cab);
  for (const z of escena.zonas) {
    const tr = crear('tr');
    tr.append(crear('th', null, z.nombre));
    tr.append(crear('td', 'num', num(z.volumen_l, 2) + ' L'));
    tr.append(crear('td', 'num', num(z.libre_l, 2) + ' L'));
    tr.title = z.nota || '';
    t.append(tr);
  }
}

function tablaResumen() {
  const t = $('#tabla-resumen');
  const r = escena.resumen;
  const fila = (k, v, proc) => {
    const tr = crear('tr');
    tr.append(crear('th', null, k));
    const td = crear('td', 'num', v);
    if (proc) td.append(crear('div', 'proc', proc));
    tr.append(td);
    t.append(tr);
  };
  const mm = (dims) => dims.map((d) => d.toFixed(1)).join(' × ') + ' mm';
  fila('envolvente 6U', num(r.volumen_exterior_l, 2) + ' L', mm(escena.envolvente.dims));
  fila('zona útil interior', num(r.volumen_interior_l, 2) + ' L', mm(escena.zona_util.dims));
  fila('ocupado por lo colocado', num(r.volumen_ocupado_l, 2) + ' L');
  fila('libre', num(r.volumen_libre_l, 2) + ' L',
    r.fiable ? 'cifra cerrada' : 'techo, no cifra de diseño: faltan envolventes');
  fila('componentes', String(r.componentes));
  fila('colocados', String(r.piezas_colocadas));
  fila('sin envolvente', String(r.sin_envolvente.length));
  fila('datos pendientes', String(r.pendientes_tbd) + ' TBD');
  fila('discrepancias entre fuentes', String(r.discrepancias));
}

function avisos() {
  const ul = $('#chequeos');
  for (const c of escena.chequeos) {
    const li = crear('li');
    const tit = crear('div', 'titulo');
    tit.append(crear('span', CLASE_ESTADO[c.estado] || '', '●'), crear('span', null, c.titulo));
    li.append(tit, crear('div', 'cuerpo', c.mensaje));
    if (c.falta) li.append(crear('div', 'falta', 'falta: ' + c.falta));
    ul.append(li);
  }
  const ui = $('#interferencias');
  if (!escena.interferencias.length) {
    ui.append(crear('li', 'cuerpo', 'Ninguna entre las piezas colocadas.'));
  } else {
    for (const i of escena.interferencias) {
      const li = crear('li');
      const tit = crear('div', 'titulo');
      tit.append(crear('span', 'est-falla', '●'), crear('span', null, `${i.tipo}: ${i.a} — ${i.b}`));
      li.append(tit, crear('div', 'cuerpo', i.detalle));
      ui.append(li);
    }
  }
  const malos = escena.chequeos.filter((c) => c.estado === 'falla').length
    + escena.interferencias.length;
  const sinDato = escena.chequeos.filter((c) => c.estado === 'no comprobable').length;
  const chip = $('#cuenta-avisos');
  chip.textContent = String(malos || sinDato);
  if (malos) chip.classList.add('est-falla');
}

function hojaActiva(cual) {
  document.querySelectorAll('.pestanas button').forEach((b) =>
    b.classList.toggle('activa', b.dataset.pestana === cual));
  document.querySelectorAll('#panel section').forEach((s) => {
    s.hidden = s.dataset.hoja !== cual;
  });
}

function pestanas() {
  document.querySelectorAll('.pestanas button').forEach((b) => {
    b.onclick = () => hojaActiva(b.dataset.pestana);
  });
}

arrancar();
