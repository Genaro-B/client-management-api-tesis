import { useState, useEffect } from 'react'
import Modal from './Modal.jsx'
import { Loader2 } from 'lucide-react'

const emptyForm = {
  nombre: '',
  apellido: '',
  email: '',
  telefono: '',
}

export default function ClientFormModal({ client, onClose, onSave }) {
  const isEditing = !!client
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (client) {
      setForm({
        nombre: client.nombre || '',
        apellido: client.apellido || '',
        email: client.email || '',
        telefono: client.telefono || '',
      })
    } else {
      setForm(emptyForm)
    }
  }, [client])

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: null }))
  }

  const validate = () => {
    const errs = {}
    if (!form.nombre.trim()) errs.nombre = 'El nombre es obligatorio'
    if (!form.apellido.trim()) errs.apellido = 'El apellido es obligatorio'
    if (!form.email.trim()) errs.email = 'El email es obligatorio'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Email inválido'
    if (form.telefono && !/^[\d\s+\-()]+$/.test(form.telefono)) errs.telefono = 'Teléfono inválido'
    return errs
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0) return

    setSaving(true)
    try {
      const payload = {
        nombre: form.nombre.trim(),
        apellido: form.apellido.trim(),
        email: form.email.trim(),
        telefono: form.telefono.trim() || undefined,
      }
      await onSave(payload)
      onClose()
    } catch {
      // error handled by hook
    } finally {
      setSaving(false)
    }
  }

  return (
    <Modal title={isEditing ? 'Editar Cliente' : 'Nuevo Cliente'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Nombre"
            value={form.nombre}
            onChange={(v) => handleChange('nombre', v)}
            error={errors.nombre}
            disabled={saving}
            required
          />
          <Field
            label="Apellido"
            value={form.apellido}
            onChange={(v) => handleChange('apellido', v)}
            error={errors.apellido}
            disabled={saving}
            required
          />
        </div>

        <Field
          label="Email"
          type="email"
          value={form.email}
          onChange={(v) => handleChange('email', v)}
          error={errors.email}
          disabled={saving}
          required
        />

        <Field
          label="Teléfono"
          value={form.telefono}
          onChange={(v) => handleChange('telefono', v)}
          error={errors.telefono}
          disabled={saving}
        />

        <div className="flex gap-2.5 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="flex-1 py-2.5 rounded-lg bg-secondary text-slate-700 dark:text-slate-300 text-[13px] font-semibold hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors duration-150"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={saving}
            className="flex-1 py-2.5 rounded-lg bg-primary text-primary-foreground text-[13px] font-semibold hover:bg-blue-700 disabled:opacity-60 transition-colors duration-150 flex items-center justify-center gap-2"
          >
            {saving && <Loader2 size={14} className="animate-spin" />}
            {saving ? 'Guardando…' : 'Guardar'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

function Field({ label, type = 'text', value, onChange, error, disabled, required }) {
  return (
    <div>
      <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
        {label}
        {required && <span className="text-destructive ml-0.5">*</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className={`w-full bg-background border rounded-lg py-2.5 px-3 text-[13px] text-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] disabled:opacity-60 ${
          error ? 'border-destructive' : 'border-slate-200 dark:border-slate-600'
        }`}
      />
      {error && <p className="text-[11px] text-destructive mt-1">{error}</p>}
    </div>
  )
}
