import { useState, useEffect } from 'react'
import Modal from './Modal.jsx'
import { Loader2, ImagePlus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { uploadProductImage, deleteProductImage } from '../services/productService.js'

const emptyForm = {
  nombre: '',
  descripcion: '',
  precio: '',
  stock: '',
  categoria: '',
}

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp']
const MAX_IMAGE_SIZE = 2 * 1024 * 1024 // 2MB, mismo límite que el backend

export default function ProductFormModal({ product, isAdmin, onClose, onSave, onRefresh }) {
  const isEditing = !!product
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState({})
  const [selectedFile, setSelectedFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [imageError, setImageError] = useState('')
  const [removeImage, setRemoveImage] = useState(false)

  useEffect(() => {
    setSelectedFile(null)
    setPreviewUrl(null)
    setImageError('')
    setRemoveImage(false)
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

  // Liberar el object URL del preview al cambiar de archivo o desmontar el modal
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: null }))
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!ALLOWED_TYPES.includes(file.type)) {
      setImageError('Solo se permiten imágenes JPG, PNG o WebP')
      setSelectedFile(null)
      setPreviewUrl(null)
      e.target.value = ''
      return
    }
    if (file.size > MAX_IMAGE_SIZE) {
      setImageError('La imagen supera el máximo de 2MB')
      setSelectedFile(null)
      setPreviewUrl(null)
      e.target.value = ''
      return
    }

    setImageError('')
    setRemoveImage(false)
    setSelectedFile(file)
    setPreviewUrl(URL.createObjectURL(file))
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
      const saved = await onSave(payload)

      // Solo admin: subir / reemplazar / quitar la imagen tras guardar el producto
      if (isAdmin && saved?.id) {
        try {
          if (removeImage && saved.image_url) {
            await deleteProductImage(saved.id)
            toast.success('Imagen eliminada correctamente')
            onRefresh?.()
          } else if (selectedFile) {
            await uploadProductImage(saved.id, selectedFile)
            toast.success('Imagen subida correctamente')
            onRefresh?.()
          }
        } catch (imageErr) {
          toast.error(imageErr.message || 'El producto se guardó, pero no se pudo subir la imagen')
        }
      }

      onClose()
    } catch {
      // error handled by hook
    } finally {
      setSaving(false)
    }
  }

  const currentPreview = previewUrl || (isEditing && product.image_url && !removeImage ? product.image_url : null)
  const showPreviewBox = !!previewUrl || (isEditing && !!product.image_url)

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

        {isAdmin && (
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
              Imagen
            </label>

            {showPreviewBox && !removeImage && (
              <div className="mb-2 flex items-center gap-3">
                <div className="w-14 h-14 rounded-lg overflow-hidden bg-slate-100 dark:bg-slate-800 ring-1 ring-slate-200 dark:ring-slate-700 flex items-center justify-center flex-shrink-0">
                  {currentPreview ? (
                    <img src={currentPreview} alt="Preview" className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-[13px] font-bold text-slate-400">
                      {form.nombre?.charAt(0)?.toUpperCase() || '?'}
                    </span>
                  )}
                </div>
                {isEditing && product.image_url && !previewUrl && (
                  <button
                    type="button"
                    onClick={() => setRemoveImage(true)}
                    disabled={saving}
                    className="text-[12px] font-semibold text-red-500 hover:text-red-600 disabled:opacity-60 flex items-center gap-1"
                  >
                    <Trash2 size={12} />
                    Quitar imagen
                  </button>
                )}
              </div>
            )}

            {removeImage && (
              <p className="text-[11px] text-amber-600 dark:text-amber-500 mb-2">
                Se quitará la imagen al guardar.
              </p>
            )}

            {removeImage ? (
              <button
                type="button"
                onClick={() => setRemoveImage(false)}
                disabled={saving}
                className="text-[12px] font-semibold text-primary hover:text-blue-700 disabled:opacity-60"
              >
                Cancelar quitar imagen
              </button>
            ) : (
              <label className="cursor-pointer inline-flex items-center gap-2 py-2 px-3 rounded-lg bg-secondary text-[12px] font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 disabled:opacity-60 transition-colors duration-150">
                <ImagePlus size={14} />
                {currentPreview ? 'Reemplazar imagen' : 'Subir imagen'}
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                  disabled={saving}
                  className="hidden"
                />
              </label>
            )}

            {imageError && <p className="text-[11px] text-destructive mt-1">{imageError}</p>}
          </div>
        )}

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