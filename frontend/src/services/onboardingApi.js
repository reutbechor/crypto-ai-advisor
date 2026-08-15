import { apiRequest } from './apiClient.js'


function authorizationHeader(token) {
  return {
    Authorization: `Bearer ${token}`,
  }
}

export function completeOnboarding(preferences, token) {
  return apiRequest('/api/onboarding', {
    method: 'POST',
    headers: authorizationHeader(token),
    body: JSON.stringify(preferences),
  })
}

export function getPreferences(token) {
  return apiRequest('/api/onboarding/preferences', {
    headers: authorizationHeader(token),
  })
}
