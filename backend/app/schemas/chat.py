import uuid
from datetime import datetime
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None


class ExtractionResult(BaseModel):
    category: str
    data: dict
    confidence: float


class ChatResponse(BaseModel):
    response: str
    session_id: uuid.UUID
    extractions: list[ExtractionResult]


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
