import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext.jsx'

// Se mockea DIRECTAMENTE el servicio (patrón D3 para niveles superiores):
// aísla el contexto sin acoplarse al mock de axios.
const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  getStoredUser: vi.fn(),
  saveUser: vi.fn(),
  updateUser: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}))

vi.mock('../services/authService.js', () => ({
  login: mocks.login,
  getStoredUser: mocks.getStoredUser,
  saveUser: mocks.saveUser,
  updateUser: mocks.updateUser,
}))

vi.mock('sonner', () => ({
  toast: { success: mocks.toastSuccess, error: mocks.toastError },
}))

const adminUser = {
  id: 8,
  email: 'admin@utn.edu.ar',
  nombre: 'Genaro',
  apellido: 'Busto',
  role: 'admin',
  avatar: null,
}

const clienteUser = {
  id: 3,
  email: 'cliente@example.com',
  nombre: 'María',
  apellido: 'López',
  role: 'cliente',
  avatar: null,
}

let captured

function Probe() {
  captured = useAuth()
  return (
    <div>
      <span>{captured.user ? `${captured.user.nombre} (${captured.user.email})` : 'anonimo'}</span>
      <span>{captured.isAuthenticated ? 'autenticado' : 'invitado'}</span>
      <span>{captured.isAdmin ? 'admin' : 'no-admin'}</span>
      <span>{captured.error ?? 'sin-error'}</span>
    </div>
  )
}

function renderProvider() {
  return render(
    <AuthProvider>
      <Probe />
    </AuthProvider>,
  )
}

beforeEach(() => {
  mocks.login.mockReset().mockResolvedValue(adminUser)
  mocks.getStoredUser.mockReset().mockReturnValue(null)
  mocks.saveUser.mockClear()
  mocks.toastSuccess.mockClear()
})

describe('AuthContext', () => {
  it('restaura la sesión guardada en el inicio', async () => {
    mocks.getStoredUser.mockReturnValue(adminUser)

    renderProvider()

    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()
    expect(screen.getByText('autenticado')).toBeInTheDocument()
    expect(screen.getByText('admin')).toBeInTheDocument()
  })

  it('login exitoso setea el usuario y dispara el toast de bienvenida', async () => {
    mocks.login.mockResolvedValue(adminUser)

    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar')
    })

    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()
    expect(mocks.login).toHaveBeenCalledWith('admin@utn.edu.ar')
    expect(mocks.saveUser).toHaveBeenCalledWith(adminUser)
    expect(mocks.toastSuccess).toHaveBeenCalledWith('Bienvenido, Genaro')
  })

  it('login con error setea error y relanza la excepción', async () => {
    mocks.login.mockRejectedValue(new Error('Email no registrado'))

    renderProvider()

    await act(async () => {
      await expect(captured.login('inexistente@example.com')).rejects.toThrow('Email no registrado')
    })

    expect(await screen.findByText('Email no registrado')).toBeInTheDocument()
    expect(mocks.toastSuccess).not.toHaveBeenCalled()
  })

  it('logout limpia el usuario y dispara el toast de cierre de sesión', async () => {
    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar')
    })
    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()

    act(() => captured.logout())

    expect(await screen.findByText('anonimo')).toBeInTheDocument()
    expect(screen.getByText('invitado')).toBeInTheDocument()
    expect(sessionStorage.getItem('crm_user')).toBeNull()
    expect(mocks.toastSuccess).toHaveBeenCalledWith('Sesión cerrada correctamente')
  })

  it('isAdmin es false cuando el rol es cliente', async () => {
    mocks.login.mockResolvedValue(clienteUser)

    renderProvider()

    await act(async () => {
      await captured.login('cliente@example.com')
    })

    expect(await screen.findByText('María (cliente@example.com)')).toBeInTheDocument()
    expect(screen.getByText('autenticado')).toBeInTheDocument()
    expect(screen.getByText('no-admin')).toBeInTheDocument()
  })

  it('isAuthenticated es false sin sesión', () => {
    renderProvider()

    expect(screen.getByText('anonimo')).toBeInTheDocument()
    expect(screen.getByText('invitado')).toBeInTheDocument()
    expect(screen.getByText('no-admin')).toBeInTheDocument()
  })
})