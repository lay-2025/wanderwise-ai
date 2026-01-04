# WanderWise AI

Python習得とポートフォリオ作成を目的とした、旅行関連のAIチャットボットプロジェクト

## 🎯 プロジェクト概要

**WanderWise AI** は、ユーザーのチャットを通じて旅行データを収集し、LLMの学習過程を可視化するインタラクティブな学習プラットフォームです。

### メイン機能
1. **🤖 チャットを通じた旅行データ収集**
   - ユーザーが旅行について質問・会話することで、自然な形で旅行データを収集
   - 会話履歴から有用な旅行情報を自動抽出・構造化

2. **📊 LLM学習可視化機能**
   - ベクトル化プロセスをリアルタイムで可視化
   - 学習データの管理・検索結果の確認
   - RAG（検索拡張生成）の動作を視覚的に理解

### 主な特徴
- 💬 インタラクティブなチャットインターフェース
- 📈 リアルタイム学習過程可視化
- 🔍 RAG（Retrieval-Augmented Generation）実装
- 🐳 Dockerコンテナ化による開発環境統一
- 🔧 FastAPI + React のモダンアーキテクチャ

## 🏗️ アーキテクチャ構成

### バックエンド (Python)
- **フレームワーク**: FastAPI
- **LLM統合**: OpenAI API (GPT-4/3.5-turbo)
- **データベース**: PostgreSQL + ChromaDB (ベクトルデータベース)
- **RAG実装**: LangChainを使用
- **主なAPIエンドポイント**:
  - `POST /chat` - チャットメッセージ送受信とデータ収集
  - `GET /chat/history` - 会話履歴の取得
  - `POST /learning/upload` - 学習データのアップロード
  - `GET /learning/status/{task_id}` - ベクトル化処理の進捗確認
  - `GET /learning/search` - 学習データ検索
  - `GET /learning/visualize` - ベクトルデータ可視化

### フロントエンド
- **フレームワーク**: React + TypeScript
- **UIライブラリ**: Material-UI
- **チャットインターフェース**: リアルタイムチャットUI
- **状態管理**: React Hooks

### Docker構成
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=travel_db
      - POSTGRES_USER=travel_user
      - POSTGRES_PASSWORD=travel_pass
  chromadb:
    image: chromadb/chroma:latest
    ports: ["8001:8000"]
```

## 🛠️ 技術スタック

### バックエンド
- **Python 3.11**
- **FastAPI**: 高性能Webフレームワーク
- **OpenAI**: LLM APIクライアント
- **LangChain**: RAG実装フレームワーク
- **ChromaDB**: ベクトルデータベース
- **SQLAlchemy**: ORM
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGIサーバー

### フロントエンド
- **Node.js 18**
- **React 18**: UIフレームワーク
- **TypeScript**: 型安全な開発
- **Axios**: HTTPクライアント
- **Material-UI**: UIコンポーネントライブラリ

### 開発・運用環境
- **Docker & Docker Compose**: コンテナ化
- **PostgreSQL**: リレーショナルデータベース
- **Nginx**: リバースプロキシ
- **Git**: バージョン管理

## 🧠 メイン機能の実装

### 1. チャットを通じた旅行データ収集
ユーザーの会話から旅行関連データを自動収集・学習する仕組み：

1. **会話監視**: チャット中のメッセージをリアルタイムで解析
2. **情報抽出**: 旅行関連キーワード（場所、施設、体験など）を自動抽出
3. **データ構造化**: 抽出した情報を構造化データとして保存
4. **継続学習**: 新しい会話データでLLMの知識を継続的に更新

### 2. LLM学習可視化機能
ベクトル化と学習過程を視覚的に確認できるダッシュボード：

1. **データ収集**: 旅行ガイド、観光情報、会話履歴などを収集
2. **ドキュメント分割**: 長いテキストを適切なサイズのチャンクに分割
3. **ベクトル化**: OpenAI embeddings APIでテキストをベクトル変換
4. **ベクトル保存**: ChromaDBにベクトルデータを保存
5. **類似度検索**: ユーザークエリと類似するドキュメントを検索
6. **回答生成**: 検索結果をコンテキストとしてLLMに渡して回答生成

### 実装フロー
```
ユーザーチャット → データ抽出・構造化 → ベクトル化 → 可視化ダッシュボード表示
                      ↓
               LLM学習 → 検索・回答生成 → チャット応答
```

## 📋 開発フェーズ

### Phase 1: 基礎構築とチャット機能 (2-3日)
- [ ] Docker環境構築
- [ ] FastAPIバックエンドの基本API作成
- [ ] PostgreSQLデータベース設定
- [ ] 基本的なチャットUI実装
- [ ] OpenAI API連携

### Phase 2: データ収集機能 (2-3日)
- [ ] チャットからのデータ抽出機能
- [ ] 会話履歴の保存・管理
- [ ] 旅行情報のパース・構造化
- [ ] データ収集APIの実装

### Phase 3: 学習可視化機能 (3-4日)
- [ ] ベクトル化パイプライン構築
- [ ] ChromaDB統合
- [ ] 学習進捗可視化ダッシュボード
- [ ] ベクトル検索結果の表示

### Phase 4: RAG統合 (2-3日)
- [ ] 検索拡張生成の実装
- [ ] 学習データとチャット応答の連携
- [ ] 回答品質の最適化

### Phase 5: UI/UX改善と最適化 (2-3日)
- [ ] レスポンシブデザインの改善
- [ ] リアルタイム処理の最適化
- [ ] エラーハンドリング強化
- [ ] パフォーマンス最適化

## 🚀 クイックスタート

### 環境準備
```bash
# Python 3.11以上
python --version

# Node.js 18以上
node --version

# Docker Desktop
docker --version

# OpenAI APIキー取得
# https://platform.openai.com/api-keys
```

### プロジェクトセットアップ
```bash
# リポジトリクローン（または新規作成）
cd Python_Travel

# 環境変数設定
cp .env.example .env
# .envファイルにOPENAI_API_KEYを設定

# Dockerコンテナ起動
docker-compose up -d

# バックエンド依存関係インストール
cd backend
pip install -r requirements.txt

# フロントエンド依存関係インストール
cd ../frontend
npm install
```

### 開発サーバー起動
```bash
# バックエンド（別ターミナル）
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド（別ターミナル）
cd frontend
npm start
```

## 📁 プロジェクト構造

```
wanderwise-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # チャットAPI
│   │   │   └── documents.py     # ドキュメント管理API
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        # 設定管理
│   │   │   └── database.py      # DB接続
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py   # LLM連携サービス
│   │   │   └── rag_service.py   # RAGサービス
│   │   └── main.py              # FastAPIアプリ
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── Message.tsx
│   │   │   ├── LearningDashboard.tsx    # 学習可視化ダッシュボード
│   │   │   ├── DataCollectionPanel.tsx  # データ収集パネル
│   │   │   └── VectorVisualization.tsx  # ベクトル可視化
│   │   ├── pages/
│   │   │   ├── ChatPage.tsx            # チャットページ
│   │   │   └── LearningPage.tsx        # 学習管理ページ
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore
```

## 🎓 学習ポイント

このプロジェクトを通じて習得できるスキル：

### Python開発スキル
- FastAPIを使用したRESTful API開発
- 非同期プログラミング (async/await)
- 型ヒントを使用した堅牢なコード
- 環境変数と設定管理

### LLM/機械学習スキル
- OpenAI APIの効果的な活用
- プロンプトエンジニアリング
- RAG（検索拡張生成）の実装と可視化
- ベクトルデータベースの操作
- 自然言語処理によるデータ抽出

### システム設計スキル
- マイクロサービスアーキテクチャ
- API設計原則
- データベース設計
- エラーハンドリング

### DevOpsスキル
- Dockerコンテナ化
- マルチコンテナオーケストレーション
- 環境分離
- 開発・本番環境の管理

### フロントエンドスキル
- React Hooksを使用したモダン開発
- TypeScriptによる型安全
- RESTful APIとの連携
- UI/UX設計

## 🔗 関連リソース

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [OpenAI APIドキュメント](https://platform.openai.com/docs)
- [LangChainドキュメント](https://python.langchain.com/)
- [ChromaDBドキュメント](https://docs.trychroma.com/)
- [React公式ドキュメント](https://react.dev/)

## 📝 ライセンス

このプロジェクトは学習目的で作成されており、MITライセンスの下で公開されています。

---

**Happy Coding! 🚀**
