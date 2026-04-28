# IF設計書 — GET /api/learning/visualize

> 作成日: 2026-04-24  
> ステータス: 実装済み

---

## 概要

| 項目 | 内容 |
|---|---|
| **エンドポイント** | `GET /api/learning/visualize` |
| **機能** | ChromaDB のベクトルデータ件数と PostgreSQL のドキュメントステータスを集計して返す |
| **認証** | JWT Cookie 認証（必須） |
| **用途** | 管理ダッシュボードでのベクトル化状況・データ分布の可視化 |

---

## リクエスト

クエリパラメータなし。

```
GET /api/learning/visualize
```

---

## レスポンス

### 200 OK

```json
{
  "total_chunks": 15,
  "by_category": {
    "destination": 5,
    "accommodation": 3,
    "food": 2,
    "transportation": 2,
    "experience": 1,
    "schedule": 1,
    "budget": 1,
    "tip": 0
  },
  "by_source": {
    "chat": 15,
    "upload": 0,
    "manual": 0
  },
  "documents": {
    "total": 3,
    "vectorized": 3,
    "processing": 0,
    "failed": 0,
    "pending": 0
  }
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `total_chunks` | integer | ChromaDB に保存されているチャンク総数 |
| `by_category` | object | カテゴリ別チャンク件数（ChromaDB メタデータ集計） |
| `by_source` | object | ソース別チャンク件数（ChromaDB メタデータ集計） |
| `documents` | object | PostgreSQL の documents テーブルのステータス別件数 |
| `documents.total` | integer | ドキュメント総数 |
| `documents.vectorized` | integer | ベクトル化済み件数 |
| `documents.processing` | integer | 処理中件数 |
| `documents.failed` | integer | 失敗件数 |
| `documents.pending` | integer | 未処理件数 |

### 200 OK（データなし）

ChromaDB にデータがない、またはコレクションが未作成の場合は件数 0 で返す。

```json
{
  "total_chunks": 0,
  "by_category": {},
  "by_source": {},
  "documents": {
    "total": 0,
    "vectorized": 0,
    "processing": 0,
    "failed": 0,
    "pending": 0
  }
}
```

### 500 Internal Server Error

ChromaDB / PostgreSQL 接続エラー時。

---

## 処理フロー

```
1. ChromaDB コレクション存在確認
   - 未作成の場合: total_chunks=0、by_category={}、by_source={} で返す
        ↓
2. ChromaDB から全チャンクのメタデータを取得
        ↓
3. メタデータを集計
   - category キーでグルーピング → by_category
   - source キーでグルーピング → by_source
        ↓
4. PostgreSQL の documents テーブルをステータス別に集計 → documents
        ↓
5. VisualizeResponse を返す
```

---

## テスト観点

| # | 区分 | テストケース | 期待結果 |
|---|---|---|---|
| 1 | 正常系 | リクエストで200が返る | 200 |
| 2 | 正常系 | レスポンスに必須フィールドが含まれる | total_chunks/by_category/by_source/documents |
| 3 | 正常系 | documents に必須フィールドが含まれる | total/vectorized/processing/failed/pending |
| 4 | 正常系 | ChromaDB データあり | total_chunks が件数を返す |
| 5 | 正常系 | by_category にカテゴリ別件数が含まれる | — |
| 6 | 正常系 | by_source にソース別件数が含まれる | — |
| 7 | 正常系 | ChromaDB データなし | total_chunks=0、by_category={}、by_source={} |
| 8 | 異常系 | サービスが例外を投げた場合 | 500 |
| 9 | 異常系 | 未認証 | 401 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-04-28 | 1.1.0 | JWT Cookie 認証を必須化 |
| 2026-04-24 | 1.0.0 | 初版作成 |
