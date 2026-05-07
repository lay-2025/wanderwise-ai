"""
document_service のユニットテスト。
外部依存（httpx・ChromaDB・Ollama・DB）はすべてモックする。
"""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.document_service import (
    _chunk_text,
    _format_size,
    build_document_response,
    fetch_url_content,
    vectorize_document_by_id,
)


# ---------------------------------------------------------------
# _format_size
# ---------------------------------------------------------------

def test_format_size_bytes():
    assert _format_size("abc") == "3 B"


def test_format_size_kilobytes():
    text = "a" * 2048
    result = _format_size(text)
    assert result.endswith("KB")


def test_format_size_megabytes():
    text = "a" * (1024 * 1024 + 1)
    result = _format_size(text)
    assert result.endswith("MB")


def test_format_size_1023bytes():
    text = "a" * 1023
    assert _format_size(text) == "1023 B"


def test_format_size_exactly_1kb():
    text = "a" * 1024
    assert _format_size(text) == "1.0 KB"


# ---------------------------------------------------------------
# _chunk_text
# ---------------------------------------------------------------

def test_chunk_text_短いテキストは1チャンク():
    chunks = _chunk_text("hello")
    assert chunks == ["hello"]


def test_chunk_text_空文字は空リスト():
    chunks = _chunk_text("")
    assert chunks == []


def test_chunk_text_500文字ちょうどは2チャンク():
    # CHUNK_SIZE=500, CHUNK_OVERLAP=50: [0:500] + [450:500] の2チャンクになる
    text = "a" * 500
    chunks = _chunk_text(text)
    assert len(chunks) == 2


def test_chunk_text_501文字は2チャンクになる():
    text = "a" * 501
    chunks = _chunk_text(text)
    assert len(chunks) == 2


def test_chunk_text_オーバーラップで連続性が保たれる():
    # CHUNK_SIZE=500, CHUNK_OVERLAP=50 なのでスライドは450文字
    text = "a" * 1000
    chunks = _chunk_text(text)
    # 1st: [0:500], 2nd: [450:950], 3rd: [900:1000]
    assert len(chunks) == 3


def test_chunk_text_空白のみのチャンクはスキップされる():
    text = "   " + "a" * 500 + "   "
    chunks = _chunk_text(text)
    assert all(c.strip() for c in chunks)


# ---------------------------------------------------------------
# fetch_url_content
# ---------------------------------------------------------------

@pytest.mark.asyncio
async def test_fetch_url_content_正常系():
    html = "<html><body><p>旅行情報</p></body></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.document_service.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_url_content("https://example.com")

    assert "旅行情報" in result


@pytest.mark.asyncio
async def test_fetch_url_content_scriptタグが除去される():
    html = "<html><body><p>本文</p><script>alert(1)</script></body></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.document_service.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_url_content("https://example.com")

    assert "alert" not in result
    assert "本文" in result


@pytest.mark.asyncio
async def test_fetch_url_content_空行が除去される():
    html = "<html><body><p>  </p><p>内容</p></body></html>"
    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.document_service.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_url_content("https://example.com")

    lines = result.splitlines()
    assert all(line.strip() for line in lines)


# ---------------------------------------------------------------
# build_document_response
# ---------------------------------------------------------------

def test_build_document_response_チャンク数が含まれる():
    doc = MagicMock()
    doc.id = uuid.uuid4()
    doc.title = "テスト"
    doc.source = "upload"
    doc.status = "vectorized"
    doc.is_active = True
    doc.url = "https://example.com"
    doc.content = "テスト本文"
    doc.created_at = MagicMock()
    doc.updated_at = MagicMock()

    db = MagicMock()
    db.query.return_value.filter.return_value.count.return_value = 5

    result = build_document_response(doc, db)

    assert result["chunks"] == 5
    assert result["title"] == "テスト"
    assert result["source"] == "upload"


def test_build_document_response_チャンク0件はNone():
    doc = MagicMock()
    doc.content = "x"
    doc.id = uuid.uuid4()

    db = MagicMock()
    db.query.return_value.filter.return_value.count.return_value = 0

    result = build_document_response(doc, db)

    assert result["chunks"] is None


def test_build_document_response_sizeフィールドがある():
    doc = MagicMock()
    doc.content = "hello"
    doc.id = uuid.uuid4()

    db = MagicMock()
    db.query.return_value.filter.return_value.count.return_value = 0

    result = build_document_response(doc, db)

    assert "size" in result
    assert result["size"] == "5 B"


# ---------------------------------------------------------------
# vectorize_document_by_id
# ---------------------------------------------------------------

def test_vectorize_document_by_id_ドキュメントが存在しない場合は何もしない():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    with patch("app.core.database.SessionLocal", return_value=mock_db):
        vectorize_document_by_id(uuid.uuid4())

    mock_db.commit.assert_not_called()


def test_vectorize_document_by_id_成功時にstatusがvectorizedになる():
    doc_id = uuid.uuid4()
    doc = MagicMock()
    doc.id = doc_id
    doc.content = "旅行情報のテキスト" * 10
    doc.title = "テスト"
    doc.source = "upload"
    doc.status = "processing"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    mock_embedder = MagicMock()
    mock_embedder.embed_documents.return_value = [[0.1, 0.2, 0.3]]

    mock_collection = MagicMock()
    mock_chroma = MagicMock()
    mock_chroma.get_or_create_collection.return_value = mock_collection

    with (
        patch("app.core.database.SessionLocal", return_value=mock_db),
        patch("app.services.document_service.OllamaEmbeddings", return_value=mock_embedder),
        patch("app.services.document_service.chromadb.HttpClient", return_value=mock_chroma),
    ):
        vectorize_document_by_id(doc_id)

    assert doc.status == "vectorized"
    mock_db.commit.assert_called()


def test_vectorize_document_by_id_コンテンツ空の場合statusがfailedになる():
    doc_id = uuid.uuid4()
    doc = MagicMock()
    doc.id = doc_id
    doc.content = ""
    doc.status = "processing"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    with patch("app.core.database.SessionLocal", return_value=mock_db):
        vectorize_document_by_id(doc_id)

    assert doc.status == "failed"


def test_vectorize_document_by_id_例外時にstatusがfailedになる():
    doc_id = uuid.uuid4()
    doc = MagicMock()
    doc.id = doc_id
    doc.content = "有効なテキスト" * 20
    doc.title = "テスト"
    doc.source = "upload"
    doc.status = "processing"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    with (
        patch("app.core.database.SessionLocal", return_value=mock_db),
        patch("app.services.document_service.OllamaEmbeddings", side_effect=Exception("Ollama接続エラー")),
    ):
        vectorize_document_by_id(doc_id)

    assert doc.status == "failed"


def test_vectorize_document_by_id_ChromaDBにaddが呼ばれる():
    doc_id = uuid.uuid4()
    doc = MagicMock()
    doc.id = doc_id
    doc.content = "旅行情報" * 30
    doc.title = "テスト"
    doc.source = "upload"
    doc.status = "processing"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = doc

    mock_embedder = MagicMock()
    mock_embedder.embed_documents.return_value = [[0.1] * 10 for _ in range(3)]

    mock_collection = MagicMock()
    mock_chroma = MagicMock()
    mock_chroma.get_or_create_collection.return_value = mock_collection

    with (
        patch("app.core.database.SessionLocal", return_value=mock_db),
        patch("app.services.document_service.OllamaEmbeddings", return_value=mock_embedder),
        patch("app.services.document_service.chromadb.HttpClient", return_value=mock_chroma),
    ):
        vectorize_document_by_id(doc_id)

    mock_collection.add.assert_called_once()
