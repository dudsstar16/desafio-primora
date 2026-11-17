export type Client = {
  id_cliente: string
  razao_social: string
  bairro_normalizado: string
  cidade: string
  uf: string
  vendedor_id: number
}

export type Seller = {
  id_vendedor: number
  nome_vendedor: string
}

export type MetricItem = { nome?: string; campo?: string; total: number }

export type Metrics = {
  clientes: number
  vendedores: number
  auditorias: number
  conflitos: number
  bairros: MetricItem[]
  campos: MetricItem[]
}

export type Snapshot = {
  generatedAt: string
  clients: Client[]
  sellers: Seller[]
  metrics: Metrics
}

export type PresentationData = Snapshot & {
  source: 'live' | 'fallback'
}
