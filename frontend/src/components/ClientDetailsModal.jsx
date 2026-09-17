import { useState, useEffect, useCallback } from 'react'
import Modal from './Modal.jsx'
import Avatar from './Avatar.jsx'
import StatusBadge from './StatusBadge.jsx'
import AssignProductModal from './AssignProductModal.jsx'
import { Pencil, Plus, Trash2, Minus, Plus as PlusIcon, RefreshCw, History } from 'lucide-react'
import { getInteractions } from '../services/interactionService.js'

function formatTimestamp(ts) {
  if (!ts) return '—'
  try {
    return new Date(ts).toLocaleString('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ts
  }
}

function payloadResumen(payload) {
  if (!payload) return '—'
  try {
    const obj = JSON.parse(payload)
    if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
      const first = Object.values(obj)[0]
      if (typeof first === 'string') return first
    }
    return JSON.stringify(obj)
  } catch {
    return payload
  }
}

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

  // --- Historial de interacciones (timeline del cliente) ---
  const [interactions, setInteractions] = useState([])
  const [loadingInteractions, setLoadingInteractions] = useState(true)
  const [errorInteractions, setErrorInteractions] = useState(false)

  const loadInteractions = useCallback(async () => {
    setLoadingInteractions(true)
    setErrorInteractions(false)
    try {
      const res = await getInteractions({ client_id: client.id, limit: 50 })
      setInteractions(res.items || [])
    } catch {
      setErrorInteractions(true)
    } finally {
      setLoadingInteractions(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client.id])

  useEffect(() => {
    loadInteractions()
  }, [loadInteractions])

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

      {/* Historial de interacciones */}
      <div className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-[13px] font-semibold text-foreground flex items-center gap-1.5">
            <History size={14} className="text-muted-foreground" />
            Historial de interacciones
          </h4>
          <button
            onClick={loadInteractions}
            disabled={loadingInteractions}
            className="p-1 rounded-md text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150 disabled:opacity-40"
            title="Actualizar historial"
          >
            <RefreshCw size={13} className={loadingInteractions ? 'animate-spin' : ''} />
          </button>
        </div>

        {loadingInteractions ? (
          <div className="flex items-center justify-center gap-2 py-6">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-[12px] text-muted-foreground">Cargando interacciones…</p>
          </div>
        ) : errorInteractions ? (
          <div className="flex flex-col items-center gap-2 py-6 rounded-lg border border-dashed border-red-200 dark:border-red-900">
            <p className="text-[12px] text-muted-foreground">
              No se pudo cargar el historial de interacciones.
            </p>
            <button
              onClick={loadInteractions}
              className="text-[12px] font-semibold text-primary hover:text-blue-700"
            >
              Reintentar
            </button>
          </div>
        ) : interactions.length === 0 ? (
          <p className="text-[12px] text-muted-foreground py-4 text-center italic">
            Sin interacciones registradas
          </p>
        ) : (
          <div className="max-h-[40vh] overflow-y-auto rounded-lg border border-slate-100 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800">
            {interactions.map((interaccion) => (
              <div key={interaccion.id} className="py-2.5 px-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
                    {interaccion.source}
                  </span>
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {formatTimestamp(interaccion.timestamp)}
                  </span>
                </div>
                <p className="text-[12px] text-foreground mt-1">
                  {payloadResumen(interaccion.payload)}
                </p>
                {interaccion.intent && (
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    Intención: <span className="font-mono">{interaccion.intent}</span>
                  </p>
                )}
              </div>
            ))}
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
