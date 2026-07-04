import { useState, useEffect } from 'react'
import { MessageSquare, AlertCircle, RefreshCw, Search } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import useAuth from '../hooks/useAuth.js'
import { getInteractions } from '../services/interactionService.js'

const sourceStyles = {
  telegram: 'bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-950/40 dark:text-sky-300 dark:ring-sky-800',
  webhook: 'bg-purple-50 text-purple-700 ring-purple-200 dark:bg-purple-950/40 dark:text-purple-300 dark:ring-purple-800',
  api: 'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:ring-emerald-800',
  n8n: 'bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:ring-amber-800',
  system: 'bg-slate-50 text-slate-700 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700',
}

function SourceBadge({ source }) {
  const style = sourceStyles[source] || sourceStyles.system
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ring-1 ${style}`}>
      {source}
    </span>
  )
}

export default function InteractionsPage() {
  const { user, isAdmin, logout } = useAuth()
  const [interactions, setInteractions] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  function loadInteractions() {
    setLoading(true)
    setError(null)
    getInteractions({ limit: 200 })
      .then((res) => {
        setInteractions(res.items || [])
        setTotal(res.total || 0)
      })
      .catch((err) => {
        setError(err.message || 'Error al cargar interacciones')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadInteractions()
  }, [])

  const filtered = search
    ? interactions.filter(
        (ix) =>
          ix.source?.toLowerCase().includes(search.toLowerCase()) ||
          ix.user?.toLowerCase().includes(search.toLowerCase()) ||
          ix.payload?.toLowerCase().includes(search.toLowerCase()) ||
          (ix.idempotency_key || '').toLowerCase().includes(search.toLowerCase())
      )
    : interactions

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Interacciones"
          subtitle="Registro de mensajes y eventos recibidos vía Telegram, webhooks y API"
        />

        <div className="flex-1 overflow-y-auto p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-[22px] font-semibold text-foreground font-display">
                Interacciones
              </h1>
              <p className="text-[13px] text-muted-foreground mt-1">
                {total} registros en total
              </p>
            </div>
            <button
              onClick={loadInteractions}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-medium text-primary border border-border hover:bg-accent transition-colors disabled:opacity-50"
            >
              <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
              Actualizar
            </button>
          </div>

          {/* Search */}
          <div className="relative mb-5">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Buscar por source, usuario, payload..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 rounded-lg border border-border bg-card text-[13px] text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
          </div>

          {/* Error */}
          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground">{error}</p>
            </div>
          )}

          {/* Loading */}
          {loading && !error && (
            <div className="flex items-center justify-center py-28">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {/* Empty */}
          {!loading && !error && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-50 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                <MessageSquare size={20} className="text-slate-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">
                {search ? 'Sin resultados' : 'No hay interacciones'}
              </p>
              <p className="text-[12px] text-muted-foreground">
                {search ? 'Probá con otros términos de búsqueda' : 'Los mensajes de Telegram aparecerán aquí cuando lleguen'}
              </p>
            </div>
          )}

          {/* Table */}
          {!loading && !error && filtered.length > 0 && (
            <div className="bg-card border border-border rounded-xl overflow-hidden">
              <table className="w-full text-[13px]">
                <thead>
                  <tr className="border-b border-border bg-muted/50">
                    <th className="text-left py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">ID</th>
                    <th className="text-left py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Source</th>
                    <th className="text-left py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Usuario</th>
                    <th className="text-left py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Payload</th>
                    <th className="text-left py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Fecha</th>
                    <th className="text-right py-3 px-4 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Detalle</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.map((ix) => (
                    <tr key={ix.id} className="hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-4 text-muted-foreground font-mono text-[12px]">
                        #{ix.id}
                      </td>
                      <td className="py-3 px-4">
                        <SourceBadge source={ix.source} />
                      </td>
                      <td className="py-3 px-4 text-foreground font-medium">
                        {(() => {
                          try { const p = JSON.parse(ix.payload); return (p.first_name || '') + (p.last_name ? ' ' + p.last_name : '') || ix.user || '—' }
                          catch { return ix.user || <span className="text-muted-foreground italic">—</span> }
                        })()}
                      </td>
                      <td className="py-3 px-4 max-w-[260px]">
                        <code className="text-[12px] text-muted-foreground font-mono block truncate">
                          {ix.payload || '—'}
                        </code>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground text-[12px] whitespace-nowrap">
                        {ix.timestamp ? new Date(ix.timestamp).toLocaleString('es-AR') : '—'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setExpandedId(expandedId === ix.id ? null : ix.id)}
                          className="text-primary hover:text-primary/80 text-[12px] font-medium transition-colors"
                        >
                          {expandedId === ix.id ? 'Cerrar' : 'Ver más'}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Expanded detail */}
          {expandedId && (() => {
            const ix = interactions.find((i) => i.id === expandedId)
            if (!ix) return null
            return (
              <div className="mt-4 bg-card border border-border rounded-xl p-5 animate-in fade-in slide-in-from-top-2 duration-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-[14px] font-semibold text-foreground">
                    Detalle de interacción #{ix.id}
                  </h3>
                  <button
                    onClick={() => setExpandedId(null)}
                    className="text-[12px] text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Cerrar
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4 text-[13px]">
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">ID</p>
                    <p className="text-foreground font-mono">{ix.id}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Source</p>
                    <SourceBadge source={ix.source} />
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Usuario</p>
                    <p className="text-foreground">{(() => {
                      try { const p = JSON.parse(ix.payload); return (p.first_name || '') + (p.last_name ? ' ' + p.last_name : '') || ix.user || '—' }
                      catch { return ix.user || '—' }
                    })()}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Fecha</p>
                    <p className="text-foreground">{ix.timestamp ? new Date(ix.timestamp).toLocaleString('es-AR') : '—'}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Intent</p>
                    <p className="text-foreground">{ix.intent || '—'}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Result</p>
                    <p className="text-foreground">{ix.result || '—'}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Idempotency Key</p>
                    <p className="text-foreground font-mono text-[12px]">{ix.idempotency_key || '—'}</p>
                  </div>
                  <div>
                    <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-1">Client ID</p>
                    <p className="text-foreground">{ix.clientId || '—'}</p>
                  </div>
                </div>
                <div className="mt-4">
                  <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Payload completo</p>
                  <pre className="bg-muted/50 rounded-lg p-4 text-[12px] font-mono text-foreground overflow-x-auto whitespace-pre-wrap">
                    {(() => {
                      try {
                        const parsed = JSON.parse(ix.payload)
                        return JSON.stringify(parsed, null, 2)
                      } catch {
                        return ix.payload || '—'
                      }
                    })()}
                  </pre>
                </div>
              </div>
            )
          })()}
        </div>
      </main>
    </div>
  )
}
