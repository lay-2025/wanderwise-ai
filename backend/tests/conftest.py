import uuid
from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.security import get_current_user

# テスト全体で共通のユーザーID（所有者チェックのテストで使用）
MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def make_mock_session(session_id: uuid.UUID | None = None, user_id: uuid.UUID | None = None) -> MagicMock:
    """ChatSession モックを生成する。"""
    session = MagicMock()
    session.id = session_id or uuid.uuid4()
    session.user_id = user_id or MOCK_USER_ID
    session.title = None
    return session


def make_mock_message(message_id: uuid.UUID | None = None) -> MagicMock:
    """Message モックを生成する。"""
    message = MagicMock()
    message.id = message_id or uuid.uuid4()
    return message


def make_mock_db() -> MagicMock:
    """DB セッションモックを生成する。"""
    db = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


def make_mock_user(user_id: uuid.UUID | None = None) -> MagicMock:
    """User モックを生成する。"""
    user = MagicMock()
    user.id = user_id or MOCK_USER_ID
    user.email = "test@example.com"
    user.name = "テストユーザー"
    return user


@pytest.fixture
def mock_db() -> MagicMock:
    return make_mock_db()


@pytest.fixture
def client(mock_db: MagicMock) -> TestClient:
    """
    DB依存・認証依存をモックに差し替えたテスト用クライアント。
    """
    mock_user = make_mock_user()
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
