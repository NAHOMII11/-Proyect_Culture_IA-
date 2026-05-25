export const COLOMBIA_BOUNDS = {
  latMin: -4.3,
  latMax: 13.5,
  lngMin: -81.8,
  lngMax: -66.8,
}

export const BOGOTA_CENTER = { lat: 4.6097, lng: -74.0817 }

export function isInColombia(lat, lng) {
  if (lat == null || lng == null) return false
  const la = Number(lat)
  const lo = Number(lng)
  if (Number.isNaN(la) || Number.isNaN(lo)) return false
  return (
    la >= COLOMBIA_BOUNDS.latMin &&
    la <= COLOMBIA_BOUNDS.latMax &&
    lo >= COLOMBIA_BOUNDS.lngMin &&
    lo <= COLOMBIA_BOUNDS.lngMax
  )
}

export function filterPlacesInColombia(places = []) {
  return places.filter((place) =>
    isInColombia(place.latitude ?? place.lat, place.longitude ?? place.lng)
  )
}
