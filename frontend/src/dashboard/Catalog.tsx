import { ArrowUpRight, ChevronRight } from 'lucide-react'
import type { Seller } from '../types'
import type { Customer } from './api'
import { Dialog } from './Dialogs'

export type Selection = { kind: 'customer'; id: string } | { kind: 'seller'; id: number }
export type RecordDetail = { kind: 'customer'; record: Customer } | { kind: 'seller'; record: Seller }
export type Filters = { search: string; neighborhood: string; seller: string; order: string }
export const initialFilters: Filters = { search: '', neighborhood: '', seller: '', order: 'asc' }

const collator = new Intl.Collator('pt-BR', { sensitivity: 'base', numeric: true })
const normalize = (value: string) => value.trim().normalize('NFD').replace(/\p{M}/gu, '').toLowerCase()
const dateFormatter = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeZone: 'UTC' })

export function customerCounts(customers: Customer[]) {
  const counts = new Map<number, number>()
  for (const item of customers) counts.set(item.vendedor_id, (counts.get(item.vendedor_id) ?? 0) + 1)
  return counts
}

export function Catalog({ kind, customers, sellers, counts, filters, change, choose }: {
  kind: 'customer' | 'seller'; customers: Customer[]; sellers: Seller[]; counts: Map<number, number>
  filters: Filters; change: (filters: Filters) => void; choose: (selection: Selection) => void
}) {
  const sellerNames = new Map(sellers.map(item => [item.id_vendedor, item.nome_vendedor]))
  const neighborhoods = [...new Set(customers.map(item => item.bairro_normalizado))].filter(Boolean).sort(collator.compare)
  const keyword = normalize(filters.search)
  const compare = (a: string, b: string) => (filters.order === 'asc' ? 1 : -1) * collator.compare(a, b)
  const customerRows = customers.filter(item =>
    normalize(`${item.id_cliente} ${item.razao_social}`).includes(keyword)
    && (!filters.neighborhood || item.bairro_normalizado === filters.neighborhood)
    && (!filters.seller || item.vendedor_id === Number(filters.seller)),
  ).sort((a, b) => compare(a.razao_social, b.razao_social))
  const sellerRows = sellers.filter(item => normalize(`${item.id_vendedor} ${item.nome_vendedor}`).includes(keyword))
    .sort((a, b) => compare(a.nome_vendedor, b.nome_vendedor))
  const count = kind === 'customer' ? customerRows.length : sellerRows.length

  return <>
    <div className="vetor-filters">
      <label>Buscar {kind === 'customer' ? 'cliente' : 'vendedor'}
        <input type="search" placeholder="Nome ou ID" value={filters.search}
          onChange={event => change({ ...filters, search: event.target.value })} />
      </label>
      {kind === 'customer' && <>
        <label>Bairro
          <select value={filters.neighborhood} onChange={event => change({ ...filters, neighborhood: event.target.value })}>
            <option value="">Todos</option>
            {neighborhoods.map(item => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label>Vendedor
          <select value={filters.seller} onChange={event => change({ ...filters, seller: event.target.value })}>
            <option value="">Todos</option>
            {sellers.map(item => <option key={item.id_vendedor} value={item.id_vendedor}>{item.nome_vendedor}</option>)}
          </select>
        </label>
      </>}
      <label>Ordenar por nome
        <select value={filters.order} onChange={event => change({ ...filters, order: event.target.value })}>
          <option value="asc">A–Z</option><option value="desc">Z–A</option>
        </select>
      </label>
    </div>
    <div className="vetor-results">
      <span role="status">{count} {count === 1 ? 'resultado' : 'resultados'}</span>
      {(filters.search || filters.neighborhood || filters.seller || filters.order !== 'asc')
        && <button className="vetor-text-button" onClick={() => change(initialFilters)}>Limpar filtros</button>}
    </div>
    {count === 0
      ? <div className="vetor-empty">Nenhum cadastro encontrado.</div>
      : <table className="vetor-table" aria-label={kind === 'customer' ? 'Clientes' : 'Vendedores'} role="table">
        <thead role="rowgroup"><tr role="row">
          <th scope="col" role="columnheader">Cadastro</th>
          {kind === 'customer'
            ? <><th scope="col" role="columnheader">Localidade</th><th scope="col" role="columnheader">Vendedor</th></>
            : <th scope="col" role="columnheader">Clientes vinculados</th>}
          <th scope="col" role="columnheader"><span className="vetor-sr-only">Ação</span></th>
        </tr></thead>
        <tbody role="rowgroup">{kind === 'customer'
          ? customerRows.map(item => <tr key={item.id_cliente} role="row">
            <td role="cell"><strong>{item.razao_social}</strong><small>{item.id_cliente}</small></td>
            <td role="cell"><strong>{item.bairro_normalizado || '—'}</strong><small>{item.cidade} / {item.uf}</small></td>
            <td role="cell"><span className="vetor-mobile-label">Vendedor</span>
              {sellerNames.get(item.vendedor_id) ?? item.vendedor_id}
            </td>
            <td role="cell"><button className="vetor-text-button" aria-label={`Detalhes de ${item.razao_social}`}
              onClick={() => choose({ kind, id: item.id_cliente })}>Detalhes <ChevronRight size={16} /></button></td>
          </tr>)
          : sellerRows.map(item => <tr key={item.id_vendedor} role="row">
            <td role="cell"><strong>{item.nome_vendedor}</strong><small>ID {item.id_vendedor}</small></td>
            <td role="cell"><span className="vetor-mobile-label">Clientes vinculados</span>
              {counts.get(item.id_vendedor) ?? 0}
            </td>
            <td role="cell"><button className="vetor-text-button" aria-label={`Detalhes de ${item.nome_vendedor}`}
              onClick={() => choose({ kind, id: item.id_vendedor })}>Detalhes <ChevronRight size={16} /></button></td>
          </tr>)}</tbody>
      </table>}
  </>
}

export function Details({ detail, sellers, linkedCount, canWrite, close, edit, remove, showCustomers }: {
  detail: RecordDetail; sellers: Seller[]; linkedCount: number; canWrite: boolean
  close: () => void; edit: () => void; remove: () => void; showCustomers: (id: number) => void
}) {
  const customer = detail.kind === 'customer' ? detail.record : undefined
  const seller = detail.kind === 'seller' ? detail.record : undefined
  const date = customer?.data_cadastro_normalizado ? new Date(customer.data_cadastro_normalizado) : null
  const fields = customer ? [
    ['ID', customer.id_cliente], ['CNPJ', customer.cnpj_normalizado],
    ['Telefone', customer.telefone_normalizado], ['E-mail', customer.email],
    ['Bairro', customer.bairro_normalizado], ['CEP', customer.cep_normalizado],
    ['Cidade / UF', `${customer.cidade} / ${customer.uf}`],
    ['Cadastro', date && !Number.isNaN(date.getTime()) ? dateFormatter.format(date) : customer.data_cadastro_normalizado],
    ['Vendedor', sellers.find(item => item.id_vendedor === customer.vendedor_id)?.nome_vendedor ?? customer.vendedor_id],
  ] : [['ID', seller?.id_vendedor], ['Clientes vinculados', linkedCount]]
  return <Dialog title={customer?.razao_social ?? seller?.nome_vendedor ?? 'Detalhes'} close={close}>
    <dl className="vetor-details">
      {fields.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value ?? '—'}</dd></div>)}
    </dl>
    {seller && <button className="vetor-text-button" onClick={() => showCustomers(seller.id_vendedor)}>
      Ver clientes vinculados <ArrowUpRight size={16} />
    </button>}
    {canWrite && <footer className="vetor-dialog-actions">
      <button className="vetor-button vetor-outline-danger" onClick={remove}>Excluir</button>
      <button className="vetor-button vetor-primary" onClick={edit}>Editar cadastro</button>
    </footer>}
  </Dialog>
}
