# WanderWise AI — フロントエンド追加ファイル

> 生成日: 2026-05-01
> 対象プロジェクト: `lay-2025/wanderwise-ai`

---

## このフォルダの内容

設計資料（`IMPLEMENTATION_PLAN.md` / `STEP4_RAG_QUALITY_DESIGN.md`）をもとに追加・更新したファイル一覧です。

```
src/
├── types/
│   └── extraction.ts          ★ 新規 — 旅行抽出データの共通型定義
├── lib/
│   └── api.additions.ts       ★ 新規 — api.ts への追記分（末尾にマージ）
├── components/
│   ├── ExtractionBadge.tsx    ★ 新規 — メッセージ下の抽出バッジ（小）
│   ├── ExtractionPanel.tsx    ★ 新規 — 右サイドパネル（カテゴリ別詳細）
│   ├── RagCompareModal.tsx    ★ 新規 — RAGあり・なし比較モーダル
│   ├── SourceBadge.tsx        ★ 新規 — chat/upload/manual バッジ
│   └── DocToggle.tsx          ★ 新規 — RAG ON/OFF トグルスイッチ
└── app/(main)/
    ├── chat/[sessionId]/
    │   └── page.tsx           ★ 更新 — 抽出バッジ・パネル・RAG比較を追加
    └── learning/
        ├── layout.tsx         ★ 新規 — 学習管理ページレイアウト
        └── page.tsx           ★ 新規 — 学習管理ページ本体
```

---

## 導入手順

### 1. 型定義を追加

```bash
mkdir -p frontend/src/types
cp src/types/extraction.ts frontend/src/types/
```

### 2. api.ts に API 関数を追記

`api.additions.ts` の内容を `frontend/src/lib/api.ts` の末尾にコピーしてください。

> ⚠️ `import type { TravelExtraction }` の行は不要です（同ファイル内に型を移動するか、`@/types/extraction` からインポートしてください）。

あわせて、既存の `ChatResponse` の型を更新してください：

```ts
// 変更前
export interface ChatResponse {
  response: string
  session_id: string
  extractions: unknown[]  // ← これを変更
}

// 変更後
import type { TravelExtraction } from '@/types/extraction'

export interface ChatResponse {
  response: string
  session_id: string
  extractions: TravelExtraction[]  // ← 型を明示
}
```

### 3. コンポーネントをコピー

```bash
cp src/components/ExtractionBadge.tsx  frontend/src/components/
cp src/components/ExtractionPanel.tsx  frontend/src/components/
cp src/components/RagCompareModal.tsx  frontend/src/components/
cp src/components/SourceBadge.tsx      frontend/src/components/
cp src/components/DocToggle.tsx        frontend/src/components/
```

### 4. チャットページを差し替え

```bash
cp src/app/\(main\)/chat/\[sessionId\]/page.tsx \
   frontend/src/app/\(main\)/chat/\[sessionId\]/page.tsx
```

### 5. 学習管理ページを追加

```bash
mkdir -p frontend/src/app/\(main\)/learning
cp src/app/\(main\)/learning/layout.tsx \
   frontend/src/app/\(main\)/learning/
cp src/app/\(main\)/learning/page.tsx \
   frontend/src/app/\(main\)/learning/
```

### 6. ナビゲーションに「学習管理」を追加（既存 Header.tsx）

`frontend/src/components/Header.tsx` の `<Link href="/learning">` がすでに存在するため変更不要です。

---

## バックエンドとの対応関係

| フロントエンド | バックエンド API | 実装ステップ |
|---|---|---|
| `getExtractions(sessionId)` | `GET /api/data/travel?session_id=` | Step 1 |
| `getDocuments()` | `GET /api/documents` | Step 4 |
| `toggleDocument(id)` | `PATCH /api/documents/:id/toggle` | Step 4 |
| `uploadDocumentFromUrl(title, url)` | `POST /api/documents/upload` | Step 4 |
| `searchDocuments(query)` | `GET /api/learning/search?q=` | Step 2 |
| `compareRag(query, sessionId)` | `POST /api/chat` (compare_mode=true) | Step 4 |

---

## lucide-react アイコン追加

`chat/[sessionId]/page.tsx` で以下のアイコンを使用しています。
プロジェクトの `lucide-react` に含まれていない場合は追加してください：

```ts
import { Sparkles, Columns2 } from 'lucide-react'
```

---

## 注意事項

- `learning/layout.tsx` は `(main)/layout.tsx` と重複する場合があります。既存の `(main)/layout.tsx` で `AuthProvider` と `Header` が既にラップされている場合は `learning/layout.tsx` は不要です。
- ベクトル可視化（t-SNE）は現在モックデータです。`GET /api/learning/visualize` 実装後に `getVisualize()` に差し替えてください。
