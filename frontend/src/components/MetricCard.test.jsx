import { render, screen } from '@testing-library/react'
import { AlertTriangle } from 'lucide-react'
import MetricCard from './MetricCard.jsx'

describe('MetricCard', () => {
  it('renderiza etiqueta y valor', () => {
    render(<MetricCard label="Agotados" value={3} />)

    expect(screen.getByText('Agotados')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('renderiza el ícono cuando se pasa (chip de tone)', () => {
    const { container } = render(
      <MetricCard
        label="Críticos"
        value={2}
        icon={AlertTriangle}
        tone={{ bg: 'bg-amber-50', ring: 'ring-amber-100', color: 'text-amber-600' }}
      />,
    )

    expect(screen.getByText('Críticos')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('soporta valores no numéricos (umbral)', () => {
    render(<MetricCard label="Umbral crítico" value="≤ 5" />)

    expect(screen.getByText('Umbral crítico')).toBeInTheDocument()
    expect(screen.getByText('≤ 5')).toBeInTheDocument()
  })
})
