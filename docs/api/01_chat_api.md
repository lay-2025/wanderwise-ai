# チャットAPI インターフェース設計書

## 概要

| 項目 | 内容 |
|------|------|
| ベースURL | `http://localhost:8000` |
| 認証 | なし（開発環境） |
| データ形式 | JSON |
| 文字コード | UTF-8 |

---

## エンドポイント一覧

| # | メソッド | パス | 概要 |
|---|----------|------|------|
| 1 | GET | `/health` | ヘルスチェック |
| 2 | POST | `/api/chat` | チャットメッセージ送受信・データ収集 |

---

## 1. ヘルスチェック

### リクエスト

```
GET /health
```

### レスポンス

**成功時 (200 OK)**

```json
{
  "status": "ok"
}
```

---

## 2. チャットメッセージ送受信

### リクエスト

```
POST /api/chat
Content-Type: application/json
```

**リクエストボディ**

| フィールド | 型 | 必須 | 説明 |
|------------|------|------|------|
| `message` | string | ○ | ユーザーのメッセージ |
| `session_id` | UUID | ✗ | セッションID。省略時は新規セッションを自動作成 |

```json
{
  "message": "京都のおすすめ観光スポットを教えてください",
  "session_id": "1e01979e-6168-4b5f-b2c5-577c212b74c6"
}
```

### レスポンス

**成功時 (200 OK)**

| フィールド | 型 | 説明 |
|------------|------|------|
| `response` | string | AIの返答メッセージ |
| `session_id` | UUID | セッションID（次回リクエストで引き継ぎに使用） |
| `extractions` | array | ユーザーメッセージから抽出した旅行データの一覧 |

**`extractions` の各要素**

| フィールド | 型 | 説明 |
|------------|------|------|
| `category` | string | 旅行情報のカテゴリ（後述） |
| `data` | object | 抽出した構造化データ（カテゴリにより内容が異なる） |
| `confidence` | float | 抽出信頼度（0.0〜1.0） |

```json
{
  "response": "京都のおすすめ観光スポットをご紹介します。...",
  "session_id": "1e01979e-6168-4b5f-b2c5-577c212b74c6",
  "extractions": [
    {
      "category": "destination",
      "data": { "name": "嵐山", "type": "place" },
      "confidence": 0.9
    },
    {
      "category": "accommodation",
      "data": { "name": "リッツカールトン", "type": "hotel" },
      "confidence": 0.9
    },
    {
      "category": "budget",
      "data": { "amount": 100000, "currency": "JPY" },
      "confidence": 0.9
    }
  ]
}
```

**エラー時 (500 Internal Server Error)**

| フィールド | 型 | 説明 |
|------------|------|------|
| `detail` | string | エラー内容 |

```json
{
  "detail": "エラーの詳細メッセージ"
}
```

---

### extractions のカテゴリ一覧

| category | data の例 | 説明 |
|---|---|---|
| `destination` | `{"name": "京都", "type": "city"}` | 旅行先（都市・観光地・国） |
| `accommodation` | `{"name": "リッツカールトン", "type": "hotel"}` | 宿泊施設 |
| `transportation` | `{"mode": "train", "details": "新幹線"}` | 交通手段 |
| `food` | `{"name": "湯豆腐", "type": "料理"}` | グルメ・食事 |
| `experience` | `{"name": "着物レンタル", "type": "activity"}` | 体験・アクティビティ |
| `schedule` | `{"start": "2026-05-01", "duration_days": 3}` | 日程・時期 |
| `budget` | `{"amount": 80000, "currency": "JPY"}` | 予算・費用 |
| `tip` | `{"content": "朝一番が空いておすすめ"}` | 旅行のコツ・情報 |

---

### 処理フロー

```
フロントエンド
    │
    │ POST /api/chat {"message": "...", "session_id": "..."}
    ▼
FastAPI (backend:8000)
    │
    ├─① セッション取得または新規作成（PostgreSQL: sessions）
    │
    ├─② ユーザーメッセージを保存（PostgreSQL: messages）
    │
    ├─③ LangChain ChatOllama で返答生成
    │       └─ Ollama (ollama:11434) / qwen2.5:3b
    │
    ├─④ アシスタント返答を保存（PostgreSQL: messages）
    │
    ├─⑤ ユーザーメッセージから旅行データを抽出
    │       └─ Ollama (ollama:11434) / qwen2.5:3b（JSON形式で抽出）
    │
    ├─⑥ 抽出データを保存（PostgreSQL: travel_extractions）
    │
    │ {"response": "...", "session_id": "...", "extractions": [...]}
    ▼
フロントエンド
```

---

### システムプロンプト

**チャット用**

> あなたは旅行アシスタントAIです。
> 旅行に関する質問を中心に、日本語で親切・丁寧に答えてください。
> 旅行以外の一般的な質問にも対応できます。

**旅行データ抽出用**（内部処理・フロントエンドには非公開）

> ユーザーのメッセージから旅行に関する情報を抽出し、JSON配列のみで返す。

---

### 使用モデル

| 用途 | モデル名 | 説明 |
|------|----------|------|
| チャット（推論） | `qwen2.5:3b` | Alibaba製。日本語対応 |
| 旅行データ抽出 | `qwen2.5:3b` | 同モデルをJSON抽出プロンプトで流用 |
| 埋め込み（RAG用） | `nomic-embed-text` | テキストのベクトル化（Step 2で実装予定） |

---

## 関連ファイル

| ファイル | 説明 |
|----------|------|
| `backend/app/routers/chat.py` | チャットエンドポイントの実装 |
| `backend/app/schemas/chat.py` | リクエスト・レスポンスのPydanticスキーマ |
| `backend/app/services/chat_service.py` | セッション・メッセージのDB操作 |
| `backend/app/services/extraction_service.py` | 旅行データ抽出ロジック |
| `backend/app/main.py` | FastAPIアプリのエントリポイント |

## 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|----------|
| 2026-04-22 | 1.1.0 | セッション管理・メッセージ保存・旅行データ抽出を追加 |
| 2026-04-21 | 1.0.0 | 初版作成（チャット機能） |
