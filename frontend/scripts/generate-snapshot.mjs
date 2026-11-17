import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const here = dirname(fileURLToPath(import.meta.url))
const root = resolve(here, '../..')

function parseCsv(text) {
  const [header, ...rows] = text.trim().split(/\r?\n/)
  const fields = header.split(';')
  return rows.map((row) => Object.fromEntries(row.split(';').map((value, index) => [fields[index], value])))
}

const [clientsText, sellersText, auditText] = await Promise.all([
  readFile(resolve(root, 'data/processed/clientes_limpos.csv'), 'utf8'),
  readFile(resolve(root, 'data/processed/vendedores_limpos.csv'), 'utf8'),
  readFile(resolve(root, 'data/processed/auditoria_etl.csv'), 'utf8'),
])

const clients = parseCsv(clientsText)
const sellers = parseCsv(sellersText)
const audit = parseCsv(auditText)
const byNeighborhood = Object.entries(
  clients.reduce((acc, item) => {
    acc[item.bairro_normalizado] = (acc[item.bairro_normalizado] || 0) + 1
    return acc
  }, {}),
).map(([nome, total]) => ({ nome, total }))
const byField = Object.entries(
  audit.reduce((acc, item) => {
    const key = item.campo_afetado.toUpperCase()
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {}),
).map(([campo, total]) => ({ campo, total }))

const snapshot = {
  generatedAt: new Date().toISOString(),
  clients: clients.map((item) => ({
    id_cliente: item.id_cliente,
    razao_social: item.razao_social,
    bairro_normalizado: item.bairro_normalizado,
    cidade: item.cidade,
    uf: item.uf,
    vendedor_id: Number(item.vendedor_id),
  })),
  sellers: sellers.map((item) => ({
    id_vendedor: Number(item.id_vendedor),
    nome_vendedor: item.nome_vendedor,
  })),
  metrics: {
    clientes: clients.length,
    vendedores: sellers.length,
    auditorias: audit.length,
    conflitos: audit.filter((item) => item.regra_aplicada.includes('GUARDRAIL_CONFLITO')).length,
    bairros: byNeighborhood,
    campos: byField,
  },
}

await mkdir(resolve(here, '../public'), { recursive: true })
await writeFile(resolve(here, '../public/snapshot.json'), JSON.stringify(snapshot, null, 2) + '\n', 'utf8')
console.log(`Snapshot gerado: ${clients.length} clientes, ${sellers.length} vendedores, ${audit.length} auditorias.`)
