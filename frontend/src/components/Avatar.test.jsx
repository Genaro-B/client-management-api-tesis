import { render, screen } from '@testing-library/react'
import Avatar from './Avatar.jsx'

describe('Avatar', () => {
  it('muestra las iniciales "JP" para Juan Pérez', () => {
    render(<Avatar nombre="Juan" apellido="Pérez" />)

    expect(screen.getByText('JP')).toBeInTheDocument()
  })

  it('convierte las iniciales a mayúsculas', () => {
    render(<Avatar nombre="ana" apellido="gomez" />)

    expect(screen.getByText('AG')).toBeInTheDocument()
  })

  it('usa "?" como inicial cuando falta nombre o apellido', () => {
    render(<Avatar nombre="" apellido="" />)

    expect(screen.getByText('??')).toBeInTheDocument()
  })

  it('con src renderiza una <img> con el alt correcto', () => {
    render(<Avatar nombre="Juan" apellido="Pérez" src="https://example.com/foto.jpg" />)

    const img = screen.getByRole('img', { name: 'Juan Pérez' })
    expect(img).toHaveAttribute('src', 'https://example.com/foto.jpg')
    expect(screen.queryByText('JP')).not.toBeInTheDocument()
  })
})