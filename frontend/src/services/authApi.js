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

export async function signupUser(userData) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    })
  } catch {
    throw new ApiError('Unable to reach the server.', 0)
  }

  const responseBody = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(responseBody?.detail || 'Request failed.', response.status)
  }

  return responseBody
}
