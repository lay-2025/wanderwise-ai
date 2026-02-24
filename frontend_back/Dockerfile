# ベースイメージ
FROM node:20-alpine

# 作業ディレクトリの設定
WORKDIR /app

# npmパッケージのインストール
COPY package.json package-lock.json* ./
RUN npm install

# アプリケーションコードのコピー
COPY . .

# 開発用サーバー起動
CMD ["npm", "run", "dev"]
