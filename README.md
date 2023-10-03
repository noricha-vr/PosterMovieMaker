# PosterMovieMaker

このプロジェクトは、指定されたJSONから画像URLを読み取り、それらの画像を1枚1秒の動画に変換した後、Google Cloud Storageにアップロードするものです。

## 前提条件

- Dockerがインストールされている
- Google Cloud Runでの利用を想定
- Cloud Storageへのアクセス権限がある`/credentials.json`が存在する(ローカルでの実行時のみ)

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
docker run -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json -p 8080:8080 poster-movie-maker
```

5. `http://localhost:8080/`にアクセス

6. クラウドストレージのバケットルートに`poster.mp4`が作成される

## オプション

settings.py から設定を変更できます。

JSON_URL: JSONのURL
JSON_IMAGE_KEY: JSONの画像URLのキー
BUKECT_NAME: GCSのバケット名
GCS_FILE_PATH: GCSにアップロードするファイルのパス
DEFAULT_IMAGE_URL： 画像が見つからなかった場合に表示する画像のURL

もしくは、コンテナ起動時に環境変数を設定することでも上記の設定を変更できます。

```
docker run \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json \
  -e JSON_URL=your_json_url \
  -e JSON_IMAGE_KEY=your_json_image_key \
  -e BUCKET_NAME=your_bucket_name \
  -e GCS_FILE_PATH=your_file_path \
  -e DEFAULT_IMAGE_URL=your_default_image_url \
  -p 8080:8080 \
  poster-movie-maker

```

## Credit

開発元　個人開発者集会運営・スタッフ 

- のりちゃん(noricha-vr)

- アセット作成・公開 Azukimochi [TaAGatheringListSystem](https://github.com/Azukimochi/TaAGatheringListSystem) 

## 関連情報

- [JSONデータ](https://noricha-vr.github.io/toGithubPagesJson/sample.json) by のりちゃん(noricha-vr)

## ライセンス

MIT
