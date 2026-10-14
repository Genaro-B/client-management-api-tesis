// Medición de casos para Tabla 6
const fs = require('fs');
const path = require('path');
const { CASOS } = require('./casos');

const RAIZ = path.resolve(__dirname, '..', '..');
const FLUJO = path.join(RAIZ, 'Docs', 'flujos', 'Actual', 'v2-flujo-mejorado.json');
const SALIDA = path.join(__dirname, 'resultados-casos-tabla6.json');

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
  console.log('MEDICION CASOS TABLA 6');
  console.log('='.repeat(70));
  const resultados = [];
  for (const caso of CASOS) {
    const r = await crear().enviar(caso.mensaje, { productos: PRODUCTOS });
    const det = detectar(r);
    const conforme = det === caso.intencion;
    resultados.push({
      id: caso.id,
      categoria: caso.categoria,
      intencion: caso.intencion,
      mensaje: caso.mensaje,
      detectado: det,
      conforme,
    });
    console.log(`${caso.id} ${conforme ? 'OK' : 'FALLA'} ${caso.categoria.padEnd(10)} -> det:${det.padEnd(12)} esp:${caso.intencion}`);
  }

  const porCategoria = {};
  for (const c of resultados) {
    if (!porCategoria[c.categoria]) {
      porCategoria[c.categoria] = { count: 0, conformes: 0, no_conformes: 0 };
    }
    porCategoria[c.categoria].count++;
    if (c.conforme) porCategoria[c.categoria].conformes++;
    else porCategoria[c.categoria].no_conformes++;
  }

  const total = resultados.length;
  const conformesTotal = resultados.filter(x => x.conforme).length;

  const salida = {
    generado: new Date().toISOString(),
    nota_metodologica:
      'Cada mensaje se evalua con estado conversacional limpio (modo=menu, carrito vacio). Deteccion por huellas del Bot Router.',
    casos: resultados,
    por_categoria: porCategoria,
    resumen: {
      total,
      conformes: conformesTotal,
      no_conformes: total - conformesTotal,
      conformidad_global_pct: pct(conformesTotal, total),
    },
  };

  fs.writeFileSync(SALIDA, JSON.stringify(salida, null, 2), 'utf8');
  console.log();
  console.log(`Escritos: ${path.relative(RAIZ, SALIDA)}`);
  console.log(`Conformidad global: ${pct(conformesTotal, total)}% (${conformesTotal}/${total})`);
})();
