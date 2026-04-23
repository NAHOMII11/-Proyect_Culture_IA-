// src/pages/HomePage.jsx
import { useEffect, useMemo, useState } from 'react'
import Header from '../components/layout/Header'
import PlaceGrid from '../components/places/PlaceGrid'
import TouristMap from '../components/map/TouristMap'
import { getFeaturedPlaces, getPlaceDetail } from '../services/placesService'

function HomePage() {
  const [places, setPlaces] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPlace, setSelectedPlace] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [showDetail, setShowDetail] = useState(false)
  const [nameFilter, setNameFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')

  useEffect(() => {
    const loadPlaces = async () => {
      try {
        setLoading(true)
        const data = await getFeaturedPlaces()
        const activePlaces = data.filter((place) => place.status === 'active')
        setPlaces(activePlaces)
        if (activePlaces.length > 0) {
          setSelectedPlace(activePlaces[0])
        }
      } catch (err) {
        setError('No fue posible cargar los lugares turísticos')
      } finally {
        setLoading(false)
      }
    }

    loadPlaces()
  }, [])

  const categories = useMemo(() => {
    return [...new Set(places.map((place) => place.category).filter(Boolean))]
  }, [places])

  const filteredPlaces = useMemo(() => {
    const name = nameFilter.trim().toLowerCase()
    const category = categoryFilter.trim().toLowerCase()

    return places.filter((place) => {
      const matchesName = !name || place.name.toLowerCase().includes(name)
      const matchesCategory = !category || place.category.toLowerCase() === category
      return matchesName && matchesCategory
    })
  }, [places, nameFilter, categoryFilter])

  const openDetail = async (place) => {
    setSelectedPlace(place)
    setShowDetail(true)
    setDetail(null)
    setDetailLoading(true)

    try {
      const data = await getPlaceDetail(place.id)
      setDetail(data)
    } catch (err) {
      setDetail({
        id: place.id,
        name: place.name,
        category: place.category,
        description: place.description,
        imagelink: place.imagelink,
        latitude: null,
        longitude: null
      })
    } finally {
      setDetailLoading(false)
    }
  }

  return (
    <>
      <Header />

      <main className="page">
        <section className="hero">
          <div>
            <p className="eyebrow">Explora Colombia Y Sitios Culturales</p>
            <h1>Encuentra lugares turísticos, consulta destinos y traza rutas fácilmente</h1>
            <p className="hero-text">
              Navega por un catálogo visual de destinos y al final encuentra un mapa interactivo para planear recorridos.
            </p>
          </div>
        </section>

        <section className="section">
          <div className="section-head">
            <h2>Catálogo turístico</h2>
            <p>Selecciona un lugar para mostrarlo como destino en el mapa.</p>
          </div>

          <div className="filters">
            <input
              type="text"
              placeholder="Buscar por nombre..."
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
            />

            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              <option value="">Todas las categorías</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {loading && <p className="section-note">Cargando lugares...</p>}
          {error && <p className="error-text">{error}</p>}

          {!loading && !error && (
            <PlaceGrid
              places={filteredPlaces}
              onSelect={openDetail}
            />
          )}
        </section>

        <section className="section">
          <div className="section-head">
            <h2>Mapa y rutas</h2>
            <p>
              Ruta actual hacia: <strong>{selectedPlace?.name || 'Sin selección'}</strong>
            </p>
          </div>

          <TouristMap selectedPlace={selectedPlace} places={filteredPlaces} />
        </section>
      </main>

      {showDetail && (
        <div className="detail-overlay" onClick={() => setShowDetail(false)}>
          <div className="detail-card" onClick={(e) => e.stopPropagation()}>
            <button className="detail-close" onClick={() => setShowDetail(false)}>
              ×
            </button>

            {detailLoading ? (
              <p>Cargando detalle...</p>
            ) : detail ? (
              <>
                <img
                  src={detail.imagelink}
                  alt={detail.name}
                  className="detail-image"
                />
                <h3>{detail.name}</h3>
                <p className="badge">{detail.category}</p>
                <p>{detail.description}</p>
                <p><strong>Dirección:</strong> {detail.address || 'Sin dirección'}</p>
                <p><strong>Latitud:</strong> {detail.latitude ?? 'N/A'}</p>
                <p><strong>Longitud:</strong> {detail.longitude ?? 'N/A'}</p>
              </>
            ) : null}
          </div>
        </div>
      )}
    </>
  )
}

export default HomePage