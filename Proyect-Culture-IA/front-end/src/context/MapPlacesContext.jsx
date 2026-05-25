import { createContext, useContext, useMemo, useState } from 'react'

const MapPlacesContext = createContext(null)

export function MapPlacesProvider({ children }) {
  const [highlightPlaces, setHighlightPlaces] = useState([])

  const value = useMemo(
    () => ({
      highlightPlaces,
      setHighlightPlaces,
      showPlacesOnMap: (places) => setHighlightPlaces(places || []),
      clearMapPlaces: () => setHighlightPlaces([]),
    }),
    [highlightPlaces]
  )

  return (
    <MapPlacesContext.Provider value={value}>
      {children}
    </MapPlacesContext.Provider>
  )
}

export function useMapPlaces() {
  const ctx = useContext(MapPlacesContext)
  if (!ctx) {
    throw new Error('useMapPlaces debe usarse dentro de MapPlacesProvider')
  }
  return ctx
}
