# IF設計書 — POST /api/learning/vectorize

> 作成日: 2026-04-23  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `POST /api/learning/vectorize` |
| **機能** | チャットから収集した旅行データ（travel_extractions）を documents / chunks に変換し、ChromaDB にベクトル保存する |
| **認証** | JWT Cookie 認証（必須） |
| **トリガー** | 管理画面の「ベクトル化を実行」ボタン |
| **処理方式** | 同期（完了まで待機） |
| **対象ソース** | `source = chat` のみ |

---

## リクエスト

```
POST /api/learning/vectorize
Content-Type: application/json（ボディなし）
```

---

## レスポンス

### 200 OK

```json
{
  "processed": 3,
  "skipped": 1,
  "failed": 0,
  "total_chunks": 12
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `processed` | integer | 新たにベクトル化したセッション数 |
| `skipped` | integer | スキップしたセッション数（既に vectorized） |
| `failed` | integer | 失敗したセッション数 |
| `total_chunks` | integer | 今回作成したチャンク総数 |

### 500 Internal Server Error

```json
{ "detail": "エラー内容" }
```

---

## 処理フロー

```
1. travel_extractions を持つセッションを全件取得
        ↓
2. セッションごとに処理
   ├─ document（title: chat-session-{session_id}）が vectorized → スキップ
   ├─ document が failed → 削除して再処理
   └─ document なし → 新規処理
        ↓
3. travel_extractions を自然文テキストに変換（カテゴリ別テンプレート）
        ↓
4. document を作成（status: processing）
        ↓
5. extraction ごとに1チャンクを作成（セマンティックチャンキング）
        ↓
6. nomic-embed-text でバッチ embedding 生成
        ↓
7. ChromaDB（コレクション: travel_knowledge）に保存
        ↓
8. chunks.chroma_id を更新 / document.status を vectorized に更新
        ↓（例外発生時）
   document.status を failed に更新
```

---

## チャンキング設計

RAG スキルのガイドに従い **セマンティックチャンキング** を採用。
各 travel_extraction が意味的に独立した単位（destination / budget / schedule など）のため、**1抽出 = 1チャンク** とする。

| 方針 | 理由 |
|---|---|
| 1抽出 = 1チャンク | 各 extraction は意味的に独立している |
| カテゴリをメタデータに付与 | 類似度検索時にカテゴリフィルタが可能 |
| セッションIDをメタデータに付与 | どの会話由来かをトレース可能 |

---

## ChromaDB 設計

| 項目 | 値 |
|---|---|
| コレクション名 | `travel_knowledge` |
| embedding モデル | `nomic-embed-text`（Ollama） |
| ID | `uuid4`（`chunks.chroma_id` と一致） |

**メタデータ構造:**

```json
{
  "document_id": "uuid",
  "session_id": "uuid",
  "category": "destination",
  "source": "chat"
}
```

---

## テキスト変換テンプレート

| category | 変換例 |
|---|---|
| `destination` | `旅行先: 京都（city）、日本` |
| `accommodation` | `宿泊施設: リッツカールトン（hotel）、京都` |
| `transportation` | `交通手段: 新幹線、東京から京都` |
| `food` | `グルメ: 湯豆腐（料理）、京都` |
| `experience` | `体験: 着物レンタル（activity）、祇園` |
| `schedule` | `日程: 2026-05-01から3日間` |
| `budget` | `予算: 80000 JPY（total）` |
| `tip` | `旅行のコツ: 混雑を避けるなら朝一番（嵐山）` |
| その他 | `{category}: {JSON文字列}` |

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | 未変換データあり | 200・processed > 0 |
| 2 | 正常系 | 全セッション変換済み | 200・processed=0, skipped>0 |
| 3 | 正常系 | 対象データなし | 200・全て0 |
| 4 | 正常系 | レスポンスに必須フィールドが含まれる | processed/skipped/failed/total_chunks |
| 5 | 異常系 | vectorize_chat_data が例外 | 500 |
| 6 | 異常系 | 未認証 | 401 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-28 | 1.1.0 | JWT Cookie 認証を必須化 |
| 2026-04-23 | 1.0.0 | 初版作成 |
