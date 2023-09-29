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
    git clone https://github.com/your-username/your-repo.git
    ```

2. ディレクトリに移動

    ```bash
    cd your-repo
    ```

3. Dockerイメージをビルド

    ```bash
    docker build -t image-to-movie .
    ```

4. Dockerコンテナを実行

    ```bash
    docker run -p 8080:8080 image-to-movie
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

要約: Readmeはプロジェクトの概要、前提条件、セットアップ手順、使用技術、貢献方法、ライセンスについて説明しています。

信頼値: 90
