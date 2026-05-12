import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000'
})

export const getFeaturedPlaces = async () => {
  const { data } = await api.get('/bff/dashplaces/')
  return data?.featured_products || []
}

export const getPlaceDetail = async (id) => {
  const { data } = await api.get(`/api/v1_places/places/${id}`)
  return data
}

export const getAllPlaces = async () => {
  const { data } = await api.get('/api/v1_places/places/')
  return data || []
}

export const updatePlace = async (id, payload) => {
  const { data } = await api.patch(`/api/v1_places/places/${id}`, payload)
  return data
}

export const deletePlace = async (id) => {
  const { data } = await api.delete(`/api/v1_places/places/${id}`)
  return data
}