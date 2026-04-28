# IF設計書 — GET /api/chat/history

> 作成日: 2026-04-23  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `GET /api/chat/history` |
| **機能** | 指定セッションの会話履歴（メッセージ一覧）を時系列で取得する |
| **認証** | JWT Cookie 認証（必須） |

---

## リクエスト

### クエリパラメータ

| パラメータ | 型 | 必須 | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `session_id` | UUID | ✅ | — | UUID v4形式 | 取得対象のセッションID |
| `limit` | integer | — | `50` | 1〜100 | 1回のレスポンスに含めるメッセージ数 |
| `offset` | integer | — | `0` | 0以上 | スキップするメッセージ数（ページング用） |

### リクエスト例

```
GET /api/chat/history?session_id=550e8400-e29b-41d4-a716-446655440000
GET /api/chat/history?session_id=550e8400-e29b-41d4-a716-446655440000&limit=20&offset=0
```

---

## レスポンス

### 200 OK — 正常

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": null,
  "messages": [
    {
      "id": "aaaaaaaa-0000-0000-0000-000000000001",
      "role": "user",
      "content": "京都旅行を考えています",
      "created_at": "2026-04-23T10:00:00"
    },
    {
      "id": "aaaaaaaa-0000-0000-0000-000000000002",
      "role": "assistant",
      "content": "京都は素晴らしい旅行先ですね。おすすめのスポットをご紹介します。",
      "created_at": "2026-04-23T10:00:05"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `session_id` | UUID | セッションID |
| `title` | string \| null | セッションタイトル（任意） |
| `messages` | array | メッセージ一覧（`created_at` 昇順） |
| `messages[].id` | UUID | メッセージID |
| `messages[].role` | `"user"` \| `"assistant"` | 送信者 |
| `messages[].content` | string | メッセージ本文 |
| `messages[].created_at` | ISO 8601 datetime | 送信日時（UTC） |
| `total` | integer | セッション内の総メッセージ数（ページング計算用） |
| `limit` | integer | リクエストで指定した limit 値 |
| `offset` | integer | リクエストで指定した offset 値 |

---

### 401 Unauthorized — 未認証

```json
{ "detail": "Not authenticated" }
```

### 403 Forbidden — 他ユーザーのセッション

```json
{ "detail": "アクセス権限がありません" }
```

### 404 Not Found — セッションが存在しない

```json
{ "detail": "Session not found" }
```

### 422 Unprocessable Entity — バリデーションエラー

```json
{
  "detail": [
    {
      "loc": ["query", "session_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

**発生条件:**

| 条件 | エラー内容 |
|---|---|
| `session_id` が未指定 | `Field required` |
| `session_id` がUUID形式でない | `value is not a valid uuid` |
| `limit` が1未満または100超 | `ensure this value is greater than or equal to 1` |
| `offset` が0未満 | `ensure this value is greater than or equal to 0` |

---

## ページング仕様

- メッセージは `created_at` **昇順**（古い順）で返す
- クライアントは `total` と `limit` / `offset` を使ってページ数を計算する
- 例: `total=150`, `limit=50` の場合、3ページ分存在する
  - Page 1: `offset=0`
  - Page 2: `offset=50`
  - Page 3: `offset=100`

---

## 処理フロー

```
1. Cookie から JWT を検証 → ログインユーザーを特定
        ↓
2. クエリパラメータのバリデーション（FastAPI / Pydantic）
        ↓
3. sessions テーブルから session_id で検索
        ↓（存在しない場合 → 404）
4. session.user_id とログインユーザーの id を照合
        ↓（不一致の場合 → 403）
5. messages テーブルから session_id でフィルタ
   - 総件数を COUNT で取得（total）
   - created_at 昇順で ORDER BY
   - OFFSET / LIMIT でページング
        ↓
6. HistoryResponse を返す
```

---

## DB クエリ

```sql
-- セッション取得
SELECT id, title, user_id, created_at, updated_at
FROM sessions
WHERE id = :session_id;

-- 総件数
SELECT COUNT(*) FROM messages WHERE session_id = :session_id;

-- メッセージ取得（ページング）
SELECT id, role, content, created_at
FROM messages
WHERE session_id = :session_id
ORDER BY created_at ASC
LIMIT :limit OFFSET :offset;
```

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | 存在するセッションIDを指定 | 200、メッセージ一覧が返る |
| 2 | 正常系 | メッセージが0件のセッション | 200、`messages=[]`, `total=0` |
| 3 | 正常系 | `limit=2&offset=0` でページング | 200、最大2件のメッセージが返る |
| 4 | 正常系 | `limit=2&offset=2` で2ページ目 | 200、3件目以降のメッセージが返る |
| 5 | 正常系 | メッセージが `created_at` 昇順で返る | 最初のメッセージが最も古い |
| 6 | 正常系 | レスポンスに `total/limit/offset` が含まれる | ページング情報が正しい |
| 7 | 異常系 | 存在しない `session_id` を指定 | 404 |
| 8 | 異常系 | 他ユーザーの `session_id` を指定 | 403 |
| 9 | 異常系 | `session_id` 未指定 | 422 |
| 10 | 異常系 | `session_id` がUUID形式でない | 422 |
| 11 | 異常系 | `limit=0`（範囲外） | 422 |
| 12 | 異常系 | `limit=101`（範囲外） | 422 |
| 13 | 異常系 | `offset=-1`（負の値） | 422 |
| 14 | 異常系 | 未認証 | 401 |
| 15 | 異常系 | DBエラー発生 | 500 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-28 | 1.1.0 | JWT Cookie 認証を必須化。403（他ユーザーのセッション）を追加。処理フローに認証・所有者チェックを追記 |
| 2026-04-23 | 1.0.0 | 初版作成 |
