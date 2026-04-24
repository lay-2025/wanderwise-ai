import chromadb
from langchain_ollama import OllamaEmbeddings

COLLECTION_NAME = "travel_knowledge"
_N_RESULTS = 5
_MIN_SIMILARITY = 0.6


def build_rag_context(
    query: str,
    chroma_host: str,
    chroma_port: int,
    ollama_url: str,
    n_results: int = _N_RESULTS,
    min_similarity: float = _MIN_SIMILARITY,
) -> str | None:
    """
    ChromaDB から関連チャンクを検索してコンテキスト文字列を構築する。
    コレクション未作成・データなし・類似度不足・接続エラーの場合はすべて None を返す。
    """
    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME not in existing:
            return None

        collection = client.get_collection(COLLECTION_NAME)
        if collection.count() == 0:
            return None

        embedder = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)
        query_embedding = embedder.embed_query(query)

        raw = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count()),
            include=["documents", "distances"],
        )

        documents = raw["documents"][0]
        distances = raw["distances"][0]

        relevant = [
            doc
            for doc, dist in zip(documents, distances)
            if (1 - dist) >= min_similarity
        ]

        if not relevant:
            return None

        return "\n".join(f"- {doc}" for doc in relevant)

    except Exception:
        return None
