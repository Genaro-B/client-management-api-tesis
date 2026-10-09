// Regresión: desde que el backend exige JWT (ef8f26c), los services protegidos
// DEBEN adjuntar Authorization: Bearer en cada request. Cada uno crea su propia
// instancia axios, así que el interceptor de authService NO les llega: sin este
// fix el backend responde 401 y las páginas pintan "Error de conexión".

const mocks = vi.hoisted(() => {
  const requestUse = vi.fn()
  const responseUse = vi.fn()
  const noop = vi.fn()
  const create = vi.fn(() => ({
    get: noop,
    post: noop,
    put: noop,
    patch: noop,
    delete: noop,
    interceptors: { request: { use: requestUse }, response: { use: responseUse } },
  }))
  return { create, requestUse, responseUse }
})

vi.mock('axios', () => ({
  default: { create: mocks.create },
}))

const PROTECTED_SERVICES = [
  './clientService.js',
  './metricService.js',
  './productService.js',
  './interactionService.js',
  './adminBotService.js',
]

beforeEach(() => {
  vi.resetModules()
  mocks.requestUse.mockClear()
  sessionStorage.clear()
})

describe.each(PROTECTED_SERVICES)('%s', (mod) => {
  it('adjunta Authorization: Bearer cuando hay token en sessionStorage', async () => {
    sessionStorage.setItem('crm_token', 'tok-123')
    await import(mod)
    expect(mocks.requestUse).toHaveBeenCalledTimes(1)
    const fn = mocks.requestUse.mock.calls[0][0]
    const config = fn({ headers: { 'Content-Type': 'application/json' } })
    expect(config.headers.Authorization).toBe('Bearer tok-123')
    expect(config.headers['Content-Type']).toBe('application/json')
  })

  it('no agrega Authorization cuando no hay token', async () => {
    await import(mod)
    expect(mocks.requestUse).toHaveBeenCalledTimes(1)
    const fn = mocks.requestUse.mock.calls[0][0]
    const config = fn({ headers: { 'Content-Type': 'application/json' } })
    expect(config.headers.Authorization).toBeUndefined()
  })
})
