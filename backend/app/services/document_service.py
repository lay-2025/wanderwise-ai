import uuid
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from langchain_ollama import OllamaEmbeddings
import chromadb

from app.models.document import Document
from app.models.chunk import Chunk
from app.core.config import settings

COLLECTION_NAME = "travel_knowledge"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _format_size(content: str) -> str:
    n = len(content.encode("utf-8"))
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _chunk_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


async def fetch_url_content(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; WanderWiseBot/1.0)"}
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]
    return "\n".join(lines)


def build_document_response(doc: Document, db: Session) -> dict:
    chunk_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
    return {
        "id": doc.id,
        "title": doc.title,
        "source": doc.source,
        "status": doc.status,
        "is_active": doc.is_active,
        "chunks": chunk_count if chunk_count > 0 else None,
        "size": _format_size(doc.content),
        "url": doc.url,
        "created_at": doc.created_at,
        "updated_at": doc.updated_at,
    }


def vectorize_document_by_id(document_id: uuid.UUID) -> None:
    """バックグラウンドタスクとして呼び出されるベクトル化処理。独自DBセッションを使用。"""
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        chunks_text = _chunk_text(doc.content)
        if not chunks_text:
            doc.status = "failed"
            db.commit()
            return

        chunk_objs: list[Chunk] = []
        for i, text in enumerate(chunks_text):
            chunk = Chunk(document_id=doc.id, chunk_index=i, content=text)
            db.add(chunk)
            chunk_objs.append(chunk)
        db.commit()
        for c in chunk_objs:
            db.refresh(c)

        embedder = OllamaEmbeddings(
            model="nomic-embed-text", base_url=settings.ollama_base_url
        )
        embeddings = embedder.embed_documents(chunks_text)

        chroma_client = chromadb.HttpClient(
            host=settings.chroma_server_host, port=settings.chroma_server_http_port
        )
        collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

        chroma_ids = [str(uuid.uuid4()) for _ in chunk_objs]
        collection.add(
            ids=chroma_ids,
            embeddings=embeddings,
            documents=chunks_text,
            metadatas=[
                {
                    "document_id": str(doc.id),
                    "document_title": doc.title,
                    "source": doc.source,
                }
                for _ in chunk_objs
            ],
        )

        for chunk, chroma_id in zip(chunk_objs, chroma_ids):
            chunk.chroma_id = chroma_id

        doc.status = "vectorized"
        doc.updated_at = datetime.utcnow()
        db.commit()

    except Exception:
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if doc:
                doc.status = "failed"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
