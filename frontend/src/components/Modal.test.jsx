import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Modal from './Modal.jsx'

describe('Modal', () => {
  it('renderiza el título y los children', () => {
    render(
      <Modal title="Confirmar baja" onClose={() => {}}>
        <p>¿Seguro que querés eliminar este cliente?</p>
      </Modal>,
    )

    expect(screen.getByText('Confirmar baja')).toBeInTheDocument()
    expect(screen.getByText('¿Seguro que querés eliminar este cliente?')).toBeInTheDocument()
  })

  it('Escape invoca onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <Modal title="Hola" onClose={onClose}>
        <p>contenido</p>
      </Modal>,
    )

    await user.keyboard('{Escape}')

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('clic en el backdrop invoca onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    const { container } = render(
      <Modal title="Hola" onClose={onClose}>
        <p>contenido</p>
      </Modal>,
    )

    // container.firstChild = overlay; su primer hijo es la capa visual del backdrop
    const backdrop = container.firstChild.firstChild
    await user.click(backdrop)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('clic en el botón de cierre (X) invoca onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <Modal title="Hola" onClose={onClose}>
        <p>contenido</p>
      </Modal>,
    )

    await user.click(screen.getByRole('button'))

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('clic dentro del contenido NO invoca onClose', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()

    render(
      <Modal title="Hola" onClose={onClose}>
        <p>contenido</p>
      </Modal>,
    )

    await user.click(screen.getByText('contenido'))

    expect(onClose).not.toHaveBeenCalled()
  })
})