"""
GET /api/learning/search の統合テスト。
search_similar_chunks をモックし、エンドポイントの入出力・エラーハンドリングを検証する。
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.schemas.learning import SearchResponse, SearchResult

LEARNING_SERVICE = "app.routers.learning"

SAMPLE_RESULT = SearchResult(
    document_id="7b66d212-76c2-4e24-b642-59efc69d9256",
    document_title="嵐山観光ガイド",
    source="chat",
    chunk="旅行先: 嵐山（place）",
    score=0.87,
)


def make_search_response(query: str, results: list[SearchResult] | None = None) -> SearchResponse:
    if results is None:
        results = [SAMPLE_RESULT]
    return SearchResponse(query=query, results=results, total=len(results))


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_クエリを指定して検索すると200が返る(client: TestClient):
    response = make_search_response("京都のおすすめ観光地")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response):
        res = client.get("/api/learning/search", params={"q": "京都のおすすめ観光地"})

    assert res.status_code == 200


def test_レスポンスに必須フィールドが含まれる(client: TestClient):
    response = make_search_response("京都のおすすめ観光地")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response):
        res = client.get("/api/learning/search", params={"q": "京都のおすすめ観光地"})
    data = res.json()

    assert "query" in data
    assert "results" in data
    assert "total" in data


def test_resultsの各要素に必須フィールドが含まれる(client: TestClient):
    response = make_search_response("京都のおすすめ観光地")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response):
        res = client.get("/api/learning/search", params={"q": "京都のおすすめ観光地"})
    item = res.json()["results"][0]

    assert "document_id" in item
    assert "document_title" in item
    assert "source" in item
    assert "chunk" in item
    assert "score" in item


def test_データなしの場合空のresultsが返る(client: TestClient):
    response = SearchResponse(query="京都", results=[], total=0)
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response):
        res = client.get("/api/learning/search", params={"q": "京都"})
    data = res.json()

    assert res.status_code == 200
    assert data["results"] == []
    assert data["total"] == 0


def test_queryフィールドにリクエストのクエリが反映される(client: TestClient):
    response = make_search_response("混雑を避けるコツ")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response):
        res = client.get("/api/learning/search", params={"q": "混雑を避けるコツ"})

    assert res.json()["query"] == "混雑を避けるコツ"


def test_n_resultsが返却件数に反映される(client: TestClient):
    results = [SAMPLE_RESULT, SAMPLE_RESULT, SAMPLE_RESULT]
    response = SearchResponse(query="旅行", results=results, total=3)
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response) as mock:
        res = client.get("/api/learning/search", params={"q": "旅行", "n_results": 3})

    assert res.status_code == 200
    _, kwargs = mock.call_args
    assert kwargs["n_results"] == 3


def test_sourceフィルタがサービスに渡される(client: TestClient):
    response = make_search_response("宿泊施設")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response) as mock:
        res = client.get("/api/learning/search", params={"q": "宿泊施設", "source": "chat"})

    assert res.status_code == 200
    _, kwargs = mock.call_args
    assert kwargs["source"] == "chat"


def test_categoryフィルタがサービスに渡される(client: TestClient):
    response = make_search_response("宿泊施設")
    with patch(f"{LEARNING_SERVICE}.search_similar_chunks", return_value=response) as mock:
        res = client.get(
            "/api/learning/search",
            params={"q": "宿泊施設", "category": "accommodation"},
        )

    assert res.status_code == 200
    _, kwargs = mock.call_args
    assert kwargs["category"] == "accommodation"


# ---------------------------------------------------------------
# 異常系 — 422
# ---------------------------------------------------------------

def test_qが未指定の場合422が返る(client: TestClient):
    res = client.get("/api/learning/search")

    assert res.status_code == 422


def test_n_resultsが0の場合422が返る(client: TestClient):
    res = client.get("/api/learning/search", params={"q": "旅行", "n_results": 0})

    assert res.status_code == 422


def test_n_resultsが21の場合422が返る(client: TestClient):
    res = client.get("/api/learning/search", params={"q": "旅行", "n_results": 21})

    assert res.status_code == 422


# ---------------------------------------------------------------
# 異常系 — 500
# ---------------------------------------------------------------

def test_search_similar_chunksが例外を投げた場合500が返る(client: TestClient):
    with patch(
        f"{LEARNING_SERVICE}.search_similar_chunks",
        side_effect=Exception("ChromaDB接続エラー"),
    ):
        res = client.get("/api/learning/search", params={"q": "旅行"})

    assert res.status_code == 500
