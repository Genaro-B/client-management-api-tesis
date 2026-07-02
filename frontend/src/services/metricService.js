import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
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

export function getDashboard() {
  return api.get('/metrics/dashboard').then((r) => r.data)
}
