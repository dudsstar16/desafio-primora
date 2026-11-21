import React from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Dashboard from './Dashboard'

const publicCustomer = {
  id_cliente: 'CLI0002', razao_social: 'Cliente do teste', vendedor_id: 1,
  bairro_normalizado: 'Taguatinga', cidade: 'Brasília', uf: 'DF',
  cnpj_normalizado: '************05', telefone_normalizado: '*******2084',
  email: 'c***@example.com', cep_normalizado: '72140010',
  data_cadastro_normalizado: '2023-10-07',
}
const privateCustomer = { ...publicCustomer, cnpj_normalizado: '28327648350305' }
const response = (value: unknown, status = 200) => new Response(JSON.stringify(value), {
  status, headers: { 'Content-Type': 'application/json' },
})
let client: QueryClient
const originalShowModal = Object.getOwnPropertyDescriptor(HTMLDialogElement.prototype, 'showModal')
const originalClose = Object.getOwnPropertyDescriptor(HTMLDialogElement.prototype, 'close')

beforeEach(() => {
  sessionStorage.clear()
  // Vitest's JSX runtime for existing tests is classic.
  vi.stubGlobal('React', React)
  Object.defineProperty(HTMLDialogElement.prototype, 'showModal', { configurable: true, value: function (this: HTMLDialogElement) {
    this.setAttribute('open', '')
  } })
  Object.defineProperty(HTMLDialogElement.prototype, 'close', { configurable: true, value: function (this: HTMLDialogElement) {
    this.removeAttribute('open')
  } })
  client = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: 60_000 } } })
})

afterEach(() => {
  cleanup()
  client?.clear()
  for (const [name, descriptor] of [['showModal', originalShowModal], ['close', originalClose]] as const) {
    if (descriptor) Object.defineProperty(HTMLDialogElement.prototype, name, descriptor)
    else Reflect.deleteProperty(HTMLDialogElement.prototype, name)
  }
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
  sessionStorage.clear()
})

function setup(handler?: (path: string, options: RequestInit) => Promise<Response> | undefined) {
  const fetchMock = vi.fn((input: RequestInfo | URL, options: RequestInit = {}) => {
    const path = String(input)
    const custom = handler?.(path, options)
    if (custom) return custom
    const authenticated = Boolean((options.headers as Record<string, string>)?.Authorization)
    if (path.endsWith('/auth/me/')) return Promise.resolve(response({ username: 'operadora', can_write: true }))
    if (path.endsWith('/clientes/')) return Promise.resolve(response([authenticated ? privateCustomer : publicCustomer]))
    if (path.endsWith('/vendedores/')) return Promise.resolve(response([{ id_vendedor: 1, nome_vendedor: 'Vendedor teste' }]))
    if (path.endsWith('/health/')) return Promise.resolve(response({ status: 'ok', database: 'available' }))
    throw new Error('Unexpected request ' + path)
  })
  vi.stubGlobal('fetch', fetchMock)
  render(<QueryClientProvider client={client}><Dashboard /></QueryClientProvider>)
  return fetchMock
}

async function openCustomer() {
  fireEvent.click(screen.getByRole('button', { name: 'Clientes' }))
  fireEvent.click(await screen.findByRole('button', { name: 'Detalhes de Cliente do teste' }))
}

describe('permissões e sessão do dashboard', () => {
  it('consulta publicamente sem cookies ou token e oculta controles de escrita', async () => {
    const fetchMock = setup()
    await openCustomer()
    expect(screen.getByText('************05')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Editar cadastro' })).toBeNull()
    expect(screen.queryByRole('button', { name: 'Novo cliente' })).toBeNull()
    for (const [, options] of fetchMock.mock.calls) {
      expect(options?.credentials).toBe('omit')
      expect((options?.headers as Record<string, string>).Authorization).toBeUndefined()
    }
  })

  it('remove token inválido e retorna à consulta pública', async () => {
    sessionStorage.setItem('primora:dashboard:token', 'invalido')
    setup(path => path.endsWith('/auth/me/')
      ? Promise.resolve(response({ detail: 'Token inválido' }, 401)) : undefined)
    await screen.findByText('A sessão perdeu a autorização. Entre novamente para editar cadastros.')
    expect(sessionStorage.getItem('primora:dashboard:token')).toBeNull()
    await openCustomer()
    expect(screen.getByText('************05')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Editar cadastro' })).toBeNull()
  })

  it('descarta resposta autenticada atrasada e limpa o cache após sair', async () => {
    sessionStorage.setItem('primora:dashboard:token', 'token-de-teste')
    let delayed = false
    let release: ((response: Response) => void) | undefined
    setup((path, options) => {
      if (delayed && path.endsWith('/clientes/') && (options.headers as Record<string, string>).Authorization) {
        return new Promise(resolve => { release = resolve })
      }
    })
    await screen.findByText('Modo administrativo · operadora')
    await openCustomer()
    await screen.findByText('28327648350305')
    fireEvent.click(screen.getByRole('button', { name: 'Fechar' }))
    delayed = true
    fireEvent.click(screen.getByRole('button', { name: 'Atualizar dados' }))
    await waitFor(() => expect(release).toBeDefined())
    fireEvent.click(screen.getByRole('button', { name: 'Sair' }))
    release!(response([privateCustomer]))
    await openCustomer()
    await screen.findByText('************05')
    expect(screen.queryByText('28327648350305')).toBeNull()
    expect(sessionStorage.getItem('primora:dashboard:token')).toBeNull()
    expect(client.getQueryCache().findAll({ queryKey: ['vetor-dashboard', 0] })).toHaveLength(0)
  })
})
