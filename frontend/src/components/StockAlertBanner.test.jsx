import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import StockAlertBanner from './StockAlertBanner.jsx'

// Paridad con dashboard/components.py render_stock_alert_banner(summary):
// componente presentacional puro — recibe el resumen ya calculado
// (computeStockBands) y no renderiza nada si no hay alertas.
function renderBanner(summary) {
  return render(
    <MemoryRouter initialEntries={['/metrics']}>
      <Routes>
        <Route path="/metrics" element={<StockAlertBanner summary={summary} />} />
        <Route path="/stock" element={<div>StockPage</div>} />
      </Routes>
    </MemoryRouter>,
  )
}

const resumen = (out, low, normal) => ({
  threshold: 5,
  out_of_stock: Array.from({ length: out }, (_, i) => ({ id: i })),
  low_stock: Array.from({ length: low }, (_, i) => ({ id: i })),
  normal: Array.from({ length: normal }, (_, i) => ({ id: i })),
  counts: { out_of_stock: out, low_stock: low, normal, alert: out + low },
})

describe('StockAlertBanner', () => {
  it('no renderiza nada sin resumen (carga en curso o error)', () => {
    const { container } = renderBanner(null)

    expect(container).toBeEmptyDOMElement()
  })

  it('no renderiza nada cuando no hay alertas (alert = 0)', () => {
    const { container } = renderBanner(resumen(0, 0, 10))

    expect(container).toBeEmptyDOMElement()
  })

  it('muestra el texto exacto con pluralización cuando hay alertas', () => {
    renderBanner(resumen(1, 2, 4))

    expect(
      screen.getByText('⚠ 3 productos con stock crítico (1 agotado)'),
    ).toBeInTheDocument()
  })

  it('usa singular cuando hay una sola alerta', () => {
    renderBanner(resumen(0, 1, 9))

    expect(
      screen.getByText('⚠ 1 producto con stock crítico (0 agotados)'),
    ).toBeInTheDocument()
  })

  it('usa tono crítico (rojo) cuando hay agotados y tono de advertencia (ámbar) si solo hay críticos', () => {
    const { container, unmount } = renderBanner(resumen(1, 0, 5))
    expect(container.querySelector('[class*="bg-red-50"]')).toBeInTheDocument()
    unmount()

    const critico = renderBanner(resumen(0, 3, 5))
    expect(critico.container.querySelector('[class*="bg-amber-50"]')).toBeInTheDocument()
    expect(critico.container.querySelector('[class*="bg-red-50"]')).not.toBeInTheDocument()
  })

  it('el botón "Ver stock →" navega a /stock', async () => {
    renderBanner(resumen(1, 0, 0))
    const user = userEvent.setup()

    await user.click(screen.getByRole('button', { name: 'Ver stock →' }))

    expect(await screen.findByText('StockPage')).toBeInTheDocument()
  })
})
