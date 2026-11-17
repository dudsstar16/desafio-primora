import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Background, Controls, Handle, Position, ReactFlow, type Edge, type Node, type NodeProps } from '@xyflow/react'
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import {
  ArrowDown, ArrowRight, Braces, Check, ChevronRight, CircleDot, Database, ExternalLink,
  FileJson, GitBranch, Layers3, Menu, Pause, Play, Search, Server, ShieldCheck, Sparkles, TestTube2, X,
} from 'lucide-react'
import { loadPresentationData } from './data'
import type { Client } from './types'
import Pipeline from './Pipeline'
import Decision from './Decision'
import Architecture from './Architecture'
import ApiDemo from './ApiDemo'

gsap.registerPlugin(ScrollTrigger)

const chapters = [
  ['caos', 'O caos'], ['caminho', 'O caminho'], ['decisao', 'A decisão'], ['prova', 'A prova'],
  ['resultado', 'O resultado'], ['sistema', 'O sistema vivo'], ['confianca', 'A confiança'],
] as const

const pipeline = [
  { id: 'csv', label: 'CSV bruto', file: 'data/raw', description: '47 cadastros preservados exatamente como chegaram.', example: '20 grafias para apenas 4 bairros.' },
  { id: 'extract', label: 'Extração', file: 'etl/extract.py', description: 'Todos os campos entram como texto para proteger zeros significativos.', example: '04711… continua com zero à esquerda.' },
  { id: 'normalize', label: 'Normalização', file: 'etl/transform_fields.py', description: 'CNPJ, telefone e datas assumem um formato único e previsível.', example: '+55 (61) 95386-2084 → 61953862084' },
  { id: 'cep', label: 'CEP + cache', file: 'etl/cep_service.py', description: 'ViaCEP, fallback BrasilAPI e cache local reduzem falhas e repetição.', example: 'O mesmo CEP só precisa ser consultado uma vez.' },
  { id: 'guardrail', label: 'Guardrail', file: 'etl/transform_address.py', description: 'Quando há conflito, o CEP validado prevalece sobre o texto livre.', example: 'Sul (Águas Claras) → Taguatinga' },
  { id: 'audit', label: 'Auditoria', file: 'etl/audit.py', description: 'Cada alteração registra origem, destino e regra aplicada.', example: '188 transformações rastreáveis.' },
  { id: 'db', label: 'Banco + API', file: 'etl/load.py · Django', description: 'As tabelas relacionais abastecem endpoints públicos de leitura.', example: 'SQLite local e PostgreSQL em produção.' },
]

const cases = [
  { id: 'CLI0002', title: 'O texto dizia uma coisa. O CEP, outra.', before: 'Sul (Aguas Claras)', after: 'Taguatinga', cep: '72140-010', note: 'O CEP oficial localizou o cadastro na QNM 32.' },
  { id: 'CLI0017', title: 'Uma abreviação escondia o conflito.', before: 'Vte Pires', after: 'Taguatinga', cep: '72110-800', note: 'A referência externa venceu a grafia informal.' },
  { id: 'CLI0033', title: 'Mesmo conflito, outra escrita.', before: 'Vicente Pires - DF', after: 'Taguatinga', cep: '72110-800', note: 'O sistema aplicou a mesma regra de forma determinística.' },
]

const fieldFallback = [
  { campo: 'CEP', total: 47 }, { campo: 'BAIRRO', total: 42 }, { campo: 'CNPJ', total: 38 },
  { campo: 'TELEFONE', total: 37 }, { campo: 'DATA', total: 24 },
]

const architectureNodes: Node[] = [
  { id: 'raw', position: { x: 0, y: 120 }, data: { title: 'Origem', label: 'CSV bruto', kind: 'raw', detail: 'Fonte imutável · 47 clientes' }, type: 'story' },
  { id: 'etl', position: { x: 240, y: 40 }, data: { title: 'Transformação', label: 'ETL Python', kind: 'etl', detail: 'Limpeza · CEP · guardrail' }, type: 'story' },
  { id: 'db', position: { x: 490, y: 150 }, data: { title: 'Persistência', label: 'PostgreSQL', kind: 'db', detail: '3 tabelas relacionais' }, type: 'story' },
  { id: 'django', position: { x: 740, y: 45 }, data: { title: 'Aplicação', label: 'Django REST', kind: 'api', detail: 'Regras · token · admin' }, type: 'story' },
  { id: 'user', position: { x: 980, y: 145 }, data: { title: 'Consumo', label: 'Experiência', kind: 'user', detail: 'Dados prontos para decidir' }, type: 'story' },
]
const architectureEdges: Edge[] = [
  ['raw', 'etl'], ['etl', 'db'], ['db', 'django'], ['django', 'user'],
].map(([source, target], index) => ({ id: `e${index}`, source, target, animated: true, style: { stroke: '#FFB31A', strokeWidth: 3 } }))

function StoryNode({ data }: NodeProps) {
  const d = data as { title: string; label: string; detail: string }
  return <div className="story-node" tabIndex={0}><Handle type="target" position={Position.Left} /><small>{d.title}</small><strong>{d.label}</strong><span>{d.detail}</span><Handle type="source" position={Position.Right} /></div>
}

function CountUp({ value }: { value: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  useEffect(() => {
    if (!ref.current) return
    const counter = { value: 0 }
    const tween = gsap.to(counter, { value, duration: 1.4, ease: 'power3.out', snap: { value: 1 }, scrollTrigger: { trigger: ref.current, start: 'top 90%' }, onUpdate: () => { if (ref.current) ref.current.textContent = String(counter.value) } })
    return () => { tween.kill() }
  }, [value])
  return <span ref={ref}>0</span>
}

function TiltCard({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  function move(event: React.MouseEvent<HTMLDivElement>) {
    if (!ref.current || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const rect = ref.current.getBoundingClientRect()
    const rx = ((event.clientY - rect.top) / rect.height - .5) * -5
    const ry = ((event.clientX - rect.left) / rect.width - .5) * 5
    gsap.to(ref.current, { rotateX: rx, rotateY: ry, duration: .25, transformPerspective: 800 })
  }
  return <div ref={ref} className={`tilt-card ${className}`} onMouseMove={move} onMouseLeave={() => gsap.to(ref.current, { rotateX: 0, rotateY: 0 })}>{children}</div>
}

function App() {
  const root = useRef<HTMLDivElement>(null)
  const [activeChapter, setActiveChapter] = useState('caos')
  const [menuOpen, setMenuOpen] = useState(false)
  const [presentMode, setPresentMode] = useState(false)
  const [selectedStep, setSelectedStep] = useState(pipeline[0])
  const [selectedCase, setSelectedCase] = useState(0)
  const [compare, setCompare] = useState(52)
  const [neighborhood, setNeighborhood] = useState('Todos')
  const [query, setQuery] = useState('')
  const [apiDemo, setApiDemo] = useState<'idle' | 'loading' | 'done'>('idle')
  const { data, isLoading } = useQuery({ queryKey: ['presentation'], queryFn: loadPresentationData })

  const metrics = data?.metrics ?? { clientes: 47, vendedores: 5, auditorias: 188, conflitos: 3, bairros: [], campos: [] }
  const neighborhoods = metrics.bairros.length ? metrics.bairros : [
    { nome: 'Águas Claras', total: 21 }, { nome: 'Taguatinga', total: 13 }, { nome: 'Guará', total: 6 },
    { nome: 'Vicente Pires', total: 6 }, { nome: 'Não Informado', total: 1 },
  ]
  const fieldData = metrics.campos.length ? metrics.campos : fieldFallback
  const clients = useMemo(() => (data?.clients || []).filter((client) => {
    const matchesNeighborhood = neighborhood === 'Todos' || client.bairro_normalizado === neighborhood
    const text = `${client.id_cliente} ${client.razao_social}`.toLocaleLowerCase('pt-BR')
    return matchesNeighborhood && text.includes(query.toLocaleLowerCase('pt-BR'))
  }), [data?.clients, neighborhood, query])

  useEffect(() => {
    if (!root.current || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const context = gsap.context(() => {
      gsap.from('.hero-word span', { yPercent: 115, stagger: .12, duration: 1.1, ease: 'power4.out' })
      gsap.to('.data-orbit', { rotate: 18, yPercent: 10, scrollTrigger: { trigger: '#caos', start: 'top top', end: 'bottom top', scrub: 1 } })
      gsap.utils.toArray<HTMLElement>('.reveal').forEach((item) => gsap.from(item, { y: 45, opacity: 0, duration: .8, ease: 'power3.out', scrollTrigger: { trigger: item, start: 'top 86%' } }))
      chapters.forEach(([id]) => ScrollTrigger.create({ trigger: `#${id}`, start: 'top center', end: 'bottom center', onToggle: (self) => self.isActive && setActiveChapter(id) }))
    }, root)
    return () => context.revert()
  }, [])

  function goTo(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
    setMenuOpen(false)
  }

  function runApiDemo() {
    setApiDemo('loading')
    window.setTimeout(() => setApiDemo('done'), 850)
  }

  return <div ref={root} className={presentMode ? 'app presentation-mode' : 'app'}>
    <header className="topbar">
      <button className="brand" onClick={() => goTo('caos')} aria-label="Voltar ao início"><Sparkles size={16} /> PRIMORA <span>data story</span></button>
      <div className="top-actions">
        <span className={`source-badge ${data?.source || 'loading'}`}><i />{isLoading ? 'Conectando' : data?.source === 'live' ? 'Dados ao vivo' : 'Modo demonstração'}</span>
        <button className="mode-button" onClick={() => setPresentMode((value) => !value)}>{presentMode ? <Pause size={15} /> : <Play size={15} />}{presentMode ? 'Sair da apresentação' : 'Modo apresentação'}</button>
        <button className="icon-button" onClick={() => setMenuOpen((value) => !value)} aria-label="Abrir capítulos" aria-expanded={menuOpen}>{menuOpen ? <X /> : <Menu />}</button>
      </div>
    </header>

    <nav className={`chapter-menu ${menuOpen ? 'open' : ''}`} aria-label="Capítulos da apresentação">
      <div><small>7 capítulos · 8–10 minutos</small><h2>Escolha onde<br />a história começa.</h2></div>
      <ol>{chapters.map(([id, label], index) => <li key={id}><button className={activeChapter === id ? 'active' : ''} onClick={() => goTo(id)}><span>0{index + 1}</span>{label}<ChevronRight /></button></li>)}</ol>
    </nav>

    <aside className="chapter-rail" aria-label="Progresso da apresentação">
      {chapters.map(([id, label], index) => <button key={id} className={activeChapter === id ? 'active' : ''} onClick={() => goTo(id)} aria-label={`Ir para ${label}`}><span>{String(index + 1).padStart(2, '0')}</span></button>)}
    </aside>

    <main id="conteudo">
      <section id="caos" className="chapter hero dark-section">
        <div className="hero-grid">
          <div className="eyebrow"><span>01</span> O ponto de partida</div>
          <h1 className="hero-word"><span>47 CLIENTES.</span><span className="outline">MUITAS</span><span>VERSÕES DA</span><span className="amber">VERDADE.</span></h1>
          <p className="hero-copy">Uma base que não falava a mesma língua precisava se tornar confiável, auditável e disponível para decisões reais.</p>
          <button className="round-cta" onClick={() => goTo('caminho')}>Iniciar<br />transformação<ArrowDown /></button>
        </div>
        <div className="data-orbit" aria-hidden="true">
          {['AGUAS CLARAS', 'Vte Pires', '00000-000', '+55 (61)', 'Dec 24, 2023', 'guara - df', 'Sul (Aguas Claras)'].map((item, index) => <span key={item} style={{ '--i': index } as React.CSSProperties}>{item}</span>)}
          <div className="orbit-core"><Braces /><strong>dados<br />brutos</strong></div>
        </div>
        <div className="hero-foot"><span>Distribuidora Vetor · Brasília/DF</span><span>Role para acompanhar o dado ↓</span></div>
      </section>

      <Pipeline />
      <Decision />

      <section id="prova" className="chapter proof-section">
        <div className="proof-number reveal"><span><CountUp value={metrics.auditorias} /></span><div><div className="eyebrow"><span>04</span> A prova</div><h2>mudanças.<br />Nenhuma<br /><em>no escuro.</em></h2></div></div>
        <div className="proof-grid reveal">
          <div className="chart-card"><div><small>AUDITORIA POR CAMPO</small><p>Cada coluna conta onde a base precisou de cuidado.</p></div><ResponsiveContainer width="100%" height={290}><BarChart data={fieldData}><CartesianGrid strokeDasharray="2 8" vertical={false} stroke="#9CAF8855" /><XAxis dataKey="campo" tickLine={false} axisLine={false} /><YAxis hide /><Tooltip cursor={{ fill: '#F4EEDC' }} /><Bar dataKey="total" radius={[14, 14, 0, 0]}>{fieldData.map((_, index) => <Cell key={index} fill={index === 0 ? '#F06445' : '#294A32'} />)}</Bar></BarChart></ResponsiveContainer></div>
          <TiltCard className="missing-case"><span>CLI0047</span><h3>E quando não existe resposta?</h3><div className="empty-data">CEP <i>vazio</i><br />BAIRRO <i>vazio</i></div><ArrowDown /><strong>Não Informado</strong><p>O pipeline preserva a incerteza. Ele não inventa um endereço para preencher uma lacuna.</p></TiltCard>
        </div>
      </section>

      <section id="resultado" className="chapter result-section cream-section">
        <header className="section-heading reveal"><div className="eyebrow"><span>05</span> O resultado</div><h2>Agora a base<br /><em>fala uma só língua.</em></h2></header>
        <div className="metric-grid reveal">
          {[['clientes', metrics.clientes, 'clientes prontos'], ['vendedores', metrics.vendedores, 'vendedores relacionados'], ['auditorias', metrics.auditorias, 'transformações auditadas'], ['conflitos', metrics.conflitos, 'conflitos corrigidos']].map(([key, value, label]) => <TiltCard key={String(key)} className={`metric ${key}`}><small>{label}</small><strong><CountUp value={Number(value)} /></strong><span>0{['clientes','vendedores','auditorias','conflitos'].indexOf(String(key)) + 1}</span></TiltCard>)}
        </div>
        <div className="explorer reveal">
          <div className="neighborhood-chart"><header><div><small>DISTRIBUIÇÃO FINAL</small><h3>Clique em um bairro<br />para filtrar a base.</h3></div><button onClick={() => setNeighborhood('Todos')}>Limpar filtro</button></header><ResponsiveContainer width="100%" height={320}><BarChart layout="vertical" data={neighborhoods} margin={{ left: 12, right: 20 }}><XAxis type="number" hide /><YAxis width={110} type="category" dataKey="nome" tickLine={false} axisLine={false} /><Tooltip /><Bar dataKey="total" radius={[0, 12, 12, 0]} onClick={(_, index) => setNeighborhood(String(neighborhoods[index]?.nome || 'Todos'))}>{neighborhoods.map((item) => <Cell key={String(item.nome)} cursor="pointer" fill={neighborhood === item.nome ? '#F06445' : '#FFB31A'} />)}</Bar></BarChart></ResponsiveContainer></div>
          <div className="client-panel"><header><div><small>EXPLORADOR DE CLIENTES</small><strong>{neighborhood}</strong></div><label><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar cliente" /></label></header><div className="client-list">{clients.length ? clients.slice(0, 9).map((client: Client) => <article key={client.id_cliente}><span>{client.id_cliente}</span><div><strong>{client.razao_social}</strong><small>{client.bairro_normalizado} · {client.cidade}/{client.uf}</small></div><CircleDot /></article>) : <div className="empty-list">{data ? 'Nenhum cliente encontrado.' : 'Carregando base interativa…'}</div>}</div></div>
        </div>
      </section>

      <section id="sistema" className="chapter system-section dark-section">
        <header className="section-heading reveal"><div className="eyebrow"><span>06</span> O sistema vivo</div><h2>Um dado limpo<br /><em>precisa circular.</em></h2><p>Arraste, aproxime e explore a arquitetura ponta a ponta.</p></header>
        <Architecture />
        <ApiDemo />
      </section>

      <section id="confianca" className="chapter trust-section">
        <div className="trust-title reveal"><div className="eyebrow"><span>07</span> A confiança</div><h2>Não basta<br />funcionar.<br /><em>É preciso provar.</em></h2></div>
        <div className="test-equation reveal"><div><TestTube2 /><strong>7</strong><span>testes ETL</span></div><b>+</b><div><Server /><strong>8</strong><span>vendedores</span></div><b>+</b><div><Database /><strong>5</strong><span>clientes</span></div><b>=</b><div className="total"><ShieldCheck /><strong>20</strong><span>testes automatizados</span></div></div>
        <div className="finale reveal"><span>DESAFIO PRIMORA · DISTRIBUIDORA VETOR</span><h2>Dados limpos.<br /><em>Decisões confiáveis.</em><br />Sistema pronto<br />para evoluir.</h2><div className="final-links"><a href="https://github.com/dudsstar16/desafio-primora/actions" target="_blank" rel="noreferrer"><GitBranch />GitHub Actions<ExternalLink /></a><a href={`${import.meta.env.VITE_API_URL || ''}/api/swagger/`} target="_blank" rel="noreferrer"><Braces />Swagger<ExternalLink /></a><a href={`${import.meta.env.VITE_API_URL || ''}/api/docs/`} target="_blank" rel="noreferrer"><Layers3 />Redoc<ExternalLink /></a></div></div>
        <footer><div><Sparkles />PRIMORA</div><p>Hefestos27 · alderiana · Eduarda Reis</p><button onClick={() => goTo('caos')}>Recomeçar a história ↑</button></footer>
      </section>
    </main>
  </div>
}

export default App
