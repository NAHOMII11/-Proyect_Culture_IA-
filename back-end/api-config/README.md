# Config — CulturalRoute AI

**FastAPI** que persiste y expone **parámetros configurables** del sistema (pesos de scoring, radios, límites, listas JSON, etc.) en PostgreSQL (`config_db`). No implementa lógica de scoring ni de rutas: solo **clave → valor** vía API.

## Requisitos

- Python **3.11+** (versiones concretas en `requirements.txt`)
- Docker y Docker Compose (para levantar la BD)
- FastAPI, Uvicorn, SQLAlchemy, psycopg, Pydantic (instalados con `requirements.txt`)


## Cómo correr

**Con Docker (API + Postgres)**

Contenedores: **`config_api`** (API) y **`config_db`** (PostgreSQL, base `config_db`). Usuario/contraseña por defecto: `config_user` / `config_password`.

1. **Primera vez** (o cuando cambies `Dockerfile` / `requirements.txt`): construye la imagen y levanta todo:

```bash
cd api-config
docker compose up -d --build
```

2. más rápido

```bash
cd api-config
docker compose up -d
```
```

- API: `http://localhost:8010` · Docs: `http://localhost:8010/docs`  
- Postgres en el host: **5435**

**Solo API en local:** define `DATABASE_URL` (ej. si ya se levanto solo la BD con Docker y expone el puerto **5435**):**

```text
postgresql+psycopg://config_user:config_password@localhost:5435/config_db
```

```bash
cd api-config
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

## Endpoints

### `GET http://localhost:8010/health`

Comprueba que el servicio responde.

**Responde:**

```json
{ "status": "ok", "service": "config" }
```

---

### `GET http://localhost:8010/config/parameters`

Lista todos los parámetros.

**Responde**

```json
[
  {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "config_key": "scoring.weights",
    "config_value": "{\"data_quality\":0.3,\"cultural_relevance\":0.4,\"accessibility\":0.3}",
    "description": "Pesos del scoring por variable (JSON).",
    "created_at": "2026-04-07T12:00:00+00:00",
    "updated_at": "2026-04-07T12:00:00+00:00"
  }
]
```

---

### `GET http://localhost:8010/config/parameters/by-key/scoring.weights`

Obtiene un parámetro por clave (ej. `scoring.weights`).

**Responde** (un solo objeto, `200 OK`):

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "config_key": "scoring.weights",
  "config_value": "{\"data_quality\":0.3,\"cultural_relevance\":0.4,\"accessibility\":0.3}",
  "description": "Pesos del scoring por variable (JSON).",
  "created_at": "2026-04-07T12:00:00+00:00",
  "updated_at": "2026-04-07T12:00:00+00:00"
}
```

### `GET http://localhost:8010/config/parameters/by-id/{uuid}`

Obtiene un parámetro por `id`.

---

### `POST http://localhost:8010/config/parameters`

Crea un parámetro.

**Request body:**

```json
{
  "config_key": "route.max_places_default",
  "config_value": "8",
  "description": "Máximo de lugares por ruta por defecto"
}
```

**Responde:** `201` — objeto del parámetro creado.

---

### `PUT http://localhost:8010/config/parameters/by-key/{config_key}`

Actualiza `config_value` y/o `description`.

**Request body** (al menos uno de los dos campos):

```json
{
  "config_value": "{\"data_quality\":0.35,\"cultural_relevance\":0.35,\"accessibility\":0.3}",
  "description": "Pesos actualizados"
}
```

**Responde:** objeto actualizado.

## Pruebas

```bash
cd api-config
python -m pytest -q
```

