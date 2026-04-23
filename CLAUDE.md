# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## コマンド

### 起動・停止

```bash
docker compose up -d           # 全コンテナ起動（backend / postgres / chromadb / ollama）
docker compose down
docker compose up -d --build   # requirements.txt 変更後
```

### フロントエンド（別ターミナル）

```bash
cd frontend && npm run dev
```

### ログ

```bash
docker compose logs -f backend
```

### テスト

```bash
docker compose exec backend python -m pytest
docker compose exec backend python -m pytest tests/integration/test_chat_api.py  # 特定ファイル
docker compose exec backend python -m pytest --cov=app --cov-report=term-missing
```

### マイグレーション

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend alembic revision --autogenerate -m "説明"
```

### アクセス先

| サービス | URL |
|---|---|
| フロントエンド | http://localhost:3000 |
| バックエンド API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ChromaDB | http://localhost:8001 |
| Ollama | http://localhost:11434 |

---

## アーキテクチャ

### データフロー

```
チャット送信
  → messages に保存（PostgreSQL）
  → Ollama (qwen2.5:3b) で返答生成 → messages に保存
  → 旅行データを抽出 → travel_extractions に保存
  → documents / chunks に変換
  → nomic-embed-text でベクトル化 → ChromaDB に保存
  → 次回チャット時に ChromaDB から RAG コンテキストを付与
```

**PostgreSQL がすべての真実の源。** ChromaDB はベクトル検索専用で、`chunks.chroma_id` で紐づける。

### DB テーブル関係

```
sessions ──< messages ──< travel_extractions
                │
                └──> documents ──< chunks ── (chroma_id) ──> ChromaDB
```

### バックエンド構成（`backend/app/`）

| レイヤー | 場所 | 責務 |
|---|---|---|
| ルーター | `routers/` | HTTP リクエスト受信・レスポンス返却 |
| サービス | `services/` | ビジネスロジック・DB 操作・LLM 呼び出し |
| モデル | `models/` | SQLAlchemy ORM（5テーブル） |
| スキーマ | `schemas/` | Pydantic リクエスト・レスポンス定義 |

### テスト方針

- DB・Ollama は **すべてモック**。`tests/conftest.py` の `mock_db` / `client` フィクスチャを使う
- `make_mock_session()` / `make_mock_message()` でテスト用オブジェクトを生成
- ユニットテスト: `tests/unit/`（サービス関数単体）
- 統合テスト: `tests/integration/`（エンドポイント入出力）

---

## コミット規約

```
<type>: <概要（日本語）>

- <変更点1>
- <変更点2>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### type 一覧

| type | 用途 |
|---|---|
| `feat` | 新機能・新エンドポイントの追加 |
| `fix` | バグ修正 |
| `test` | テストの追加・修正 |
| `docs` | ドキュメント・設計書の追加・修正 |
| `chore` | 設定ファイル・依存関係・ビルド環境の変更 |
| `refactor` | 動作を変えないコード整理・構造改善 |

コミット実行前に分割案を提示し、ユーザーの確認を得てから実行する。

---

## スキル

| 作業 | スキル | 発動 |
|---|---|---|
| FastAPI ルーター・スキーマ・DI の実装 | `fastapi` | 自動 |
| RAG パイプライン・ChromaDB・チャンク分割 | `rag-implementation` | `/rag-implementation` |
| テスト追加・カバレッジ改善 | `pytest-coverage` | `/pytest-coverage` |
| Next.js フロントエンド実装 | `next-best-practices` | 自動 |
| AI チャット UI・ストリーミング | `vercel-ai-sdk` | 自動 |
| アーキテクチャ設計・リファクタリング | `architecture-patterns` | 自動 |
