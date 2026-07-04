import { useState, useEffect } from 'react'
import Modal from './Modal.jsx'
import { Loader2 } from 'lucide-react'

const emptyForm = {
  nombre: '',
  descripcion: '',
  precio: '',
  stock: '',
  categoria: '',
}

export default function ProductFormModal({ product, onClose, onSave }) {
  const isEditing = !!product
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (product) {
      setForm({
        nombre: product.nombre || '',
        descripcion: product.descripcion || '',
        precio: product.precio?.toString() || '',
        stock: product.stock?.toString() || '',
        categoria: product.categoria || '',
      })
    } else {
      setForm(emptyForm)
    }
  }, [product])

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: null }))
  }

  const validate = () => {
    const errs = {}
    if (!form.nombre.trim()) errs.nombre = 'El nombre es obligatorio'
    const precio = parseFloat(form.precio)
    if (form.precio === '' || isNaN(precio)) errs.precio = 'El precio es obligatorio'
    else if (precio < 0) errs.precio = 'El precio no puede ser negativo'
    const stock = parseInt(form.stock, 10)
    if (form.stock !== '' && !isNaN(stock) && stock < 0) errs.stock = 'El stock no puede ser negativo'
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
        descripcion: form.descripcion.trim() || undefined,
        precio: parseFloat(form.precio),
        stock: form.stock !== '' ? parseInt(form.stock, 10) : 0,
        categoria: form.categoria.trim() || undefined,
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
    <Modal title={isEditing ? 'Editar Producto' : 'Nuevo Producto'} onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field
          label="Nombre"
          value={form.nombre}
          onChange={(v) => handleChange('nombre', v)}
          error={errors.nombre}
          disabled={saving}
          required
        />

        <Field
          label="Descripción"
          value={form.descripcion}
          onChange={(v) => handleChange('descripcion', v)}
          disabled={saving}
          textarea
        />

        <div className="grid grid-cols-2 gap-3">
          <Field
            label="Precio ($)"
            type="number"
            step="0.01"
            min="0"
            value={form.precio}
            onChange={(v) => handleChange('precio', v)}
            error={errors.precio}
            disabled={saving}
            required
          />
          <Field
            label="Stock"
            type="number"
            min="0"
            value={form.stock}
            onChange={(v) => handleChange('stock', v)}
            error={errors.stock}
            disabled={saving}
          />
        </div>

        <Field
          label="Categoría"
          value={form.categoria}
          onChange={(v) => handleChange('categoria', v)}
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

function Field({ label, type = 'text', step, min, value, onChange, error, disabled, required, textarea }) {
  const inputClass = `w-full bg-background border rounded-lg py-2.5 px-3 text-[13px] text-foreground outline-none transition-all duration-150 focus:border-primary focus:shadow-[0_0_0_3px_rgba(37,99,235,0.20)] disabled:opacity-60 ${
    error ? 'border-destructive' : 'border-slate-200 dark:border-slate-600'
  }`

  return (
    <div>
      <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
        {label}
        {required && <span className="text-destructive ml-0.5">*</span>}
      </label>
      {textarea ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          rows={3}
          className={`${inputClass} resize-none`}
        />
      ) : (
        <input
          type={type}
          step={step}
          min={min}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className={inputClass}
        />
      )}
      {error && <p className="text-[11px] text-destructive mt-1">{error}</p>}
    </div>
  )
}
