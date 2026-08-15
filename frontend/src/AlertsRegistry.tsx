import { useMemo, useState } from 'react'
import { listAlerts, reviewAlert, type Alert, type AlertStatus } from './api/client'
import { useFetch } from './api/useFetch'
import { PrimaryButton, SecondaryButton } from './components/form'

/**
 * T30 - Table des alertes avec filtres (police mono pour les donnees,
 * cf. tokens T24) et T31 - ecran de decision (Valider/Rejeter/Escalader).
 * Meme disposition maitre-detail que T28, pour rester coherent plutot
 * que d'inventer un 3e paradigme d'ecran.
 */

const statusLabels: Record<AlertStatus, string> = {
  OPEN: 'Ouverte',
  VALIDATED: 'Validée',
  REJECTED: 'Rejetée',
  ESCALATED: 'Escaladée',
}

const statusColor: Record<AlertStatus, string> = {
  OPEN: 'text-ocre-texte',
  VALIDATED: 'text-vert',
  REJECTED: 'text-graphite/60',
  ESCALATED: 'text-tampon',
}

const severityColor: Record<Alert['severity'], string> = {
  LOW: 'text-vert',
  MEDIUM: 'text-ocre-texte',
  HIGH: 'text-tampon',
  CRITICAL: 'text-tampon',
}

const decisionActions: Array<{ status: Exclude<AlertStatus, 'OPEN'>; label: string }> = [
  { status: 'VALIDATED', label: 'Valider' },
  { status: 'REJECTED', label: 'Rejeter' },
  { status: 'ESCALATED', label: 'Escalader' },
]

function formatDate(value: string) {
  return new Date(value).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}

export default function AlertsRegistry() {
  const { data: alerts, error, loading, reload } = useFetch<Alert[]>(() => listAlerts())
  const [statusFilter, setStatusFilter] = useState<AlertStatus | 'ALL'>('OPEN')
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [reviewNote, setReviewNote] = useState('')
  const [pendingAction, setPendingAction] = useState<Exclude<AlertStatus, 'OPEN'> | null>(null)
  const [toast, setToast] = useState<{ action: string; alertId: number } | null>(null)
  const [reviewError, setReviewError] = useState<string | null>(null)

  const filtered = useMemo(() => {
    if (!alerts) return []
    if (statusFilter === 'ALL') return alerts
    return alerts.filter((a) => a.status === statusFilter)
  }, [alerts, statusFilter])

  const selected = filtered.find((a) => a.id === selectedId) ?? filtered[0] ?? null

  const handleDecision = async (action: Exclude<AlertStatus, 'OPEN'>) => {
    if (!selected) return
    if (reviewNote.trim().length < 3) {
      setPendingAction(action)
      setReviewError('La justification doit compter au moins 3 caractères.')
      return
    }
    setPendingAction(action)
    setReviewError(null)
    try {
      await reviewAlert(selected.id, action, reviewNote.trim())
      const label = decisionActions.find((d) => d.status === action)?.label ?? action
      setToast({ action: label, alertId: selected.id })
      setReviewNote('')
      reload()
    } catch (err) {
      setReviewError(err instanceof Error ? err.message : 'Échec de la décision.')
    } finally {
      setPendingAction(null)
    }
  }

  return (
    <div>
      <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">Registre des alertes</p>
      <h1 className="mt-2 text-3xl text-encre sm:text-4xl">Alertes à traiter</h1>

      <div className="mt-5 flex flex-wrap gap-2">
        {(['OPEN', 'VALIDATED', 'REJECTED', 'ESCALATED', 'ALL'] as const).map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatusFilter(s)}
            className={`rounded-sm border px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors ${
              statusFilter === s ? 'border-encre bg-encre text-papier' : 'border-encre/20 text-graphite/65 hover:border-encre/40'
            }`}
          >
            {s === 'ALL' ? 'Toutes' : statusLabels[s]}
          </button>
        ))}
      </div>

      {toast && (
        <div className="mt-4 rounded-sm border border-vert/40 bg-vert/5 px-4 py-2">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-vert">
            Alerte #{toast.alertId} — {toast.action}.
          </p>
        </div>
      )}

      {loading && <p className="mt-6 text-sm text-graphite/60">Chargement des alertes…</p>}

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
        <div className="mt-6 grid gap-4 lg:grid-cols-[1fr_minmax(0,22rem)]">
          <div className="overflow-x-auto rounded-sm border border-encre/12">
            <table className="w-full min-w-[520px] border-collapse text-left text-sm">
              <thead>
                <tr className="border-b border-encre/15 bg-papier-soutenu/50">
                  <th className="px-4 py-2 font-mono text-[9px] font-medium uppercase tracking-[0.14em] text-graphite/55">ID</th>
                  <th className="px-4 py-2 font-mono text-[9px] font-medium uppercase tracking-[0.14em] text-graphite/55">Type</th>
                  <th className="px-4 py-2 font-mono text-[9px] font-medium uppercase tracking-[0.14em] text-graphite/55">Sévérité</th>
                  <th className="px-4 py-2 font-mono text-[9px] font-medium uppercase tracking-[0.14em] text-graphite/55">Statut</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-sm text-graphite/55">
                      Aucune alerte pour ce filtre.
                    </td>
                  </tr>
                )}
                {filtered.map((alert, index) => (
                  <tr
                    key={alert.id}
                    onClick={() => setSelectedId(alert.id)}
                    className={`cursor-pointer transition-colors ${
                      selected?.id === alert.id ? 'bg-papier-soutenu/60' : index % 2 === 1 ? 'bg-papier-soutenu/20' : ''
                    }`}
                  >
                    <td className="px-4 py-2.5 font-mono text-xs text-graphite/60">#{alert.id}</td>
                    <td className="px-4 py-2.5 text-encre">{alert.alert_type}</td>
                    <td className={`px-4 py-2.5 font-mono text-[10px] uppercase tracking-[0.1em] ${severityColor[alert.severity]}`}>
                      {alert.severity}
                    </td>
                    <td className={`px-4 py-2.5 font-mono text-[10px] uppercase tracking-[0.1em] ${statusColor[alert.status]}`}>
                      {statusLabels[alert.status]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="rounded-sm border border-encre/12 bg-papier-soutenu/40 p-5">
            {!selected ? (
              <p className="text-sm text-graphite/55">Sélectionnez une alerte pour voir le détail et décider.</p>
            ) : (
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-graphite/50">
                  Alerte #{selected.id} · {formatDate(selected.created_at)}
                </p>
                <h2 className="mt-1 text-xl text-encre">{selected.alert_type}</h2>
                <p className="mt-2 text-sm leading-6 text-graphite/75">{selected.description}</p>

                {selected.status !== 'OPEN' ? (
                  <div className="mt-5 rounded-sm border border-encre/10 bg-papier p-3">
                    <p className={`font-mono text-[10px] uppercase tracking-[0.14em] ${statusColor[selected.status]}`}>
                      {statusLabels[selected.status]}
                    </p>
                    {selected.review_note && <p className="mt-1 text-sm text-graphite/70">{selected.review_note}</p>}
                  </div>
                ) : (
                  <div className="mt-5">
                    <label htmlFor="review-note" className="block text-sm font-medium text-graphite/85">
                      Justification de la décision
                    </label>
                    <textarea
                      id="review-note"
                      rows={3}
                      value={reviewNote}
                      onChange={(e) => setReviewNote(e.target.value)}
                      className="mt-1 w-full resize-none rounded-sm border border-encre/20 bg-papier px-3 py-2.5 font-mono text-sm text-encre focus:border-encre focus:outline-none focus:ring-1 focus:ring-encre"
                    />
                    {reviewError && <p className="mt-1 font-mono text-[10px] text-tampon">{reviewError}</p>}

                    <div className="mt-4 flex flex-wrap gap-2">
                      <PrimaryButton
                        type="button"
                        disabled={pendingAction !== null}
                        onClick={() => handleDecision('VALIDATED')}
                      >
                        Valider
                      </PrimaryButton>
                      <SecondaryButton
                        type="button"
                        disabled={pendingAction !== null}
                        onClick={() => handleDecision('REJECTED')}
                      >
                        Rejeter
                      </SecondaryButton>
                      <SecondaryButton
                        type="button"
                        disabled={pendingAction !== null}
                        onClick={() => handleDecision('ESCALATED')}
                      >
                        Escalader
                      </SecondaryButton>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
