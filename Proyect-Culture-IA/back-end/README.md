# 📚 Documentación Backend - Index

## 🎯 Documentos Principales (LEER ESTOS)

### 1. **QUICK_START.md** ⭐ COMIENZA AQUÍ
Guía de 30 segundos para empezar. Todo lo que necesitas saber para levantar los servicios.

**Contiene:**
- Requisitos previos
- Instalación paso a paso
- Primeros tests
- Comandos útiles
- Troubleshooting común
- Workflow de desarrollo

**Leer si:** Acabas de clonar el proyecto o necesitas levantar el backend rápidamente.

---

### 2. **ARCHITECTURE_AND_INTEGRATION.md** 📐 ENTIENDE LA ESTRUCTURA
Visión completa de la arquitectura de microservicios, cómo se conectan los servicios.

**Contiene:**
- Diagrama de arquitectura
- Tabla de todos los servicios (puertos, bases de datos)
- Estructura de docker-compose.yml
- Cómo inicia todo
- Dependencias entre servicios
- Performance esperado

**Leer si:** Quieres entender cómo funciona todo en conjunto, quieres agregar nuevos servicios, o necesitas debuggear problemas de conectividad.

---

### 3. **SERVICES_GUIDE.md** 🔧 USA LOS SERVICIOS
Guía detallada de cada servicio individual. Endpoints, ejemplos, variables de entorno.

**Contiene:**
- Guía de cada uno de los 11 servicios
- Endpoints disponibles
- Ejemplos de curl/fetch
- Variables de entorno específicas
- Parámetros de consultas
- Dependencias entre servicios

**Leer si:** Necesitas usar/integrar un servicio específico, quieres ver ejemplos de requests, o necesitas entender qué hace cada API.

---

## 📋 Documentos Secundarios (Archivos Legados)

Estos archivos contienen la misma información pero de forma duplicada. Se mantienen para referencia pero **NO** necesitas leerlos si tienes los 3 principales:

- `README_RECOMMENDATION_API.md` → Ver **SERVICES_GUIDE.md** (sección Recommendation)
- `RECOMMENDATION_SETUP_SUMMARY.md` → Ver **QUICK_START.md** + **SERVICES_GUIDE.md**
- `API_RECOMMENDATION_FINAL_STATUS.md` → Ver **SERVICES_GUIDE.md** (sección Recommendation)
- `RECOMMENDATION_API_INTEGRATION.md` → Ver **ARCHITECTURE_AND_INTEGRATION.md**
- `API_AIASSISTANT_GATEWAY.md` → Ver **SERVICES_GUIDE.md** (sección AIAssistant)
- `GATEWAY_INTEGRATION_SUMMARY.md` → Ver **ARCHITECTURE_AND_INTEGRATION.md**
- `API_DOCUMENTATION.md` → Ver **SERVICES_GUIDE.md**
- `GROQ_MIGRATION_SUMMARY.md` → Ver **SERVICES_GUIDE.md** (AIAssistant) + **QUICK_START.md** (setup)
- `OPENROUTER_MIGRATION_SUMMARY.md` → Ver **SERVICES_GUIDE.md** (AIAssistant) + **QUICK_START.md** (setup)
- `VERIFY_RECOMMENDATION_INTEGRATION.md` → Ver **QUICK_START.md** (testing)
- `RECOMMENDATION_DOCS_INDEX.md` → Este archivo (index consolidado)
- `ARCHITECTURE_DIAGRAM.md` → Ver **ARCHITECTURE_AND_INTEGRATION.md** (diagrama)

---

## 🚀 Quick Navigation

### Necesito...

**Levantar el backend** → `QUICK_START.md`

**Entender la arquitectura** → `ARCHITECTURE_AND_INTEGRATION.md`

**Usar un servicio específico** → `SERVICES_GUIDE.md`

**Configurar AI Assistant** → `QUICK_START.md` (sección "Configuración Inicial") + `SERVICES_GUIDE.md` (sección "Asistente IA")

**Integrar un nuevo servicio** → `ARCHITECTURE_AND_INTEGRATION.md` + luego modifica `docker-compose.yml`

**Debuggear un problema** → `QUICK_START.md` (troubleshooting) + `docker-compose logs [servicio]`

**Ver ejemplos de requests** → `SERVICES_GUIDE.md` (ejemplos en cada sección)

**Entender puertos y bases de datos** → `ARCHITECTURE_AND_INTEGRATION.md` (tablas de puertos)

**Configurar variables de entorno** → `QUICK_START.md` (sección "Configuración Inicial")

---

## 📊 Mapa de Servicios

```
┌─────────────────────────────────────────────────┐
│          Frontend (3000, 5173)                  │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │   Gateway (8000)    │
        └──────────┬──────────┘
        ┌──────────┴──────────────────────────────┐
        │                                         │
    ┌───▼───┐  ┌───▼──┐  ┌────▼──┐  ┌────▼──┐
    │Auth   │  │Geo   │  │Places │  │Config │ ...
    │(8001) │  │(8002)│  │(8003) │  │(8004) │
    └───┬───┘  └───┬──┘  └────┬──┘  └────┬──┘
        │          │          │          │
    ┌───▼───┐  ┌───▼──┐  ┌────▼──┐  ┌────▼──┐
    │DB     │  │DB    │  │DB     │  │DB     │
    │(5432) │  │(5433)│  │(5434) │  │(5435) │
    └───────┘  └──────┘  └───────┘  └───────┘
```

---

## 📌 Checklist de Inicio

- [ ] Leo `QUICK_START.md`
- [ ] Instalo Docker Desktop
- [ ] Ejecuto `docker-compose up --build`
- [ ] Espero 30 segundos
- [ ] Ejecuto `curl http://localhost:8000/health`
- [ ] Leo `ARCHITECTURE_AND_INTEGRATION.md` para entender la estructura
- [ ] Identifico qué servicio necesito usar
- [ ] Leo la sección correspondiente en `SERVICES_GUIDE.md`
- [ ] Hago mis primeros requests

---

## 🔗 Enlaces Útiles

| Recurso | URL |
|---------|-----|
| Swagger API Gateway | http://localhost:8000/docs |
| Swagger Auth API | http://localhost:8001/docs |
| Swagger Places API | http://localhost:8003/docs |
| Swagger AI Assistant | http://localhost:8009/docs |
| Swagger Recommendation | http://localhost:8010/docs |
| PostgreSQL DB | localhost:5432-5442 (ver tabla de puertos) |

---

## 📝 Tabla de Referencia Rápida

| Componente | Ubicación | Detalles |
|-----------|-----------|---------|
| Configuración Central | `docker-compose.yml` | Orquestación de servicios |
| Gateway Config | `api-bff-gateway/app/core/config.py` | URLs de servicios |
| Gateway Rutas | `api-bff-gateway/app/services/upstreams.py` | Mapeo de endpoints |
| Auth API | `api-atenticacion/` | Autenticación |
| Recommendation DB | `recommendation-db` puerto 5441 | Historial recomendaciones |
| AI Assistant Config | `api-aiassistant/.env` | API Keys (Groq/OpenAI) |
| Quality Importer | `api-dataquality/` | Importar CSV de lugares |

---

## 🎓 Secuencia de Aprendizaje Recomendada

1. **Primer día:** Lee `QUICK_START.md` y levanta el backend
2. **Segundo día:** Lee `ARCHITECTURE_AND_INTEGRATION.md` y entiende la estructura
3. **Día 3+:** Lee `SERVICES_GUIDE.md` y aprende cada servicio específico
4. **Integración:** Modifica `docker-compose.yml`, `config.py` y `upstreams.py` según necesites

---

## 🛠️ Troubleshooting Rápido

**¿No funciona algo?**
1. Revisa: `docker-compose logs [servicio]`
2. Reinicia: `docker-compose restart [servicio]`
3. Reconstruye: `docker-compose build --no-cache [servicio]`
4. Si todo falla: `docker-compose down -v && docker-compose up --build`

**¿No entiendes algo?**
1. Busca en `QUICK_START.md` (setup)
2. Busca en `ARCHITECTURE_AND_INTEGRATION.md` (estructura)
3. Busca en `SERVICES_GUIDE.md` (funcionalidad)

---

## 📦 Versión & Mantenimiento

- **Versión:** 1.0.0
- **Última actualización:** 2024
- **Mantenido por:** Copilot Team
- **Estado:** ✅ Listo para Producción

---

## 💡 Pro Tips

- Usa `docker-compose logs -f [servicio]` para ver logs en tiempo real
- Accede a Swagger en cada puerto `/docs` para documentación interactiva
- Usa `docker-compose ps` para ver estado rápidamente
- Monta volúmenes en `docker-compose.yml` para desarrollo hot-reload
- Usa `-d` flag en `docker-compose up -d` para ejecutar en background
- Usa `--build` flag para reconstruir imágenes: `docker-compose up --build`

---

**¿Preguntas? Lee los 3 documentos principales en este orden:**
1. QUICK_START.md
2. ARCHITECTURE_AND_INTEGRATION.md  
3. SERVICES_GUIDE.md

**Eso es todo lo que necesitas.** 🚀
