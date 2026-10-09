import { BRAND } from '../config/brand.js'

const SIZES = {
  sm: 'w-7 h-7 rounded-lg text-[11px]',
  md: 'w-8 h-8 rounded-xl text-[13px]',
  lg: 'w-12 h-12 rounded-2xl text-[19px]',
}

// Marca reutilizable: cuadro con gradiente + iniciales de BRAND.
// El nombre hereda el color del contenedor para funcionar sobre sidebar
// oscuro y sobre fondo claro por igual.
export default function BrandMark({ size = 'md', showName = false, className = '' }) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className={`${SIZES[size]} bg-gradient-to-br ${BRAND.primaryGradient} flex items-center justify-center flex-shrink-0 shadow-sm`}
      >
        <span className="font-bold text-white font-display">{BRAND.initials}</span>
      </div>
      {showName && (
        <span className="text-sm font-semibold font-display tracking-tight">
          {BRAND.name}
        </span>
      )}
    </div>
  )
}
