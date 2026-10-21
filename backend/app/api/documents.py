from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from app.ingestion.pipeline import pipeline
from app.retrieval.hybrid_index import hybrid_index
from app.retrieval.retriever import document_retriever
from app.agents.document_agent import document_agent
from app.core.config_loader import config_loader
from app.core.rbac import get_current_user
from app.db.models import User
from app.schemas.query import CitationItem

router = APIRouter(prefix="/documents", tags=["Document Intelligence"])

class SearchRequest(BaseModel):
    query: str
    department: Optional[str] = None
    top_k: int = 4

class SearchResponse(BaseModel):
    query: str
    status: str
    summary: str
    citations: List[CitationItem]
    evidence_fences: List[str]
    claims: List[str]

@router.get("/list")
def list_indexed_documents():
    """List summary of all documents currently ingested and indexed in memory."""
    docs = {}
    for chunk in hybrid_index.chunks:
        doc_id = chunk.doc_id
        if doc_id not in docs:
            docs[doc_id] = {
                "doc_id": doc_id,
                "filename": chunk.metadata.get("filename", doc_id),
                "source_type": chunk.source_type,
                "department": chunk.metadata.get("department", "General"),
                "classification": chunk.metadata.get("classification", "Internal"),
                "chunk_count": 0
            }
        docs[doc_id]["chunk_count"] += 1
    return {
        "total_chunks": len(hybrid_index.chunks),
        "total_documents": len(docs),
        "documents": list(docs.values())
    }

@router.post("/search", response_model=SearchResponse)
def search_documents(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute document intelligence search through the specialized Document Agent."""
    role = current_user.role if current_user else "CXO"
    result = document_agent.process(
        query=payload.query,
        department=payload.department,
        user_role=role
    )
    return SearchResponse(
        query=payload.query,
        status=result["status"],
        summary=result["summary"],
        citations=result["citations"],
        evidence_fences=result["evidence_fences"],
        claims=result["claims"]
    )

@router.post("/reindex")
def trigger_reindex(current_user: User = Depends(get_current_user)):
    """Trigger document re-indexing from the active industry's data/unstructured folder."""
    active_ind = config_loader.active_industry_id
    data_dir = config_loader.config_dir / active_ind / "data" / "unstructured"

    if not data_dir.exists():
        raise HTTPException(status_code=404, detail=f"No unstructured directory found for {active_ind}")

    chunks, reports = pipeline.ingest_directory(data_dir)
    hybrid_index.clear()
    hybrid_index.add_chunks(chunks)

    return {
        "status": "success",
        "industry": active_ind,
        "chunks_indexed": len(chunks),
        "reports": [r.dict() for r in reports]
    }
