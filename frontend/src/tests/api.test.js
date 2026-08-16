import { afterEach, expect, it, vi } from 'vitest'
import { getDashboard } from '../services/dashboardApi.js'
import { saveFeedback } from '../services/feedbackApi.js'


afterEach(() => {
  vi.unstubAllGlobals()
})


it('sends authenticated dashboard and feedback requests without client-owned user_id', async () => {
  const fetchMock = vi.fn()
    .mockResolvedValueOnce({ ok: true, json: async () => ({ user: { id: 7 } }) })
    .mockResolvedValueOnce({ ok: true, json: async () => ({ vote: 'up' }) })
  vi.stubGlobal('fetch', fetchMock)

  await getDashboard('dashboard-token')
  await saveFeedback('feedback-token', {
    content_type: 'news',
    content_id: 'btc-001',
    vote: 'up',
  })

  const [dashboardUrl, dashboardOptions] = fetchMock.mock.calls[0]
  const [feedbackUrl, feedbackOptions] = fetchMock.mock.calls[1]
  expect(dashboardUrl).toMatch(/\/api\/dashboard$/)
  expect(dashboardOptions.headers.Authorization).toBe('Bearer dashboard-token')
  expect(feedbackUrl).toMatch(/\/api\/feedback$/)
  expect(feedbackOptions.method).toBe('PUT')
  expect(feedbackOptions.headers.Authorization).toBe('Bearer feedback-token')
  expect(JSON.parse(feedbackOptions.body)).toEqual({
    content_type: 'news',
    content_id: 'btc-001',
    vote: 'up',
  })
  expect(feedbackOptions.body).not.toContain('user_id')
})

