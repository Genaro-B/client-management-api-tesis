// Tarjeta de métrica unificada — paridad con metric_card() de
// dashboard/components.py. La usan Métricas y el panel de Stock.
export default function MetricCard({ label, value, icon: Icon, tone }) {
  return (
    <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-3 mb-4">
        {Icon && (
          <div
            className={`w-10 h-10 rounded-xl ${tone.bg} ring-1 ${tone.ring} flex items-center justify-center`}
          >
            <Icon size={18} className={tone.color} />
          </div>
        )}
        <p className="text-[12px] text-muted-foreground font-medium uppercase tracking-wider">
          {label}
        </p>
      </div>
      <p className="text-[32px] font-bold text-foreground font-display tracking-tight">
        {value}
      </p>
    </div>
  )
}
