import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Pagination from './Pagination.jsx'

describe('Pagination', () => {
  it('muestra el rango visible "Mostrando X–Y de Z"', () => {
    render(
      <Pagination page={2} totalPages={3} total={45} pageSize={20} onPageChange={() => {}} />,
    )

    expect(screen.getByText('Mostrando 21–40 de 45')).toBeInTheDocument()
    expect(screen.getByText('Página 2 de 3')).toBeInTheDocument()
  })

  it('muestra "Mostrando 0–0 de 0" cuando no hay registros', () => {
    render(
      <Pagination page={1} totalPages={1} total={0} pageSize={20} onPageChange={() => {}} />,
    )

    expect(screen.getByText('Mostrando 0–0 de 0')).toBeInTheDocument()
  })

  it('deshabilita Anterior en la página 1', () => {
    render(
      <Pagination page={1} totalPages={5} total={100} pageSize={20} onPageChange={() => {}} />,
    )

    expect(screen.getByTitle('Anterior')).toBeDisabled()
    expect(screen.getByTitle('Siguiente')).toBeEnabled()
  })

  it('deshabilita Siguiente en la última página', () => {
    render(
      <Pagination page={5} totalPages={5} total={100} pageSize={20} onPageChange={() => {}} />,
    )

    expect(screen.getByTitle('Siguiente')).toBeDisabled()
    expect(screen.getByTitle('Anterior')).toBeEnabled()
  })

  it('Siguiente llama a onPageChange con page + 1', async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()

    render(
      <Pagination page={2} totalPages={5} total={100} pageSize={20} onPageChange={onPageChange} />,
    )

    await user.click(screen.getByTitle('Siguiente'))

    expect(onPageChange).toHaveBeenCalledWith(3)
  })

  it('Anterior llama a onPageChange con page - 1', async () => {
    const user = userEvent.setup()
    const onPageChange = vi.fn()

    render(
      <Pagination page={3} totalPages={5} total={100} pageSize={20} onPageChange={onPageChange} />,
    )

    await user.click(screen.getByTitle('Anterior'))

    expect(onPageChange).toHaveBeenCalledWith(2)
  })

  it('no renderiza controles cuando totalPages === 1', () => {
    render(
      <Pagination page={1} totalPages={1} total={10} pageSize={20} onPageChange={() => {}} />,
    )

    expect(screen.queryByTitle('Anterior')).not.toBeInTheDocument()
    expect(screen.queryByTitle('Siguiente')).not.toBeInTheDocument()
    expect(screen.queryByText(/Página 1 de 1/)).not.toBeInTheDocument()
  })
})