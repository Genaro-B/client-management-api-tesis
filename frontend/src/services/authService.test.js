import { login, getStoredUser, saveUser } from './authService.js'

// axios.create({...}) corre al importar el módulo → el mock debe devolver
// el instance (con post/get) desde el factory, no recién en beforeEach.
const mocks = vi.hoisted(() => {
  const post = vi.fn()
  const get = vi.fn()
  const create = vi.fn(() => ({ post, get }))
  return { create, post, get }
})

vi.mock('axios', () => ({
  default: { create: mocks.create },
}))

beforeEach(() => {
  // create NO se limpia: su única llamada (la del import del módulo) es
  // justamente la que verifica la baseURL /api/v1.
  mocks.post.mockClear()
  mocks.post.mockResolvedValue({ data: {} })
})

describe('authService', () => {
  it('login hace POST a /auth/login con { email } y mapea la respuesta', async () => {
    mocks.post.mockResolvedValue({
      data: {
        id: 8,
        email: 'admin@utn.edu.ar',
        nombre: 'Genaro',
        apellido: 'Busto',
        role: 'admin',
      },
    })

    const user = await login('admin@utn.edu.ar')

    // El instance se crea con baseURL /api/v1 → endpoint completo /api/v1/auth/login
    expect(mocks.create).toHaveBeenCalledWith(
      expect.objectContaining({ baseURL: '/api/v1' }),
    )
    expect(mocks.post).toHaveBeenCalledWith('/auth/login', { email: 'admin@utn.edu.ar' })
    expect(user).toEqual({
      id: 8,
      email: 'admin@utn.edu.ar',
      nombre: 'Genaro',
      apellido: 'Busto',
      role: 'admin',
      avatar: null,
    })
  })

  it('login con rol no-admin sigue mapeando la respuesta completa', async () => {
    mocks.post.mockResolvedValue({
      data: {
        id: 3,
        email: 'cliente@example.com',
        nombre: 'María',
        apellido: 'López',
        role: 'cliente',
      },
    })

    const user = await login('cliente@example.com')

    expect(mocks.post).toHaveBeenCalledWith('/auth/login', { email: 'cliente@example.com' })
    expect(user).toEqual({
      id: 3,
      email: 'cliente@example.com',
      nombre: 'María',
      apellido: 'López',
      role: 'cliente',
      avatar: null,
    })
  })

  it('login propaga el error cuando el backend rechaza', async () => {
    mocks.post.mockRejectedValue(new Error('Email no registrado'))

    await expect(login('inexistente@example.com')).rejects.toThrow('Email no registrado')
  })

  it('getStoredUser devuelve null cuando no hay sesión guardada', () => {
    expect(getStoredUser()).toBeNull()
  })

  it('getStoredUser parsea el JSON guardado en sessionStorage', () => {
    const usuario = { id: 8, email: 'admin@utn.edu.ar', role: 'admin' }
    sessionStorage.setItem('crm_user', JSON.stringify(usuario))

    expect(getStoredUser()).toEqual(usuario)
  })

  it('saveUser hace roundtrip con sessionStorage', () => {
    const usuario = { id: 8, email: 'admin@utn.edu.ar', nombre: 'Genaro', role: 'admin' }

    saveUser(usuario)

    expect(getStoredUser()).toEqual(usuario)
  })
})