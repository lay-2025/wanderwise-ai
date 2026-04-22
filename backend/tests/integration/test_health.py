"""
main.py のエンドポイントテスト（GET / と GET /health）。
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_ルートエンドポイントが200を返す():
    res = client.get("/")

    assert res.status_code == 200
    assert res.json() == {"message": "Welcome to WanderWise AI API"}


def test_ヘルスチェックが200を返す():
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
