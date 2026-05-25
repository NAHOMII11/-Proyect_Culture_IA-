/**
 * Punto único de configuración HTTP del frontend.
 * El cliente solo conoce el gateway (BFF); los microservicios quedan detrás.
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const API = {
  auth: `${API_BASE_URL}/api/v1_auth/auth`,
  gateway: (service, path = '') =>
    `${API_BASE_URL}/api/${service}/${path}`.replace(/\/$/, ''),
  bff: {
    nearby: `${API_BASE_URL}/bff/nearby`,
    distance: `${API_BASE_URL}/bff/distance`,
    dashplaces: `${API_BASE_URL}/bff/dashplaces`,
    ranking: `${API_BASE_URL}/bff/v2/ranking`,
    catalog: (placeId) => `${API_BASE_URL}/bff/v2/catalog/${placeId}`,
    routes: `${API_BASE_URL}/bff/v2/routes`,
    routeById: (id) => `${API_BASE_URL}/bff/v2/routes/${id}`,
    recommendations: `${API_BASE_URL}/bff/v2/recommendations`,
    assistantQuery: `${API_BASE_URL}/bff/v2/assistant/query`,
  },
  quality: `${API_BASE_URL}/api/v1_quality`,
  audit: `${API_BASE_URL}/api/v1_audit`,
}
