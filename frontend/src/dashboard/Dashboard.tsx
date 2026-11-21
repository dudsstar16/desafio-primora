import { useCallback, useEffect, useRef, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import {
  Activity, ArrowRight, ArrowUpRight, BriefcaseBusiness, Building2, LayoutGrid,
  LockKeyhole, LogIn, LogOut, Plus, RefreshCw, Sparkles,
} from 'lucide-react'
import type { Seller } from '../types'
import { api, ApiError, errorMessage, storeToken, storedToken, type Customer, type Health, type Identity, type Session } from './api'
import { Catalog, customerCounts, Details, initialFilters, type RecordDetail, type Selection } from './Catalog'
import { ConfirmDelete, Editor, Login, type EditTarget, type RecordBody } from './Dialogs'
import './dashboard.css'

type Area = 'overview' | 'customer' | 'seller'
const navigation = [
  { id: 'overview', label: 'Visão geral', icon: LayoutGrid },
  { id: 'customer', label: 'Clientes', icon: Building2 },
  { id: 'seller', label: 'Vendedores', icon: BriefcaseBusiness },
] as const
const dashboardKey = ['vetor-dashboard'] as const
const unauthorized = (error: unknown) => error instanceof ApiError && error.status === 401
const sessionFor = (token: string, key: number): Session => ({ token, key, controller: new AbortController() })
const numberFormat = new Intl.NumberFormat('pt-BR')
const timeFormat = new Intl.DateTimeFormat('pt-BR', { timeStyle: 'short' })
const showCount = (count?: number) => count === undefined ? '—' : numberFormat.format(count)

export default function Dashboard() {
  const queryClient = useQueryClient()
  const nextSession = useRef(1)
  const [session, setSession] = useState(() => {
    const token = storedToken()
    return token ? sessionFor(token, 0) : null
  })
  const [area, setArea] = useState<Area>('overview')
  const [filters, setFilters] = useState(initialFilters)
  const [selection, setSelection] = useState<Selection | null>(null)
  const [editor, setEditor] = useState<EditTarget | null>(null)
  const [deletion, setDeletion] = useState<RecordDetail | null>(null)
  const [loginOpen, setLoginOpen] = useState(false)
  const [notice, setNotice] = useState('')

  const identity = useQuery({
    queryKey: [...dashboardKey, session?.key, 'identity'],
    queryFn: ({ signal }) => api<Identity>('/auth/me/', { session, signal }),
    enabled: Boolean(session),
    retry: false,
  })
  const activeSession = session && identity.data?.can_write && !identity.isError ? session : null
  const scope = activeSession?.key ?? 'public'
  const customers = useQuery({
    queryKey: [...dashboardKey, scope, 'customers'],
    queryFn: ({ signal }) => api<Customer[]>('/clientes/', { session: activeSession, signal }),
    retry: false,
  })
  const sellers = useQuery({
    queryKey: [...dashboardKey, scope, 'sellers'],
    queryFn: ({ signal }) => api<Seller[]>('/vendedores/', { session: activeSession, signal }),
    retry: false,
  })
  const health = useQuery({
    queryKey: [...dashboardKey, 'health'],
    queryFn: ({ signal }) => api<Health>('/health/', { signal }),
    retry: false,
  })

  const signOut = useCallback((message: string) => {
    if (session) {
      session.controller.abort()
      const key = [...dashboardKey, session.key]
      void queryClient.cancelQueries({ queryKey: key })
      queryClient.removeQueries({ queryKey: key })
    }
    storeToken(null)
    setSession(null)
    setSelection(null)
    setEditor(null)
    setDeletion(null)
    setNotice(message)
  }, [queryClient, session])
  const sessionRejected = Boolean(session && (
    unauthorized(identity.error) || (activeSession && (unauthorized(customers.error) || unauthorized(sellers.error)))
    || (identity.data && !identity.data.can_write)
  ))
  useEffect(() => {
    if (sessionRejected) signOut('A sessão perdeu a autorização. Entre novamente para editar cadastros.')
  }, [sessionRejected, signOut])

  async function login(username: string, password: string) {
    const { token } = await api<{ token: string }>('/auth/token/', { method: 'POST', body: { username, password } })
    const candidate = sessionFor(token, nextSession.current++)
    const profile = await api<Identity>('/auth/me/', { session: candidate })
    if (!profile.can_write) throw new ApiError(403, { detail: 'Esta conta não pode alterar cadastros.' })
    queryClient.setQueryData([...dashboardKey, candidate.key, 'identity'], profile)
    storeToken(token)
    setSession(candidate)
    setLoginOpen(false)
    setNotice(`Sessão iniciada como ${profile.username}.`)
  }

  function goTo(next: Area, sellerId?: number) {
    setArea(next)
    setSelection(null)
    setFilters({ ...initialFilters, seller: sellerId === undefined ? '' : String(sellerId) })
  }

  async function write(kind: 'customer' | 'seller', method: 'POST' | 'PATCH' | 'DELETE',
    id?: string | number, body?: RecordBody) {
    if (!activeSession || sessionRejected) return
    const path = kind === 'customer' ? '/clientes/' : '/vendedores/'
    const url = id === undefined ? path : `${path}${encodeURIComponent(id)}/`
    try {
      await api(url, { method, body, session: activeSession })
    } catch (error) {
      if (unauthorized(error)) signOut('A sessão perdeu a autorização. Entre novamente para editar cadastros.')
      throw error
    }
    setSelection(null)
    setEditor(null)
    setDeletion(null)
    setNotice(method === 'DELETE' ? 'Cadastro excluído.' : 'Cadastro salvo.')
    await queryClient.invalidateQueries({
      predicate: query => query.queryKey[0] === dashboardKey[0]
        && (query.queryKey[2] === 'customers' || query.queryKey[2] === 'sellers'),
    })
    void queryClient.invalidateQueries({ queryKey: ['presentation'] })
  }

  function save(body: RecordBody) {
    if (!editor) return Promise.resolve()
    const id = editor.kind === 'customer' ? editor.record?.id_cliente : editor.record?.id_vendedor
    return write(editor.kind, id === undefined ? 'POST' : 'PATCH', id, body)
  }

  const customerRows = sessionRejected || customers.isError ? undefined : customers.data
  const sellerRows = sessionRejected || sellers.isError ? undefined : sellers.data
  const counts = customerCounts(customerRows ?? [])
  const canWrite = Boolean(activeSession && !sessionRejected)
  const customer = selection?.kind === 'customer' ? customerRows?.find(item => item.id_cliente === selection.id) : undefined
  const seller = selection?.kind === 'seller' ? sellerRows?.find(item => item.id_vendedor === selection.id) : undefined
  const detail: RecordDetail | null = customer ? { kind: 'customer', record: customer }
    : seller ? { kind: 'seller', record: seller } : null
  const catalogError = customers.error || sellers.error
  const refresh = () => {
    void customers.refetch()
    void sellers.refetch()
    void health.refetch()
  }
  const connected = !health.isError && health.data?.status === 'ok' && health.data?.database === 'available'
  const healthLabel = health.isPending ? 'Verificando' : connected ? 'Operacional' : 'Indisponível'
  const updated = Math.max(customers.dataUpdatedAt, sellers.dataUpdatedAt, health.dataUpdatedAt)
  const refreshing = customers.isFetching || sellers.isFetching || health.isFetching
  const areaLabel = navigation.find(item => item.id === area)?.label

  return <div className="vetor">
    <aside className="vetor-rail">
      <a href="/" className="vetor-brand"><Sparkles size={23} aria-hidden="true" /><span>Vetor<small>Distribuidora</small></span></a>
      <nav aria-label="Seções do painel">
        {navigation.map(({ id, label, icon: Icon }) => <button key={id} aria-current={id === area ? 'page' : undefined}
          onClick={() => goTo(id)}><Icon size={19} aria-hidden="true" />{label}</button>)}
      </nav>
      <a className="vetor-back" href="/">Apresentação <ArrowUpRight size={16} /></a>
    </aside>
    <main id="conteudo" tabIndex={-1} className="vetor-main">
      <header className="vetor-top">
        <p>Painel operacional <span>/ {areaLabel}</span></p>
        <div className="vetor-actions">
          <span className="vetor-mode"><LockKeyhole size={15} aria-hidden="true" />
            {canWrite ? `Modo administrativo · ${identity.data?.username}` : 'Somente leitura'}
          </span>
          {session ? <button className="vetor-button" onClick={() => signOut('Sessão encerrada.')}>
            <LogOut size={16} /> Sair
          </button> : <button className="vetor-button vetor-primary" onClick={() => setLoginOpen(true)}>
            <LogIn size={16} /> Entrar
          </button>}
        </div>
      </header>
      <div className="vetor-content">
        {notice && <p className="vetor-notice" role="status">{notice}</p>}
        {session && !sessionRejected && !canWrite && <div className="vetor-notice" role="status">
          {identity.isError ? <>Não foi possível verificar o login. <button className="vetor-text-button"
            onClick={() => void identity.refetch()}>Tentar novamente</button></> : 'Validando sessão…'}
        </div>}
        <section className="vetor-intro">
          <div>
            <h1>{areaLabel}<span>.</span></h1>
            <p>{area === 'overview' ? 'Acompanhe os cadastros e o estado da API da Distribuidora Vetor.'
              : area === 'customer' ? 'Consulte cadastros por bairro ou vendedor.' : 'Consulte vendedores e os clientes que atendem.'}</p>
          </div>
          <button className="vetor-button" disabled={refreshing} onClick={refresh}>
            <RefreshCw size={16} /> Atualizar dados
          </button>
        </section>

        <div className="vetor-summary" aria-label="Resumo dos cadastros e da API">
          <button className="vetor-stat" onClick={() => goTo('customer')}>
            <span><Building2 size={17} /> Clientes</span><strong>{showCount(customerRows?.length)}</strong>
            <small>Explorar clientes <ArrowRight size={14} /></small>
          </button>
          <button className="vetor-stat" onClick={() => goTo('seller')}>
            <span><BriefcaseBusiness size={17} /> Vendedores</span><strong>{showCount(sellerRows?.length)}</strong>
            <small>Explorar vendedores <ArrowRight size={14} /></small>
          </button>
          <article className="vetor-stat vetor-stat-health">
            <span><Activity size={17} /> Saúde da API</span>
            <strong className="vetor-health" role="status">{healthLabel}</strong>
            <small>{health.isError ? errorMessage(health.error) : connected ? 'Banco de dados disponível' : 'Verificação da API e do banco'}</small>
          </article>
        </div>

        {area === 'overview' ? <section className="vetor-panel" aria-labelledby="distribution-title">
          <div className="vetor-panel-header"><div>
            <h2 id="distribution-title">Carteira por vendedor</h2>
            <p>Abra uma carteira para ver os clientes vinculados.</p>
          </div></div>
          {customerRows && sellerRows && sellerRows.length > 0
            ? <ul className="vetor-distribution">
              {[...sellerRows].sort((a, b) => (counts.get(b.id_vendedor) ?? 0) - (counts.get(a.id_vendedor) ?? 0))
                .map(item => <li key={item.id_vendedor}>
                  <button onClick={() => goTo('customer', item.id_vendedor)}>
                    <span>{item.nome_vendedor}</span>
                    <meter min={0} max={Math.max(customerRows.length, 1)} value={counts.get(item.id_vendedor) ?? 0}
                      aria-label={`Clientes de ${item.nome_vendedor}`} />
                    <strong>{counts.get(item.id_vendedor) ?? 0}</strong><ArrowUpRight size={16} />
                  </button>
                </li>)}
            </ul>
            : <CatalogStatus error={catalogError} ready={Boolean(customerRows && sellerRows)} refresh={refresh} />}
        </section> : <section className="vetor-panel" aria-labelledby="catalog-title">
          <div className="vetor-panel-header">
            <div><h2 id="catalog-title">{area === 'customer' ? 'Cadastro de clientes' : 'Cadastro de vendedores'}</h2>
              {area === 'customer' && !canWrite && <p>CNPJ, telefone e e-mail aparecem mascarados nas consultas públicas.</p>}
            </div>
            {canWrite && customerRows && sellerRows && <button className="vetor-button vetor-primary"
              disabled={area === 'customer' && sellerRows.length === 0} onClick={() => setEditor({ kind: area })}>
              <Plus size={17} />{area === 'customer' ? 'Novo cliente' : 'Novo vendedor'}
            </button>}
          </div>
          {canWrite && area === 'customer' && sellerRows?.length === 0 && <p>Cadastre um vendedor para vincular ao novo cliente.</p>}
          {customerRows && sellerRows
            ? <Catalog kind={area} customers={customerRows} sellers={sellerRows} counts={counts} filters={filters}
              change={setFilters} choose={setSelection} />
            : <CatalogStatus error={catalogError} ready={false} refresh={refresh} />}
        </section>}
        {updated > 0 && <footer className="vetor-footer">Última leitura da API às {timeFormat.format(updated)}</footer>}
      </div>
    </main>

    {loginOpen && <Login close={() => setLoginOpen(false)} login={login} />}
    {detail && <Details detail={detail} sellers={sellerRows ?? []}
      linkedCount={seller ? counts.get(seller.id_vendedor) ?? 0 : 0}
      canWrite={canWrite} close={() => setSelection(null)}
      edit={() => { setSelection(null); setEditor(detail) }}
      remove={() => { setSelection(null); setDeletion(detail) }}
      showCustomers={id => goTo('customer', id)} />}
    {canWrite && editor && <Editor target={editor} sellers={sellerRows ?? []} close={() => setEditor(null)} save={save} />}
    {canWrite && deletion && <ConfirmDelete
      name={deletion.kind === 'customer' ? deletion.record.razao_social : deletion.record.nome_vendedor}
      close={() => setDeletion(null)}
      remove={() => write(deletion.kind, 'DELETE', deletion.kind === 'customer'
        ? deletion.record.id_cliente : deletion.record.id_vendedor)} />}
  </div>
}

function CatalogStatus({ error, ready, refresh }: { error: unknown; ready: boolean; refresh: () => void }) {
  if (error) return <div className="vetor-empty">
    <p role="alert">{errorMessage(error)}</p>
    <button className="vetor-button" onClick={refresh}>Tentar novamente</button>
  </div>
  return <p className="vetor-empty" role="status">{ready ? 'Nenhum vendedor cadastrado.' : 'Consultando cadastros…'}</p>
}
