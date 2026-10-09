import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import StockPage from './StockPage.jsx'

const productMocks = vi.hoisted(() => ({ getProducts: vi.fn() }))

vi.mock('../services/productService.js', () => ({
  getProducts: productMocks.getProducts,
}))

// Misma convención que LoginPage.test.jsx: se mockea useAuth para aislar
// la página (Sidebar/Topbar consumen el mismo hook).
const authMocks = vi.hoisted(() => ({
  user: { id: 1, nombre: 'Genaro', apellido: 'Busto', email: 'admin@utn.edu.ar', role: 'admin' },
  isAdmin: true,
  logout: vi.fn(),
}))

vi.mock('../hooks/useAuth.js', () => ({
  default: () => authMocks,
}))

function renderStockPage() {
  return render(
    <MemoryRouter initialEntries={['/stock']}>
      <StockPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  productMocks.getProducts.mockReset()
  authMocks.logout.mockReset()
})

describe('StockPage', () => {
  it('muestra el estado de carga mientras pide los productos', () => {
    productMocks.getProducts.mockReturnValue(new Promise(() => {}))

    renderStockPage()

    expect(screen.getByText('Cargando stock…')).toBeInTheDocument()
  })

  it('muestra conteos por banda y agrupa productos con semáforo', async () => {
    productMocks.getProducts.mockResolvedValue({
      items: [
        { id: 1, nombre: 'Yerba', stock: 10, activo: true, categoria: 'General' },
        { id: 2, nombre: 'Azúcar', stock: 3, activo: true, categoria: 'General' },
        { id: 3, nombre: 'Café espresso', stock: 0, activo: true, categoria: 'Bebidas' },
        { id: 4, nombre: 'Mate criollo', stock: 5, activo: true, categoria: 'Bebidas' },
        { id: 5, nombre: 'Inactivo', stock: 1, activo: false, categoria: 'General' },
      ],
    })

    renderStockPage()

    expect(await screen.findByText('Panel de Stock')).toBeInTheDocument()
    // Tarjetas de conteo
    expect(screen.getByText('Agotados')).toBeInTheDocument()
    expect(screen.getByText('Críticos')).toBeInTheDocument()
    expect(screen.getByText('Normales')).toBeInTheDocument()
    expect(screen.getByText('Umbral crítico')).toBeInTheDocument()
    expect(screen.getByText('≤ 5')).toBeInTheDocument()
    // Encabezados de banda con conteo (semáforo)
    expect(
      await screen.findByRole('heading', { name: /AGOTADOS \(stock = 0\) · 1/ }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /CRÍTICOS \(stock ≤ umbral\) · 2/ }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: /NORMALES \(stock > umbral\) · 1/ }),
    ).toBeInTheDocument()
    // Productos en su banda (el inactivo no aparece)
    expect(screen.getByText('Café espresso')).toBeInTheDocument()
    expect(screen.getByText('Azúcar')).toBeInTheDocument()
    expect(screen.getByText('Mate criollo')).toBeInTheDocument()
    expect(screen.getByText('Yerba')).toBeInTheDocument()
    expect(screen.queryByText('Inactivo')).not.toBeInTheDocument()
  })

  it('muestra el vacío del catálogo cuando no hay productos activos', async () => {
    productMocks.getProducts.mockResolvedValue({ items: [] })

    renderStockPage()

    expect(
      await screen.findByText('No hay productos activos en el catálogo.'),
    ).toBeInTheDocument()
  })

  it('muestra error con reintento que vuelve a pedir los productos', async () => {
    productMocks.getProducts.mockRejectedValueOnce(new Error('sin backend'))
    const user = userEvent.setup()

    renderStockPage()

    expect(await screen.findByText('Error de conexión')).toBeInTheDocument()

    productMocks.getProducts.mockResolvedValueOnce({ items: [] })
    await user.click(screen.getByRole('button', { name: 'Reintentar conexión' }))

    expect(
      await screen.findByText('No hay productos activos en el catálogo.'),
    ).toBeInTheDocument()
    expect(productMocks.getProducts).toHaveBeenCalledTimes(2)
  })

  it('cada banda vacía muestra su mensaje', async () => {
    productMocks.getProducts.mockResolvedValue({
      items: [
        { id: 1, nombre: 'Yerba', stock: 10, activo: true, categoria: 'General' },
      ],
    })

    renderStockPage()

    expect(await screen.findByText('Sin productos agotados.')).toBeInTheDocument()
    expect(screen.getByText('Sin productos con stock crítico.')).toBeInTheDocument()
  })
})
