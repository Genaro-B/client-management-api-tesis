// Validez externa
const fs = require('fs');
const path = require('path');
const { INDEPENDIENTES } = require('./independientes');

const RAIZ = path.resolve(__dirname, '..', '..');
const FLUJO = path.join(RAIZ, 'Docs', 'flujos', 'Actual', 'v2-flujo-mejorado.json');
const SALIDA = path.join(__dirname, 'resultados-validez-externa.json');

const flow = JSON.parse(fs.readFileSync(FLUJO, 'utf8'));
const nodes = flow.nodes || flow;
const codigo = nodes.find(n => n.name === 'Bot Router')['parameters'].functionCode;

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

function crear() {
  let staticData = {};
  let actual = {};
  const getWorkflowStaticData = () => staticData;
  const $input = { first: () => ({ json: actual }) };
  const fn = new AsyncFunction('getWorkflowStaticData', '$input', codigo);
  return {
    async enviar(mensaje, datos = {}) {
      actual = { mensaje, productos: [], user_id: 'u1', ...datos };
      const r = await fn(getWorkflowStaticData, $input);
      return Array.isArray(r) ? r[0].json : r;
    },
  };
}

const PRODUCTOS = [
  { id: 1, nombre: 'Jamon', precio: 8500, stock: 5 },
  { id: 2, nombre: 'Queso', precio: 5200, stock: 3 },
  { id: 3, nombre: 'Vino Tinto', precio: 12000, stock: 0 },
];

const HUELLAS = [
  ['Número de producto inválido', 'numero_invalido'],
  ['no tiene stock disponible', 'sin_stock'],
  ['No entendí ese comando', 'fallback'],
  ['agregado a tu carrito', 'producto_seleccionado'],
  ['Bienvenido al sistema', 'menu'],
  ['Productos para comprar', 'comprar'],
  ['Nuestro Catálogo', 'catalogo'],
  ['Lista de Precios', 'precios'],
  ['asesor se va a comunicar', 'asesor'],
  ['Contame tu consulta', 'otra'],
  ['Tu carrito está vacío', 'carrito'],
  ['Total: $', 'carrito'],
  ['Compra finalizada', 'finalizar'],
];

function detectar(salida) {
  const m = String(salida.mensaje || '');
  for (const [huella, etiqueta] of HUELLAS) {
    if (m.includes(huella)) return etiqueta;
  }
  return 'desconocido';
}

function pct(n, d) {
  return d === 0 ? 0 : Math.round((n / d) * 1000) / 10;
}

(async () => {
  console.log('='.repeat(70));
  console.log('VALIDEZ EXTERNA');
  console.log('='.repeat(70));
  const detalle = [];
  for (const c of INDEPENDIENTES) {
    const r = await crear().enviar(c.mensaje, { productos: PRODUCTOS });
    const det = detectar(r);
    const conforme = det === c.intencion_esperada;
    detalle.push({
      id: c.id,
      intencion_esperada: c.intencion_esperada,
      mensaje: c.mensaje,
      detectado: det,
      conforme,
    });
    console.log(`${c.id} ${conforme ? 'OK' : 'FALLA'} esp:${c.intencion_esperada.padEnd(10)} det:${det.padEnd(12)} msg:${c.mensaje}`);
  }

  const total = detalle.length;
  const conformes = detalle.filter(x => x.conforme).length;
  const precision = pct(conformes, total);
  const fallbackCount = detalle.filter(x => x.detectado === 'fallback').length;
  const tasa_fallback = pct(fallbackCount, total);

  const expectedCats = Array.from(new Set(detalle.map(x => x.intencion_esperada)));
  const alcanzadas = expectedCats.filter(cat =>
    detalle.some(x => x.intencion_esperada === cat && x.conforme)
  );
  const cobertura = pct(alcanzadas.length, expectedCats.length);

  const por_intencion = {};
  for (const c of detalle) {
    if (!por_intencion[c.intencion_esperada]) {
      por_intencion[c.intencion_esperada] = { total: 0, conformes: 0 };
    }
    por_intencion[c.intencion_esperada].total++;
    if (c.conforme) por_intencion[c.intencion_esperada].conformes++;
  }

  const fallos = detalle.filter(x => !x.conforme);

  const salida = {
    generado: new Date().toISOString(),
    nota_metodologica:
      'Conjunto independiente, mensajes redactados sin conocer el catalogo. Cada mensaje con runner FRESH. Deteccion por huellas.',
    total,
    precision,
    tasa_fallback,
    cobertura,
    detalle,
    por_intencion,
    fallos,
  };

  fs.writeFileSync(SALIDA, JSON.stringify(salida, null, 2), 'utf8');
  console.log();
  console.log(`Escritos: ${path.relative(RAIZ, SALIDA)}`);
  console.log(`Precision: ${precision}% (${conformes}/${total}) | Tasa fallback: ${tasa_fallback}% | Cobertura: ${cobertura}%`);
})();
