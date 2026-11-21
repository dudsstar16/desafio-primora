import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from 'react'
import { X } from 'lucide-react'
import type { Seller } from '../types'
import { ApiError, errorMessage, type Customer } from './api'

export function Dialog({ title, close, children, busy = false }: {
  title: string; close: () => void; children: ReactNode; busy?: boolean
}) {
  const ref = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  useEffect(() => {
    const dialog = ref.current
    dialog?.showModal()
    return () => dialog?.close()
  }, [])

  return <dialog ref={ref} className="vetor-dialog" aria-labelledby={titleId} onCancel={event => {
    event.preventDefault()
    if (!busy) close()
  }}>
    <header className="vetor-dialog-header">
      <h2 id={titleId}>{title}</h2>
      <button type="button" className="vetor-icon-button" aria-label="Fechar" disabled={busy} onClick={close}><X size={20} /></button>
    </header>
    {children}
  </dialog>
}

export type EditTarget =
  | { kind: 'customer'; record?: Customer }
  | { kind: 'seller'; record?: Seller }
export type RecordBody = Customer | Pick<Seller, 'nome_vendedor'>

const customerFields = [
  { name: 'id_cliente', label: 'ID do cliente', maxLength: 20 },
  { name: 'razao_social', label: 'Razão social', maxLength: 150 },
  { name: 'cnpj_normalizado', label: 'CNPJ', maxLength: 14, numeric: true },
  { name: 'telefone_normalizado', label: 'Telefone', maxLength: 11, numeric: true },
  { name: 'email', label: 'E-mail', maxLength: 150, inputMode: 'email' },
  { name: 'bairro_normalizado', label: 'Bairro', maxLength: 100 },
  { name: 'cep_normalizado', label: 'CEP (opcional)', maxLength: 8, numeric: true, optional: true },
  { name: 'cidade', label: 'Cidade', maxLength: 50 },
  { name: 'uf', label: 'UF', maxLength: 2 },
  { name: 'data_cadastro_normalizado', label: 'Data de cadastro', type: 'date' },
] as const satisfies ReadonlyArray<{
  name: keyof Customer; label: string; maxLength?: number; type?: string; inputMode?: 'email'; numeric?: boolean; optional?: boolean
}>

type CustomerField = {
  name: typeof customerFields[number]['name']; label: string; maxLength?: number
  type?: string; inputMode?: 'email'; numeric?: boolean; optional?: boolean
}

export function Editor({ target, sellers, close, save }: {
  target: EditTarget; sellers: Seller[]; close: () => void; save: (body: RecordBody) => Promise<void>
}) {
  const [busy, setBusy] = useState(false)
  const [failure, setFailure] = useState<unknown>(null)
  const sellerLabelId = useId()
  const fields = failure instanceof ApiError ? failure.fields : {}
  const customer = target.kind === 'customer' ? target.record : undefined
  const seller = target.kind === 'seller' ? target.record : undefined
  const title = target.kind === 'customer'
    ? (customer ? 'Editar cliente' : 'Novo cliente')
    : (seller ? 'Editar vendedor' : 'Novo vendedor')
  const fieldError = (name: string) => fields[name]
    ? <small id={`error-${name}`} className="vetor-field-error">{fields[name]}</small>
    : null
  const validation = (name: string) => ({
    'aria-invalid': Boolean(fields[name]),
    'aria-describedby': fields[name] ? `error-${name}` : undefined,
  })

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) return
    const data = new FormData(event.currentTarget)
    const read = (name: string) => String(data.get(name) ?? '').trim()
    setBusy(true)
    setFailure(null)
    try {
      if (target.kind === 'seller') {
        await save({ nome_vendedor: read('nome_vendedor') })
      } else {
        await save({
          id_cliente: read('id_cliente'),
          razao_social: read('razao_social'),
          cnpj_normalizado: read('cnpj_normalizado'),
          telefone_normalizado: read('telefone_normalizado'),
          email: read('email'),
          bairro_normalizado: read('bairro_normalizado'),
          cep_normalizado: read('cep_normalizado') || null,
          cidade: read('cidade'),
          uf: read('uf').toUpperCase(),
          data_cadastro_normalizado: read('data_cadastro_normalizado'),
          vendedor_id: Number(read('vendedor_id')),
        })
      }
    } catch (error) {
      setFailure(error)
    } finally {
      setBusy(false)
    }
  }

  return <Dialog title={title} close={close} busy={busy}>
    <form onSubmit={submit}>
      <fieldset className="vetor-form-grid" disabled={busy}>
        {target.kind === 'seller'
          ? <label className="vetor-span">Nome do vendedor
            <input name="nome_vendedor" defaultValue={seller?.nome_vendedor} maxLength={100} required {...validation('nome_vendedor')} />
            {fieldError('nome_vendedor')}
          </label>
          : <>
            {customerFields.map((field: CustomerField) => <label key={field.name}>{field.label}
              <input name={field.name} defaultValue={customer?.[field.name] ?? ''} type={field.type ?? 'text'}
                inputMode={field.numeric ? 'numeric' : field.inputMode} maxLength={field.maxLength}
                pattern={field.numeric ? '[0-9]+' : undefined}
                readOnly={field.name === 'id_cliente' && Boolean(customer)}
                required={!field.optional} {...validation(field.name)} />
              {fieldError(field.name)}
            </label>)}
            <label className="vetor-span"><span id={sellerLabelId}>Vendedor</span>
              <select name="vendedor_id" aria-labelledby={sellerLabelId} defaultValue={customer?.vendedor_id ?? ''} required {...validation('vendedor_id')}>
                <option value="">Selecione</option>
                {sellers.map(item => <option key={item.id_vendedor} value={item.id_vendedor}>{item.nome_vendedor}</option>)}
              </select>
              {fieldError('vendedor_id')}
            </label>
          </>}
      </fieldset>
      {Boolean(failure) && <p role="alert" className="vetor-error">
        {fields.non_field_errors || (Object.keys(fields).length ? 'Revise os campos indicados.' : errorMessage(failure))}
      </p>}
      <footer className="vetor-dialog-actions">
        <button type="button" className="vetor-button" onClick={close} disabled={busy}>Cancelar</button>
        <button className="vetor-button vetor-primary" disabled={busy}>{busy ? 'Salvando…' : 'Salvar cadastro'}</button>
      </footer>
    </form>
  </Dialog>
}

export function ConfirmDelete({ name, close, remove }: {
  name: string; close: () => void; remove: () => Promise<void>
}) {
  const [busy, setBusy] = useState(false)
  const [failure, setFailure] = useState('')
  async function confirm() {
    setBusy(true)
    setFailure('')
    try {
      await remove()
    } catch (error) {
      setFailure(errorMessage(error))
    } finally {
      setBusy(false)
    }
  }
  return <Dialog title="Excluir cadastro" close={close} busy={busy}>
    <p>Deseja excluir <strong>{name}</strong>? A exclusão é permanente.</p>
    {failure && <p className="vetor-error" role="alert">{failure}</p>}
    <footer className="vetor-dialog-actions">
      <button className="vetor-button" onClick={close} disabled={busy}>Cancelar</button>
      <button className="vetor-button vetor-danger" onClick={confirm} disabled={busy}>{busy ? 'Excluindo…' : 'Excluir cadastro'}</button>
    </footer>
  </Dialog>
}

export function Login({ close, login }: {
  close: () => void; login: (username: string, password: string) => Promise<void>
}) {
  const [busy, setBusy] = useState(false)
  const [failure, setFailure] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy) return
    const data = new FormData(event.currentTarget)
    setBusy(true)
    setFailure('')
    try {
      await login(String(data.get('username')).trim(), String(data.get('password')))
    } catch (error) {
      setFailure(error instanceof ApiError
        ? error.fields.non_field_errors || errorMessage(error)
        : errorMessage(error))
    } finally {
      setBusy(false)
    }
  }

  return <Dialog title="Entrar no painel" close={close} busy={busy}>
    <form onSubmit={submit}>
      <fieldset className="vetor-form-grid" disabled={busy}>
        <label className="vetor-span">Usuário<input name="username" autoComplete="username" required /></label>
        <label className="vetor-span">Senha<input type="password" name="password" autoComplete="current-password" required /></label>
      </fieldset>
      {failure && <p className="vetor-error" role="alert">{failure}</p>}
      <footer className="vetor-dialog-actions">
        <button type="button" className="vetor-button" onClick={close} disabled={busy}>Cancelar</button>
        <button className="vetor-button vetor-primary" disabled={busy}>{busy ? 'Entrando…' : 'Entrar'}</button>
      </footer>
    </form>
  </Dialog>
}
