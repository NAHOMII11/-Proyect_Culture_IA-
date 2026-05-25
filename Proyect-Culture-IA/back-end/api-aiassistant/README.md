# AI Assistant API

FastAPI-based service for handling chat queries with Groq AI and persisting results to PostgreSQL.

## Features

- Chat query submission to Groq.com (fast inference with Mixtral, Llama, Gemma models)
- Query history persistence in PostgreSQL
- RESTful API endpoints for chat management
- Docker containerization with database service
- Health checks and database connectivity verification

## Setup

### Environment Variables

Create a `.env` file with:

```
DATABASE_URL=postgresql+psycopg2://aiassistant_user:aiassistant_password@aiassistant-db:5432/aiassistant_db
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
PYTHONPATH=/app
```

**Available Models on Groq:**
- `llama-3.1-70b-versatile` - Recomendado (Alta calidad)
- `llama-3.1-8b-instant` - Rápido y ligero
- `mixtral-8x7b-32768` - ⚠️ Descontinuado (usar llama-3.1-70b-versatile)
- https://console.groq.com/docs/models

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database (or use Docker):
```bash
docker-compose up aiassistant-db
```

3. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8009
```

## Docker Deployment

The API is deployed as part of the main backend docker-compose:

```bash
cd ../
docker-compose up api-aiassistant aiassistant-db
```

## API Endpoints

### POST /aiassistant/chat
Submit a query to the AI assistant and save to database

**Request:**
```json
{
  "user_id": "user-123",
  "query_text": "What is cultural heritage?"
}
```

**Response:**
```json
{
  "query_id": "uuid",
  "user_id": "user-123",
  "query_text": "What is cultural heritage?",
  "response_text": "Cultural heritage refers to...",
  "ai_provider": "groq",
  "created_at": "2024-01-15T10:30:00",
  "status": "success"
}
```

### GET /aiassistant/chat/{query_id}
Retrieve a specific query and its response

**Response:**
```json
{
  "query_id": "uuid",
  "user_id": "user-123",
  "query_text": "What is cultural heritage?",
  "response_text": "Cultural heritage refers to...",
  "ai_provider": "groq",
  "created_at": "2024-01-15T10:30:00",
  "status": "success"
}
```

### GET /aiassistant/chat
List chat history with pagination

**Query Parameters:**
- `user_id` (optional): Filter by user
- `skip` (optional, default=0): Pagination offset
- `limit` (optional, default=10): Pagination limit

**Response:**
```json
{
  "total": 42,
  "skip": 0,
  "limit": 10,
  "items": [...]
}
```

### GET /aiassistant/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Database Schema

### chat_queries table
- `id` (UUID): Primary key
- `user_id` (String): User identifier
- `query_text` (Text): User's query
- `response_text` (Text): AI response
- `ai_provider` (String): Provider used (groq)
- `status` (String): Query status (pending, success, error)
- `metadata` (JSON): Additional data (tokens, cost, model, etc.)
- `created_at` (Timestamp): Query submission time
- `updated_at` (Timestamp): Last update time

## Architecture

```
api-aiassistant/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── domain/
│   │   ├── __init__.py
│   │   └── models.py        # SQLAlchemy models
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database.py      # Database setup
│   │   └── repository.py    # Data access layer
│   └── application/
│       ├── __init__.py
│       ├── schemas.py       # Pydantic schemas
│       └── services.py      # Business logic
├── init-db/
│   └── init.sql             # Database initialization
├── Dockerfile
├── requirements.txt
└── .env
```

## Integration

This API is integrated with the main docker-compose orchestration and connected through the BFF gateway at `http://gateway-bff:8000/api/v1_aiassistant/*`

For local testing without BFF, access directly at `http://localhost:8009`

## Getting Groq API Key

1. Go to https://console.groq.com
2. Sign up or login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Add it to your `.env` file as `GROQ_API_KEY`
