import { useState, useEffect, useCallback } from 'react'
import {
  AlertCircle, Inbox, ShoppingCart, DollarSign, Receipt, TrendingUp,
  CheckCircle, XCircle, Search,
} from 'lucide-react'
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
} from 'recharts'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import MetricCard from '../components/MetricCard.jsx'
import useAuth from '../hooks/useAuth.js'
import { toast } from 'sonner'
import {
  getVentasMetrics,
  listSales,
  confirmSale,
  completeSale,
  cancelSale,
  searchTicket,
} from '../services/salesService.js'

const fmtMoney = (n) => `$${Number(n || 0).toLocaleString('es-AR')}`

const fmtFecha = (iso) => {
  if (!iso) return '—'
  const d = new Date(iso)
  return isNaN(d.getTime()) ? iso : d.toLocaleDateString('es-AR')
}

// Badge de estado de venta. StatusBadge existente solo maneja activo/inactivo
// (booleano), así que acá se mapea el estado de la venta a color + etiqueta.
const ESTADOS = {
  PENDIENTE: { label: 'Pendiente', classes: 'bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-900 dark:text-amber-200 dark:ring-amber-700', dot: 'bg-amber-500' },
  CONFIRMADO: { label: 'Confirmado', classes: 'bg-blue-50 text-blue-700 ring-blue-200 dark:bg-blue-900 dark:text-blue-200 dark:ring-blue-700', dot: 'bg-blue-500' },
  COMPLETADO: { label: 'Completado', classes: 'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-900 dark:text-emerald-200 dark:ring-emerald-700', dot: 'bg-emerald-500' },
  CANCELADO: { label: 'Cancelado', classes: 'bg-slate-100 text-slate-500 ring-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:ring-slate-600', dot: 'bg-slate-400 dark:bg-slate-500' },
}

function EstadoBadge({ estado }) {
  const cfg = ESTADOS[estado] || { label: estado, classes: 'bg-slate-100 text-slate-500 ring-slate-200', dot: 'bg-slate-400' }
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider ring-1 ring-inset ${cfg.classes}`}>
      <span className={`w-[6px] h-[6px] rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  )
}

export default function VentasPage() {
  const { user, isAdmin, logout } = useAuth()
  const [metrics, setMetrics] = useState(null)
  const [sales, setSales] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [ticketQuery, setTicketQuery] = useState({ cliente: '', fecha: '' })
  const [ticket, setTicket] = useState(null)
  const [ticketLoading, setTicketLoading] = useState(false)

  const fetchAll = useCallback(() => {
    setLoading(true)
    setError(null)
    Promise.all([getVentasMetrics(), listSales({ limit: 50 })])
      .then(([m, s]) => {
        setMetrics(m)
        setSales(s.items || [])
      })
      .catch((err) => setError(err.message || 'Error al cargar las ventas'))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    fetchAll()
  }, [fetchAll])

  const handleTransition = async (id, accion) => {
    const fn = { confirm: confirmSale, complete: completeSale, cancel: cancelSale }[accion]
    try {
      await fn(id)
      const msgs = { confirm: 'Venta confirmada', complete: 'Venta completada', cancel: 'Venta cancelada' }
      toast.success(msgs[accion])
      fetchAll()
    } catch (err) {
      toast.error(err.message || 'No se pudo actualizar la venta')
    }
  }

  const handleSearchTicket = async (e) => {
    e.preventDefault()
    if (!ticketQuery.cliente.trim()) return
    setTicketLoading(true)
    try {
      const res = await searchTicket(ticketQuery)
      setTicket(res)
    } catch (err) {
      toast.error(err.message || 'No se pudo buscar el ticket')
    } finally {
      setTicketLoading(false)
    }
  }

  const summary = metrics?.summary
  const serie = metrics?.serieDiaria || []
  const variacion = summary?.vsPeriodoAnterior?.ventas ?? 0

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Ventas"
          subtitle="Gestión de ventas y tickets"
        />

        <div className="flex-1 overflow-y-auto p-8">
          <div className="mb-8">
            <h1 className="text-[22px] font-semibold text-foreground font-display">
              Panel de Ventas
            </h1>
            <p className="text-[13px] text-muted-foreground mt-1">
              Resumen, tickets y estado de las ventas (solo confirmadas y completadas cuentan)
            </p>
          </div>

          {loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-7 h-7 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <p className="text-[13px] text-muted-foreground">Cargando ventas…</p>
            </div>
          )}

          {error && !loading && (
            <div className="flex flex-col items-center justify-center py-28 gap-3">
              <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/40 ring-1 ring-red-100 dark:ring-red-900 flex items-center justify-center">
                <AlertCircle size={20} className="text-red-500 dark:text-red-400" />
              </div>
              <p className="text-[14px] font-semibold text-foreground">Error de conexión</p>
              <p className="text-[12px] text-muted-foreground max-w-[20rem] text-center">
                No se pudieron cargar las ventas. Verificá la conexión e intentá de nuevo.
              </p>
              <button
                onClick={fetchAll}
                className="text-[13px] font-semibold text-primary hover:text-blue-700 flex items-center gap-1"
              >
                Reintentar conexión
              </button>
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-6">
              {/* ── Cards de resumen ── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <MetricCard
                  label="Ventas"
                  value={summary?.ventas ?? 0}
                  icon={ShoppingCart}
                  tone={{ bg: 'bg-blue-50 dark:bg-blue-950/50', ring: 'ring-blue-100 dark:ring-blue-900', color: 'text-blue-600 dark:text-blue-400' }}
                />
                <MetricCard
                  label="Ingresos"
                  value={fmtMoney(summary?.ingresos)}
                  icon={DollarSign}
                  tone={{ bg: 'bg-emerald-50 dark:bg-emerald-950/50', ring: 'ring-emerald-100 dark:ring-emerald-900', color: 'text-emerald-600 dark:text-emerald-400' }}
                />
                <MetricCard
                  label="Ticket promedio"
                  value={fmtMoney(summary?.ticketPromedio)}
                  icon={Receipt}
                  tone={{ bg: 'bg-amber-50 dark:bg-amber-950/50', ring: 'ring-amber-100 dark:ring-amber-900', color: 'text-amber-600 dark:text-amber-400' }}
                />
                <MetricCard
                  label="Variación"
                  value={`${variacion >= 0 ? '+' : ''}${variacion}%`}
                  icon={TrendingUp}
                  tone={{ bg: 'bg-violet-50 dark:bg-violet-950/50', ring: 'ring-violet-100 dark:ring-violet-900', color: 'text-violet-600 dark:text-violet-400' }}
                />
              </div>

              {/* ── Serie temporal ── */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <h3 className="text-[14px] font-semibold text-foreground mb-4">
                  Ventas por día
                </h3>
                {serie.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={serie}>
                      <XAxis
                        dataKey="fecha"
                        tick={{ fontSize: 10 }}
                        tickFormatter={(v) => v.slice(5)}
                        interval="preserveStartEnd"
                      />
                      <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="ventas"
                        stroke="var(--color-chart-1)"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[280px] text-[13px] text-muted-foreground">
                    Sin ventas en el período
                  </div>
                )}
              </div>

              {/* ── Buscador de tickets ── */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <h3 className="text-[14px] font-semibold text-foreground mb-4">
                  Buscar ticket
                </h3>
                <form onSubmit={handleSearchTicket} className="flex flex-wrap items-end gap-4">
                  <div className="flex flex-col gap-1">
                    <label htmlFor="ticket-cliente" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                      Cliente
                    </label>
                    <input
                      id="ticket-cliente"
                      type="text"
                      value={ticketQuery.cliente}
                      onChange={(e) => setTicketQuery((q) => ({ ...q, cliente: e.target.value }))}
                      className="px-3 py-2 rounded-lg border border-border bg-background text-[13px]"
                      placeholder="Nombre del cliente"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label htmlFor="ticket-fecha" className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                      Fecha
                    </label>
                    <input
                      id="ticket-fecha"
                      type="date"
                      value={ticketQuery.fecha}
                      onChange={(e) => setTicketQuery((q) => ({ ...q, fecha: e.target.value }))}
                      className="px-3 py-2 rounded-lg border border-border bg-background text-[13px]"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={ticketLoading}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white text-[13px] font-semibold hover:opacity-90 disabled:opacity-50"
                  >
                    <Search size={14} />
                    Buscar
                  </button>
                </form>

                {ticket && (
                  <div className="mt-5">
                    {ticket.ventas && ticket.ventas.length > 0 ? (
                      <div className="space-y-3">
                        <p className="text-[13px] font-semibold text-foreground">
                          Ticket de {ticket.cliente}
                        </p>
                        {ticket.ventas.map((v) => (
                          <div key={v.id} className="border border-border rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-[12px] text-muted-foreground">{fmtFecha(v.fecha)}</span>
                              <EstadoBadge estado={v.estado} />
                            </div>
                            <ul className="space-y-1">
                              {v.items.map((it, idx) => (
                                <li key={idx} className="text-[13px] text-foreground flex justify-between">
                                  <span>{it.cantidad} x {it.producto_nombre}</span>
                                  <span className="font-mono">{fmtMoney(it.cantidad * it.precio_unitario)}</span>
                                </li>
                              ))}
                            </ul>
                            <p className="text-right text-[13px] font-bold text-foreground mt-2">
                              Total: {fmtMoney(v.total)}
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[13px] text-muted-foreground">
                        No se encontraron ventas para ese cliente en esa fecha.
                      </p>
                    )}
                  </div>
                )}
              </div>

              {/* ── Tabla de ventas ── */}
              {sales.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 gap-3">
                  <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center">
                    <Inbox size={20} className="text-slate-400 dark:text-slate-500" />
                  </div>
                  <p className="text-[14px] font-semibold text-foreground">No hay ventas</p>
                  <p className="text-[12px] text-muted-foreground">Todavía no se registraron ventas.</p>
                </div>
              ) : (
                <div className="bg-card border border-border rounded-xl shadow-sm overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border bg-slate-50/80 dark:bg-slate-900/50">
                        <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Cliente</th>
                        <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Fecha</th>
                        <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Total</th>
                        <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-left">Estado</th>
                        {isAdmin && (
                          <th className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground py-3 px-5 text-right">Acciones</th>
                        )}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {sales.map((s) => (
                        <tr key={s.id}>
                          <td className="py-3 px-5 text-[13px] font-semibold text-foreground">
                            {s.cliente_nombre || '—'}
                          </td>
                          <td className="py-3 px-5 text-[13px] text-muted-foreground">{fmtFecha(s.fecha)}</td>
                          <td className="py-3 px-5 text-[13px] font-mono font-semibold text-foreground">{fmtMoney(s.total)}</td>
                          <td className="py-3 px-5"><EstadoBadge estado={s.estado} /></td>
                          {isAdmin && (
                            <td className="py-3 px-5">
                              <div className="flex justify-end gap-2">
                                {s.estado === 'PENDIENTE' && (
                                  <button
                                    onClick={() => handleTransition(s.id, 'confirm')}
                                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 text-white text-[12px] font-semibold hover:bg-blue-700"
                                  >
                                    <CheckCircle size={13} /> Confirmar
                                  </button>
                                )}
                                {s.estado === 'CONFIRMADO' && (
                                  <button
                                    onClick={() => handleTransition(s.id, 'complete')}
                                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 text-white text-[12px] font-semibold hover:bg-emerald-700"
                                  >
                                    <CheckCircle size={13} /> Completar
                                  </button>
                                )}
                                {(s.estado === 'PENDIENTE' || s.estado === 'CONFIRMADO') && (
                                  <button
                                    onClick={() => handleTransition(s.id, 'cancel')}
                                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-200 text-slate-700 text-[12px] font-semibold hover:bg-slate-300 dark:bg-slate-700 dark:text-slate-200"
                                  >
                                    <XCircle size={13} /> Cancelar
                                  </button>
                                )}
                              </div>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
