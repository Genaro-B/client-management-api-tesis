import { Eye, Pencil, Trash2 } from 'lucide-react'
import Avatar from './Avatar.jsx'
import StatusBadge from './StatusBadge.jsx'

const columns = [
  { key: 'id', label: 'ID', mono: true },
  { key: 'nombre', label: 'Nombre' },
  { key: 'email', label: 'Email' },
  { key: 'telefono', label: 'Teléfono', mono: true },
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

function Cell({ column, client }) {
  if (column.key === 'nombre') {
    return (
      <td className="py-4 px-5">
        <div className="flex items-center gap-3">
          <Avatar nombre={client.nombre} apellido={client.apellido} />
          <div>
            <span className="text-[13px] font-semibold text-slate-800 dark:text-slate-100">
              {client.nombre} {client.apellido}
            </span>
          </div>
        </div>
      </td>
    )
  }

  if (column.key === 'email') {
    return (
      <td className="py-4 px-5 text-[13px] text-slate-600 dark:text-slate-300">
        {client.email || '—'}
      </td>
    )
  }

  if (column.key === 'telefono') {
    return (
      <td className="py-4 px-5 text-[13px] text-slate-600 dark:text-slate-300 font-mono">
        {client.telefono || '—'}
      </td>
    )
  }

  if (column.key === 'estado') {
    return (
      <td className="py-4 px-5">
        <StatusBadge activo={client.activo} />
      </td>
    )
  }

  if (column.key === 'fecha_registro') {
    return (
      <td className="py-4 px-5 text-[12px] text-slate-500 dark:text-slate-400 font-mono">
        {formatDate(client.fecha_registro)}
      </td>
    )
  }

  if (column.key === 'id') {
    return (
      <td className="py-4 px-5 text-[11px] text-muted-foreground font-mono">
        #{client.id}
      </td>
    )
  }

  return null
}

export default function ClientTable({ clients, isAdmin, onView, onEdit, onDelete }) {
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
          {clients.map((client) => (
            <tr
              key={client.id}
              className="group transition-colors duration-150 hover:bg-blue-50/30 dark:hover:bg-blue-950/20"
            >
              {visibleColumns.map((col) => {
                if (col.key === 'acciones') {
                  return (
                    <td key={col.key} className="py-4 px-5">
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                        <button
                          onClick={() => onView(client)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-blue-50 dark:hover:bg-blue-950/30 hover:text-blue-600 transition-colors duration-150"
                          title="Ver"
                        >
                          <Eye size={15} />
                        </button>
                        <button
                          onClick={() => onEdit(client)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-amber-50 dark:hover:bg-amber-950/30 hover:text-amber-600 transition-colors duration-150"
                          title="Editar"
                        >
                          <Pencil size={15} />
                        </button>
                        <button
                          onClick={() => onDelete(client)}
                          className="p-1.5 rounded-md text-slate-400 hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600 transition-colors duration-150"
                          title="Eliminar"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  )
                }
                return <Cell key={col.key} column={col} client={client} />
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex items-center justify-between py-3 px-5 border-t border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30">
        <span className="text-[11px] text-muted-foreground">
          {clients.length} {clients.length === 1 ? 'cliente encontrado' : 'clientes encontrados'}
        </span>
      </div>
    </div>
  )
}
