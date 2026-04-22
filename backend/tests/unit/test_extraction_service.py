"""
extraction_service のユニットテスト。
LLMの呼び出しをモックし、JSONパース・バリデーションのロジックのみを検証する。
LaravelのUnit テストに相当。
"""
import json
from unittest.mock import MagicMock, patch

from app.services.extraction_service import extract_travel_data

OLLAMA_URL = "http://localhost:11434"


def _mock_llm(response_content: str) -> MagicMock:
    """指定した文字列を返すLLMモックを生成する。"""
    mock_result = MagicMock()
    mock_result.content = response_content

    mock_instance = MagicMock()
    mock_instance.invoke.return_value = mock_result

    return mock_instance


# ---------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------

def test_旅行情報がある場合は抽出して返す():
    response = json.dumps([
        {"category": "destination", "data": {"name": "京都", "type": "city"}, "confidence": 0.9}
    ])
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm(response)):
        result = extract_travel_data("京都に行きたいです", OLLAMA_URL)

    assert len(result) == 1
    assert result[0]["category"] == "destination"
    assert result[0]["data"]["name"] == "京都"
    assert result[0]["confidence"] == 0.9


def test_複数カテゴリを同時に抽出できる():
    response = json.dumps([
        {"category": "destination", "data": {"name": "嵐山"}, "confidence": 0.9},
        {"category": "transportation", "data": {"mode": "train", "details": "新幹線"}, "confidence": 0.85},
        {"category": "budget", "data": {"amount": 100000, "currency": "JPY"}, "confidence": 0.8},
    ])
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm(response)):
        result = extract_travel_data("新幹線で嵐山へ、予算10万円", OLLAMA_URL)

    assert len(result) == 3
    categories = [r["category"] for r in result]
    assert "destination" in categories
    assert "transportation" in categories
    assert "budget" in categories


def test_confidence未指定の場合はデフォルト1_0が設定される():
    response = json.dumps([
        {"category": "destination", "data": {"name": "京都"}}
        # confidence なし
    ])
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm(response)):
        result = extract_travel_data("京都旅行", OLLAMA_URL)

    assert result[0]["confidence"] == 1.0


# ---------------------------------------------------------------
# 空・無効データ系
# ---------------------------------------------------------------

def test_旅行情報がない場合は空リストを返す():
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm("[]")):
        result = extract_travel_data("今日の天気は晴れです", OLLAMA_URL)

    assert result == []


def test_LLMが無効なJSONを返した場合は空リストを返す():
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm("これはJSONではありません")):
        result = extract_travel_data("何か", OLLAMA_URL)

    assert result == []


def test_categoryまたはdataが欠けているアイテムは除外される():
    response = json.dumps([
        {"category": "destination", "data": {"name": "京都"}, "confidence": 0.9},  # 正常
        {"invalid_key": "value"},                                                    # category/data なし → 除外
        {"category": "budget"},                                                      # data なし → 除外
    ])
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm(response)):
        result = extract_travel_data("テスト", OLLAMA_URL)

    assert len(result) == 1
    assert result[0]["category"] == "destination"


def test_LLMが例外を投げた場合は空リストを返す():
    mock_instance = MagicMock()
    mock_instance.invoke.side_effect = Exception("Ollama接続エラー")

    with patch("app.services.extraction_service.ChatOllama", return_value=mock_instance):
        result = extract_travel_data("京都旅行", OLLAMA_URL)

    assert result == []


def test_JSONの前後に余分なテキストがあっても解析できる():
    """LLMが説明文をJSONの前後に付けた場合でも正しく解析できる。"""
    response = '以下が抽出結果です：\n[{"category": "destination", "data": {"name": "大阪"}, "confidence": 0.9}]\n以上です。'
    with patch("app.services.extraction_service.ChatOllama", return_value=_mock_llm(response)):
        result = extract_travel_data("大阪旅行", OLLAMA_URL)

    assert len(result) == 1
    assert result[0]["data"]["name"] == "大阪"
