import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.database import get_db
from app.models import TravelExtraction
from app.schemas.chat import ChatRequest, ChatResponse, ExtractionResult, HistoryResponse, MessageResponse
from app.services.chat_service import get_or_create_session, save_message, get_session_history
from app.services.extraction_service import extract_travel_data

router = APIRouter(prefix="/chat", tags=["chat"])

DbDep = Annotated[Session, Depends(get_db)]

# --- 開発用（旅行以外の一般的な質問にも回答する）---
CHAT_SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
旅行に関する質問を中心に、日本語で親切・丁寧に答えてください。
旅行以外の一般的な質問にも対応できます。"""

# --- 本番用（旅行以外は断る場合はこちらに切り替え）---
# CHAT_SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
# 旅行に関する質問に、親切・丁寧・簡潔に日本語で答えてください。
# 旅行と関係のない質問には「旅行に関するご質問をお待ちしています」と返してください。"""


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: DbDep) -> ChatResponse:
    try:
        # セッション取得または新規作成
        session = get_or_create_session(db, request.session_id)

        # ユーザーメッセージをDBに保存
        user_message = save_message(db, session.id, "user", request.message)

        # LLMで返答生成（sync）
        llm = ChatOllama(model="qwen2.5:3b", base_url=settings.ollama_base_url)
        result = llm.invoke([
            SystemMessage(content=CHAT_SYSTEM_PROMPT),
            HumanMessage(content=request.message),
        ])
        assistant_content = result.content

        # アシスタント返答をDBに保存
        save_message(db, session.id, "assistant", assistant_content)

        # ユーザーメッセージから旅行データを抽出してDBに保存
        raw_extractions = extract_travel_data(request.message, settings.ollama_base_url)
        saved_extractions: list[ExtractionResult] = []
        for item in raw_extractions:
            db.add(TravelExtraction(
                message_id=user_message.id,
                session_id=session.id,
                category=item["category"],
                data=item["data"],
                confidence=item["confidence"],
            ))
            saved_extractions.append(ExtractionResult(**item))
        db.commit()

        return ChatResponse(
            response=assistant_content,
            session_id=session.id,
            extractions=saved_extractions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
def get_history(
    db: DbDep,
    session_id: uuid.UUID = Query(..., description="取得対象のセッションID"),
    limit: int = Query(50, ge=1, le=100, description="取得件数（1〜100）"),
    offset: int = Query(0, ge=0, description="スキップ件数"),
) -> HistoryResponse:
    try:
        session, messages, total = get_session_history(db, session_id, limit, offset)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return HistoryResponse(
            session_id=session.id,
            title=session.title,
            messages=[MessageResponse.model_validate(m) for m in messages],
            total=total,
            limit=limit,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
