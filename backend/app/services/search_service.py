from langchain_ollama import OllamaEmbeddings
import chromadb

from app.schemas.learning import SearchResult, SearchResponse

COLLECTION_NAME = "travel_knowledge"


def search_similar_chunks(
    query: str,
    n_results: int,
    source: str | None,
    category: str | None,
    chroma_host: str,
    chroma_port: int,
    ollama_url: str,
) -> SearchResponse:
    client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

    # コレクションが未作成の場合は空を返す
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME not in existing:
        return SearchResponse(query=query, results=[], total=0)

    collection = client.get_collection(COLLECTION_NAME)
    if collection.count() == 0:
        return SearchResponse(query=query, results=[], total=0)

    # クエリをベクトル化
    embedder = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
    query_embedding = embedder.embed_query(query)

    # ChromaDB フィルタ構築
    where: dict | None = None
    if source and category:
        where = {"$and": [{"source": source}, {"category": category}]}
    elif source:
        where = {"source": source}
    elif category:
        where = {"category": category}

    # 類似度検索
    raw = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
        where=where,
    )

    results: list[SearchResult] = []
    ids = raw["ids"][0]
    documents = raw["documents"][0]
    metadatas = raw["metadatas"][0]
    distances = raw["distances"][0]

    for chroma_id, content, meta, distance in zip(ids, documents, metadatas, distances):
        results.append(SearchResult(
            chroma_id=chroma_id,
            content=content,
            similarity=round(1 - distance, 4),
            category=meta.get("category"),
            source=meta.get("source"),
            session_id=meta.get("session_id"),
            document_id=meta.get("document_id"),
        ))

    return SearchResponse(query=query, results=results, total=len(results))
