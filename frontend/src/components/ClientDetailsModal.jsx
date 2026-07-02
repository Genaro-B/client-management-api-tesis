import Modal from './Modal.jsx'
import Avatar from './Avatar.jsx'
import StatusBadge from './StatusBadge.jsx'
import { Pencil } from 'lucide-react'

export default function ClientDetailsModal({ client, isAdmin, onClose, onEdit }) {
  return (
    <Modal title="Detalles del Cliente" onClose={onClose}>
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
