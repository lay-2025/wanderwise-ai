import uuid
from sqlalchemy.orm import Session
from app.models import TravelExtraction


def get_travel_data(
    db: Session,
    session_id: uuid.UUID | None,
    category: str | None,
    limit: int,
    offset: int,
) -> tuple[list[TravelExtraction], int]:
    query = db.query(TravelExtraction)
    if session_id is not None:
        query = query.filter(TravelExtraction.session_id == session_id)
    if category is not None:
        query = query.filter(TravelExtraction.category == category)
    total = query.count()
    items = query.order_by(TravelExtraction.created_at.desc()).offset(offset).limit(limit).all()
    return items, total
