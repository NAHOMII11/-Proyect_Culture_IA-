# Audit Service — CulturalRoute AI (Sprint 3)

Microservicio de auditoría y trazabilidad funcional. Guarda eventos que otros servicios envían con `POST /audit/events`.

---

## Qué se implementó

### Backend (`back-end/api-audit/`)

| Archivo / carpeta | Qué hace |
|-------------------|----------|
| `app/main.py` | FastAPI, CORS, health, creación de tablas al arrancar |
| `app/routers/audit.py` | Endpoints REST de auditoría |
| `app/application/audit_service.py` | Lógica: registrar, listar, resumen, detalle |
| `app/application/errors.py` | Errores de aplicación |
| `app/domain/audit_event.py` | Modelo de evento, filtros, `create_audit_event()` |
| `app/infrastructure/audit_repository.py` | PostgreSQL (`audit_db`), tabla `audit_events` |
| `app/schemas/audit_schema.py` | DTOs Pydantic (request/response) |
| `Dockerfile` | Imagen del servicio |
| `docker-compose.yml` | `audit_db` + `audit_api` (solo audit) |
| `requirements.txt` | Dependencias Python |

**Patrones en código:** Service Layer, Repository, Factory (`create_audit_event`), DTOs.

**Base de datos propia:** `audit_db` (PostgreSQL). 

### Frontend (módulo audit)

| Archivo | Qué se agregó |
|---------|----------------|
| `front-end/src/pages/AuditPage.jsx` | Pantalla de monitoreo `/auditoria` |
| `front-end/src/services/auditService.js` | Cliente HTTP vía gateway (`localhost:8000`) |
| `front-end/src/routes/AppRouter.jsx` | Ruta `/auditoria` |
| `front-end/src/components/layout/Header.jsx` | Enlace “Auditoría” en el menú |
| `front-end/src/styles/global.css` | Estilos `.audit-*` |

### Docker del equipo (`back-end/docker-compose.yml`)

- Servicios `audit_db` y `audit_api` 
- `audit_api` en puerto **8008**; BD en puerto host **5439** 

---

## Puertos

| Componente | Puerto |
|------------|--------|
| Audit API | **8008** |
| Gateway (BFF) | **8000** |
| Frontend | **5173** |
| PostgreSQL audit (compose `api-audit`) | **5436** |

---

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| POST | `/audit/events` | Registrar evento |
| GET | `/audit/events` | Listar (filtros opcionales) |
| GET | `/audit/events/summary` | Resumen por tipo y servicio |
| GET | `/audit/events/{event_id}` | Detalle de un evento |

**Filtros en GET `/audit/events`:** `event_type`, `source_service`, `reference_id`, `date_from`, `date_to`, `skip`, `limit`.

---

## Endpoints de prueba

### Directo al servicio (puerto 8008)

```bash
# Health
curl http://localhost:8008/health

# Crear evento
curl -X POST http://localhost:8008/audit/events \
  -H "Content-Type: application/json" \
  -d "{\"event_type\":\"place_enriched\",\"source_service\":\"ai-enrichment-service\",\"reference_id\":\"test-001\",\"payload_summary\":{\"confidence\":0.9}}"

# Listar eventos
curl "http://localhost:8008/audit/events?limit=10"

# Resumen
curl http://localhost:8008/audit/events/summary

# Detalle (reemplazar UUID)
curl http://localhost:8008/audit/events/{event_id}
```

### Vía gateway (puerto 8000)

Prefijo: `/api/v1_audit`

```bash
curl http://localhost:8000/api/v1_audit/health

curl -X POST http://localhost:8000/api/v1_audit/audit/events \
  -H "Content-Type: application/json" \
  -d "{\"event_type\":\"score_calculated\",\"source_service\":\"analytics-service\",\"reference_id\":\"test-002\",\"payload_summary\":{\"score_value\":0.81}}"

curl "http://localhost:8000/api/v1_audit/audit/events?limit=10"

curl http://localhost:8000/api/v1_audit/audit/events/summary
```

### UI

- `http://localhost:5173/auditoria`

---

## Cuerpo mínimo para POST `/audit/events`

```json
{
  "event_type": "score_calculated",
  "source_service": "analytics-service",
  "reference_id": "uuid-del-recurso",
  "payload_summary": {
    "score_value": 0.81
  }
}
```

## Variables de entorno

- `DATABASE_URL` — default: `postgresql+psycopg://audit_user:audit_pass@audit_db:5432/audit_db`

---

## Ejecutar

```bash
# Solo audit
cd back-end/api-audit
docker compose up --build

# Stack completo (desde back-end/)
docker compose up -d audit_db audit_api gateway-bff
```

Frontend:

```bash
cd front-end
npm run dev
```
