import { useState, useEffect, useCallback } from 'react'
import { AlertCircle, Inbox, XCircle, AlertTriangle, CheckCircle, Gauge } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import MetricCard from '../components/MetricCard.jsx'
import useAuth from '../hooks/useAuth.js'
import { getProducts } from '../services/productService.js'
import { computeStockBands } from '../utils/stock.js'

// Paridad con dashboard/pages_stock.py: bandas disjuntas con semáforo de
// color, conteos por grupo y solo productos activos (el endpoint ya
// devuelve activos; computeStockBands lo garantiza además).
function StockBand({ titulo, dotClass, textClass, productos, vacioMsg }) {
  return (
    <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
      <div className="flex items-center gap-2.5 px-5 py-3.5 border-b border-border bg-slate-50/80 dark:bg-slate-900/50">
        <span className={`w-2.5 h-2.5 rounded-full ${dotClass}`} aria-hidden="true" />
        <h2 className="text-[11px] font-bold uppercase tracking-widest text-foreground">
          {titulo} · {productos.length}
        </h2>
      </div>
      {productos.length === 0 ? (
        <p className="px-5 py-4 text-[13px] text-muted-foreground">{vacioMsg}</p>
      ) : (
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100 dark:border-slate-700">
              <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Nombre</th>
              <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Stock</th>
              <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Categoría</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {productos.map((p) => (
              <tr key={p.id}>
                <td className="py-3 px-5 text-[13px] font-semibold text-slate-800 dark:text-slate-100">
                  {p.nombre}
                </td>
                <td className={`py-3 px-5 text-[13px] font-mono font-semibold ${textClass}`}>
                  {p.stock}
                </td>
                <td className="py-3 px-5 text-[13px] text-slate-600 dark:text-slate-300">
                  {p.categoria || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default function StockPage() {
  const { user, isAdmin, logout } = useAuth()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchStock = useCallback(() => {
    setLoading(true)
    setError(null)
    getProducts({ limit: 10000 })
      .then((res) => setSummary(computeStockBands(res.items || [])))
      .catch((err) => setError(err.message || 'Error al cargar el stock'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    fetchStock()
  }, [fetchStock])

  const total = summary
    ? summary.counts.out_of_stock + summary.counts.low_stock + summary.counts.normal
    : 0

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Stock"
          subtitle="Panel de stock por banda de disponibilidad"
        />

        <div className="flex-1 overflow-y-auto p-8">
          <div className="mb-8">
            <h1 className="text-[22px] font-semibold text-foreground font-display">
              Panel de Stock
            </h1>
            <p className="text-[13px] text-muted-foreground mt-1">
              Productos activos agrupados por semáforo de disponibilidad
            </p>
          </div>

          {loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-[13px] text-muted-foreground">Cargando stock…</p>
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground max-w-[20rem] text-center">
                No se pudo cargar el stock. Verificá la conexión e intentá de nuevo.
              </p>
              <button
                onClick={fetchStock}
                className="text-[13px] font-semibold text-primary hover:text-blue-700 flex items-center gap-1"
              >
                Reintentar conexión
              </button>
            </div>
          )}

          {!loading && !error && total === 0 && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                <Inbox size={20} className="text-slate-400 dark:text-slate-500" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Sin datos aún</p>
              <p className="text-[12px] text-muted-foreground">
                No hay productos activos en el catálogo.
              </p>
            </div>
          )}

          {!loading && !error && total > 0 && summary && (
            <div className="space-y-6">
              {/* ── Conteos por grupo (tarjetas unificadas) ── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <MetricCard
                  label="Agotados"
                  value={summary.counts.out_of_stock}
                  icon={XCircle}
                  tone={{ bg: 'bg-red-50 dark:bg-red-950/50', ring: 'ring-red-100 dark:ring-red-900', color: 'text-red-600 dark:text-red-400' }}
                />
                <MetricCard
                  label="Críticos"
                  value={summary.counts.low_stock}
                  icon={AlertTriangle}
                  tone={{ bg: 'bg-amber-50 dark:bg-amber-950/50', ring: 'ring-amber-100 dark:ring-amber-900', color: 'text-amber-600 dark:text-amber-400' }}
                />
                <MetricCard
                  label="Normales"
                  value={summary.counts.normal}
                  icon={CheckCircle}
                  tone={{ bg: 'bg-emerald-50 dark:bg-emerald-950/50', ring: 'ring-emerald-100 dark:ring-emerald-900', color: 'text-emerald-600 dark:text-emerald-400' }}
                />
                <MetricCard
                  label="Umbral crítico"
                  value={`≤ ${summary.threshold}`}
                  icon={Gauge}
                  tone={{ bg: 'bg-blue-50 dark:bg-blue-950/50', ring: 'ring-blue-100 dark:ring-blue-900', color: 'text-blue-600 dark:text-blue-400' }}
                />
              </div>

              {/* ── Bandas con semáforo de color ── */}
              <StockBand
                titulo="AGOTADOS (stock = 0)"
                dotClass="bg-red-500"
                textClass="text-red-500 dark:text-red-400"
                productos={summary.out_of_stock}
                vacioMsg="Sin productos agotados."
              />
              <StockBand
                titulo="CRÍTICOS (stock ≤ umbral)"
                dotClass="bg-amber-500"
                textClass="text-amber-500 dark:text-amber-400"
                productos={summary.low_stock}
                vacioMsg="Sin productos con stock crítico."
              />
              <StockBand
                titulo="NORMALES (stock > umbral)"
                dotClass="bg-emerald-500"
                textClass="text-slate-600 dark:text-slate-300"
                productos={summary.normal}
                vacioMsg="Sin datos aún: no hay productos en esta banda."
              />
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
