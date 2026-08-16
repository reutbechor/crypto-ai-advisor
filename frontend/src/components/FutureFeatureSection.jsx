function FutureFeatureSection({ id, eyebrow, title, description, detail, variant }) {
  return (
    <section
      className={`dashboard-future dashboard-future--${variant}`}
      id={id}
      aria-labelledby={`${id}-title`}
      tabIndex="-1"
    >
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h2 id={`${id}-title`}>{title}</h2>
        <p>{description}</p>
        <span>{detail}</span>
      </div>
      <div className="future-visual" aria-hidden="true">
        <span />
        <span />
        <span />
      </div>
    </section>
  )
}

export default FutureFeatureSection
