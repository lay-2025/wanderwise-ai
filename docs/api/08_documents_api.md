# IF設計書 — /api/documents

> 作成日: 2026-05-07  
> ステータス: 実装済み

---

## 概要

RAG用ドキュメントの管理（一覧取得・URLからの取り込み・RAG ON/OFF切り替え・削除）を行うエンドポイント群。  
全ドキュメントは全ユーザーで共有される（`is_active` フラグで検索対象を制御）。

| エンドポイント | メソッド | 機能 |
|---|---|---|
| `/api/documents` | GET | ドキュメント一覧取得 |
| `/api/documents/upload` | POST | URLからドキュメントを取り込み |
| `/api/documents/{document_id}/toggle` | PATCH | RAG ON/OFF 切り替え |
| `/api/documents/{document_id}` | DELETE | ドキュメント削除 |

**認証:** 全エンドポイントで JWT Cookie 認証が必須。

---

## GET /api/documents — ドキュメント一覧取得

### レスポンス 200 OK

```json
{
  "documents": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "title": "嵐山観光ガイド 2026",
      "source": "upload",
      "status": "vectorized",
      "is_active": true,
      "chunks": 42,
      "size": "129.3 KB",
      "url": "https://example.com/arashiyama",
      "created_at": "2026-05-07T10:00:00",
      "updated_at": "2026-05-07T10:01:30"
    }
  ],
  "total": 1
}
```

#### フィールド定義

| フィールド | 型 | 説明 |
|---|---|---|
| `documents` | array | ドキュメント一覧（登録日時の降順） |
| `documents[].id` | string (uuid) | ドキュメントID |
| `documents[].title` | string | ドキュメント名 |
| `documents[].source` | string | データ出所（`chat` / `upload` / `manual`） |
| `documents[].status` | string | ベクトル化状態（後述） |
| `documents[].is_active` | boolean | RAG検索対象か |
| `documents[].chunks` | integer \| null | チャンク数（ベクトル化前は null） |
| `documents[].size` | string \| null | 本文サイズ（`"129.3 KB"` など） |
| `documents[].url` | string \| null | 取り込み元URL（upload 時のみ） |
| `documents[].created_at` | string (datetime) | 登録日時 |
| `documents[].updated_at` | string (datetime) | 最終更新日時 |
| `total` | integer | 総件数 |

#### status の値

| 値 | 説明 |
|---|---|
| `pending` | 未処理 |
| `processing` | ベクトル化中 |
| `vectorized` | 完了（RAG検索可能） |
| `failed` | 失敗 |

---

## POST /api/documents/upload — URLからドキュメントを取り込み

URLのHTMLを取得・解析してドキュメントとして登録し、バックグラウンドでChromaDBにベクトル化する。

### リクエストボディ

```json
{
  "title": "嵐山観光ガイド 2026",
  "url": "https://example.com/arashiyama"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `title` | string | ✅ | ドキュメント名 |
| `url` | string | ✅ | 取り込み対象URL |

### 処理フロー

```
1. httpx で URL に GET リクエスト（タイムアウト30秒）
        ↓
2. BeautifulSoup4 で HTML 解析
   - script / style / nav / footer / header / aside / noscript を除去
   - テキスト行を抽出・空行除去
        ↓
3. documents テーブルに登録（status=processing）
        ↓
4. レスポンス返却（status=200）
        ↓（バックグラウンド）
5. 500文字チャンクに分割（オーバーラップ50文字）
6. chunks テーブルに保存
7. nomic-embed-text でベクトル化
8. ChromaDB（travel_knowledge コレクション）に保存
9. status を vectorized に更新
```

### レスポンス 200 OK

登録直後のドキュメント（`status=processing`）を返す。ベクトル化はバックグラウンドで完了する。

```json
{
  "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "title": "嵐山観光ガイド 2026",
  "source": "upload",
  "status": "processing",
  "is_active": true,
  "chunks": null,
  "size": "129.3 KB",
  "url": "https://example.com/arashiyama",
  "created_at": "2026-05-07T10:00:00",
  "updated_at": "2026-05-07T10:00:00"
}
```

### エラーレスポンス

| ステータス | 条件 | detail |
|---|---|---|
| 422 | URL への HTTP リクエスト失敗 | `"URLの取得に失敗しました: {status_code}"` |
| 422 | ネットワークエラー・タイムアウト | `"URLの取得に失敗しました: {message}"` |
| 422 | HTML からテキスト抽出不可（空） | `"URLからテキストを抽出できませんでした"` |
| 401 | 未認証 | — |

> **注意:** X（Twitter）等のJavaScriptレンダリングSPAはテキスト抽出不可（422）。静的HTMLページのみ対応。

---

## PATCH /api/documents/{document_id}/toggle — RAG ON/OFF 切り替え

`is_active` を反転する（ON→OFF または OFF→ON）。

### パスパラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `document_id` | uuid | 対象ドキュメントID |

### レスポンス 200 OK

```json
{
  "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "title": "嵐山観光ガイド 2026",
  "source": "upload",
  "status": "vectorized",
  "is_active": false,
  "chunks": 42,
  "size": "129.3 KB",
  "url": "https://example.com/arashiyama",
  "created_at": "2026-05-07T10:00:00",
  "updated_at": "2026-05-07T10:02:00"
}
```

### エラーレスポンス

| ステータス | 条件 | detail |
|---|---|---|
| 404 | document_id が存在しない | `"ドキュメントが見つかりません"` |
| 401 | 未認証 | — |

---

## DELETE /api/documents/{document_id} — ドキュメント削除

ドキュメントとそれに紐づくチャンクをDBから削除する。  
ChromaDB のベクトルデータは削除されない（孤立ベクトルとして残留）。

### パスパラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `document_id` | uuid | 対象ドキュメントID |

### レスポンス 204 No Content

ボディなし。

### エラーレスポンス

| ステータス | 条件 | detail |
|---|---|---|
| 404 | document_id が存在しない | `"ドキュメントが見つかりません"` |
| 401 | 未認証 | — |

---

## ChromaDB への保存仕様

コレクション名: `travel_knowledge`（チャット由来ドキュメントと共有）

| メタデータフィールド | 値 |
|---|---|
| `document_id` | `documents.id` の文字列 |
| `document_title` | `documents.title` |
| `source` | `"upload"` |

---

## テスト観点

| # | 区分 | エンドポイント | テストケース | 期待結果 |
|---|---|---|---|---|
| 1 | 正常系 | GET | ドキュメント一覧取得 | 200・documents/total を返す |
| 2 | 正常系 | GET | 0件の場合 | 200・空リスト |
| 3 | 正常系 | POST | URL取り込み成功 | 200・status=processing |
| 4 | 正常系 | POST | DBにドキュメントが追加される | db.add が呼ばれる |
| 5 | 異常系 | POST | URLへのHTTPエラー | 422 |
| 6 | 異常系 | POST | ネットワークエラー | 422 |
| 7 | 異常系 | POST | 空コンテンツ | 422 |
| 8 | 異常系 | POST | title 未指定 | 422 |
| 9 | 異常系 | POST | url 未指定 | 422 |
| 10 | 正常系 | PATCH | is_active が反転する | 200・is_active 反転 |
| 11 | 異常系 | PATCH | 存在しない ID | 404 |
| 12 | 正常系 | DELETE | 削除成功 | 204 |
| 13 | 異常系 | DELETE | 存在しない ID | 404 |

---

## 変更履歴

| 日付 | バージョン | 変更内容 |
|---|---|---|
| 2026-05-07 | 1.0.0 | 初版作成 |
