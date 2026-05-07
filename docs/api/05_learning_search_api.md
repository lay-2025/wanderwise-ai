# IF設計書 — GET /api/learning/search

> 作成日: 2026-04-23  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `GET /api/learning/search` |
| **機能** | クエリ文字列を nomic-embed-text でベクトル化し、ChromaDB で意味的に近いチャンクを検索して返す |
| **認証** | JWT Cookie 認証（必須） |
| **検索方式** | コサイン類似度（ChromaDB デフォルト） |

---

## リクエスト

### クエリパラメータ

| パラメータ | 型 | 必須 | デフォルト | 制約 | 説明 |
|---|---|---|---|---|---|
| `q` | string | ✅ | — | 1文字以上 | 検索クエリ |
| `n_results` | integer | — | `5` | 1〜20 | 返却件数 |
| `source` | string | — | — | `chat` / `upload` / `manual` | ソースでフィルタ |
| `category` | string | — | — | — | カテゴリでフィルタ |

### リクエスト例

```
GET /api/learning/search?q=京都のおすすめ観光地
GET /api/learning/search?q=混雑を避けるコツ&n_results=3
GET /api/learning/search?q=宿泊施設&category=accommodation
GET /api/learning/search?q=旅行先&source=chat&n_results=10
```

---

## レスポンス

### 200 OK

```json
{
  "query": "京都のおすすめ観光地",
  "results": [
    {
      "document_id": "7b66d212-76c2-4e24-b642-59efc69d9256",
      "document_title": "嵐山観光ガイド",
      "source": "upload",
      "chunk": "旅行先: 嵐山（place）",
      "score": 0.87
    }
  ],
  "total": 1
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `query` | string | リクエストで指定した検索クエリ |
| `results` | array | 類似度の高い順に並んだチャンク一覧 |
| `results[].document_id` | string \| null | 元ドキュメントID |
| `results[].document_title` | string \| null | ドキュメント名（upload/manual 由来時のみ） |
| `results[].source` | string \| null | データソース（`chat` / `upload` / `manual`） |
| `results[].chunk` | string | チャンク本文 |
| `results[].score` | float | 類似度スコア（0.0〜1.0、高いほど類似） |
| `total` | integer | 返却件数 |

### 200 OK（データなし）

ChromaDB にデータがない、またはコレクションが未作成の場合は空で返す。

```json
{ "query": "京都", "results": [], "total": 0 }
```

### 422 Unprocessable Entity

| 条件 | エラー内容 |
|---|---|
| `q` が未指定 | `Field required` |
| `n_results` が1未満または20超 | バリデーションエラー |

### 500 Internal Server Error

Ollama / ChromaDB 接続エラー時。

---

## 処理フロー

```
1. クエリパラメータのバリデーション
        ↓
2. nomic-embed-text でクエリをベクトル化
        ↓
3. ChromaDB でコサイン類似度検索
   - source / category フィルタを適用（指定時）
   - コレクションが存在しない場合は空を返す
        ↓
4. distance → score（1 - distance）に変換
        ↓
5. SearchResponse を返す
```

---

## score について

ChromaDB はコサイン距離（低いほど近い）を返すため、`score = 1 - distance` に変換して返す。

| score | 意味 |
|---|---|
| 1.0 | 完全一致 |
| 0.8〜1.0 | 高い類似度 |
| 0.5〜0.8 | 中程度 |
| 0.5未満 | 低い類似度 |

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | クエリを指定して検索 | 200・results が返る |
| 2 | 正常系 | データなし | 200・`results=[]`, `total=0` |
| 3 | 正常系 | レスポンスに必須フィールドが含まれる | query/results/total |
| 4 | 正常系 | results の各要素に必須フィールドが含まれる | document_id/chunk/score 等 |
| 5 | 正常系 | n_results が返却件数に反映される | — |
| 6 | 正常系 | source フィルタがサービスに渡される | — |
| 7 | 正常系 | category フィルタがサービスに渡される | — |
| 8 | 異常系 | `q` 未指定 | 422 |
| 9 | 異常系 | `n_results=0` | 422 |
| 10 | 異常系 | `n_results=21` | 422 |
| 11 | 異常系 | ChromaDB / Ollama エラー | 500 |
| 12 | 異常系 | 未認証 | 401 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-05-07 | 1.2.0 | レスポンスフィールド名を変更（content→chunk, similarity→score）。document_title を追加、chroma_id/category/session_id を削除 |
| 2026-04-28 | 1.1.0 | JWT Cookie 認証を必須化 |
| 2026-04-23 | 1.0.0 | 初版作成 |
