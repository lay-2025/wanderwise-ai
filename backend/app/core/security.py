from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import User

COOKIE_NAME = "access_token"


def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.jwt_expire_days)
    payload = {"sub": user_id, "email": email, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> User:
    if access_token is None:
        raise HTTPException(status_code=401, detail="ログインが必要です")

    try:
        payload = jwt.decode(
            access_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="認証情報が無効です")
    except JWTError:
        raise HTTPException(status_code=401, detail="認証情報が無効です")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="ユーザーが存在しません")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
