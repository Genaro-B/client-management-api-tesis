import Modal from './Modal.jsx'
import StatusBadge from './StatusBadge.jsx'
import { Pencil, Package } from 'lucide-react'

export default function ProductDetailsModal({ product, isAdmin, onClose, onEdit }) {
  return (
    <Modal title="Detalles del Producto" onClose={onClose}>
      <div className="flex flex-col items-center gap-5 mb-5">
        <div className="w-16 h-16 rounded-xl bg-blue-50 dark:bg-blue-950/40 ring-1 ring-blue-100 dark:ring-blue-900 flex items-center justify-center">
          <Package size={28} className="text-blue-600 dark:text-blue-400" />
        </div>
        <div className="text-center">
          <h3 className="text-[17px] font-semibold text-foreground font-display">
            {product.nombre}
          </h3>
          {product.categoria && (
            <p className="text-[12px] text-muted-foreground mt-0.5">{product.categoria}</p>
          )}
          <div className="mt-2">
            <StatusBadge activo={product.activo} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-4">
        <Field label="Precio" value={'$' + Number(product.precio).toLocaleString('es-AR', { minimumFractionDigits: 2 })} mono />
        <Field label="Stock" value={product.stock?.toString() || '0'} mono />
        <Field label="Descripción" value={product.descripcion || '—'} fullwidth />
        <Field label="Fecha registro" value={product.fecha_registro ? new Date(product.fecha_registro).toLocaleDateString('es-AR') : '—'} mono />
      </div>

      <div className="mt-6 flex gap-2.5">
        <button
          onClick={onClose}
          className="flex-1 py-2.5 rounded-lg bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-150"
        >
          Cerrar
        </button>
        {isAdmin && (
          <button
            onClick={onEdit}
            className="flex-1 py-2.5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 transition-colors duration-150 flex items-center justify-center gap-2"
          >
            <Pencil size={14} />
            Editar Producto
          </button>
        )}
      </div>
    </Modal>
  )
}

function Field({ label, value, mono, fullwidth }) {
  return (
    <div className={fullwidth ? 'col-span-2' : ''}>
      <span className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
        {label}
      </span>
      <span className={`text-[13px] text-foreground ${mono ? 'font-mono' : ''}`}>
        {value}
      </span>
    </div>
  )
}
