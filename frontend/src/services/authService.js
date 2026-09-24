import axios from 'axios'

const USER_KEY = 'crm_user'
const TOKEN_KEY = 'crm_token'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

/* ─────────────── Interceptores ─────────────── */

// Agrega el Bearer token a toda request saliente si hay sesión activa.
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
  }
  return config
})

// Ante 401 en endpoints protegidos (token vencido/inválido) limpia la sesión.
// El login NO limpia: un 401 ahí es credenciales inválidas, no sesión vencida.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes('/auth/login')
    if (error.response?.status === 401 && !isLoginRequest) {
      sessionStorage.removeItem(TOKEN_KEY)
      sessionStorage.removeItem(USER_KEY)
    }
    return Promise.reject(error)
  },
)

/* ─────────────── Backend auth ─────────────── */

export async function login(email, password) {
  const { data } = await api.post('/auth/login', { email, password })
  const { access_token: token, user } = data
  if (token) {
    sessionStorage.setItem(TOKEN_KEY, token)
  }
  return { ...user, avatar: null }
}

export async function changePassword(currentPassword, newPassword) {
  const { data } = await api.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
  return data
}

/* ─────────────── sessionStorage helpers ─────────────── */

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY)
}

export function getStoredUser() {
  try {
    const raw = sessionStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    sessionStorage.removeItem(USER_KEY)
    return null
  }
}

export function saveUser(userData) {
  sessionStorage.setItem(USER_KEY, JSON.stringify(userData))
}

export function updateUser(updates) {
  const current = getStoredUser()
  if (!current) return null
  const updated = { ...current, ...updates }
  saveUser(updated)
  return updated
}