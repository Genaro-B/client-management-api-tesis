import { Moon, Sun } from 'lucide-react'
import useTheme from '../hooks/useTheme.js'

export default function ThemeToggle() {
  const { dark, toggle } = useTheme()

  return (
    <button
      onClick={toggle}
      className="p-2.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150"
      title={dark ? 'Activar modo claro' : 'Activar modo oscuro'}
    >
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  )
}
