# IF設計書 — GET /api/data/travel

> 作成日: 2026-04-23  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `GET /api/data/travel` |
| **機能** | チャットから収集した旅行データ（travel_extractions）の一覧を取得する |
| **認証** | なし（開発フェーズ） |

---

## リクエスト

### クエリパラメータ

| パラメータ | 型 | 必須 | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `session_id` | UUID | — | — | UUID v4形式 | セッションIDでフィルタ |
| `category` | string | — | — | — | カテゴリでフィルタ（例: `destination`） |
| `limit` | integer | — | `50` | 1〜100 | 取得件数 |
| `offset` | integer | — | `0` | 0以上 | スキップ件数 |

### カテゴリ一覧

| category | 説明 |
|---|---|
| `destination` | 旅行先（都市・観光地） |
| `accommodation` | 宿泊施設 |
| `transportation` | 交通手段 |
| `food` | グルメ・食事 |
| `experience` | 体験・アクティビティ |
| `schedule` | 日程・時期 |
| `budget` | 予算・費用 |
| `tip` | 旅行のコツ・アドバイス |

### リクエスト例

```
GET /api/data/travel
GET /api/data/travel?category=destination
GET /api/data/travel?session_id=550e8400-e29b-41d4-a716-446655440000
GET /api/data/travel?category=destination&limit=20&offset=0
```

---

## レスポンス

### 200 OK

```json
{
  "items": [
    {
      "id": "aaaaaaaa-0000-0000-0000-000000000001",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "message_id": "bbbbbbbb-0000-0000-0000-000000000001",
      "category": "destination",
      "data": { "name": "京都", "type": "city", "country": "日本" },
      "confidence": 0.9,
      "created_at": "2026-04-23T10:00:00"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `items` | array | 旅行データ一覧（`created_at` 降順） |
| `items[].id` | UUID | レコードID |
| `items[].session_id` | UUID | 元セッションID |
| `items[].message_id` | UUID | 抽出元メッセージID |
| `items[].category` | string | カテゴリ |
| `items[].data` | object | 抽出した構造化データ（カテゴリにより異なる） |
| `items[].confidence` | float | 抽出信頼度（0.0〜1.0） |
| `items[].created_at` | ISO 8601 | 抽出日時（UTC） |
| `total` | integer | 条件に一致する総件数 |
| `limit` | integer | リクエストで指定した limit |
| `offset` | integer | リクエストで指定した offset |

---

### 422 Unprocessable Entity — バリデーションエラー

| 条件 | エラー内容 |
|---|---|
| `session_id` がUUID形式でない | `value is not a valid uuid` |
| `limit` が1未満または100超 | バリデーションエラー |
| `offset` が0未満 | バリデーションエラー |

---

## 処理フロー

```
1. クエリパラメータのバリデーション
        ↓
2. travel_extractions を検索
   - session_id が指定されていればフィルタ
   - category が指定されていればフィルタ
   - created_at 降順（新しい順）
   - OFFSET / LIMIT でページング
        ↓
3. TravelDataResponse を返す
```

---

## DB クエリ

```sql
SELECT COUNT(*) FROM travel_extractions
[WHERE session_id = :session_id]
[AND category = :category];

SELECT id, session_id, message_id, category, data, confidence, created_at
FROM travel_extractions
[WHERE session_id = :session_id]
[AND category = :category]
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;
```

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | フィルタなしで取得 | 200・全件が返る |
| 2 | 正常系 | category フィルタ指定 | 200・指定カテゴリのみ返る |
| 3 | 正常系 | session_id フィルタ指定 | 200・指定セッションのみ返る |
| 4 | 正常系 | データが0件 | 200・`items=[]`, `total=0` |
| 5 | 正常系 | レスポンスに必須フィールドが含まれる | items / total / limit / offset |
| 6 | 正常系 | limit / offset が正しく返る | ページング情報が正しい |
| 7 | 正常系 | created_at 降順で返る | 最初の要素が最も新しい |
| 8 | 異常系 | `session_id` がUUID形式でない | 422 |
| 9 | 異常系 | `limit=0` | 422 |
| 10 | 異常系 | `limit=101` | 422 |
| 11 | 異常系 | `offset=-1` | 422 |
| 12 | 異常系 | DBエラー | 500 |
