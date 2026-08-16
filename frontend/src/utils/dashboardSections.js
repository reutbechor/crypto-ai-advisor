export const dashboardSectionDefinitions = [
  { id: 'market', preference: 'coin_prices', label: 'Market' },
  { id: 'news', preference: 'market_news', label: 'News' },
  { id: 'ai-insight', preference: 'ai_insights', label: 'AI Insight' },
  { id: 'meme', preference: 'fun', label: 'Meme' },
]

const sectionByPreference = new Map(
  dashboardSectionDefinitions.map((section) => [section.preference, section]),
)

export function getOrderedDashboardSections(contentPreferences) {
  const preferences = Array.isArray(contentPreferences) ? contentPreferences : []
  const selectedSections = []
  const selectedIds = new Set()

  preferences.forEach((preference) => {
    const section = sectionByPreference.get(preference)
    if (section && !selectedIds.has(section.id)) {
      selectedSections.push(section)
      selectedIds.add(section.id)
    }
  })

  return [
    ...selectedSections,
    ...dashboardSectionDefinitions.filter((section) => !selectedIds.has(section.id)),
  ]
}

export function getDashboardNavigationItems(contentPreferences) {
  return [
    { id: 'overview', label: 'Overview' },
    ...getOrderedDashboardSections(contentPreferences).map(({ id, label }) => ({ id, label })),
  ]
}
