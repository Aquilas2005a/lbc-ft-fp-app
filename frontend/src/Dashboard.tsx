import { useState } from 'react'
import { listAlerts, listTransactions, type Alert, type Transaction } from './api/client'
import { useFetch } from './api/useFetch'
import RiskCharts from './RiskCharts'
import { downloadCsv } from './utils/exportCsv'

type RiskBand = {
  id: 'faible' | 'moyen' | 'eleve'
  label: string
  count: number
  color: string
  textColor: string
}

const riskBands: RiskBand[] = [
  { id: 'faible', label: 'Faible', count: 872, color: 'bg-vert', textColor: 'text-vert' },
  { id: 'moyen', label: 'Moyen', count: 341, color: 'bg-ocre', textColor: 'text-ocre-texte' },
  { id: 'eleve', label: 'Élevé', count: 71, color: 'bg-tampon', textColor: 'text-tampon' },
]

const totalPortefeuille = riskBands.reduce((sum, band) => sum + band.count, 0)

type Alerte = { id: string; client: string; motif: string; montant: string; urgence: 'haute' | 'moyenne' }
const alertesPrioritaires: Alerte[] = [
  { id: 'AL-0231', client: 'SARL Tokpa Négoce', motif: 'Seuil de transaction dépassé sur 48h', montant: '4 200 000 FCFA', urgence: 'haute' },
  { id: 'AL-0229', client: 'R. Adjovi (particulier)', motif: 'Bénéficiaire lié à un dossier existant', montant: '850 000 FCFA', urgence: 'haute' },
  { id: 'AL-0224', client: 'Coopérative Zou Épargne', motif: 'Activité inhabituelle vs profil déclaré', montant: '1 960 000 FCFA', urgence: 'haute' },
  { id: 'AL-0219', client: 'M. Houngbo', motif: 'Document d’identité arrivant à expiration', montant: '—', urgence: 'moyenne' },
]

type Mouvement = { heure: string; client: string; type: string; montant: string; statut: 'validé' | 'en revue' }
const derniersMouvements: Mouvement[] = [
  { heure: '14:52', client: 'SARL Tokpa Négoce', type: 'Virement sortant', montant: '4 200 000 FCFA', statut: 'en revue' },
  { heure: '14:10', client: 'A. Dossou', type: 'Dépôt guichet', montant: '150 000 FCFA', statut: 'validé' },
  { heure: '13:47', client: 'Coopérative Zou Épargne', type: 'Collecte groupée', montant: '1 960 000 FCFA', statut: 'en revue' },
  { heure: '13:02', client: 'R. Adjovi', type: 'Virement entrant', montant: '850 000 FCFA', statut: 'en revue' },
  { heure: '11:35', client: 'M. Houngbo', type: 'Retrait', montant: '60 000 FCFA', statut: 'validé' },
]

function StatLedgerItem({ value, label }: { value: string; label: string }) {
  return <div className="flex flex-col gap-1 px-5 py-4 first:pl-0 last:pr-0"><p className="font-display text-3xl leading-none text-encre sm:text-4xl">{value}</p><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-graphite/55">{label}</p></div>
}

function riskStampClass(level: 'Faible' | 'Moyen' | 'Élevé') {
  return level === 'Élevé' ? 'border-tampon text-tampon' : level === 'Moyen' ? 'border-ocre-texte text-ocre-texte' : 'border-vert text-vert'
}

export default function Dashboard({ onNavigate }: { onNavigate: (tab: 'dossiers' | 'alertes' | 'clients') => void }) {
  const { data: alerts } = useFetch<Alert[]>(() => listAlerts())
  const { data: transactions } = useFetch<Transaction[]>(() => listTransactions())
  const [exportMessage, setExportMessage] = useState<string | null>(null)

  const exportAlerts = () => {
    const rows = (alerts ?? []).map((alert) => ({
      id: alert.id,
      type: alert.alert_type,
      severite: alert.severity,
      statut: alert.status,
      client_id: alert.client_id,
      transaction_id: alert.transaction_id,
      creee_le: alert.created_at,
    }))
    if (downloadCsv('kora-alertes.csv', rows)) setExportMessage(`${rows.length} alerte(s) exportée(s).`)
  }

  const exportTransactions = () => {
    const rows = (transactions ?? []).map((tx) => ({
      id: tx.id,
      compte_id: tx.account_id,
      montant: tx.amount,
      devise: tx.currency,
      type: tx.transaction_type,
      statut: tx.status,
      contrepartie: tx.counterparty_name,
      pays: tx.counterparty_country,
      horodatage: tx.timestamp,
    }))
    if (downloadCsv('kora-transactions.csv', rows)) setExportMessage(`${rows.length} transaction(s) exportée(s).`)
  }

  return (
    <div className="space-y-10">
      <section>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">Superviseur · aujourd’hui</p>
        <h1 className="mt-2 text-3xl text-encre sm:text-4xl">Le portefeuille en un coup d’œil</h1>
        <div className="mt-5 flex flex-wrap divide-x divide-encre/12 rounded-sm border border-encre/12 bg-papier-soutenu/40">
          <StatLedgerItem value="1 284" label="Clients actifs" /><StatLedgerItem value="7" label="Alertes ouvertes" /><StatLedgerItem value="42,9 M" label="Volume FCFA · 7 jours" /><StatLedgerItem value="5" label="Dossiers en attente" />
        </div>
      </section>

      <section>
        <h2 className="text-xl text-encre">Où se situe le risque du portefeuille</h2>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-graphite/70">Répartition des {totalPortefeuille.toLocaleString('fr-FR')} clients actifs par niveau, comme un tampon de classement — pas un score isolé.</p>
        <div className="mt-5 overflow-hidden rounded-sm border border-encre/15">
          <div className="flex h-9 w-full">{riskBands.map((band) => <div key={band.id} className={`${band.color} h-full`} style={{ width: `${(band.count / totalPortefeuille) * 100}%` }} />)}</div>
          <div className="flex divide-x divide-encre/10 border-t border-encre/10 bg-papier">
            {riskBands.map((band) => <div key={band.id} className="flex-1 px-4 py-3"><span className={`inline-flex -rotate-2 items-center rounded-sm border-2 px-2 py-0.5 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] ${band.textColor}`}>{band.label}</span><p className="mt-2 font-display text-2xl text-encre">{band.count}</p><p className="font-mono text-[10px] text-graphite/50">{((band.count / totalPortefeuille) * 100).toFixed(1)} % du portefeuille</p></div>)}
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">{riskBands.map((band) => <span key={band.id} className={`rounded-sm border px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] ${riskStampClass(band.label as 'Faible' | 'Moyen' | 'Élevé')}`}>{band.label} · signature T26</span>)}</div>
      </section>

      <RiskCharts />

      <section>
        <div className="flex flex-wrap items-end justify-between gap-3"><div><h2 className="text-xl text-encre">Exports de contrôle</h2><p className="mt-1 text-sm text-graphite/65">Les exports servent à l’analyse hors ligne et au dossier de revue.</p></div><div className="flex flex-wrap gap-2"><button type="button" onClick={exportAlerts} className="rounded-sm border border-encre/25 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-encre hover:bg-encre hover:text-papier">Exporter les alertes</button><button type="button" onClick={exportTransactions} className="rounded-sm border border-encre/25 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-encre hover:bg-encre hover:text-papier">Exporter les transactions</button></div></div>
        {exportMessage && <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-vert" aria-live="polite">{exportMessage}</p>}
      </section>

      <section>
        <h2 className="text-xl text-encre">Ce qui attend une décision</h2>
        <p className="mt-1 max-w-2xl text-sm leading-6 text-graphite/70">Les signaux les plus importants restent visibles avant l’ouverture du registre.</p>
        <div className="mt-4 divide-y divide-encre/10 rounded-sm border border-encre/12 bg-papier">{alertesPrioritaires.map((alerte) => <div key={alerte.id} className="flex items-start gap-3 px-4 py-3 sm:items-center sm:px-5"><span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full sm:mt-0 ${alerte.urgence === 'haute' ? 'bg-tampon' : 'bg-ocre'}`} aria-hidden="true"/><div className="min-w-0 flex-1"><div className="flex flex-wrap items-baseline gap-x-2"><p className="font-mono text-[10px] text-graphite/45">{alerte.id}</p><p className="truncate text-sm font-semibold text-encre">{alerte.client}</p></div><p className="mt-0.5 text-xs leading-5 text-graphite/65">{alerte.motif}</p></div><p className="shrink-0 font-mono text-xs text-graphite/70">{alerte.montant}</p></div>)}</div>
        <button type="button" onClick={() => onNavigate('alertes')} className="mt-3 font-mono text-[10px] uppercase tracking-[0.16em] text-ocre-texte underline decoration-ocre-texte/40 underline-offset-4 hover:text-encre">Ouvrir le registre des alertes →</button>
      </section>

      <section>
        <h2 className="text-xl text-encre">Dernier mouvement du registre</h2>
        <div className="mt-4 overflow-x-auto rounded-sm border border-encre/12"><table className="w-full min-w-[560px] border-collapse text-left text-sm"><thead><tr className="border-b border-encre/15 bg-papier-soutenu/50"><th className="px-4 py-2 font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/55">Heure</th><th className="px-4 py-2 font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/55">Client</th><th className="px-4 py-2 font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/55">Opération</th><th className="px-4 py-2 text-right font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/55">Montant</th><th className="px-4 py-2 font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/55">Statut</th></tr></thead><tbody>{derniersMouvements.map((mvt, index) => <tr key={`${mvt.heure}-${mvt.client}`} className={index % 2 === 1 ? 'bg-papier-soutenu/25' : ''}><td className="px-4 py-2.5 font-mono text-xs text-graphite/60">{mvt.heure}</td><td className="px-4 py-2.5 text-encre">{mvt.client}</td><td className="px-4 py-2.5 text-graphite/70">{mvt.type}</td><td className="px-4 py-2.5 text-right font-mono text-xs text-graphite/80">{mvt.montant}</td><td className="px-4 py-2.5"><span className={`font-mono text-[10px] uppercase tracking-[0.1em] ${mvt.statut === 'validé' ? 'text-vert' : 'text-ocre-texte'}`}>{mvt.statut}</span></td></tr>)}</tbody></table></div>
      </section>
    </div>
  )
}
