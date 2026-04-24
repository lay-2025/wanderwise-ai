from pydantic import BaseModel


class DocumentStats(BaseModel):
    total: int
    vectorized: int
    processing: int
    failed: int
    pending: int


class VisualizeResponse(BaseModel):
    total_chunks: int
    by_category: dict[str, int]
    by_source: dict[str, int]
    documents: DocumentStats


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
