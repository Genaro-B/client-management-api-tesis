import { useState, useEffect, useCallback } from 'react'
import { getProducts, createProduct as apiCreate, updateProduct as apiUpdate, deleteProduct as apiDelete } from '../services/productService.js'
import { toast } from 'sonner'

const PAGE_SIZE = 20

export default function useProducts() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ searchTerm: '' })
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)

  // Al cambiar los filtros, la página vuelve a la 1
  useEffect(() => {
    setPage(1)
  }, [filters])

  const refreshProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { limit: PAGE_SIZE, offset: (page - 1) * PAGE_SIZE }
      if (filters.searchTerm) params.q = filters.searchTerm
      const res = await getProducts(params)
      setProducts(res.items || [])
      setTotal(res.total || 0)
      const tp = Math.max(1, Math.ceil((res.total || 0) / PAGE_SIZE))
      setTotalPages(tp)
      // Si la página actual quedó fuera de rango (p. ej. se borró el último ítem
      // de la última página), volvemos a la última página válida.
      if (page > tp) setPage(tp)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters, page])

  useEffect(() => {
    refreshProducts()
  }, [refreshProducts])

  const createProduct = async (data) => {
    try {
      const product = await apiCreate(data)
      setProducts((prev) => [...prev, product])
      toast.success('Producto creado correctamente')
      return product
    } catch (err) {
      toast.error(err.message || 'Error al crear el producto')
      throw err
    }
  }

  const updateProduct = async (id, data) => {
    try {
      const product = await apiUpdate(id, data)
      setProducts((prev) => prev.map((p) => (p.id === id ? product : p)))
      toast.success('Producto actualizado correctamente')
      return product
    } catch (err) {
      toast.error(err.message || 'Error al actualizar el producto')
      throw err
    }
  }

  const deleteProduct = async (id) => {
    try {
      await apiDelete(id)
      setProducts((prev) => prev.filter((p) => p.id !== id))
      toast.success('Producto eliminado correctamente')
    } catch (err) {
      toast.error(err.message || 'Error al eliminar el producto')
      throw err
    }
  }

  return {
    products,
    loading,
    error,
    filters,
    setFilters,
    page,
    setPage,
    totalPages,
    total,
    refreshProducts,
    createProduct,
    updateProduct,
    deleteProduct,
  }
}
