"""
GET /api/learning/visualize の統合テスト。
get_visualize_data をモックし、エンドポイントの入出力・エラーハンドリングを検証する。
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.schemas.learning import DocumentStats, VisualizeResponse

LEARNING_SERVICE = "app.routers.learning"


def make_visualize_response(
    total_chunks: int = 15,
    by_category: dict | None = None,
    by_source: dict | None = None,
    doc_total: int = 3,
    vectorized: int = 3,
) -> VisualizeResponse:
    return VisualizeResponse(
        total_chunks=total_chunks,
        by_category=by_category if by_category is not None else {"destination": 5, "food": 2},
        by_source=by_source if by_source is not None else {"chat": total_chunks},
        documents=DocumentStats(
            total=doc_total,
            vectorized=vectorized,
            processing=0,
            failed=0,
            pending=0,
        ),
    )


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_リクエストで200が返る(client: TestClient):
    response = make_visualize_response()
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient):
    response = make_visualize_response()
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")
    data = res.json()

    assert "total_chunks" in data
    assert "by_category" in data
    assert "by_source" in data
    assert "documents" in data


def test_documentsに必須フィールドが含まれる(client: TestClient):
    response = make_visualize_response()
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")
    docs = res.json()["documents"]

    assert "total" in docs
    assert "vectorized" in docs
    assert "processing" in docs
    assert "failed" in docs
    assert "pending" in docs


def test_ChromaDBデータありの場合total_chunksが返る(client: TestClient):
    response = make_visualize_response(total_chunks=15)
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")

    assert res.json()["total_chunks"] == 15


def test_by_categoryにカテゴリ別件数が含まれる(client: TestClient):
    response = make_visualize_response(by_category={"destination": 5, "food": 2, "tip": 1})
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")
    by_cat = res.json()["by_category"]

    assert by_cat["destination"] == 5
    assert by_cat["food"] == 2
    assert by_cat["tip"] == 1


def test_by_sourceにソース別件数が含まれる(client: TestClient):
    response = make_visualize_response(by_source={"chat": 10, "upload": 5})
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")
    by_src = res.json()["by_source"]

    assert by_src["chat"] == 10
    assert by_src["upload"] == 5


def test_ChromaDBデータなしの場合total_chunksが0になる(client: TestClient):
    response = VisualizeResponse(
        total_chunks=0,
        by_category={},
        by_source={},
        documents=DocumentStats(total=0, vectorized=0, processing=0, failed=0, pending=0),
    )
    with patch(f"{LEARNING_SERVICE}.get_visualize_data", return_value=response):
        res = client.get("/api/learning/visualize")
    data = res.json()

    assert data["total_chunks"] == 0
    assert data["by_category"] == {}
    assert data["by_source"] == {}


# ---------------------------------------------------------------
# 異常系 — 500
# ---------------------------------------------------------------

def test_get_visualize_dataが例外を投げた場合500が返る(client: TestClient):
    with patch(
        f"{LEARNING_SERVICE}.get_visualize_data",
        side_effect=Exception("ChromaDB接続エラー"),
    ):
        res = client.get("/api/learning/visualize")

    assert res.status_code == 500
