import { ChevronLeft, ChevronRight } from 'lucide-react'

/**
 * Controles de paginación server-side reutilizables.
 *
 * Muestra el rango visible ("Mostrando X–Y de Z") y los botones ←/→.
 * Los botones se deshabilitan en los extremos (página 1 / última).
 * Los controles numéricos solo aparecen cuando hay más de una página.
 */
export default function Pagination({ page, totalPages, total, pageSize = 20, onPageChange }) {
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  const hasMoreThanOnePage = totalPages > 1

  return (
    <div className="flex items-center justify-between py-3 px-5 border-t border-slate-100 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30">
      <span className="text-[11px] text-muted-foreground">
        Mostrando {start}–{end} de {total}
      </span>

      {hasMoreThanOnePage && (
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 hover:text-slate-700 dark:hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none transition-colors duration-150"
            title="Anterior"
          >
            <ChevronLeft size={15} />
          </button>

          <span className="text-[11px] font-semibold text-muted-foreground whitespace-nowrap">
            Página {page} de {totalPages}
          </span>

          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 hover:text-slate-700 dark:hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none transition-colors duration-150"
            title="Siguiente"
          >
            <ChevronRight size={15} />
          </button>
        </div>
      )}
    </div>
  )
}