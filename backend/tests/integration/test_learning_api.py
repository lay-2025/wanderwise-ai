"""
POST /api/learning/vectorize の統合テスト。
vectorize_chat_data をモックし、エンドポイントの入出力・エラーハンドリングを検証する。
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

LEARNING_SERVICE = "app.routers.learning"


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_ベクトル化実行で200が返る(client: TestClient):
    result = {"processed": 2, "skipped": 0, "failed": 0, "total_chunks": 6}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient):
    result = {"processed": 2, "skipped": 1, "failed": 0, "total_chunks": 6}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")
    data = res.json()

    assert "processed" in data
    assert "skipped" in data
    assert "failed" in data
    assert "total_chunks" in data


def test_未変換データがある場合processedが返る(client: TestClient):
    result = {"processed": 3, "skipped": 0, "failed": 0, "total_chunks": 12}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")

    assert res.json()["processed"] == 3
    assert res.json()["total_chunks"] == 12


def test_全セッション変換済みの場合skippedが返る(client: TestClient):
    result = {"processed": 0, "skipped": 5, "failed": 0, "total_chunks": 0}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")

    assert res.json()["processed"] == 0
    assert res.json()["skipped"] == 5


def test_対象データなしの場合全て0が返る(client: TestClient):
    result = {"processed": 0, "skipped": 0, "failed": 0, "total_chunks": 0}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")
    data = res.json()

    assert data["processed"] == 0
    assert data["skipped"] == 0
    assert data["failed"] == 0
    assert data["total_chunks"] == 0


def test_失敗があった場合failedが返る(client: TestClient):
    result = {"processed": 1, "skipped": 0, "failed": 2, "total_chunks": 4}
    with patch(f"{LEARNING_SERVICE}.vectorize_chat_data", return_value=result):
        res = client.post("/api/learning/vectorize")

    assert res.json()["failed"] == 2


# ---------------------------------------------------------------
# 異常系 — 500
# ---------------------------------------------------------------

def test_vectorize_chat_dataが例外を投げた場合500が返る(client: TestClient):
    with patch(
        f"{LEARNING_SERVICE}.vectorize_chat_data",
        side_effect=Exception("ChromaDB接続エラー"),
    ):
        res = client.post("/api/learning/vectorize")

    assert res.status_code == 500
