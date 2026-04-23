from pydantic import BaseModel


class VectorizeResponse(BaseModel):
    processed: int
    skipped: int
    failed: int
    total_chunks: int
