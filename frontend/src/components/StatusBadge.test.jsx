import { render, screen } from '@testing-library/react'
import StatusBadge from './StatusBadge.jsx'

describe('StatusBadge', () => {
  it('muestra "Activo" cuando activo=true', () => {
    render(<StatusBadge activo={true} />)

    expect(screen.getByText('Activo')).toBeInTheDocument()
    expect(screen.queryByText('Inactivo')).not.toBeInTheDocument()
  })

  it('muestra "Inactivo" cuando activo=false', () => {
    render(<StatusBadge activo={false} />)

    expect(screen.getByText('Inactivo')).toBeInTheDocument()
    expect(screen.queryByText('Activo')).not.toBeInTheDocument()
  })

  it('trata activo=1 (número) como activo', () => {
    render(<StatusBadge activo={1} />)

    expect(screen.getByText('Activo')).toBeInTheDocument()
  })

  it('trata activo=0 (número) como inactivo', () => {
    render(<StatusBadge activo={0} />)

    expect(screen.getByText('Inactivo')).toBeInTheDocument()
  })
})