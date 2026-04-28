# IF設計書 — 認証 API

> 作成日: 2026-04-28  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **ベースパス** | `/api/auth` |
| **機能** | ユーザー登録・ログイン・ログアウト・認証情報取得 |
| **認証方式** | JWT を httpOnly Cookie（`access_token`）に保存。有効期限 30 日 |

---

## エンドポイント一覧

| # | メソッド | パス | 認証 | 概要 |
|---|---|---|---|---|
| 1 | POST | `/api/auth/register` | 不要 | ユーザー登録 |
| 2 | POST | `/api/auth/login` | 不要 | ログイン |
| 3 | POST | `/api/auth/logout` | 必須 | ログアウト |
| 4 | GET | `/api/auth/me` | 必須 | ログイン中のユーザー情報取得 |

---

## 共通レスポンス — UserResponse

登録・ログイン・`/me` で共通して返すユーザー情報。

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | UUID | ユーザーID |
| `email` | string | メールアドレス |
| `name` | string | 表示名 |
| `created_at` | ISO 8601 datetime | アカウント作成日時（UTC） |

---

## 1. ユーザー登録

### リクエスト

```
POST /api/auth/register
Content-Type: application/json
```

**リクエストボディ**

| フィールド | 型 | 必須 | 制約 | 説明 |
|---|---|---|---|---|
| `email` | string | ✅ | メール形式 | メールアドレス |
| `password` | string | ✅ | 8文字以上 | パスワード |
| `name` | string | ✅ | 1〜100文字 | 表示名 |

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "旅行太郎"
}
```

### レスポンス

**成功時 (201 Created)**

登録完了後、自動でログイン状態になる。レスポンスヘッダに httpOnly Cookie がセットされる。

```http
Set-Cookie: access_token=<JWT>; Path=/; Max-Age=2592000; HttpOnly; SameSite=lax
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "旅行太郎",
  "created_at": "2026-04-28T10:00:00"
}
```

**エラー時 (409 Conflict) — メールアドレス重複**

```json
{ "detail": "このメールアドレスは既に登録されています" }
```

**エラー時 (422 Unprocessable Entity) — バリデーションエラー**

| 条件 | エラー内容 |
|---|---|
| `email` が未指定または形式不正 | バリデーションエラー |
| `password` が8文字未満 | バリデーションエラー |
| `name` が未指定または100文字超 | バリデーションエラー |

---

## 2. ログイン

### リクエスト

```
POST /api/auth/login
Content-Type: application/json
```

**リクエストボディ**

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `email` | string | ✅ | メールアドレス |
| `password` | string | ✅ | パスワード |

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### レスポンス

**成功時 (200 OK)**

レスポンスヘッダに httpOnly Cookie がセットされる。

```http
Set-Cookie: access_token=<JWT>; Path=/; Max-Age=2592000; HttpOnly; SameSite=lax
```

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "旅行太郎",
  "created_at": "2026-04-28T10:00:00"
}
```

**エラー時 (401 Unauthorized)**

```json
{ "detail": "メールアドレスまたはパスワードが正しくありません" }
```

---

## 3. ログアウト

### リクエスト

```
POST /api/auth/logout
```

認証（Cookie）が必須。ボディなし。

### レスポンス

**成功時 (200 OK)**

Cookie が削除される。

```http
Set-Cookie: access_token=; Path=/; Max-Age=0; HttpOnly; SameSite=lax
```

```json
{ "message": "ログアウトしました" }
```

**エラー時 (401 Unauthorized) — 未ログイン**

```json
{ "detail": "Not authenticated" }
```

---

## 4. ログイン中のユーザー情報取得

### リクエスト

```
GET /api/auth/me
```

認証（Cookie）が必須。

### レスポンス

**成功時 (200 OK)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "旅行太郎",
  "created_at": "2026-04-28T10:00:00"
}
```

**エラー時 (401 Unauthorized) — 未ログイン**

```json
{ "detail": "Not authenticated" }
```

---

## 処理フロー

```
POST /api/auth/register
  → メールアドレス重複チェック（users テーブル）
  → パスワードをハッシュ化（bcrypt）
  → users テーブルに挿入
  → JWT 生成 → httpOnly Cookie にセット
  → UserResponse を返す

POST /api/auth/login
  → メールアドレスでユーザー検索
  → パスワード検証（bcrypt）
  → JWT 生成 → httpOnly Cookie にセット
  → UserResponse を返す

POST /api/auth/logout
  → Cookie を削除
  → {"message": "ログアウトしました"} を返す

GET /api/auth/me
  → Cookie から JWT を取得・検証
  → ユーザーIDで users テーブルを検索
  → UserResponse を返す
```

---

## Cookie 仕様

| 属性 | 値 |
|---|---|
| 名前 | `access_token` |
| HttpOnly | true（JavaScript からアクセス不可） |
| SameSite | `lax` |
| Max-Age | 2592000（30日） |
| Secure | false（開発環境。本番は true を推奨） |

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | 新規メールで登録 | 201・UserResponse・Cookie セット |
| 2 | 異常系 | 重複メールで登録 | 409 |
| 3 | 異常系 | password が7文字 | 422 |
| 4 | 正常系 | 正しい認証情報でログイン | 200・UserResponse・Cookie セット |
| 5 | 異常系 | 存在しないメールでログイン | 401 |
| 6 | 異常系 | パスワード誤りでログイン | 401 |
| 7 | 正常系 | ログイン済みでログアウト | 200・Cookie 削除 |
| 8 | 異常系 | 未ログインでログアウト | 401 |
| 9 | 正常系 | ログイン済みで /me | 200・UserResponse |
| 10 | 異常系 | 未ログインで /me | 401 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-28 | 1.0.0 | 初版作成（register / login / logout / me） |
