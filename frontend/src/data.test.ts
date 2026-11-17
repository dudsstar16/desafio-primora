import { afterEach, describe, expect, it, vi } from 'vitest'
import { loadPresentationData, normalizeMetrics } from './data'

afterEach(() => vi.unstubAllGlobals())

describe('dados da apresentação', () => {
  it('normaliza o contrato agregado retornado pelo Django', () => {
    const metrics = normalizeMetrics({
      totals: { clients: 2, sellers: 1, audit_changes: 4, corrected_conflicts: 1 },
      neighborhoods: [{ name: 'Águas Claras', count: 21 }],
      audit_by_field: [{ field: 'cep', count: 47 }],
    })
    expect(metrics).toEqual({
      clientes: 2, vendedores: 1, auditorias: 4, conflitos: 1,
      bairros: [{ nome: 'Águas Claras', total: 21 }],
      campos: [{ campo: 'CEP', total: 47 }],
    })
  })

  it('usa o snapshot quando a API não responde', async () => {
    const snapshot = {
      generatedAt: '2026-11-17T00:00:00.000Z', clients: [], sellers: [],
      metrics: { clientes: 47, vendedores: 5, auditorias: 188, conflitos: 3, bairros: [], campos: [] },
    }
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
      if (String(input).endsWith('/snapshot.json')) return Promise.resolve({ ok: true, json: () => Promise.resolve(snapshot) })
      return Promise.reject(new Error('API indisponível'))
    }))
    await expect(loadPresentationData()).resolves.toMatchObject({ source: 'fallback', metrics: { clientes: 47 } })
  })
})
