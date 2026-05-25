import { httpClient } from '../utils/httpClient'

const api = httpClient

export const getFeaturedPlaces = async () => {
  const { data } = await api.get('/bff/dashplaces/')
  return data?.featured_products || []
}

export const getPlaceDetail = async (id) => {
  const { data } = await api.get(`/api/v1_places/places/${id}`)
  return data
}

export const getPlaceDetailBff = async (id) => {
  const { data } = await api.get(`/bff/v2/catalog/${id}`)
  return data
}

export const getAllPlaces = async () => {
  const { data } = await api.get('/api/v1_places/places/?limit=100')
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