/**
 * T32 - Client API frontend centralise.
 * Point d'entree unique vers le backend FastAPI. Aucun composant ne doit
 * appeler fetch() directement en dehors de ce module.
 */

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'
const API_PREFIX = '/api/v1'

export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(status: number, detail: unknown) {
    const message =
      typeof detail === 'string'
        ? detail
        : typeof detail === 'object' && detail !== null && 'detail' in detail
          ? String((detail as { detail?: unknown }).detail ?? `Erreur API (${status})`)
          : `Erreur API (${status})`
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${API_PREFIX}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })

  if (!res.ok) {
    let detail: unknown
    try {
      detail = await res.json()
    } catch {
      detail = await res.text()
    }
    throw new ApiError(res.status, detail)
  }

  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

// ---- Clients ----

export type Client = {
  id: number
  first_name: string
  last_name: string
  email: string | null
  birth_date: string | null
  nationality: string | null
  risk_score: number
  is_pep: boolean
  is_sanctioned: boolean
  created_at: string
  updated_at: string
}

export type ClientCreateInput = {
  first_name: string
  last_name: string
  email?: string | null
  birth_date?: string | null
  nationality?: string | null
  is_pep: boolean
}

export function listClients(): Promise<Client[]> {
  return request<Client[]>('/clients')
}

export function getClient(id: number): Promise<Client> {
  return request<Client>(`/clients/${id}`)
}

export function createClient(input: ClientCreateInput): Promise<Client> {
  return request<Client>('/clients', { method: 'POST', body: JSON.stringify(input) })
}

// ---- Comptes ----

export type Account = {
  id: number
  client_id: number
  account_number: string
  balance: string
  currency: string
  status: string
  created_at: string
}

export function listAccounts(clientId?: number): Promise<Account[]> {
  const query = clientId !== undefined ? `?client_id=${clientId}` : ''
  return request<Account[]>(`/accounts${query}`)
}

// ---- Transactions ----

export type TransactionType = 'credit' | 'debit' | 'deposit' | 'transfer' | 'withdrawal'

export type Transaction = {
  id: number
  account_id: number
  amount: string
  currency: string
  transaction_type: TransactionType
  status: string
  counterparty_name: string | null
  counterparty_account: string | null
  counterparty_country: string | null
  timestamp: string
}

export type TransactionCreateInput = {
  account_id: number
  amount: number
  currency: string
  transaction_type: TransactionType
  counterparty_name?: string | null
  counterparty_account?: string | null
  counterparty_country?: string | null
}

export function listTransactions(): Promise<Transaction[]> {
  return request<Transaction[]>('/transactions')
}

export function createTransaction(input: TransactionCreateInput): Promise<Transaction> {
  return request<Transaction>('/transactions', { method: 'POST', body: JSON.stringify(input) })
}

// ---- Alertes ----

export type AlertStatus = 'OPEN' | 'VALIDATED' | 'REJECTED' | 'ESCALATED'
export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type Alert = {
  id: number
  alert_type: string
  severity: AlertSeverity
  status: AlertStatus
  description: string
  client_id: number | null
  transaction_id: number | null
  review_note: string | null
  reviewed_by: string | null
  reviewed_at: string | null
  created_at: string
}

export function listAlerts(): Promise<Alert[]> {
  return request<Alert[]>('/alerts')
}

export function reviewAlert(id: number, status: Exclude<AlertStatus, 'OPEN'>, reviewNote: string): Promise<Alert> {
  return request<Alert>(`/alerts/${id}/review`, {
    method: 'PUT',
    body: JSON.stringify({ status, review_note: reviewNote }),
  })
}
