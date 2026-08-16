import { useMemo } from 'react'
import { listAlerts, listClients, type AlertSeverity, type Client } from './api/client'
import { useFetch } from './api/useFetch'

type Severity = Exclude<AlertSeverity, never>

const severityMeta: Record<Severity, { label: string; color: string }> = {
  LOW: { label: 'Faible', color: '#3F7057' },
  MEDIUM: { label: 'Moyen', color: '#8A5F0F' },
  HIGH: { label: 'Élevé', color: '#9B2948' },
  CRITICAL: { label: 'Critique', color: '#6E1834' },
}

function formatDay(value: string) {
  return new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: '2-digit' }).format(new Date(value))
}

export default function RiskCharts() {
  const { data: alerts } = useFetch(() => listAlerts())
  const { data: clients } = useFetch<Client[]>(() => listClients())

  const severity = useMemo(() => {
    const counts: Record<Severity, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 }
    for (const alert of alerts ?? []) counts[alert.severity] += 1
    return (Object.keys(counts) as Severity[]).map((key) => ({ key, ...severityMeta[key], count: counts[key] }))
  }, [alerts])

  const riskTimeline = useMemo(() => {
    const buckets = new Map<string, { total: number; count: number }>()
    for (const client of clients ?? []) {
      const day = client.created_at.slice(0, 10)
      const current = buckets.get(day) ?? { total: 0, count: 0 }
      current.total += client.risk_score
      current.count += 1
      buckets.set(day, current)
    }
    return [...buckets.entries()]
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-7)
      .map(([day, bucket]) => ({ day, value: Math.round(bucket.total / bucket.count) }))
  }, [clients])

  const maxSeverity = Math.max(1, ...severity.map((item) => item.count))
  const maxRisk = Math.max(100, ...riskTimeline.map((item) => item.value))

  return (
    <section className="grid gap-6 lg:grid-cols-2" aria-labelledby="risk-charts-title">
      <div>
        <div className="mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">T36 · alertes</p>
          <h2 id="risk-charts-title" className="mt-1 text-xl text-encre">Criticité des alertes</h2>
          <p className="mt-1 text-sm leading-5 text-graphite/65">Une lecture par niveau pour prioriser la revue humaine.</p>
        </div>
        <div className="space-y-3 rounded-sm border border-encre/12 bg-papier p-4">
          {severity.map((item) => (
            <div key={item.key}>
              <div className="mb-1 flex items-center justify-between gap-3 font-mono text-[10px] uppercase tracking-[0.12em]">
                <span className="text-graphite/65">{item.label}</span>
                <span className="text-encre">{item.count}</span>
              </div>
              <div className="h-3 overflow-hidden rounded-sm border border-encre/10 bg-papier-soutenu/50">
                <div
                  className="h-full transition-[width] duration-300"
                  style={{ width: `${(item.count / maxSeverity) * 100}%`, backgroundColor: item.color }}
                  title={`${item.label}: ${item.count} alerte(s)`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <div className="mb-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">T36 · risque</p>
          <h2 className="mt-1 text-xl text-encre">Évolution du score moyen</h2>
          <p className="mt-1 text-sm leading-5 text-graphite/65">Une timeline simple plutôt qu’une jauge concurrente au tampon de T26.</p>
        </div>
        <div className="rounded-sm border border-encre/12 bg-papier p-4">
          {riskTimeline.length === 0 ? (
            <p className="py-10 text-center text-sm text-graphite/50">Pas encore assez de données historiques.</p>
          ) : (
            <svg viewBox="0 0 420 190" className="h-auto w-full" role="img" aria-label="Évolution du score de risque moyen">
              <line x1="32" y1="150" x2="400" y2="150" stroke="#17324D" strokeOpacity="0.18" />
              <line x1="32" y1="100" x2="400" y2="100" stroke="#17324D" strokeOpacity="0.10" />
              <line x1="32" y1="50" x2="400" y2="50" stroke="#17324D" strokeOpacity="0.10" />
              <polyline
                fill="none"
                stroke="#9B2948"
                strokeWidth="4"
                strokeLinejoin="round"
                strokeLinecap="round"
                points={riskTimeline.map((point, index) => {
                  const x = riskTimeline.length === 1 ? 216 : 32 + (368 * index) / (riskTimeline.length - 1)
                  const y = 150 - (118 * point.value) / maxRisk
                  return `${x},${y}`
                }).join(' ')}
              />
              {riskTimeline.map((point, index) => {
                const x = riskTimeline.length === 1 ? 216 : 32 + (368 * index) / (riskTimeline.length - 1)
                const y = 150 - (118 * point.value) / maxRisk
                return (
                  <g key={point.day}>
                    <circle cx={x} cy={y} r="5" fill="#E7EEE8" stroke="#9B2948" strokeWidth="3">
                      <title>{`${formatDay(point.day)} : score moyen ${point.value}/100`}</title>
                    </circle>
                    <text x={x} y="172" textAnchor="middle" fontSize="9" fill="#202522" opacity="0.6">{formatDay(point.day)}</text>
                  </g>
                )
              })}
              <text x="20" y="55" textAnchor="end" fontSize="9" fill="#202522" opacity="0.55">100</text>
              <text x="20" y="105" textAnchor="end" fontSize="9" fill="#202522" opacity="0.55">50</text>
              <text x="20" y="155" textAnchor="end" fontSize="9" fill="#202522" opacity="0.55">0</text>
            </svg>
          )}
        </div>
      </div>
    </section>
  )
}
