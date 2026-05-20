import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const normalizePlace = (place = {}) => ({
  id: place.id || place.place_id || crypto.randomUUID?.() || `${place.name}-${place.latitude}`,
  place_id: place.place_id || place.id,
  name: place.name || 'Lugar sin nombre',
  description: place.description || 'Sin descripción disponible.',
  category: place.category || 'Sin categoría',
  address: place.address || 'Sin dirección registrada',
  imagelink: place.imagelink || 'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?auto=format&fit=crop&w=900&q=80',
  status: place.status || 'active',
  latitude: Number(place.latitude ?? place.lat),
  longitude: Number(place.longitude ?? place.lng),
  lat: Number(place.latitude ?? place.lat),
  lng: Number(place.longitude ?? place.lng),
  distance_km: place.distance_km,
  score: Number(place.score ?? place.importance_score ?? 0),
})

export const getDashboardPlaces = async () => {
  const { data } = await api.get('/bff/dashplaces/')
  return (data?.featured_products || []).map(normalizePlace)
}

export const getCatalogPlaces = async () => {
  const { data } = await api.get('/api/v1_places/places/')
  return (Array.isArray(data) ? data : []).map(normalizePlace)
}

export const getPlaceById = async (id) => {
  const { data } = await api.get(`/api/v1_places/places/${id}`)
  return normalizePlace(data)
}

export const getNearby = async ({ lat, lng, radiusKm }) => {
  const { data } = await api.get('/bff/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  })

  return {
    ...data,
    nearby_places: (data?.nearby_places || []).map(normalizePlace),
  }
}

export const getDistanceBetweenPlaces = async (originId, destinationId) => {
  const { data } = await api.get('/bff/distance', {
    params: {
      place_id_origin: originId,
      place_id_destination: destinationId,
    },
  })
  return data
}

export const getRanking = async () => {
  const { data } = await api.get('/api/v1_analytics/analytics/ranking')
  return (Array.isArray(data) ? data : [])
    .map((item) => ({
      id: item.id || item.place_id || `${item.name}-${item.city}`,
      name: item.name || 'Sin nombre',
      city: item.city || item.address || 'Sin ciudad',
      score: Number(item.score ?? item.importance_score ?? 0),
      category: item.category || 'Turístico',
    }))
    .sort((a, b) => b.score - a.score)
}

export const askAssistant = async (message, context = {}) => {
  try {
    const { data } = await api.post('/api/v1_aiassistant/assistant/chat', {
      message,
      context,
    })
    return data?.answer || data?.response || data?.message
  } catch {
    const query = message.toLowerCase()
    const places = context.places || []

    if (query.includes('ranking')) {
      return 'Puedes revisar la sección Ranking para ver los lugares ordenados por puntaje turístico.'
    }

    if (query.includes('ruta') || query.includes('distancia')) {
      return 'Para calcular una ruta, entra a la sección Rutas, selecciona origen y destino, y presiona Calcular distancia.'
    }

    const match = places.find((place) => query.includes(place.name.toLowerCase()))
    if (match) {
      return `${match.name}: ${match.description} Dirección: ${match.address}. Categoría: ${match.category}.`
    }

    return 'Puedo ayudarte a buscar lugares del catálogo, entender el ranking o guiarte para calcular rutas. Prueba preguntando por un lugar específico.'
  }
}
