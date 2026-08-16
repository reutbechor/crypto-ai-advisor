import { useEffect, useState } from 'react'


function MemeImage({ alt, className = '', src }) {
  const [hasFailed, setHasFailed] = useState(false)

  useEffect(() => {
    setHasFailed(false)
  }, [src])

  if (!src || hasFailed) {
    return (
      <div className={`meme-image-fallback ${className}`} role="img" aria-label={alt || 'Crypto meme unavailable'}>
        <span aria-hidden="true">:)</span>
        <strong>Image temporarily unavailable</strong>
      </div>
    )
  }

  return (
    <img
      className={className}
      src={src}
      alt={alt}
      loading="lazy"
      onError={() => setHasFailed(true)}
    />
  )
}

export default MemeImage
