import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import VentasPage from './VentasPage.jsx'

const salesMocks = vi.hoisted(() => ({
  getVentasMetrics: vi.fn(),
  listSales: vi.fn(),
  getSale: vi.fn(),
  confirmSale: vi.fn(),
  completeSale: vi.fn(),
  cancelSale: vi.fn(),
  searchTicket: vi.fn(),
}))

vi.mock('../services/salesService.js', () => salesMocks)

const toastMocks = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: { success: toastMocks.success, error: toastMocks.error },
}))

const authMocks = vi.hoisted(() => ({
  user: { id: 1, nombre: 'Genaro', apellido: 'Busto', email: 'admin@utn.edu.ar', role: 'admin' },
  isAdmin: true,
  logout: vi.fn(),
}))

vi.mock('../hooks/useAuth.js', () => ({
  default: () => authMocks,
}))

const METRICS = {
  summary: {
    ventas: 2,
    ingresos: 400,
    ticketPromedio: 200,
    vsPeriodoAnterior: { ventas: 100, ingresos: 50 },
  },
  serieDiaria: [{ fecha: '2026-10-01', ventas: 1, ingresos: 100 }],
  topProductos: [],
  porHorario: [],
}

const SALES = {
  items: [
    {
      id: 1, cliente_nombre: 'Juan', fecha: '2026-10-01T10:00:00',
      total: 100, estado: 'PENDIENTE',
      items: [{ producto_nombre: 'Widget', cantidad: 1, precio_unitario: 100 }],
    },
    {
      id: 2, cliente_nombre: 'Ana', fecha: '2026-10-01T11:00:00',
      total: 300, estado: 'CONFIRMADO',
      items: [{ producto_nombre: 'Gadget', cantidad: 2, precio_unitario: 150 }],
    },
  ],
  total: 2,
}

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/sales']}>
      <VentasPage />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  salesMocks.getVentasMetrics.mockResolvedValue(METRICS)
  salesMocks.listSales.mockResolvedValue(SALES)
})

describe('VentasPage', () => {
  it('muestra el estado de carga mientras pide los datos', () => {
    salesMocks.getVentasMetrics.mockReturnValue(new Promise(() => {}))
    salesMocks.listSales.mockReturnValue(new Promise(() => {}))

    renderPage()

    expect(screen.getByText('Cargando ventas…')).toBeInTheDocument()
  })

  it('muestra las cards de resumen y la tabla de ventas', async () => {
    renderPage()

    expect(await screen.findByText('Ingresos')).toBeInTheDocument()
    expect(screen.getAllByText('Ventas').length).toBeGreaterThan(0)
    expect(screen.getByText('Ticket promedio')).toBeInTheDocument()
    expect(screen.getByText('Variación')).toBeInTheDocument()
    expect(screen.getByText('$400')).toBeInTheDocument()
    expect(screen.getByText('Juan')).toBeInTheDocument()
    expect(screen.getByText('Ana')).toBeInTheDocument()
  })

  it('muestra quién confirmó la venta en la tabla', async () => {
    salesMocks.listSales.mockResolvedValue({
      items: [
        {
          id: 2, cliente_nombre: 'Ana', fecha: '2026-10-01T11:00:00',
          total: 300, estado: 'CONFIRMADO', confirmado_por_nombre: 'Ana Gomez',
          items: [{ producto_nombre: 'Gadget', cantidad: 2, precio_unitario: 150 }],
        },
      ],
      total: 1,
    })

    renderPage()

    expect(await screen.findByText('Ana Gomez')).toBeInTheDocument()
  })

  it('muestra un guion cuando la venta no tiene confirmador', async () => {
    renderPage()

    await screen.findByText('Juan')

    expect(screen.getAllByText('—').length).toBeGreaterThan(0)
  })

  it('confirma una venta PENDIENTE y refresca', async () => {
    salesMocks.confirmSale.mockResolvedValue({ id: 1, estado: 'CONFIRMADO' })
    const user = userEvent.setup()

    renderPage()
    await screen.findByText('Juan')

    const botones = screen.getAllByRole('button', { name: 'Confirmar' })
    await user.click(botones[0])

    await waitFor(() => expect(salesMocks.confirmSale).toHaveBeenCalledWith(1))
    expect(toastMocks.success).toHaveBeenCalled()
    expect(salesMocks.listSales).toHaveBeenCalledTimes(2)
  })

  it('muestra error con reintento que vuelve a pedir los datos', async () => {
    salesMocks.getVentasMetrics.mockRejectedValueOnce(new Error('sin backend'))
    const user = userEvent.setup()

    renderPage()

    expect(await screen.findByText('Error de conexión')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Reintentar conexión' }))
    expect(await screen.findByText('Juan')).toBeInTheDocument()
  })

  it('busca un ticket por cliente y muestra los productos', async () => {
    salesMocks.searchTicket.mockResolvedValue({
      cliente: 'Juan',
      ventas: [
        {
          id: 1, estado: 'CONFIRMADO', total: 100, fecha: '2026-10-01T10:00:00',
          confirmado_por_nombre: 'Ana Gomez',
          items: [{ producto_nombre: 'Widget', cantidad: 2, precio_unitario: 50 }],
        },
      ],
    })
    const user = userEvent.setup()

    renderPage()
    await screen.findByText('Juan')

    await user.type(screen.getByLabelText('Cliente'), 'Juan')
    await user.type(screen.getByLabelText('Fecha'), '2026-10-01')
    await user.click(screen.getByRole('button', { name: 'Buscar' }))

    expect(await screen.findByText(/Widget/)).toBeInTheDocument()
    expect(screen.getByText('Confirmado por: Ana Gomez')).toBeInTheDocument()
    expect(salesMocks.searchTicket).toHaveBeenCalledWith({ cliente: 'Juan', fecha: '2026-10-01' })
  })
})
