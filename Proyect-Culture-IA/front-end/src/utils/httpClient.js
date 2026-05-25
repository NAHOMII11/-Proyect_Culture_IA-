import axios from 'axios'
import { API_BASE_URL } from '../config/api'
import { getToken } from './auth'

export const httpClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

httpClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function fetchJson(url, options = {}) {
  const response = await fetch(url, options)
  if (!response.ok) {
    throw new Error(options.errorMessage || 'Error en la solicitud')
  }
  return response.json()
}
