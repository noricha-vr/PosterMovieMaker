# PosterMovieMaker

画像から動画への変換とGCSアップロード

このプロジェクトは、指定されたJSONから画像URLを読み取り、それらの画像を1枚1秒の動画に変換した後、Google Cloud Storageにアップロードするものです。

## 前提条件

- Dockerがインストールされている
- Google Cloud SDKがインストールされている
- GCPの認証情報が設定されている

## セットアップ

1. このリポジトリをクローン

    ```bash
    git clone git@github.com:noricha-vr/PosterMovieMaker.git
    ```

2. ディレクトリに移動

    ```bash
    cd PosterMovieMaker
    ```

3. Dockerイメージをビルド

    ```bash
    docker build -t poster-movie-maker .
    ```

4. Dockerコンテナを実行

    ```bash
    docker run -p 8080:8080 poster-movie-maker
    ```

5. ブラウザまたは`curl`で`http://localhost:8080/`にアクセス

## 使用技術

- Python 3.8
- FFmpeg
- Gunicorn
- Flask
- Google Cloud Storage

## 貢献

プルリクエストは歓迎です。

## ライセンス

MIT
