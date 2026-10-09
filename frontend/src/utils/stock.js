// Utilidades de stock — lógica pura compartida por el panel de stock
// (/stock) y el banner de alertas de la página de métricas.

// Umbral de stock crítico. Espejo de LOW_STOCK_THRESHOLD en
// backend/src/core/config.py — el frontend no puede importar el backend,
// así que se mantiene como constante local (mantener sincronizados).
export const LOW_STOCK_THRESHOLD = 5

// Banda de un producto (criterios del dashboard: queries.py get_stock_summary):
// - out_of_stock: stock <= 0
// - low_stock:    0 < stock <= umbral
// - normal:       stock > umbral (o sin dato numérico: no se alerta sin dato)
export function getStockBand(stock, threshold = LOW_STOCK_THRESHOLD) {
  if (stock == null || !Number.isFinite(Number(stock))) return 'normal'
  const s = Number(stock)
  if (s <= 0) return 'out_of_stock'
  if (s <= threshold) return 'low_stock'
  return 'normal'
}

// Resumen de stock del catálogo activo: bandas disjuntas + conteos.
// Paridad con dashboard/queries.py get_stock_summary():
// solo productos activos, ordenadas por stock ascendente (lo más urgente
// primero) y luego por nombre; counts.alert = out_of_stock + low_stock.
export function computeStockBands(products = [], threshold = LOW_STOCK_THRESHOLD) {
  const activos = (products ?? []).filter((p) => p && p.activo !== false)
  const bands = { out_of_stock: [], low_stock: [], normal: [] }

  for (const product of activos) {
    bands[getStockBand(product.stock, threshold)].push(product)
  }

  const porStockAsc = (a, b) =>
    Number(a.stock ?? 0) - Number(b.stock ?? 0) ||
    String(a.nombre ?? '').localeCompare(String(b.nombre ?? ''), 'es')
  bands.out_of_stock.sort(porStockAsc)
  bands.low_stock.sort(porStockAsc)
  bands.normal.sort(porStockAsc)

  return {
    threshold,
    ...bands,
    counts: {
      out_of_stock: bands.out_of_stock.length,
      low_stock: bands.low_stock.length,
      normal: bands.normal.length,
      alert: bands.out_of_stock.length + bands.low_stock.length,
    },
  }
}
