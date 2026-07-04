import { useState, useEffect, useCallback } from 'react'
import { getProducts, createProduct as apiCreate, updateProduct as apiUpdate, deleteProduct as apiDelete } from '../services/productService.js'
import { toast } from 'sonner'

export default function useProducts() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ searchTerm: '' })

  const refreshProducts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (filters.searchTerm) params.q = filters.searchTerm
      const res = await getProducts(params)
      setProducts(res.items || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

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
    refreshProducts,
    createProduct,
    updateProduct,
    deleteProduct,
  }
}
