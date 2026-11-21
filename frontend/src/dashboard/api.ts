import type { Client } from '../types'

export type Customer = Client & {
  cnpj_normalizado: string
  telefone_normalizado: string
  email: string
  cep_normalizado: string | null
  data_cadastro_normalizado: string
}
export type Identity = { username: string; can_write: boolean }
export type Health = { status: string; database: string }
export type Session = { key: number; token: string; controller: AbortController }

const storageKey = 'primora:dashboard:token'
const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export function storedToken() {
  try {
    return sessionStorage.getItem(storageKey)
  } catch {
    return null
  }
}

export function storeToken(token: string | null) {
  try {
    if (token) sessionStorage.setItem(storageKey, token)
    else sessionStorage.removeItem(storageKey)
  } catch {
    // The current page can still operate when storage is unavailable.
  }
}

export class ApiError extends Error {
  readonly status: number
  readonly fields: Record<string, string>

  constructor(status: number, body: Record<string, unknown>) {
    super(typeof body.detail === 'string' ? body.detail : `A API retornou HTTP ${status}.`)
    this.status = status
    this.fields = Object.fromEntries(Object.entries(body)
      .filter(([, value]) => Array.isArray(value) && value.every(item => typeof item === 'string'))
      .map(([field, messages]) => [field, (messages as string[]).join(' ')]))
  }
}

export async function api<T>(
  path: string,
  { method = 'GET', body, session, signal }: {
    method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
    body?: object
    session?: Session | null
    signal?: AbortSignal
  } = {},
): Promise<T> {
  const signals = [AbortSignal.timeout(15_000)]
  if (signal) signals.push(signal)
  if (session) signals.push(session.controller.signal)
  const requestSignal = AbortSignal.any(signals)

  const response = await fetch(`${baseUrl}/api${path}`, {
    method,
    signal: requestSignal,
    credentials: 'omit',
    cache: 'no-store',
    headers: {
      Accept: 'application/json',
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(session ? { Authorization: `Token ${session.token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new ApiError(response.status, errorBody && typeof errorBody === 'object' ? errorBody : {})
  }
  const data = response.status === 204 ? undefined : await response.json()
  requestSignal.throwIfAborted()
  return data as T
}

export function errorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error && error.name === 'TimeoutError') {
    return 'O servidor demorou a responder. Ele pode estar iniciando. Tente novamente.'
  }
  return 'Não foi possível conectar à API. Tente novamente.'
}
