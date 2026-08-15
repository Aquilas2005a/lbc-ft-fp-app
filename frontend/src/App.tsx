/**
 * T24 - Point d'entree minimal du frontend.
 * Objectif de cette tache : confirmer que Vite + React + Tailwind
 * demarrent avec les tokens du design "Registre de decision" charges
 * correctement (palette, typographie, focus clavier) via les classes
 * utilitaires Tailwind generees par @theme (pas des var() arbitraires,
 * pour verifier reellement le cablage du theme).
 *
 * La navigation, le layout et le hero complets sont traites en T25.
 */
function App() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 bg-papier px-6 text-center">
      <span className="font-mono text-xs uppercase tracking-widest text-encre">
        KORA / Conformite
      </span>
      <h1 className="font-display text-4xl text-encre md:text-5xl">
        Registre de decision
      </h1>
      <p className="max-w-md text-graphite">
        Socle Vite + React + Tailwind initialise. Palette, typographie et
        focus clavier sont en place pour construire la navigation en T25.
      </p>

      <div className="flex flex-wrap justify-center gap-3">
        <span className="inline-flex items-center gap-2 rounded-sm border-2 border-tampon px-3 py-1 font-mono text-xs font-semibold text-tampon">
          A REVOIR
        </span>
        <span className="inline-flex items-center gap-2 rounded-sm border-2 border-vert px-3 py-1 font-mono text-xs font-semibold text-vert">
          CONFORME
        </span>
        <span className="inline-flex items-center gap-2 rounded-sm border-2 border-ocre-texte px-3 py-1 font-mono text-xs font-semibold text-ocre-texte">
          150 000 XOF
        </span>
      </div>

      <button
        type="button"
        className="mt-4 rounded-sm bg-encre px-4 py-2 font-texte text-sm font-medium text-papier transition-colors hover:bg-encre-clair"
      >
        Ouvrir la revue
      </button>
    </main>
  )
}

export default App
