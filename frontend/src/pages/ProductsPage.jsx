import { useState } from 'react'
import { AlertCircle, Inbox, EyeOff } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import ProductFilters from '../components/ProductFilters.jsx'
import ProductTable from '../components/ProductTable.jsx'
import ProductDetailsModal from '../components/ProductDetailsModal.jsx'
import ProductFormModal from '../components/ProductFormModal.jsx'
import DeleteProductModal from '../components/DeleteProductModal.jsx'
import useProducts from '../hooks/useProducts.js'
import useAuth from '../hooks/useAuth.js'
import { exportProductsToExcel } from '../services/productService.js'

export default function ProductsPage() {
  const { user, isAdmin, logout } = useAuth()
  const {
    products,
    loading,
    error,
    filters,
    setFilters,
    refreshProducts,
    createProduct,
    updateProduct,
    deleteProduct,
  } = useProducts()

  const [selectedProduct, setSelectedProduct] = useState(null)
  const [showFormModal, setShowFormModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [deletingProduct, setDeletingProduct] = useState(null)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onNewProduct={() => { setEditingProduct(null); setShowFormModal(true) }}
          onLogout={logout}
          title="Productos"
          subtitle="Gestión del catálogo de productos"
          onExport={exportProductsToExcel}
          exportLabel="Exportar Excel"
        />
        <div className="flex-1 overflow-y-auto p-8">
          <ProductFilters
            filters={filters}
            onFiltersChange={setFilters}
          />

          {loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-[13px] text-muted-foreground">Cargando productos…</p>
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground max-w-[20rem] text-center">
                No se pudieron cargar los productos. Verificá la conexión e intentá de nuevo.
              </p>
              <button
                onClick={refreshProducts}
                className="text-[13px] font-semibold text-primary hover:text-blue-700 flex items-center gap-1"
              >
                Reintentar conexión
              </button>
            </div>
          )}

          {!loading && !error && products.length === 0 && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                <Inbox size={20} className="text-slate-400 dark:text-slate-500" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">No hay productos</p>
              <p className="text-[12px] text-muted-foreground">
                No se encontraron productos para mostrar.
              </p>
            </div>
          )}

          {!loading && !error && products.length > 0 && (
            <ProductTable
              products={products}
              isAdmin={isAdmin}
              onView={(p) => setSelectedProduct(p)}
              onEdit={(p) => { setEditingProduct(p); setShowFormModal(true) }}
              onDelete={(p) => setDeletingProduct(p)}
            />
          )}

          {!loading && !error && !isAdmin && (
            <div className="flex items-center justify-center gap-2 mt-4 py-3 px-4 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700">
              <EyeOff size={14} className="text-slate-400 dark:text-slate-500" />
              <p className="text-[12px] text-muted-foreground">
                Modo solo lectura — no tenés permisos para crear, editar o eliminar productos.
              </p>
            </div>
          )}
        </div>
      </main>

      {selectedProduct && (
        <ProductDetailsModal
          product={selectedProduct}
          isAdmin={isAdmin}
          onClose={() => setSelectedProduct(null)}
          onEdit={() => { setEditingProduct(selectedProduct); setSelectedProduct(null); setShowFormModal(true) }}
        />
      )}

      {showFormModal && (
        <ProductFormModal
          product={editingProduct}
          onClose={() => { setShowFormModal(false); setEditingProduct(null) }}
          onSave={editingProduct
            ? (data) => updateProduct(editingProduct.id, data)
            : (data) => createProduct(data)
          }
        />
      )}

      {deletingProduct && (
        <DeleteProductModal
          product={deletingProduct}
          onClose={() => setDeletingProduct(null)}
          onConfirm={() => deleteProduct(deletingProduct.id).then(() => setDeletingProduct(null))}
        />
      )}
    </div>
  )
}
