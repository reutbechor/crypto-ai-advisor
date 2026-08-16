import { describe, expect, it } from 'vitest'
import {
  getDashboardNavigationItems,
  getOrderedDashboardSections,
} from '../utils/dashboardSections.js'


describe('dashboard section ordering', () => {
  it('honors valid preference order and safely fills missing sections', () => {
    expect(getOrderedDashboardSections(['fun', 'coin_prices']).map(({ id }) => id))
      .toEqual(['meme', 'market', 'news', 'ai-insight'])
    expect(getOrderedDashboardSections(['ai_insights', 'market_news']).map(({ id }) => id))
      .toEqual(['ai-insight', 'news', 'market', 'meme'])
    expect(getOrderedDashboardSections([]).map(({ id }) => id))
      .toEqual(['market', 'news', 'ai-insight', 'meme'])
    expect(getOrderedDashboardSections(['unknown', 'fun', 'fun', 'coin_prices']).map(({ id }) => id))
      .toEqual(['meme', 'market', 'news', 'ai-insight'])
    expect(getDashboardNavigationItems(['fun'])[0])
      .toEqual({ id: 'overview', label: 'Overview' })
  })
})

