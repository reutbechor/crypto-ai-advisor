const dailyDateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
  timeZone: 'UTC',
})

function formatDailyDate(value) {
  const [year, month, day] = value.split('-').map(Number)
  return dailyDateFormatter.format(new Date(Date.UTC(year, month - 1, day)))
}

function DailyDateLabel({ date, label }) {
  if (!date) {
    return null
  }

  return (
    <span className="daily-date-label">
      <strong>{label}</strong>
      <span aria-hidden="true">&middot;</span>
      <time dateTime={date}>{formatDailyDate(date)}</time>
    </span>
  )
}

export default DailyDateLabel
