import { useState } from 'react'
import Modal from './Modal.jsx'
import { AlertCircle, Loader2 } from 'lucide-react'

export default function DeleteClientModal({ client, onClose, onConfirm }) {
  const [deleting, setDeleting] = useState(false)

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await onConfirm()
    } catch {
      setDeleting(false)
    }
  }

  return (
    <Modal title="Eliminar Cliente" onClose={onClose} size="sm">
      <div className="flex flex-col items-center text-center gap-4">
        <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
          <AlertCircle size={20} className="text-destructive" />
        </div>

        <div>
          <p className="text-[14px] font-semibold text-foreground">
            ¿Eliminar este cliente?
          </p>
          <p className="text-[12px] text-muted-foreground mt-1">
            Esta acción no se puede deshacer. Se eliminarán todos los datos de{' '}
            <strong className="text-foreground">
              {client.nombre} {client.apellido}
            </strong>
            .
          </p>
        </div>

        <div className="flex gap-2.5 w-full pt-2">
          <button
            onClick={onClose}
            disabled={deleting}
            className="flex-1 py-2.5 rounded-lg bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors duration-150"
          >
            Cancelar
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="flex-1 py-2.5 rounded-lg bg-destructive text-white text-[13px] font-semibold hover:bg-red-700 disabled:opacity-60 transition-colors duration-150 flex items-center justify-center gap-2"
          >
            {deleting && <Loader2 size={14} className="animate-spin" />}
            {deleting ? 'Eliminando…' : 'Eliminar'}
          </button>
        </div>
      </div>
    </Modal>
  )
}
