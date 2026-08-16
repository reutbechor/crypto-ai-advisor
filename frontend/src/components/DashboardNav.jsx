function DashboardNav({ activeSection, items, onNavigate }) {
  return (
    <nav className="dashboard-nav" aria-label="Dashboard sections">
      <div className="dashboard-nav-list">
        {items.map((item) => (
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
