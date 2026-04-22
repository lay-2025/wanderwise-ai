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
