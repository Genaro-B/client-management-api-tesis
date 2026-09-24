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
        <Route path="/change-password" element={<div>ChangePassword</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

const adminSinFlag = {
  id: 8,
  email: 'admin@utn.edu.ar',
  nombre: 'Genaro',
  role: 'admin',
  password_change_required: false,
}

const adminConFlag = {
  ...adminSinFlag,
  password_change_required: true,
}

beforeEach(() => {
  authMocks.login.mockReset().mockResolvedValue(adminSinFlag)
  authMocks.setError.mockClear()
  authMocks.error = null
})

describe('LoginPage', () => {
  it('renderiza el formulario con título, email y contraseña', () => {
    renderLoginPage()

    expect(screen.getByRole('heading', { name: 'Iniciar sesión' })).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ingrese su email institucional')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Ingrese su contraseña')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Iniciar sesión' })).toBeInTheDocument()
  })

  it('submit con email y password llama login(email, password) y navega a /dashboard', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.type(
      screen.getByPlaceholderText('Ingrese su email institucional'),
      'admin@utn.edu.ar',
    )
    await user.type(screen.getByPlaceholderText('Ingrese su contraseña'), 'cambiar123')
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authMocks.login).toHaveBeenCalledWith('admin@utn.edu.ar', 'cambiar123')
    expect(await screen.findByText('Dashboard')).toBeInTheDocument()
  })

  it('login con password_change_required navega a /change-password', async () => {
    authMocks.login.mockResolvedValue(adminConFlag)
    const user = userEvent.setup()

    renderLoginPage()

    await user.type(
      screen.getByPlaceholderText('Ingrese su email institucional'),
      'admin@utn.edu.ar',
    )
    await user.type(screen.getByPlaceholderText('Ingrese su contraseña'), 'cambiar123')
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(await screen.findByText('ChangePassword')).toBeInTheDocument()
  })

  it('submit sin email muestra el error y no llama login', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authMocks.setError).toHaveBeenCalledWith('Ingresá tu email')
    expect(authMocks.login).not.toHaveBeenCalled()
  })

  it('submit sin password muestra el error y no llama login', async () => {
    const user = userEvent.setup()

    renderLoginPage()

    await user.type(
      screen.getByPlaceholderText('Ingrese su email institucional'),
      'admin@utn.edu.ar',
    )
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authMocks.setError).toHaveBeenCalledWith('Ingresá tu contraseña')
    expect(authMocks.login).not.toHaveBeenCalled()
  })

  it('muestra el error cuando useAuth lo provee', () => {
    authMocks.error = 'Credenciales inválidas'

    renderLoginPage()

    expect(screen.getByText('Credenciales inválidas')).toBeInTheDocument()
  })

  it('no muestra el botón de acceso rápido de admin (ya no existe cuenta fija)', () => {
    renderLoginPage()

    expect(
      screen.queryByRole('button', { name: /inicio rápido/i }),
    ).not.toBeInTheDocument()
  })
})