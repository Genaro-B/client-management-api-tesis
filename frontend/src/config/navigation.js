import {
  LayoutDashboard, Users, BarChart3, Settings, UserCircle,
  RotateCcw, MessageSquare, Package, Boxes, ShoppingCart,
} from 'lucide-react'

// Fuente única de verdad de la navegación: la consumen el Sidebar (menú),
// el Topbar (título de página) y el document.title (useEffect del Topbar).
export const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Package, label: 'Productos', path: '/products' },
  { icon: Boxes, label: 'Stock', path: '/stock' },
  { icon: ShoppingCart, label: 'Ventas', path: '/sales' },
  { icon: BarChart3, label: 'Métricas', path: '/metrics' },
  { icon: MessageSquare, label: 'Interacciones', path: '/interactions' },
  { icon: Users, label: 'Clientes', path: '/dashboard' },
  { icon: RotateCcw, label: 'Inactivos', path: '/inactive' },
  { icon: UserCircle, label: 'Perfil', path: '/profile' },
  { icon: Settings, label: 'Configuración', path: '#' },
]

// Devuelve la etiqueta de página para una ruta (o null si no matchea).
export function getPageTitle(pathname) {
  const item = navItems.find(
    (entry) => entry.path === pathname && entry.path !== '#',
  )
  return item?.label ?? null
}
