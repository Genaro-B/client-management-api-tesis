import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, BarChart3, Settings, UserCircle, RotateCcw, Menu, MessageSquare, Package } from 'lucide-react'
import useAuth from '../hooks/useAuth.js'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Package, label: 'Productos', path: '/products' },
  { icon: BarChart3, label: 'Métricas', path: '/metrics' },
  { icon: MessageSquare, label: 'Interacciones', path: '/interactions' },
  { icon: Users, label: 'Clientes', path: '/dashboard' },
  { icon: RotateCcw, label: 'Inactivos', path: '/inactive' },
  { icon: UserCircle, label: 'Perfil', path: '/profile' },
  { icon: Settings, label: 'Configuración', path: '#' },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const { isAdmin } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <aside
      className={`flex-shrink-0 ${
        collapsed ? 'w-[60px]' : 'w-[220px]'
      } bg-sidebar flex flex-col transition-all duration-300 ease-in-out overflow-hidden`}
    >
      {/* Logo */}
      <div
        className={`h-16 flex items-center ${
          collapsed ? 'justify-center' : 'px-5'
        } border-b border-sidebar-border gap-3`}
      >
        <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
          <span className="text-[11px] font-bold text-primary-foreground">C</span>
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-sidebar-foreground font-display">
            CRM Admin
          </span>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-2 space-y-1">
        {navItems
          .filter((item) => item.label !== 'Inactivos' || isAdmin)
          .map((item) => {
          if (item.path === '#') {
            return (
              <div
                key={item.label}
                className={`flex items-center gap-3 py-2.5 px-3 rounded-lg text-[13px] font-medium text-slate-400 cursor-not-allowed ${collapsed ? 'justify-center px-0' : ''}`}
                title={collapsed ? item.label : undefined}
              >
                <item.icon size={18} strokeWidth={1.5} className="flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </div>
            )
          }

          const isActive = location.pathname === item.path

          return (
            <button
              key={item.label}
              onClick={() => navigate(item.path)}
              title={collapsed ? item.label : undefined}
              className={`w-full flex items-center gap-3 py-2.5 px-3 rounded-lg text-[13px] font-medium transition-colors duration-150 ${
                isActive
                  ? 'bg-primary text-white shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/7'
              } ${collapsed ? 'justify-center px-0' : ''}`}
            >
              <item.icon size={18} strokeWidth={1.5} className="flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </button>
          )
        })}
      </nav>

      {/* Collapse button */}
      <div className="border-t border-sidebar-border p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center gap-3 py-2 px-3 rounded-lg text-[12px] text-slate-500 hover:text-slate-300 hover:bg-white/6 transition-colors duration-150"
        >
          <Menu size={16} className="flex-shrink-0" />
          {!collapsed && <span>Contraer</span>}
        </button>
      </div>
    </aside>
  )
}
