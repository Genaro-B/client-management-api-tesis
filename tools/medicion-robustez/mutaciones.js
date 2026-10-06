// Conjunto de mensajes y reglas de mutacion para medir la robustez del
// clasificador de intenciones del nodo "Bot Router" de n8n.
//
// TODO ESTO ES DECLARADO Y AUDITABLE: la intencion esperada de cada mensaje
// base esta escrita a mano arriba de cada entrada, y cada regla de mutacion
// esta definida abajo. No hay nada "sacado de la nada".
//
// IMPORTANTE: este conjunto NO es un conjunto de validacion independiente
// redactado por terceros (ver README.md). Mide otra cosa: que pasa cuando el
// usuario escribe una variante que el sistema NO fue disenado para entender.

/** Intenciones del catalogo del sistema, con sus variantes canonicas. */
const BASE = [
  // Menu principal
  { intencion: 'menu',        mensajes: ['hola', 'menu', 'volver'] },
  // 1 Comprar
  { intencion: 'comprar',     mensajes: ['comprar', 'quiero comprar'] },
  // 2 Catalogo
  { intencion: 'catalogo',    mensajes: ['catalogo', 'ver productos'] },
  // 3 Precios
  { intencion: 'precios',     mensajes: ['precio'] },
  // 4 Asesor
  { intencion: 'asesor',      mensajes: ['asesor', 'hablar con alguien'] },
  // 5 Otra consulta
  { intencion: 'otra',        mensajes: ['consulta', 'otra cosa'] },
  // 6 Ver carrito
  { intencion: 'carrito',     mensajes: ['carrito', 'mis productos'] },
  // 7 Finalizar compra
  { intencion: 'finalizar',   mensajes: ['finalizar', 'terminar'] },
];

/** Forma acentuada de cada palabra, solo cuando existe. */
const CON_TILDE = {
  catalogo: 'catálogo', menu: 'menú', numero: 'número',
  mas: 'más', que: 'qué', como: 'cómo',
};

/** Aplica los tildes que correspondan; devuelve null si la palabra no cambia. */
function acentuar(msg) {
  const palabras = msg.split(' ');
  let cambio = false;
  const out = palabras.map((p) => {
    const clave = p.toLowerCase();
    if (CON_TILDE[clave]) { cambio = true; return CON_TILDE[clave]; }
    return p;
  });
  return cambio ? out.join(' ') : null;
}

/** Elimina el segundo caracter de la palabra mas larga (error tipografico). */
function typo(msg) {
  const palabras = msg.split(' ');
  let idx = -1;
  let mejor = 0;
  palabras.forEach((p, i) => { if (p.length > mejor) { mejor = p.length; idx = i; } });
  if (idx < 0 || mejor < 4) return null;
  const p = palabras[idx];
  return [...palabras.slice(0, idx), p[0] + p.slice(2), ...palabras.slice(idx + 1)].join(' ');
}

/** Invierte el orden de las palabras. */
function reordenar(msg) {
  const palabras = msg.split(' ');
  if (palabras.length < 2) return null;
  return [...palabras].reverse().join(' ');
}

/**
 * Reglas de mutacion. Cada una es mecanica y deterministica: dada una entrada
 * produce siempre la misma salida. Mutan la FORMA sin cambiar la INTENCION.
 */
const REGLAS = [
  { id: 'M1', nombre: 'agregar palabras de cortesia',
    aplicar: (m) => [`por favor ${m}`, `${m} por favor`, `hola, ${m}`] },
  { id: 'M2', nombre: 'agregar o anteponer puntuacion',
    aplicar: (m) => [`${m}!`, `${m}?`, `¿${m}?`, `${m}.`] },
  { id: 'M3', nombre: 'escribir en mayusculas',
    aplicar: (m) => [m.toUpperCase()] },
  { id: 'M4', nombre: 'escribir con tildes',
    aplicar: (m) => { const r = acentuar(m); return r ? [r] : []; } },
  { id: 'M5', nombre: 'reordenar las palabras',
    aplicar: (m) => { const r = reordenar(m); return r ? [r] : []; } },
  { id: 'M6', nombre: 'error tipografico (borrar un caracter)',
    aplicar: (m) => { const r = typo(m); return r ? [r] : []; } },
  { id: 'M7', nombre: 'sustantivo en plural',
    aplicar: (m) => [`${m}s`] },
  { id: 'M8', nombre: 'envolver en una oracion',
    aplicar: (m) => [`quisiera ${m} por favor`, `necesito ${m}`, `dame ${m}`] },
];

/** Casos de la Tabla 7 de la tesis, con su secuencia previa (estado real). */
const CASOS_TABLA7 = [
  { id: 'T7-1', etiqueta: 'variacion minima fuera de catalogo',
    pasos: [{ mensaje: 'Quiero comprar jamon' }],
    nota: 'La tesis afirma 0 % (no matchea). El codigo usa includes("comprar").' },
  { id: 'T7-2', etiqueta: 'puntuacion que rompe la igualdad exacta',
    pasos: [{ mensaje: 'hola!' }],
    nota: 'El menu exige igualdad exacta (msg === "hola").' },
  { id: 'T7-3', etiqueta: 'numero fuera de rango en modo catalogo',
    pasos: [{ mensaje: '2' }, { mensaje: '10' }],
    nota: 'Requiere estar en modo catalogo. Comportamiento esperado: validacion.' },
];

module.exports = { BASE, REGLAS, CASOS_TABLA7, CON_TILDE };
