import uuid
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models import ChatSession, Message

_TITLE_MAX_LEN = 40


def get_or_create_session(
    db: Session,
    session_id: uuid.UUID | None,
    user_id: uuid.UUID,
) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session:
            return session
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def set_session_title_if_empty(db: Session, session: ChatSession, first_message: str) -> None:
    if session.title is None:
        session.title = first_message[:_TITLE_MAX_LEN]
        db.commit()


def save_message(db: Session, session_id: uuid.UUID, role: str, content: str) -> Message:
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_user_sessions(db: Session, user_id: uuid.UUID) -> list[tuple]:
    return (
        db.query(ChatSession, func.count(Message.id).label("message_count"))
        .outerjoin(Message, Message.session_id == ChatSession.id)
        .filter(ChatSession.user_id == user_id)
        .group_by(ChatSession.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def create_empty_session(db: Session, user_id: uuid.UUID) -> ChatSession:
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session_title(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    title: str,
) -> ChatSession | None:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return None
    session.title = title
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        return False
    db.delete(session)
    db.commit()
    return True


def touch_session(db: Session, session: ChatSession) -> None:
    session.updated_at = datetime.utcnow()
    db.commit()


def get_session_history(
    db: Session,
    session_id: uuid.UUID,
    limit: int,
    offset: int,
) -> tuple[ChatSession | None, list[Message], int]:
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session is None:
        return None, [], 0
    total = db.query(Message).filter(Message.session_id == session_id).count()
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return session, messages, total
