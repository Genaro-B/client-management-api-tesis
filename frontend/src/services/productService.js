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

export function getProducts(params = {}) {
  return api.get('/products/', { params }).then((r) => r.data)
}

export function getProduct(id) {
  return api.get(`/products/${id}`).then((r) => r.data)
}

export function createProduct(data) {
  return api.post('/products/', data).then((r) => r.data)
}

export function updateProduct(id, data) {
  return api.patch(`/products/${id}`, data).then((r) => r.data)
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}`)
}

export function getInactiveProducts(params = {}) {
  return api.get('/products/inactive', { params }).then((r) => r.data)
}

export function restoreProduct(id) {
  return api.patch(`/products/${id}/restore`).then((r) => r.data)
}

export async function exportProductsToExcel() {
  try {
    const response = await api.get('/products/export', { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'productos.xlsx'
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
