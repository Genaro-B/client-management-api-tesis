import { useState, useEffect } from 'react'
import {
  Users, UserCheck, UserX, MessageSquare, CalendarDays, Clock,
  AlertCircle, RefreshCw,
} from 'lucide-react'
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend,
  LineChart, Line, XAxis, YAxis, BarChart, Bar,
} from 'recharts'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import useAuth from '../hooks/useAuth.js'
import { getDashboard } from '../services/metricService.js'

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

export default function MetricsPage() {
  const { user, isAdmin, logout } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = () => {
    setLoading(true)
    setError(null)
    getDashboard()
      .then((res) => setData(res))
      .catch((err) => setError(err.message || 'Error al cargar métricas'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchData()
  }, [])

  const summaryCards = data
    ? [
        {
          label: 'Total Clientes',
          value: data.summary.totalClients,
          icon: Users,
          bg: 'bg-blue-50 dark:bg-blue-950/50',
          ring: 'ring-blue-100 dark:ring-blue-900',
          color: 'text-blue-600 dark:text-blue-400',
        },
        {
          label: 'Activos',
          value: data.summary.activeClients,
          icon: UserCheck,
          bg: 'bg-emerald-50 dark:bg-emerald-950/50',
          ring: 'ring-emerald-100 dark:ring-emerald-900',
          color: 'text-emerald-600 dark:text-emerald-400',
        },
        {
          label: 'Inactivos',
          value: data.summary.inactiveClients,
          icon: UserX,
          bg: 'bg-slate-50 dark:bg-slate-800',
          ring: 'ring-slate-200 dark:ring-slate-700',
          color: 'text-slate-500 dark:text-slate-400',
        },
        {
          label: 'Total Interacciones',
          value: data.summary.totalInteractions,
          icon: MessageSquare,
          bg: 'bg-violet-50 dark:bg-violet-950/50',
          ring: 'ring-violet-100 dark:ring-violet-900',
          color: 'text-violet-600 dark:text-violet-400',
        },
        {
          label: 'Hoy',
          value: data.summary.interactionsToday,
          icon: CalendarDays,
          bg: 'bg-amber-50 dark:bg-amber-950/50',
          ring: 'ring-amber-100 dark:ring-amber-900',
          color: 'text-amber-600 dark:text-amber-400',
        },
        {
          label: 'Esta Semana',
          value: data.summary.interactionsThisWeek,
          icon: Clock,
          bg: 'bg-rose-50 dark:bg-rose-950/50',
          ring: 'ring-rose-100 dark:ring-rose-900',
          color: 'text-rose-600 dark:text-rose-400',
        },
      ]
    : []

  const hasInteractions = data?.interactionsTimeline?.some((d) => d.count > 0)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Métricas"
          subtitle="Dashboard con métricas agregadas del sistema"
        />

        <div className="flex-1 overflow-y-auto p-8">
          <div className="mb-8">
            <h1 className="text-[22px] font-semibold text-foreground font-display">
              Métricas
            </h1>
            <p className="text-[13px] text-muted-foreground mt-1">
              Dashboard con métricas agregadas del sistema
            </p>
          </div>

          {/* Loading state */}
          {loading && (
            <div className="flex items-center justify-center py-28">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground">{error}</p>
              <button
                onClick={fetchData}
                className="mt-2 inline-flex items-center gap-2 px-4 py-2 text-[13px] font-medium rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                <RefreshCw size={14} />
                Reintentar
              </button>
            </div>
          )}

          {/* Dashboard content */}
          {data && !loading && (
            <div className="space-y-8">
              {/* ── Summary cards: 3×2 grid ── */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
                {summaryCards.map((card) => (
                  <div key={card.label} className="bg-card border border-border rounded-xl p-6 shadow-sm">
                    <div className="flex items-center gap-3 mb-4">
                      <div
                        className={`w-10 h-10 rounded-xl ${card.bg} ring-1 ${card.ring} flex items-center justify-center`}
                      >
                        <card.icon size={18} className={card.color} />
                      </div>
                      <div>
                        <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wider">
                          {card.label}
                        </p>
                      </div>
                    </div>
                    <p className="text-[32px] font-bold text-foreground font-display tracking-tight">
                      {card.value}
                    </p>
                  </div>
                ))}
              </div>

              {/* ── Charts row: PieChart + LineChart ── */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* PieChart: Interactions by source */}
                <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                  <h3 className="text-[14px] font-semibold text-foreground mb-4">
                    Interacciones por Fuente
                  </h3>
                  {data.interactionsBySource &&
                  Object.keys(data.interactionsBySource).length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={Object.entries(data.interactionsBySource).map(
                            ([name, value]) => ({ name, value }),
                          )}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          dataKey="value"
                          label={({ name, percent }) =>
                            `${name} ${(percent * 100).toFixed(0)}%`
                          }
                        >
                          {Object.entries(data.interactionsBySource).map(
                            (_, idx) => (
                              <Cell
                                key={`src-${idx}`}
                                fill={CHART_COLORS[idx % CHART_COLORS.length]}
                              />
                            ),
                          )}
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-[13px] text-muted-foreground">
                      Sin datos de interacciones
                    </div>
                  )}
                </div>

                {/* LineChart: Interactions timeline (30 days) */}
                <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                  <h3 className="text-[14px] font-semibold text-foreground mb-4">
                    Interacciones (Últimos 30 días)
                  </h3>
                  {hasInteractions ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={data.interactionsTimeline}>
                        <XAxis
                          dataKey="date"
                          tick={{ fontSize: 10 }}
                          tickFormatter={(v) => v.slice(5)}
                          interval="preserveStartEnd"
                        />
                        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="count"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 4 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-[300px] text-[13px] text-muted-foreground">
                      Sin interacciones en los últimos 30 días
                    </div>
                  )}
                </div>
              </div>

              {/* ── BarChart: Top intents (horizontal) ── */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <h3 className="text-[14px] font-semibold text-foreground mb-4">
                  Top Intents
                </h3>
                {data.topIntents && data.topIntents.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart
                      data={data.topIntents}
                      layout="vertical"
                      margin={{ left: 20 }}
                    >
                      <XAxis
                        type="number"
                        allowDecimals={false}
                        tick={{ fontSize: 11 }}
                      />
                      <YAxis
                        type="category"
                        dataKey="intent"
                        tick={{ fontSize: 12 }}
                        width={100}
                      />
                      <Tooltip />
                      <Bar
                        dataKey="count"
                        fill="#3b82f6"
                        radius={[0, 4, 4, 0]}
                        barSize={24}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[250px] text-[13px] text-muted-foreground">
                    Sin intents registrados
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
