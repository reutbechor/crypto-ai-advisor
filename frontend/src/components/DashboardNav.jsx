const navigationItems = [
  { id: 'overview', label: 'Overview' },
  { id: 'market', label: 'Market' },
  { id: 'news', label: 'News' },
  { id: 'ai-insight', label: 'AI Insight' },
  { id: 'meme', label: 'Meme' },
]

function DashboardNav({ activeSection, onNavigate }) {
  return (
    <nav className="dashboard-nav" aria-label="Dashboard sections">
      <div className="dashboard-nav-list">
        {navigationItems.map((item) => (
          <button
            className={activeSection === item.id ? 'dashboard-nav-item--active' : ''}
            type="button"
            aria-current={activeSection === item.id ? 'location' : undefined}
            onClick={() => onNavigate(item.id)}
            key={item.id}
          >
            {item.label}
          </button>
        ))}
      </div>
    </nav>
  )
}

export default DashboardNav
