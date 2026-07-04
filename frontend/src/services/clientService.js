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

export function getClients(params = {}) {
  return api.get('/clients/', { params }).then((r) => r.data)
}

export function getClient(id) {
  return api.get(`/clients/${id}`).then((r) => r.data)
}

export function createClient(data) {
  return api.post('/clients/', data).then((r) => r.data)
}

export function updateClient(id, data) {
  return api.patch(`/clients/${id}`, data).then((r) => r.data)
}

export function deleteClient(id) {
  return api.delete(`/clients/${id}`)
}

export function getInactiveClients(params = {}) {
  return api.get('/clients/inactive', { params }).then((r) => r.data)
}

export function restoreClient(id) {
  return api.patch(`/clients/${id}/restore`).then((r) => r.data)
}

export function getClientProductos(clientId) {
  return api.get(`/clients/${clientId}/productos`).then((r) => r.data)
}

export function addClientProducto(clientId, data) {
  return api.post(`/clients/${clientId}/productos`, data).then((r) => r.data)
}

export function setClientProductos(clientId, data) {
  return api.put(`/clients/${clientId}/productos`, data).then((r) => r.data)
}

export function removeClientProducto(clientId, productoId) {
  return api.delete(`/clients/${clientId}/productos/${productoId}`)
}

export async function exportClientsToExcel() {
  try {
    const response = await api.get('/clients/export', { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'clientes.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (err) {
    const { toast } = await import('sonner')
    toast.error(err.message || 'Error al exportar Excel')
    throw err
  }
}
