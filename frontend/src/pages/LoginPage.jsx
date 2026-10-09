import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Loader2, AlertCircle, ShieldCheck, BarChart3, Users } from 'lucide-react'
import useAuth from '../hooks/useAuth.js'
import BrandMark from '../components/BrandMark.jsx'
import { BRAND } from '../config/brand.js'

const BENEFITS = [
  { icon: ShieldCheck, text: 'Conexión segura y datos protegidos' },
  { icon: BarChart3, text: 'Métricas y seguimiento en tiempo real' },
  { icon: Users, text: 'Gestión integral de clientes y productos' },
]

export default function LoginPage() {
  const { login, loading, error, setError } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim()) {
      setError?.('Ingresá tu email')
      return
    }
    if (!password) {
      setError?.('Ingresá tu contraseña')
      return
    }
    try {
      const user = await login(email.trim(), password)
      navigate(user?.password_change_required ? '/change-password' : '/dashboard')
    } catch {
      // error handled by hook
    }
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* ── Panel de marca (izquierda, oculto en pantallas chicas) ── */}
      <aside className="hidden lg:flex lg:w-1/2 relative flex-col justify-between p-12 bg-sidebar text-sidebar-foreground overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/25 via-transparent to-indigo-600/20" />
        <div className="pointer-events-none absolute -top-24 -left-24 w-96 h-96 rounded-full bg-primary/20 blur-3xl" />

        <div className="relative">
          <BrandMark size="lg" showName />
        </div>

        <div className="relative max-w-md">
          <h1 className="text-[32px] leading-tight font-semibold font-display">
            {BRAND.tagline}
          </h1>
          <p className="text-[13px] text-slate-400 mt-4">
            Sistema de automatización y administración de prospectos para la
            gestión y seguimiento académico.
          </p>

          <ul className="mt-8 space-y-4">
            {BENEFITS.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-[13px] text-slate-300">
                <span className="w-8 h-8 rounded-lg bg-white/7 flex items-center justify-center flex-shrink-0">
                  <Icon size={15} strokeWidth={1.75} className="text-primary" />
                </span>
                {text}
              </li>
            ))}
          </ul>
        </div>

        <div className="relative flex items-center gap-3 text-[12px] text-slate-500">
          <span>{BRAND.name}</span>
          <span className="w-1 h-1 rounded-full bg-slate-600" />
          <span>UTN · Tesis de grado</span>
        </div>
      </aside>

      {/* ── Panel del formulario (derecha) ── */}
      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-8 py-4">
          <div className="flex items-center gap-3 lg:hidden">
            <BrandMark size="sm" showName className="text-foreground" />
          </div>
          <div className="hidden lg:block" />
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 text-[11px] font-semibold">
            <ShieldCheck size={13} />
            Conexión segura
          </div>
        </header>

        <main className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="w-full max-w-md bg-card border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl">
            <div className="p-6">
              <h2 className="text-[15px] font-semibold text-foreground mb-5">
                Iniciar sesión
              </h2>

              {error && (
                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900 mb-4">
                  <AlertCircle size={15} className="text-destructive flex-shrink-0" />
                  <p className="text-[12px] text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                    Email
                  </label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="email"
                      placeholder="Ingrese su email institucional"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                      className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2.5 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] disabled:opacity-60"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                    Contraseña
                  </label>
                  <div className="relative">
                    <Lock size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="password"
                      placeholder="Ingrese su contraseña"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                      className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2.5 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] disabled:opacity-60"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors duration-150 flex items-center justify-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-card"
                >
                  {loading && <Loader2 size={14} className="animate-spin" />}
                  {loading ? 'Validando acceso…' : 'Iniciar sesión'}
                </button>
              </form>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
