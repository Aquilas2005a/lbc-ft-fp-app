/** Fonctions utilitaires de style, separees des composants pour le Fast Refresh. */
export function inputClasses(hasError: boolean) {
  return `w-full rounded-sm border bg-papier px-3 py-2.5 font-mono text-sm text-encre placeholder:text-graphite/35 focus:outline-none focus:ring-1 ${
    hasError ? 'border-tampon focus:border-tampon focus:ring-tampon' : 'border-encre/20 focus:border-encre focus:ring-encre'
  }`
}
