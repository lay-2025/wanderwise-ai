# ER図

> 対象DB: PostgreSQL 15 / `travel_db`
> 最終更新: 2026-04-22

---

```mermaid
erDiagram
    sessions {
        uuid id PK
        varchar title
        timestamp created_at
        timestamp updated_at
    }

    messages {
        uuid id PK
        uuid session_id FK
        varchar role
        text content
        timestamp created_at
    }

    travel_extractions {
        uuid id PK
        uuid message_id FK
        uuid session_id FK
        varchar category
        jsonb data
        float confidence
        timestamp created_at
    }

    documents {
        uuid id PK
        varchar title
        text content
        varchar source
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    chunks {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        varchar chroma_id
        timestamp created_at
    }

    sessions ||--o{ messages : "1対多"
    sessions ||--o{ travel_extractions : "1対多"
    messages ||--o{ travel_extractions : "1対多"
    documents ||--o{ chunks : "1対多"
```

---

## ストレージ役割分担

| DB | 保存するもの |
|---|---|
| **PostgreSQL** | セッション・メッセージ・抽出旅行データ・ドキュメントメタデータ・チャンクメタデータ |
| **ChromaDB** | テキストのベクトル（embedding）・チャンク本文・検索フィルタ用メタデータ |

`chunks.chroma_id` で PostgreSQL ↔ ChromaDB を紐づける。
