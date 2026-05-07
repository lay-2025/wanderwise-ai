import uuid
from datetime import datetime
from pydantic import BaseModel, HttpUrl


class DocumentUploadRequest(BaseModel):
    title: str
    url: str


class DocumentResponse(BaseModel):
    id: uuid.UUID
    title: str
    source: str
    status: str
    is_active: bool
    chunks: int | None
    size: str | None
    url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class DocumentToggleResponse(BaseModel):
    id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}
