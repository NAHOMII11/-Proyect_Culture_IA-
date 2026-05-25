# API Recommendation - Referencia Rápida

## 🚀 Iniciar

```bash
cd back-end
docker-compose up -d
```

## 🧪 Tests Rápidos

### Health Check
```bash
curl http://localhost:8000/api/v1_recommendation/recomendaciones/health
```

### Get All Recommendations
```bash
curl http://localhost:8000/api/v1_recommendation/recomendaciones
```

### Filter by Category
```bash
curl "http://localhost:8000/api/v1_recommendation/recomendaciones?preferencia=Museo"
```

### Filter by Distance
```bash
curl "http://localhost:8000/api/v1_recommendation/recomendaciones?max_distancia=3.0"
```

## 📊 Response Example

```json
{
  "place_id": "place-123",
  "name": "Museo del Oro",
  "category": "Museo",
  "relevance_index": 8.5,
  "distance_km": 2.3,
  "explanation": [
    "Excellent cultural relevance score (9.0)",
    "Very close to your location (2.3 km)",
    "Matches your 'Museo' preference"
  ]
}
```

## 🔐 Database

**External (localhost):**
- Host: `localhost`
- Port: `5441`
- User: `rec_user`
- Password: `rec_password`
- Database: `recommendation_db`

**Internal (Docker):**
- Host: `recommendation-db`
- Port: `5432`

## 📋 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recomendaciones` | Get recommendations |
| GET | `/recomendaciones/health` | Health check |

## ⚙️ Configuration Files Modified

1. **docker-compose.yml** - Added db-recommendation and api-recommendation services
2. **config.py** - Added recommendation_api_url
3. **upstreams.py** - Added v1_recommendation mapping
4. **Dockerfile** - Changed port to 8010
5. **main.py** - Added CORS, health endpoint

## 🎯 Status

✅ **READY TO USE**

All services are configured and running through docker-compose.
