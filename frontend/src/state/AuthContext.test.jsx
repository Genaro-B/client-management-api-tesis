import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext.jsx'

// Se mockea DIRECTAMENTE el servicio (patrón D3 para niveles superiores):
// aísla el contexto sin acoplarse al mock de axios.
const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  changePassword: vi.fn(),
  getStoredUser: vi.fn(),
  saveUser: vi.fn(),
  updateUser: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}))

vi.mock('../services/authService.js', () => ({
  login: mocks.login,
  changePassword: mocks.changePassword,
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
  password_change_required: false,
  avatar: null,
}

const adminUserConFlag = {
  ...adminUser,
  password_change_required: true,
}

const clienteUser = {
  id: 3,
  email: 'cliente@example.com',
  nombre: 'María',
  apellido: 'López',
  role: 'cliente',
  password_change_required: false,
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
      <span>{captured.user?.password_change_required ? 'debe-cambiar' : 'sin-cambio'}</span>
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
  mocks.changePassword.mockReset().mockResolvedValue({ status: 'ok' })
  mocks.getStoredUser.mockReset().mockReturnValue(null)
  mocks.saveUser.mockClear()
  mocks.toastSuccess.mockClear()
  sessionStorage.clear()
})

describe('AuthContext', () => {
  it('restaura la sesión guardada en el inicio', async () => {
    mocks.getStoredUser.mockReturnValue(adminUser)

    renderProvider()

    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()
    expect(screen.getByText('autenticado')).toBeInTheDocument()
    expect(screen.getByText('admin')).toBeInTheDocument()
  })

  it('login con email y password setea el usuario y dispara el toast', async () => {
    mocks.login.mockResolvedValue(adminUser)

    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar', 'cambiar123')
    })

    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()
    expect(mocks.login).toHaveBeenCalledWith('admin@utn.edu.ar', 'cambiar123')
    expect(mocks.saveUser).toHaveBeenCalledWith(adminUser)
    expect(mocks.toastSuccess).toHaveBeenCalledWith('Bienvenido, Genaro')
  })

  it('login con password_change_required expone el flag del usuario', async () => {
    mocks.login.mockResolvedValue(adminUserConFlag)

    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar', 'cambiar123')
    })

    expect(await screen.findByText('debe-cambiar')).toBeInTheDocument()
  })

  it('login con error setea error y relanza la excepción', async () => {
    mocks.login.mockRejectedValue(new Error('Credenciales inválidas'))

    renderProvider()

    await act(async () => {
      await expect(captured.login('inexistente@example.com', 'x')).rejects.toThrow('Credenciales inválidas')
    })

    expect(await screen.findByText('Credenciales inválidas')).toBeInTheDocument()
    expect(mocks.toastSuccess).not.toHaveBeenCalled()
  })

  it('changePassword llama al servicio y actualiza el flag del usuario', async () => {
    mocks.login.mockResolvedValue(adminUserConFlag)

    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar', 'cambiar123')
    })

    await act(async () => {
      const result = await captured.changePassword('cambiar123', 'nuevaSegura1')
      expect(result).toEqual({ status: 'ok' })
    })

    expect(mocks.changePassword).toHaveBeenCalledWith('cambiar123', 'nuevaSegura1')
    // El flag se limpia en el usuario en memoria
    expect(captured.user.password_change_required).toBe(false)
    expect(await screen.findByText('sin-cambio')).toBeInTheDocument()
  })

  it('changePassword con error relanza y mantiene el flag', async () => {
    mocks.login.mockResolvedValue(adminUserConFlag)
    mocks.changePassword.mockRejectedValue(new Error('Password actual incorrecta'))

    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar', 'cambiar123')
    })

    await act(async () => {
      await expect(captured.changePassword('mala', 'nuevaSegura1')).rejects.toThrow('Password actual incorrecta')
    })

    expect(captured.user.password_change_required).toBe(true)
  })

  it('logout limpia el usuario y el token de sessionStorage', async () => {
    renderProvider()

    await act(async () => {
      await captured.login('admin@utn.edu.ar', 'cambiar123')
    })
    sessionStorage.setItem('crm_token', 'jwt-token-123')
    expect(await screen.findByText('Genaro (admin@utn.edu.ar)')).toBeInTheDocument()

    act(() => captured.logout())

    expect(await screen.findByText('anonimo')).toBeInTheDocument()
    expect(screen.getByText('invitado')).toBeInTheDocument()
    expect(sessionStorage.getItem('crm_user')).toBeNull()
    expect(sessionStorage.getItem('crm_token')).toBeNull()
    expect(mocks.toastSuccess).toHaveBeenCalledWith('Sesión cerrada correctamente')
  })

  it('isAdmin es false cuando el rol es cliente', async () => {
    mocks.login.mockResolvedValue(clienteUser)

    renderProvider()

    await act(async () => {
      await captured.login('cliente@example.com', 'x')
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