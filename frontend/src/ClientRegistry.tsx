import { useMemo, useState } from 'react'
import { listAccounts, listClients, type Account, type Client } from './api/client'
import { useFetch } from './api/useFetch'

/**
 * T28 - Registre clients : liste + fiche detail en disposition maitre-detail,
 * coherente avec le rail de navigation pose en T25 (contenu dans la meme
 * zone de section, sans modal ni nouveau paradigme d'ecran).
 */

type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH'

function riskLevel(score: number): RiskLevel {
  if (score >= 70) return 'HIGH'
  if (score >= 31) return 'MEDIUM'
  return 'LOW'
}

const riskMeta: Record<RiskLevel, { label: string; textColor: string }> = {
  LOW: { label: 'Faible', textColor: 'text-vert' },
  MEDIUM: { label: 'Moyen', textColor: 'text-ocre-texte' },
  HIGH: { label: 'Élevé', textColor: 'text-tampon' },
}

function RiskSeal({ score }: { score: number }) {
  const level = riskLevel(score)
  const meta = riskMeta[level]
  return (
    <span
      className={`inline-flex -rotate-2 items-center rounded-sm border-2 px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] ${meta.textColor}`}
      style={{ borderColor: 'currentcolor' }}
    >
      {meta.label}
    </span>
  )
}

function formatDate(value: string | null) {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('fr-FR')
}

export default function ClientRegistry() {
  const { data: clients, error, loading, reload } = useFetch<Client[]>(() => listClients())
  const [query, setQuery] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const filtered = useMemo(() => {
    if (!clients) return []
    const q = query.trim().toLowerCase()
    if (!q) return clients
    return clients.filter((c) => `${c.first_name} ${c.last_name}`.toLowerCase().includes(q))
  }, [clients, query])

  const selected = filtered.find((c) => c.id === selectedId) ?? filtered[0] ?? null

  const {
    data: accounts,
    loading: accountsLoading,
  } = useFetch<Account[]>(() => (selected ? listAccounts(selected.id) : Promise.resolve([])), [selected?.id])

  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">Registre clients</p>
      <h1 className="mt-2 text-3xl text-encre sm:text-4xl">Rechercher un dossier client</h1>

      <div className="mt-5">
        <label htmlFor="client-search" className="sr-only">
          Rechercher un client par nom
        </label>
        <input
          id="client-search"
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Nom ou prénom du client"
          className="w-full max-w-md rounded-sm border border-encre/20 bg-papier px-3 py-2.5 font-mono text-sm text-encre placeholder:text-graphite/35 focus:border-encre focus:outline-none focus:ring-1 focus:ring-encre"
        />
      </div>

      {loading && <p className="mt-6 text-sm text-graphite/60">Chargement du registre…</p>}

      {error && (
        <div className="mt-6 rounded-sm border border-tampon/40 bg-tampon/5 p-4">
          <p className="text-sm text-tampon">Le registre est indisponible : {error}</p>
          <button
            type="button"
            onClick={reload}
            className="mt-2 font-mono text-[10px] uppercase tracking-[0.16em] text-tampon underline underline-offset-4"
          >
            Réessayer
          </button>
        </div>
      )}

      {!loading && !error && (
        <div className="mt-6 grid gap-4 lg:grid-cols-[minmax(0,20rem)_1fr]">
          <div className="divide-y divide-encre/10 rounded-sm border border-encre/12 bg-papier">
            {filtered.length === 0 && (
              <p className="px-4 py-6 text-sm text-graphite/55">Aucun client ne correspond à cette recherche.</p>
            )}
            {filtered.map((client) => (
              <button
                key={client.id}
                type="button"
                onClick={() => setSelectedId(client.id)}
                className={`flex w-full items-center justify-between gap-2 px-4 py-3 text-left transition-colors ${
                  selected?.id === client.id ? 'bg-papier-soutenu/60' : 'hover:bg-papier-soutenu/30'
                }`}
              >
                <span>
                  <span className="block text-sm font-semibold text-encre">
                    {client.first_name} {client.last_name}
                  </span>
                  <span className="font-mono text-[10px] text-graphite/50">Dossier #{client.id}</span>
                </span>
                <RiskSeal score={client.risk_score} />
              </button>
            ))}
          </div>

          <div className="rounded-sm border border-encre/12 bg-papier-soutenu/40 p-5 sm:p-6">
            {!selected ? (
              <p className="text-sm text-graphite/55">Sélectionnez un client dans la liste pour ouvrir sa fiche.</p>
            ) : (
              <div>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-graphite/50">
                      Dossier #{selected.id}
                    </p>
                    <h2 className="mt-1 text-2xl text-encre">
                      {selected.first_name} {selected.last_name}
                    </h2>
                  </div>
                  <RiskSeal score={selected.risk_score} />
                </div>

                {(selected.is_pep || selected.is_sanctioned) && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selected.is_pep && (
                      <span className="rounded-sm border-2 border-ocre-texte px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-ocre-texte">
                        Fonction politique déclarée
                      </span>
                    )}
                    {selected.is_sanctioned && (
                      <span className="rounded-sm border-2 border-tampon px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-tampon">
                        Sanction identifiée
                      </span>
                    )}
                  </div>
                )}

                <dl className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div>
                    <dt className="font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">Nationalité</dt>
                    <dd className="mt-1 text-sm text-graphite/80">{selected.nationality ?? '—'}</dd>
                  </div>
                  <div>
                    <dt className="font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">Date de naissance</dt>
                    <dd className="mt-1 font-mono text-sm text-graphite/80">{formatDate(selected.birth_date)}</dd>
                  </div>
                  <div>
                    <dt className="font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">E-mail</dt>
                    <dd className="mt-1 text-sm text-graphite/80">{selected.email ?? '—'}</dd>
                  </div>
                  <div>
                    <dt className="font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">Score de risque</dt>
                    <dd className="mt-1 font-mono text-sm text-graphite/80">{selected.risk_score.toFixed(0)} / 100</dd>
                  </div>
                </dl>

                <div className="mt-6 border-t border-encre/10 pt-4">
                  <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">Comptes</p>
                  {accountsLoading ? (
                    <p className="mt-2 text-sm text-graphite/55">Chargement des comptes…</p>
                  ) : accounts && accounts.length > 0 ? (
                    <ul className="mt-2 divide-y divide-encre/10">
                      {accounts.map((acc) => (
                        <li key={acc.id} className="flex items-center justify-between py-2 text-sm">
                          <span className="font-mono text-graphite/70">{acc.account_number}</span>
                          <span className="font-mono text-graphite/80">
                            {acc.balance} {acc.currency}
                          </span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-sm text-graphite/55">Aucun compte enregistré pour ce client.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
