import chromadb
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas.learning import DocumentStats, VisualizeResponse

COLLECTION_NAME = "travel_knowledge"


def get_visualize_data(
    db: Session,
    chroma_host: str,
    chroma_port: int,
) -> VisualizeResponse:
    doc_stats = _get_document_stats(db)

    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME not in existing:
        return VisualizeResponse(
            total_chunks=0,
            by_category={},
            by_source={},
            documents=doc_stats,
        )

    collection = client.get_collection(COLLECTION_NAME)
    total = collection.count()
    if total == 0:
        return VisualizeResponse(
            total_chunks=0,
            by_category={},
            by_source={},
            documents=doc_stats,
        )

    result = collection.get(include=["metadatas"])
    metadatas = result["metadatas"] or []

    by_category: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for meta in metadatas:
        cat = meta.get("category")
        if cat:
            by_category[cat] = by_category.get(cat, 0) + 1
        src = meta.get("source")
        if src:
            by_source[src] = by_source.get(src, 0) + 1

    return VisualizeResponse(
        total_chunks=total,
        by_category=by_category,
        by_source=by_source,
        documents=doc_stats,
    )


def _get_document_stats(db: Session) -> DocumentStats:
    statuses = ["vectorized", "processing", "failed", "pending"]
    counts: dict[str, int] = {s: 0 for s in statuses}

    rows = db.query(Document.status, Document.id).all()
    total = len(rows)
    for row in rows:
        status = row.status
        if status in counts:
            counts[status] += 1

    return DocumentStats(total=total, **counts)
