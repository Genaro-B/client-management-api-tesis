import { LOW_STOCK_THRESHOLD, getStockBand, computeStockBands } from './stock.js'

const activo = (overrides) => ({ activo: true, categoria: 'General', ...overrides })

describe('LOW_STOCK_THRESHOLD', () => {
  it('espeja el umbral del backend (backend/src/core/config.py)', () => {
    expect(LOW_STOCK_THRESHOLD).toBe(5)
  })
})

describe('getStockBand', () => {
  it('stock = 0 (y negativo) → out_of_stock', () => {
    expect(getStockBand(0)).toBe('out_of_stock')
    expect(getStockBand(-3)).toBe('out_of_stock')
  })

  it('0 < stock <= umbral → low_stock (el umbral exacto es crítico)', () => {
    expect(getStockBand(1)).toBe('low_stock')
    expect(getStockBand(5)).toBe('low_stock')
  })

  it('stock > umbral → normal', () => {
    expect(getStockBand(6)).toBe('normal')
  })

  it('umbral personalizado', () => {
    expect(getStockBand(3, 3)).toBe('low_stock')
    expect(getStockBand(4, 3)).toBe('normal')
  })

  it('sin stock definido → normal (no se alerta sin dato)', () => {
    expect(getStockBand(undefined)).toBe('normal')
    expect(getStockBand(null)).toBe('normal')
  })
})

describe('computeStockBands', () => {
  it('separa bandas disjuntas con conteos y ordena por stock ascendente', () => {
    const products = [
      activo({ id: 1, nombre: 'Yerba', stock: 10 }),
      activo({ id: 2, nombre: 'Azúcar', stock: 3 }),
      activo({ id: 3, nombre: 'Café espresso', stock: 0 }),
      activo({ id: 4, nombre: 'Mate criollo', stock: 5 }),
    ]

    const resumen = computeStockBands(products)

    expect(resumen.threshold).toBe(5)
    expect(resumen.out_of_stock.map((p) => p.nombre)).toEqual(['Café espresso'])
    expect(resumen.low_stock.map((p) => p.nombre)).toEqual(['Azúcar', 'Mate criollo'])
    expect(resumen.normal.map((p) => p.nombre)).toEqual(['Yerba'])
    expect(resumen.counts).toEqual({
      out_of_stock: 1,
      low_stock: 2,
      normal: 1,
      alert: 3,
    })
  })

  it('el umbral exacto (5) cae en low_stock y 6 en normal', () => {
    const resumen = computeStockBands([
      activo({ id: 1, nombre: 'En el umbral', stock: 5 }),
      activo({ id: 2, nombre: 'Sobre el umbral', stock: 6 }),
    ])

    expect(resumen.low_stock.map((p) => p.stock)).toEqual([5])
    expect(resumen.normal.map((p) => p.stock)).toEqual([6])
  })

  it('todos agotados: las otras bandas quedan vacías', () => {
    const resumen = computeStockBands([
      activo({ id: 1, nombre: 'A', stock: 0 }),
      activo({ id: 2, nombre: 'B', stock: 0 }),
      activo({ id: 3, nombre: 'C', stock: -1 }),
    ])

    expect(resumen.out_of_stock).toHaveLength(3)
    expect(resumen.low_stock).toEqual([])
    expect(resumen.normal).toEqual([])
    expect(resumen.counts.alert).toBe(3)
  })

  it('lista vacía: todo en cero, sin alertas', () => {
    const resumen = computeStockBands([])

    expect(resumen.counts).toEqual({
      out_of_stock: 0,
      low_stock: 0,
      normal: 0,
      alert: 0,
    })
    expect(resumen.out_of_stock).toEqual([])
    expect(resumen.low_stock).toEqual([])
    expect(resumen.normal).toEqual([])
  })

  it('ignora productos inactivos aunque tengan stock crítico', () => {
    const resumen = computeStockBands([
      activo({ id: 1, nombre: 'Activo normal', stock: 10 }),
      { id: 2, nombre: 'Inactivo agotado', stock: 0, activo: false },
      { id: 3, nombre: 'Inactivo crítico', stock: 2, activo: false },
    ])

    expect(resumen.counts).toEqual({
      out_of_stock: 0,
      low_stock: 0,
      normal: 1,
      alert: 0,
    })
  })

  it('acepta un umbral propio sin modificar el default', () => {
    const resumen = computeStockBands(
      [activo({ id: 1, nombre: 'A', stock: 4 })],
      3,
    )

    expect(resumen.threshold).toBe(3)
    expect(resumen.normal.map((p) => p.nombre)).toEqual(['A'])
    expect(LOW_STOCK_THRESHOLD).toBe(5)
  })

  it('sin argumentos devuelve bandas vacías', () => {
    const resumen = computeStockBands()

    expect(resumen.counts.alert).toBe(0)
    expect(resumen.threshold).toBe(5)
  })
})
