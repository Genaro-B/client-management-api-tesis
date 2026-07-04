import { Plus, LogOut, FileDown } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import ThemeToggle from './ThemeToggle.jsx'
import Avatar from './Avatar.jsx'
import { exportClientsToExcel } from '../services/clientService.js'

export default function Topbar({ user, isAdmin, onNewClient, onNewProduct, onLogout, title = 'Clientes', subtitle = 'Gestión de clientes del CRM', onExport, exportLabel }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    onLogout()
    navigate('/')
  }

  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-8 flex-shrink-0">
      <div className="flex items-center gap-6">
        <div>
          <h1 className="text-[17px] font-semibold text-foreground font-display">
            {title}
          </h1>
          <p className="text-[12px] text-muted-foreground mt-0.5">
            {subtitle}
          </p>
        </div>

        {user && (
          <div className="hidden sm:flex items-center gap-3 pl-6 border-l border-border">
            <div className="text-right">
              <p className="text-[11px] text-muted-foreground">
                Usuario: <span className="text-foreground font-medium">{user.nombre} {user.apellido}</span>
              </p>
              <span className={`inline-block text-[10px] font-bold uppercase tracking-wider mt-0.5 ${
                isAdmin ? 'text-blue-600' : 'text-slate-500'
              }`}>
                {isAdmin ? 'Administrador' : 'Usuario estándar'}
              </span>
            </div>
            <button onClick={() => navigate('/profile')} className="hover:opacity-80 transition-opacity">
              <Avatar nombre={user.nombre} apellido={user.apellido} src={user.avatar} size="sm" />
            </button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-3">
          {isAdmin && (onNewClient || onNewProduct) && (
            <button
              onClick={onNewClient || onNewProduct}
              className="flex items-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground text-[13px] font-semibold rounded-lg shadow-sm shadow-blue-500/20 hover:bg-blue-700 active:bg-blue-800 transition-colors duration-150"
            >
              <Plus size={15} strokeWidth={2.5} />
              {onNewProduct ? 'Nuevo Producto' : 'Nuevo Cliente'}
            </button>
          )}

        <button
          onClick={onExport || exportClientsToExcel}
          className="flex items-center gap-2 px-4 py-2.5 bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-150"
          title="Descargar Excel"
        >
          <FileDown size={15} strokeWidth={2} />
          {exportLabel || 'Exportar Excel'}
        </button>

        <ThemeToggle />

        <button
          onClick={handleLogout}
          className="p-2.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150"
          title="Cerrar sesión"
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  )
}
