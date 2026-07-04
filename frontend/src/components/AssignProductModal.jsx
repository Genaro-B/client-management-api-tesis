import { useState, useEffect } from 'react'
import Modal from './Modal.jsx'
import { getProducts } from '../services/productService.js'
import { Loader2, Search } from 'lucide-react'

export default function AssignProductModal({ onClose, onAssign }) {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [cantidad, setCantidad] = useState(1)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getProducts({ limit: 200 })
        setProducts(res.items || [])
      } catch {
        // silent
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  const filtered = search
    ? products.filter(
        (p) =>
          p.nombre.toLowerCase().includes(search.toLowerCase()) ||
          (p.categoria && p.categoria.toLowerCase().includes(search.toLowerCase()))
      )
    : products

  const handleSelect = (product) => {
    setSelectedProduct((prev) => (prev?.id === product.id ? null : product))
    setCantidad(1)
  }

  const handleSubmit = async () => {
    if (!selectedProduct) return
    setSaving(true)
    try {
      await onAssign({
        producto_id: selectedProduct.id,
        nombre: selectedProduct.nombre,
        precio: selectedProduct.precio,
        cantidad,
      })
      onClose()
    } catch {
      // handled by hook
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title="Agregar Producto" onClose={onClose} size="lg">
      {/* Search */}
      <div className="relative mb-4">
        <Search
          size={15}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <input
          type="text"
          placeholder="Buscar producto…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2.5 pl-9 pr-3 text-[13px] text-foreground outline-none focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] transition-all duration-150"
        />
      </div>

      {/* Product list */}
      <div className="max-h-56 overflow-y-auto border border-slate-200 dark:border-slate-700 rounded-lg divide-y divide-slate-100 dark:divide-slate-700 mb-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 size={18} className="animate-spin text-slate-400" />
          </div>
        ) : filtered.length === 0 ? (
          <p className="text-[13px] text-muted-foreground text-center py-8">
            {search ? 'Sin resultados' : 'No hay productos disponibles'}
          </p>
        ) : (
          filtered.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => handleSelect(p)}
              className={`w-full text-left px-4 py-2.5 text-[13px] transition-colors duration-150 ${
                selectedProduct?.id === p.id
                  ? 'bg-primary/10 text-primary font-semibold'
                  : 'text-foreground hover:bg-slate-50 dark:hover:bg-slate-800'
              }`}
            >
              <span>{p.nombre}</span>
              <span className="text-muted-foreground ml-2 font-mono">
                ${p.precio.toLocaleString('es-AR')}
              </span>
              {p.categoria && (
                <span className="text-[11px] text-muted-foreground ml-2 opacity-60">
                  {p.categoria}
                </span>
              )}
            </button>
          ))
        )}
      </div>

      {/* Cantidad */}
      {selectedProduct && (
        <div className="mb-4">
          <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
            Cantidad
          </label>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setCantidad(Math.max(1, cantidad - 1))}
              disabled={cantidad <= 1}
              className="w-9 h-9 rounded-lg border border-slate-200 dark:border-slate-600 text-foreground text-[15px] font-semibold hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 transition-colors duration-150"
            >
              −
            </button>
            <span className="w-12 text-center text-[15px] font-semibold font-mono text-foreground">
              {cantidad}
            </span>
            <button
              type="button"
              onClick={() => setCantidad(cantidad + 1)}
              className="w-9 h-9 rounded-lg border border-slate-200 dark:border-slate-600 text-foreground text-[15px] font-semibold hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-150"
            >
              +
            </button>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2.5 pt-2">
        <button
          type="button"
          onClick={onClose}
          disabled={saving}
          className="flex-1 py-2.5 rounded-lg bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors duration-150"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!selectedProduct || saving}
          className="flex-1 py-2.5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors duration-150 flex items-center justify-center gap-2"
        >
          {saving && <Loader2 size={14} className="animate-spin" />}
          {saving ? 'Asignando…' : 'Asignar Producto'}
        </button>
      </div>
    </Modal>
  )
}
