import { useState, type FormEvent } from 'react'
import { createClient } from './api/client'
import { FieldError, FieldLabel, FormActions, PrimaryButton, SecondaryButton } from './components/form'
import { inputClasses } from './components/formStyles'

type FormState = {
  firstName: string
  lastName: string
  birthDate: string
  nationality: string
  email: string
  isPep: 'oui' | 'non' | ''
  contexte: string
}

const emptyForm: FormState = {
  firstName: '',
  lastName: '',
  birthDate: '',
  nationality: '',
  email: '',
  isPep: '',
  contexte: '',
}

const requiredFields: Array<keyof FormState> = ['firstName', 'lastName', 'birthDate', 'nationality', 'isPep']

const fieldLabels: Record<keyof FormState, string> = {
  firstName: 'Prénom',
  lastName: 'Nom',
  birthDate: 'Date de naissance',
  nationality: 'Nationalité',
  email: 'Adresse e-mail',
  isPep: 'Fonction politique',
  contexte: 'Éléments de contexte',
}

export default function ClientOnboardingForm() {
  const [form, setForm] = useState<FormState>(emptyForm)
  const [touchedSubmit, setTouchedSubmit] = useState(false)
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const missing = requiredFields.filter((field) => !form[field])

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
      await createClient({
        first_name: form.firstName,
        last_name: form.lastName,
        birth_date: form.birthDate || null,
        nationality: form.nationality || null,
        email: form.email || null,
        is_pep: form.isPep === 'oui',
      })
      setStatus('saved')
      setForm(emptyForm)
      setTouchedSubmit(false)
    } catch (err) {
      setStatus('error')
      setErrorMessage(err instanceof Error ? err.message : 'Erreur inattendue.')
    }
  }

  const handleReset = () => {
    setForm(emptyForm)
    setTouchedSubmit(false)
    setStatus('idle')
  }

  return (
    <div className="mx-auto max-w-3xl">
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">Agent terrain</p>
      <h1 className="mt-2 text-3xl text-encre sm:text-4xl">Ouvrir un dossier client</h1>
      <p className="mt-2 max-w-xl text-sm leading-6 text-graphite/70">
        Vous renseignez ce que le client vous déclare aujourd’hui. Le dossier reste modifiable tant que vous ne l’avez pas enregistré.
      </p>

      <form onSubmit={handleSubmit} noValidate className="mt-7 space-y-7">
        <fieldset className="grid gap-4 sm:grid-cols-2">
          <legend className="sr-only">Identité du client</legend>

          <div>
            <FieldLabel htmlFor="firstName">{fieldLabels.firstName}</FieldLabel>
            <input
              id="firstName"
              type="text"
              autoComplete="given-name"
              value={form.firstName}
              onChange={(event) => update('firstName', event.target.value)}
              className={inputClasses(touchedSubmit && !form.firstName)}
            />
            <FieldError show={touchedSubmit && !form.firstName} />
          </div>

          <div>
            <FieldLabel htmlFor="lastName">{fieldLabels.lastName}</FieldLabel>
            <input
              id="lastName"
              type="text"
              autoComplete="family-name"
              value={form.lastName}
              onChange={(event) => update('lastName', event.target.value)}
              className={inputClasses(touchedSubmit && !form.lastName)}
            />
            <FieldError show={touchedSubmit && !form.lastName} />
          </div>

          <div>
            <FieldLabel htmlFor="birthDate">{fieldLabels.birthDate}</FieldLabel>
            <input
              id="birthDate"
              type="date"
              value={form.birthDate}
              onChange={(event) => update('birthDate', event.target.value)}
              className={inputClasses(touchedSubmit && !form.birthDate)}
            />
            <FieldError show={touchedSubmit && !form.birthDate} />
          </div>

          <div>
            <FieldLabel htmlFor="nationality">{fieldLabels.nationality}</FieldLabel>
            <input
              id="nationality"
              type="text"
              placeholder="Béninoise"
              autoComplete="off"
              value={form.nationality}
              onChange={(event) => update('nationality', event.target.value)}
              className={inputClasses(touchedSubmit && !form.nationality)}
            />
            <FieldError show={touchedSubmit && !form.nationality} />
          </div>

          <div className="sm:col-span-2">
            <FieldLabel htmlFor="email" hint="si le client en a une">
              {fieldLabels.email}
            </FieldLabel>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={(event) => update('email', event.target.value)}
              className={inputClasses(false)}
            />
          </div>
        </fieldset>

        <fieldset>
          <legend className="block text-sm font-medium text-graphite/85">
            Le client exerce une fonction publique importante, ou est proche de quelqu’un qui en exerce une
          </legend>
          <p className="mt-1 text-xs leading-5 text-graphite/55">
            Demandez-le directement au client. Une réponse « oui » n’empêche pas le dossier d’avancer, elle change juste le niveau de vérification.
          </p>
          <div className="mt-3 flex gap-2">
            {(['non', 'oui'] as const).map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => update('isPep', value)}
                className={`rounded-sm border px-4 py-2 font-mono text-xs uppercase tracking-[0.14em] transition-colors ${
                  form.isPep === value
                    ? 'border-encre bg-encre text-papier'
                    : `border-encre/20 text-graphite/70 hover:border-encre/40 ${touchedSubmit && !form.isPep ? 'border-tampon' : ''}`
                }`}
              >
                {value === 'oui' ? 'Oui' : 'Non'}
              </button>
            ))}
          </div>
          <FieldError show={touchedSubmit && !form.isPep} />
        </fieldset>

        <div>
          <FieldLabel htmlFor="contexte" hint="facultatif">
            {fieldLabels.contexte}
          </FieldLabel>
          <p className="mt-1 text-xs leading-5 text-graphite/55">
            Ce que vous savez déjà sur ce client et qui peut aider une décision plus tard.
          </p>
          <textarea
            id="contexte"
            rows={4}
            value={form.contexte}
            onChange={(event) => update('contexte', event.target.value)}
            className={`${inputClasses(false)} resize-none`}
          />
        </div>

        <FormActions>
          <PrimaryButton type="submit" disabled={status === 'saving'}>
            {status === 'saving' ? 'Enregistrement…' : 'Enregistrer le dossier'}
          </PrimaryButton>
          <SecondaryButton type="button" onClick={handleReset}>
            Annuler
          </SecondaryButton>

          {touchedSubmit && missing.length > 0 && (
            <p className="font-mono text-[10px] text-tampon">
              {missing.length} champ{missing.length > 1 ? 's' : ''} manque{missing.length > 1 ? 'nt' : ''} encore.
            </p>
          )}
          {status === 'saved' && (
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-vert">Dossier enregistré.</p>
          )}
          {status === 'error' && errorMessage && (
            <p className="font-mono text-[10px] text-tampon">Échec : {errorMessage}</p>
          )}
        </FormActions>
      </form>
    </div>
  )
}
