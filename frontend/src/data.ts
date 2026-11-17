import type { Client, Metrics, PresentationData, Seller, Snapshot } from './types'
import offlineSnapshot from '../public/snapshot.json'

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const timeout = 2500

async function getJson<T>(path: string): Promise<T> {
  const controller = new AbortController()
  const timer = window.setTimeout(() => controller.abort(), timeout)
  try {
    const response = await fetch(`${API_URL}${path}`, { signal: controller.signal })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    return (await response.json()) as T
  } finally {
    window.clearTimeout(timer)
  }
}

export function normalizeMetrics(payload: Record<string, unknown>): Metrics {
  const totals = (payload.totais || payload.totals || payload) as Record<string, number>
  const neighborhoods = (payload.bairros || payload.neighborhoods || []) as Array<Record<string, unknown>>
  const auditFields = (payload.campos || payload.auditoria_por_campo || payload.audit_by_field || []) as Array<Record<string, unknown>>
  return {
    clientes: totals.clientes ?? totals.clients ?? 47,
    vendedores: totals.vendedores ?? totals.sellers ?? 5,
    auditorias: totals.auditorias ?? totals.audit_changes ?? 188,
    conflitos: totals.conflitos ?? totals.corrected_conflicts ?? 3,
    bairros: neighborhoods.map((item) => ({ nome: String(item.nome ?? item.name), total: Number(item.total ?? item.count) })),
    campos: auditFields.map((item) => ({ campo: String(item.campo ?? item.field).toUpperCase(), total: Number(item.total ?? item.count) })),
  }
}

export async function loadPresentationData(): Promise<PresentationData> {
  if (import.meta.env.VITE_OFFLINE_DEMO === 'true') {
    return { ...(offlineSnapshot as Snapshot), source: 'fallback' }
  }
  try {
    const [clients, sellers, rawMetrics] = await Promise.all([
      getJson<Client[]>('/api/clientes/'),
      getJson<Seller[]>('/api/vendedores/'),
      getJson<Record<string, unknown>>('/api/apresentacao/metricas/'),
    ])
    return {
      generatedAt: new Date().toISOString(),
      clients,
      sellers,
      metrics: normalizeMetrics(rawMetrics),
      source: 'live',
    }
  } catch {
    const fallback = await fetch('/snapshot.json').then((response) => response.json() as Promise<Snapshot>)
    return { ...fallback, source: 'fallback' }
  }
}
