import {
  login,
  changePassword,
  getStoredUser,
  saveUser,
  getToken,
} from './authService.js'

// axios.create({...}) corre al importar el módulo → el mock debe devolver
// el instance (con post/get/interceptors) desde el factory, no recién en beforeEach.
const mocks = vi.hoisted(() => {
  const post = vi.fn()
  const get = vi.fn()
  // Captura los interceptores registrados en el import del módulo (el vi.fn
  // recibe la función y la guarda para usarla en los tests).
  const requestInterceptor = { fn: null }
  const responseInterceptor = { fn: null }
  const requestUse = vi.fn((fn) => {
    requestInterceptor.fn = fn
    return fn
  })
  const responseUse = vi.fn((onFulfilled, onRejected) => {
    // El error handler es el 2º argumento de interceptors.response.use
    responseInterceptor.fn = onRejected
    return onFulfilled
  })
  const create = vi.fn(() => ({
    post,
    get,
    interceptors: { request: { use: requestUse }, response: { use: responseUse } },
  }))
  return { create, post, get, requestUse, responseUse, requestInterceptor, responseInterceptor }
})

vi.mock('axios', () => ({
  default: { create: mocks.create },
}))

beforeEach(() => {
  // create NO se limpia: su única llamada (la del import del módulo) es
  // justamente la que verifica la baseURL /api/v1.
  mocks.post.mockClear()
  mocks.post.mockResolvedValue({ data: {} })
  mocks.requestUse.mockClear()
  mocks.responseUse.mockClear()
  sessionStorage.clear()
})

describe('authService', () => {
  it('login hace POST a /auth/login con { email, password }', async () => {
    mocks.post.mockResolvedValue({
      data: {
        access_token: 'jwt-token-123',
        token_type: 'bearer',
        user: {
          id: 8,
          email: 'admin@utn.edu.ar',
          nombre: 'Genaro',
          apellido: 'Busto',
          role: 'admin',
          password_change_required: false,
        },
      },
    })

    const user = await login('admin@utn.edu.ar', 'cambiar123')

    expect(mocks.create).toHaveBeenCalledWith(
      expect.objectContaining({ baseURL: '/api/v1' }),
    )
    expect(mocks.post).toHaveBeenCalledWith('/auth/login', {
      email: 'admin@utn.edu.ar',
      password: 'cambiar123',
    })
    expect(user).toEqual({
      id: 8,
      email: 'admin@utn.edu.ar',
      nombre: 'Genaro',
      apellido: 'Busto',
      role: 'admin',
      password_change_required: false,
      avatar: null,
    })
  })

  it('login guarda el access_token en sessionStorage', async () => {
    mocks.post.mockResolvedValue({
      data: {
        access_token: 'jwt-token-123',
        user: { id: 8, email: 'a@x.com', role: 'admin', password_change_required: false },
      },
    })

    await login('a@x.com', 'cambiar123')

    expect(sessionStorage.getItem('crm_token')).toBe('jwt-token-123')
  })

  it('login propaga el error cuando el backend rechaza', async () => {
    mocks.post.mockRejectedValue(new Error('Credenciales inválidas'))

    await expect(login('inexistente@example.com', 'x')).rejects.toThrow('Credenciales inválidas')
    expect(sessionStorage.getItem('crm_token')).toBeNull()
  })

  it('el interceptor de request agrega Authorization: Bearer cuando hay token', () => {
    const requestInterceptor = mocks.requestInterceptor.fn
    sessionStorage.setItem('crm_token', 'jwt-token-123')

    const config = requestInterceptor({ headers: {}, url: '/clients/' })

    expect(config.headers.Authorization).toBe('Bearer jwt-token-123')
  })

  it('el interceptor de request NO agrega Authorization sin token', () => {
    const requestInterceptor = mocks.requestInterceptor.fn
    sessionStorage.removeItem('crm_token')

    const config = requestInterceptor({ headers: {}, url: '/clients/' })

    expect(config.headers.Authorization).toBeUndefined()
  })

  it('el interceptor de response limpia la sesión ante 401 (token vencido)', async () => {
    const responseInterceptor = mocks.responseInterceptor.fn
    sessionStorage.setItem('crm_token', 'vencido')
    sessionStorage.setItem('crm_user', JSON.stringify({ id: 8, email: 'a@x.com' }))

    const error = { response: { status: 401 }, config: { url: '/clients/' } }
    await expect(responseInterceptor(error)).rejects.toBe(error)

    expect(sessionStorage.getItem('crm_token')).toBeNull()
    expect(sessionStorage.getItem('crm_user')).toBeNull()
  })

  it('el interceptor de response NO limpia la sesión ante 401 del login', async () => {
    const responseInterceptor = mocks.responseInterceptor.fn
    sessionStorage.setItem('crm_token', 'previo')

    const error = { response: { status: 401 }, config: { url: '/auth/login' } }
    await expect(responseInterceptor(error)).rejects.toBe(error)

    expect(sessionStorage.getItem('crm_token')).toBe('previo')
  })

  it('changePassword hace POST a /auth/change-password con ambas passwords', async () => {
    mocks.post.mockResolvedValue({ data: { status: 'ok' } })

    const result = await changePassword('cambiar123', 'nuevaSegura1')

    expect(mocks.post).toHaveBeenCalledWith('/auth/change-password', {
      current_password: 'cambiar123',
      new_password: 'nuevaSegura1',
    })
    expect(result).toEqual({ status: 'ok' })
  })

  it('getToken devuelve el token guardado o null', () => {
    expect(getToken()).toBeNull()
    sessionStorage.setItem('crm_token', 'abc')
    expect(getToken()).toBe('abc')
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