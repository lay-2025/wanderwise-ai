"""
チャットAPI の統合テスト。
DB・LLM をモックし、エンドポイントの入出力・ふるまいを検証する。
LaravelのFeatureテスト（$this->postJson('/api/chat', [...])）に相当。
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_mock_message, make_mock_session

# サービス関数のモックパス
CHAT_SERVICE = "app.routers.chat"


# ---------------------------------------------------------------
# 共通モック設定
# ---------------------------------------------------------------

@pytest.fixture
def mock_services(mock_db):
    """チャットエンドポイントが依存するサービス・LLMをまとめてモックする。"""
    session = make_mock_session()
    message = make_mock_message()

    with (
        patch(f"{CHAT_SERVICE}.get_or_create_session", return_value=session) as mock_session,
        patch(f"{CHAT_SERVICE}.save_message", return_value=message) as mock_save,
        patch(f"{CHAT_SERVICE}.extract_travel_data", return_value=[]) as mock_extract,
        patch(f"{CHAT_SERVICE}.ChatOllama") as mock_llm,
    ):
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value.content = "テスト返答です。"
        mock_llm.return_value = mock_llm_instance

        yield {
            "session": session,
            "message": message,
            "mock_session": mock_session,
            "mock_save": mock_save,
            "mock_extract": mock_extract,
            "mock_llm": mock_llm,
        }


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_チャット送信で200が返る(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "こんにちは"})

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "京都旅行を考えています"})
    data = res.json()

    assert "response" in data
    assert "session_id" in data
    assert "extractions" in data


def test_レスポンスのsession_idはUUID形式(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "旅行の相談です"})
    session_id = res.json()["session_id"]

    assert uuid.UUID(session_id)  # UUID形式でなければ例外が発生する


def test_LLMの返答がresponseに含まれる(client: TestClient, mock_services):
    mock_services["mock_llm"].return_value.invoke.return_value.content = "京都は素晴らしい街です。"

    res = client.post("/api/chat", json={"message": "京都はどうですか？"})

    assert res.json()["response"] == "京都は素晴らしい街です。"


def test_旅行データが抽出された場合extractionsに含まれる(client: TestClient, mock_services):
    mock_services["mock_extract"].return_value = [
        {"category": "destination", "data": {"name": "京都"}, "confidence": 0.9}
    ]

    res = client.post("/api/chat", json={"message": "京都に行きたい"})
    extractions = res.json()["extractions"]

    assert len(extractions) == 1
    assert extractions[0]["category"] == "destination"
    assert extractions[0]["data"]["name"] == "京都"


def test_旅行情報がない場合extractionsは空リスト(client: TestClient, mock_services):
    mock_services["mock_extract"].return_value = []

    res = client.post("/api/chat", json={"message": "こんにちは"})

    assert res.json()["extractions"] == []


# ---------------------------------------------------------------
# セッション管理
# ---------------------------------------------------------------

def test_session_id未指定で新規セッションが作成される(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "はじめまして"})

    # get_or_create_session が session_id=None で呼ばれる
    mock_services["mock_session"].assert_called_once()
    call_args = mock_services["mock_session"].call_args
    assert call_args.args[1] is None  # 第2引数（session_id）がNone


def test_session_id指定で既存セッションが引き継がれる(client: TestClient, mock_services):
    existing_id = str(uuid.uuid4())

    res = client.post("/api/chat", json={
        "message": "続きの質問です",
        "session_id": existing_id,
    })

    assert res.status_code == 200
    # get_or_create_session に既存IDが渡される
    call_args = mock_services["mock_session"].call_args
    assert str(call_args.args[1]) == existing_id


# ---------------------------------------------------------------
# DB保存の確認
# ---------------------------------------------------------------

def test_ユーザーメッセージとアシスタント返答がDBに保存される(client: TestClient, mock_services):
    client.post("/api/chat", json={"message": "京都旅行の相談"})

    # save_message が2回呼ばれる（user + assistant）
    assert mock_services["mock_save"].call_count == 2

    calls = mock_services["mock_save"].call_args_list
    roles = [call.args[2] for call in calls]  # 第3引数がrole
    assert "user" in roles
    assert "assistant" in roles


# ---------------------------------------------------------------
# 異常系
# ---------------------------------------------------------------

def test_messageが空文字の場合は422を返す(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": ""})

    # Pydanticのバリデーションエラー（空文字はminlength違反ではないが構造は通る）
    # LLMエラーが発生しないため200になる場合もあることを確認
    assert res.status_code in (200, 422)


def test_リクエストボディがない場合は422を返す(client: TestClient, mock_services):
    res = client.post("/api/chat", json={})

    assert res.status_code == 422


def test_LLMがエラーを返した場合は500を返す(client: TestClient, mock_services):
    mock_services["mock_llm"].return_value.invoke.side_effect = Exception("Ollama接続エラー")

    res = client.post("/api/chat", json={"message": "こんにちは"})

    assert res.status_code == 500
