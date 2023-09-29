import unittest
from unittest.mock import patch, MagicMock
from utils import download_images, image_to_movie, upload_blob, MovieConfig  
from unittest.mock import patch
from moviepy.editor import VideoFileClip
import os

class TestUtils(unittest.TestCase):
    
    def test_download_images(self):
        data = [
            {"ポスター": "https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png"},
            {"ポスター": "https://cdn.discordapp.com/attachments/1136630413054464070/1147808687201734736/3.png?ex=6515e064&is=65148ee4&hm=41f9e78af5f07d90fe5b5b8caebf28483c54e0dbfa521c21b50e4431b0f00dd3&"}
        ]
        result = download_images(data)
        self.assertEqual(result, ['img/000.png', 'img/001.png'])
    

    @patch("subprocess.call")
    def test_image_to_movie_creation_and_duration(self, mock_subprocess_call):
        # MovieConfigオブジェクトの作成とimage_pathsの定義
        movie_config = MovieConfig(frame_rate=2, width=640, encode_speed="fast", output_movie_path="movie/output.mp4")
        image_paths = ["img/000.png", "img/001.png"]

        # image_to_movie関数の呼び出し
        image_to_movie(movie_config, image_paths)

        # 動画ファイルが存在することを確認
        self.assertTrue(os.path.exists(movie_config.output_movie_path), "動画ファイルが存在しません")

        # 動画の長さが、画像の枚数とフレームレートに基づいて正しいことを確認
        with VideoFileClip(movie_config.output_movie_path) as clip:
            expected_duration = len(image_paths) / movie_config.frame_rate
            self.assertEqual(clip.duration, expected_duration)

        # テスト後に動画ファイルを削除
        os.remove(movie_config.output_movie_path)
    
    @patch("google.cloud.storage.Client")
    def test_upload_blob(self, mock_storage_client):
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        upload_blob("my_bucket", "source_file.mp4", "destination_blob_name")
        
        mock_storage_client.return_value.bucket.assert_called_once_with("my_bucket")
        mock_bucket.blob.assert_called_once_with("destination_blob_name")
        mock_blob.upload_from_filename.assert_called_once_with("source_file.mp4")


if __name__ == '__main__':
    unittest.main()
