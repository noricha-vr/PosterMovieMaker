import json
import shutil
import unittest
from unittest.mock import patch
from utils import download_images, image_to_movie, to_image_urls, upload_blob, MovieConfig,bucket_name,destination_blob_name
from moviepy.editor import VideoFileClip
import os
import logging
import sys
from google.cloud import storage
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class TestUtils(unittest.TestCase):

    def setUp(self) -> None:
        with open("tests/test_data.json", "r") as f:
            self.data = json.load(f)
        self.image_urls = to_image_urls(self.data)
        self.image_paths = download_images(self.image_urls)
        logging.debug(self.image_urls)
        logging.debug(self.image_paths)
        # 動画作成
        movie_config = MovieConfig(frame_rate=2, width=640, encode_speed="fast", output_movie_path="movie/output.mp4")
        image_to_movie(movie_config, self.image_paths)
        self.assertTrue(os.path.exists(movie_config.output_movie_path), "動画ファイルが存在しません")

    # def tearDown(self) -> None:
    #     if os.path.exists("img"):
    #         shutil.rmtree("img")
    #     output_movie_path = "movie/output.mp4"
    #     if os.path.exists(output_movie_path):
    #         os.remove(output_movie_path)

    def test_to_image_url(self):
        self.assertEqual(self.image_urls, 
            ['https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png',
            'https://cdn.discordapp.com/attachments/1111955559562870875/1153912198700224532/Poster20230919_002.png',
            'https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png'] , 
            "画像のURLが一致しません")

    def test_download_images(self):
        self.assertEqual(len(self.image_paths), len(self.data), "画像の枚数が一致しません")

    @patch("subprocess.call")
    def test_image_to_movie_creation_and_duration(self, mock_subprocess_call):
        movie_config = MovieConfig(frame_rate=2, width=640, encode_speed="fast", output_movie_path="movie/output.mp4")
        image_to_movie(movie_config, self.image_paths)
        self.assertTrue(os.path.exists(movie_config.output_movie_path), "動画ファイルが存在しません")
        with VideoFileClip(movie_config.output_movie_path) as clip:
            expected_duration = len(self.image_paths) / movie_config.frame_rate
            self.assertEqual(clip.duration, expected_duration)

    
    def test_upload_movie(self):
        upload_blob(bucket_name, "movie/output.mp4", destination_blob_name)
        # アップロードされた動画の存在を確認
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        self.assertTrue(blob.exists(), "アップロードされた動画が存在しません")
