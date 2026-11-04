import sys
from pathlib import Path

# Ensure backend directory is on sys.path so 'import app...' works from any working directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
if str(_BACKEND_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR.parent))

from contextlib import asynccontextmanager
import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import ensure_database_initialized
from app.db.seeder import seed_database
from app.core.config_loader import config_loader
from app.api.auth import router as auth_router
from app.api.config import router as config_router
from app.api.query import router as query_router
from app.api.documents import router as documents_router
from app.api.sql import router as sql_router
from app.api.audit import router as audit_router
from app.api.evaluation import router as evaluation_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lightweight initialization on app startup
    try:
        ensure_database_initialized()
        config_loader.reload_all()
        print(f"[{settings.APP_NAME}] Startup complete. Active industry: {config_loader.active_industry_id}")
    except Exception as e:
        print(f"[{settings.APP_NAME}] Startup warning: {e}")
    yield
    print(f"[{settings.APP_NAME}] Shutting down cleanly.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Knowledge Intelligence Reference Platform - Multi-Agent RAG with Evidence Validation & Auditing",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"[ERROR] Unhandled exception on {request.method} {request.url.path}: {tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{type(exc).__name__}: {str(exc)}",
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": [line.strip() for line in tb.splitlines()[-6:] if line.strip()]
        }
    )

# Mount API Routers (mounted both at /api and root / so any proxy or gateway path matches)
api_routers = [
    auth_router,
    config_router,
    query_router,
    documents_router,
    sql_router,
    audit_router,
    evaluation_router,
]

for r in api_routers:
    app.include_router(r, prefix="/api")
    app.include_router(r)

@app.get("/api/health")
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "active_industry": config_loader.active_industry_id,
        "available_industries": [i["id"] for i in config_loader.list_available_industries()]
    }

# Mount frontend production build if available (local monolithic mode only, Vercel routes frontend directly)
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

if not os.environ.get("VERCEL"):
    frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
