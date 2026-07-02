export default function StatusBadge({ activo }) {
  const isActive = activo === true || activo === 1

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold tracking-wider ${
        isActive
          ? 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200 dark:bg-emerald-900 dark:text-emerald-200 dark:ring-emerald-700'
          : 'bg-slate-100 text-slate-500 ring-1 ring-inset ring-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:ring-slate-600'
      }`}
    >
      <span
        className={`w-[6px] h-[6px] rounded-full ${
          isActive ? 'bg-emerald-500' : 'bg-slate-400 dark:bg-slate-500'
        }`}
      />
      {isActive ? 'Activo' : 'Inactivo'}
    </span>
  )
}
