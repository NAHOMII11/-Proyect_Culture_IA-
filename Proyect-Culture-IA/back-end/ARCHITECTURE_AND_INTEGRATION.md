# 🏗️ Arquitectura de Microservicios - Backend

## 📊 Visión General

La aplicación Backend está basada en una arquitectura de **microservicios** con un **API Gateway (BFF)** como punto de entrada centralizado. Cada servicio está containerizado con Docker y orquestado con Docker Compose.

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React/Vite)                        │
│                     localhost:3000/5173                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   API BFF Gateway        │
                    │   Port: 8000             │
                    │   (Punto de entrada)     │
                    └────┬──┬──┬──┬──┬──┬──┬───┘
        ┌───────────┬─────┼──┼──┼──┼──┼──┼──┴────────────────┐
        │           │     │  │  │  │  │  │                   │
        ▼           ▼     ▼  ▼  ▼  ▼  ▼  ▼                   ▼
    ┌────────┐ ┌────────┐ ┌──────────────────────────────────────┐
    │  Auth  │ │  Geo   │ │          Otros Servicios            │
    │ 8001   │ │ 8002   │ │ Places(8003) Config(8004)           │
    └────────┘ └────────┘ │ Quality(8005) Enrichment(8006)      │
                          │ Analytics(8007) Audit(8008)         │
                          │ AIAssistant(8009) Recommendation(8010)
                          │ Route(8011)                          │
                          └──────────────────────────────────────┘
        │           │     │  │  │  │  │  │                   │
        ▼           ▼     ▼  ▼  ▼  ▼  ▼  ▼                   ▼
    ┌────────┐ ┌────────┐ ┌──────────────────────────────────────┐
    │  Auth  │ │  Geo   │ │       Bases de Datos PostgreSQL      │
    │ DB     │ │ DB     │ │ (Cada servicio tiene su propia BD)   │
    │ 5432   │ │ 5433   │ │ Puertos: 5434, 5435, 5436... 5442    │
    └────────┘ └────────┘ └──────────────────────────────────────┘
```

---

## 🌐 Servicios Disponibles

### Servicios Principales

| # | Servicio | Puerto | Base de Datos | Descripción |
|---|----------|--------|---------------|-------------|
| 1 | **auth-api** | 8001 | 5432 | Autenticación y autorización |
| 2 | **geo-api** | 8002 | 5433 | Servicios geolocalización |
| 3 | **places-api** | 8003 | 5434 | CRUD de lugares culturales |
| 4 | **config-api** | 8004 | 5435 | Configuración global |
| 5 | **quality-api** | 8005 | 5436 | Validación de calidad de datos |
| 6 | **enrichment-api** | 8006 | 5437 | Enriquecimiento con IA |
| 7 | **analytics-api** | 8007 | 5438 | Análisis y estadísticas |
| 8 | **audit-api** | 8008 | 5439 | Auditoría y logs |
| 9 | **aiassistant-api** | 8009 | 5440 | Asistente IA (Chat GPT/Groq/OpenRouter) |
| 10 | **recommendation-api** | 8010 | 5441 | Recomendaciones personalizadas |
| 11 | **route-api** | 8011 | 5442 | Rutas y planificación |
| **GATEWAY** | **gateway-bff** | 8000 | — | Punto de entrada único |

---

## 🔌 Conexión Gateway

### Rutas Disponibles

Todos los servicios son accesibles mediante el Gateway en formato:
```
http://localhost:8000/api/v1_<servicio>/<endpoints>
```

#### Ejemplos

```bash
# Autenticación
GET  http://localhost:8000/api/v1_auth/auth/login
POST http://localhost:8000/api/v1_auth/auth/register

# Lugares
GET  http://localhost:8000/api/v1_places/places
POST http://localhost:8000/api/v1_places/places

# Recomendaciones
GET  http://localhost:8000/api/v1_recommendation/recomendaciones?preferencia=Museo

# Asistente IA
POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat

# Rutas
GET  http://localhost:8000/api/v1_route/routes
```

---

## 🐳 Docker Compose Structure

### Servicios en docker-compose.yml

```yaml
services:
  # Bases de Datos (11 instancias de PostgreSQL)
  db:                    # Para api-auth
  db-geo:                # Para api-geo
  db_places:             # Para api-places
  config_db:             # Para config-api
  postgres_quality_data: # Para quality-api
  db-iaenri:             # Para enrichment-api
  analytics-db:          # Para analytics-api
  audit_db:              # Para audit-api
  aiassistant-db:        # Para aiassistant-api
  recommendation-db:     # Para recommendation-api
  db-route:              # Para route-api

  # APIs (11 microservicios)
  api-auth
  api-geo
  api-place
  config_api
  api-quality
  api-iaenri
  analytics-service
  audit_api
  api-aiassistant
  api-recommendation
  api-route

  # Gateway
  gateway-bff            # Punto de entrada único

networks:
  cultureia-network:     # Red compartida para todos los servicios
    driver: bridge

volumes:
  # Volúmenes para persistencia de datos
  postgres_*_data: [11 volúmenes]
```

---

## 🚀 Cómo Iniciar

### Prerequisitos
- Docker Desktop instalado
- Puerto 8000 disponible (Gateway)
- ~12 GB RAM (11 DBs + 11 APIs)

### Pasos

```bash
# 1. Navega a la carpeta backend
cd back-end

# 2. Construye y levanta todos los contenedores
docker-compose up --build

# 3. Espera ~30-60 segundos para que todo inicie
# Verás logs de cada servicio inicializándose

# 4. Verifica que todo esté corriendo
docker-compose ps
# Deberías ver 11 servicios + 11 databases marcados como "Up"
```

---

## 🔍 Verificación de Servicios

### Prueba de Salud (Health Checks)

```bash
# 1. Gateway
curl http://localhost:8000/health

# 2. Autenticación
curl http://localhost:8000/api/v1_auth/health

# 3. Lugares
curl http://localhost:8000/api/v1_places/health

# 4. Recomendaciones
curl http://localhost:8000/api/v1_recommendation/recomendaciones/health

# 5. Asistente IA
curl http://localhost:8000/api/v1_aiassistant/aiassistant/health
```

Respuesta esperada:
```json
{ "status": "healthy" }
```

---

## 📁 Estructura de Directorios

```
back-end/
├── docker-compose.yml          # Orquestación de servicios
├── api-atenticacion/           # Servicio de autenticación
├── api-geo/                    # Servicio de geolocalización
├── api-catalogo/               # Servicio de lugares
├── api-config/                 # Configuración
├── api-dataquality/            # Validación de datos
├── api-ia-Enrichment/          # Enriquecimiento IA
├── api-analytics/              # Analytics
├── api-audit/                  # Auditoría
├── api-aiassistant/            # Asistente IA
├── api-recommendation/         # Recomendaciones
├── api-route/                  # Rutas
├── api-bff-gateway/            # Gateway BFF
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py       # Configuración de URLs
│   │   └── services/
│   │       └── upstreams.py    # Mapeo de rutas
│   └── requirements.txt
└── [documentación]             # Archivos .md
```

---

## 🔐 Variables de Entorno

Cada servicio tiene su propio `.env`:

```bash
# api-atenticacion/.env
DATABASE_URL=postgresql://user:password@db:5432/cultureia_db
SECRET_KEY=cultureia_db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# api-aiassistant/.env
GROQ_API_KEY=xxxx        # o OPENAI_API_KEY / OPENROUTER_KEY
DATABASE_URL=postgresql://aiassistant_user:aiassistant_password@aiassistant-db:5432/aiassistant_db

# api-recommendation/.env
DATABASE_URL=postgresql://rec_user:rec_password@recommendation-db:5432/recommendation_db

# ... más archivos .env en cada carpeta
```

---

## 💾 Gestión de Volúmenes

### Persistencia de Datos

Los datos se persisten en volúmenes de Docker:

```bash
# Ver volúmenes
docker volume ls

# Inspeccionar un volumen
docker volume inspect cultureia-network_postgres_auth_data

# Limpiar volúmenes (CUIDADO: borra datos)
docker volume prune
```

---

## 🛑 Detener y Limpiar

```bash
# Detener todos los servicios sin borrar datos
docker-compose stop

# Detener y remover contenedores
docker-compose down

# Detener, remover contenedores y volúmenes (PELIGRO)
docker-compose down -v

# Ver logs en tiempo real
docker-compose logs -f [nombre_servicio]

# Ver logs de un servicio específico
docker-compose logs api-recommendation
```

---

## 🔄 Dependencias entre Servicios

```
Gateway (8000)
├─▶ Auth (8001) ──▶ DB (5432)
├─▶ Geo (8002) ──▶ DB (5433)
├─▶ Places (8003) ──▶ DB (5434)
├─▶ Config (8004) ──▶ DB (5435)
├─▶ Quality (8005) ──▶ DB (5436)
│   └─▶ Llama Places (8003)
├─▶ Enrichment (8006) ──▶ DB (5437)
├─▶ Analytics (8007) ──▶ DB (5438)
├─▶ Audit (8008) ──▶ DB (5439)
├─▶ AIAssistant (8009) ──▶ DB (5440)
├─▶ Recommendation (8010) ──▶ DB (5441)
│   └─▶ Llama Places (8003)
└─▶ Route (8011) ──▶ DB (5442)
    ├─▶ Llama Geo (8002)
    ├─▶ Llama Places (8003)
    └─▶ Llama Analytics (8007)
```

---

## 📊 Performance Esperado

| Métrica | Valor |
|---------|-------|
| Tiempo de inicio | 30-60 segundos |
| Latencia promedio | 50-200ms |
| Conexión a BD | ~5-10ms |
| Llamadas inter-servicios | ~20-50ms |
| Uso de RAM | 8-12 GB |
| Uso de CPU | 10-30% (en reposo) |

---

## ⚠️ Troubleshooting

### Problema: Puerto ya en uso

```bash
# Encontrar qué proceso usa el puerto
netstat -ano | findstr :8000

# Matar el proceso
taskkill /PID <PID> /F
```

### Problema: Base de datos no inicia

```bash
# Ver logs de la BD
docker-compose logs recommendation-db

# Esperar a que esté lista
docker-compose logs recommendation-db | grep "ready to accept connections"
```

### Problema: Contenedor crashea

```bash
# Ver logs completos
docker-compose logs [servicio]

# Reconstruir imagen
docker-compose up --build [servicio]
```

---

## 📞 Recursos

- **Gateway Health:** http://localhost:8000/health
- **API Documentation:** Cada servicio expone `/docs` (Swagger)
- **Direct Access:** http://localhost:8009/docs (AIAssistant ej.)

---

**Última actualización:** 2024  
**Versión:** 1.0.0  
**Mantenido por:** Copilot
