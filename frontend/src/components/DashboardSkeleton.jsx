function DashboardSkeleton() {
  return (
    <div className="dashboard-loading" aria-live="polite" aria-busy="true">
      <span className="sr-only">Loading your dashboard...</span>
      <div className="skeleton-block skeleton-block--welcome" />
      <div className="skeleton-heading" />
      <div className="market-grid">
        {[1, 2, 3].map((item) => (
          <div className="skeleton-market-card" key={item} />
        ))}
      </div>
    </div>
  )
}

export default DashboardSkeleton
