const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export async function apiRequest(path, options = {}) {
  let response
  const { headers, ...fetchOptions } = options

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    })
  } catch {
    throw new ApiError('Unable to reach the server.', 0)
  }

  const responseBody = await response.json().catch(() => null)

  if (!response.ok) {
    const message =
      typeof responseBody?.detail === 'string'
        ? responseBody.detail
        : 'Request failed.'
    throw new ApiError(message, response.status)
  }

  return responseBody
}
