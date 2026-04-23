import uuid
from datetime import datetime
from pydantic import BaseModel


class TravelExtractionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    message_id: uuid.UUID
    category: str
    data: dict
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class TravelDataResponse(BaseModel):
    items: list[TravelExtractionResponse]
    total: int
    limit: int
    offset: int
