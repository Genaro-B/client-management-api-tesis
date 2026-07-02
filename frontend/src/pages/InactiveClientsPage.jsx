import { useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { AlertCircle, Inbox, RefreshCw, UserX, Search, RotateCcw, Undo2 } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import useAuth from '../hooks/useAuth.js'
import { getInactiveClients, restoreClient } from '../services/clientService.js'

export default function InactiveClientsPage() {
  const { user, isAdmin, logout } = useAuth()

  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [search, setSearch] = useState('')
  const [restoringId, setRestoringId] = useState(null)
  const [confirmRestore, setConfirmRestore] = useState(null)

  const fetchInactive = useCallback(async (q) => {
    setLoading(true)
    setError(false)
    try {
      const data = await getInactiveClients(q ? { q } : {})
      setClients(data.items)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchInactive()
  }, [fetchInactive])

  const handleRestore = async (clientId) => {
    setConfirmRestore(null)
    setRestoringId(clientId)
    try {
      await restoreClient(clientId)
      toast.success('Cliente restaurado correctamente')
      setClients((prev) => prev.filter((c) => c.id !== clientId))
    } catch (err) {
      toast.error(err.message || 'Error al restaurar el cliente')
    } finally {
      setRestoringId(null)
    }
  }

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => fetchInactive(search), 300)
    return () => clearTimeout(t)
  }, [search, fetchInactive])

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar user={user} isAdmin={isAdmin} onLogout={logout} />

        <div className="flex-1 overflow-y-auto p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-[20px] font-semibold text-foreground">Clientes Inactivos</h1>
              <p className="text-[13px] text-muted-foreground mt-1">
                Usuarios que fueron eliminados. Podés restaurarlos para que vuelvan a estar activos.
              </p>
            </div>
            <button
              onClick={() => fetchInactive(search)}
              className="flex items-center gap-2 py-2 px-4 rounded-lg text-[13px] font-medium text-muted-foreground hover:text-foreground hover:bg-white/7 border border-border transition-colors"
            >
              <RefreshCw size={15} />
              Actualizar
            </button>
          </div>

          {/* Search */}
          <div className="relative mb-6">
            <Search
              size={16}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="text"
              placeholder="Buscar por nombre…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-border bg-card text-[13px] text-foreground placeholder:text-slate-400 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-[13px] text-muted-foreground">Cargando clientes inactivos…</p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground max-w-[20rem] text-center">
                No se pudieron cargar los clientes inactivos.
              </p>
              <button
                onClick={() => fetchInactive(search)}
                className="text-[13px] font-semibold text-primary hover:text-blue-700 flex items-center gap-1"
              >
                Reintentar conexión
              </button>
            </div>
          )}

          {/* Empty */}
          {!loading && !error && clients.length === 0 && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                <UserX size={20} className="text-slate-400 dark:text-slate-500" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">No hay clientes inactivos</p>
              <p className="text-[12px] text-muted-foreground text-center max-w-[20rem]">
                {search
                  ? 'No se encontraron clientes inactivos con ese nombre.'
                  : 'No hay clientes eliminados. Cuando elimines un cliente, aparecerá acá.'}
              </p>
            </div>
          )}

          {/* Table */}
          {!loading && !error && clients.length > 0 && (
            <div className="rounded-xl border border-border overflow-hidden bg-card">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-muted/50">
                    <th className="text-left py-3 px-4 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider">Nombre</th>
                    <th className="text-left py-3 px-4 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider">Apellido</th>
                    <th className="text-left py-3 px-4 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider">Email</th>
                    <th className="text-left py-3 px-4 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider">Teléfono</th>
                    <th className="text-right py-3 px-4 text-[12px] font-semibold text-muted-foreground uppercase tracking-wider">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {clients.map((client) => (
                    <tr key={client.id} className="hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-4 text-[13px] font-medium text-foreground">{client.nombre}</td>
                      <td className="py-3 px-4 text-[13px] text-muted-foreground">{client.apellido}</td>
                      <td className="py-3 px-4 text-[13px] text-muted-foreground">{client.email}</td>
                      <td className="py-3 px-4 text-[13px] text-muted-foreground">{client.telefono || '—'}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          disabled={restoringId === client.id}
                          onClick={() => setConfirmRestore(client)}
                          className="inline-flex items-center gap-1.5 py-1.5 px-3 rounded-lg text-[12px] font-semibold text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 transition-colors disabled:opacity-50"
                        >
                          <RotateCcw size={13} />
                          {restoringId === client.id ? 'Restaurando…' : 'Restaurar'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Confirm restore modal */}
      {confirmRestore && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-sm mx-4 rounded-xl border border-border bg-card p-6 shadow-xl">
            <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-950/40 flex items-center justify-center mb-4">
              <Undo2 size={18} className="text-emerald-600 dark:text-emerald-400" />
            </div>
            <h2 className="text-[15px] font-semibold text-foreground mb-1">Restaurar cliente</h2>
            <p className="text-[13px] text-muted-foreground mb-6">
              ¿Estás seguro de que querés restaurar a <strong>{confirmRestore.nombre} {confirmRestore.apellido}</strong>? Va a volver a aparecer en la lista de clientes activos.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setConfirmRestore(null)}
                className="py-2 px-4 rounded-lg text-[13px] font-medium text-muted-foreground hover:text-foreground border border-border transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleRestore(confirmRestore.id)}
                className="py-2 px-4 rounded-lg text-[13px] font-semibold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors"
              >
                Restaurar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
