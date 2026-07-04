import { useState } from 'react'
import Modal from './Modal.jsx'
import Avatar from './Avatar.jsx'
import StatusBadge from './StatusBadge.jsx'
import AssignProductModal from './AssignProductModal.jsx'
import { Pencil, Plus, Trash2, Minus, Plus as PlusIcon } from 'lucide-react'

export default function ClientDetailsModal({
  client,
  isAdmin,
  onClose,
  onEdit,
  onAssignProduct,
  onRemoveProduct,
  onUpdateQuantity,
}) {
  const [showAssignModal, setShowAssignModal] = useState(false)

  const productos = client.productos_asignados || []
  const total = productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0)

  return (
    <Modal title="Detalles del Cliente" onClose={onClose} size="lg">
      <div className="flex flex-col items-center gap-5 mb-5">
        <Avatar nombre={client.nombre} apellido={client.apellido} size="lg" />
        <div className="text-center">
          <h3 className="text-[17px] font-semibold text-foreground font-display">
            {client.nombre} {client.apellido}
          </h3>
          <p className="text-[12px] text-muted-foreground mt-0.5">{client.email}</p>
          <div className="mt-2">
            <StatusBadge activo={client.activo} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-4">
        <Field label="Email" value={client.email} mono={false} />
        <Field label="Teléfono" value={client.telefono || '—'} mono />
        <Field label="Fecha registro" value={client.fecha_registro ? new Date(client.fecha_registro).toLocaleDateString('es-AR') : '—'} mono />
      </div>

      {/* Productos Asignados */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-[13px] font-semibold text-foreground">
            Productos Asignados
          </h4>
          {isAdmin && (
            <button
              onClick={() => setShowAssignModal(true)}
              className="py-1.5 px-3 rounded-lg bg-primary text-primary-foreground text-[11px] font-semibold hover:bg-blue-700 transition-colors duration-150 flex items-center gap-1.5"
            >
              <Plus size={13} />
              Agregar Producto
            </button>
          )}
        </div>

        {productos.length === 0 ? (
          <p className="text-[12px] text-muted-foreground py-4 text-center italic">
            Sin productos asignados
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <Th>Producto</Th>
                  <Th className="text-right">Precio Unit.</Th>
                  <Th className="text-center">Cantidad</Th>
                  <Th className="text-right">Subtotal</Th>
                  {isAdmin && <Th className="text-right">Acciones</Th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {productos.map((p) => (
                  <tr key={p.producto_id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                    <Td>{p.nombre}</Td>
                    <Td className="text-right font-mono">
                      ${p.precio.toLocaleString('es-AR')}
                    </Td>
                    <Td className="text-center">
                      {isAdmin ? (
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => onUpdateQuantity(client.id, p.producto_id, Math.max(1, p.cantidad - 1))}
                            disabled={p.cantidad <= 1}
                            className="p-0.5 rounded border border-slate-200 dark:border-slate-600 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-30 transition-colors duration-150"
                          >
                            <Minus size={11} />
                          </button>
                          <span className="font-mono font-semibold min-w-[20px] text-center">
                            {p.cantidad}
                          </span>
                          <button
                            type="button"
                            onClick={() => onUpdateQuantity(client.id, p.producto_id, p.cantidad + 1)}
                            className="p-0.5 rounded border border-slate-200 dark:border-slate-600 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors duration-150"
                          >
                            <PlusIcon size={11} />
                          </button>
                        </div>
                      ) : (
                        <span className="font-mono">{p.cantidad}</span>
                      )}
                    </Td>
                    <Td className="text-right font-mono font-semibold">
                      ${(p.precio * p.cantidad).toLocaleString('es-AR')}
                    </Td>
                    {isAdmin && (
                      <Td className="text-right">
                        <button
                          type="button"
                          onClick={() => {
                            if (window.confirm(`¿Quitar "${p.nombre}" de la lista?`)) {
                              onRemoveProduct(client.id, p.producto_id)
                            }
                          }}
                          className="p-1 rounded text-slate-400 hover:text-destructive hover:bg-destructive/10 transition-colors duration-150"
                          title="Quitar producto"
                        >
                          <Trash2 size={13} />
                        </button>
                      </Td>
                    )}
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-slate-300 dark:border-slate-600">
                  <Td className="font-semibold" colSpan={isAdmin ? 3 : 3}>
                    Total
                  </Td>
                  <Td className="text-right font-mono font-bold text-[14px]">
                    ${total.toLocaleString('es-AR')}
                  </Td>
                  {isAdmin && <Td />}
                </tr>
              </tfoot>
            </table>
          </div>
        )}
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
            Editar Cliente
          </button>
        )}
      </div>

      {showAssignModal && (
        <AssignProductModal
          onClose={() => setShowAssignModal(false)}
          onAssign={(data) => onAssignProduct(client.id, data)}
        />
      )}
    </Modal>
  )
}

function Field({ label, value, mono }) {
  return (
    <div>
      <span className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1">
        {label}
      </span>
      <span className={`text-[13px] text-foreground ${mono ? 'font-mono' : ''}`}>
        {value}
      </span>
    </div>
  )
}

function Th({ children, className = '' }) {
  return (
    <th className={`text-[10px] font-bold uppercase tracking-widest text-muted-foreground pb-2 ${className}`}>
      {children}
    </th>
  )
}

function Td({ children, className = '', colSpan }) {
  return (
    <td colSpan={colSpan} className={`py-2.5 text-foreground ${className}`}>
      {children}
    </td>
  )
}
