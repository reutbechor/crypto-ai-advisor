import { apiRequest } from './apiClient.js'


export function getDashboard(token) {
  return apiRequest('/api/dashboard', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
}
