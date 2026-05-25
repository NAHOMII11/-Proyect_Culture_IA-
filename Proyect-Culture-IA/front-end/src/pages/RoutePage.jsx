import { useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import Header from '../components/layout/Header'
import { generateRoute } from '../services/routeService'

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const userIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
})

const stopIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34],
})

const CATEGORIES = ['Museo', 'Monumento', 'Teatro', 'Cultural', 'Iglesia', 'Parque']
const DEFAULT_CENTER = [4.6097, -74.0817]

function RoutePage() {
  const [userLat, setUserLat] = useState('4.6097')
  const [userLng, setUserLng] = useState('-74.0817')
  const [availableTime, setAvailableTime] = useState(180)
  const [maxPlaces, setMaxPlaces] = useState(4)
  const [selectedCategories, setSelectedCategories] = useState([])
  const [route, setRoute] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const toggleCategory = (cat) => {
    setSelectedCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    )
  }

  const useMyLocation = () => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition((pos) => {
      setUserLat(pos.coords.latitude.toFixed(6))
      setUserLng(pos.coords.longitude.toFixed(6))
    })
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setError('')
    setRoute(null)
    const parsedLat = parseFloat(userLat)
    const parsedLng = parseFloat(userLng)
    if (isNaN(parsedLat) || isNaN(parsedLng)) {
      setError('Ingresa coordenadas válidas')
      return
    }
    try {
      setLoading(true)
      const data = await generateRoute({
        user_lat: parsedLat,
        user_lng: parsedLng,
        preferred_categories: selectedCategories,
        available_time_minutes: availableTime,
        max_places: maxPlaces,
      })
      setRoute(data)
    } catch {
      setError('No se pudo generar la ruta. Verifica que el backend esté activo.')
    } finally {
      setLoading(false)
    }
  }

  const mapCenter = [parseFloat(userLat) || DEFAULT_CENTER[0], parseFloat(userLng) || DEFAULT_CENTER[1]]

  const polylinePoints = route
    ? [
        mapCenter,
        ...route.places
          .filter((p) => p.latitude && p.longitude)
          .map((p) => [p.latitude, p.longitude]),
      ]
    : []

  return (
    <>
      <Header />
      <main className="page">

        <section className="hero">
          <div>
            <p className="eyebrow">Planificación inteligente</p>
            <h1>Generar ruta cultural</h1>
            <p className="hero-text">
              El sistema selecciona los mejores lugares según tu tiempo disponible,
              combinando score cultural y proximidad geográfica.
            </p>
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <h2>Configurar ruta</h2>
            <p>Define tu punto de partida y preferencias</p>
          </div>

          <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div style={{ flex: 1, minWidth: '140px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '6px' }}>Latitud</label>
                <input type="number" step="any" value={userLat} onChange={(e) => setUserLat(e.target.value)} required
                  style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }} />
              </div>
              <div style={{ flex: 1, minWidth: '140px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '6px' }}>Longitud</label>
                <input type="number" step="any" value={userLng} onChange={(e) => setUserLng(e.target.value)} required
                  style={{ width: '100%', padding: '10px 14px', border: '1px solid var(--border)', borderRadius: '10px' }} />
              </div>
              <button type="button" onClick={useMyLocation}
                style={{ padding: '10px 20px', background: 'transparent', color: 'var(--primary)', border: '1.5px solid var(--primary)', borderRadius: '10px', cursor: 'pointer', fontWeight: '600', whiteSpace: 'nowrap' }}>
                📍 Mi ubicación
              </button>
            </div>

            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '6px' }}>
                  Tiempo disponible: <strong>{availableTime} min</strong>
                </label>
                <input type="range" min="30" max="480" step="15" value={availableTime}
                  onChange={(e) => setAvailableTime(parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--primary)' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--muted)' }}>
                  <span>30 min</span><span>8 horas</span>
                </div>
              </div>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '6px' }}>
                  Máximo de lugares: <strong>{maxPlaces}</strong>
                </label>
                <input type="range" min="1" max="10" step="1" value={maxPlaces}
                  onChange={(e) => setMaxPlaces(parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--primary)' }} />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--muted)' }}>
                  <span>1</span><span>10</span>
                </div>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '10px' }}>
                Categorías preferidas <span style={{ color: 'var(--muted)', fontWeight: '400' }}>(opcional — vacío = todas)</span>
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {CATEGORIES.map((cat) => (
                  <button key={cat} type="button" onClick={() => toggleCategory(cat)}
                    style={{
                      padding: '6px 16px', borderRadius: '20px', border: '1.5px solid var(--primary)',
                      background: selectedCategories.includes(cat) ? 'var(--primary)' : 'transparent',
                      color: selectedCategories.includes(cat) ? '#fff' : 'var(--primary)',
                      cursor: 'pointer', fontWeight: '600', fontSize: '0.85rem', transition: 'all 0.15s'
                    }}>
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}
              style={{ alignSelf: 'flex-start', padding: '12px 32px', fontSize: '1rem' }}>
              {loading ? '⏳ Generando ruta...' : '🗺️ Generar ruta'}
            </button>
          </form>

          {error && <p className="error-text" style={{ marginTop: '12px' }}>{error}</p>}
        </section>

        {route && (
          <>
            <section className="section">
              <div className="section-head">
                <h2>Ruta generada</h2>
                <p>Optimizada por score cultural y proximidad geográfica</p>
              </div>

              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '24px' }}>
                {[
                  { label: 'Lugares', value: route.total_places },
                  { label: 'Duración estimada', value: `${route.estimated_duration_minutes} min` },
                  { label: 'Score promedio', value: route.average_score.toFixed(1) },
                ].map((stat) => (
                  <div key={stat.label} style={{
                    flex: 1, minWidth: '140px', padding: '20px',
                    background: 'var(--accent)', borderRadius: 'var(--radius)', textAlign: 'center'
                  }}>
                    <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--muted)' }}>{stat.label}</p>
                    <p style={{ margin: '6px 0 0', fontSize: '1.6rem', fontWeight: '800', color: 'var(--primary)' }}>{stat.value}</p>
                  </div>
                ))}
              </div>

              {route.total_places === 0 ? (
                <p className="section-note">No se encontraron lugares. Intenta aumentar el tiempo o quitar filtros.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {route.places.map((stop, idx) => (
                    <div key={stop.place_id} style={{
                      display: 'flex', gap: '16px', alignItems: 'center', padding: '16px',
                      background: 'var(--card)', border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)', boxShadow: 'var(--shadow)'
                    }}>
                      <div style={{
                        width: '40px', height: '40px', borderRadius: '50%',
                        background: 'var(--primary)', color: '#fff',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: '800', fontSize: '1rem', flexShrink: 0
                      }}>
                        {stop.order}
                      </div>
                      <div style={{ flex: 1 }}>
                        <strong style={{ fontSize: '1rem' }}>{stop.name || `Lugar ${stop.order}`}</strong>
                        <div style={{ display: 'flex', gap: '16px', marginTop: '6px', flexWrap: 'wrap' }}>
                          <span style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>🕐 Llega: {stop.arrival_estimated}</span>
                          <span style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>🕐 Sale: {stop.departure_estimated}</span>
                          {idx > 0 && (
                            <span style={{ fontSize: '0.82rem', color: 'var(--muted)' }}>
                              📏 {stop.distance_from_previous_km} km · ~{Math.round(stop.distance_from_previous_km / 4.5 * 60)} min caminando desde parada anterior
                            </span>
                          )}
                        </div>
                      </div>
                      <div style={{
                        background: 'var(--accent)', color: 'var(--primary)',
                        padding: '6px 14px', borderRadius: '20px',
                        fontWeight: '700', fontSize: '0.9rem', flexShrink: 0
                      }}>
                        Score {stop.score_value}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="section">
              <div className="section-head">
                <h2>Mapa del recorrido</h2>
                <p>🔴 Punto de partida — 🔵 Paradas — línea muestra el recorrido</p>
              </div>
              <div className="map-wrapper">
                <MapContainer center={mapCenter} zoom={14} style={{ height: '460px', width: '100%' }}>
                  <TileLayer
                    attribution="&copy; OpenStreetMap contributors"
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />

                  <Marker position={mapCenter} icon={userIcon}>
                    <Popup>📍 Tu punto de partida</Popup>
                  </Marker>

                  {route.places
                    .filter((p) => p.latitude && p.longitude)
                    .map((stop) => (
                      <Marker key={stop.place_id} position={[stop.latitude, stop.longitude]} icon={stopIcon}>
                        <Popup>
                          <strong>{stop.order}. {stop.name || 'Lugar'}</strong><br />
                          🕐 Llega: {stop.arrival_estimated}<br />
                          🕐 Sale: {stop.departure_estimated}<br />
                          ⭐ Score: {stop.score_value}
                        </Popup>
                      </Marker>
                    ))}

                  {polylinePoints.length > 1 && (
                    <Polyline
                      positions={polylinePoints}
                      pathOptions={{ color: '#0f766e', weight: 4, opacity: 0.8, dashArray: '8 4' }}
                    />
                  )}
                </MapContainer>
              </div>
            </section>
          </>
        )}

      </main>
    </>
  )
}

export default RoutePage