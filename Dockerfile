FROM python:3.8-slim

# OSのパッケージインストール
RUN apt-get update && \
    apt-get install -y ffmpeg wget git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# 必要なディレクトリの作成
RUN mkdir -p /app/img && mkdir -p /app/movie

# 作業ディレクトリの設定
WORKDIR /app/src

# 環境変数の設定
ENV PORT 8080
ENV PYTHONPATH /app/src

# アプリケーションのディレクトリをコピー
COPY . /app

# アプリケーションの起動
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
