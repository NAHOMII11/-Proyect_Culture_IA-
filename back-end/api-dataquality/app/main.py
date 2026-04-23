from fastapi import FastAPI

from app.api.v1.routes.imports import router as imports_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(imports_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}