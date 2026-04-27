import json
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from langchain_ollama import OllamaEmbeddings
import chromadb

from app.models import ChatSession, TravelExtraction, Document, Chunk

COLLECTION_NAME = "travel_knowledge"


def extraction_to_text(category: str, data: dict) -> str:
    """travel_extraction の category / data を検索しやすい自然文に変換する。"""
    if category == "destination":
        name = data.get("name", "")
        type_ = data.get("type", "")
        country = data.get("country", "")
        return f"旅行先: {name}（{type_}）" + (f"、{country}" if country else "")
    if category == "accommodation":
        name = data.get("name", "")
        type_ = data.get("type", "")
        location = data.get("location", "")
        return f"宿泊施設: {name}（{type_}）" + (f"、{location}" if location else "")
    if category == "transportation":
        type_ = data.get("type", "")
        from_ = data.get("from", "")
        to = data.get("to", "")
        return f"交通手段: {type_}、{from_}から{to}"
    if category == "food":
        name = data.get("name", "")
        type_ = data.get("type", "")
        location = data.get("location", "")
        return f"グルメ: {name}（{type_}）" + (f"、{location}" if location else "")
    if category == "experience":
        name = data.get("name", "")
        type_ = data.get("type", "")
        location = data.get("location", "")
        return f"体験: {name}（{type_}）" + (f"、{location}" if location else "")
    if category == "schedule":
        start = data.get("start", "")
        duration = data.get("duration_days", "")
        return f"日程: {start}から{duration}日間"
    if category == "budget":
        amount = data.get("amount", "")
        currency = data.get("currency", "")
        type_ = data.get("type", "")
        return f"予算: {amount} {currency}（{type_}）"
    if category == "tip":
        content = data.get("content", "")
        target = data.get("target", "")
        return f"旅行のコツ: {content}" + (f"（{target}）" if target else "")
    return f"{category}: {json.dumps(data, ensure_ascii=False)}"


def vectorize_chat_data(
    db: Session,
    chroma_host: str,
    chroma_port: int,
    ollama_url: str,
) -> dict:
    """
    travel_extractions を持つセッションを document / chunk に変換し ChromaDB に保存する。
    既に vectorized なセッションはスキップ、failed は再処理する。
    """
    sessions = (
        db.query(ChatSession)
        .join(TravelExtraction, TravelExtraction.session_id == ChatSession.id)
        .distinct()
        .all()
    )

    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    embedder = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_url)

    processed = skipped = failed = total_chunks = 0

    for session in sessions:
        doc_title = f"chat-session-{session.id}"

        # 変換済みはスキップ
        if db.query(Document).filter(
            Document.title == doc_title,
            Document.status == "vectorized",
        ).first():
            skipped += 1
            continue

        # 失敗済みは削除して再処理
        failed_doc = db.query(Document).filter(
            Document.title == doc_title,
            Document.status == "failed",
        ).first()
        if failed_doc:
            db.delete(failed_doc)
            db.commit()

        extractions = (
            db.query(TravelExtraction)
            .filter(TravelExtraction.session_id == session.id)
            .order_by(TravelExtraction.created_at.asc())
            .all()
        )

        chunk_texts = [extraction_to_text(e.category, e.data) for e in extractions]
        full_content = "\n".join(chunk_texts)

        doc = Document(
            title=doc_title,
            content=full_content,
            source="chat",
            status="processing",
            created_by_user_id=session.user_id,
            source_session_id=session.id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            # セマンティックチャンキング: 1抽出 = 1チャンク
            chunk_objs: list[Chunk] = []
            for i, text in enumerate(chunk_texts):
                chunk = Chunk(document_id=doc.id, chunk_index=i, content=text)
                db.add(chunk)
                chunk_objs.append(chunk)
            db.commit()
            for c in chunk_objs:
                db.refresh(c)

            # バッチ embedding 生成
            embeddings = embedder.embed_documents(chunk_texts)

            # ChromaDB に保存
            chroma_ids = [str(uuid.uuid4()) for _ in chunk_objs]
            collection.add(
                ids=chroma_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=[
                    {
                        "document_id": str(doc.id),
                        "session_id": str(session.id),
                        "category": extractions[i].category,
                        "source": "chat",
                        "created_by_user_id": str(session.user_id),
                        "source_session_id": str(session.id),
                    }
                    for i in range(len(chunk_objs))
                ],
            )

            # chroma_id を chunks に書き戻す
            for chunk, chroma_id in zip(chunk_objs, chroma_ids):
                chunk.chroma_id = chroma_id

            doc.status = "vectorized"
            doc.updated_at = datetime.utcnow()
            db.commit()

            processed += 1
            total_chunks += len(chunk_objs)

        except Exception:
            doc.status = "failed"
            db.commit()
            failed += 1

    return {
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "total_chunks": total_chunks,
    }
