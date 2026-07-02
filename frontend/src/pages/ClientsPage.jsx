import { useState } from 'react'
import { AlertCircle, Inbox, EyeOff } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import ClientFilters from '../components/ClientFilters.jsx'
import ClientTable from '../components/ClientTable.jsx'
import ClientDetailsModal from '../components/ClientDetailsModal.jsx'
import ClientFormModal from '../components/ClientFormModal.jsx'
import DeleteClientModal from '../components/DeleteClientModal.jsx'
import useClients from '../hooks/useClients.js'
import useAuth from '../hooks/useAuth.js'

export default function ClientsPage() {
  const { user, isAdmin, logout } = useAuth()
  const {
    clients,
    loading,
    error,
    filters,
    setFilters,
    refreshClients,
    createClient,
    updateClient,
    deleteClient,
  } = useClients()

  const [selectedClient, setSelectedClient] = useState(null)
  const [showFormModal, setShowFormModal] = useState(false)
  const [editingClient, setEditingClient] = useState(null)
  const [deletingClient, setDeletingClient] = useState(null)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onNewClient={() => { setEditingClient(null); setShowFormModal(true) }}
          onLogout={logout}
        />
        <div className="flex-1 overflow-y-auto p-8">
          <ClientFilters
            filters={filters}
            onFiltersChange={setFilters}
          />

          {loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-[13px] text-muted-foreground">Cargando clientes…</p>
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground max-w-[20rem] text-center">
                No se pudieron cargar los clientes. Verificá la conexión e intentá de nuevo.
              </p>
              <button
                onClick={refreshClients}
                className="text-[13px] font-semibold text-primary hover:text-blue-700 flex items-center gap-1"
              >
                Reintentar conexión
              </button>
            </div>
          )}

          {!loading && !error && clients.length === 0 && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                <Inbox size={20} className="text-slate-400 dark:text-slate-500" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">No hay clientes</p>
              <p className="text-[12px] text-muted-foreground">
                No se encontraron clientes para mostrar.
              </p>
            </div>
          )}

          {!loading && !error && clients.length > 0 && (
            <ClientTable
              clients={clients}
              isAdmin={isAdmin}
              onView={(c) => setSelectedClient(c)}
              onEdit={(c) => { setEditingClient(c); setShowFormModal(true) }}
              onDelete={(c) => setDeletingClient(c)}
            />
          )}

          {!loading && !error && !isAdmin && (
            <div className="flex items-center justify-center gap-2 mt-4 py-3 px-4 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700">
              <EyeOff size={14} className="text-slate-400 dark:text-slate-500" />
              <p className="text-[12px] text-muted-foreground">
                Modo solo lectura — no tenés permisos para crear, editar o eliminar clientes.
              </p>
            </div>
          )}
        </div>
      </main>

      {selectedClient && (
        <ClientDetailsModal
          client={selectedClient}
          isAdmin={isAdmin}
          onClose={() => setSelectedClient(null)}
          onEdit={() => { setEditingClient(selectedClient); setSelectedClient(null); setShowFormModal(true) }}
        />
      )}

      {showFormModal && (
        <ClientFormModal
          client={editingClient}
          onClose={() => { setShowFormModal(false); setEditingClient(null) }}
          onSave={editingClient
            ? (data) => updateClient(editingClient.id, data)
            : (data) => createClient(data)
          }
        />
      )}

      {deletingClient && (
        <DeleteClientModal
          client={deletingClient}
          onClose={() => setDeletingClient(null)}
          onConfirm={() => deleteClient(deletingClient.id).then(() => setDeletingClient(null))}
        />
      )}
    </div>
  )
}
