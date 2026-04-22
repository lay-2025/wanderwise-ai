import uuid
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
