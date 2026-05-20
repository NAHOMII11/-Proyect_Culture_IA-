================================================================================
  S3-H5 – BFF AVANZADO  |  api-bff-gateway
  Historia de usuario: PCA-36 / PCA-45
  Sprint 3 | Developer: D1
================================================================================

QUÉ SE HIZO
-----------
Se implementó el BFF Avanzado (Backend for Frontend) correspondiente a la
historia S3-H5 del Sprint 3. El BFF actúa como punto único de entrada para
el frontend, agregando respuestas de múltiples microservicios en una sola
llamada, manejando errores de servicios internos y adaptando los payloads
para que el frontend los consuma directamente sin lógica adicional.

CRITERIOS DE ACEPTACIÓN CUMPLIDOS
----------------------------------
✅ 1. Endpoint consolidado que agrega respuestas de catálogo, score y rutas
✅ 2. Manejo de errores de servicios internos
✅ 3. Adaptación de payloads para el frontend


ENDPOINTS NUEVOS (prefijo: /bff/v2)
-------------------------------------
Todos los endpoints nuevos se encuentran en:
  app/routers/bff_advanced.py

  GET  /bff/v2/catalog
       → Agrega: Place Service + Analytics Service (score por lugar)
       → Si Analytics cae, el catálogo igual responde (modo degradado)
       → Payload adaptado: incluye score, score_level junto a cada lugar

  GET  /bff/v2/catalog/{place_id}
       → Agrega: Place Service + Geo Service + Analytics Service EN PARALELO
       → Geo y Analytics son opcionales: si fallan, se devuelven como null
       → Payload adaptado: coordinates { latitude, longitude } + score en un solo JSON

  GET  /bff/v2/ranking
       → Consulta Analytics Service y enriquece con nombre/categoría/ciudad
         desde Place Service
       → El frontend recibe posición + score + nombre en una sola respuesta

  POST /bff/v2/routes
       Body: { user_lat, user_lng, preferred_categories, available_time_minutes, max_places }
       → Delega al Route Service y devuelve la ruta generada al frontend

  POST /bff/v2/assistant/query
       Body: { question, user_context: { lat, lng } }
       → Delega al AI Assistant Service y devuelve la respuesta contextual


ARCHIVOS CREADOS O MODIFICADOS
--------------------------------
NUEVOS:
  app/routers/bff_advanced.py          → Endpoints del Sprint 3
  app/application/catalog_aggregator.py → Lógica de agregación paralela
  app/infrastructure/place_client.py   → Cliente HTTP → Place Service
  app/infrastructure/analytics_client.py → Cliente HTTP → Analytics Service
  app/infrastructure/geo_client.py     → Cliente HTTP → Geo Service
  app/infrastructure/route_client.py   → Cliente HTTP → Route Service
  app/infrastructure/assistant_client.py → Cliente HTTP → Assistant Service
  app/schemas/bff_schemas.py           → Schemas Pydantic de entrada/salida
  tests/test_bff_advanced.py           → 5 pruebas unitarias con mocks

MODIFICADOS:
  app/main.py          → Registra bff_advanced_router + manejadores globales
                         de ConnectError y TimeoutException
  app/core/config.py   → Agrega ROUTE_API_URL y ASSISTANT_API_URL
  app/services/upstreams.py → Mapea v1_routes y v1_assistant
  .env                 → Variables de entorno actualizadas
  requirements.txt     → Agrega pytest y pytest-asyncio


CÓMO LEVANTAR EL SERVICIO
--------------------------
  # Opción 1: Docker
  docker build -t bff-gateway .
  docker run -p 8000:8000 --env-file .env bff-gateway

  # Opción 2: Local
  pip install -r requirements.txt
  uvicorn app.main:app --reload --port 8000

  # Documentación automática (Swagger)
  http://localhost:8000/docs


CÓMO CORRER LAS PRUEBAS
------------------------
  pip install -r requirements.txt
  pytest tests/test_bff_advanced.py -v

  Pruebas incluidas:
  - test_catalog_with_scores_includes_score     → catálogo agrega score correctamente
  - test_catalog_degraded_when_analytics_fails  → modo degradado si analytics cae
  - test_place_detail_aggregates_all_services   → detalle agrega place+geo+score
  - test_place_detail_geo_optional              → geo opcional, no bloquea el detalle
  - test_ranking_enriched_with_names            → ranking incluye nombre del lugar


MANEJO DE ERRORES (criterio 2)
--------------------------------
Todos los endpoints responden con estructura consistente ante fallos internos:

  Servicio caído (503):
  { "error": "service_unavailable", "message": "...", "service": "place-service" }

  Timeout (504):
  { "error": "gateway_timeout", "message": "...", "service": "analytics-service" }

  Error del upstream (502):
  { "error": "upstream_error", "message": "...", "upstream_status": 500 }

  No encontrado (404):
  { "error": "not_found", "message": "...", "service": "place-service" }

  Los endpoints de catálogo y ranking operan en MODO DEGRADADO: si Analytics
  o Geo fallan, el BFF devuelve igual una respuesta válida con los campos
  afectados en null, sin romper la experiencia del usuario.


NOTAS TÉCNICAS
--------------
- Las llamadas a múltiples servicios se hacen en PARALELO con asyncio.gather,
  no en secuencia, lo que reduce la latencia total.
- El BFF NO contiene lógica de negocio: no calcula scores, no genera rutas,
  no interpreta preguntas. Solo agrega y adapta.
- Los endpoints del Sprint 1 y 2 (dashboard, nearby, distance) se conservan
  intactos en app/routers/bff.py.
- Compatible con el docker-compose general del proyecto.

================================================================================
