# WanderWise AI — インストール済みスキル一覧

このプロジェクトで利用可能なスキルの概要です。
スキル本体は `.agents/skills/` に格納されており、`.claude/skills/` からシンボリックリンクで参照されます。

---

## フロントエンド

### `next-best-practices` ⭐ 基本スキル
- **発動**: 自動（`user-invocable: false`）— Next.js コードの作成・編集時に常時適用
- **用途**: **実装全般の基準スキル**。他のフロントスキルより優先する
- **概要**: Next.js App Router のベストプラクティス集
- **カバー範囲**:
  - ファイル構成・ルートセグメント規約
  - React Server Component (RSC) の境界設計
  - Next.js 15+ の async API パターン
  - メタデータ・エラーハンドリング・ルートハンドラー
  - 画像・フォント最適化、バンドル設定
- **出典**: [vercel/nextjs-skills](https://skills.sh/vercel/nextjs-skills/next-best-practices)

---

### `web-design-guidelines` — リファクタリング・レビュー用
- **発動**: `/web-design-guidelines` で明示指定
- **用途**: **UI品質審査・リファクタリング時のみ使用**。通常の実装には使わない
- **概要**: Vercel の Web UI ガイドラインに基づくデザイン・アクセシビリティ審査
- **カバー範囲**:
  - デザイン品質・一貫性のチェック
  - アクセシビリティ（a11y）ガイドライン
  - UX ベストプラクティス
- **出典**: [vercel-labs/agent-skills](https://skills.sh/vercel-labs/agent-skills/web-design-guidelines)

---

### `vercel-composition-patterns` — リファクタリング用
- **発動**: `/vercel-composition-patterns` で明示指定
- **用途**: **コンポーネント設計のリファクタリング時のみ使用**。通常の実装には使わない
- **概要**: React コンポーネントの合成パターン集（React 19 API 対応）
- **カバー範囲**:
  - コンポーネントアーキテクチャ・状態管理パターン
  - Boolean prop 増殖の回避
  - 10+ の名前付き合成パターン
- **出典**: [vercel-labs/agent-skills](https://skills.sh/vercel-labs/agent-skills/vercel-composition-patterns)

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
- **概要**: ChromaDB・Pinecone・Qdrant など主要ベクターDB に対応した RAG パイプライン実装ガイド（7,800 installs）
- **カバー範囲**:
  - ドキュメントのチャンク分割戦略（再帰的分割・トークンベース・セマンティック）
  - Embedding 生成と ChromaDB への保存
  - 高度な検索パターン（ハイブリッド検索・マルチクエリ・HyDE・MMR）
  - クロスエンコーダーによるリランキング
  - RAG を組み込んだチャットエンドポイントの設計
- **インストール先**: プロジェクトローカル（`.agents/skills/rag-implementation`）
- **出典**: [wshobson/agents](https://skills.sh/wshobson/agents/rag-implementation)

---

### `embedding-strategies`
- **発動**: `/embedding-strategies` で明示指定
- **概要**: ベクトル検索アプリケーション向けの埋め込みモデル選択と最適化ガイド（6,300 installs）
- **カバー範囲**:
  - 埋め込みモデルの選定と比較（Voyage AI・OpenAI・BGE・ローカルモデル）
  - チャンキング戦略（トークンベース・文ベース・セマンティック）
  - Matryoshka 次元削減・バッチ処理最適化
  - 評価指標（Precision@K・Recall@K・MRR・NDCG@K）
- **インストール先**: プロジェクトローカル（`.agents/skills/embedding-strategies`）
- **出典**: [wshobson/agents](https://skills.sh/wshobson/agents/embedding-strategies)

---

### `hybrid-search-implementation`
- **発動**: `/hybrid-search-implementation` で明示指定
- **概要**: ベクトル検索とキーワード検索を組み合わせたハイブリッド検索の実装ガイド（5,900 installs）
- **カバー範囲**:
  - RRF（Reciprocal Rank Fusion）による結果統合（k=60）
  - 線形結合による重み調整（alpha パラメータ）
  - クロスエンコーダーによるリランキング（50件取得→絞り込み）
  - データタイプ別の Dense/Sparse 重みガイドライン
  - MRR・Recall@5・Precision@5 による評価
- **インストール先**: プロジェクトローカル（`.agents/skills/hybrid-search-implementation`）
- **出典**: [wshobson/agents](https://skills.sh/wshobson/agents/hybrid-search-implementation)

---

## ユーティリティ

### `find-skills`
- **発動**: `/find-skills` で明示指定
- **概要**: skills.sh エコシステムから新しいスキルを検索・インストールするためのガイド
- **使用場面**: 新しい機能領域のスキルを探したいとき

---

## 発動方法まとめ

| スキル | 自動発動 | 手動呼び出し | 用途 | インストール先 |
|--------|----------|-------------|------|---------------|
| `next-best-practices` | 常時（Next.js コード全般） | ― | **実装基準（優先）** | プロジェクト |
| `vercel-ai-sdk` | チャット・ストリーミング実装時 | `/vercel-ai-sdk` | AI チャット UI 実装 | プロジェクト |
| `web-design-guidelines` | なし | `/web-design-guidelines` | UI レビュー・リファクタリング | プロジェクト |
| `vercel-composition-patterns` | なし | `/vercel-composition-patterns` | コンポーネント設計リファクタリング | プロジェクト |
| `fastapi` | FastAPI コード作業時 | `/fastapi` | バックエンド実装 | プロジェクト |
| `architecture-patterns` | アーキテクチャ設計・リファクタリング時 | `/architecture-patterns` | 設計・リファクタリング | プロジェクト |
| `pytest-coverage` | なし | `/pytest-coverage` | テスト・カバレッジ | プロジェクト |
| `rag-implementation` | なし | `/rag-implementation` | RAG パイプライン実装（網羅的） | プロジェクト |
| `embedding-strategies` | なし | `/embedding-strategies` | 埋め込みモデル選定・チャンキング最適化 | プロジェクト |
| `hybrid-search-implementation` | なし | `/hybrid-search-implementation` | ハイブリッド検索・リランキング実装 | プロジェクト |
| `find-skills` | なし | `/find-skills` | スキル検索 | プロジェクト |

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
