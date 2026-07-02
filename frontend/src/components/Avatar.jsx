const palette = [
  { bg: 'bg-blue-100', text: 'text-blue-700' },
  { bg: 'bg-violet-100', text: 'text-violet-700' },
  { bg: 'bg-emerald-100', text: 'text-emerald-700' },
  { bg: 'bg-amber-100', text: 'text-amber-700' },
  { bg: 'bg-rose-100', text: 'text-rose-700' },
  { bg: 'bg-cyan-100', text: 'text-cyan-700' },
]

export default function Avatar({ nombre, apellido, src, size = 'sm' }) {
  const sizeClass = size === 'lg'
    ? 'w-14 h-14 text-[18px]'
    : size === 'xl'
    ? 'w-20 h-20 text-[24px]'
    : 'w-8 h-8 text-[11px]'

  // If we have a photo, show it
  if (src) {
    return (
      <img
        src={src}
        alt={`${nombre} ${apellido}`}
        className={`${sizeClass} rounded-full object-cover flex-shrink-0 ring-2 ring-white dark:ring-slate-800`}
      />
    )
  }

  // Fallback: initials avatar
  const colorIndex = (nombre?.length + apellido?.length) % 6
  const { bg, text } = palette[colorIndex]
  const initials = `${(nombre || '?')[0]}${(apellido || '?')[0]}`.toUpperCase()

  return (
    <div
      className={`${sizeClass} ${bg} ${text} rounded-full flex items-center justify-center font-bold flex-shrink-0`}
    >
      {initials}
    </div>
  )
}
