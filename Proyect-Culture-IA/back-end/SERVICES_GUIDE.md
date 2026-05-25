# 📚 Guía de Servicios Individuales

## Tabla de Contenidos

1. [Autenticación (Auth)](#autenticación-auth)
2. [Geolocalización (Geo)](#geolocalización-geo)
3. [Lugares Culturales (Places)](#lugares-culturales-places)
4. [Configuración (Config)](#configuración-config)
5. [Calidad de Datos (Quality)](#calidad-de-datos-quality)
6. [Enriquecimiento IA (Enrichment)](#enriquecimiento-ia-enrichment)
7. [Analítica (Analytics)](#analítica-analytics)
8. [Auditoría (Audit)](#auditoría-audit)
9. [Asistente IA (AIAssistant)](#asistente-ia-aiassistant)
10. [Recomendaciones (Recommendation)](#recomendaciones-recommendation)
11. [Rutas (Route)](#rutas-route)

---

## Autenticación (Auth)

**Puerto:** 8001 | **DB:** 5432 | **Base de Datos:** cultureia_db

### Descripción
Servicio de autenticación y autorización. Gestiona login, registro y token validation.

### Endpoints Principales
```bash
POST   /api/v1_auth/auth/login          # Iniciar sesión
POST   /api/v1_auth/auth/register       # Registrarse
GET    /api/v1_auth/auth/me             # Perfil actual
POST   /api/v1_auth/auth/refresh        # Refrescar token
GET    /api/v1_auth/health              # Health check
```

### Variables de Entorno
```
DATABASE_URL=postgresql://user:password@db:5432/cultureia_db
SECRET_KEY=cultureia_db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Ejemplo de Uso
```bash
# Login
curl -X POST http://localhost:8000/api/v1_auth/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Resultado
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "123"
}
```

---

## Geolocalización (Geo)

**Puerto:** 8002 | **DB:** 5433 | **Base de Datos:** cultureia_geo_db

### Descripción
Servicio de geolocalización. Gestiona coordenadas, mapas, ubicaciones.

### Endpoints Principales
```bash
GET    /api/v1_geo/geo/points           # Obtener puntos geográficos
POST   /api/v1_geo/geo/points           # Crear punto
GET    /api/v1_geo/geo/points/{id}      # Detalle de punto
PUT    /api/v1_geo/geo/points/{id}      # Actualizar punto
GET    /api/v1_geo/health               # Health check
```

### Ejemplo de Uso
```bash
# Obtener puntos cercanos
curl "http://localhost:8000/api/v1_geo/geo/points?lat=4.7110&lon=-74.0110&radius=5"

# Crear punto geográfico
curl -X POST http://localhost:8000/api/v1_geo/geo/points \
  -H "Content-Type: application/json" \
  -d '{
    "place_id": "place-123",
    "latitude": 4.7110,
    "longitude": -74.0110,
    "address": "Bogotá, Colombia"
  }'
```

---

## Lugares Culturales (Places)

**Puerto:** 8003 | **DB:** 5434 | **Base de Datos:** places_db

### Descripción
CRUD de lugares culturales. Gestiona museos, iglesias, parques, monumentos, etc.

### Endpoints Principales
```bash
GET    /api/v1_places/places            # Listar lugares
POST   /api/v1_places/places            # Crear lugar
GET    /api/v1_places/places/{id}       # Detalle de lugar
PUT    /api/v1_places/places/{id}       # Actualizar lugar
DELETE /api/v1_places/places/{id}       # Eliminar lugar
GET    /api/v1_places/health            # Health check
```

### Ejemplo de Uso
```bash
# Listar todos los lugares
curl http://localhost:8000/api/v1_places/places

# Crear nuevo lugar
curl -X POST http://localhost:8000/api/v1_places/places \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Museo del Oro",
    "category": "Museo",
    "address": "Carrera 6, Bogotá",
    "description": "Museo de oro prehispánico",
    "latitude": 4.7110,
    "longitude": -74.0110
  }'

# Respuesta
{
  "id": "place-123",
  "name": "Museo del Oro",
  "category": "Museo",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Configuración (Config)

**Puerto:** 8004 | **DB:** 5435 | **Base de Datos:** config_db

### Descripción
Servicio de configuración global. Parámetros, settings, constantes.

### Endpoints Principales
```bash
GET    /api/v1_config/config            # Obtener configuración
POST   /api/v1_config/config            # Guardar configuración
GET    /api/v1_config/health            # Health check
```

### Ejemplo de Uso
```bash
# Obtener configuración actual
curl http://localhost:8000/api/v1_config/config

# Actualizar configuración
curl -X POST http://localhost:8000/api/v1_config/config \
  -H "Content-Type: application/json" \
  -d '{
    "max_search_radius": 10,
    "recommendation_limit": 5
  }'
```

---

## Calidad de Datos (Quality)

**Puerto:** 8005 | **DB:** 5436 | **Base de Datos:** data_quality_db

### Descripción
Validación y limpieza de datos. Procesa archivos CSV, valida información, genera reportes.

### Endpoints Principales
```bash
POST   /api/v1_quality/import           # Importar CSV
GET    /api/v1_quality/import/{batch_id} # Estado de importación
GET    /api/v1_quality/import/errors    # Errores de importación
GET    /api/v1_quality/health           # Health check
```

### Ejemplo de Uso
```bash
# Importar CSV
curl -X POST http://localhost:8000/api/v1_quality/import \
  -F "file=@lugares_culturales.csv"

# Respuesta
{
  "batch_id": "batch-123",
  "status": "processing",
  "message": "Importación iniciada"
}

# Verificar estado
curl http://localhost:8000/api/v1_quality/import/batch-123

# Respuesta
{
  "batch_id": "batch-123",
  "status": "completed",
  "processed_rows": 100,
  "valid_rows": 95,
  "invalid_rows": 5
}
```

### Columnas CSV Requeridas
```csv
nombre, ciudad, direccion, descripcion, categoria, latitude, longitude
```

---

## Enriquecimiento IA (Enrichment)

**Puerto:** 8006 | **DB:** 5437 | **Base de Datos:** places

### Descripción
Enriquecimiento de datos usando IA. Genera descripciones, categorías automáticas.

### Endpoints Principales
```bash
POST   /api/v1_enrichment/enrich        # Enriquecer lugar
GET    /api/v1_enrichment/health        # Health check
```

### Ejemplo de Uso
```bash
# Enriquecer datos de un lugar
curl -X POST http://localhost:8000/api/v1_enrichment/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "place_id": "place-123",
    "name": "Iglesia Antigua",
    "description": "Iglesia del siglo XVI"
  }'
```

---

## Analítica (Analytics)

**Puerto:** 8007 | **DB:** 5438 | **Base de Datos:** analytics_db

### Descripción
Recopila estadísticas, eventos, métricas de uso.

### Endpoints Principales
```bash
POST   /api/v1_analytics/events         # Registrar evento
GET    /api/v1_analytics/stats          # Obtener estadísticas
GET    /api/v1_analytics/health         # Health check
```

### Ejemplo de Uso
```bash
# Registrar evento
curl -X POST http://localhost:8000/api/v1_analytics/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "place_viewed",
    "place_id": "place-123",
    "user_id": "user-456",
    "timestamp": "2024-01-15T10:30:00Z"
  }'

# Obtener estadísticas
curl "http://localhost:8000/api/v1_analytics/stats?from=2024-01-01&to=2024-01-31"
```

---

## Auditoría (Audit)

**Puerto:** 8008 | **DB:** 5439 | **Base de Datos:** audit_db

### Descripción
Registro de auditoría. Logs de acciones, cambios, accesos.

### Endpoints Principales
```bash
GET    /api/v1_audit/logs               # Obtener logs
POST   /api/v1_audit/logs               # Crear log
GET    /api/v1_audit/health             # Health check
```

### Ejemplo de Uso
```bash
# Ver logs de auditoría
curl "http://localhost:8000/api/v1_audit/logs?user_id=user-123&action=delete"
```

---

## Asistente IA (AIAssistant)

**Puerto:** 8009 | **DB:** 5440 | **Base de Datos:** aiassistant_db

### Descripción
Chatbot asistente IA. Utiliza Groq, OpenAI o OpenRouter API.

### Endpoints Principales
```bash
POST   /api/v1_aiassistant/aiassistant/chat      # Enviar pregunta
GET    /api/v1_aiassistant/aiassistant/chat/{id} # Obtener respuesta
GET    /api/v1_aiassistant/aiassistant/health    # Health check
```

### Variables de Entorno
```
# Opción 1: Groq (Recomendado - Gratis)
GROQ_API_KEY=gsk_xxxxx
GROQ_MODEL=mixtral-8x7b-32768

# Opción 2: OpenAI
OPENAI_API_KEY=sk-xxxxx

# Opción 3: OpenRouter
OPENROUTER_API_KEY=sk-or-xxxxx

DATABASE_URL=postgresql://aiassistant_user:aiassistant_password@aiassistant-db:5432/aiassistant_db
```

### Ejemplo de Uso
```bash
# Enviar consulta
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "query_text": "¿Qué museos hay en Bogotá?"
  }'

# Respuesta
{
  "query_id": "query-456",
  "response": "En Bogotá hay varios museos...",
  "created_at": "2024-01-15T10:30:00Z"
}

# Obtener respuesta guardada
curl http://localhost:8000/api/v1_aiassistant/aiassistant/chat/query-456
```

---

## Recomendaciones (Recommendation)

**Puerto:** 8010 | **DB:** 5441 | **Base de Datos:** recommendation_db

### Descripción
Motor de recomendaciones personalizadas. Sugiere lugares basado en preferencias y ubicación.

### Algoritmo
```
relevance_index = (score * 0.70) + (proximity * 0.20) + (preference * 0.10)

Donde:
  score:     Puntaje cultural del lugar (0-10)
  proximity: 1 / (distancia_km + 0.1)
  preference: 1 si coincide categoría, 0 si no
```

### Endpoints Principales
```bash
GET    /api/v1_recommendation/recomendaciones           # Obtener recomendaciones
GET    /api/v1_recommendation/recomendaciones/health    # Health check
```

### Parámetros
```
?preferencia=Museo              # Categoría preferida
?max_distancia=5.0              # Distancia máxima en km
?preferencia=Museo&max_distancia=3.0  # Ambos
```

### Ejemplo de Uso
```bash
# Obtener recomendaciones
curl "http://localhost:8000/api/v1_recommendation/recomendaciones?preferencia=Museo&max_distancia=5.0"

# Respuesta
[
  {
    "place_id": "place-123",
    "name": "Museo del Oro",
    "category": "Museo",
    "relevance_index": 8.52,
    "distance_km": 2.3,
    "explanation": [
      "Excelente puntaje de relevancia (9.0)",
      "Muy cercano (2.3 km)",
      "Coincide con tu preferencia por Museos"
    ]
  }
]
```

---

## Rutas (Route)

**Puerto:** 8011 | **DB:** 5442 | **Base de Datos:** route_db

### Descripción
Planificación de rutas turísticas. Genera itinerarios óptimos entre lugares.

### Endpoints Principales
```bash
POST   /api/v1_route/routes             # Crear ruta
GET    /api/v1_route/routes/{id}        # Obtener ruta
GET    /api/v1_route/health             # Health check
```

### Ejemplo de Uso
```bash
# Crear ruta
curl -X POST http://localhost:8000/api/v1_route/routes \
  -H "Content-Type: application/json" \
  -d '{
    "place_ids": ["place-123", "place-456", "place-789"],
    "start_point": {"lat": 4.7110, "lon": -74.0110}
  }'

# Respuesta
{
  "route_id": "route-001",
  "places": [
    {"id": "place-123", "name": "Museo 1", "order": 1},
    {"id": "place-456", "name": "Museo 2", "order": 2}
  ],
  "total_distance": 8.5,
  "estimated_time": "2 hours"
}
```

---

## 🔗 Dependencias entre Servicios

```
Quality ──▶ Places              (Importa lugares)
Route ──▶ Geo                   (Obtiene coordenadas)
Route ──▶ Places                (Obtiene datos de lugares)
Route ──▶ Analytics             (Registra eventos)
Recommendation ──▶ Places       (Obtiene lugares para recomendar)
AIAssistant ──▶ Places          (Información de lugares)
AIAssistant ──▶ Recommendation  (Recomendaciones del asistente)
```

---

## 📊 Estado de Servicios (Dashboard)

Para verificar que todos los servicios estén activos:

```bash
#!/bin/bash
echo "=== Backend Services Status ==="
services=("auth" "geo" "places" "config" "quality" "enrichment" "analytics" "audit" "aiassistant" "recommendation" "route")

for service in "${services[@]}"; do
  status=$(curl -s http://localhost:8000/api/v1_$service/health || echo "DOWN")
  echo "$service: $status"
done
```

---

**Última actualización:** 2024  
**Versión:** 1.0.0
