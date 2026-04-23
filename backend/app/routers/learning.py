from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.learning import VectorizeResponse
from app.services.vectorize_service import vectorize_chat_data

router = APIRouter(prefix="/learning", tags=["learning"])

DbDep = Annotated[Session, Depends(get_db)]


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
