import { render, screen } from '@testing-library/react'
import ProductTable from './ProductTable.jsx'

const baseProps = {
  isAdmin: false,
  page: 1,
  totalPages: 1,
  total: 2,
  onPageChange: vi.fn(),
}

const producto = (overrides) => ({
  id: 1,
  nombre: 'Producto',
  precio: 100,
  stock: 10,
  categoria: 'General',
  activo: true,
  fecha_registro: '2026-01-01',
  ...overrides,
})

function rowFor(product) {
  render(<ProductTable {...baseProps} products={[product]} />)
  return screen.getByText(product.nombre).closest('tr')
}

describe('ProductTable — resaltado de umbral de stock', () => {
  it('stock = 0: número en rojo y fila agotada', () => {
    const row = rowFor(producto({ nombre: 'Agotado', stock: 0 }))

    expect(screen.getByText('0')).toHaveClass('text-red-500')
    expect(row.className).toContain('bg-red-50')
  })

  it('stock = 5 (umbral exacto): número en ámbar y fila crítica', () => {
    const row = rowFor(producto({ nombre: 'En umbral', stock: 5 }))

    expect(screen.getByText('5')).toHaveClass('text-amber-500')
    expect(row.className).toContain('bg-amber-50')
  })

  it('stock = 6 (sobre el umbral): sin resaltado', () => {
    const row = rowFor(producto({ nombre: 'Sano', stock: 6 }))

    expect(screen.getByText('6')).toHaveClass('text-slate-600')
    expect(row.className).not.toContain('bg-red-50')
    expect(row.className).not.toContain('bg-amber-50')
  })
})
