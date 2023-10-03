import json
import shutil
import unittest
from unittest.mock import patch
from settings import BUKECT_NAME
from utils import download_images, image_to_movie, process_images, to_image_urls, upload_blob, MovieConfig
from moviepy.editor import VideoFileClip
import os
import logging
import sys
from PIL import Image
from google.cloud import storage
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# 環境変数の設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials.json"


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.assertTrue(os.path.exists(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]), "credentials.jsonが存在しません")
        with open("tests/test_data.json", "r") as f:
            self.data = json.load(f)
        self.image_urls = to_image_urls(self.data)
        self.image_paths = download_images(self.image_urls)
        self.image_paths = process_images(self.image_paths)
        logging.debug(self.image_urls)
        logging.debug(self.image_paths)
        # 動画作成
        self.movie_config = MovieConfig(
            encode_speed="fast", output_movie_path="movie/poster_test.mp4")
        image_to_movie(self.movie_config, self.image_paths)
        self.assertTrue(os.path.exists(
            self.movie_config.output_movie_path), "動画ファイルが存在しません")

    def tearDown(self) -> None:
        if os.path.exists("img"):
            shutil.rmtree("img")
        if os.path.exists(self.movie_config.output_movie_path):
            os.remove(self.movie_config.output_movie_path)

    def test_to_image_url(self):
        self.assertEqual(self.image_urls,
                         ['https://cdn.discordapp.com/attachments/1053199603035553822/1158768381449740338/black.png',
                          "https://cdn.discordapp.com/attachments/1136630413054464070/1147808687201734736/3.png",
                          "https://cdn.discordapp.com/attachments/1111955559562870875/1153912198700224532/Poster20230919_002.png",
                          "https://cdn.discordapp.com/attachments/1022831613186424880/1157205676523782204/271472907-a4b672da-1c66-4768-82e9-1468a9be8453.png"],
                         "画像のURLが一致しません")

    def test_download_images(self):
        self.assertEqual(len(self.image_paths), len(self.data), "画像の枚数が一致しません")

    def test_process_image(self):
        for png_path in self.image_paths:
            with Image.open(png_path) as img:
                self.assertEqual(img.format, "PNG",
                                 f"{png_path} は PNG 形式ではありません")
                self.assertEqual(img.size, (1280, 720),
                                 f"{png_path} は HD サイズではありません")

    @patch("subprocess.call")
    def test_image_to_movie_creation_and_duration(self, mock_subprocess_call):
        self.assertTrue(os.path.exists(
            self.movie_config.output_movie_path), "動画ファイルが存在しません")
        with VideoFileClip(self.movie_config.output_movie_path) as clip:
            expected_duration = len(self.data)
            self.assertEqual(clip.duration, expected_duration)

    def test_upload_movie(self):
        destination_blob_name = "poster_test.mp4"
        upload_blob(self.movie_config.output_movie_path, destination_blob_name)
        # アップロードされた動画の存在を確認
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUKECT_NAME)
        blob = bucket.blob(destination_blob_name)
        self.assertTrue(blob.exists(), "アップロードされた動画が存在しません")
