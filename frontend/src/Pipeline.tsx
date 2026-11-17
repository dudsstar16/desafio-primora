import { useState } from 'react'
import './pipeline-details.css'

const stages = [
  { name: 'CSV bruto', file: 'data/raw/02-clientes_distribuidora_vetor.csv', receives: '47 cadastros originais', delivers: 'Uma fonte preservada para reprocessamento', rule: 'Grafias, máscaras e datas são mantidas na origem; o arquivo original não é alterado.', examples: ['Sul (Aguas Claras) · 72140-010'] },
  { name: 'Extração', file: 'etl/extract.py', receives: 'CSV com campos em formatos variados', delivers: 'Registros lidos como texto', rule: 'Ler identificadores como texto preserva zeros significativos e evita interpretações numéricas.', examples: ['03.447.134/9361-83 permanece texto'] },
  { name: 'Normalização', file: 'etl/transform_fields.py', receives: 'CNPJ, telefone e data originais', delivers: 'Campos padronizados para consulta', rule: 'Remove máscaras e converte datas reconhecidas para o formato ISO.', examples: ['28.327.648/3503-05 → 28327648350305', '+55 61 95386-2084 → 61953862084', 'Feb 28, 2023 → 2023-02-28'] },
  { name: 'CEP + cache', file: 'etl/cep_service.py', receives: 'CEP informado no cadastro', delivers: 'CEP normalizado e referência geográfica quando disponível', rule: 'Remove máscara e descarta padrões inválidos; procura primeiro no cache e, quando necessário, consulta ViaCEP e depois BrasilAPI. Uma referência indisponível limita a confirmação.', examples: ['72140-010 → 72140010', 'Cache: Taguatinga Norte (Taguatinga)'] },
  { name: 'Guardrail', file: 'etl/transform_address.py', receives: 'Bairro informado e referência de CEP', delivers: 'Bairro canônico e regra aplicada', rule: 'Com referência de CEP utilizável, ela prevalece no conflito. Sem ela, usa o texto reconhecido; sem informação, marca Não Informado.', examples: ['Sul (Aguas Claras) + 72140-010 → Taguatinga'] },
  { name: 'Auditoria', file: 'etl/audit.py', receives: 'Original, valor tratado e regra', delivers: 'Registro rastreável de tratamento', rule: 'A auditoria acompanha as transformações; esta estação é uma representação didática.', examples: ['CLI0002 · bairro · Sul (Aguas Claras) → Taguatinga · GUARDRAIL_CONFLITO_CEP_VENCEU_TEXTO'] },
  { name: 'Carga + integração', file: 'etl/load.py · api/clientes/management', receives: 'Clientes, vendedores e auditoria tratados', delivers: 'CSVs, SQLite e artefatos PostgreSQL', rule: 'O pipeline produz artefatos locais. No Render, uma carga idempotente inicializa o PostgreSQL vazio.', examples: ['5 vendedores · 47 clientes · 188 registros de auditoria'] },
]

export default function Pipeline() {
  const [selected, setSelected] = useState(0)
  const [expanded, setExpanded] = useState(false)
  const [guided, setGuided] = useState(false)
  const stage = stages[selected]
  function select(index: number) { setSelected(index); setExpanded(false) }
  return <section id="caminho" className="chapter cream-section pipeline-section">
    <header className="section-heading"><div className="eyebrow"><span>02</span> O caminho</div><h2>O dado não é limpo.<br /><em>Ele atravessa decisões.</em></h2><p>Clique em cada estação para entender o que acontece — e por quê.</p></header>
    <div className="pipeline-layout">
      <div className="pipeline-track" aria-label="Etapas do pipeline ETL">{stages.map((item, index) => <button key={item.name} className={`pipeline-step ${selected === index ? 'active' : ''}`} aria-pressed={selected === index} onClick={() => select(index)}><span>{String(index + 1).padStart(2, '0')}</span><i /><strong>{item.name}</strong></button>)}</div>
      <div className="step-detail pipeline-detail"><small>{stage.file}</small><h3>{stage.name}</h3><p>{stage.rule}</p><div className="pipeline-io"><p><b>Recebe</b> {stage.receives}</p><p><b>Entrega</b> {stage.delivers}</p></div><button className="detail-toggle" aria-expanded={expanded} onClick={() => setExpanded(!expanded)}>{expanded ? 'Fechar detalhes' : 'Explorar detalhes'} <span aria-hidden="true">{expanded ? '−' : '+'}</span></button>{expanded && <div className="pipeline-expanded"><strong>Exemplos e evidências</strong>{stage.examples.map(example => <p key={example}>{example}</p>)}</div>}</div>
    </div>
    <div className="guided-record"><button className="detail-toggle" aria-expanded={guided} onClick={() => { setGuided(!guided); if (!guided) select(0) }}>{guided ? 'Fechar acompanhamento' : 'Acompanhar um cadastro · CLI0002'}</button>{guided && <div className="guided-content"><p>Passo {selected + 1} de 7: <strong>{stage.name}</strong>. Este percurso mostra dados já processados; não executa o ETL.</p><p>{stage.examples[0]}</p><div><button disabled={selected === 0} onClick={() => select(selected - 1)}>Anterior</button><button disabled={selected === stages.length - 1} onClick={() => select(selected + 1)}>Próxima etapa →</button></div></div>}</div>
  </section>
}
