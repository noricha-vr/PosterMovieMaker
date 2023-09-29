FROM python:3.8-slim

# インストール
RUN apt-get update && \
    apt-get install -y ffmpeg wget && \
    pip install --no-cache-dir gunicorn Flask google-cloud-storage requests

# アプリケーションの準備
COPY . /app

# ディレクトリを作成
RUN mkdir -p /app/img && mkdir -p /app/movie

WORKDIR /app/src

# 環境変数
ENV PORT 8080

# Set python path
ENV PYTHONPATH /app/src

# スクリプトの実行
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
