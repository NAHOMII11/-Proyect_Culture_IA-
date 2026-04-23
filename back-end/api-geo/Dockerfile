FROM python:3.11-alpine

WORKDIR /app

ENV DATABASE_URL=postgresql://postgres:postgres@localhost:5433/geo_db \
    GEO_SERVICE_PORT=8002

# Alpine es más rápido y no necesita compilación para psycopg2-binary
COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]