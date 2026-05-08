import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, CurrentUserDep
from app.models import TravelExtraction
from app.schemas.chat import (
    ChatRequest, ChatResponse, ExtractionResult, RagSource,
    HistoryResponse, MessageResponse,
    SessionItem, SessionListResponse, SessionResponse, SessionUpdateRequest,
)
from app.services.chat_service import (
    get_or_create_session,
    save_message,
    get_session_history,
    set_session_title_if_empty,
    get_user_sessions,
    create_empty_session,
    update_session_title,
    delete_session,
    touch_session,
)
from app.models.document import Document
from app.services.extraction_service import extract_travel_data
from app.services.rag_service import build_rag_context

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])

DbDep = Annotated[Session, Depends(get_db)]

# --- 開発用（旅行以外の一般的な質問にも回答する）---
BASE_SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
旅行に関する質問を中心に、日本語で親切・丁寧に答えてください。
旅行以外の一般的な質問にも対応できます。"""

# --- 本番用（旅行以外は断る場合はこちらに切り替え）---
# BASE_SYSTEM_PROMPT = """あなたは旅行アシスタントAIです。
# 旅行に関する質問に、親切・丁寧・簡潔に日本語で答えてください。
# 旅行と関係のない質問には「旅行に関するご質問をお待ちしています」と返してください。"""

_RAG_CONTEXT_SECTION = """

【参考情報（過去の旅行データ）】
{context}

上記の参考情報があれば活用して、より具体的に回答してください。"""


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: DbDep, current_user: CurrentUserDep) -> ChatResponse:
    try:
        # ログインユーザーのセッションを取得または新規作成
        session = get_or_create_session(db, request.session_id, current_user.id)

        # ユーザーメッセージをDBに保存
        user_message = save_message(db, session.id, "user", request.message)

        # 初回メッセージからセッションタイトルを自動生成
        set_session_title_if_empty(db, session, request.message)

        # is_active=True かつ vectorized のドキュメントIDを取得
        active_ids = [
            str(row.id)
            for row in db.query(Document.id).filter(
                Document.is_active == True,
                Document.status == "vectorized",
            ).all()
        ]

        # RAGコンテキストを取得（アクティブドキュメントなし・接続不可の場合は None）
        rag_context, rag_sources = build_rag_context(
            query=request.message,
            chroma_host=settings.chroma_server_host,
            chroma_port=settings.chroma_server_http_port,
            ollama_url=settings.ollama_base_url,
            active_document_ids=active_ids,
        )
        system_prompt = BASE_SYSTEM_PROMPT
        if rag_context:
            system_prompt += _RAG_CONTEXT_SECTION.format(context=rag_context)

        # LLMで返答生成（sync）
        llm = ChatOllama(model="qwen2.5:3b", base_url=settings.ollama_base_url)
        result = llm.invoke([
            SystemMessage(content=system_prompt),
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

        # セッションの最終更新日時を更新（サイドバーの並び順に反映）
        touch_session(db, session)

        # 比較モード: RAGなしで追加呼び出し（DB保存なし）
        response_without_rag = None
        if request.compare_mode:
            llm_no_rag = ChatOllama(model="qwen2.5:3b", base_url=settings.ollama_base_url)
            result_no_rag = llm_no_rag.invoke([
                SystemMessage(content=BASE_SYSTEM_PROMPT),
                HumanMessage(content=request.message),
            ])
            response_without_rag = result_no_rag.content

        return ChatResponse(
            response=assistant_content,
            session_id=session.id,
            extractions=saved_extractions,
            rag_sources=[RagSource(**vars(s)) for s in rag_sources],
            response_without_rag=response_without_rag,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryResponse)
def get_history(
    db: DbDep,
    current_user: CurrentUserDep,
    session_id: uuid.UUID = Query(..., description="取得対象のセッションID"),
    limit: int = Query(50, ge=1, le=100, description="取得件数（1〜100）"),
    offset: int = Query(0, ge=0, description="スキップ件数"),
) -> HistoryResponse:
    try:
        session, messages, total = get_session_history(db, session_id, limit, offset)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")
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


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(db: DbDep, current_user: CurrentUserDep) -> SessionListResponse:
    results = get_user_sessions(db, current_user.id)
    sessions = [
        SessionItem(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=count,
        )
        for s, count in results
    ]
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.post("/sessions", response_model=SessionResponse, status_code=201)
def new_session(db: DbDep, current_user: CurrentUserDep) -> SessionResponse:
    session = create_empty_session(db, current_user.id)
    return SessionResponse.model_validate(session)


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
def rename_session(
    session_id: uuid.UUID,
    body: SessionUpdateRequest,
    db: DbDep,
    current_user: CurrentUserDep,
) -> SessionResponse:
    session = update_session_title(db, session_id, current_user.id, body.title)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.model_validate(session)


@router.delete("/sessions/{session_id}", status_code=204)
def remove_session(
    session_id: uuid.UUID,
    db: DbDep,
    current_user: CurrentUserDep,
) -> None:
    if not delete_session(db, session_id, current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")
