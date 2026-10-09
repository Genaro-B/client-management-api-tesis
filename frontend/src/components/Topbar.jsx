import { useEffect } from 'react'
import { Plus, LogOut, FileDown } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import ThemeToggle from './ThemeToggle.jsx'
import Avatar from './Avatar.jsx'
import BrandMark from './BrandMark.jsx'
import useAuth from '../hooks/useAuth.js'
import { exportClientsToExcel } from '../services/clientService.js'
import { getPageTitle } from '../config/navigation.js'
import { BRAND } from '../config/brand.js'

// Topbar persistente del área protegida. El título de página se resuelve,
// en prioridad: prop `title` → config de navegación (por ruta) → fallback.
// El mismo getPageTitle alimenta el document.title.
export default function Topbar({
  user,
  isAdmin,
  onNewClient,
  onNewProduct,
  onLogout,
  title,
  subtitle = 'Gestión de clientes del CRM',
  onExport,
  exportLabel,
}) {
  const navigate = useNavigate()
  const location = useLocation()
  const auth = useAuth()

  const currentUser = user ?? auth.user
  const admin = isAdmin ?? auth.isAdmin
  const resolvedTitle = title || getPageTitle(location.pathname) || 'Clientes'
  const handleLogout = onLogout ?? auth.logout

  useEffect(() => {
    const page = getPageTitle(location.pathname)
    document.title = page ? `${page} · ${BRAND.name}` : BRAND.name
  }, [location.pathname])

  return (
    <header className="sticky top-0 z-20 h-16 bg-card border-b border-border flex items-center justify-between px-8 flex-shrink-0">
      <div className="flex items-center gap-6">
        <BrandMark size="sm" className="lg:hidden" />
        <div>
          <h1 className="text-[17px] font-semibold text-foreground font-display">
            {resolvedTitle}
          </h1>
          <p className="text-[12px] text-muted-foreground mt-0.5">
            {subtitle}
          </p>
        </div>

        {currentUser && (
          <div className="hidden sm:flex items-center gap-3 pl-6 border-l border-border">
            <div className="text-right">
              <p className="text-[11px] text-muted-foreground">
                Usuario: <span className="text-foreground font-medium">{currentUser.nombre} {currentUser.apellido}</span>
              </p>
              <span className={`inline-block text-[10px] font-bold uppercase tracking-wider mt-0.5 ${
                admin ? 'text-blue-600' : 'text-slate-500'
              }`}>
                {admin ? 'Administrador' : 'Usuario estándar'}
              </span>
            </div>
            <button
              onClick={() => navigate('/profile')}
              className="rounded-full transition-opacity hover:opacity-80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Avatar nombre={currentUser.nombre} apellido={currentUser.apellido} src={currentUser.avatar} size="sm" />
            </button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
          {admin && (onNewClient || onNewProduct) && (
            <button
              onClick={onNewClient || onNewProduct}
              className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground text-[13px] font-semibold rounded-lg shadow-sm shadow-blue-500/20 hover:bg-blue-700 active:bg-blue-800 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
            >
              <Plus size={15} strokeWidth={2.5} />
              {onNewProduct ? 'Nuevo Producto' : 'Nuevo Cliente'}
            </button>
          )}

        <button
          onClick={onExport || exportClientsToExcel}
          className="flex items-center gap-2 px-4 py-2.5 bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
          title="Descargar Excel"
        >
          <FileDown size={15} strokeWidth={2} />
          {exportLabel || 'Exportar Excel'}
        </button>

        <ThemeToggle />

        <button
          onClick={() => { handleLogout?.(); navigate('/') }}
          className="p-2.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          title="Cerrar sesión"
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  )
}
