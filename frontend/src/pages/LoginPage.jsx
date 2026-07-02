import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mail, Lock, Loader2, AlertCircle, ShieldCheck, LogIn } from 'lucide-react'
import useAuth from '../hooks/useAuth.js'

export default function LoginPage() {
  const { login, loading, error, setError } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [adminLoading, setAdminLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email.trim()) {
      setError?.('Ingresá tu email')
      return
    }
    try {
      await login(email.trim())
      navigate('/dashboard')
    } catch {
      // error handled by hook
    }
  }

  const handleAdminQuickLogin = async () => {
    setAdminLoading(true)
    setEmail('admin@utn.edu.ar')
    try {
      await login('admin@utn.edu.ar')
      navigate('/dashboard')
    } catch {
      // error handled by hook
    } finally {
      setAdminLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="flex items-center justify-between px-8 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-[12px] font-bold text-primary-foreground">G</span>
          </div>
          <span className="text-[13px] font-semibold text-foreground font-display">
            Genaro Busto
          </span>
          <span className="px-2 py-0.5 rounded-md bg-blue-50 dark:bg-blue-950/50 text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">
            UTN
          </span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 text-[11px] font-semibold">
          <ShieldCheck size={13} />
          Conexión segura
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        {/* Branding */}
        <div className="text-center mb-10">
          <img
            src="/logo.jpg"
            alt="UTN Logo"
            className="h-20 mx-auto mb-5"
          />
          <h1 className="text-[26px] font-semibold text-foreground font-display">
            UTN Tesis de Grado
          </h1>
          <p className="text-[13px] text-muted-foreground mt-2 max-w-md">
            Sistema de automatización y administración de prospectos
          </p>
          <p className="text-[12px] text-slate-400 dark:text-slate-500 mt-1">
            Plataforma para la gestión y seguimiento de prospectos académicos.
          </p>
        </div>

        {/* Login Card */}
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
                    placeholder="Contraseña (sin efecto aún)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={loading}
                    className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2.5 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] disabled:opacity-60"
                  />
                </div>
                <p className="text-[9px] text-slate-400 dark:text-slate-500 mt-1 ml-1">
                  Campo decorativo — el acceso es solo por email por ahora.
                </p>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors duration-150 flex items-center justify-center gap-2"
              >
                {loading && <Loader2 size={14} className="animate-spin" />}
                {loading ? 'Validando acceso…' : 'Iniciar sesión'}
              </button>
            </form>

            {/* Admin quick access — fixed admin account */}
            <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-700">
              <button
                type="button"
                onClick={handleAdminQuickLogin}
                disabled={loading || adminLoading}
                className="w-full flex items-center justify-center gap-2 py-2 rounded-lg border border-dashed border-blue-200 dark:border-blue-800 text-[12px] font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/40 disabled:opacity-50 transition-colors"
              >
                {adminLoading ? (
                  <Loader2 size={13} className="animate-spin" />
                ) : (
                  <LogIn size={13} />
                )}
                {adminLoading ? 'Ingresando…' : 'Acceso administrador — inicio rápido'}
              </button>
              <p className="text-[10px] text-center text-slate-400 dark:text-slate-500 mt-2">
                Cuenta fija de administrador (ID 8). No aparece en la lista de clientes.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
