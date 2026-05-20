from fastapi import FastAPI
from src.api.router import router
from src.infrastructure.database import engine, Base

# Esto crea las tablas en PostgreSQL automáticamente al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CulturalRoute AI - Place Service")

# Incluimos las rutas del microservicio
app.include_router(router)

@app.get("/")
def root():
    return {"status": "Microservicio de Lugares Activo"}
