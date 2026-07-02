import { Search } from 'lucide-react'

export default function ClientFilters({ filters, onFiltersChange }) {
  const handleChange = (key, value) => {
    onFiltersChange({ ...filters, [key]: value })
  }

  const clearFilters = () => {
    onFiltersChange({ searchTerm: '' })
  }

  const hasFilters = filters.searchTerm

  return (
    <div className="flex items-center gap-3 mb-5">
      {/* Search */}
      <div className="relative flex-1 max-w-sm">
        <Search
          size={14}
          className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none"
        />
        <input
          type="text"
          placeholder="Buscar clientes por nombre…"
          value={filters.searchTerm}
          onChange={(e) => handleChange('searchTerm', e.target.value)}
          className="w-full bg-card border border-border rounded-lg py-2.5 pl-9 pr-4 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)]"
        />
      </div>

      {/* Clear button */}
      {hasFilters && (
        <button
          onClick={clearFilters}
          className="text-[13px] font-semibold text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 transition-colors duration-150 whitespace-nowrap"
        >
          Limpiar
        </button>
      )}
    </div>
  )
}
