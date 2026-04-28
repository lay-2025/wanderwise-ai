# IF設計書 — セッション管理 API

> 作成日: 2026-04-28  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **ベースパス** | `/api/chat/sessions` |
| **機能** | チャットセッションの一覧取得・新規作成・名称変更・削除 |
| **認証** | JWT Cookie 認証（必須） |

---

## エンドポイント一覧

| # | メソッド | パス | 概要 |
|---|---|---|---|
| 1 | GET | `/api/chat/sessions` | セッション一覧取得 |
| 2 | POST | `/api/chat/sessions` | 新規セッション作成 |
| 3 | PATCH | `/api/chat/sessions/{session_id}` | セッション名称変更 |
| 4 | DELETE | `/api/chat/sessions/{session_id}` | セッション削除 |

---

## 1. セッション一覧取得

### リクエスト

```
GET /api/chat/sessions
```

クエリパラメータなし。ログインユーザーのセッションのみ返す。

### レスポンス

**成功時 (200 OK)**

`updated_at` 降順（最近活動したセッションが先頭）で返す。

```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "京都旅行の相談",
      "created_at": "2026-04-28T10:00:00",
      "updated_at": "2026-04-28T12:30:00",
      "message_count": 8
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": null,
      "created_at": "2026-04-27T09:00:00",
      "updated_at": "2026-04-27T09:00:00",
      "message_count": 0
    }
  ],
  "total": 2
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `sessions` | array | セッション一覧（`updated_at` 降順） |
| `sessions[].id` | UUID | セッションID |
| `sessions[].title` | string \| null | セッションタイトル（未設定時は null） |
| `sessions[].created_at` | ISO 8601 datetime | 作成日時（UTC） |
| `sessions[].updated_at` | ISO 8601 datetime | 最終更新日時（UTC）。メッセージ送受信のたびに更新 |
| `sessions[].message_count` | integer | セッション内のメッセージ件数 |
| `total` | integer | 取得したセッション総数 |

---

## 2. 新規セッション作成

### リクエスト

```
POST /api/chat/sessions
```

ボディなし。

### レスポンス

**成功時 (201 Created)**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "title": null,
  "created_at": "2026-04-28T13:00:00",
  "updated_at": "2026-04-28T13:00:00"
}
```

#### フィールド定義（SessionResponse）

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | UUID | 新規発行されたセッションID |
| `title` | string \| null | タイトル（作成直後は null） |
| `created_at` | ISO 8601 datetime | 作成日時（UTC） |
| `updated_at` | ISO 8601 datetime | 最終更新日時（UTC） |

---

## 3. セッション名称変更

### リクエスト

```
PATCH /api/chat/sessions/{session_id}
Content-Type: application/json
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|---|---|---|
| `session_id` | UUID | 変更対象のセッションID |

**リクエストボディ**

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `title` | string | ✅ | 新しいタイトル |

```json
{ "title": "大阪・京都旅行プラン" }
```

### レスポンス

**成功時 (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "大阪・京都旅行プラン",
  "created_at": "2026-04-28T10:00:00",
  "updated_at": "2026-04-28T14:00:00"
}
```

**エラー時 (404 Not Found) — セッションが存在しない、または他ユーザーのセッション**

```json
{ "detail": "Session not found" }
```

---

## 4. セッション削除

### リクエスト

```
DELETE /api/chat/sessions/{session_id}
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|---|---|---|
| `session_id` | UUID | 削除対象のセッションID |

### レスポンス

**成功時 (204 No Content)**

レスポンスボディなし。

**エラー時 (404 Not Found) — セッションが存在しない、または他ユーザーのセッション**

```json
{ "detail": "Session not found" }
```

---

## 処理フロー

```
GET /api/chat/sessions
  → ログインユーザーのセッションを updated_at 降順で取得
  → messages テーブルを LEFT JOIN して message_count を集計
  → SessionListResponse を返す

POST /api/chat/sessions
  → 新規 ChatSession を作成（user_id = ログインユーザー）
  → SessionResponse を返す (201)

PATCH /api/chat/sessions/{session_id}
  → session_id かつ user_id でセッションを検索
  → title を更新
  → SessionResponse を返す
  （セッションが存在しない / 他ユーザーの場合 → 404）

DELETE /api/chat/sessions/{session_id}
  → session_id かつ user_id でセッションを検索
  → messages / travel_extractions / documents を CASCADE 削除
  → 204 を返す
  （セッションが存在しない / 他ユーザーの場合 → 404）
```

---

## セキュリティ

- 全エンドポイントで JWT Cookie 認証を要求する
- PATCH / DELETE は `user_id` でセッション所有者を検証する。他ユーザーのセッションは 404 として扱い、存在の有無を漏らさない

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | セッションあり → 一覧取得 | 200・sessions / total が返る |
| 2 | 正常系 | セッションなし → 一覧取得 | 200・`sessions=[]`, `total=0` |
| 3 | 正常系 | 新規セッション作成 | 201・SessionResponse（title=null） |
| 4 | 正常系 | 存在するセッションをリネーム | 200・title が変わった SessionResponse |
| 5 | 異常系 | 存在しないセッションをリネーム | 404 |
| 6 | 異常系 | 他ユーザーのセッションをリネーム | 404 |
| 7 | 正常系 | 存在するセッションを削除 | 204 |
| 8 | 異常系 | 存在しないセッションを削除 | 404 |
| 9 | 異常系 | 他ユーザーのセッションを削除 | 404 |
| 10 | 異常系 | 未認証で一覧取得 | 401 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-28 | 1.0.0 | 初版作成（GET/POST/PATCH/DELETE セッション管理） |
