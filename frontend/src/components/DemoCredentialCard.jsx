import { Shield, Eye } from 'lucide-react'

export default function DemoCredentialCard({ role, email, password, onLogin, disabled, variant = 'admin' }) {
  const isAdmin = variant === 'admin'

  return (
    <button
      onClick={() => onLogin(email, password)}
      disabled={disabled}
      className={`flex-1 p-3 rounded-xl border text-left transition-all duration-150 hover:shadow-md disabled:opacity-60 disabled:cursor-not-allowed ${
        isAdmin
          ? 'bg-blue-50/50 border-blue-100 hover:bg-blue-50 dark:bg-blue-950/30 dark:border-blue-900 dark:hover:bg-blue-950/50'
          : 'bg-slate-50 border-slate-200 hover:bg-slate-100 dark:bg-slate-900/50 dark:border-slate-700 dark:hover:bg-slate-800'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
          isAdmin ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300'
        }`}>
          <Shield size={12} />
        </div>
        <span className={`text-[11px] font-semibold ${isAdmin ? 'text-blue-700 dark:text-blue-300' : 'text-slate-700 dark:text-slate-300'}`}>
          {role}
        </span>
      </div>
      <p className="text-[10px] text-muted-foreground font-mono truncate">{email}</p>
      <div className="flex items-center gap-1 mt-1">
        <Eye size={10} className="text-slate-400 dark:text-slate-500" />
          <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">{password}</span>
      </div>
    </button>
  )
}
