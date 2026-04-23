from fastapi import FastAPI

from app.api.routes.enrichments import router as enrichments_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

settings = get_settings()

app = FastAPI(title=settings.app_name)

Base.metadata.create_all(bind=engine)

app.include_router(enrichments_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}