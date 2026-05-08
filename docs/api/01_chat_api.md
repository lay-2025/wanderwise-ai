# IF設計書 — POST /api/chat

> 作成日: 2026-04-21  
> ステータス: 一部未実装あり（後述）

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `POST /api/chat` |
| **機能** | ユーザーメッセージに対して LLM が回答を生成する。比較モード ON 時は RAGなし回答を追加で生成して並べて表示する |
| **認証** | JWT Cookie 認証（必須） |

---

## モード仕様

### 通常モード（`compare_mode=false`）

- DB への保存（messages・travel_extractions）あり
- `is_active=True` かつ `status=vectorized` のドキュメントのみを RAG 対象とする
- 参照したドキュメント情報（`rag_sources`）をレスポンスに含める

### 比較モード（`compare_mode=true`）

- **RAGあり側（左カラム）は通常モードと完全に同じ処理を行う**
  - DB への保存あり（messages・travel_extractions）
  - セッション管理あり
  - `rag_sources` をレスポンスに含める
- **RAGなし側（右カラム）はLLMを追加で1回呼び出すのみ**
  - DB への保存なし
  - 旅行データ抽出なし
  - `response_without_rag` としてレスポンスに追加

---

## リクエスト

### ボディ

```json
{
  "message": "京都でおすすめの観光地は？",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "compare_mode": false
}
```

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| `message` | string | ✅ | — | ユーザーのメッセージ |
| `session_id` | uuid \| null | — | null | セッションID。未指定時は新規セッションを作成 |
| `compare_mode` | boolean | — | `false` | true のとき RAGなし回答を追加で生成する |

---

## レスポンス

### 通常モード — 200 OK

```json
{
  "response": "京都のおすすめ観光地は嵐山や金閣寺です。特に...",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "extractions": [
    { "category": "destination", "data": { "name": "京都" }, "confidence": 1.0 }
  ],
  "rag_sources": [
    {
      "document_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "document_title": "嵐山観光ガイド 2026",
      "chunk": "嵐山は竹林や渡月橋で有名な...",
      "score": 0.87
    }
  ],
  "response_without_rag": null
}
```

### 比較モード — 200 OK

```json
{
  "response": "嵐山観光ガイドによると、春の桜シーズンは...",
  "session_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "extractions": [
    { "category": "destination", "data": { "name": "京都" }, "confidence": 1.0 }
  ],
  "rag_sources": [
    {
      "document_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "document_title": "嵐山観光ガイド 2026",
      "chunk": "嵐山は竹林や渡月橋で有名な...",
      "score": 0.87
    }
  ],
  "response_without_rag": "京都の嵐山は竹林や渡月橋が有名で..."
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `response` | string | RAGあり LLM の回答（通常・比較モード共通） |
| `session_id` | uuid | セッションID（通常・比較モード共通で返却） |
| `extractions` | array | 抽出された旅行データ（通常・比較モード共通） |
| `rag_sources` | array | 参照されたドキュメント一覧（なければ空配列） |
| `rag_sources[].document_id` | string \| null | ドキュメントID |
| `rag_sources[].document_title` | string \| null | ドキュメント名 |
| `rag_sources[].chunk` | string | 参照されたチャンク本文 |
| `rag_sources[].score` | float | 類似度スコア（0.0〜1.0） |
| `response_without_rag` | string \| null | RAGなしの回答（比較モード時のみ。通常モードは null） |

---

## 処理フロー

### 通常モード

```
1. セッション取得または新規作成
2. ユーザーメッセージを messages に保存
3. セッションタイトルを自動設定（初回のみ）
4. PostgreSQL から is_active=True かつ status=vectorized の document_id 取得
5. document_id が 0 件 → rag_sources=[] で 7 へ
   document_id が 1 件以上 → ChromaDB で類似検索（where フィルタあり）
                            → score < 0.6 のチャンクを除外
                            → rag_sources 構築
6. rag_sources があればシステムプロンプトに RAG コンテキストを付与
7. LLM 呼び出し（qwen2.5:3b）→ response
8. アシスタント返答を messages に保存
9. 旅行データ抽出 → travel_extractions に保存
10. セッション updated_at を更新
11. レスポンス返却（response_without_rag=null）
```

### 比較モード

```
1〜10. 通常モードと完全に同じ処理（DB保存・データ収集を含む）
11. LLM 追加呼び出し（RAG コンテキストなし）→ response_without_rag
12. レスポンス返却（response_without_rag あり）
```

> **ポイント:** 比較モードでは通常処理が完了した後に RAGなし呼び出しを逐次追加するだけ。  
> 既存の通常モード処理を変更せず、最後に1ステップ追加するシンプルな実装になる。

---

## RAG コンテキスト構築仕様

### is_active フィルタ

```python
# PostgreSQL からアクティブ document_id 取得
active_ids = db.query(Document.id).filter(
    Document.is_active == True,
    Document.status == "vectorized"
).all()

# ChromaDB where フィルタ
where = {"document_id": {"$in": [str(id) for id in active_ids]}}
```

**エッジケース:**

| 状況 | 動作 |
|---|---|
| アクティブドキュメントが 0 件 | ChromaDB 検索をスキップ。`rag_sources=[]` |
| ChromaDB 接続エラー | エラーを握りつぶし `rag_sources=[]`。チャットは継続 |
| score < 0.6 のチャンクのみ | `rag_sources=[]`（閾値未満は除外） |
| ChromaDB コレクション未作成 | `rag_sources=[]` |

### コレクション設定

| 設定 | 値 |
|---|---|
| コレクション名 | `travel_knowledge` |
| 返却件数上限 | 5件 |
| 最低スコア閾値 | 0.6 |
| 埋め込みモデル | `nomic-embed-text`（Ollama） |

---

## システムプロンプト構造

```
[ベースプロンプト]
あなたは旅行アシスタントAIです。
旅行に関する質問を中心に、日本語で親切・丁寧に答えてください。
旅行以外の一般的な質問にも対応できます。

[RAGコンテキストセクション（rag_sources が存在する場合のみ追加）]
【参考情報（過去の旅行データ）】
- チャンク1のテキスト
- チャンク2のテキスト
上記の参考情報があれば活用して、より具体的に回答してください。
```

比較モードの RAGなし呼び出しでは、RAGコンテキストセクションを除いたベースプロンプトのみで LLM に渡す。

---

## フロントエンド表示仕様

### 通常モード — 参照ドキュメント表示

`rag_sources` が 1 件以上の場合、アシスタントメッセージの下部に折りたたみ式で表示する。`rag_sources` が空の場合は表示しない（RAGなしで回答したことは明示しない）。

```
┌─────────────────────────────────────┐
│ アシスタントの回答テキスト...        │
│                                     │
│ ▼ 参照ドキュメント (2件)            │  ← クリックで展開/折りたたみ
│   📄 嵐山観光ガイド 2026  87% 一致  │
│   📄 Wikipedia 東京都     72% 一致  │
└─────────────────────────────────────┘
```

### 比較モード — 2カラム表示

チャット入力欄の上部にトグルボタンを配置する。ON のとき送信後の回答エリアが2カラムになる。

**カラム配置:**

| 左カラム | 右カラム |
|---|---|
| ✨ RAGあり | 📚 RAGなし |
| ドキュメントを参照した回答 | モデル自身の知識のみの回答 |
| `response` フィールド | `response_without_rag` フィールド |
| `rag_sources` を表示 | 参照ドキュメントなし |

```
[🔀 比較モード ON]  ← トグルボタン（チャット入力欄上部）

┌──────────────────┬──────────────────┐
│  ✨ RAGあり      │  📚 RAGなし      │
│  ドキュメントを  │  モデル自身の    │
│  参照して回答    │  知識のみで回答  │
│                  │                  │
│  〜〜〜〜〜〜    │  〜〜〜〜〜〜    │
│                  │                  │
│ 📄 嵐山ガイド   │                  │
│    87% 一致      │                  │
└──────────────────┴──────────────────┘
```

**比較モードのUX仕様:**

| 項目 | 仕様 |
|---|---|
| ローディング | 左（RAGあり）生成中 → 右（RAGなし）生成中と段階的に表示 |
| DB 保存 | RAGありの返答は通常通り保存（サイドバーのセッション一覧が更新される） |
| 旅行データ収集 | 通常通り実施 |
| チャット履歴 | 比較モードで送信したメッセージもセッションに蓄積される |
| 比較モード解除後 | 通常の1カラム表示に戻る |

---

## エラーレスポンス

| ステータス | 条件 |
|---|---|
| 401 | 未認証 |
| 500 | LLM / DB 接続エラー |

---

## 使用モデル

| 用途 | モデル名 |
|---|---|
| チャット（推論） | `qwen2.5:3b` |
| 旅行データ抽出（内部） | `qwen2.5:3b` |
| 埋め込み（RAG用） | `nomic-embed-text` |

---

## extractions のカテゴリ一覧

| category | data の例 |
|---|---|
| `destination` | `{"name": "京都", "type": "city"}` |
| `accommodation` | `{"name": "リッツカールトン", "type": "hotel"}` |
| `transportation` | `{"mode": "train", "details": "新幹線"}` |
| `food` | `{"name": "湯豆腐", "type": "料理"}` |
| `experience` | `{"name": "着物レンタル", "type": "activity"}` |
| `schedule` | `{"start": "2026-05-01", "duration_days": 3}` |
| `budget` | `{"amount": 80000, "currency": "JPY"}` |
| `tip` | `{"content": "朝一番が空いておすすめ"}` |

---

## 実装状況

| 機能 | 状態 |
|---|---|
| 通常チャット（LLM 呼び出し・DB保存） | ✅ 実装済み |
| RAG コンテキスト付与 | ✅ 実装済み |
| 旅行データ抽出・保存 | ✅ 実装済み |
| is_active フィルタ（RAG対象をアクティブドキュメントに限定） | ✅ 実装済み |
| rag_sources のレスポンス返却 | ✅ 実装済み |
| 参照ドキュメント折りたたみ表示（フロントエンド） | ✅ 実装済み |
| 比較モード（compare_mode・RAGなし追加呼び出し） | ✅ 実装済み |
| 比較モード UI（2カラム・トグルボタン） | ✅ 実装済み |

---

## 関連ファイル

| ファイル | 説明 |
|---|---|
| `backend/app/routers/chat.py` | チャットエンドポイント |
| `backend/app/schemas/chat.py` | リクエスト・レスポンス スキーマ |
| `backend/app/services/chat_service.py` | セッション・メッセージ DB 操作 |
| `backend/app/services/extraction_service.py` | 旅行データ抽出 |
| `backend/app/services/rag_service.py` | RAG コンテキスト構築 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-05-08 | 2.0.0 | is_active フィルタ・rag_sources・compare_mode を設計に追加。フロントエンド表示仕様を追加 |
| 2026-04-28 | 1.2.0 | 認証要件を追加。処理フローに RAG・touch_session を追記 |
| 2026-04-22 | 1.1.0 | セッション管理・メッセージ保存・旅行データ抽出を追加 |
| 2026-04-21 | 1.0.0 | 初版作成 |
