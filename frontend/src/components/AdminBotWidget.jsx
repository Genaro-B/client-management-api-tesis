import { useState, useRef, useEffect } from 'react'
import { Bot, Send, X, RefreshCw } from 'lucide-react'
import { consultAdminBot } from '../services/adminBotService.js'

const QUICK_CHIPS = [
  'Clientes nuevos del mes',
  'Productos con stock bajo',
  'Interacciones de hoy',
  'Producto más vendido',
  'Resumen de métricas',
]

let idCounter = 0
const nextId = () => `msg-${++idCounter}`

export default function AdminBotWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'bot',
      text: '¡Hola! Soy tu asistente de gestión. Preguntame sobre clientes nuevos del mes, stock bajo, interacciones de hoy, productos más vendidos o un resumen de métricas.',
    },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef(null)

  // Auto-scroll al fondo cuando llegan mensajes nuevos o cambia el estado de escritura
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, typing])

  const send = async (texto) => {
    const trimmed = (texto || '').trim()
    if (!trimmed || typing) return
    setInput('')
    setMessages((prev) => [...prev, { id: nextId(), role: 'user', text: trimmed }])
    setTyping(true)
    try {
      const data = await consultAdminBot(trimmed)
      setMessages((prev) => [...prev, { id: nextId(), role: 'bot', text: data.respuesta }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: nextId(),
          role: 'error',
          text: err.message || 'Error al consultar al asistente',
          failedQuery: trimmed,
        },
      ])
    } finally {
      setTyping(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send(input)
    }
  }

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-5 right-5 z-40 w-14 h-14 rounded-full bg-primary text-primary-foreground shadow-lg shadow-blue-500/30 hover:bg-blue-700 active:bg-blue-800 transition-colors duration-150 flex items-center justify-center"
        title={open ? 'Cerrar asistente' : 'Asistente administrativo'}
        aria-label={open ? 'Cerrar asistente' : 'Abrir asistente'}
      >
        {open ? <X size={22} /> : <Bot size={24} />}
      </button>

      {/* Panel de chat */}
      {open && (
        <div className="fixed bottom-5 right-5 z-40 w-[360px] max-w-[calc(100vw-2.5rem)] h-[520px] max-h-[calc(100vh-6rem)] bg-card border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between py-3 px-4 border-b border-border bg-primary text-primary-foreground">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-white/15 flex items-center justify-center">
                <Bot size={17} />
              </div>
              <div>
                <p className="text-[13px] font-semibold leading-tight">Asistente Administrativo</p>
                <p className="text-[10px] text-primary-foreground/70 leading-tight">
                  Datos reales del negocio
                </p>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="p-1 rounded-md text-primary-foreground/80 hover:bg-white/15 hover:text-primary-foreground transition-colors duration-150"
              title="Cerrar"
            >
              <X size={16} />
            </button>
          </div>

          {/* Mensajes */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-background/40">
            {messages.map((msg) => {
              if (msg.role === 'error') {
                return (
                  <div key={msg.id} className="flex justify-start">
                    <div className="max-w-[85%] rounded-2xl rounded-tl-sm px-3.5 py-2.5 border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40">
                      <p className="text-[12px] text-red-600 dark:text-red-400">{msg.text}</p>
                      {msg.failedQuery && (
                        <button
                          onClick={() => send(msg.failedQuery)}
                          className="mt-1.5 inline-flex items-center gap-1 text-[11px] font-semibold text-red-600 dark:text-red-400 hover:underline"
                        >
                          <RefreshCw size={11} />
                          Reintentar
                        </button>
                      )}
                    </div>
                  </div>
                )
              }

              const isUser = msg.role === 'user'
              return (
                <div key={msg.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 text-[12.5px] leading-relaxed whitespace-pre-line ${
                      isUser
                        ? 'rounded-tr-sm bg-primary text-primary-foreground'
                        : 'rounded-tl-sm bg-secondary text-foreground'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              )
            })}

            {typing && (
              <div className="flex justify-start">
                <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-secondary text-foreground flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:120ms]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground animate-bounce [animation-delay:240ms]" />
                </div>
              </div>
            )}
          </div>

          {/* Chips de consultas rápidas */}
          <div className="px-3 pt-2 pb-1 border-t border-border flex flex-wrap gap-1.5 bg-card">
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip}
                onClick={() => send(chip)}
                disabled={typing}
                className="px-2.5 py-1 rounded-full text-[11px] font-medium text-primary bg-primary/10 hover:bg-primary/20 border border-primary/20 transition-colors duration-150 disabled:opacity-40"
              >
                {chip}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 p-3 border-t border-border bg-card">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribí tu consulta…"
              disabled={typing}
              className="flex-1 px-3.5 py-2 rounded-xl border border-border bg-background text-[13px] text-foreground placeholder:text-muted-foreground outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50"
            />
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || typing}
              className="p-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-blue-700 active:bg-blue-800 transition-colors duration-150 disabled:opacity-40 disabled:pointer-events-none flex items-center justify-center"
              title="Enviar"
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}