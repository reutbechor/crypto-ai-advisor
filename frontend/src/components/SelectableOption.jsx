function SelectableOption({ label, description, meta, selected, onSelect }) {
  return (
    <button
      className={`selection-option${selected ? ' selection-option--selected' : ''}`}
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
    >
      <span className="selection-option-copy">
        <span className="selection-option-title">{label}</span>
        {description && <span className="selection-option-description">{description}</span>}
      </span>
      <span className="selection-option-meta" aria-hidden="true">
        {selected ? '✓' : meta}
      </span>
    </button>
  )
}

export default SelectableOption
