import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Topbar from './Topbar.jsx'
import { BRAND } from '../config/brand.js'

// Misma convención que StockPage.test.jsx / LoginPage.test.jsx: se mockea
// useAuth para aislar el componente del provider real.
const authMocks = vi.hoisted(() => ({
  user: { id: 1, nombre: 'Genaro', apellido: 'Busto', email: 'admin@utn.edu.ar', role: 'admin' },
  isAdmin: true,
  logout: vi.fn(),
}))

vi.mock('../hooks/useAuth.js', () => ({
  default: () => authMocks,
}))

function renderTopbar(initialPath = '/metrics') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Topbar />
    </MemoryRouter>,
  )
}

describe('Topbar', () => {
  beforeEach(() => {
    authMocks.logout.mockReset()
  })

  it('muestra el título de la página actual desde la config de navegación', () => {
    renderTopbar('/metrics')

    expect(screen.getByRole('heading', { name: 'Métricas' })).toBeInTheDocument()
  })

  it('muestra el chip de usuario con iniciales y rol desde el contexto de auth', () => {
    renderTopbar('/metrics')

    expect(screen.getByText('Genaro Busto')).toBeInTheDocument()
    expect(screen.getByText('GB')).toBeInTheDocument()
    expect(screen.getByText('Administrador')).toBeInTheDocument()
  })

  it('actualiza el título del documento según la ruta', () => {
    renderTopbar('/products')

    expect(document.title).toBe(`Productos · ${BRAND.name}`)
  })
})
