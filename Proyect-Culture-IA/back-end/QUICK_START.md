# 🚀 Quick Start & Setup Guide

## 30 Segundos para Empezar

```bash
# 1. Navega a backend
cd back-end

# 2. Levanta todo
docker-compose up --build

# 3. Espera 30 segundos y prueba
curl http://localhost:8000/health
```

---

## 📋 Pre-requisitos

- ✅ Docker Desktop instalado
- ✅ 12 GB RAM disponible
- ✅ Puertos 8000-8011 y 5432-5442 libres
- ✅ Windows PowerShell o Terminal

---

## 🎯 Instalación Paso a Paso

### Paso 1: Verificar Docker

```bash
# Verificar que Docker está corriendo
docker --version
docker-compose --version

# Salida esperada
# Docker version 24.x.x
# Docker Compose version 2.x.x
```

### Paso 2: Clonar/Preparar Proyecto

```bash
# Navega a la carpeta backend
cd c:\Users\[usuario]\Desktop\Proyect-Culture-IA\back-end

# Verifica que docker-compose.yml exista
dir docker-compose.yml
```

### Paso 3: Construir Imágenes

```bash
# Esto descargará y construirá todas las imágenes (~5-10 min primera vez)
docker-compose build

# Ver progreso de construcción
docker-compose build --verbose
```

### Paso 4: Iniciar Servicios

```bash
# Opción A: Ver logs en tiempo real
docker-compose up

# Opción B: Ejecutar en background
docker-compose up -d

# Seguir los logs después
docker-compose logs -f
```

### Paso 5: Verificar que Todo Esté Activo

```bash
# Ver estado de contenedores (espera ~30 segundos)
docker-compose ps

# Debería verse:
# NAME                      STATUS
# cultureia-auth-api        Up 15 seconds
# cultureia-postgres        Up 20 seconds
# cultureia-geo-api         Up 15 seconds
# ... [11 servicios + 11 databases] ...
```

---

## ✅ Verificación de Salud

### Prueba Rápida

```bash
# 1. Gateway principal
curl http://localhost:8000/health

# 2. Autenticación
curl http://localhost:8000/api/v1_auth/health

# 3. Lugares
curl http://localhost:8000/api/v1_places/places

# 4. Recomendaciones
curl "http://localhost:8000/api/v1_recommendation/recomendaciones?preferencia=Museo"
```

### Respuestas Esperadas

```json
// Health check
{ "status": "healthy" }

// Places list
[ { "id": "place-1", "name": "Museo del Oro", ... } ]

// Recommendations
[ { "place_id": "place-123", "relevance_index": 8.5, ... } ]
```

---

## 🔧 Configuración Inicial

### 1. API Keys para AI Assistant

Edita `api-aiassistant/.env`:

```bash
# Opción 1: Groq (RECOMENDADO - GRATIS)
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXX
GROQ_MODEL=mixtral-8x7b-32768

# Opción 2: OpenAI
# OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXX

# Opción 3: OpenRouter
# OPENROUTER_API_KEY=sk-or-XXXXXXXXXXXXXXXXXXXX

DATABASE_URL=postgresql://aiassistant_user:aiassistant_password@aiassistant-db:5432/aiassistant_db
PYTHONPATH=/app
```

**¿Cómo obtener API Keys?**

- **Groq:** https://console.groq.com (Gratis, ilimitado)
- **OpenAI:** https://platform.openai.com (Pago, por uso)
- **OpenRouter:** https://openrouter.ai (Modelo agregador)

---

## 📊 Estructura de Puertos

```
Frontend:              localhost:3000 (React/Vite)
Gateway:               localhost:8000 (punto entrada)
APIs:                  localhost:8001-8011
Databases:             localhost:5432-5442
```

### Mapa de Puertos Detallado

| Servicio | Puerto | Tipo |
|----------|--------|------|
| Gateway | 8000 | API |
| Auth | 8001 | API |
| Geo | 8002 | API |
| Places | 8003 | API |
| Config | 8004 | API |
| Quality | 8005 | API |
| Enrichment | 8006 | API |
| Analytics | 8007 | API |
| Audit | 8008 | API |
| AIAssistant | 8009 | API |
| Recommendation | 8010 | API |
| Route | 8011 | API |
| Auth DB | 5432 | PostgreSQL |
| Geo DB | 5433 | PostgreSQL |
| ... | 5434-5442 | PostgreSQL |

---

## 🧪 Primeros Tests

### Test 1: Gateway Health

```bash
curl -X GET http://localhost:8000/health
```

### Test 2: Obtener Lugares

```bash
curl -X GET "http://localhost:8000/api/v1_places/places"
```

### Test 3: Obtener Recomendaciones

```bash
curl -X GET "http://localhost:8000/api/v1_recommendation/recomendaciones?preferencia=Museo&max_distancia=5"
```

### Test 4: Enviar Pregunta al Asistente IA

```bash
curl -X POST http://localhost:8000/api/v1_aiassistant/aiassistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "query_text": "¿Qué museos hay disponibles?"
  }'
```

### Test 5: Importar CSV de Lugares

```bash
curl -X POST http://localhost:8000/api/v1_quality/import \
  -F "file=@lugares.csv"
```

---

## 🛠️ Comandos Útiles

### Ver Logs

```bash
# Todos los logs en tiempo real
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f api-aiassistant

# Últimas 50 líneas
docker-compose logs --tail=50 recommendation-db

# Logs desde hace 1 hora
docker-compose logs --since 1h api-recommendation
```

### Acceder a Contenedor

```bash
# Bash en un contenedor
docker-compose exec api-recommendation bash

# SQL en base de datos
docker-compose exec recommendation-db psql -U rec_user -d recommendation_db

# Ver variables de entorno
docker-compose exec api-aiassistant env | grep -i api
```

### Recrear Servicios

```bash
# Reconstruir una sola imagen
docker-compose build api-aiassistant

# Reiniciar un servicio
docker-compose restart api-recommendation

# Recrear un servicio (down + up)
docker-compose up -d --force-recreate api-route
```

### Detener/Parar

```bash
# Parar todos sin eliminar datos
docker-compose stop

# Detener y eliminar contenedores (conserva volúmenes)
docker-compose down

# Detener y ELIMINAR TODO (incluyendo datos)
docker-compose down -v
```

---

## 🐛 Troubleshooting Común

### Problema: "Port 8000 already in use"

```bash
# Windows: Encontrar proceso en puerto
netstat -ano | findstr :8000

# Matar proceso (reemplaza PID)
taskkill /PID 12345 /F

# O cambiar puerto en docker-compose.yml:
# gateway-bff:
#   ports:
#     - "8001:8000"  # Cambio a 8001
```

### Problema: "Connection refused" en base de datos

```bash
# Verificar que la BD esté lista
docker-compose logs recommendation-db | grep "ready to accept"

# Esperar 30 segundos más y reintentar
sleep 30
curl http://localhost:8000/api/v1_recommendation/recomendaciones/health
```

### Problema: Contenedor "Exited with code 137"

```bash
# Significa que se quedó sin memoria
# Solución 1: Aumentar RAM en Docker Desktop
# Solución 2: Parar servicios innecesarios

docker-compose stop api-analytics
docker-compose stop api-audit
```

### Problema: "UnknownHostException: db-route"

```bash
# Significa que el container no puede resolver el nombre
# Solución: Reiniciar la red

docker-compose down
docker network prune
docker-compose up -d
```

### Problema: API no responde después de cambios

```bash
# Reconstruir imagen
docker-compose build --no-cache api-aiassistant

# Reiniciar servicio
docker-compose restart api-aiassistant

# O recrear completamente
docker-compose up -d --force-recreate api-aiassistant
```

---

## 📝 Archivos de Configuración Importantes

### docker-compose.yml
```bash
# Ubicación: back-end/docker-compose.yml
# Contenido: Definición de todos los servicios y bases de datos
# Modificar si: Añadir servicios, cambiar puertos, agregar volúmenes
```

### .env files

```bash
api-atenticacion/.env         # Credenciales Auth
api-aiassistant/.env          # API Keys IA
api-recommendation/.env       # Config Recommendation
api-route/.env                # Config Route
api-dataquality/.env          # Config Quality
```

### Archivos de Inicialización BD

```bash
api-aiassistant/init-db/init.sql    # Scripts de BD para AIAssistant
api-recommendation/init-db/          # Scripts de BD para Recommendation
```

---

## 🔄 Workflow de Desarrollo

### 1. Hacer Cambios en Código

```bash
# Editar archivo, ej: api-aiassistant/app/main.py
code api-aiassistant/app/main.py
```

### 2. Reconstruir Imagen

```bash
# Con volumen montado, cambios se aplican al instante
docker-compose restart api-aiassistant

# Si no ve cambios, reconstruir:
docker-compose build --no-cache api-aiassistant
docker-compose up -d api-aiassistant
```

### 3. Ver Cambios en Logs

```bash
docker-compose logs -f api-aiassistant
```

### 4. Probar

```bash
curl http://localhost:8000/api/v1_aiassistant/aiassistant/health
```

---

## 📈 Monitoring

### Dashboard Simple (Script)

```bash
#!/bin/bash
# Guarda como: monitor.sh

while true; do
  clear
  echo "=== Backend Services Status ==="
  echo "Timestamp: $(date)"
  echo ""
  docker-compose ps | grep -E "Up|Exit"
  echo ""
  echo "Gateway:" $(curl -s http://localhost:8000/health || echo "DOWN")
  echo "Auth:" $(curl -s http://localhost:8000/api/v1_auth/health || echo "DOWN")
  echo "Recommendation:" $(curl -s http://localhost:8000/api/v1_recommendation/recomendaciones/health || echo "DOWN")
  echo ""
  sleep 5
done

# Ejecutar:
chmod +x monitor.sh
./monitor.sh
```

---

## 🌐 Acceso a APIs

### Documentación Interactiva (Swagger)

Cuando los servicios estén corriendo, accede a:

- **Gateway:** http://localhost:8000/docs
- **Auth API:** http://localhost:8001/docs
- **Geo API:** http://localhost:8002/docs
- **Places API:** http://localhost:8003/docs
- **AI Assistant:** http://localhost:8009/docs
- **Recommendation:** http://localhost:8010/docs
- **Route API:** http://localhost:8011/docs

---

## 🔐 Variables de Entorno Completas

### api-atenticacion/.env
```
DATABASE_URL=postgresql://user:password@db:5432/cultureia_db
SECRET_KEY=cultureia_db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PYTHONPATH=/app
```

### api-aiassistant/.env
```
GROQ_API_KEY=gsk_XXXXXXXXXXXX
GROQ_MODEL=mixtral-8x7b-32768
DATABASE_URL=postgresql://aiassistant_user:aiassistant_password@aiassistant-db:5432/aiassistant_db
PYTHONPATH=/app
```

### api-recommendation/.env
```
DATABASE_URL=postgresql://rec_user:rec_password@recommendation-db:5432/recommendation_db
PYTHONPATH=/app
```

---

## 📞 Soporte

Si algo no funciona:

1. **Revisa logs:** `docker-compose logs [servicio]`
2. **Reinicia servicio:** `docker-compose restart [servicio]`
3. **Reconstruye imagen:** `docker-compose build --no-cache [servicio]`
4. **Nuclear option:** `docker-compose down -v && docker-compose up --build`

---

**Última actualización:** 2024  
**Versión:** 1.0.0  
**Mantenido por:** Copilot Team
