from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.db import Base, engine
from app.db import models  # noqa: F401

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
