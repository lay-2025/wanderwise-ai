# 認証設計書

> 作成日: 2026-04-24  
> ステータス: 設計完了

---

## 概要

WanderWise AI の認証システム設計。外部サービスを使わず自前で JWT 認証を実装する。  
全 API を認証必須とし、アクセストークンは httpOnly Cookie で管理する。

---

## Cookie を選ぶ理由

| 方式 | XSS 耐性 | CSRF 耐性 | 実装コスト |
|---|---|---|---|
| **httpOnly Cookie**（今回採用） | ◎ JS からアクセス不可 | △ SameSite 設定で対策 | 低 |
| localStorage | ✗ JS から読み取り可能 | ◎ 自動送信されない | 低 |
| メモリ（React state） | ◎ | ◎ | 高（リロードで消える） |

> **httpOnly Cookie が一般的な理由**  
> XSS（クロスサイトスクリプティング）攻撃でトークンを盗まれるリスクが最も低い。  
> `SameSite=Lax` を設定することで CSRF も実用上ほぼ防げる。  
> Next.js + FastAPI の構成では Cookie が最もシンプルかつ安全な選択肢。

---

## システム構成

```
フロントエンド (Next.js)
  ↓ POST /api/auth/login（email + password）
バックエンド (FastAPI)
  ↓ パスワード検証（bcrypt）
  ↓ JWT 生成
  → Set-Cookie: access_token=<JWT>; HttpOnly; SameSite=Lax
  
以降のリクエスト
  ↓ Cookie が自動付与される
バックエンド
  ↓ Cookie から JWT を取得・検証（get_current_user 依存関数）
  → 認証済みユーザーの情報をハンドラに渡す
```

---

## DB 設計

### users テーブル

```sql
CREATE TABLE users (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email            VARCHAR(255) NOT NULL UNIQUE,
    hashed_password  VARCHAR(255) NOT NULL,
    name             VARCHAR(100) NOT NULL,
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
);
```

| カラム名 | 型 | NULL | 説明 |
|---|---|---|---|
| `id` | UUID | NO | ユーザーID |
| `email` | VARCHAR(255) | NO | ログインID（一意） |
| `hashed_password` | VARCHAR(255) | NO | bcrypt ハッシュ済みパスワード |
| `name` | VARCHAR(100) | NO | 表示名 |
| `created_at` | TIMESTAMP | NO | 登録日時 |
| `updated_at` | TIMESTAMP | NO | 最終更新日時 |

> 権限（role）カラムは初期段階では不要。将来追加する場合は Alembic マイグレーションで対応。

---

## JWT 設計

| 項目 | 値 |
|---|---|
| アルゴリズム | HS256 |
| 有効期限 | 30日 |
| ライブラリ | `python-jose[cryptography]` |
| ペイロード | `sub`（user_id）、`email`、`exp` |

### Cookie 設定

| 属性 | 値 | 理由 |
|---|---|---|
| `HttpOnly` | true | JS からのアクセスを禁止 |
| `Secure` | 本番: true / 開発: false | HTTPS 環境のみ送信 |
| `SameSite` | Lax | CSRF 対策（通常リンク遷移では送信される） |
| `Path` | `/` | 全パスで送信 |
| `Max-Age` | 2592000（30日） | JWT 有効期限と合わせる |

---

## API エンドポイント

### 一覧

| メソッド | パス | 認証必須 | 説明 |
|---|---|---|---|
| POST | `/api/auth/register` | ✗ | ユーザー登録 |
| POST | `/api/auth/login` | ✗ | ログイン・Cookie 発行 |
| POST | `/api/auth/logout` | ✓ | ログアウト・Cookie 削除 |
| GET | `/api/auth/me` | ✓ | 認証済みユーザー情報取得 |

---

### POST /api/auth/register

**リクエスト**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "山田 太郎"
}
```

| フィールド | 型 | 制約 |
|---|---|---|
| `email` | string | メール形式、最大255文字、重複不可 |
| `password` | string | 8文字以上 |
| `name` | string | 1文字以上、最大100文字 |

**レスポンス**

```json
// 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "山田 太郎",
  "created_at": "2026-04-24T10:00:00"
}
```

| ステータス | 条件 |
|---|---|
| 201 | 登録成功 |
| 409 | email が既に登録済み |
| 422 | バリデーションエラー |

---

### POST /api/auth/login

**リクエスト**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**レスポンス**

```json
// 200 OK
// Set-Cookie: access_token=<JWT>; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "山田 太郎"
}
```

| ステータス | 条件 |
|---|---|
| 200 | ログイン成功（Cookie を発行） |
| 401 | メールアドレスまたはパスワードが不正 |
| 422 | バリデーションエラー |

---

### POST /api/auth/logout

Cookie を削除してログアウトする。

**レスポンス**

```json
// 200 OK
// Set-Cookie: access_token=; HttpOnly; Max-Age=0
{ "message": "ログアウトしました" }
```

---

### GET /api/auth/me

Cookie の JWT を検証し、認証済みユーザーの情報を返す。

**レスポンス**

```json
// 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "山田 太郎",
  "created_at": "2026-04-24T10:00:00"
}
```

| ステータス | 条件 |
|---|---|
| 200 | 認証済み |
| 401 | Cookie なし・JWT 不正・期限切れ |

---

## バックエンド実装方針

### ディレクトリ構成

```
backend/app/
├── models/
│   └── user.py           # SQLAlchemy User モデル
├── schemas/
│   └── auth.py           # RegisterRequest / LoginRequest / UserResponse
├── services/
│   └── auth_service.py   # パスワードハッシュ・JWT 生成・検証
├── routers/
│   └── auth.py           # /api/auth/* エンドポイント
└── core/
    └── security.py       # get_current_user 依存関数
```

### get_current_user 依存関数

全エンドポイントで共通して使う認証依存関数。

```python
# 使用例
@router.get("/protected")
def protected(current_user: CurrentUserDep) -> ...:
    ...
```

Cookie から JWT を取得 → 検証 → User オブジェクトを返す。  
Cookie がない・JWT が不正・期限切れの場合は `401 Unauthorized` を返す。

### 依存パッケージ

```
python-jose[cryptography]   # JWT 生成・検証
passlib[bcrypt]             # パスワードハッシュ
```

---

## フロントエンド実装方針

### 認証フロー

```
1. /login ページでフォーム送信
   → POST /api/auth/login
   → 成功: Cookie が自動設定される → / にリダイレクト
   → 失敗: エラーメッセージ表示

2. 全ページで GET /api/auth/me を呼び出す
   → 成功: 認証済み → ページ表示
   → 401: /login にリダイレクト

3. ログアウトボタン押下
   → POST /api/auth/logout → /login にリダイレクト
```

### ルート保護

Next.js の `middleware.ts` で未認証ユーザーを `/login` にリダイレクトする。

```
middleware.ts
  → /login 以外のパスにアクセス
  → GET /api/auth/me で認証確認
  → 401 → /login にリダイレクト
```

---

## セキュリティ考慮事項

| 項目 | 対策 |
|---|---|
| パスワード保存 | bcrypt でハッシュ化（平文保存なし） |
| XSS | httpOnly Cookie でトークンを JS から隔離 |
| CSRF | SameSite=Lax + 状態変更は POST メソッドに限定 |
| ブルートフォース | 初期段階では対策なし（将来: レートリミット追加） |
| トークン漏洩 | 本番環境では Secure 属性で HTTPS のみ送信 |

---

## 実装ステップ

1. `users` テーブル追加（Alembic マイグレーション）
2. `python-jose` / `passlib` を `requirements.txt` に追加
3. `core/security.py` — JWT 生成・検証・`get_current_user` 依存関数
4. `services/auth_service.py` — パスワードハッシュ・ユーザー CRUD
5. `routers/auth.py` — 4エンドポイント実装
6. 既存ルーターに `get_current_user` を追加（全 API 保護）
7. Alembic マイグレーション実行
8. フロントエンド: ログインページ・middleware.ts 実装
