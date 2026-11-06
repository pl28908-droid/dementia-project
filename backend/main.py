"""FastAPI application entry point."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from . import models  # noqa: F401 - registers table metadata
from .api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMARAN API",
    description=(
        "Prototype API for cognitive activity session tracking and user-provided memory notes. "
        "Not a diagnostic or clinical system."
    ),
    version="0.1.0",
)
app.include_router(router)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
def landing_page():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "smaran-api"}
