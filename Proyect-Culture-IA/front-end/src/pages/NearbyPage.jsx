// src/pages/NearbyPage.jsx
import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import Header from '../components/layout/Header'
import { getNearbyPlaces, getDistance } from '../services/geoService'
import PlaceMapPopup from '../components/map/PlaceMapPopup'
import { BOGOTA_CENTER, isInColombia } from '../utils/colombia'
import { API } from '../config/api'
import { fetchJson } from '../utils/httpClient'

// Fix ícono Leaflet con Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const nearbyIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

const userIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})

const DEFAULT_CENTER = [BOGOTA_CENTER.lat, BOGOTA_CENTER.lng]
const MAX_RADIUS_KM = 100

// Componente para re-centrar el mapa cuando cambia la posición
function RecenterMap({ position }) {
  const map = useMap()
  useEffect(() => {
    if (position) {
      map.flyTo(position, 14, { duration: 1.2 })
    }
  }, [map, position])
  return null
}

function NearbyPage() {
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [radiusKm, setRadiusKm] = useState(5)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [locationStatus, setLocationStatus] = useState('idle')
  // idle | requesting | granted | denied

  const [selectedOrigin, setSelectedOrigin] = useState(null)
  const [selectedDestination, setSelectedDestination] = useState(null)
  const [distanceResult, setDistanceResult] = useState(null)
  const [distanceLoading, setDistanceLoading] = useState(false)
  const [distanceError, setDistanceError] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [recLoading, setRecLoading] = useState(false)

  // ── Al montar la página: detectar ubicación (sin buscar automáticamente) ──
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationStatus('denied')
      return
    }

    setLocationStatus('requesting')

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const userLat = pos.coords.latitude
        const userLng = pos.coords.longitude

        if (isInColombia(userLat, userLng)) {
          setLat(userLat.toFixed(6))
          setLng(userLng.toFixed(6))
        } else {
          setLat(DEFAULT_CENTER[0].toFixed(6))
          setLng(DEFAULT_CENTER[1].toFixed(6))
        }
        setLocationStatus('granted')
      },
      () => {
        setLocationStatus('denied')
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    )
  }, [])

  // ── Buscar manualmente (formulario) ──
  const handleSearch = async (e) => {
    e.preventDefault()
    setError('')
    setResults(null)
    setDistanceResult(null)
    setSelectedOrigin(null)
    setSelectedDestination(null)

    const parsedLat = parseFloat(lat)
    const parsedLng = parseFloat(lng)

    if (isNaN(parsedLat) || isNaN(parsedLng)) {
      setError('Ingresa coordenadas válidas')
      return
    }

    if (!isInColombia(parsedLat, parsedLng)) {
      setError('Las coordenadas deben estar dentro de Colombia')
      return
    }

    const safeRadius = Math.min(Math.max(parseFloat(radiusKm), 0.5), MAX_RADIUS_KM)

    try {
      setLoading(true)

      // Sincronizar puntos geográficos
      try {
        await fetch(API.gateway('v1_geo', 'geo/cerca'))
      } catch (err) {
        console.warn('Advertencia: No se pudo sincronizar puntos', err)
      }

      const data = await getNearbyPlaces(parsedLat, parsedLng, safeRadius)
      setResults(data)
    } catch {
      setError('No se pudo conectar con el servicio. Verifica que el backend esté activo.')
    } finally {
      setLoading(false)
    }
  }

  // ── Usar mi ubicación actual (botón manual) ──
  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setError('Tu navegador no soporta geolocalización')
      return
    }
    setLocationStatus('requesting')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const userLat = pos.coords.latitude
        const userLng = pos.coords.longitude

        if (isInColombia(userLat, userLng)) {
          setLat(userLat.toFixed(6))
          setLng(userLng.toFixed(6))
        } else {
          setLat(DEFAULT_CENTER[0].toFixed(6))
          setLng(DEFAULT_CENTER[1].toFixed(6))
          setError('Tu ubicación está fuera de Colombia. Usando Bogotá como referencia.')
        }
        setLocationStatus('granted')
      },
      () => {
        setLocationStatus('denied')
        setError('No se pudo obtener tu ubicación. Ingresa las coordenadas manualmente.')
      }
    )
  }

  // ── Calcular distancia ──
  const handleRecommendations = async () => {
    const parsedLat = parseFloat(lat)
    const parsedLng = parseFloat(lng)
    if (isNaN(parsedLat) || isNaN(parsedLng)) {
      setError('Ingresa coordenadas válidas para obtener recomendaciones')
      return
    }
    try {
      setRecLoading(true)
      const params = new URLSearchParams({
        lat: String(parsedLat),
        lng: String(parsedLng),
        max_distancia: String(radiusKm),
      })
      const payload = await fetchJson(
        `${API.bff.recommendations}?${params.toString()}`,
        { errorMessage: 'No se pudieron obtener recomendaciones' }
      )
      const data = Array.isArray(payload) ? payload : payload?.data ?? []
      setRecommendations(data)
    } catch {
      setError('No se pudieron cargar las recomendaciones')
    } finally {
      setRecLoading(false)
    }
  }

  const handleCalculateDistance = async () => {
    if (!selectedOrigin || !selectedDestination) {
      setDistanceError('Selecciona dos lugares de la lista')
      return
    }
    if (selectedOrigin === selectedDestination) {
      setDistanceError('Los dos lugares deben ser diferentes')
      return
    }
    setDistanceError('')
    setDistanceResult(null)
    try {
      setDistanceLoading(true)
      const data = await getDistance(selectedOrigin, selectedDestination)
      setDistanceResult(data)
    } catch {
      setDistanceError('No se pudo calcular la distancia')
    } finally {
      setDistanceLoading(false)
    }
  }

  const mapCenter = results
    ? [results.reference_point.lat, results.reference_point.lng]
    : DEFAULT_CENTER

  const nearbyPlaces = results?.nearby_places ?? []

  return (
    <>
      <Header />

      <main className="page">
        <section className="hero">
          <div>
            <p className="eyebrow">Exploración geográfica</p>
            <h1>Lugares cercanos</h1>
            <p className="hero-text">
              {locationStatus === 'requesting' && '📍 Detectando tu ubicación...'}
              {locationStatus === 'granted' && '📍 Mostrando lugares cercanos a tu ubicación actual.'}
              {locationStatus === 'denied' && '📍 Permiso de ubicación denegado. Ingresa las coordenadas manualmente.'}
              {locationStatus === 'idle' && 'Descubre sitios culturales cercanos a ti, ordenados por distancia.'}
            </p>
          </div>
        </section>

        {/* Formulario — siempre visible como respaldo */}
        <section className="section">
          <div className="section-head">
            <h2>Buscar por proximidad</h2>
            <p>Tu ubicación se detecta automáticamente. También puedes ingresar coordenadas manualmente.</p>
          </div>

          <form onSubmit={handleSearch} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
              <input
                type="number"
                step="any"
                placeholder="Latitud (ej: 4.6000)"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                required
                style={{ flex: 1, minWidth: '140px', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }}
              />
              <input
                type="number"
                step="any"
                placeholder="Longitud (ej: -74.0750)"
                value={lng}
                onChange={(e) => setLng(e.target.value)}
                required
                style={{ flex: 1, minWidth: '140px', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }}
              />
              <div style={{ flex: 1, minWidth: '160px' }}>
                <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--muted)', marginBottom: '4px' }}>
                  Radio: <strong>{radiusKm} km</strong>
                </label>
                <input
                  type="range"
                  min="1"
                  max={MAX_RADIUS_KM}
                  step="0.5"
                  value={radiusKm}
                  onChange={(e) => setRadiusKm(parseFloat(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--primary)' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={useMyLocation}
                style={{
                  padding: '10px 22px',
                  background: 'transparent',
                  color: 'var(--primary)',
                  border: '1.5px solid var(--primary)',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                {locationStatus === 'requesting' ? '📍 Detectando...' : '📍 Usar mi ubicación'}
              </button>
              <button
                type="submit"
                className="btn-primary"
                disabled={loading}
              >
                {loading ? 'Buscando...' : 'Buscar lugares cercanos'}
              </button>
              <button
                type="button"
                className="btn-primary"
                onClick={handleRecommendations}
                disabled={recLoading}
              >
                {recLoading ? 'Recomendando...' : 'Ver recomendaciones'}
              </button>
            </div>
          </form>

          {error && <p className="error-text" style={{ marginTop: '12px' }}>{error}</p>}
        </section>

        {/* Mapa */}
        <section className="section">
          <div className="section-head">
            <h2>Mapa</h2>
            {loading && <p className="section-note">Buscando lugares cercanos...</p>}
            {results && (
              <p>
                {nearbyPlaces.length > 0
                  ? `${nearbyPlaces.length} lugar(es) encontrado(s) en un radio de ${results.radius_km} km`
                  : `Sin resultados en un radio de ${results.radius_km} km`}
              </p>
            )}
          </div>

          <div className="map-wrapper">
            <MapContainer
              center={mapCenter}
              zoom={13}
              style={{ height: '460px', width: '100%' }}
              key={`${mapCenter[0]}-${mapCenter[1]}`}
            >
              <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              <RecenterMap position={results ? [results.reference_point.lat, results.reference_point.lng] : null} />

              {results && (
                <>
                  <Marker
                    position={[results.reference_point.lat, results.reference_point.lng]}
                    icon={userIcon}
                  >
                    <Popup>📍 Tu ubicación</Popup>
                  </Marker>
                  <Circle
                    center={[results.reference_point.lat, results.reference_point.lng]}
                    radius={results.radius_km * 1000}
                    pathOptions={{ color: '#0f766e', fillColor: '#0f766e', fillOpacity: 0.07 }}
                  />
                </>
              )}

              {nearbyPlaces.map((place) => (
                <Marker
                  key={place.place_id}
                  position={[place.latitude, place.longitude]}
                  icon={nearbyIcon}
                >
                  <PlaceMapPopup
                    placeId={place.place_id}
                    fallbackName={place.name || 'Lugar sin nombre'}
                    fallbackCategory={place.category}
                    distanceKm={place.distance_km}
                    prefetched={{
                      name: place.name,
                      category: place.category,
                      description: place.description,
                      imagelink: place.imagelink,
                    }}
                  />
                </Marker>
              ))}
            </MapContainer>
          </div>
        </section>

        {/* Lista de resultados */}
        {results && (
          <section className="section">
            <div className="section-head">
              <h2>Lista de lugares cercanos</h2>
              <p>Ordenados de menor a mayor distancia</p>
            </div>

            {nearbyPlaces.length === 0 ? (
              <p className="section-note">
                No se encontraron lugares en ese radio. Intenta aumentar el radio de búsqueda.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {nearbyPlaces.map((place, idx) => (
                  <div
                    key={place.place_id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                      padding: '16px',
                      background: 'var(--card)',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)',
                      boxShadow: 'var(--shadow)'
                    }}
                  >
                    <div style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--primary)', minWidth: '36px' }}>
                      #{idx + 1}
                    </div>
                    <div style={{ flex: 1 }}>
                      <strong>{place.name || `Lugar ${idx + 1}`}</strong>
                      {place.category && (
                        <span className="badge" style={{ marginLeft: '8px' }}>{place.category}</span>
                      )}
                      {place.address && (
                        <p style={{ color: 'var(--muted)', fontSize: '0.85rem', margin: '2px 0' }}>{place.address}</p>
                      )}
                      <small style={{ color: 'var(--muted)', fontSize: '0.78rem' }}>
                        lat {place.latitude.toFixed(5)}, lng {place.longitude.toFixed(5)}
                      </small>
                    </div>
                    <div>
                      <span style={{
                        background: 'var(--accent)',
                        color: 'var(--primary)',
                        padding: '6px 12px',
                        borderRadius: '20px',
                        fontWeight: '700',
                        fontSize: '0.9rem'
                      }}>
                        {place.distance_km} km
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {recommendations.length > 0 && (
          <section className="section">
            <div className="section-head">
              <h2>Recomendaciones para ti</h2>
              <p>Priorizadas por relevancia cultural y cercanía</p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {recommendations.slice(0, 5).map((item, idx) => (
                <div
                  key={item.place_id}
                  style={{
                    padding: '16px',
                    background: 'var(--card)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                >
                  <strong>#{idx + 1} {item.name}</strong>
                  <span className="badge" style={{ marginLeft: '8px' }}>{item.category}</span>
                  <p style={{ color: 'var(--muted)', fontSize: '0.85rem', margin: '6px 0' }}>
                    Relevancia: {item.relevance_index} · {item.distance_km} km
                  </p>
                  {item.explanation?.[0] && (
                    <p style={{ fontSize: '0.85rem', margin: 0 }}>{item.explanation[0]}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Calculadora de distancia */}
        {nearbyPlaces.length >= 2 && (
          <section className="section">
            <div className="section-head">
              <h2>Calcular distancia entre dos lugares</h2>
              <p>Selecciona un origen y un destino de los resultados anteriores</p>
            </div>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
              padding: '20px',
              background: 'var(--card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius)'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', fontSize: '0.9rem' }}>
                    Lugar de origen
                  </label>
                  <select
                    value={selectedOrigin || ''}
                    onChange={(e) => setSelectedOrigin(e.target.value)}
                    style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }}
                  >
                    <option value="">-- Selecciona origen --</option>
                    {nearbyPlaces.map((place, idx) => (
                      <option key={place.place_id} value={place.place_id}>
                        {place.name || `Lugar ${idx + 1}`} ({place.distance_km} km)
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', fontSize: '0.9rem' }}>
                    Lugar de destino
                  </label>
                  <select
                    value={selectedDestination || ''}
                    onChange={(e) => setSelectedDestination(e.target.value)}
                    style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }}
                  >
                    <option value="">-- Selecciona destino --</option>
                    {nearbyPlaces.map((place, idx) => (
                      <option key={place.place_id} value={place.place_id}>
                        {place.name || `Lugar ${idx + 1}`} ({place.distance_km} km)
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                className="btn-primary"
                onClick={handleCalculateDistance}
                disabled={distanceLoading}
                style={{ alignSelf: 'flex-start' }}
              >
                {distanceLoading ? 'Calculando...' : 'Calcular distancia'}
              </button>

              {distanceError && <p className="error-text">{distanceError}</p>}

              {distanceResult && (
                <div style={{
                  padding: '16px',
                  background: 'var(--accent)',
                  borderRadius: '12px',
                  textAlign: 'center'
                }}>
                  <p style={{ margin: 0 }}>
                    De <strong>{distanceResult.origin_name || distanceResult.place_id_origin}</strong>
                    {' '}a{' '}
                    <strong>{distanceResult.destination_name || distanceResult.place_id_destination}</strong>
                  </p>
                  <p style={{ fontSize: '1.8rem', fontWeight: '800', color: 'var(--primary)', margin: '8px 0 0' }}>
                    📏 {distanceResult.distance_km} km
                  </p>
                </div>
              )}
            </div>
          </section>
        )}
      </main>
    </>
  )
}

export default NearbyPage