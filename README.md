# PosterMovieMaker

画像から動画への変換とGCSアップロード

このプロジェクトは、指定されたJSONから画像URLを読み取り、それらの画像を1枚1秒の動画に変換した後、Google Cloud Storageにアップロードするものです。

## 前提条件

- Dockerがインストールされている
- Google Cloud Runでの利用を想定
- Cloud Storageへのアクセス権限がある credentials.json が存在する(ローカルでの実行時のみ)

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


## Credit

開発元　個人開発者集会運営・スタッフ

アセット作成・公開

- Azukimochi
JSONデータ作成

## 関連情報

- アセット [TaAGatheringListSystem](https://github.com/Azukimochi/TaAGatheringListSystem) by Azukimochi

- [JSONデータ](https://noricha-vr.github.io/toGithubPagesJson/sample.json) by のりちゃん(noricha-vr)

## ライセンス

MIT
