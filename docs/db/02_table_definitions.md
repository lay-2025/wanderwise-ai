# テーブル定義書

> 対象DB: PostgreSQL 15 / `travel_db`
> 最終更新: 2026-04-27

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-22 | 1.0.0 | 初版作成（sessions / messages / travel_extractions / documents / chunks） |
| 2026-04-27 | 1.1.0 | users テーブル追加・sessions.user_id 追加・documents に created_by_user_id / source_session_id 追加・ChromaDB メタデータ仕様追加 |

---

---

## users — ユーザー

認証済みユーザーを管理する。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | ユーザーID |
| `email` | `varchar(255)` | NO | — | UNIQUE | メールアドレス |
| `hashed_password` | `varchar(255)` | NO | — | — | bcrypt ハッシュ化済みパスワード |
| `name` | `varchar(100)` | NO | — | — | 表示名 |
| `created_at` | `timestamp` | NO | `NOW()` | — | 登録日時 |
| `updated_at` | `timestamp` | NO | `NOW()` | — | 最終更新日時 |

---

## sessions — チャットセッション

チャットの会話単位を管理する。`user_id` でユーザーと紐づき、ユーザー専有データとなる。
タイトルは初回メッセージの先頭 40 文字から自動生成される。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | セッションID |
| `user_id` | `uuid` | NO | — | FK → users.id CASCADE | セッション所有者 |
| `title` | `varchar(255)` | YES | — | — | セッション名（初回メッセージから自動生成） |
| `created_at` | `timestamp` | NO | `NOW()` | — | 開始日時 |
| `updated_at` | `timestamp` | NO | `NOW()` | — | 最終更新日時（メッセージ送信時に更新） |

---

## messages — メッセージ履歴

チャットの全発言を時系列で保存する。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | メッセージID |
| `session_id` | `uuid` | NO | — | FK → sessions.id CASCADE | 所属セッション |
| `role` | `varchar(20)` | NO | — | CHECK | 発言者。`user` or `assistant` |
| `content` | `text` | NO | — | — | メッセージ本文 |
| `created_at` | `timestamp` | NO | `NOW()` | — | 送信日時 |

**CHECK制約:**
- `role IN ('user', 'assistant')`

---

## travel_extractions — 抽出旅行データ

ユーザーの発言からLLMが抽出した旅行情報を構造化して保存する。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | 抽出データID |
| `message_id` | `uuid` | NO | — | FK → messages.id | 抽出元メッセージ |
| `session_id` | `uuid` | NO | — | FK → sessions.id CASCADE | 所属セッション |
| `category` | `varchar(50)` | NO | — | — | カテゴリ（後述） |
| `data` | `jsonb` | NO | — | — | 構造化された旅行情報 |
| `confidence` | `float8` | NO | `1.0` | — | LLM抽出信頼度（0.0〜1.0） |
| `created_at` | `timestamp` | NO | `NOW()` | — | 抽出日時 |

**category の値と data の例:**

| category | data 例 |
|---|---|
| `destination` | `{"name": "京都", "type": "city", "country": "日本"}` |
| `accommodation` | `{"name": "リッツカールトン", "type": "hotel", "location": "京都"}` |
| `transportation` | `{"type": "新幹線", "from": "東京", "to": "京都"}` |
| `food` | `{"name": "湯豆腐", "type": "料理", "location": "京都"}` |
| `experience` | `{"name": "着物レンタル", "type": "activity"}` |
| `schedule` | `{"start": "2026-05-01", "end": "2026-05-03", "duration_days": 3}` |
| `budget` | `{"amount": 80000, "currency": "JPY", "type": "total"}` |
| `tip` | `{"content": "朝一番の訪問がおすすめ", "target": "嵐山"}` |

---

## documents — 学習用ドキュメント

ベクトル化対象のドキュメントを管理する。チャット由来の抽出データや管理者がアップロードしたテキストが格納される。
全ユーザーで共有されるが、`created_by_user_id` と `source_session_id` で出所を追跡できる。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | ドキュメントID |
| `created_by_user_id` | `uuid` | YES | — | FK → users.id SET NULL | 作成者（ユーザー削除時は NULL に） |
| `source_session_id` | `uuid` | YES | — | FK → sessions.id SET NULL | チャット由来の場合のセッション（セッション削除時は NULL に） |
| `title` | `varchar(255)` | NO | — | — | ドキュメント名 |
| `content` | `text` | NO | — | — | 本文全体 |
| `source` | `varchar(50)` | NO | — | CHECK | データ出所 |
| `status` | `varchar(50)` | NO | `'pending'` | CHECK | ベクトル化の進捗状態 |
| `created_at` | `timestamp` | NO | `NOW()` | — | 登録日時 |
| `updated_at` | `timestamp` | NO | `NOW()` | — | 最終更新日時 |

**CHECK制約:**
- `source IN ('chat', 'upload', 'manual')`
- `status IN ('pending', 'processing', 'vectorized', 'failed')`

**status の遷移:**
```
pending → processing → vectorized
                    ↘ failed
```

**source 別の出所情報:**

| source | created_by_user_id | source_session_id |
|---|---|---|
| `chat` | チャットしたユーザーの ID | チャットのセッション ID |
| `upload` | アップロードしたユーザーの ID | NULL |
| `manual` | 登録したユーザーの ID | NULL |

---

## chunks — ドキュメントチャンク

ドキュメントをベクトル化単位（チャンク）に分割して管理する。ChromaDB のベクトルと `chroma_id` で紐づく。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | チャンクID |
| `document_id` | `uuid` | NO | — | FK → documents.id CASCADE | 元ドキュメント |
| `chunk_index` | `integer` | NO | — | — | 何番目のチャンクか（0始まり） |
| `content` | `text` | NO | — | — | チャンク本文 |
| `chroma_id` | `varchar(255)` | YES | — | — | ChromaDB上のID（ベクトル化後に更新） |
| `created_at` | `timestamp` | NO | `NOW()` | — | 作成日時 |

---

## ChromaDB メタデータ

各ベクトルに付与するメタデータ（`chunks` テーブルとの対応）：

| フィールド | 型 | 説明 |
|---|---|---|
| `document_id` | `str` | PostgreSQL の `documents.id` |
| `chunk_index` | `int` | チャンク番号（0始まり） |
| `source` | `str` | `'chat'` / `'upload'` / `'manual'` |
| `created_by_user_id` | `str \| None` | 作成者ユーザーID |
| `source_session_id` | `str \| None` | チャット由来セッションID |

---

## 関連ファイル

| 種別 | パス |
|---|---|
| ER図 | `docs/db/01_er_diagram.md` |
| SQLAlchemyモデル | `backend/app/models/` |
| Alembicマイグレーション | `backend/alembic/versions/` |
| DB接続設定 | `backend/app/core/database.py` |
