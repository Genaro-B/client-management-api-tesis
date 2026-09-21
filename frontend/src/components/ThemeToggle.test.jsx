import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ThemeToggle from './ThemeToggle.jsx'

describe('ThemeToggle', () => {
  it('en modo claro muestra el ícono Moon y título "Activar modo oscuro"', () => {
    localStorage.setItem('crm_theme', 'light')

    render(<ThemeToggle />)

    expect(document.querySelector('.lucide-moon')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Activar modo oscuro' })).toBeInTheDocument()
  })

  it('en modo oscuro muestra el ícono Sun y título "Activar modo claro"', () => {
    localStorage.setItem('crm_theme', 'dark')

    render(<ThemeToggle />)

    expect(document.querySelector('.lucide-sun')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Activar modo claro' })).toBeInTheDocument()
  })

  it('al hacer clic invierte el tema y lo persiste en localStorage', async () => {
    const user = userEvent.setup()
    localStorage.setItem('crm_theme', 'light')

    render(<ThemeToggle />)
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    await user.click(screen.getByRole('button', { name: 'Activar modo oscuro' }))

    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('crm_theme')).toBe('dark')
    expect(document.querySelector('.lucide-sun')).toBeInTheDocument()
  })
})