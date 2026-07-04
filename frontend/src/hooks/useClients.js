import { useState, useEffect, useCallback } from 'react'
import { getClients, getClient as apiGetClient, createClient as apiCreate, updateClient as apiUpdate, deleteClient as apiDelete, addClientProducto, removeClientProducto, setClientProductos } from '../services/clientService.js'
import { toast } from 'sonner'

export default function useClients() {
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ searchTerm: '' })

  const refreshClients = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = {}
      if (filters.searchTerm) params.q = filters.searchTerm
      const res = await getClients(params)
      setClients(res.items || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    refreshClients()
  }, [refreshClients])

  const createClient = async (data) => {
    try {
      const client = await apiCreate(data)
      setClients((prev) => [...prev, client])
      toast.success('Cliente creado correctamente')
      return client
    } catch (err) {
      toast.error(err.message || 'Error al crear el cliente')
      throw err
    }
  }

  const updateClient = async (id, data) => {
    try {
      const client = await apiUpdate(id, data)
      setClients((prev) => prev.map((c) => (c.id === id ? client : c)))
      toast.success('Cliente actualizado correctamente')
      return client
    } catch (err) {
      toast.error(err.message || 'Error al actualizar el cliente')
      throw err
    }
  }

  const deleteClient = async (id) => {
    try {
      await apiDelete(id)
      setClients((prev) => prev.filter((c) => c.id !== id))
      toast.success('Cliente eliminado correctamente')
    } catch (err) {
      toast.error(err.message || 'Error al eliminar el cliente')
      throw err
    }
  }

  // ------------------------------------------------------------------
  // Productos Asignados
  // ------------------------------------------------------------------

  const refreshSingleClient = async (id) => {
    try {
      const client = await apiGetClient(id)
      setClients((prev) => prev.map((c) => (c.id === id ? client : c)))
      return client
    } catch {
      return null
    }
  }

  const assignProduct = async (clientId, producto) => {
    try {
      const productos = await addClientProducto(clientId, producto)
      await refreshSingleClient(clientId)
      toast.success('Producto asignado correctamente')
      return productos
    } catch (err) {
      toast.error(err.message || 'Error al asignar producto')
      throw err
    }
  }

  const removeAssignedProduct = async (clientId, productoId) => {
    try {
      await removeClientProducto(clientId, productoId)
      await refreshSingleClient(clientId)
      toast.success('Producto quitado correctamente')
    } catch (err) {
      toast.error(err.message || 'Error al quitar producto')
      throw err
    }
  }

  const updateProductQuantity = async (clientId, productoId, cantidad) => {
    try {
      // Fetch current productos, update the one we want, replace everything
      const client = await apiGetClient(clientId)
      const productos = (client.productos_asignados || []).map((p) =>
        p.producto_id === productoId ? { ...p, cantidad } : p
      )
      await setClientProductos(clientId, productos)
      await refreshSingleClient(clientId)
      toast.success('Cantidad actualizada correctamente')
    } catch (err) {
      toast.error(err.message || 'Error al actualizar cantidad')
      throw err
    }
  }

  return {
    clients,
    loading,
    error,
    filters,
    setFilters,
    refreshClients,
    createClient,
    updateClient,
    deleteClient,
    assignProduct,
    removeAssignedProduct,
    updateProductQuantity,
  }
}
