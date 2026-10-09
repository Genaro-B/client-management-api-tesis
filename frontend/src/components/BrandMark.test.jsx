import { render, screen } from '@testing-library/react'
import BrandMark from './BrandMark.jsx'
import { BRAND } from '../config/brand.js'

describe('BrandMark', () => {
  it('renderiza las iniciales de la marca', () => {
    render(<BrandMark />)

    expect(screen.getByText(BRAND.initials)).toBeInTheDocument()
  })

  it('muestra el nombre de la marca cuando showName es true', () => {
    render(<BrandMark showName />)

    expect(screen.getByText(BRAND.name)).toBeInTheDocument()
  })

  it('no muestra el nombre de la marca por defecto', () => {
    render(<BrandMark />)

    expect(screen.queryByText(BRAND.name)).not.toBeInTheDocument()
  })
})
