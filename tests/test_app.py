import unittest
from unittest.mock import patch, MagicMock
from src.utils import download_images, image_to_movie, upload_blob, MovieConfig  

class TestUtils(unittest.TestCase):
    
    @patch("subprocess.run")
    def test_download_images(self, mock_subprocess_run):
        data = [
            {"ポスター": "https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png"},
            {"ポスター": "https://cdn.discordapp.com/attachments/1136630413054464070/1147808687201734736/3.png?ex=6515e064&is=65148ee4&hm=41f9e78af5f07d90fe5b5b8caebf28483c54e0dbfa521c21b50e4431b0f00dd3&"}
        ]
        result = download_images(data)
        self.assertEqual(result, "img/001.png")
        self.assertEqual(mock_subprocess_run.call_count, 2)
    
    @patch("subprocess.call")
    def test_image_to_movie(self, mock_subprocess_call):
        movie_config = MovieConfig(frame_rate=2, width=640, encode_speed="fast", output_movie_path="output.mp4")
        image_paths = ["img/000.png", "img/001.png"]
        image_to_movie(movie_config, image_paths)
        mock_subprocess_call.assert_called_once_with([
                    'ffmpeg', '-framerate', '2', '-pattern_type', 'glob', '-i', 'img/*.png',
                    '-vf', "scale='min(640,iw)':-2", '-c:v', 'h264', '-pix_fmt', 'yuv420p',
                    '-preset', 'fast', '-tune', 'stillimage', '-y', 'output.mp4'
                ])
        
        with self.assertRaises(Exception) as context:
            image_to_movie(movie_config, [])
        self.assertEqual(str(context.exception), "No image files.")
    
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
