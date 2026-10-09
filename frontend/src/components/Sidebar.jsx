import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Menu } from 'lucide-react'
import useAuth from '../hooks/useAuth.js'
import { navItems } from '../config/navigation.js'
import BrandMark from './BrandMark.jsx'

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
        className={`h-16 flex items-center text-sidebar-foreground ${
          collapsed ? 'justify-center' : 'px-5'
        } border-b border-sidebar-border`}
      >
        <BrandMark size="sm" showName={!collapsed} />
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
              className={`w-full flex items-center gap-3 py-2.5 px-3 rounded-lg text-[13px] font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60 ${
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
          className="w-full flex items-center gap-3 py-2 px-3 rounded-lg text-[12px] text-slate-500 hover:text-slate-300 hover:bg-white/6 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/60"
        >
          <Menu size={16} className="flex-shrink-0" />
          {!collapsed && <span>Contraer</span>}
        </button>
      </div>
    </aside>
  )
}
