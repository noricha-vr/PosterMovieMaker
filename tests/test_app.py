import json
import shutil
import unittest
from unittest.mock import patch
from utils import download_images, image_to_movie, process_images, to_image_urls, to_png, upload_blob, MovieConfig, bucket_name
from moviepy.editor import VideoFileClip
import os
import logging
import sys
from PIL import Image
from google.cloud import storage
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        with open("tests/test_data.json", "r") as f:
            self.data = json.load(f)
        self.image_urls = to_image_urls(self.data)
        self.image_paths = download_images(self.image_urls)
        self.image_paths = process_images(self.image_paths)
        logging.debug(self.image_urls)
        logging.debug(self.image_paths)
        # 動画作成
        self.movie_config = MovieConfig(
            width=640, encode_speed="fast", output_movie_path="movie/poster_test.mp4")
        image_to_movie(self.movie_config, self.image_paths)
        self.assertTrue(os.path.exists(
            self.movie_config.output_movie_path), "動画ファイルが存在しません")

    # def tearDown(self) -> None:
    #     if os.path.exists("img"):
    #         shutil.rmtree("img")
    #     if os.path.exists(self.movie_config.output_movie_path):
    #         os.remove(self.movie_config.output_movie_path)

    def test_to_image_url(self):
        self.assertEqual(self.image_urls,
                         ['https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png',
                          "https://cdn.discordapp.com/attachments/1136630413054464070/1147808687201734736/3.png",
                          "https://cdn.discordapp.com/attachments/1111955559562870875/1153912198700224532/Poster20230919_002.png"],
                         "画像のURLが一致しません")

    def test_download_images(self):
        self.assertEqual(len(self.image_paths), len(self.data), "画像の枚数が一致しません")

    def test_process_image(self):
        png_paths = to_png(self.image_paths)
        for png_path in png_paths:
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
        upload_blob(bucket_name, self.movie_config.output_movie_path,
                    destination_blob_name)
        # アップロードされた動画の存在を確認
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        self.assertTrue(blob.exists(), "アップロードされた動画が存在しません")
