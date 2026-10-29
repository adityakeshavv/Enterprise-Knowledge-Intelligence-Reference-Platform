from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.seeder import seed_database
from app.core.config_loader import config_loader
from app.api.auth import router as auth_router
from app.api.config import router as config_router
from app.api.query import router as query_router
from app.api.documents import router as documents_router
from app.api.sql import router as sql_router
from app.api.audit import router as audit_router
from app.api.evaluation import router as evaluation_router
from app.ingestion.pipeline import pipeline
from app.retrieval.hybrid_index import hybrid_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database initialized & seeded, configurations loaded
    seed_database()
    config_loader.reload_all()

    # Index unstructured documents for active industry
    active_ind = config_loader.active_industry_id
    data_dir = config_loader.config_dir / active_ind / "data" / "unstructured"
    if data_dir.exists():
        chunks, _ = pipeline.ingest_directory(data_dir)
        hybrid_index.clear()
        hybrid_index.add_chunks(chunks)
        print(f"[{settings.APP_NAME}] Ingested {len(chunks)} document chunks into Hybrid Index.")

    print(f"[{settings.APP_NAME}] Startup complete. Active industry: {config_loader.active_industry_id}")
    yield
    # Shutdown logic if needed
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

# Mount API Routers
app.include_router(auth_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(sql_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(evaluation_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "active_industry": config_loader.active_industry_id,
        "available_industries": [i["id"] for i in config_loader.list_available_industries()]
    }

# Mount frontend production build if available
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
