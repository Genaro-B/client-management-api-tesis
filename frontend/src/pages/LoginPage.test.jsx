import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './LoginPage.jsx'

// D4: se mockea el hook directamente — la página se prueba aislada,
// sin AuthProvider real (su cobertura vive en AuthContext.test.jsx).
const authMocks = vi.hoisted(() => ({
  login: vi.fn(),
  setError: vi.fn(),
  error: null,
}))

vi.mock('../hooks/useAuth.js', () => ({
  default: () => ({
    login: authMocks.login,
    loading: false,
    error: authMocks.error,
    setError: authMocks.setError,
  }),
}))

function renderLoginPage() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

beforeEach(() => {
  authMocks.login.mockReset().mockResolvedValue({
    id: 8,
    email: 'admin@utn.edu.ar',
    nombre: 'Genaro',
    role: 'admin',
  })
  authMocks.setError.mockClear()
  authMocks.error = null
})

describe('LoginPage', () => {
  it('renderiza el formulario con el título "Iniciar sesión"', () => {
    renderLoginPage()

    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ingrese su email institucional')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('submit con email válido llama login() y navega a /dashboard', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.type(
      screen.getByPlaceholderText('Ingrese su email institucional'),
      'admin@utn.edu.ar',
    )
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authMocks.login).toHaveBeenCalledWith('admin@utn.edu.ar')
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })

  it('submit con email vacío muestra el error y no llama login', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authMocks.setError).toHaveBeenCalledWith('Ingresá tu email')
    expect(authMocks.login).not.toHaveBeenCalled()
  })

  it('el quick login de admin llama login() con admin@utn.edu.ar y navega', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.click(screen.getByRole('button', { name: 'Acceso administrador — inicio rápido' }))

    expect(authMocks.login).toHaveBeenCalledWith('admin@utn.edu.ar')
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })

  it('muestra el error cuando useAuth lo provee', () => {
    authMocks.error = 'Email no registrado'

    renderLoginPage()

    expect(screen.getByText('Email no registrado')).toBeInTheDocument()
  })
})