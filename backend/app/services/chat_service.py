import uuid
from sqlalchemy.orm import Session
from app.models import ChatSession, Message


def get_or_create_session(db: Session, session_id: uuid.UUID | None) -> ChatSession:
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            return session
    session = ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def save_message(db: Session, session_id: uuid.UUID, role: str, content: str) -> Message:
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


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
