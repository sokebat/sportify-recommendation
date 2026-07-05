/** Thrown for any non-2xx API response, carrying enough detail for callers
 * to branch on it (e.g. show a 404 differently from a 500) instead of just
 * pattern-matching a generic Error's message string. */
export class ApiError extends Error {
  readonly status: number
  readonly detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }

  get isNotFound() {
    return this.status === 404
  }
}
