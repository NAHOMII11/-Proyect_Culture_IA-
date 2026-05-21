const BFF_URL = 'http://localhost:8000/api/v1_route'

export async function generateRoute(payload) {
  const response = await fetch(`${BFF_URL}/routes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) throw new Error('Error al generar la ruta')
  return response.json()
}

export async function getRouteById(routeId) {
  const response = await fetch(`${BFF_URL}/routes/${routeId}`)
  if (!response.ok) throw new Error('Ruta no encontrada')
  return response.json()
}

export async function listRoutes() {
  const response = await fetch(`${BFF_URL}/routes`)
  if (!response.ok) throw new Error('Error al obtener rutas')
  return response.json()
}