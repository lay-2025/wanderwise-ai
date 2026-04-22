# テーブル定義書

> 対象DB: PostgreSQL 15 / `travel_db`
> 最終更新: 2026-04-22

---

## sessions — チャットセッション

チャットの会話単位を管理する。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | セッションID |
| `title` | `varchar(255)` | YES | — | — | セッション名（任意） |
| `created_at` | `timestamp` | NO | `NOW()` | — | 開始日時 |
| `updated_at` | `timestamp` | NO | `NOW()` | — | 最終更新日時 |

---

## messages — メッセージ履歴

チャットの全発言を時系列で保存する。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | メッセージID |
| `session_id` | `uuid` | NO | — | FK → sessions.id | 所属セッション |
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
| `session_id` | `uuid` | NO | — | FK → sessions.id | 所属セッション |
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

ベクトル化対象のドキュメントを管理する。チャット由来の抽出データや管理者がアップロードしたPDF・URLが格納される。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | ドキュメントID |
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

---

## chunks — ドキュメントチャンク

ドキュメントをベクトル化単位（チャンク）に分割して管理する。ChromaDB のベクトルと `chroma_id` で紐づく。

| カラム名 | データ型 | NULL | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `id` | `uuid` | NO | `uuid_generate_v4()` | PK | チャンクID |
| `document_id` | `uuid` | NO | — | FK → documents.id | 元ドキュメント |
| `chunk_index` | `integer` | NO | — | — | 何番目のチャンクか（0始まり） |
| `content` | `text` | NO | — | — | チャンク本文 |
| `chroma_id` | `varchar(255)` | YES | — | — | ChromaDB上のID（ベクトル化後に更新） |
| `created_at` | `timestamp` | NO | `NOW()` | — | 作成日時 |

---

## 関連ファイル

| 種別 | パス |
|---|---|
| ER図 | `docs/db/01_er_diagram.md` |
| SQLAlchemyモデル | `backend/app/models/` |
| Alembicマイグレーション | `backend/alembic/versions/` |
| DB接続設定 | `backend/app/core/database.py` |
