import { useEffect, useMemo, useState } from 'react'
import { Popup } from 'react-leaflet'
import { getPlaceDetail, getPlaceDetailBff } from '../../services/placesService'
import { fetchWikiImage, getImageCandidates } from '../../utils/imageUrl'

function PlaceMapPopup({
  placeId,
  fallbackName,
  fallbackCategory,
  distanceKm,
  prefetched = null,
}) {
  const [detail, setDetail] = useState(prefetched)
  const [loading, setLoading] = useState(!prefetched)
  const [imageIndex, setImageIndex] = useState(0)
  const [wikiImage, setWikiImage] = useState('')
  const [primaryExhausted, setPrimaryExhausted] = useState(false)

  useEffect(() => {
    setImageIndex(0)
    setWikiImage('')
    setPrimaryExhausted(false)

    let active = true
    setLoading(true)
    setDetail(prefetched || null)

    const loadDetail = async () => {
      try {
        const data = await getPlaceDetailBff(placeId)
        if (active) setDetail((current) => ({ ...current, ...data }))
      } catch {
        try {
          const data = await getPlaceDetail(placeId)
          if (active) setDetail((current) => ({ ...current, ...data }))
        } catch {
          if (active && !prefetched) setDetail(null)
        }
      } finally {
        if (active) setLoading(false)
      }
    }

    loadDetail()

    return () => {
      active = false
    }
  }, [
    placeId,
    prefetched?.name,
    prefetched?.category,
    prefetched?.description,
    prefetched?.imagelink,
  ])

  const name = detail?.name || fallbackName
  const category = detail?.category || fallbackCategory
  const description = detail?.description || 'Sin descripción disponible.'
  const imageCandidates = useMemo(() => {
    const candidates = getImageCandidates(detail?.imagelink)
    const raw = detail?.imagelink?.trim()
    if (raw && !candidates.includes(raw)) {
      candidates.push(raw)
    }
    return candidates
  }, [detail?.imagelink])
  const hasPrimaryCandidates = imageCandidates.length > 0
  const primaryImage =
    hasPrimaryCandidates && !primaryExhausted
      ? (imageCandidates[imageIndex] || '')
      : ''
  const imageSrc = primaryImage || wikiImage
  const showImage = Boolean(imageSrc)

  useEffect(() => {
    if (loading) return undefined

    const placeName = detail?.name || fallbackName
    if (!placeName) return undefined

    let active = true
    fetchWikiImage(placeName, detail?.imagelink).then((url) => {
      if (active && url) setWikiImage(url)
    })

    return () => {
      active = false
    }
  }, [loading, detail?.name, detail?.imagelink, fallbackName, placeId])

  const handleImageError = () => {
    if (imageIndex + 1 < imageCandidates.length) {
      setImageIndex((current) => current + 1)
      return
    }
    setPrimaryExhausted(true)
  }

  return (
    <Popup maxWidth={300} minWidth={260} className="place-map-popup-wrapper">
      <div className="place-map-popup">
        {showImage && (
          <img
            key={imageSrc}
            src={imageSrc}
            alt={name}
            referrerPolicy="no-referrer"
            loading="lazy"
            onError={handleImageError}
            className="place-map-popup-image"
          />
        )}
        <strong className="place-map-popup-title">{name}</strong>
        {category && <span className="place-map-popup-category">{category}</span>}
        {distanceKm != null && (
          <span className="place-map-popup-distance">📏 {distanceKm} km</span>
        )}
        {loading && !description && (
          <p className="place-map-popup-loading">Cargando detalle...</p>
        )}
        <p className="place-map-popup-description">{description}</p>
      </div>
    </Popup>
  )
}

export default PlaceMapPopup
