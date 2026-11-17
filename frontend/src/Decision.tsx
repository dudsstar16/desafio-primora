import { useEffect, useState } from 'react'
import './pipeline-details.css'

const cases = [
  { id: 'CLI0002', before: 'Sul (Aguas Claras)', text: 'Águas Claras', cep: '72140-010', digits: '72140010', reference: 'Taguatinga Norte (Taguatinga)', place: 'QNM 32', audit: 7 },
  { id: 'CLI0017', before: 'Vte Pires', text: 'Vicente Pires', cep: '72110-800', digits: '72110800', reference: 'Taguatinga Norte (Taguatinga)', place: 'Área Especial', audit: 64 },
  { id: 'CLI0033', before: 'Vicente Pires - DF', text: 'Vicente Pires', cep: '72110-800', digits: '72110800', reference: 'Taguatinga Norte (Taguatinga)', place: 'Área Especial', audit: 132 },
]

export default function Decision() {
  const [selected, setSelected] = useState(0)
  const [open, setOpen] = useState(false)
  const item = cases[selected]
  useEffect(() => { function handle(event: KeyboardEvent) { if (event.key === 'Escape') setOpen(false) } window.addEventListener('keydown', handle); return () => window.removeEventListener('keydown', handle) }, [])
  return <section id="decisao" className="chapter decision-section dark-section">
    <header className="section-heading"><div className="eyebrow"><span>03</span> A decisão</div><h2>Quando o CEP<br /><em>contradiz o texto.</em></h2><p>Compare o cadastro com a referência e acompanhe a regra aplicada.</p></header>
    <div className="case-tabs" aria-label="Escolha um caso">{cases.map((entry, index) => <button key={entry.id} className={index === selected ? 'active' : ''} aria-pressed={index === selected} onClick={() => { setSelected(index); setOpen(false) }}>{entry.id}</button>)}</div>
    <div className="decision-flow" key={item.id}>
      <article className="decision-block decision-input"><small>01 · Entrada original</small><h3>Bairro informado</h3><strong>{item.before}</strong><p>CEP do cadastro: <b>{item.cep}</b></p></article>
      <article className="decision-block decision-rule"><small>02 · Regra aplicada</small><h3>Referência de CEP</h3><strong>{item.reference}</strong><p>{item.place}. O texto sugere {item.text}; a referência aponta para Taguatinga. Neste conflito, a referência prevalece.</p></article>
      <article className="decision-block decision-result"><small>03 · Resultado tratado</small><h3>Bairro canônico</h3><strong>Taguatinga</strong><p>CEP normalizado: <b>{item.digits}</b></p><p>Regra registrada: <b>GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO</b></p></article>
    </div>
    <div className="decision-foot"><p>Resultado já processado com referência de CEP preservada no cache. Esta tela não consulta o serviço de CEP.</p><button className="detail-toggle" aria-expanded={open} onClick={() => setOpen(!open)}>{open ? 'Fechar decisão' : 'Entender a decisão'} <span aria-hidden="true">{open ? '−' : '+'}</span></button></div>
    {open && <div className="decision-explanation"><h3>Da entrada à decisão</h3><ol><li>Normalizar o texto: “{item.before}” sugere {item.text}.</li><li>Consultar a referência disponível para {item.cep}: {item.reference}.</li><li>Comparar os bairros canônicos; no conflito, a referência de CEP prevalece.</li><li>Registrar a decisão na auditoria.</li></ol><p><b>Módulo:</b> etl/transform_address.py · <b>Auditoria selecionada:</b> registro {item.audit}, campo bairro, “{item.before}” → “Taguatinga”, regra GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO. A referência pode estar incompleta ou desatualizada.</p></div>}
  </section>
}
