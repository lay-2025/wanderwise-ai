import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.data import TravelDataResponse, TravelExtractionResponse
from app.services.data_service import get_travel_data

router = APIRouter(prefix="/data", tags=["data"], dependencies=[Depends(get_current_user)])

DbDep = Annotated[Session, Depends(get_db)]
SessionIdFilter = Annotated[uuid.UUID | None, Query(description="セッションIDでフィルタ")]
CategoryFilter = Annotated[str | None, Query(description="カテゴリでフィルタ（例: destination）")]
LimitParam = Annotated[int, Query(ge=1, le=100, description="取得件数（1〜100）")]
OffsetParam = Annotated[int, Query(ge=0, description="スキップ件数")]


@router.get("/travel", response_model=TravelDataResponse)
def list_travel_data(
    db: DbDep,
    session_id: SessionIdFilter = None,
    category: CategoryFilter = None,
    limit: LimitParam = 50,
    offset: OffsetParam = 0,
) -> TravelDataResponse:
    try:
        items, total = get_travel_data(db, session_id, category, limit, offset)
        return TravelDataResponse(
            items=[TravelExtractionResponse.model_validate(item) for item in items],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
