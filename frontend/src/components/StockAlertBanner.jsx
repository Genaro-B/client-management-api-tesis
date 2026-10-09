import { useNavigate } from 'react-router-dom'

// Banner slim de alerta de stock — paridad con render_stock_alert_banner()
// de dashboard/components.py: recibe el resumen de computeStockBands (una
// sola fuente de lógica, sin duplicación) y no renderiza nada si no hay
// alertas. El atajo "Ver stock →" lleva al panel /stock.
export default function StockAlertBanner({ summary }) {
  const navigate = useNavigate()
  const counts = summary?.counts

  if (!counts || counts.alert === 0) return null

  const agotados = counts.out_of_stock
  const critico = agotados > 0
  const texto =
    `⚠ ${counts.alert} ${counts.alert === 1 ? 'producto' : 'productos'} con stock crítico` +
    ` (${agotados} ${agotados === 1 ? 'agotado' : 'agotados'})`

  return (
    <div
      role="status"
      className={`flex items-center justify-between gap-4 mb-6 px-4 py-3 rounded-xl border text-[13px] font-medium ${
        critico
          ? 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-900 text-red-700 dark:text-red-300'
          : 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900 text-amber-700 dark:text-amber-300'
      }`}
    >
      <span>{texto}</span>
      <button
        onClick={() => navigate('/stock')}
        className={`shrink-0 text-[13px] font-semibold underline underline-offset-2 hover:opacity-80 transition-opacity ${
          critico ? 'text-red-700 dark:text-red-300' : 'text-amber-700 dark:text-amber-300'
        }`}
      >
        Ver stock →
      </button>
    </div>
  )
}
