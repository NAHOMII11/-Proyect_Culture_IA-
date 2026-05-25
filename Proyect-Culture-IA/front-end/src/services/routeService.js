import { API } from '../config/api'
import { fetchJson } from '../utils/httpClient'

export async function generateRoute(payload) {
  return fetchJson(API.bff.routes, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    errorMessage: 'Error al generar la ruta',
  })
}

export async function getRouteById(routeId) {
  return fetchJson(API.bff.routeById(routeId), {
    errorMessage: 'Ruta no encontrada',
  })
}

export async function listRoutes() {
  const payload = await fetchJson(API.bff.routes, {
    errorMessage: 'Error al obtener rutas',
  })
  return Array.isArray(payload) ? payload : payload?.data ?? []
}