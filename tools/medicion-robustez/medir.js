// Ejecuta el codigo REAL del nodo "Bot Router" de n8n fuera de la plataforma y
// mide su comportamiento ante mensajes fuera del catalogo.
//
// No usa Telegram, ni la API, ni n8n, ni la red: es el mismo functionCode de
// produccion, ejecutado con un stub minimo de $input y getWorkflowStaticData.
// Por eso los numeros son reproducibles en cualquier maquina con Node.
//
// Uso:  node tools/medicion-robustez/medir.js
const fs = require('fs');
const path = require('path');
const { BASE, REGLAS, CASOS_TABLA7 } = require('./mutaciones');

const RAIZ = path.resolve(__dirname, '..', '..');
const FLUJO = path.join(RAIZ, 'Docs', 'flujos', 'Actual', 'v2-flujo-mejorado.json');
const SALIDA = path.join(__dirname, 'resultados.json');

const flow = JSON.parse(fs.readFileSync(FLUJO, 'utf8'));
const nodes = flow.nodes || flow;
const codigo = next(nodes, n => n.name === 'Bot Router')['parameters'].functionCode;
function next(arr, pred) { for (const x of arr) if (pred(x)) return x; throw new Error('nodo no encontrado'); }

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;

/** Runner con estado conversacional aislado: cada `crear()` arranca en limpio. */
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

// Catalogo de productos minimo pero realista (uno sin stock, para el caso 3).
const PRODUCTOS = [
  { id: 1, nombre: 'Jamon',      precio: 8500,  stock: 5 },
  { id: 2, nombre: 'Queso',      precio: 5200,  stock: 3 },
  { id: 3, nombre: 'Vino Tinto', precio: 12000, stock: 0 },
];

/** Huellas de respuesta -> intencion. El orden importa: mas especifico primero. */
const HUELLAS = [
  ['Número de producto inválido',        'numero_invalido'],
  ['no tiene stock disponible',          'sin_stock'],
  ['No entendí ese comando',             'fallback'],
  ['agregado a tu carrito',              'producto_seleccionado'],
  ['Bienvenido al sistema',              'menu'],
  ['Productos para comprar',             'comprar'],
  ['Nuestro Catálogo',                   'catalogo'],
  ['Lista de Precios',                   'precios'],
  ['asesor se va a comunicar',           'asesor'],
  ['Contame tu consulta',                'otra'],
  ['Tu carrito está vacío',              'carrito'],
  ['Total: $',                           'carrito'],
  ['Compra finalizada',                  'finalizar'],
];

function detectar(salida) {
  const m = String(salida.mensaje || '');
  for (const [huella, etiqueta] of HUELLAS) {
    if (m.includes(huella)) return etiqueta;
  }
  return 'desconocido';
}

const pct = (n, d) => (d === 0 ? 0 : Math.round((n / d) * 1000) / 10);
const cuenta = (xs) => xs.reduce((m, x) => (m[x]++, m), {});

(async () => {
  // ---------- 1. AUDITORIA DE LAS VARIANTES DOCUMENTADAS EN LA TESIS ----------
  console.log('='.repeat(78));
  console.log('1. AUDITORIA: las variantes que la Tesis dice reconocer, contra el codigo');
  console.log('='.repeat(78));
  const documentadas = [];
  for (const grupo of BASE) {
    for (const mensaje of grupo.mensajes) {
      const r = await crear().enviar(mensaje, { productos: PRODUCTOS });
      const det = detectar(r);
      const ok = det === grupo.intencion;
      documentadas.push({ intencion: grupo.intencion, mensaje, detectado: det, ok });
      console.log(
        `  ${ok ? 'OK  ' : 'FALLA'}  ${mensaje.padEnd(20)} -> ${det.padEnd(14)} (esperada: ${grupo.intencion})`
      );
    }
  }
  const docOk = documentadas.filter(d => d.ok).length;
  console.log();
  console.log(`  Reconocidas: ${docOk}/${documentadas.length} (${pct(docOk, documentadas.length)} %)`);
  const noReconocidas = documentadas.filter(d => !d.ok);

  // ---------- 2. MUTACION SISTEMATICA ----------
  console.log();
  console.log('='.repeat(78));
  console.log('2. MUTACION SISTEMATICA: variantes de forma sobre las ya reconocidas');
  console.log('='.repeat(78));
  const mutados = [];
  for (const grupo of BASE) {
    for (const mensaje of grupo.mensajes) {
      // solo mutamos lo que el sistema ya reconoce: si la base falla, la
      // mutacion no aporta informacion sobre la regla de mutacion.
      if (!documentadas.find(d => d.mensaje === mensaje && d.ok)) continue;
      for (const regla of REGLAS) {
        for (const mutado of regla.aplicar(mensaje)) {
          if (mutado === mensaje) continue;
          const r = await crear().enviar(mutado, { productos: PRODUCTOS });
          const det = detectar(r);
          mutados.push({
            intencion: grupo.intencion, base: mensaje, regla: regla.id,
            reglaNombre: regla.nombre, mensaje: mutado, detectado: det,
            ok: det === grupo.intencion,
          });
        }
      }
    }
  }
  const acertados = mutados.filter(m => m.ok);
  const fallidos = mutados.filter(m => !m.ok);
  const fallback = mutados.filter(m => m.detectado === 'fallback');
  const precision = pct(acertados.length, mutados.length);
  const tasaFallback = pct(fallback.length, mutados.length);
  const invocadas = Object.keys(cuenta(mutados.map(m => m.intencion)));
  const alcanzadas = invocadas.filter(i => mutados.some(m => m.intencion === i && m.ok));
  const cobertura = pct(alcanzadas.length, invocadas.length);

  console.log(`  Mensajes base reconocidos y mutados: ${mutados.length}`);
  console.log(`  PRECISION (rutea a la intencion esperada): ${precision} %  (${acertados.length}/${mutados.length})`);
  console.log(`  TASA DE FALLBACK (cae en "No entendi"):     ${tasaFallback} %  (${fallback.length}/${mutados.length})`);
  console.log(`  COBERTURA DEL CATALOGO (intenciones que sobreviven): ${cobertura} %  (${alcanzadas.length}/${invocadas.length})`);
  console.log();
  console.log('  Desglose por regla (aciertos/total):');
  const porRegla = {};
  for (const m of mutados) {
    porRegla[m.regla] = porRegla[m.regla] || { nombre: m.reglaNombre, ok: 0, total: 0 };
    porRegla[m.regla].total++;
    if (m.ok) porRegla[m.regla].ok++;
  }
  for (const r of REGLAS) {
    const d = porRegla[r.id];
    if (!d) { console.log(`    ${r.id} ${r.nombre.padEnd(42)} (sin casos generados)`); continue; }
    const p = pct(d.ok, d.total);
    console.log(`    ${r.id} ${r.nombre.padEnd(42)} ${String(p).padStart(5)} %  (${d.ok}/${d.total})`);
  }
  console.log();
  console.log('  Primeros 12 fallos:');
  for (const f of fallidos.slice(0, 12)) {
    console.log(`    ${f.regla}  ${JSON.stringify(f.mensaje).padEnd(34)} -> ${f.detectado}`);
  }

  // ---------- 3. REPLAY DE LA TABLA 7 ----------
  console.log();
  console.log('='.repeat(78));
  console.log('3. REPLAY DE LOS CASOS DE LA TABLA 7 (con estado conversacional real)');
  console.log('='.repeat(78));
  const replay = [];
  for (const caso of CASOS_TABLA7) {
    const runner = crear();
    const obs = [];
    for (const paso of caso.pasos) {
      const r = await runner.enviar(paso.mensaje, { productos: PRODUCTOS });
      obs.push({ mensaje: paso.mensaje, detectado: detectar(r), salida: String(r.mensaje).split('\n')[0].slice(0, 58) });
    }
    replay.push({ ...caso, observed: obs });
    console.log(`  ${caso.id}  ${caso.etiqueta}`);
    for (const o of obs) {
      console.log(`        ${JSON.stringify(o.mensaje).padEnd(20)} -> ${o.detectado.padEnd(14)} | ${o.salida}`);
    }
  }

  const resultado = {
    generado: new Date().toISOString(),
    flujo: path.relative(RAIZ, FLUJO).replace(/\\/g, '/'),
    node: 'Bot Router',
    nota_metodologica:
      'Cada mensaje se evalua con estado conversacional limpio (modo=menu, carrito vacio). ' +
      'Se mide la CAPA DE CLASIFICACION, no el flujo de extremo a extremo.',
    definiciones: {
      precision: 'Porcentaje de mensajes que rutean a la intencion esperada.',
      cobertura_del_catalogo:
        'Porcentaje de las invocadas del catalogo que el clasificador sigue ' +
        'alcanzando bajo mutacion.',
      tasa_de_fallback:
        'Porcentaje de mensajes que caen en la rama por defecto ("No entendi ese comando").',
    },
    auditoria_variantes_documentadas: {
      total: documentadas.length,
      recognized: docOk,
      porcentaje: pct(docOk, documentadas.length),
      no_reconocidas: noReconocidas,
      detalle: documentadas,
    },
    mutacion: {
      mensajes: mutados.length,
      precision,
      cobertura_del_catalogo: cobertura,
      tasa_de_fallback: tasaFallback,
      por_regla: porRegla,
      fallos: fallidos,
    },
    replay_tabla7: replay,
  };
  fs.writeFileSync(SALIDA, JSON.stringify(resultado, null, 2), 'utf8');
  console.log();
  console.log('Resultados escritos en: ' + path.relative(RAIZ, SALIDA));
})();
