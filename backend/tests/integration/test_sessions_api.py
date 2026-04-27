"""
セッション管理 API の統合テスト。
GET/POST /api/chat/sessions, PATCH/DELETE /api/chat/sessions/{id} を検証する。
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_mock_session, MOCK_USER_ID

SESSIONS_SERVICE = "app.routers.chat"


# ---------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------

def make_session_row(session_id: uuid.UUID | None = None, title: str | None = None, count: int = 0):
    """(ChatSession, message_count) のタプルを返す。"""
    session = make_mock_session(session_id)
    session.title = title
    return (session, count)


# ---------------------------------------------------------------
# GET /api/chat/sessions
# ---------------------------------------------------------------

def test_セッション一覧取得で200が返る(client: TestClient):
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=[]):
        res = client.get("/api/chat/sessions")

    assert res.status_code == 200


def test_セッション一覧レスポンスに必須フィールドが含まれる(client: TestClient):
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=[]):
        res = client.get("/api/chat/sessions")
    data = res.json()

    assert "sessions" in data
    assert "total" in data


def test_セッションが存在する場合一覧に含まれる(client: TestClient):
    rows = [
        make_session_row(title="京都旅行", count=4),
        make_session_row(title="沖縄プラン", count=2),
    ]
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=rows):
        res = client.get("/api/chat/sessions")
    data = res.json()

    assert data["total"] == 2
    assert len(data["sessions"]) == 2


def test_セッション一覧の各要素に必須フィールドが含まれる(client: TestClient):
    rows = [make_session_row(title="テスト", count=1)]
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=rows):
        res = client.get("/api/chat/sessions")
    item = res.json()["sessions"][0]

    assert "id" in item
    assert "title" in item
    assert "created_at" in item
    assert "updated_at" in item
    assert "message_count" in item


def test_セッションが0件の場合空リストが返る(client: TestClient):
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=[]):
        res = client.get("/api/chat/sessions")
    data = res.json()

    assert data["sessions"] == []
    assert data["total"] == 0


def test_message_countが正しく返る(client: TestClient):
    rows = [make_session_row(title="京都", count=8)]
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=rows):
        res = client.get("/api/chat/sessions")

    assert res.json()["sessions"][0]["message_count"] == 8


def test_get_user_sessionsにuser_idが渡される(client: TestClient):
    with patch(f"{SESSIONS_SERVICE}.get_user_sessions", return_value=[]) as mock:
        client.get("/api/chat/sessions")

    mock.assert_called_once()
    assert mock.call_args.args[1] == MOCK_USER_ID


# ---------------------------------------------------------------
# POST /api/chat/sessions
# ---------------------------------------------------------------

def test_新規セッション作成で201が返る(client: TestClient):
    session = make_mock_session()
    with patch(f"{SESSIONS_SERVICE}.create_empty_session", return_value=session):
        res = client.post("/api/chat/sessions")

    assert res.status_code == 201


def test_作成レスポンスにidとtitleとcreated_atが含まれる(client: TestClient):
    session = make_mock_session()
    with patch(f"{SESSIONS_SERVICE}.create_empty_session", return_value=session):
        res = client.post("/api/chat/sessions")
    data = res.json()

    assert "id" in data
    assert "title" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_新規作成セッションのtitleはnull(client: TestClient):
    session = make_mock_session()
    session.title = None
    with patch(f"{SESSIONS_SERVICE}.create_empty_session", return_value=session):
        res = client.post("/api/chat/sessions")

    assert res.json()["title"] is None


def test_create_empty_sessionにuser_idが渡される(client: TestClient):
    session = make_mock_session()
    with patch(f"{SESSIONS_SERVICE}.create_empty_session", return_value=session) as mock:
        client.post("/api/chat/sessions")

    mock.assert_called_once()
    assert mock.call_args.args[1] == MOCK_USER_ID


# ---------------------------------------------------------------
# PATCH /api/chat/sessions/{session_id}
# ---------------------------------------------------------------

def test_セッション名変更で200が返る(client: TestClient):
    session_id = uuid.uuid4()
    session = make_mock_session(session_id)
    session.title = "新しいタイトル"
    with patch(f"{SESSIONS_SERVICE}.update_session_title", return_value=session):
        res = client.patch(f"/api/chat/sessions/{session_id}", json={"title": "新しいタイトル"})

    assert res.status_code == 200


def test_変更後のtitleがレスポンスに含まれる(client: TestClient):
    session_id = uuid.uuid4()
    session = make_mock_session(session_id)
    session.title = "変更後タイトル"
    with patch(f"{SESSIONS_SERVICE}.update_session_title", return_value=session):
        res = client.patch(f"/api/chat/sessions/{session_id}", json={"title": "変更後タイトル"})

    assert res.json()["title"] == "変更後タイトル"


def test_存在しないセッションIDで404が返る(client: TestClient):
    session_id = uuid.uuid4()
    with patch(f"{SESSIONS_SERVICE}.update_session_title", return_value=None):
        res = client.patch(f"/api/chat/sessions/{session_id}", json={"title": "test"})

    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"


def test_titleなしのリクエストで422が返る(client: TestClient):
    session_id = uuid.uuid4()
    res = client.patch(f"/api/chat/sessions/{session_id}", json={})

    assert res.status_code == 422


# ---------------------------------------------------------------
# DELETE /api/chat/sessions/{session_id}
# ---------------------------------------------------------------

def test_セッション削除で204が返る(client: TestClient):
    session_id = uuid.uuid4()
    with patch(f"{SESSIONS_SERVICE}.delete_session", return_value=True):
        res = client.delete(f"/api/chat/sessions/{session_id}")

    assert res.status_code == 204


def test_削除レスポンスのボディは空(client: TestClient):
    session_id = uuid.uuid4()
    with patch(f"{SESSIONS_SERVICE}.delete_session", return_value=True):
        res = client.delete(f"/api/chat/sessions/{session_id}")

    assert res.content == b""


def test_存在しないセッション削除で404が返る(client: TestClient):
    session_id = uuid.uuid4()
    with patch(f"{SESSIONS_SERVICE}.delete_session", return_value=False):
        res = client.delete(f"/api/chat/sessions/{session_id}")

    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"


def test_delete_sessionにuser_idとsession_idが渡される(client: TestClient):
    session_id = uuid.uuid4()
    with patch(f"{SESSIONS_SERVICE}.delete_session", return_value=True) as mock:
        client.delete(f"/api/chat/sessions/{session_id}")

    mock.assert_called_once()
    assert mock.call_args.args[2] == MOCK_USER_ID
