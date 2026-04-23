"""
GET /api/data/travel の統合テスト。
DB をモックし、フィルタ・ページング・エラーハンドリングを検証する。
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

DATA_SERVICE = "app.routers.data"


# ---------------------------------------------------------------
# テスト用ヘルパー
# ---------------------------------------------------------------

def make_mock_extraction(
    category: str = "destination",
    session_id: uuid.UUID | None = None,
    created_at: datetime | None = None,
) -> MagicMock:
    item = MagicMock()
    item.id = uuid.uuid4()
    item.session_id = session_id or uuid.uuid4()
    item.message_id = uuid.uuid4()
    item.category = category
    item.data = {"name": "京都", "type": "city"}
    item.confidence = 0.9
    item.created_at = created_at or datetime(2026, 4, 23, 10, 0, 0)
    return item


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_フィルタなしで200が返る(client: TestClient):
    items = [make_mock_extraction()]
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=(items, 1)):
        res = client.get("/api/data/travel")

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)):
        res = client.get("/api/data/travel")
    data = res.json()

    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data


def test_itemsの各要素に必須フィールドが含まれる(client: TestClient):
    items = [make_mock_extraction()]
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=(items, 1)):
        res = client.get("/api/data/travel")
    item = res.json()["items"][0]

    assert "id" in item
    assert "session_id" in item
    assert "message_id" in item
    assert "category" in item
    assert "data" in item
    assert "confidence" in item
    assert "created_at" in item


def test_データが0件のとき空リストが返る(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)):
        res = client.get("/api/data/travel")
    data = res.json()

    assert data["items"] == []
    assert data["total"] == 0


def test_デフォルトのlimitとoffsetが返る(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)):
        res = client.get("/api/data/travel")
    data = res.json()

    assert data["limit"] == 50
    assert data["offset"] == 0


def test_指定したlimitとoffsetがレスポンスに含まれる(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)):
        res = client.get("/api/data/travel?limit=10&offset=5")
    data = res.json()

    assert data["limit"] == 10
    assert data["offset"] == 5


# ---------------------------------------------------------------
# フィルタ
# ---------------------------------------------------------------

def test_categoryフィルタがサービスに渡される(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)) as mock:
        client.get("/api/data/travel?category=destination")

    call_args = mock.call_args
    assert call_args.args[2] == "destination"  # category


def test_session_idフィルタがサービスに渡される(client: TestClient):
    sid = uuid.uuid4()
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)) as mock:
        client.get(f"/api/data/travel?session_id={sid}")

    call_args = mock.call_args
    assert call_args.args[1] == sid  # session_id


def test_categoryフィルタで該当カテゴリのみ返る(client: TestClient):
    items = [make_mock_extraction(category="destination")]
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=(items, 1)):
        res = client.get("/api/data/travel?category=destination")

    assert res.json()["items"][0]["category"] == "destination"


def test_フィルタなし時はNoneがサービスに渡される(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", return_value=([], 0)) as mock:
        client.get("/api/data/travel")

    call_args = mock.call_args
    assert call_args.args[1] is None   # session_id
    assert call_args.args[2] is None   # category


# ---------------------------------------------------------------
# 異常系 — 422
# ---------------------------------------------------------------

def test_session_idがUUID形式でない場合422が返る(client: TestClient):
    res = client.get("/api/data/travel?session_id=not-a-uuid")

    assert res.status_code == 422


def test_limitが0の場合422が返る(client: TestClient):
    res = client.get("/api/data/travel?limit=0")

    assert res.status_code == 422


def test_limitが101の場合422が返る(client: TestClient):
    res = client.get("/api/data/travel?limit=101")

    assert res.status_code == 422


def test_offsetが負の場合422が返る(client: TestClient):
    res = client.get("/api/data/travel?offset=-1")

    assert res.status_code == 422


# ---------------------------------------------------------------
# 異常系 — 500
# ---------------------------------------------------------------

def test_DBエラー発生時に500が返る(client: TestClient):
    with patch(f"{DATA_SERVICE}.get_travel_data", side_effect=Exception("DB接続エラー")):
        res = client.get("/api/data/travel")

    assert res.status_code == 500
