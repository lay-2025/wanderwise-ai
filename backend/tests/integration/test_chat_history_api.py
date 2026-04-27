"""
GET /api/chat/history の統合テスト。
DB をモックし、エンドポイントの入出力・ページング・エラーハンドリングを検証する。
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_mock_session, MOCK_USER_ID

HISTORY_SERVICE = "app.routers.chat"


# ---------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------

def make_mock_message_obj(
    role: str = "user",
    content: str = "テストメッセージ",
    created_at: datetime | None = None,
) -> MagicMock:
    msg = MagicMock()
    msg.id = uuid.uuid4()
    msg.role = role
    msg.content = content
    msg.created_at = created_at or datetime(2026, 4, 23, 10, 0, 0)
    return msg


# ---------------------------------------------------------------
# 共通フィクスチャ
# ---------------------------------------------------------------

@pytest.fixture
def session_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_history(session_id):
    """get_session_history をモックする基本フィクスチャ。"""
    session = make_mock_session(session_id)
    session.title = None

    user_msg = make_mock_message_obj("user", "京都旅行を考えています", datetime(2026, 4, 23, 10, 0, 0))
    asst_msg = make_mock_message_obj("assistant", "京都は素晴らしい街ですね。", datetime(2026, 4, 23, 10, 0, 5))
    messages = [user_msg, asst_msg]

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(session, messages, 2)) as mock:
        yield {"mock": mock, "session": session, "messages": messages}


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_存在するセッションIDで200が返る(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")
    data = res.json()

    assert "session_id" in data
    assert "title" in data
    assert "messages" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_メッセージ一覧が返る(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")
    data = res.json()

    assert len(data["messages"]) == 2


def test_メッセージにidとroleとcontentとcreated_atが含まれる(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")
    msg = res.json()["messages"][0]

    assert "id" in msg
    assert "role" in msg
    assert "content" in msg
    assert "created_at" in msg


def test_totalが正しく返る(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.json()["total"] == 2


def test_デフォルトのlimitとoffsetが返る(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}")
    data = res.json()

    assert data["limit"] == 50
    assert data["offset"] == 0


def test_指定したlimitとoffsetがレスポンスに含まれる(client: TestClient, session_id, mock_history):
    res = client.get(f"/api/chat/history?session_id={session_id}&limit=10&offset=5")
    data = res.json()

    assert data["limit"] == 10
    assert data["offset"] == 5


def test_get_session_historyにlimitとoffsetが渡される(client: TestClient, session_id, mock_history):
    client.get(f"/api/chat/history?session_id={session_id}&limit=20&offset=10")

    call_args = mock_history["mock"].call_args
    assert call_args.args[2] == 20   # limit
    assert call_args.args[3] == 10   # offset


def test_メッセージが0件のセッションで空リストが返る(client: TestClient, session_id):
    session = make_mock_session(session_id)
    session.title = None

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(session, [], 0)):
        res = client.get(f"/api/chat/history?session_id={session_id}")
        data = res.json()

    assert res.status_code == 200
    assert data["messages"] == []
    assert data["total"] == 0


def test_titleがある場合レスポンスに含まれる(client: TestClient, session_id):
    session = make_mock_session(session_id)
    session.title = "京都旅行の相談"

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(session, [], 0)):
        res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.json()["title"] == "京都旅行の相談"


def test_titleがnullの場合nullが返る(client: TestClient, session_id, mock_history):
    mock_history["session"].title = None

    res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.json()["title"] is None


# ---------------------------------------------------------------
# ページング
# ---------------------------------------------------------------

def test_limitのデフォルトは50(client: TestClient, session_id, mock_history):
    client.get(f"/api/chat/history?session_id={session_id}")

    call_args = mock_history["mock"].call_args
    assert call_args.args[2] == 50


def test_offsetのデフォルトは0(client: TestClient, session_id, mock_history):
    client.get(f"/api/chat/history?session_id={session_id}")

    call_args = mock_history["mock"].call_args
    assert call_args.args[3] == 0


# ---------------------------------------------------------------
# 異常系 — 404
# ---------------------------------------------------------------

def test_存在しないセッションIDで404が返る(client: TestClient):
    unknown_id = uuid.uuid4()

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(None, [], 0)):
        res = client.get(f"/api/chat/history?session_id={unknown_id}")

    assert res.status_code == 404
    assert res.json()["detail"] == "Session not found"


# ---------------------------------------------------------------
# 異常系 — 422 バリデーション
# ---------------------------------------------------------------

def test_session_id未指定で422が返る(client: TestClient):
    res = client.get("/api/chat/history")

    assert res.status_code == 422


def test_session_idがUUID形式でない場合422が返る(client: TestClient):
    res = client.get("/api/chat/history?session_id=not-a-uuid")

    assert res.status_code == 422


def test_limitが0の場合422が返る(client: TestClient, session_id):
    res = client.get(f"/api/chat/history?session_id={session_id}&limit=0")

    assert res.status_code == 422


def test_limitが101の場合422が返る(client: TestClient, session_id):
    res = client.get(f"/api/chat/history?session_id={session_id}&limit=101")

    assert res.status_code == 422


def test_offsetが負の場合422が返る(client: TestClient, session_id):
    res = client.get(f"/api/chat/history?session_id={session_id}&offset=-1")

    assert res.status_code == 422


# ---------------------------------------------------------------
# 異常系 — 500
# ---------------------------------------------------------------

def test_DBエラー発生時に500が返る(client: TestClient, session_id):
    with patch(f"{HISTORY_SERVICE}.get_session_history", side_effect=Exception("DB接続エラー")):
        res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.status_code == 500


# ---------------------------------------------------------------
# 異常系 — 403 所有者チェック
# ---------------------------------------------------------------

def test_他ユーザーのセッションへのアクセスで403が返る(client: TestClient, session_id):
    other_user_id = uuid.uuid4()  # MOCK_USER_ID とは異なる UUID
    session = make_mock_session(session_id, user_id=other_user_id)
    session.title = None

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(session, [], 0)):
        res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.status_code == 403
    assert res.json()["detail"] == "アクセス権限がありません"


def test_自分のセッションへのアクセスで200が返る(client: TestClient, session_id):
    session = make_mock_session(session_id, user_id=MOCK_USER_ID)
    session.title = None

    with patch(f"{HISTORY_SERVICE}.get_session_history", return_value=(session, [], 0)):
        res = client.get(f"/api/chat/history?session_id={session_id}")

    assert res.status_code == 200
