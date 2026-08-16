import { apiRequest } from './apiClient.js'


export function saveFeedback(token, feedback) {
  return apiRequest('/api/feedback', {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(feedback),
  })
}
