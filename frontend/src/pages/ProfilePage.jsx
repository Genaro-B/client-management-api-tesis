import { useState, useRef } from 'react'
import { Camera, Save, Loader2, User, ShieldCheck, Mail, AlertCircle } from 'lucide-react'
import Sidebar from '../components/Sidebar.jsx'
import Topbar from '../components/Topbar.jsx'
import Avatar from '../components/Avatar.jsx'
import useAuth from '../hooks/useAuth.js'

export default function ProfilePage() {
  const { user, isAdmin, logout, updateProfile, updateAvatar } = useAuth()

  const [nombre, setNombre] = useState(user?.nombre || '')
  const [apellido, setApellido] = useState(user?.apellido || '')
  const [email, setEmail] = useState(user?.email || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [avatarPreview, setAvatarPreview] = useState(null)
  const fileInputRef = useRef(null)

  const handleSave = async (e) => {
    e.preventDefault()
    if (!nombre.trim() || !apellido.trim()) {
      setError('El nombre y apellido son obligatorios')
      return
    }
    setSaving(true)
    setError(null)
    try {
      updateProfile({ nombre: nombre.trim(), apellido: apellido.trim(), email: email.trim() })
    } catch {
      setError('Error al guardar los cambios')
    } finally {
      setSaving(false)
    }
  }

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      setError('La imagen no puede superar los 2MB')
      return
    }

    // Validate type
    if (!file.type.startsWith('image/')) {
      setError('Solo se permiten archivos de imagen')
      return
    }

    const reader = new FileReader()
    reader.onload = (event) => {
      const base64 = event.target.result
      setAvatarPreview(base64)
      updateAvatar(base64)
    }
    reader.readAsDataURL(file)
  }

  const handleRemoveAvatar = () => {
    setAvatarPreview(null)
    updateAvatar(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex flex-1 flex-col overflow-hidden min-w-0 bg-background">
        <Topbar
          user={user}
          isAdmin={isAdmin}
          onLogout={logout}
          title="Perfil"
          subtitle="Gestioná tu información personal"
        />

        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-2xl mx-auto space-y-8">

            {/* Avatar section */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-[13px] font-semibold text-foreground mb-4">
                Foto de perfil
              </h3>
              <div className="flex items-center gap-6">
                <div className="relative">
                  <Avatar
                    nombre={nombre}
                    apellido={apellido}
                    src={avatarPreview || user?.avatar}
                    size="xl"
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-md hover:bg-blue-700 transition-colors border-2 border-card"
                  >
                    <Camera size={13} />
                  </button>
                </div>
                <div className="flex flex-col gap-2">
                  <p className="text-[12px] text-muted-foreground">
                    Subí una foto para tu perfil. Formatos: JPG, PNG, WebP. Máx 2MB.
                  </p>
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      className="py-1.5 px-3 rounded-lg text-[11px] font-semibold bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors"
                    >
                      Subir foto
                    </button>
                    {(avatarPreview || user?.avatar) && (
                      <button
                        type="button"
                        onClick={handleRemoveAvatar}
                        className="py-1.5 px-3 rounded-lg text-[11px] font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 border border-red-200 dark:border-red-900 transition-colors"
                      >
                        Eliminar
                      </button>
                    )}
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarChange}
                    className="hidden"
                  />
                </div>
              </div>
            </div>

            {/* Profile form */}
            <form onSubmit={handleSave} className="bg-card border border-border rounded-xl p-6 space-y-5">
              <h3 className="text-[13px] font-semibold text-foreground">
                Información personal
              </h3>

              {error && (
                <div className="flex items-center gap-2.5 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-100 dark:border-red-900">
                  <AlertCircle size={14} className="text-destructive flex-shrink-0" />
                  <p className="text-[11px] text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}

              {/* Role (read-only) */}
              <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50/50 dark:bg-blue-950/30 border border-blue-100 dark:border-blue-900">
                <ShieldCheck size={16} className="text-blue-600 dark:text-blue-400 flex-shrink-0" />
                <div>
                  <p className="text-[12px] font-medium text-foreground">
                    {isAdmin ? 'Administrador' : 'Usuario estándar'}
                  </p>
                  <p className="text-[10px] text-muted-foreground">
                    {isAdmin
                      ? 'Tenés acceso completo al sistema. El rol de administrador es fijo y no se puede modificar.'
                      : 'Acceso de solo lectura a la mayoría de las secciones.'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                    Nombre
                  </label>
                  <div className="relative">
                    <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={nombre}
                      onChange={(e) => setNombre(e.target.value)}
                      className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)]"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                    Apellido
                  </label>
                  <div className="relative">
                    <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={apellido}
                      onChange={(e) => setApellido(e.target.value)}
                      className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)]"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
                  Email
                </label>
                <div className="relative">
                  <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-background border border-slate-200 dark:border-slate-600 rounded-lg py-2 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground outline-none transition-all focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)]"
                  />
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-2 py-2.5 px-5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors"
                >
                  {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                  {saving ? 'Guardando…' : 'Guardar cambios'}
                </button>
              </div>
            </form>

            {/* Account info */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-[13px] font-semibold text-foreground mb-3">
                Información de la cuenta
              </h3>
              <div className="space-y-2 text-[12px] text-muted-foreground">
                <p>
                  <span className="font-medium text-foreground">Email:</span>{' '}
                  {user?.email}
                </p>
                <p>
                  <span className="font-medium text-foreground">Rol:</span>{' '}
                  {isAdmin ? 'Administrador' : 'Usuario estándar'}
                </p>
                <p className="text-[11px] text-slate-400 dark:text-slate-500 pt-2 border-t border-border mt-2">
                  Esta es una cuenta de administrador fija. No se puede eliminar. Los datos se almacenan localmente en tu navegador.
                </p>
              </div>
            </div>

          </div>
        </div>
      </main>
    </div>
  )
}
