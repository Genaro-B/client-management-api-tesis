import { Eye, Pencil, Trash2 } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

const columns = [
  { key: 'id', label: 'ID', mono: true },
  { key: 'nombre', label: 'Nombre' },
  { key: 'precio', label: 'Precio' },
  { key: 'stock', label: 'Stock' },
  { key: 'categoria', label: 'Categoría' },
  { key: 'estado', label: 'Estado' },
  { key: 'fecha_registro', label: 'Fecha registro', mono: true },
  { key: 'acciones', label: 'Acciones' },
]

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return dateStr
  }
}

function formatPrice(price) {
  if (price == null) return '—'
  return '$' + Number(price).toLocaleString('es-AR', { minimumFractionDigits: 2 })
}

function Cell({ column, product }) {
  if (column.key === 'nombre') {
    return (
      <td className="py-4 px-5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-50 dark:bg-blue-950/40 ring-1 ring-blue-100 dark:ring-blue-900 flex items-center justify-center flex-shrink-0">
            <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400">
              {product.nombre?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
          <div>
            <span className="text-[13px] font-semibold text-slate-800 dark:text-slate-100">
              {product.nombre}
            </span>
          </div>
        </div>
      </td>
    )
  }

  if (column.key === 'precio') {
    return (
      <td className="py-4 px-5 text-[13px] text-slate-600 dark:text-slate-300 font-mono font-semibold">
        {formatPrice(product.precio)}
      </td>
    )
  }

  if (column.key === 'stock') {
    const stock = product.stock ?? '—'
    const stockClass = stock === 0
      ? 'text-red-500 dark:text-red-400'
      : stock < 5
        ? 'text-amber-500 dark:text-amber-400'
        : 'text-slate-600 dark:text-slate-300'
    return (
      <td className={`py-4 px-5 text-[13px] font-mono font-semibold ${stockClass}`}>
        {stock}
      </td>
    )
  }

  if (column.key === 'categoria') {
    return (
      <td className="py-4 px-5 text-[13px] text-slate-600 dark:text-slate-300">
        {product.categoria || '—'}
      </td>
    )
  }

  if (column.key === 'estado') {
    return (
      <td className="py-4 px-5">
        <StatusBadge activo={product.activo} />
      </td>
    )
  }

  if (column.key === 'fecha_registro') {
    return (
      <td className="py-4 px-5 text-[12px] text-slate-500 dark:text-slate-400 font-mono">
        {formatDate(product.fecha_registro)}
      </td>
    )
  }

  if (column.key === 'id') {
    return (
      <td className="py-4 px-5 text-[11px] text-muted-foreground font-mono">
        #{product.id}
      </td>
    )
  }

  return null
}

export default function ProductTable({ products, isAdmin, onView, onEdit, onDelete }) {
  const visibleColumns = isAdmin ? columns : columns.filter((c) => c.key !== 'acciones')

  return (
    <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-slate-50/80 dark:bg-slate-900/50 border-b border-slate-100 dark:border-slate-700">
            {visibleColumns.map((col) => (
              <th
                key={col.key}
                className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3.5 px-5 text-left whitespace-nowrap"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[#f8fafc] dark:divide-slate-800">
          {products.map((product) => (
            <tr
              key={product.id}
              className="group transition-colors duration-150 hover:bg-blue-50/30 dark:hover:bg-blue-950/20"
            >
              {visibleColumns.map((col) => {
                if (col.key === 'acciones') {
                  return (
                    <td key={col.key} className="py-4 px-5">
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                        <button
                          onClick={() => onView(product)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-blue-50 dark:hover:bg-blue-950/30 hover:text-blue-600 transition-colors duration-150"
                          title="Ver"
                        >
                          <Eye size={15} />
                        </button>
                        <button
                          onClick={() => onEdit(product)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-amber-50 dark:hover:bg-amber-950/30 hover:text-amber-600 transition-colors duration-150"
                          title="Editar"
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => onDelete(product)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 transition-colors duration-150"
                          title="Eliminar"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  )
                }
                return <Cell key={col.key} column={col} product={product} />
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center justify-between py-3 px-5 border-t border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30">
        <span className="text-[11px] text-muted-foreground">
          {products.length} {products.length === 1 ? 'producto encontrado' : 'productos encontrados'}
        </span>
      </div>
    </div>
  )
}
