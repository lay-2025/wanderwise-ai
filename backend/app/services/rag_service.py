from dataclasses import dataclass

import chromadb
from langchain_ollama import OllamaEmbeddings

COLLECTION_NAME = "travel_knowledge"
_N_RESULTS = 5
_MIN_SIMILARITY = 0.6


@dataclass
class RagSource:
    document_id: str | None
    document_title: str | None
    chunk: str
    score: float


def build_rag_context(
    query: str,
    chroma_host: str,
    chroma_port: int,
    ollama_url: str,
    active_document_ids: list[str],
    n_results: int = _N_RESULTS,
    min_similarity: float = _MIN_SIMILARITY,
) -> tuple[str | None, list[RagSource]]:
    """
    ChromaDB から関連チャンクを検索してコンテキスト文字列と参照ソース一覧を返す。
    active_document_ids が空、コレクション未作成、類似度不足、接続エラーの場合は (None, []) を返す。
    """
    if not active_document_ids:
        return None, []

    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME not in existing:
            return None, []

        collection = client.get_collection(COLLECTION_NAME)
        if collection.count() == 0:
            return None, []

        embedder = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
        query_embedding = embedder.embed_query(query)

        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            include=["documents", "metadatas", "distances"],
            where={"document_id": {"$in": active_document_ids}},
        )

        documents = raw["documents"][0]
        metadatas = raw["metadatas"][0]
        distances = raw["distances"][0]

        sources: list[RagSource] = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            score = round(1 - dist, 4)
            if score >= min_similarity:
                sources.append(RagSource(
                    document_id=meta.get("document_id"),
                    document_title=meta.get("document_title"),
                    chunk=doc,
                    score=score,
                ))

        if not sources:
            return None, []

        context = "\n".join(f"- {s.chunk}" for s in sources)
        return context, sources

    except Exception:
        return None, []
