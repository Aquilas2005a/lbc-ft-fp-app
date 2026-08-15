import type { ReactNode } from 'react'

type LandingPageProps = { onEnterApp: () => void }

const pillars = [
  { number: '01', title: 'Vérifier', text: 'Screening, identité, signaux et contexte réunis avant la décision.' },
  { number: '02', title: 'Décider', text: 'Une revue humaine, explicable et documentée, sans automatiser le jugement.' },
  { number: '03', title: 'Tracer', text: 'Chaque action importante laisse une preuve exploitable pour le contrôle.' },
]

const proofItems = [
  ['Clients', 'registre centralisé'],
  ['Transactions', 'mouvements surveillés'],
  ['Alertes', 'revue humaine'],
  ['Audit', 'décisions traçables'],
]

function Accent({ children }: { children: ReactNode }) {
  return <span className="text-ocre">{children}</span>
}

export default function LandingPage({ onEnterApp }: LandingPageProps) {
  return (
    <main className="min-h-screen overflow-x-hidden bg-papier text-graphite selection:bg-ocre selection:text-encre">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-papier/10 bg-encre/75 text-papier backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
          <a href="#accueil" className="flex items-center gap-3" aria-label="KORA, accueil">
            <span className="inline-flex h-9 w-9 items-center justify-center border border-papier/35 font-mono text-[10px] tracking-[0.18em]">K</span>
            <span><span className="block font-mono text-[9px] uppercase tracking-[0.28em] text-papier/60">Conformité</span><span className="block font-display text-lg leading-none">KORA</span></span>
          </a>
          <nav className="hidden items-center gap-7 lg:flex" aria-label="Navigation du site">
            <a href="#approche" className="font-mono text-[10px] uppercase tracking-[0.16em] text-papier/70 transition-colors hover:text-papier">Approche</a>
            <a href="#metier" className="font-mono text-[10px] uppercase tracking-[0.16em] text-papier/70 transition-colors hover:text-papier">Métier</a>
            <a href="#preuve" className="font-mono text-[10px] uppercase tracking-[0.16em] text-papier/70 transition-colors hover:text-papier">Preuves</a>
            <button type="button" onClick={onEnterApp} className="rounded-sm border border-papier/35 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.16em] text-papier transition-colors hover:bg-papier hover:text-encre">Se connecter</button>
          </nav>
          <button type="button" onClick={onEnterApp} className="rounded-sm bg-ocre px-4 py-2 font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-encre lg:hidden">Entrer</button>
        </div>
      </header>

      <section id="accueil" className="relative isolate min-h-[82vh] overflow-hidden bg-encre text-papier">
        <img src="/images/hero-1600.webp" srcSet="/images/hero-720.webp 720w, /images/hero-1200.webp 1200w, /images/hero-1600.webp 1600w" sizes="100vw" alt="Transaction en espèces sur un marché ouest-africain" width={1600} height={841} fetchPriority="high" decoding="async" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(23,50,77,0.97)_0%,rgba(23,50,77,0.86)_42%,rgba(23,50,77,0.45)_78%,rgba(23,50,77,0.18)_100%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(23,50,77,0.2)_0%,rgba(23,50,77,0.08)_42%,rgba(23,50,77,0.9)_100%)]" />
        <div className="relative mx-auto flex min-h-[82vh] max-w-7xl items-end px-5 pb-14 pt-28 sm:px-8 sm:pb-18 lg:pb-20">
          <div className="max-w-4xl">
            <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-ocre">LBC / FT / FP · finance de proximité</p>
            <h1 className="mt-5 max-w-4xl font-display text-5xl leading-[0.98] text-papier sm:text-6xl lg:text-8xl">La conformité doit <Accent>éclairer</Accent> la décision, pas ralentir le terrain.</h1>
            <p className="mt-6 max-w-2xl text-base leading-7 text-papier/78 sm:text-lg">KORA rassemble les clients, transactions, alertes et preuves dans un même dossier de décision — conçu pour les équipes qui travaillent au plus près des clients.</p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <button type="button" onClick={onEnterApp} className="rounded-sm bg-ocre px-5 py-3.5 font-texte text-sm font-semibold text-encre transition-transform hover:-translate-y-0.5">Accéder à l’espace KORA</button>
              <a href="#approche" className="rounded-sm border border-papier/40 bg-encre/20 px-5 py-3.5 font-texte text-sm font-medium text-papier backdrop-blur transition-colors hover:bg-papier/10">Découvrir l’approche</a>
            </div>
            <p className="mt-8 font-mono text-[9px] uppercase tracking-[0.18em] text-papier/45">Photo : Nannawa Badiya / Pexels · traitement KORA</p>
          </div>
        </div>
      </section>

      <section id="approche" className="border-b border-encre/10 bg-papier px-5 py-20 sm:px-8 lg:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1.4fr] lg:gap-20">
            <div><p className="font-mono text-[10px] uppercase tracking-[0.24em] text-ocre-texte">L’approche KORA</p><h2 className="mt-3 max-w-md font-display text-4xl leading-tight text-encre sm:text-5xl">Un dossier unique pour passer du <span className="text-tampon">signal</span> à la décision.</h2></div>
            <p className="max-w-2xl text-base leading-8 text-graphite/75 sm:text-lg">Le produit ne remplace pas le jugement de l’équipe conformité. Il donne au bon rôle la bonne information, au bon moment, puis conserve la trace de ce qui a été vérifié, décidé et justifié.</p>
          </div>
          <div className="mt-14 grid border-y border-encre/12 md:grid-cols-3">{pillars.map((pillar) => <article key={pillar.number} className="border-b border-encre/12 px-5 py-8 last:border-b-0 md:border-b-0 md:border-r md:last:border-r-0 lg:px-8 lg:py-10"><p className="font-mono text-[10px] text-ocre-texte">{pillar.number}</p><h3 className="mt-4 font-display text-3xl text-encre">{pillar.title}</h3><p className="mt-3 max-w-sm text-sm leading-6 text-graphite/70">{pillar.text}</p></article>)}</div>
        </div>
      </section>

      <section id="metier" className="bg-encre px-5 py-20 text-papier sm:px-8 lg:py-28">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl"><p className="font-mono text-[10px] uppercase tracking-[0.24em] text-ocre">Pensé pour le métier</p><h2 className="mt-3 font-display text-4xl leading-tight sm:text-5xl">De l’agent terrain au superviseur, <Accent>le même registre</Accent>, des vues adaptées.</h2></div>
          <div className="mt-14 grid gap-px overflow-hidden border border-papier/12 bg-papier/12 sm:grid-cols-2 lg:grid-cols-4">{proofItems.map(([title, text]) => <div key={title} className="bg-encre px-6 py-7 lg:px-7"><p className="font-display text-3xl">{title}</p><p className="mt-2 font-mono text-[9px] uppercase tracking-[0.16em] text-papier/50">{text}</p></div>)}</div>
          <div className="mt-14 grid gap-8 lg:grid-cols-3">
            <article className="border-t-2 border-ocre pt-5"><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ocre">Agent terrain</p><p className="mt-3 text-sm leading-6 text-papier/70">Saisir un dossier, vérifier une identité et enregistrer un mouvement sans quitter le geste métier.</p></article>
            <article className="border-t-2 border-papier/30 pt-5"><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-papier/70">Superviseur</p><p className="mt-3 text-sm leading-6 text-papier/70">Voir les signaux qui demandent une décision, comprendre le portefeuille et prioriser les revues.</p></article>
            <article className="border-t-2 border-tampon pt-5"><p className="font-mono text-[10px] uppercase tracking-[0.18em] text-papier/70">Conformité</p><p className="mt-3 text-sm leading-6 text-papier/70">Conserver les preuves, justifier l’arbitrage et disposer d’un historique auditable.</p></article>
          </div>
        </div>
      </section>

      <section id="preuve" className="bg-papier px-5 py-20 sm:px-8 lg:py-28">
        <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-end lg:gap-20">
          <div><p className="font-mono text-[10px] uppercase tracking-[0.24em] text-ocre-texte">La preuve reste visible</p><h2 className="mt-3 max-w-3xl font-display text-4xl leading-tight text-encre sm:text-5xl">Une décision sans trace est une décision difficile à défendre.</h2><p className="mt-5 max-w-2xl text-base leading-8 text-graphite/70">KORA relie le signal initial à la décision finale : données client, transaction, alerte, justification et audit restent dans la même histoire.</p></div>
          <div className="border-l-2 border-encre pl-6 sm:pl-8"><p className="font-display text-5xl text-encre">1 dossier.</p><p className="mt-1 font-display text-5xl text-encre"><span className="text-ocre">5</span> traces utiles.</p><p className="mt-5 font-mono text-[9px] uppercase tracking-[0.16em] text-graphite/50">Client · compte · transaction · alerte · audit</p></div>
        </div>
      </section>

      <section className="border-t border-encre/10 bg-papier-soutenu/60 px-5 py-16 sm:px-8 lg:py-20"><div className="mx-auto flex max-w-7xl flex-col gap-7 sm:flex-row sm:items-end sm:justify-between"><div><p className="font-mono text-[10px] uppercase tracking-[0.24em] text-ocre-texte">Espace professionnel</p><h2 className="mt-2 max-w-xl font-display text-4xl text-encre">Prêt à ouvrir le registre de décision ?</h2></div><button type="button" onClick={onEnterApp} className="shrink-0 rounded-sm bg-encre px-5 py-3.5 font-texte text-sm font-semibold text-papier transition-transform hover:-translate-y-0.5">Entrer dans KORA</button></div></section>
      <footer className="border-t border-encre/10 bg-papier px-5 py-8 sm:px-8"><div className="mx-auto flex max-w-7xl flex-col gap-2 sm:flex-row sm:items-center sm:justify-between"><p className="font-mono text-[9px] uppercase tracking-[0.2em] text-graphite/45">KORA · Registre de décision</p><p className="font-mono text-[9px] uppercase tracking-[0.14em] text-graphite/40">Vérifier · Décider · Tracer</p></div></footer>
    </main>
  )
}
