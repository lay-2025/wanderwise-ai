import uuid
from typing import Annotated

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, CurrentUserDep
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import (
    DocumentUploadRequest,
    DocumentResponse,
    DocumentListResponse,
    DocumentToggleResponse,
)
from app.services.document_service import (
    fetch_url_content,
    build_document_response,
    vectorize_document_by_id,
)

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)],
)

DbDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=DocumentListResponse)
def list_documents(db: DbDep) -> DocumentListResponse:
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    items = [DocumentResponse(**build_document_response(doc, db)) for doc in docs]
    return DocumentListResponse(documents=items, total=len(items))


@router.post("/upload", response_model=DocumentResponse)
async def upload_from_url(
    request: DocumentUploadRequest,
    background_tasks: BackgroundTasks,
    db: DbDep,
    current_user: CurrentUserDep,
) -> DocumentResponse:
    try:
        content = await fetch_url_content(request.url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"URLの取得に失敗しました: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"URLの取得に失敗しました: {str(e)}")

    if not content.strip():
        raise HTTPException(status_code=422, detail="URLからテキストを抽出できませんでした")

    doc = Document(
        title=request.title,
        content=content,
        source="upload",
        status="processing",
        is_active=True,
        url=request.url,
        created_by_user_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(vectorize_document_by_id, doc.id)

    return DocumentResponse(**build_document_response(doc, db))


@router.patch("/{document_id}/toggle", response_model=DocumentResponse)
def toggle_document(document_id: uuid.UUID, db: DbDep) -> DocumentResponse:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")

    doc.is_active = not doc.is_active
    db.commit()
    db.refresh(doc)
    return DocumentResponse(**build_document_response(doc, db))


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: uuid.UUID, db: DbDep) -> None:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="ドキュメントが見つかりません")

    db.delete(doc)
    db.commit()
