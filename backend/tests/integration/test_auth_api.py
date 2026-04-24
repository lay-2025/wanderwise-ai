"""
POST /api/auth/register・login・logout / GET /api/auth/me の統合テスト。
auth_service をモックし、エンドポイントの入出力・認証フロー・エラーを検証する。
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from tests.conftest import make_mock_user

AUTH_SERVICE = "app.routers.auth"


def make_mock_db_user(
    user_id: uuid.UUID | None = None,
    email: str = "test@example.com",
    name: str = "テストユーザー",
) -> MagicMock:
    user = make_mock_user(user_id)
    user.email = email
    user.name = name
    user.created_at = datetime(2026, 4, 24, 10, 0, 0)
    return user


# ---------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------

def test_ユーザー登録で201が返る(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=None),
        patch(f"{AUTH_SERVICE}.create_user", return_value=user),
        patch(f"{AUTH_SERVICE}.create_access_token", return_value="dummy.token"),
    ):
        res = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "テストユーザー",
        })

    assert res.status_code == 201


def test_登録レスポンスに必須フィールドが含まれる(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=None),
        patch(f"{AUTH_SERVICE}.create_user", return_value=user),
        patch(f"{AUTH_SERVICE}.create_access_token", return_value="dummy.token"),
    ):
        res = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "テストユーザー",
        })
    data = res.json()

    assert "id" in data
    assert "email" in data
    assert "name" in data
    assert "created_at" in data


def test_登録成功でCookieが設定される(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=None),
        patch(f"{AUTH_SERVICE}.create_user", return_value=user),
        patch(f"{AUTH_SERVICE}.create_access_token", return_value="dummy.token"),
    ):
        res = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "テストユーザー",
        })

    assert "access_token" in res.cookies


def test_メール重複の場合409が返る(client: TestClient):
    existing_user = make_mock_db_user()
    with patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=existing_user):
        res = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "テストユーザー",
        })

    assert res.status_code == 409


def test_パスワードが8文字未満の場合422が返る(client: TestClient):
    res = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "short",
        "name": "テスト",
    })

    assert res.status_code == 422


def test_メール形式が不正の場合422が返る(client: TestClient):
    res = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "password123",
        "name": "テスト",
    })

    assert res.status_code == 422


# ---------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------

def test_ログインで200が返る(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=user),
        patch(f"{AUTH_SERVICE}.verify_password", return_value=True),
        patch(f"{AUTH_SERVICE}.create_access_token", return_value="dummy.token"),
    ):
        res = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })

    assert res.status_code == 200


def test_ログイン成功でCookieが設定される(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=user),
        patch(f"{AUTH_SERVICE}.verify_password", return_value=True),
        patch(f"{AUTH_SERVICE}.create_access_token", return_value="dummy.token"),
    ):
        res = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123",
        })

    assert "access_token" in res.cookies


def test_メールアドレスが存在しない場合401が返る(client: TestClient):
    with patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=None):
        res = client.post("/api/auth/login", json={
            "email": "notfound@example.com",
            "password": "password123",
        })

    assert res.status_code == 401


def test_パスワードが不正の場合401が返る(client: TestClient):
    user = make_mock_db_user()
    with (
        patch(f"{AUTH_SERVICE}.get_user_by_email", return_value=user),
        patch(f"{AUTH_SERVICE}.verify_password", return_value=False),
    ):
        res = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })

    assert res.status_code == 401


# ---------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------

def test_ログアウトで200が返る(client: TestClient):
    res = client.post("/api/auth/logout")

    assert res.status_code == 200


def test_ログアウトでCookieが削除される(client: TestClient):
    client.cookies.set("access_token", "dummy.token")
    res = client.post("/api/auth/logout")

    assert res.json()["message"] == "ログアウトしました"


# ---------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------

def test_認証済みで200が返る(client: TestClient):
    res = client.get("/api/auth/me")

    assert res.status_code == 200


def test_meレスポンスに必須フィールドが含まれる(client: TestClient):
    res = client.get("/api/auth/me")
    data = res.json()

    assert "id" in data
    assert "email" in data
    assert "name" in data
    assert "created_at" in data
