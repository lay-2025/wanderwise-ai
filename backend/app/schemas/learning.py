from pydantic import BaseModel


class VectorizeResponse(BaseModel):
    processed: int
    skipped: int
    failed: int
    total_chunks: int


class SearchResult(BaseModel):
    chroma_id: str
    content: str
    similarity: float
    category: str | None
    source: str | None
    session_id: str | None
    document_id: str | None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
