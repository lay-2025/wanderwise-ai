import uuid
from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None
    compare_mode: bool = False


class ExtractionResult(BaseModel):
    category: str
    data: dict
    confidence: float


class RagSource(BaseModel):
    document_id: str | None
    document_title: str | None
    chunk: str
    score: float


class ChatResponse(BaseModel):
    response: str
    session_id: uuid.UUID
    extractions: list[ExtractionResult]
    rag_sources: list[RagSource] = []
    response_without_rag: str | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    session_id: uuid.UUID
    title: str | None
    messages: list[MessageResponse]
    total: int
    limit: int
    offset: int


class SessionItem(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: list[SessionItem]
    total: int


class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionUpdateRequest(BaseModel):
    title: str
