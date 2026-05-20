import { useEffect, useMemo, useState } from 'react'
import TouristMap from '../components/map/TouristMap'
import {
  askAssistant,
  getCatalogPlaces,
  getDashboardPlaces,
  getDistanceBetweenPlaces,
  getNearby,
  getPlaceById,
  getRanking,
  normalizePlace,
} from '../services/bffService'

const DEFAULT_CENTER = { lat: 7.8939, lng: -72.5078 }

const menuItems = [
  { id: 'catalogo', label: 'Catálogo', icon: '🎭' },
  { id: 'mapa', label: 'Mapa', icon: '🗺️' },
  { id: 'ranking', label: 'Ranking', icon: '🌟' },
  { id: 'rutas', label: 'Rutas', icon: '🧭' },
  { id: 'asistente', label: 'Asistente', icon: '🤖' },
]

function StateBox({ type = 'info', title, text, action }) {
  return (
    <div className={`state-box state-${type}`}>
      <strong>{title}</strong>
      {text && <p>{text}</p>}
      {action}
    </div>
  )
}

function FinalInterface() {
  const [activeSection, setActiveSection] = useState('catalogo')
  const [places, setPlaces] = useState([])
  const [selectedPlace, setSelectedPlace] = useState(null)
  const [selectedDetail, setSelectedDetail] = useState(null)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [catalogError, setCatalogError] = useState('')
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')

  const [ranking, setRanking] = useState([])
  const [rankingLoading, setRankingLoading] = useState(false)
  const [rankingError, setRankingError] = useState('')

  const [nearbyLoading, setNearbyLoading] = useState(false)
  const [nearbyError, setNearbyError] = useState('')
  const [nearbyPlaces, setNearbyPlaces] = useState([])
  const [userPoint, setUserPoint] = useState(DEFAULT_CENTER)
  const [radiusKm, setRadiusKm] = useState(10)

  const [originId, setOriginId] = useState('')
  const [destinationId, setDestinationId] = useState('')
  const [routeResult, setRouteResult] = useState(null)
  const [routeLoading, setRouteLoading] = useState(false)
  const [routeError, setRouteError] = useState('')

  const [assistantInput, setAssistantInput] = useState('')
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Hola, soy tu asistente cultural. Puedes preguntarme por lugares, rutas o ranking.',
    },
  ])

  const loadPlaces = async () => {
    setCatalogLoading(true)
    setCatalogError('')
    try {
      let data = await getDashboardPlaces()
      const hasCoordinates = data.some((place) => Number.isFinite(place.lat) && Number.isFinite(place.lng))

      if (!data.length || !hasCoordinates) {
        data = await getCatalogPlaces()
      }

      const active = data.filter((place) => place.status !== 'inactive')
      setPlaces(active)
      setSelectedPlace(active.find((p) => Number.isFinite(p.lat) && Number.isFinite(p.lng)) || active[0] || null)
    } catch {
      setCatalogError('No fue posible cargar el catálogo desde el BFF o el servicio de lugares.')
    } finally {
      setCatalogLoading(false)
    }
  }

  const loadRanking = async () => {
    setRankingLoading(true)
    setRankingError('')
    try {
      setRanking(await getRanking())
    } catch {
      setRankingError('No se pudo cargar el ranking. Verifica que analytics-service esté activo.')
    } finally {
      setRankingLoading(false)
    }
  }

  useEffect(() => {
    loadPlaces()
    loadRanking()
  }, [])

  const categories = useMemo(() => {
    return [...new Set(places.map((place) => place.category).filter(Boolean))]
  }, [places])

  const filteredPlaces = useMemo(() => {
    const cleanQuery = query.trim().toLowerCase()
    return places.filter((place) => {
      const matchesQuery =
        !cleanQuery ||
        place.name.toLowerCase().includes(cleanQuery) ||
        place.description.toLowerCase().includes(cleanQuery) ||
        place.address.toLowerCase().includes(cleanQuery)
      const matchesCategory = !category || place.category === category
      return matchesQuery && matchesCategory
    })
  }, [places, query, category])

  const selectPlace = async (place) => {
    const normalized = normalizePlace(place)
    setSelectedPlace(normalized)
    setSelectedDetail(null)
    setActiveSection('mapa')

    try {
      const detail = await getPlaceById(normalized.id)
      setSelectedDetail(detail)
    } catch {
      setSelectedDetail(normalized)
    }
  }

  const detectLocationAndSearch = () => {
    setNearbyError('')
    if (!navigator.geolocation) {
      setNearbyError('Tu navegador no soporta geolocalización. Se usará una ubicación por defecto.')
      searchNearby(DEFAULT_CENTER)
      return
    }

    setNearbyLoading(true)
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const point = {
          lat: Number(position.coords.latitude.toFixed(6)),
          lng: Number(position.coords.longitude.toFixed(6)),
        }
        setUserPoint(point)
        searchNearby(point)
      },
      () => {
        setNearbyLoading(false)
        setNearbyError('No se pudo obtener tu ubicación. Se usará una ubicación por defecto.')
        searchNearby(DEFAULT_CENTER)
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  const searchNearby = async (point = userPoint) => {
    setNearbyLoading(true)
    setNearbyError('')
    try {
      const data = await getNearby({ lat: point.lat, lng: point.lng, radiusKm })
      setNearbyPlaces(data.nearby_places || [])
    } catch {
      setNearbyError('No fue posible consultar lugares cercanos desde el BFF.')
    } finally {
      setNearbyLoading(false)
    }
  }

  const calculateRoute = async () => {
    setRouteError('')
    setRouteResult(null)

    if (!originId || !destinationId) {
      setRouteError('Selecciona un lugar de origen y uno de destino.')
      return
    }

    if (originId === destinationId) {
      setRouteError('El origen y el destino deben ser diferentes.')
      return
    }

    setRouteLoading(true)
    try {
      const data = await getDistanceBetweenPlaces(originId, destinationId)
      setRouteResult(data)
      const destination = places.find((place) => String(place.place_id || place.id) === String(destinationId))
      if (destination) setSelectedPlace(destination)
    } catch {
      setRouteError('No se pudo calcular la distancia entre los lugares seleccionados.')
    } finally {
      setRouteLoading(false)
    }
  }

  const sendAssistantMessage = async (event) => {
    event.preventDefault()
    const text = assistantInput.trim()
    if (!text) return

    setMessages((prev) => [...prev, { role: 'user', text }])
    setAssistantInput('')
    setAssistantLoading(true)

    const answer = await askAssistant(text, { places: filteredPlaces.slice(0, 20), selectedPlace })
    setMessages((prev) => [...prev, { role: 'assistant', text: answer }])
    setAssistantLoading(false)
  }

  const routePlaces = places.filter((place) => place.place_id || place.id)

  return (
    <div className="final-app">
      <aside className="side-nav">
        <div className="side-brand">
          <span className="brand-mark">C</span>
          <div>
            <strong>Culture IA</strong>
            <small>Festival digital</small>
          </div>
        </div>

        <nav>
          {menuItems.map((item) => (
            <button
              key={item.id}
              className={`side-link ${activeSection === item.id ? 'active' : ''}`}
              onClick={() => setActiveSection(item.id)}
              type="button"
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="final-main">
        <header className="topbar">
          <div>
            <p className="eyebrow">🎨 Plataforma CulturalRoute AI</p>
            <h1>Explora cultura, rutas y lugares con una experiencia viva</h1>
          </div>
          <button className="btn btn-primary" type="button" onClick={loadPlaces} disabled={catalogLoading}>
            {catalogLoading ? 'Actualizando...' : 'Actualizar datos'}
          </button>
        </header>

        <section className="summary-grid">
          <article className="summary-card"><strong>{places.length}</strong><span>Lugares</span></article>
          <article className="summary-card"><strong>{categories.length}</strong><span>Categorías</span></article>
          <article className="summary-card"><strong>{ranking.length}</strong><span>Ranking</span></article>
          <article className="summary-card"><strong>{nearbyPlaces.length}</strong><span>Cercanos</span></article>
        </section>

        {activeSection === 'catalogo' && (
          <section className="final-panel">
            <div className="section-head split-head">
              <div>
                <h2>Catálogo cultural</h2>
                <p>Descubre destinos, tradiciones y espacios turísticos conectados desde el BFF.</p>
              </div>
              <div className="filters compact-filters">
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar lugar..." />
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="">Todas</option>
                  {categories.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </div>
            </div>

            {catalogLoading && <StateBox title="Cargando catálogo" text="Consultando datos del BFF..." />}
            {catalogError && <StateBox type="error" title="Error" text={catalogError} action={<button className="btn" onClick={loadPlaces}>Reintentar</button>} />}
            {!catalogLoading && !catalogError && filteredPlaces.length === 0 && <StateBox title="Sin resultados" text="No hay lugares que coincidan con los filtros aplicados." />}

            {!catalogLoading && !catalogError && filteredPlaces.length > 0 && (
              <div className="catalog-grid-final">
                {filteredPlaces.map((place) => (
                  <article className="place-card interactive-card" key={place.id} onClick={() => selectPlace(place)}>
                    <img src={place.imagelink} alt={place.name} className="place-image" />
                    <div className="place-body">
                      <span className="badge">{place.category}</span>
                      <h3>{place.name}</h3>
                      <p>{place.description}</p>
                      <small>{place.address}</small>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {activeSection === 'mapa' && (
          <section className="final-panel">
            <div className="section-head">
              <h2>Mapa cultural interactivo</h2>
              <p>Ubica cada experiencia y navega visualmente por los destinos seleccionados.</p>
            </div>
            {!selectedPlace && <StateBox title="Selecciona un lugar" text="Elige un destino del catálogo para mostrarlo en el mapa." />}
            <TouristMap selectedPlace={selectedPlace} places={filteredPlaces} />
            {selectedDetail && (
              <div className="detail-inline">
                <img src={selectedDetail.imagelink} alt={selectedDetail.name} />
                <div>
                  <span className="badge">{selectedDetail.category}</span>
                  <h3>{selectedDetail.name}</h3>
                  <p>{selectedDetail.description}</p>
                  <strong>{selectedDetail.address}</strong>
                </div>
              </div>
            )}
          </section>
        )}

        {activeSection === 'ranking' && (
          <section className="final-panel">
            <div className="section-head split-head">
              <div>
                <h2>Ranking de experiencias</h2>
                <p>Lugares destacados según los datos integrados con analytics-service.</p>
              </div>
              <button className="btn" onClick={loadRanking} disabled={rankingLoading}>Recargar ranking</button>
            </div>
            {rankingLoading && <StateBox title="Cargando ranking" text="Consultando el servicio de analítica..." />}
            {rankingError && <StateBox type="error" title="Error" text={rankingError} action={<button className="btn" onClick={loadRanking}>Reintentar</button>} />}
            {!rankingLoading && !rankingError && ranking.length === 0 && <StateBox title="Ranking vacío" text="Aún no hay puntajes calculados." />}
            {!rankingLoading && !rankingError && ranking.length > 0 && (
              <div className="ranking-grid">
                {ranking.map((item, index) => {
                  const percentage = Math.max(0, Math.min(100, item.score * 100))
                  return (
                    <article className="ranking-card" key={item.id || index}>
                      <div className="ranking-position">#{index + 1}</div>
                      <div className="ranking-main">
                        <h3>{item.name}</h3>
                        <div className="ranking-meta"><span className="badge">{item.city}</span><span>{item.category}</span></div>
                        <div className="ranking-bar"><div className="ranking-bar-fill" style={{ width: `${percentage}%` }} /></div>
                      </div>
                      <div className="ranking-score"><strong>{Math.round(percentage)}%</strong><p>Score</p></div>
                    </article>
                  )
                })}
              </div>
            )}
          </section>
        )}

        {activeSection === 'rutas' && (
          <section className="final-panel routes-layout">
            <div>
              <div className="section-head">
                <h2>Rutas culturales y cercanas</h2>
                <p>Planea recorridos, calcula distancias y encuentra espacios culturales alrededor tuyo.</p>
              </div>

              <div className="route-card">
                <h3>Calcular distancia</h3>
                <select value={originId} onChange={(e) => setOriginId(e.target.value)}>
                  <option value="">Origen</option>
                  {routePlaces.map((place) => <option key={`o-${place.id}`} value={place.place_id || place.id}>{place.name}</option>)}
                </select>
                <select value={destinationId} onChange={(e) => setDestinationId(e.target.value)}>
                  <option value="">Destino</option>
                  {routePlaces.map((place) => <option key={`d-${place.id}`} value={place.place_id || place.id}>{place.name}</option>)}
                </select>
                <button className="btn btn-primary" onClick={calculateRoute} disabled={routeLoading}>{routeLoading ? 'Calculando...' : 'Calcular distancia'}</button>
                {routeError && <p className="error-text">{routeError}</p>}
                {routeResult && (
                  <div className="result-box">
                    <strong>Resultado</strong>
                    <pre>{JSON.stringify(routeResult, null, 2)}</pre>
                  </div>
                )}
              </div>

              <div className="route-card">
                <h3>Lugares cercanos</h3>
                <label>Radio: {radiusKm} km</label>
                <input type="range" min="1" max="100" value={radiusKm} onChange={(e) => setRadiusKm(Number(e.target.value))} />
                <button className="btn" onClick={detectLocationAndSearch} disabled={nearbyLoading}>{nearbyLoading ? 'Buscando...' : 'Buscar cerca de mí'}</button>
                {nearbyError && <p className="error-text">{nearbyError}</p>}
              </div>
            </div>

            <div className="nearby-list">
              {nearbyLoading && <StateBox title="Buscando lugares" text="Consultando proximidad geográfica..." />}
              {!nearbyLoading && nearbyPlaces.length === 0 && <StateBox title="Sin búsqueda" text="Presiona Buscar cerca de mí para ver resultados." />}
              {!nearbyLoading && nearbyPlaces.map((place) => (
                <button key={place.id} className="nearby-item" onClick={() => selectPlace(place)} type="button">
                  <strong>{place.name}</strong>
                  <span>{place.distance_km ? `${Number(place.distance_km).toFixed(2)} km` : place.category}</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {activeSection === 'asistente' && (
          <section className="final-panel assistant-layout">
            <div className="section-head">
              <h2>Asistente cultural IA</h2>
              <p>Pregunta por recomendaciones, rutas, lugares y experiencias del catálogo.</p>
            </div>
            <div className="chat-box">
              {messages.map((message, index) => (
                <div key={index} className={`chat-message ${message.role}`}>
                  {message.text}
                </div>
              ))}
              {assistantLoading && <div className="chat-message assistant">Pensando...</div>}
            </div>
            <form className="chat-form" onSubmit={sendAssistantMessage}>
              <input value={assistantInput} onChange={(e) => setAssistantInput(e.target.value)} placeholder="Ej: ¿Qué lugar recomiendas visitar?" />
              <button className="btn btn-primary" type="submit" disabled={assistantLoading}>Enviar</button>
            </form>
          </section>
        )}
      </main>
    </div>
  )
}

export default FinalInterface
