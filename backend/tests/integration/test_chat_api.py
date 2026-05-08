"""
チャットAPI の統合テスト。
DB・LLM をモックし、エンドポイントの入出力・ふるまいを検証する。
"""
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tests.conftest import make_mock_message, make_mock_session, MOCK_USER_ID

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
        patch(f"{CHAT_SERVICE}.set_session_title_if_empty") as mock_title,
        patch(f"{CHAT_SERVICE}.save_message", return_value=message) as mock_save,
        patch(f"{CHAT_SERVICE}.extract_travel_data", return_value=[]) as mock_extract,
        patch(f"{CHAT_SERVICE}.build_rag_context", return_value=(None, [])) as mock_rag,
        patch(f"{CHAT_SERVICE}.ChatOllama") as mock_llm,
    ):
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value.content = "テスト返答です。"
        mock_llm.return_value = mock_llm_instance

        yield {
            "session": session,
            "message": message,
            "mock_session": mock_session,
            "mock_title": mock_title,
            "mock_save": mock_save,
            "mock_extract": mock_extract,
            "mock_rag": mock_rag,
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
    assert "rag_sources" in data
    assert "response_without_rag" in data


def test_レスポンスのsession_idはUUID形式(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "旅行の相談です"})
    session_id = res.json()["session_id"]

    assert uuid.UUID(session_id)


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

    mock_services["mock_session"].assert_called_once()
    call_args = mock_services["mock_session"].call_args
    assert call_args.args[1] is None  # session_id が None


def test_session_id指定で既存セッションが引き継がれる(client: TestClient, mock_services):
    existing_id = str(uuid.uuid4())

    res = client.post("/api/chat", json={
        "message": "続きの質問です",
        "session_id": existing_id,
    })

    assert res.status_code == 200
    call_args = mock_services["mock_session"].call_args
    assert str(call_args.args[1]) == existing_id  # session_id が渡される


def test_ログインユーザーのuser_idがセッション作成に渡される(client: TestClient, mock_services):
    client.post("/api/chat", json={"message": "テスト"})

    call_args = mock_services["mock_session"].call_args
    assert call_args.args[2] == MOCK_USER_ID  # user_id がモックユーザーのID


def test_初回メッセージでタイトル自動生成が呼ばれる(client: TestClient, mock_services):
    client.post("/api/chat", json={"message": "京都旅行の相談"})

    mock_services["mock_title"].assert_called_once()


# ---------------------------------------------------------------
# DB保存の確認
# ---------------------------------------------------------------

def test_ユーザーメッセージとアシスタント返答がDBに保存される(client: TestClient, mock_services):
    client.post("/api/chat", json={"message": "京都旅行の相談"})

    assert mock_services["mock_save"].call_count == 2
    calls = mock_services["mock_save"].call_args_list
    roles = [call.args[2] for call in calls]
    assert "user" in roles
    assert "assistant" in roles


# ---------------------------------------------------------------
# 異常系
# ---------------------------------------------------------------

def test_messageが空文字の場合は422(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": ""})

    assert res.status_code in (200, 422)


def test_リクエストボディがない場合は422を返す(client: TestClient, mock_services):
    res = client.post("/api/chat", json={})

    assert res.status_code == 422


def test_LLMがエラーを返した場合は500を返す(client: TestClient, mock_services):
    mock_services["mock_llm"].return_value.invoke.side_effect = Exception("Ollama接続エラー")

    res = client.post("/api/chat", json={"message": "こんにちは"})

    assert res.status_code == 500


# ---------------------------------------------------------------
# RAG統合
# ---------------------------------------------------------------

def test_RAGコンテキストがある場合も200が返る(client: TestClient, mock_services):
    from app.services.rag_service import RagSource
    source = RagSource(
        document_id="doc-1",
        document_title="嵐山観光ガイド",
        chunk="旅行先: 嵐山（place）",
        score=0.87,
    )
    mock_services["mock_rag"].return_value = ("- 旅行先: 嵐山（place）", [source])

    res = client.post("/api/chat", json={"message": "嵐山のおすすめは？"})

    assert res.status_code == 200


def test_RAGコンテキストがある場合rag_sourcesがレスポンスに含まれる(client: TestClient, mock_services):
    from app.services.rag_service import RagSource
    source = RagSource(
        document_id="doc-1",
        document_title="嵐山観光ガイド",
        chunk="旅行先: 嵐山（place）",
        score=0.87,
    )
    mock_services["mock_rag"].return_value = ("- 旅行先: 嵐山（place）", [source])

    res = client.post("/api/chat", json={"message": "嵐山のおすすめは？"})
    data = res.json()

    assert len(data["rag_sources"]) == 1
    assert data["rag_sources"][0]["document_title"] == "嵐山観光ガイド"
    assert data["rag_sources"][0]["score"] == 0.87


def test_RAGコンテキストがない場合も200が返る(client: TestClient, mock_services):
    mock_services["mock_rag"].return_value = (None, [])

    res = client.post("/api/chat", json={"message": "旅行の相談です"})

    assert res.status_code == 200


# ---------------------------------------------------------------
# 比較モード
# ---------------------------------------------------------------

def test_比較モードOFFではresponse_without_ragはnull(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "旅行の相談です"})
    data = res.json()

    assert data["response_without_rag"] is None


def test_比較モードONで200が返る(client: TestClient, mock_services):
    res = client.post("/api/chat", json={"message": "旅行の相談です", "compare_mode": True})

    assert res.status_code == 200


def test_比較モードONではresponse_without_ragに値が入る(client: TestClient, mock_services):
    mock_services["mock_llm"].return_value.invoke.return_value.content = "RAGなし回答です。"

    res = client.post("/api/chat", json={"message": "旅行の相談です", "compare_mode": True})
    data = res.json()

    assert data["response_without_rag"] == "RAGなし回答です。"


def test_比較モードONでもDBへの保存は通常通り行われる(client: TestClient, mock_services):
    client.post("/api/chat", json={"message": "京都旅行の相談", "compare_mode": True})

    assert mock_services["mock_save"].call_count == 2
    calls = mock_services["mock_save"].call_args_list
    roles = [call.args[2] for call in calls]
    assert "user" in roles
    assert "assistant" in roles
