from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import COOKIE_NAME, CurrentUserDep, create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import create_user, get_user_by_email, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

DbDep = Annotated[Session, Depends(get_db)]

_COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30日


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )


@router.post("/register", response_model=UserResponse, status_code=201)
def register(request: RegisterRequest, response: Response, db: DbDep) -> UserResponse:
    if get_user_by_email(db, request.email):
        raise HTTPException(status_code=409, detail="このメールアドレスは既に登録されています")
    user = create_user(db, email=request.email, password=request.password, name=request.name)
    _set_auth_cookie(response, create_access_token(str(user.id), user.email))
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login(request: LoginRequest, response: Response, db: DbDep) -> UserResponse:
    user = get_user_by_email(db, request.email)
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="メールアドレスまたはパスワードが正しくありません")
    _set_auth_cookie(response, create_access_token(str(user.id), user.email))
    return UserResponse.model_validate(user)


@router.post("/logout")
def logout(response: Response, _: CurrentUserDep) -> dict:
    response.delete_cookie(key=COOKIE_NAME)
    return {"message": "ログアウトしました"}


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)
