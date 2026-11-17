import { useEffect, useRef, useState } from 'react'
import saved from '../public/snapshot.json'
import './architecture.css'

const offline = import.meta.env.VITE_OFFLINE_DEMO === 'true'
const base = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const routes = [
  { id:'metrics', label:'Métricas da apresentação', path:'/api/apresentacao/metricas/' },
  { id:'clients', label:'Clientes de Águas Claras', path:'/api/clientes/bairro/aguas%20claras/' },
  { id:'sellers', label:'Vendedores', path:'/api/vendedores/' },
] as const
type Route = typeof routes[number]['id']
type Result = { kind:'live'|'saved'; value:unknown; time:string; status?:number }
const example = (id:Route) => id==='clients' ? saved.clients.filter(c=>c.bairro_normalizado==='Águas Claras') : id==='sellers' ? saved.sellers : { aviso:'Exemplo de snapshot; campos locais podem diferir do formato da API.', totais:saved.metrics }

export default function ApiDemo() {
  const [selected,setSelected]=useState<Route>('metrics')
  const [result,setResult]=useState<Result|null>(null)
  const [error,setError]=useState('')
  const [loading,setLoading]=useState(false)
  const controller=useRef<AbortController|null>(null)
  useEffect(()=>()=>controller.current?.abort(),[])
  const route=routes.find(r=>r.id===selected)!
  const choose=(value:Route)=>{controller.current?.abort();controller.current=null;setLoading(false);setError('');setResult(null);setSelected(value)}
  const savedExample=()=>{setError('');setResult({kind:'saved',value:example(selected),time:new Date().toLocaleTimeString('pt-BR')})}
  async function run() {
    const abort = new AbortController(); controller.current=abort; setError('');setResult(null);setLoading(true)
    const timer=window.setTimeout(()=>abort.abort(),2500)
    try {
      const response=await fetch(`${base}${route.path}`,{signal:abort.signal,headers:{Accept:'application/json'}})
      if(!response.ok) throw new Error(`HTTP ${response.status}`)
      const value:unknown=await response.json()
      if(controller.current===abort) setResult({kind:'live',status:response.status,value,time:new Date().toLocaleTimeString('pt-BR')})
    } catch(e) {
      if(controller.current===abort) setError(e instanceof Error && e.name==='AbortError' ? 'Tempo de espera esgotado. A API pode estar despertando.' : `Não foi possível consultar a API${e instanceof Error ? `: ${e.message}` : '.'}`)
    } finally { window.clearTimeout(timer); if(controller.current===abort){controller.current=null;setLoading(false)} }
  }
  return <div className="api-lab"><div className="api-copy"><span>GET · SOMENTE LEITURA</span><h3>A API responde.<br/>A interface traduz.</h3><p>Escolha uma consulta. A resposta ao vivo vem diretamente da API; o exemplo salvo usa o snapshot da apresentação.</p><label htmlFor="api-route">Consulta</label><select id="api-route" value={selected} onChange={e=>choose(e.target.value as Route)}>{routes.map(r=><option key={r.id} value={r.id}>{r.label}</option>)}</select><button onClick={offline?savedExample:run} disabled={loading}>{loading?'Consultando…':offline?'Mostrar exemplo salvo':'Consultar API'} →</button>{error && <div className="api-error" role="alert"><p>{error}</p><button onClick={savedExample}>Ver exemplo salvo</button></div>}</div><div className="api-terminal"><header><span>GET {route.path}</span></header><div className="api-meta" aria-live="polite">{loading?'Consultando a API…': result ? `${result.kind==='live'?'RESPOSTA AO VIVO':'EXEMPLO SALVO · SNAPSHOT'}${result.status?` · HTTP ${result.status}`:''} · ${result.time}` : offline?'MODO OFFLINE · escolha uma consulta':'Aguardando consulta'} </div><pre>{result?JSON.stringify(result.value,null,2):'// A resposta aparecerá aqui.'}</pre></div></div>
}
