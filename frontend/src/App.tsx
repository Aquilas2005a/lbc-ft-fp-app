import { useState } from 'react'
import Dashboard from './Dashboard'

type Role = 'terrain' | 'superviseur' | 'conformite'
type Tab = 'accueil' | 'dossiers' | 'alertes' | 'clients' | 'audit'

type NavItem = {
  id: Tab
  label: string
  short: string
}

const roleMeta: Record<Role, { label: string; description: string }> = {
  terrain: {
    label: 'Agent terrain',
    description: 'Saisie rapide, dossiers et vérifications au point de contact.',
  },
  superviseur: {
    label: 'Superviseur',
    description: 'Suivi des équipes, alertes à traiter et décisions en attente.',
  },
  conformite: {
    label: 'Conformité',
    description: 'Screening, preuves, audit et décisions à forte traçabilité.',
  },
}

const navByRole: Record<Role, NavItem[]> = {
  terrain: [
    { id: 'accueil', label: 'Accueil', short: '01' },
    { id: 'dossiers', label: 'Dossiers', short: '02' },
    { id: 'clients', label: 'Clients', short: '03' },
  ],
  superviseur: [
    { id: 'accueil', label: 'Tableau', short: '01' },
    { id: 'dossiers', label: 'Dossiers', short: '02' },
    { id: 'alertes', label: 'Alertes', short: '03' },
    { id: 'clients', label: 'Clients', short: '04' },
  ],
  conformite: [
    { id: 'accueil', label: 'Accueil', short: '01' },
    { id: 'alertes', label: 'Alertes', short: '02' },
    { id: 'clients', label: 'Screening', short: '03' },
    { id: 'audit', label: 'Audit', short: '04' },
  ],
}

const tabCopy: Record<Exclude<Tab, 'accueil'>, { title: string; body: string }> = {
  dossiers: {
    title: 'Dossiers de décision',
    body: 'Retrouver les dossiers actifs, leur statut et la prochaine action attendue.',
  },
  alertes: {
    title: 'Alertes à traiter',
    body: 'Centraliser les signalements qui exigent une revue humaine et une justification.',
  },
  clients: {
    title: 'Registre clients',
    body: 'Rechercher un client, lancer un screening et conserver les éléments de contexte.',
  },
  audit: {
    title: 'Journal d’audit',
    body: 'Consulter les décisions et actions importantes avec leur trace temporelle.',
  },
}

function FolderIcon({ active = false }: { active?: boolean }) {
  return (
    <span
      aria-hidden="true"
      className={`inline-flex h-7 w-7 items-center justify-center rounded-sm border font-mono text-[10px] ${
        active ? 'border-ocre bg-ocre text-encre' : 'border-papier/40 text-papier'
      }`}
    >
      +
    </span>
  )
}

function App() {
  const [role, setRole] = useState<Role>('terrain')
  const [activeTab, setActiveTab] = useState<Tab>('accueil')
  const navItems = navByRole[role]
  const roleInfo = roleMeta[role]

  const changeRole = (nextRole: Role) => {
    setRole(nextRole)
    setActiveTab('accueil')
  }

  return (
    <main className="min-h-screen bg-papier text-graphite">
      <div className="min-h-screen lg:grid lg:grid-cols-[17rem_1fr]">
        <aside className="hidden border-r border-encre bg-encre text-papier lg:flex lg:flex-col">
          <div className="flex items-center justify-between border-b border-papier/15 px-5 py-5">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-papier/65">KORA</p>
              <p className="font-display text-xl">Registre de décision</p>
            </div>
            <span className="font-mono text-[10px] text-papier/55">T25</span>
          </div>

          <div className="px-4 pt-5">
            <p className="px-2 font-mono text-[10px] uppercase tracking-[0.24em] text-papier/50">Rôle actif</p>
            <div className="mt-2 grid gap-1 rounded-sm border border-papier/10 bg-black/10 p-1">
              {(Object.keys(roleMeta) as Role[]).map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => changeRole(item)}
                  className={`flex items-center justify-between rounded-sm px-3 py-2 text-left text-sm transition-colors ${
                    role === item ? 'bg-papier text-encre' : 'text-papier/75 hover:bg-papier/10'
                  }`}
                >
                  <span>{roleMeta[item].label}</span>
                  <span className="font-mono text-[9px] uppercase">{item.slice(0, 3)}</span>
                </button>
              ))}
            </div>
          </div>

          <nav className="px-4 py-5" aria-label="Navigation principale">
            <p className="px-2 font-mono text-[10px] uppercase tracking-[0.24em] text-papier/50">Dossier</p>
            <div className="mt-2 space-y-1">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveTab(item.id)}
                  className={`group flex w-full items-center gap-3 border-l-2 px-3 py-3 text-left transition-colors ${
                    activeTab === item.id
                      ? 'border-ocre bg-papier/10 text-papier'
                      : 'border-transparent text-papier/65 hover:border-papier/30 hover:bg-papier/5 hover:text-papier'
                  }`}
                >
                  <FolderIcon active={activeTab === item.id} />
                  <span className="flex-1 font-mono text-xs uppercase tracking-[0.14em]">{item.label}</span>
                  <span className="font-mono text-[9px] text-papier/40">{item.short}</span>
                </button>
              ))}
            </div>
          </nav>

          <div className="mt-auto border-t border-papier/15 px-5 py-4">
            <p className="font-mono text-[9px] uppercase tracking-[0.2em] text-papier/40">Contexte</p>
            <p className="mt-1 text-xs text-papier/65">{roleInfo.description}</p>
          </div>
        </aside>

        <div className="flex min-h-screen flex-col">
          <header className="sticky top-0 z-20 border-b border-encre/15 bg-papier/95 backdrop-blur lg:px-8">
            <div className="flex min-h-16 items-center justify-between gap-3 px-4 py-3 sm:px-6">
              <div className="min-w-0">
                <div className="flex items-center gap-2 font-mono text-[9px] uppercase tracking-[0.22em] text-encre/55">
                  <span>KORA</span>
                  <span>/</span>
                  <span>{roleInfo.label}</span>
                </div>
                <p className="truncate font-display text-lg text-encre sm:text-xl">
                  {activeTab === 'accueil'
                    ? role === 'superviseur'
                      ? 'Tableau de bord'
                      : 'Accueil opérationnel'
                    : tabCopy[activeTab].title}
                </p>
              </div>

              <div className="flex shrink-0 items-center gap-2">
                <span className="hidden rounded-sm border border-encre/15 bg-papier-soutenu px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-encre/70 sm:inline-flex">
                  Mode local
                </span>
                <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-encre bg-encre font-mono text-[10px] font-semibold text-papier">
                  KA
                </span>
              </div>
            </div>
          </header>

          <nav className="order-last sticky bottom-0 z-30 border-t border-encre/15 bg-encre px-2 py-2 lg:hidden" aria-label="Navigation mobile">
            <div className="flex gap-1 overflow-x-auto">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveTab(item.id)}
                  className={`min-w-[6.2rem] flex-1 rounded-sm px-2 py-2.5 text-center transition-colors ${
                    activeTab === item.id ? 'bg-papier text-encre' : 'text-papier/70 hover:bg-papier/10 hover:text-papier'
                  }`}
                >
                  <span className="block font-mono text-[9px] uppercase tracking-[0.16em]">{item.short}</span>
                  <span className="mt-0.5 block text-xs font-semibold">{item.label}</span>
                </button>
              ))}
            </div>
          </nav>

          <section className="flex-1 px-4 pb-8 pt-5 sm:px-6 lg:px-8 lg:pb-12 lg:pt-8">
            {activeTab === 'accueil' && role === 'superviseur' ? (
              <Dashboard onNavigate={setActiveTab} />
            ) : activeTab === 'accueil' ? (
              <>
                <section className="relative isolate overflow-hidden rounded-sm border border-encre/20 bg-encre" style={{ minHeight: '50vh' }}>
                  <img
                    src="/images/hero-1600.webp"
                    srcSet="/images/hero-720.webp 720w, /images/hero-1200.webp 1200w, /images/hero-1600.webp 1600w"
                    sizes="(max-width: 768px) 100vw, 1200px"
                    alt="Vendeuse de marché ouest-africain recevant un paiement en espèces devant son étal de fruits"
                    loading="lazy"
                    decoding="async"
                    width={1600}
                    height={841}
                    className="absolute inset-0 h-full w-full object-cover"
                  />
                  <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(23,50,77,0.97)_0%,rgba(23,50,77,0.78)_42%,rgba(23,50,77,0.24)_82%,rgba(23,50,77,0.05)_100%)]" />
                  <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(200,146,45,0.12),transparent_44%,rgba(23,50,77,0.74)_100%)]" />

                  <div className="relative flex h-full min-h-[50vh] items-end p-5 sm:p-8 lg:max-w-3xl lg:p-12">
                    <div className="pb-2 sm:pb-4">
                      <span className="inline-flex border border-ocre bg-ocre/15 px-2.5 py-1 font-mono text-[10px] font-semibold uppercase tracking-[0.18em] text-ocre">
                        Finance de proximité / terrain
                      </span>
                      <h1 className="mt-4 max-w-2xl font-display text-4xl leading-[1.03] text-papier sm:text-5xl lg:text-6xl">
                        Chaque décision doit rester compréhensible, même au milieu du terrain.
                      </h1>
                      <p className="mt-4 max-w-xl text-sm leading-6 text-papier/80 sm:text-base">
                        KORA donne à l’équipe un dossier unique pour vérifier, décider et laisser une trace — sans ralentir le travail de proximité.
                      </p>
                      <div className="mt-6 flex flex-wrap gap-3">
                        <button
                          type="button"
                          onClick={() => setActiveTab('dossiers')}
                          className="rounded-sm bg-ocre px-4 py-3 font-texte text-sm font-semibold text-encre shadow-sm transition-transform hover:-translate-y-0.5"
                        >
                          Ouvrir les dossiers
                        </button>
                        <button
                          type="button"
                          onClick={() => setActiveTab('alertes')}
                          className="rounded-sm border border-papier/45 bg-encre/35 px-4 py-3 font-texte text-sm font-medium text-papier backdrop-blur transition-colors hover:bg-encre/55"
                        >
                          Voir les alertes
                        </button>
                      </div>
                      <a
                        href="https://www.pexels.com/photo/exchange-27814588/"
                        target="_blank"
                        rel="noreferrer"
                        className="mt-5 inline-block font-mono text-[9px] uppercase tracking-[0.16em] text-papier/50 underline decoration-papier/30 underline-offset-4 hover:text-papier"
                      >
                        Photo : Nannawa Badiya / Pexels · libre d’utilisation
                      </a>
                    </div>
                  </div>
                </section>

                <section className="mt-5 grid gap-3 md:grid-cols-3">
                  {[
                    ['01', 'Vérifier', 'Dossier lisible, identités et signaux réunis au même endroit.'],
                    ['02', 'Décider', 'La revue reste humaine, explicable et documentée.'],
                    ['03', 'Tracer', 'Chaque action importante laisse un historique exploitable.'],
                  ].map(([number, title, body]) => (
                    <article key={number} className="border-t-2 border-encre bg-papier-soutenu/45 px-4 py-4 sm:px-5">
                      <p className="font-mono text-[10px] text-ocre-texte">{number}</p>
                      <h2 className="mt-2 text-xl text-encre">{title}</h2>
                      <p className="mt-1 text-sm leading-5 text-graphite/75">{body}</p>
                    </article>
                  ))}
                </section>
              </>
            ) : (
              <section className="mx-auto max-w-4xl rounded-sm border border-encre/15 bg-papier-soutenu/50 p-6 sm:p-8">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ocre-texte">{roleInfo.label}</p>
                <h1 className="mt-2 text-4xl text-encre">{tabCopy[activeTab].title}</h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-graphite/80">{tabCopy[activeTab].body}</p>
                <div className="mt-7 grid gap-3 sm:grid-cols-3">
                  {['À traiter', 'En revue', 'Historique'].map((label, index) => (
                    <div key={label} className="rounded-sm border border-encre/10 bg-papier p-4">
                      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-encre/50">0{index + 1}</p>
                      <p className="mt-2 text-sm font-semibold text-encre">{label}</p>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </section>
        </div>
      </div>
    </main>
  )
}

export default App
