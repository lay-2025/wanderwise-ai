"""
documents API エンドポイントの統合テスト。
DB・外部サービスはモックし、エンドポイントの入出力・エラーハンドリングを検証する。
"""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

DOC_SERVICE = "app.routers.documents"

MOCK_DOC_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

NOW = datetime(2026, 1, 1, 0, 0, 0)


def make_mock_doc(
    doc_id: uuid.UUID | None = None,
    title: str = "テストドキュメント",
    source: str = "upload",
    status: str = "processing",
    is_active: bool = True,
    url: str | None = "https://example.com",
    content: str = "テスト本文",
) -> MagicMock:
    doc = MagicMock()
    doc.id = doc_id or MOCK_DOC_ID
    doc.title = title
    doc.source = source
    doc.status = status
    doc.is_active = is_active
    doc.url = url
    doc.content = content
    doc.created_at = NOW
    doc.updated_at = NOW
    return doc


def _base_response(doc: MagicMock, chunks: int | None = None) -> dict:
    """build_document_response の戻り値を再現する辞書。"""
    return {
        "id": doc.id,
        "title": doc.title,
        "source": doc.source,
        "status": doc.status,
        "is_active": doc.is_active,
        "chunks": chunks,
        "size": "9 B",
        "url": doc.url,
        "created_at": NOW,
        "updated_at": NOW,
    }


# ---------------------------------------------------------------
# GET /api/documents
# ---------------------------------------------------------------

def test_ドキュメント一覧が返る(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()
    mock_db.query.return_value.order_by.return_value.all.return_value = [doc]

    with patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(doc)):
        res = client.get("/api/documents")

    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert len(data["documents"]) == 1
    assert data["documents"][0]["title"] == "テストドキュメント"


def test_ドキュメントが0件の場合空リストが返る(client: TestClient, mock_db: MagicMock):
    mock_db.query.return_value.order_by.return_value.all.return_value = []

    res = client.get("/api/documents")

    assert res.status_code == 200
    assert res.json()["total"] == 0
    assert res.json()["documents"] == []


def test_一覧レスポンスに必須フィールドが含まれる(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()
    mock_db.query.return_value.order_by.return_value.all.return_value = [doc]

    with patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(doc)):
        res = client.get("/api/documents")

    item = res.json()["documents"][0]
    for field in ["id", "title", "source", "status", "is_active", "created_at", "updated_at"]:
        assert field in item


# ---------------------------------------------------------------
# POST /api/documents/upload
# ---------------------------------------------------------------

def test_URLアップロード成功で201相当のレスポンスが返る(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()
    mock_db.refresh.side_effect = lambda obj: None

    with (
        patch(f"{DOC_SERVICE}.fetch_url_content", new=AsyncMock(return_value="本文テキスト")),
        patch(f"{DOC_SERVICE}.vectorize_document_by_id"),
        patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(doc)),
    ):
        res = client.post(
            "/api/documents/upload",
            json={"title": "テストドキュメント", "url": "https://example.com"},
        )

    assert res.status_code == 200
    assert res.json()["title"] == "テストドキュメント"


def test_URLアップロードでDBにドキュメントが追加される(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()

    with (
        patch(f"{DOC_SERVICE}.fetch_url_content", new=AsyncMock(return_value="本文テキスト")),
        patch(f"{DOC_SERVICE}.vectorize_document_by_id"),
        patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(doc)),
    ):
        client.post(
            "/api/documents/upload",
            json={"title": "テストドキュメント", "url": "https://example.com"},
        )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called()


def test_URL取得失敗時に422が返る(client: TestClient, mock_db: MagicMock):
    import httpx

    with patch(
        f"{DOC_SERVICE}.fetch_url_content",
        new=AsyncMock(side_effect=httpx.HTTPStatusError("404", request=MagicMock(), response=MagicMock(status_code=404))),
    ):
        res = client.post(
            "/api/documents/upload",
            json={"title": "失敗ドキュメント", "url": "https://example.com/notfound"},
        )

    assert res.status_code == 422
    assert "URLの取得に失敗しました" in res.json()["detail"]


def test_URL取得でネットワークエラーの場合422が返る(client: TestClient, mock_db: MagicMock):
    with patch(
        f"{DOC_SERVICE}.fetch_url_content",
        new=AsyncMock(side_effect=Exception("接続タイムアウト")),
    ):
        res = client.post(
            "/api/documents/upload",
            json={"title": "タイムアウトドキュメント", "url": "https://example.com/timeout"},
        )

    assert res.status_code == 422
    assert "URLの取得に失敗しました" in res.json()["detail"]


def test_コンテンツが空の場合422が返る(client: TestClient, mock_db: MagicMock):
    with patch(f"{DOC_SERVICE}.fetch_url_content", new=AsyncMock(return_value="   ")):
        res = client.post(
            "/api/documents/upload",
            json={"title": "空ドキュメント", "url": "https://example.com/empty"},
        )

    assert res.status_code == 422
    assert "テキストを抽出できませんでした" in res.json()["detail"]


def test_アップロード時にtitleフィールドが必須(client: TestClient):
    res = client.post(
        "/api/documents/upload",
        json={"url": "https://example.com"},
    )
    assert res.status_code == 422


def test_アップロード時にurlフィールドが必須(client: TestClient):
    res = client.post(
        "/api/documents/upload",
        json={"title": "タイトルのみ"},
    )
    assert res.status_code == 422


# ---------------------------------------------------------------
# PATCH /api/documents/{id}/toggle
# ---------------------------------------------------------------

def test_トグルでis_activeが反転する(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc(is_active=True)
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    toggled = make_mock_doc(is_active=False)
    with patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(toggled)):
        res = client.patch(f"/api/documents/{MOCK_DOC_ID}/toggle")

    assert res.status_code == 200
    assert res.json()["is_active"] is False


def test_トグル対象が存在しない場合404が返る(client: TestClient, mock_db: MagicMock):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    res = client.patch(f"/api/documents/{uuid.uuid4()}/toggle")

    assert res.status_code == 404
    assert "ドキュメントが見つかりません" in res.json()["detail"]


def test_トグルでDBがコミットされる(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc(is_active=True)
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    with patch(f"{DOC_SERVICE}.build_document_response", return_value=_base_response(doc)):
        client.patch(f"/api/documents/{MOCK_DOC_ID}/toggle")

    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------
# DELETE /api/documents/{id}
# ---------------------------------------------------------------

def test_削除で204が返る(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    res = client.delete(f"/api/documents/{MOCK_DOC_ID}")

    assert res.status_code == 204


def test_削除でDBのdeleteが呼ばれる(client: TestClient, mock_db: MagicMock):
    doc = make_mock_doc()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    client.delete(f"/api/documents/{MOCK_DOC_ID}")

    mock_db.delete.assert_called_once_with(doc)
    mock_db.commit.assert_called_once()


def test_削除対象が存在しない場合404が返る(client: TestClient, mock_db: MagicMock):
    mock_db.query.return_value.filter.return_value.first.return_value = None

    res = client.delete(f"/api/documents/{uuid.uuid4()}")

    assert res.status_code == 404
    assert "ドキュメントが見つかりません" in res.json()["detail"]
