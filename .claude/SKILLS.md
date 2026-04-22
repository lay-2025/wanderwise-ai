# WanderWise AI — インストール済みスキル一覧

このプロジェクトで利用可能なスキルの概要です。
スキル本体は `.agents/skills/` に格納されており、`.claude/skills/` からシンボリックリンクで参照されます。

---

## フロントエンド

### `next-best-practices`
- **発動**: 自動（`user-invocable: false`）— Next.js コードの作成・編集時に常時適用
- **概要**: Next.js App Router のベストプラクティス集
- **カバー範囲**:
  - ファイル構成・ルートセグメント規約
  - React Server Component (RSC) の境界設計
  - Next.js 15+ の async API パターン
  - メタデータ・エラーハンドリング・ルートハンドラー
  - 画像・フォント最適化、バンドル設定
- **出典**: [vercel/nextjs-skills](https://skills.sh/vercel/nextjs-skills/next-best-practices)

---

### `vercel-ai-sdk`
- **発動**: 自動（チャット・ストリーミング実装時）または `/vercel-ai-sdk` で明示指定
- **概要**: Vercel AI SDK v5 の実装パターンガイド
- **カバー範囲**:
  - `generateText` / `streamText` の使い方
  - `useChat` フックによるチャット UI 実装
  - ツール呼び出し（Tool Calling）
  - テキスト埋め込み（Embeddings）
  - MCP インテグレーション
- **出典**: [wsimmonds/claude-nextjs-skills](https://skills.sh/wsimmonds/claude-nextjs-skills/vercel-ai-sdk)

---

## バックエンド

### `fastapi`
- **発動**: 自動（FastAPI コード作業時）または `/fastapi` で明示指定
- **概要**: FastAPI 公式リポジトリ発のベストプラクティス集
- **カバー範囲**:
  - `Annotated` スタイルによるパラメータ・依存性宣言
  - ルーター分割と `include_router` の規約
  - 依存性注入（Dependency Injection）パターン
  - `async def` vs `def` の使い分け
  - ストリーミング（SSE・JSON Lines）
  - Pydantic モデルと返却型の設計
- **出典**: [fastapi/fastapi](https://skills.sh/fastapi/fastapi/fastapi)

---

### `architecture-patterns`
- **発動**: 自動（アーキテクチャ設計・リファクタリング時）または `/architecture-patterns` で明示指定
- **概要**: バックエンドの設計パターン集（Clean Architecture / DDD / Hexagonal）
- **カバー範囲**:
  - Clean Architecture（レイヤー依存の方向ルール）
  - Hexagonal Architecture（ポートとアダプター）
  - Domain-Driven Design（境界コンテキスト・集約・値オブジェクト）
  - 依存サイクルのデバッグ手法
  - テスト可能な構造設計
- **出典**: [wshobson/agents](https://skills.sh/wshobson/agents/architecture-patterns)

---

## テスト

### `pytest-coverage`
- **発動**: `/pytest-coverage` で明示指定
- **概要**: GitHub 公式リポジトリ発の pytest ベストプラクティス・カバレッジガイド
- **カバー範囲**:
  - ユニットテスト・統合テストの設計
  - フィクスチャ（`conftest.py`）の活用
  - `unittest.mock` / `pytest-mock` によるモック
  - FastAPI `TestClient` を使った API テスト
  - カバレッジ計測（`pytest-cov`）
- **インストール先**: プロジェクトローカル（`.agents/skills/pytest-coverage`）
- **出典**: [github/awesome-copilot](https://skills.sh/github/awesome-copilot/pytest-coverage)

---

## AI / RAG

### `rag-implementation`
- **発動**: `/rag-implementation` で明示指定
- **概要**: ChromaDB + LangChain を使った RAG パイプラインの実装パターンガイド
- **カバー範囲**:
  - ドキュメントのチャンク分割戦略
  - Embedding 生成と ChromaDB への保存
  - 類似度検索とコンテキスト付与
  - RAG を組み込んだチャットエンドポイントの設計
- **インストール先**: プロジェクトローカル（`.agents/skills/rag-implementation`）
- **出典**: [davila7/claude-code-templates](https://skills.sh/davila7/claude-code-templates/rag-implementation)

---

## ユーティリティ

### `find-skills`
- **発動**: `/find-skills` で明示指定
- **概要**: skills.sh エコシステムから新しいスキルを検索・インストールするためのガイド
- **使用場面**: 新しい機能領域のスキルを探したいとき

---

## 発動方法まとめ

| スキル | 自動発動 | 手動呼び出し | インストール先 |
|--------|----------|-------------|---------------|
| `next-best-practices` | 常時（Next.js コード全般） | ― | プロジェクト |
| `vercel-ai-sdk` | チャット・ストリーミング実装時 | `/vercel-ai-sdk` | プロジェクト |
| `fastapi` | FastAPI コード作業時 | `/fastapi` | プロジェクト |
| `architecture-patterns` | アーキテクチャ設計・リファクタリング時 | `/architecture-patterns` | プロジェクト |
| `pytest-coverage` | なし | `/pytest-coverage` | プロジェクト |
| `rag-implementation` | なし | `/rag-implementation` | プロジェクト |
| `find-skills` | なし | `/find-skills` | プロジェクト |

---

## スキルの追加・更新

```bash
# 新規インストール
npx skills add <owner/repo@skill-name> -y

# 更新確認
npx skills check

# 全スキル更新
npx skills update
```
