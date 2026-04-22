# Analytics Service

Servicio de an�lisis para CulturalRoute AI, construido con FastAPI y PostgreSQL.

## Requisitos

- Docker y Docker Compose

## Ejecutar el proyecto

1. Clona o descarga el repositorio.
2. Navega al directorio del proyecto.
3. Ejecuta docker-compose up --build para construir y ejecutar los contenedores.

El servicio estar� disponible en http://localhost:8000.

## Endpoints

- POST /analytics/score: Calcular y guardar el score de un lugar.
- GET /analytics/places/{place_id}/score: Obtener el score de un lugar.
- PUT /analytics/places/{place_id}/score: Actualizar el score de un lugar con nuevas variables.
- DELETE /analytics/places/{place_id}/score: Eliminar el score de un lugar.
- GET /analytics/ranking: Obtener el ranking de lugares.

## Documentaci�n

Accede a http://localhost:8000/docs para la documentaci�n interactiva de la API.
