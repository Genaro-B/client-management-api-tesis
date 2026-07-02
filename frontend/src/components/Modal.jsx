import { useEffect } from 'react'
import { X } from 'lucide-react'

export default function Modal({ title, children, onClose, size = 'md' }) {
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  const maxWidth = size === 'sm' ? 'max-w-md' : 'max-w-lg'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-[rgba(15,23,42,0.40)] dark:bg-[rgba(0,0,0,0.60)] backdrop-blur-[2px]" />

      {/* Modal shell */}
      <div
        className={`relative w-full ${maxWidth} bg-card border border-slate-200 dark:border-slate-700 rounded-xl shadow-2xl overflow-hidden`}
      >
        {/* Header */}
        <div className="flex items-center justify-between py-4 px-6 border-b border-slate-100 dark:border-slate-700">
          <h2 className="text-[15px] font-semibold text-foreground tracking-tight">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-600 dark:hover:text-slate-300 transition-colors duration-150"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="py-5 px-6">
          {children}
        </div>
      </div>
    </div>
  )
}
