import axios from 'axios'

const STORAGE_KEY = 'crm_user'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

/* ─────────────── Backend auth ─────────────── */

export async function login(email) {
  const { data } = await api.post('/auth/login', { email })
  return {
    id: data.id,
    email: data.email,
    nombre: data.nombre,
    apellido: data.apellido,
    role: data.role,
    avatar: null,
  }
}

/* ─────────────── sessionStorage helpers ─────────────── */

export function getStoredUser() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    sessionStorage.removeItem(STORAGE_KEY)
    return null
  }
}

export function saveUser(userData) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(userData))
}

export function updateUser(updates) {
  const current = getStoredUser()
  if (!current) return null
  const updated = { ...current, ...updates }
  saveUser(updated)
  return updated
}
