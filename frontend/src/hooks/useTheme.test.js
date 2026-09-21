import { renderHook, act } from '@testing-library/react'
import useTheme from './useTheme.js'

describe('useTheme', () => {
  it('arranca en modo oscuro cuando localStorage tiene crm_theme=dark', () => {
    localStorage.setItem('crm_theme', 'dark')

    const { result } = renderHook(() => useTheme())

    expect(result.current.dark).toBe(true)
  })

  it('arranca en modo claro cuando localStorage tiene crm_theme=light', () => {
    localStorage.setItem('crm_theme', 'light')

    const { result } = renderHook(() => useTheme())

    expect(result.current.dark).toBe(false)
  })

  it('usa la preferencia del sistema (matchMedia) cuando no hay valor guardado', () => {
    vi.stubGlobal('matchMedia', vi.fn().mockReturnValue({
      matches: true,
      media: '(prefers-color-scheme: dark)',
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    }))

    const { result } = renderHook(() => useTheme())

    expect(result.current.dark).toBe(true)

    vi.unstubAllGlobals()
  })

  it('toggle invierte el estado y persiste el nuevo valor en localStorage', () => {
    localStorage.setItem('crm_theme', 'dark')

    const { result } = renderHook(() => useTheme())
    expect(result.current.dark).toBe(true)

    act(() => result.current.toggle())

    expect(result.current.dark).toBe(false)
    expect(localStorage.getItem('crm_theme')).toBe('light')
  })

  it('agrega y remueve la clase dark en <html> según el estado', () => {
    localStorage.setItem('crm_theme', 'dark')

    const { result } = renderHook(() => useTheme())
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    act(() => result.current.toggle())

    expect(result.current.dark).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})