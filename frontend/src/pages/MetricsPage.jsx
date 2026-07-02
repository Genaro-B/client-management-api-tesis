import { useState, useEffect } from 'react'
import { Users, UserCheck, UserX, TrendingUp, AlertCircle } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import useAuth from '../hooks/useAuth.js'
import { getClients } from '../services/clientService.js'

export default function MetricsPage() {
  const { user, isAdmin, logout } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    getClients()
      .then((res) => {
        if (cancelled) return
        const clients = res.items || []
        const total = clients.length
        const activos = clients.filter((c) => c.activo === true || c.activo === 1).length
        const inactivos = total - activos
        setStats({ total, activos, inactivos })
      })
      .catch((err) => {
        if (cancelled) return
        setError(err.message || 'Error al cargar métricas')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [])

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Métricas"
          subtitle="Resumen general del estado de los clientes"
        />

        <div className="flex-1 overflow-y-auto p-8">
          <div className="mb-8">
            <h1 className="text-[22px] font-semibold text-foreground font-display">
              Métricas
            </h1>
            <p className="text-[13px] text-muted-foreground mt-1">
              Resumen general del estado de los clientes
            </p>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-28">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground">No se pudieron cargar las métricas.</p>
            </div>
          )}

          {stats && !loading && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              {/* Total */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 dark:bg-blue-950/50 ring-1 ring-blue-100 dark:ring-blue-900 flex items-center justify-center">
                    <Users size={18} className="text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wider">
                      Total clientes
                    </p>
                  </div>
                </div>
                <p className="text-[32px] font-bold text-foreground font-display tracking-tight">
                  {stats.total}
                </p>
              </div>

              {/* Activos */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-950/50 ring-1 ring-emerald-100 dark:ring-emerald-900 flex items-center justify-center">
                    <UserCheck size={18} className="text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wider">
                      Activos
                    </p>
                  </div>
                </div>
                <p className="text-[32px] font-bold text-emerald-600 dark:text-emerald-400 font-display tracking-tight">
                  {stats.activos}
                </p>
              </div>

              {/* Inactivos */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-slate-50 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                    <UserX size={18} className="text-slate-500 dark:text-slate-400" />
                  </div>
                  <div>
                    <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wider">
                      Inactivos
                    </p>
                  </div>
                </div>
                <p className="text-[32px] font-bold text-slate-500 dark:text-slate-400 font-display tracking-tight">
                  {stats.inactivos}
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
