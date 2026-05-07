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
    document_id: str | None
    document_title: str | None
    source: str | None
    chunk: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int
