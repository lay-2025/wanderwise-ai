from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.learning import VectorizeResponse, SearchResponse, VisualizeResponse
from app.services.vectorize_service import vectorize_chat_data
from app.services.search_service import search_similar_chunks
from app.services.visualize_service import get_visualize_data

router = APIRouter(prefix="/learning", tags=["learning"])

DbDep = Annotated[Session, Depends(get_db)]

QueryParam = Annotated[str, Query(min_length=1, description="検索クエリ")]
NResultsParam = Annotated[int, Query(ge=1, le=20, description="返却件数（1〜20）")]
SourceFilter = Annotated[str | None, Query(description="ソースでフィルタ（chat / upload / manual）")]
CategoryFilter = Annotated[str | None, Query(description="カテゴリでフィルタ")]


@router.post("/vectorize", response_model=VectorizeResponse)
def vectorize(db: DbDep) -> VectorizeResponse:
    try:
        result = vectorize_chat_data(
            db,
            chroma_host=settings.chroma_server_host,
            chroma_port=settings.chroma_server_http_port,
            ollama_url=settings.ollama_base_url,
        )
        return VectorizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=SearchResponse)
def search(
    q: QueryParam,
    n_results: NResultsParam = 5,
    source: SourceFilter = None,
    category: CategoryFilter = None,
) -> SearchResponse:
    try:
        return search_similar_chunks(
            query=q,
            n_results=n_results,
            source=source,
            category=category,
            chroma_host=settings.chroma_server_host,
            chroma_port=settings.chroma_server_http_port,
            ollama_url=settings.ollama_base_url,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualize", response_model=VisualizeResponse)
def visualize(db: DbDep) -> VisualizeResponse:
    try:
        return get_visualize_data(
            db,
            chroma_host=settings.chroma_server_host,
            chroma_port=settings.chroma_server_http_port,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
