# AI Enrichment Service (Mock)

Servicio mock de enriquecimiento de lugares culturales con IA simulada usando **FastAPI**.

## Carpetas modificadas

```
services/ai-enrichment-service/
├── app.py                 ← servicio FastAPI y lógica mock
├── requirements.txt       ← dependencias del servicio (FastAPI, uvicorn, pydantic)
├── README.md              ← este archivo
```

> ⚠️ Solo se modifican archivos dentro de `services/ai-enrichment-service/`. No se toca ninguna otra carpeta del proyecto.

## Endpoints

### `GET /health`
Verifica que el servicio esté corriendo.

**Response:**
```json
{ "status": "ok", "service": "ai-enrichment-service", "timestamp": "..." }
```

---

### `POST /enrichments`
Enriquece un lugar con categoría normalizada, etiquetas y nivel de confianza.

**Request body:**
```json
{
  "place_id": "place-001",
  "name": "Museo Nacional de Arte",
  "description": "Exhibición permanente de arte colonial y contemporáneo"
}
```

**Response:**
```json
{
  "place_id": "place-001",
  "name": "Museo Nacional de Arte",
  "description": "Exhibición permanente de arte colonial y contemporáneo",
  "category": "Museo",
  "tags": ["arte", "historia", "exhibición", "cultura", "educación"],
  "confidence": 0.93,
  "enriched_at": "2026-04-02T21:00:00.000Z"
}
```

---

### `POST /enrichments/batch`
Enriquece múltiples lugares en una sola llamada.

**Request body:**
```json
{
  "places": [
    { "place_id": "p1", "name": "Parque Central", "description": "Gran parque con jardines y áreas verdes" },
    { "place_id": "p2", "name": "Teatro Municipal", "description": "Espectáculos de danza y ópera" }
  ]
}
```

**Response:**
```json
{
  "enriched": [ ...array de resultados... ],
  "total": 2
}
```

---

## Base de datos y persistencia

- Se utiliza **SQLite** para almacenar los lugares enriquecidos automáticamente.
- El modelo Place almacena: place_id, name, description, category, tags, confidence, enriched_at.
- Puedes consultar todos los lugares enriquecidos con:

### `GET /places`
Devuelve todos los lugares enriquecidos guardados en la base de datos.

**Response:**
```json
[
  {
    "place_id": "place-001",
    "name": "Museo Nacional de Arte",
    "description": "Exhibición permanente de arte colonial y contemporáneo",
    "category": "Museo",
    "tags": ["arte", "historia", "exhibición", "cultura", "educación"],
    "confidence": 0.93,
    "enriched_at": "2026-04-02T21:00:00.000Z"
  },
  ...
]
```

---

## Cómo correr localmente

```bash
cd services/ai-enrichment-service
pip install -r requirements.txt
uvicorn app:app --reload --port 3000
# Servidor en http://localhost:3000
```

---

## Uso con Docker

### Dockerfile
Ya incluido en el proyecto. Construye la imagen y ejecuta el contenedor:

```bash
docker build -t ai-enrichment-service .
docker run -p 3000:3000 ai-enrichment-service
```

### docker-compose.yml
Ya incluido en el proyecto. Para levantar el servicio y persistir la base de datos:

```bash
docker-compose up --build
```

Esto expone el API en http://localhost:3000 y la base de datos SQLite se mantiene en el host.

---

## Notas
- No se requiere configuración adicional para la base de datos, se crea automáticamente.
- El servicio es completamente mock, no usa IA real ni llamadas externas.
- Puedes modificar la lógica de enriquecimiento en `app.py`.
