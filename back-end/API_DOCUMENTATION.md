# 🗺️ CulturalRoute AI - API Documentation
## Comprehensive Microservices Endpoints Reference

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Authentication Service](#1-authentication-service)
3. [Audit Service](#2-audit-service)
4. [BFF Gateway](#3-bff-gateway)
5. [Configuration Service](#4-configuration-service)
6. [Geolocation Service](#5-geolocation-service)
7. [Places Catalog Service](#6-places-catalog-service)
8. [Data Quality Service](#7-data-quality-service)
9. [AI Enrichment Service](#8-ai-enrichment-service)
10. [Analytics Service](#9-analytics-service)
11. [Service Dependencies](#service-dependencies)

---

## Overview

**Architecture:** Microservices with BFF Gateway pattern  
**Framework:** FastAPI (Python)  
**Database:** PostgreSQL (per service)  
**Authentication:** JWT Bearer Token  
**Base URL:** `http://localhost:8000`

---

## 1. Authentication Service

**Base Path:** `/auth`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Register new user
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "User Name"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true
}
```

```bash
# User login
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1QiLC...",
  "token_type": "bearer"
}
```

```bash
# Get current authenticated user
GET /auth/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true
}
```

```bash
# Health check
GET /auth/health

Response: 200 OK
{
  "status": "ok",
  "service": "auth-service"
}
```

---

## 2. Audit Service

**Base Path:** `/audit`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Create audit event
POST /audit/events
Content-Type: application/json

{
  "event_type": "lugar_visitado",
  "entity_type": "place",
  "entity_id": "uuid",
  "source_service": "frontend",
  "metadata": {
    "user_id": "uuid",
    "action": "view"
  }
}

Response: 201 Created
{
  "id": "uuid",
  "event_type": "lugar_visitado",
  "timestamp": "2026-05-05T16:03:31Z",
  ...
}
```

```bash
# List audit events (paginated)
GET /audit/events?skip=0&limit=100

Response: 200 OK
[
  {
    "id": "uuid",
    "event_type": "lugar_visitado",
    "timestamp": "2026-05-05T16:03:31Z",
    ...
  },
  ...
]
```

```bash
# Health check
GET /audit/health

Response: 200 OK
{
  "status": "healthy",
  "service": "audit-service"
}
```

---

## 3. BFF Gateway

**Base Paths:** `/api` (proxy) and `/bff` (aggregator)  
**Framework:** FastAPI  
**Status:** ✅ Active

### Gateway (Proxy Pattern)

Routes all requests to appropriate microservices:

```bash
# Dynamic routing pattern
GET/POST/PUT/PATCH/DELETE /api/{service_name}/{path:path}

Examples:
GET  /api/v1_places/places/
POST /api/v1_geo/geo/points
GET  /api/v1_config/config/parameters
```

### BFF Aggregator Endpoints

```bash
# Dashboard summary
GET /bff/dashboard

Response: 200 OK
{
  "total_places": 42,
  "total_users": 150,
  "recent_visits": [...],
  "analytics_summary": {...}
}
```

```bash
# Filtered places dashboard
GET /bff/dashplaces

Response: 200 OK
{
  "featured_products": [
    {
      "id": "uuid",
      "name": "Museo Nacional de Colombia",
      "category": "Museo",
      "status": "active",
      ...
    },
    ...
  ]
}
```

```bash
# Find nearby places
GET /bff/nearby?lat=4.636&lng=-74.063&radius_km=5

Query Parameters:
- lat (float, required): Latitude
- lng (float, required): Longitude
- radius_km (float, optional, default=5.0): Search radius in kilometers

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Museo Nacional",
    "distance_km": 0.5,
    "latitude": 4.636,
    "longitude": -74.063,
    ...
  },
  ...
]
```

```bash
# Calculate distance
GET /bff/distance?place_id_origin=uuid1&place_id_destination=uuid2

Query Parameters:
- place_id_origin (UUID, required): Starting place
- place_id_destination (UUID, required): Destination place

Response: 200 OK
{
  "origin": "Museo Nacional",
  "destination": "Teatro Colón",
  "distance_km": 2.5,
  "estimated_time_minutes": 8
}
```

```bash
# Health check
GET /bff/health

Response: 200 OK
{
  "status": "ok",
  "app": "BFF Gateway",
  "version": "1.0.0",
  "environment": "development"
}
```

### CORS Configuration
- ✅ `http://localhost:5173` (Vite/React dev)
- ✅ `http://localhost:3000`
- ✅ `http://127.0.0.1:5173`

---

## 4. Configuration Service

**Base Path:** `/config`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# List all parameters
GET /config/parameters?skip=0&limit=100

Response: 200 OK
[
  {
    "id": "uuid",
    "config_key": "MAP_DEFAULT_CENTER",
    "config_value": "7.8939,-72.5078",
    "description": "Default map center coordinates",
    "created_at": "2026-05-05T16:03:31Z"
  },
  ...
]
```

```bash
# Get parameter by ID
GET /config/parameters/by-id/{parameter_id}

Response: 200 OK
{
  "id": "uuid",
  "config_key": "API_VERSION",
  "config_value": "v1.0.0",
  ...
}
```

```bash
# Get parameter by key
GET /config/parameters/by-key/MAP_DEFAULT_CENTER

Response: 200 OK
{
  "config_key": "MAP_DEFAULT_CENTER",
  "config_value": "7.8939,-72.5078",
  ...
}
```

```bash
# Create parameter
POST /config/parameters
Content-Type: application/json

{
  "config_key": "MAX_PLACES_PER_PAGE",
  "config_value": "20",
  "description": "Maximum places per page"
}

Response: 201 Created
```

```bash
# Update parameter
PUT /config/parameters/by-key/MAX_PLACES_PER_PAGE
Content-Type: application/json

{
  "config_value": "50",
  "description": "Updated max places"
}

Response: 200 OK
```

---

## 5. Geolocation Service

**Base Path:** `/geo`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Register geo point for place
POST /geo/points
Content-Type: application/json

{
  "place_id": "uuid",
  "latitude": 4.636,
  "longitude": -74.063,
  "address": "Ak 7 #N. 28-66"
}

Response: 201 Created
{
  "id": "uuid",
  "place_id": "uuid",
  "latitude": 4.636,
  "longitude": -74.063,
  "address": "Ak 7 #N. 28-66"
}
```

```bash
# Get geo point by place
GET /geo/places/{place_id}

Response: 200 OK
{
  "place_id": "uuid",
  "latitude": 4.636,
  "longitude": -74.063,
  "address": "Ak 7 #N. 28-66"
}
```

```bash
# Find nearby places
GET /geo/nearby?lat=4.636&lng=-74.063&radius_km=5

Query Parameters:
- lat (float, required): Your latitude
- lng (float, required): Your longitude
- radius_km (float, optional, default=5.0): Radius in kilometers

Response: 200 OK
[
  {
    "place_id": "uuid",
    "name": "Museo Nacional",
    "distance_km": 0.2,
    "latitude": 4.636,
    "longitude": -74.063
  },
  ...
]
```

```bash
# Calculate distance between places
GET /geo/distance?place_id_origin=uuid1&place_id_destination=uuid2

Response: 200 OK
{
  "origin_id": "uuid1",
  "destination_id": "uuid2",
  "distance_km": 2.5
}
```

```bash
# Health check
GET /geo/health

Response: 200 OK
{
  "status": "ok",
  "service": "geo-service"
}
```

---

## 6. Places Catalog Service

**Base Path:** `/places`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Create place
POST /places/
Content-Type: application/json

{
  "name": "Museo Nacional de Colombia",
  "description": "El museo más antiguo de Colombia",
  "category": "Museo",
  "address": "Ak 7 #N. 28-66",
  "imagelink": "https://...",
  "latitude": 4.6366306,
  "longitude": -74.0635342,
  "status": "active"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "Museo Nacional de Colombia",
  ...
}
```

```bash
# List places (paginated)
GET /places/?skip=0&limit=10

Query Parameters:
- skip (int, default=0): Pagination offset
- limit (int, default=10): Page size

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Museo Nacional de Colombia",
    "category": "Museo",
    "status": "active",
    "latitude": 4.6366306,
    "longitude": -74.0635342,
    ...
  },
  ...
]
```

```bash
# Get place by ID
GET /places/{place_id}

Response: 200 OK
{
  "id": "uuid",
  "name": "Museo Nacional de Colombia",
  "description": "El museo más antiguo de Colombia",
  "category": "Museo",
  "address": "Ak 7 #N. 28-66",
  "imagelink": "https://...",
  "latitude": 4.6366306,
  "longitude": -74.0635342,
  "status": "active",
  "created_at": "2026-05-05T16:03:31Z",
  "updated_at": "2026-05-05T16:03:31Z"
}
```

```bash
# Update place (partial)
PATCH /places/{place_id}
Content-Type: application/json

{
  "name": "Museo Nacional - Updated Name",
  "status": "inactive"
}

Response: 200 OK
{
  "id": "uuid",
  "name": "Museo Nacional - Updated Name",
  "status": "inactive",
  ...
}
```

```bash
# Delete place
DELETE /places/{place_id}

Response: 200 OK
{
  "detail": "Lugar eliminado correctamente"
}
```

```bash
# Enrich place coordinates (via Nominatim)
PATCH /places/{place_id}/enrich

Response: 200 OK
{
  "id": "uuid",
  "name": "Museo Nacional de Colombia",
  "latitude": 4.6366306,  // Updated if changed
  "longitude": -74.0635342,  // Updated if changed
  ...
}
```

```bash
# Service status
GET /

Response: 200 OK
{
  "status": "Microservicio de Lugares Activo"
}
```

---

## 7. Data Quality Service

**Base Path:** `/imports`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Upload CSV file for import
POST /imports
Content-Type: multipart/form-data

Form Data:
- file: <csv_file>  // Must be .csv format

Response: 202 Accepted
{
  "batch_id": "uuid",
  "status": "processing",
  "message": "Import queued for processing"
}
```

```bash
# Get import batch status
GET /imports/{batch_id}

Response: 200 OK
{
  "batch_id": "uuid",
  "status": "completed|processing|failed",
  "processed_rows": 150,
  "valid_rows": 145,
  "invalid_rows": 5,
  "started_at": "2026-05-05T16:03:31Z",
  "completed_at": "2026-05-05T16:05:31Z"
}
```

```bash
# Get validation errors for batch
GET /imports/{batch_id}/errors

Response: 200 OK
[
  {
    "row_number": 15,
    "field_name": "latitude",
    "error_type": "INVALID_COORDINATE",
    "message": "Latitude must be between -90 and 90"
  },
  {
    "row_number": 42,
    "field_name": "category",
    "error_type": "MISSING_REQUIRED_FIELD",
    "message": "Category is required"
  }
]
```

```bash
# Health check
GET /health

Response: 200 OK
{
  "status": "ok"
}
```

### CSV Format Requirements

**Required Columns:**
- `name` (string): Place name
- `description` (string): Place description
- `category` (string): Place category
- `address` (string): Place address
- `latitude` (float): Latitude coordinate
- `longitude` (float): Longitude coordinate

**Optional Columns:**
- `imagelink` (string): Image URL
- `status` (string): "active" or "inactive"

### Processing

- **Asynchronous:** Returns 202 immediately, processes in background
- **Validation:** All rows validated before insertion
- **Atomic:** All valid rows inserted together or none
- **Audit Trail:** Import tracked in audit service

---

## 8. AI Enrichment Service

**Base Path:** `/enrichments`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Enrich single place
POST /enrichments
Content-Type: application/json

{
  "place_id": "uuid",
  "name": "Museo Nacional de Colombia",
  "description": "El museo más antiguo de Colombia",
  "category": "Museo",
  "address": "Ak 7 #N. 28-66"
}

Response: 201 Created
{
  "place_id": "uuid",
  "name": "Museo Nacional de Colombia",
  "description": "El museo más antiguo de Colombia",
  "category": "Museo",
  "tags": ["history", "culture", "museum", "bogota"],
  "confidence": 0.95,
  "enriched_at": "2026-05-05T16:03:31Z"
}
```

```bash
# Batch enrich places
POST /enrichments/batch
Content-Type: application/json

{
  "places": [
    {
      "place_id": "uuid1",
      "name": "Museo Nacional",
      ...
    },
    {
      "place_id": "uuid2",
      "name": "Teatro Colón",
      ...
    }
  ]
}

Response: 201 Created
{
  "total_places": 2,
  "successful": 2,
  "failed": 0,
  "places": [
    {
      "place_id": "uuid1",
      "tags": ["history", "museum"],
      "confidence": 0.95,
      ...
    },
    ...
  ]
}
```

```bash
# Get enrichment data
GET /enrichments/{place_id}

Response: 200 OK
{
  "place_id": "uuid",
  "name": "Museo Nacional",
  "tags": ["history", "culture"],
  "confidence": 0.95,
  "enriched_at": "2026-05-05T16:03:31Z"
}
```

```bash
# Health check
GET /health

Response: 200 OK
{
  "status": "ok",
  "service": "ai-enrichment-service"
}
```

### Enrichment Features

- **Auto-categorization:** AI-determined category
- **Tag Generation:** Relevant tags from description
- **Confidence Score:** 0.0-1.0 confidence level
- **Audit Integration:** Logged as "lugar enriquecido" event

---

## 9. Analytics Service

**Base Path:** `/analytics`  
**Framework:** FastAPI  
**Status:** ✅ Active

### Endpoints

```bash
# Calculate and save place score
POST /analytics/score
Content-Type: application/json

{
  "place_id": "uuid",
  "variables": {
    "visitor_count": 5000,
    "rating": 4.5,
    "accessibility": 0.8,
    "cultural_importance": 0.9
  }
}

Response: 200 OK
{
  "place_id": "uuid",
  "score_value": 87.5,
  "level": "excellent",
  "explanation": {
    "visitor_count_score": 25,
    "rating_score": 20,
    "accessibility_score": 16,
    "cultural_score": 26.5
  }
}
```

```bash
# Get place score
GET /analytics/places/{place_id}/score

Response: 200 OK
{
  "place_id": "uuid",
  "score_value": 87.5,
  "level": "excellent",
  "last_updated": "2026-05-05T16:03:31Z"
}
```

```bash
# Get places ranking
GET /analytics/ranking

Response: 200 OK
[
  {
    "rank": 1,
    "place_id": "uuid1",
    "name": "Museo Nacional",
    "score": 95.0,
    "level": "excellent"
  },
  {
    "rank": 2,
    "place_id": "uuid2",
    "name": "Teatro Colón",
    "score": 92.5,
    "level": "excellent"
  },
  ...
]
```

```bash
# Update place score
PUT /analytics/places/{place_id}/score
Content-Type: application/json

{
  "place_id": "uuid",
  "variables": { ... }
}

Response: 200 OK
{ ... }
```

```bash
# Delete place score
DELETE /analytics/places/{place_id}/score

Response: 200 OK
{
  "message": "Score eliminado"
}
```

### Score Levels

- **excellent:** 85+
- **good:** 70-84
- **fair:** 55-69
- **poor:** < 55

---

## Service Dependencies

```
┌─────────────────────────────────┐
│      Frontend (React/Vite)      │
│    http://localhost:5173        │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│     BFF Gateway (Aggregator)    │
│    http://localhost:8000        │
│   /api/* (proxy) /bff/* (agg)   │
└─┬───────────┬──────────┬────────┘
  │           │          │
  ▼           ▼          ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    Auth      │ │   Places     │ │     Geo      │
│  Service     │ │   Catalog    │ │   Service    │
└──────────────┘ └──────────────┘ └──────────────┘

┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    Config    │ │     Audit    │ │ AI Enrichment│
│   Service    │ │   Service    │ │   Service    │
└──────────────┘ └──────────────┘ └──────────────┘

┌──────────────┐ ┌──────────────┐
│ Data Quality │ │  Analytics   │
│   Service    │ │   Service    │
└──────────────┘ └──────────────┘
```

---

## Common Response Patterns

### Success Response
```json
{
  "id": "uuid",
  "name": "Resource Name",
  "status": "active",
  "created_at": "2026-05-05T16:03:31Z",
  "updated_at": "2026-05-05T16:03:31Z"
}
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "invalid email format",
      "type": "value_error.email"
    }
  ]
}
```

### Pagination
```json
{
  "data": [...],
  "skip": 0,
  "limit": 10,
  "total": 150
}
```

---

## Authentication

All protected endpoints require:

```bash
Authorization: Bearer <access_token>
```

**To get a token:**
1. Call `POST /auth/login` with email and password
2. Receive `access_token` in response
3. Include in `Authorization` header for protected requests

---

## Rate Limiting

No rate limiting currently implemented. Recommended for production.

---

## Status Summary

| Service | Status | Endpoints | Last Updated |
|---------|--------|-----------|--------------|
| Authentication | ✅ | 4 | 2026-05-05 |
| Audit | ✅ | 3 | 2026-05-05 |
| BFF Gateway | ✅ | 6 | 2026-05-05 |
| Configuration | ✅ | 6 | 2026-05-05 |
| Geolocation | ✅ | 5 | 2026-05-05 |
| Places Catalog | ✅ | 8 | 2026-05-05 |
| Data Quality | ✅ | 4 | 2026-05-05 |
| AI Enrichment | ✅ | 4 | 2026-05-05 |
| Analytics | ✅ | 5 | 2026-05-05 |
| AI Assistant | ❌ | - | - |
| Route | ❌ | - | - |

**Total:** 45+ active endpoints across 9 services

---

**Generated:** 2026-05-05  
**API Version:** v1  
**Environment:** Development (localhost:8000)
