import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Adjunta el JWT a cada request (misma clave que authService).
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('crm_token')
  if (token) {
    config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response) {
      const msg = error.response.data?.detail || error.response.statusText
      return Promise.reject(new Error(msg))
    }
    if (error.request) {
      return Promise.reject(new Error('Error de conexión con el servidor'))
    }
    return Promise.reject(error)
  }
)

export function listSales(params = {}) {
  return api.get('/sales/', { params }).then((r) => r.data)
}

export function getSale(id) {
  return api.get(`/sales/${id}`).then((r) => r.data)
}

export function confirmSale(id) {
  return api.post(`/sales/${id}/confirm`).then((r) => r.data)
}

export function completeSale(id) {
  return api.post(`/sales/${id}/complete`).then((r) => r.data)
}

export function cancelSale(id) {
  return api.post(`/sales/${id}/cancel`).then((r) => r.data)
}

export function searchTicket({ cliente, fecha }) {
  return api
    .get('/sales/ticket', { params: { cliente, fecha } })
    .then((r) => r.data)
}

export function getVentasMetrics(params = {}) {
  return api.get('/metrics/ventas', { params }).then((r) => r.data)
}
