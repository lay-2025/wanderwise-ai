# 🐳 WanderWise AI 開発環境ガイド

このドキュメントでは、Dockerを使用したローカル開発環境の操作方法について説明します。

## 📍 アクセスURL
- **フロントエンド画面**: [http://localhost:3000](http://localhost:3000)
- **バックエンド API 仕様 (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ 基本的なDockerコマンド

開発を行う際には、ターミナルで対象のディレクトリ（`c:\Users\USER\Desktop\DockerProject\wanderwise-ai`）を開き、以下のコマンドを実行します。

### 1. アプリケーションの起動
```bash
docker-compose up -d
```
> 全てのコンテナ（フロントエンド、バックエンド、データベース）をバックグラウンドで起動します。開発を始めるときはこれを実行します。

### 2. コンテナの停止
```bash
docker-compose down
```
> 開発を終了するときに実行し、すべてのコンテナネットワークを停止します。

### 3. 起動ログの確認
```bash
# 全てのログを見る
docker-compose logs -f

# 特定のコンテナ（例: フロントエンドのみ）のログを見る
docker-compose logs -f frontend
```
> エラーが起きた時や、`console.log()` / `print()` の出力内容を確認したい時に使用します（`Ctrl+C` で終了）。

### 4. パッケージの追加や設定変更をした場合
```bash
docker-compose build
# または
docker-compose up -d --build
```
> `npm install`でパッケージを追加した場合や、Pythonの`requirements.txt`を更新した場合など、コンテナの再構築が必要な時に実行します。

---

## 💻 開発における仕組みについて

現在のDocker環境は**「ホットリロード（自動反映）」**が有効になっています。

### フロントエンド（React / Next.js）
- 内部的に `npm run dev` で起動しています。
- コンテナと皆さんのPC（ホストOS）のフォルダは繋がっているため（Volumeマウント）、**お手元のPCでコードを保存すると、ブラウザが自動的にリロードされて即座に変更が反映されます。**
- コンテナに入って毎回ビルドを実行する必要はありません。

### バックエンド（Python / FastAPI）
- 内部的に `uvicorn app.main:app --reload` で起動しています。
- こちらも同様に、バックエンドのPythonコードを書き換えて保存すると、APIサーバーが自動的に再起動し、変更が即座に反映されます。

---

## ⚠️ プロダクション（本番）デプロイ時の注意

本プロジェクトには本番用の `docker-compose.prod.yml` も同封されています。
本番サーバー（AWSなど）に持ち込む際は、以下のコマンドで起動します。

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```
> ※ 本番用ではホットリロード機能が無効化され、静的にビルド・最適化された状態で起動します。
