import { useState, type FormEvent } from 'react'
import { createTransaction, listAccounts, type Account, type TransactionType } from './api/client'
import { useFetch } from './api/useFetch'
import { FieldError, FieldLabel, FormActions, PrimaryButton, SecondaryButton } from './components/form'
import { inputClasses } from './components/formStyles'

/**
 * T29 - Formulaire transaction. Meme systeme de composants que T27
 * (fieldset, FieldLabel, FieldError, inputClasses, boutons partages) :
 * aucune reinvention de style.
 */

type FormState = {
  accountId: string
  amount: string
  currency: string
  transactionType: TransactionType
  counterpartyName: string
  counterpartyCountry: string
}

const emptyForm: FormState = {
  accountId: '',
  amount: '',
  currency: 'XOF',
  transactionType: 'transfer',
  counterpartyName: '',
  counterpartyCountry: '',
}

const typeLabels: Record<TransactionType, string> = {
  deposit: 'Dépôt',
  withdrawal: 'Retrait',
  transfer: 'Virement',
  credit: 'Crédit',
  debit: 'Débit',
}

export default function TransactionForm() {
  const { data: accounts } = useFetch<Account[]>(() => listAccounts())
  const [form, setForm] = useState<FormState>(emptyForm)
  const [touchedSubmit, setTouchedSubmit] = useState(false)
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const missing: string[] = []
  if (!form.accountId) missing.push('accountId')
  if (!form.amount || Number(form.amount) <= 0) missing.push('amount')

  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setStatus('idle')
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setTouchedSubmit(true)
    if (missing.length > 0) return

    setStatus('saving')
    setErrorMessage(null)
    try {
      await createTransaction({
        account_id: Number(form.accountId),
        amount: Number(form.amount),
        currency: form.currency,
        transaction_type: form.transactionType,
        counterparty_name: form.counterpartyName || null,
        counterparty_country: form.counterpartyCountry || null,
      })
      setStatus('saved')
      setForm({ ...emptyForm, accountId: form.accountId, currency: form.currency })
      setTouchedSubmit(false)
    } catch (err) {
      setStatus('error')
      setErrorMessage(err instanceof Error ? err.message : 'Erreur inattendue.')
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">Agent terrain</p>
      <h1 className="mt-2 text-3xl text-encre sm:text-4xl">Enregistrer un mouvement</h1>
      <p className="mt-2 max-w-xl text-sm leading-6 text-graphite/70">
        Renseignez le mouvement tel que le client vous le declare. Le compte doit deja exister dans le registre.
      </p>

      <form onSubmit={handleSubmit} noValidate className="mt-7 space-y-7">
        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="sr-only">Compte et montant</legend>

          <div>
            <FieldLabel htmlFor="accountId">Compte du client</FieldLabel>
            <select
              id="accountId"
              value={form.accountId}
              onChange={(e) => update('accountId', e.target.value)}
              className={inputClasses(touchedSubmit && !form.accountId)}
            >
              <option value="">Sélectionner un compte</option>
              {accounts?.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.account_number} — client #{acc.client_id}
                </option>
              ))}
            </select>
            <FieldError show={touchedSubmit && !form.accountId} message="Choisissez le compte concerné." />
          </div>

          <div>
            <FieldLabel htmlFor="transactionType">Type de mouvement</FieldLabel>
            <select
              id="transactionType"
              value={form.transactionType}
              onChange={(e) => update('transactionType', e.target.value as TransactionType)}
              className={inputClasses(false)}
            >
              {(Object.keys(typeLabels) as TransactionType[]).map((type) => (
                <option key={type} value={type}>
                  {typeLabels[type]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <FieldLabel htmlFor="amount">Montant</FieldLabel>
            <input
              id="amount"
              type="number"
              min="0.01"
              step="0.01"
              value={form.amount}
              onChange={(e) => update('amount', e.target.value)}
              className={inputClasses(touchedSubmit && (!form.amount || Number(form.amount) <= 0))}
            />
            <FieldError
              show={touchedSubmit && (!form.amount || Number(form.amount) <= 0)}
              message="Indiquez un montant supérieur à zéro."
            />
          </div>

          <div>
            <FieldLabel htmlFor="currency">Devise</FieldLabel>
            <input
              id="currency"
              type="text"
              maxLength={3}
              value={form.currency}
              onChange={(e) => update('currency', e.target.value.toUpperCase())}
              className={inputClasses(false)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="counterpartyName" hint="facultatif">
              Nom de la contrepartie
            </FieldLabel>
            <input
              id="counterpartyName"
              type="text"
              value={form.counterpartyName}
              onChange={(e) => update('counterpartyName', e.target.value)}
              className={inputClasses(false)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="counterpartyCountry" hint="code pays, facultatif">
              Pays de la contrepartie
            </FieldLabel>
            <input
              id="counterpartyCountry"
              type="text"
              maxLength={2}
              placeholder="BJ"
              value={form.counterpartyCountry}
              onChange={(e) => update('counterpartyCountry', e.target.value.toUpperCase())}
              className={inputClasses(false)}
            />
          </div>
        </fieldset>

        <FormActions>
          <PrimaryButton type="submit" disabled={status === 'saving'}>
            {status === 'saving' ? 'Enregistrement…' : 'Enregistrer le mouvement'}
          </PrimaryButton>
          <SecondaryButton type="button" onClick={() => { setForm(emptyForm); setTouchedSubmit(false); setStatus('idle') }}>
            Annuler
          </SecondaryButton>

          {status === 'saved' && (
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-vert">Mouvement enregistré.</p>
          )}
          {status === 'error' && errorMessage && (
            <p className="font-mono text-[10px] text-tampon">Échec : {errorMessage}</p>
          )}
        </FormActions>
      </form>
    </div>
  )
}
