import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

export const getNearbyPlaces = async (lat, lng, radiusKm = 5) => {
  const { data } = await api.get('/bff/nearby', {
    params: { lat, lng, radius_km: radiusKm }
  })
  return data
}

export const getDistance = async (originId, destinationId) => {
  const { data } = await api.get('/bff/distance', {
    params: {
      place_id_origin: originId,
      place_id_destination: destinationId
    }
  })
  return data
}