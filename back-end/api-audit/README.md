## Audit Service - CulturalRoute AI

Microservicio de auditoría para **registrar eventos funcionales/operativos** del sistema (ej.: *lugar enriquecido*, *score recalculado*, *ruta generada*, *interacción del asistente*).  
**No reemplaza logs técnicos**: sirve para trazabilidad a nivel plataforma.

### Stack
- **API**: FastAPI
- **DB**: PostgreSQL (`audit_db`)

### Variables de entorno
- **`DATABASE_URL`** (opcional): cadena de conexión a PostgreSQL.  
  Si no se define, usa por defecto:

```bash
postgresql+psycopg://audit_user:audit_pass@audit_db:5432/audit_db
```

### Ejecutar local (sin Docker)
En `back-end/api-audit`:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007
```

API disponible en `http://localhost:8007`

### Ejecutar con Docker
En `back-end/api-audit`:

```bash
docker-compose up --build
```

Esto levanta:
- **PostgreSQL** en `localhost:5436`
- **API** en `localhost:8007`

### Endpoints
Base URL:
- Local: `http://localhost:8007`
- Docker: `http://localhost:8007`

URLs completas:
- `GET http://localhost:8007/health`
- `POST http://localhost:8007/audit/events`
- `GET http://localhost:8007/audit/events?skip=0&limit=100`

### Ejemplo: crear un evento
Request:

```json
{
  "event_type": "lugar enriquecido",
  "source_service": "ai-enrichment-service",
  "reference_id": "place_id:uuid-o-identificador-del-lugar",
  "payload_summary": {
    "normalized_category": "museo",
    "labels": ["patrimonio", "historia"],
    "confidence": 0.87
  }
}
```

Respuesta (ejemplo):

```json
{
  "id": "uuid-generado",
  "event_type": "lugar enriquecido",
  "source_service": "ai-enrichment-service",
  "reference_id": "place_id:uuid-o-identificador-del-lugar",
  "payload_summary": {
    "normalized_category": "museo",
    "labels": ["patrimonio", "historia"],
    "confidence": 0.87
  },
  "created_at": "2026-04-21T00:00:00.000000"
}
```