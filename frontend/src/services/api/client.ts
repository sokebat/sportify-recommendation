import { ApiError } from './errors'

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

interface RequestOptions {
  /** Lets callers (e.g. React Query) cancel a request that's gone stale. */
  signal?: AbortSignal
}

async function request<T>(endpoint: string, init: RequestInit, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    signal: options.signal,
    ...init,
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new ApiError(response.status, errorBody.detail || `Request failed with status ${response.status}`)
  }

  return response.json()
}

export function get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  return request<T>(endpoint, { method: 'GET' }, options)
}

export function post<T>(endpoint: string, body: unknown, options?: RequestOptions): Promise<T> {
  return request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }, options)
}
