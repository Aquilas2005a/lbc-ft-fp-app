import type { ReactNode } from 'react'

/**
 * Systeme de composants de formulaire partage entre T27 (onboarding client)
 * et T29 (transaction), pour ne pas reinventer un style par ecran.
 */
export function FieldError({ show, message = 'Ce champ manque pour ouvrir le dossier.' }: { show: boolean; message?: string }) {
  if (!show) return null
  return <p className="mt-1 font-mono text-[10px] text-tampon">{message}</p>
}

export function FieldLabel({ htmlFor, children, hint }: { htmlFor: string; children: ReactNode; hint?: string }) {
  return (
    <label htmlFor={htmlFor} className="block text-sm font-medium text-graphite/85">
      {children}
      {hint && <span className="ml-1 font-mono text-[10px] font-normal normal-case text-graphite/40">{hint}</span>}
    </label>
  )
}

export function FormActions({ children }: { children: ReactNode }) {
  return <div className="flex flex-wrap items-center gap-3 border-t border-encre/12 pt-5">{children}</div>
}

export function PrimaryButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className="rounded-sm bg-ocre px-5 py-2.5 font-texte text-sm font-semibold text-encre shadow-sm transition-transform hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:translate-y-0"
    >
      {children}
    </button>
  )
}

export function SecondaryButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className="rounded-sm border border-encre/20 px-5 py-2.5 font-texte text-sm text-graphite/70 hover:border-encre/40 hover:text-encre"
    >
      {children}
    </button>
  )
}
