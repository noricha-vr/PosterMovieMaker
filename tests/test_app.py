import unittest
from unittest.mock import patch, Mock
from src.app import app, run_script  # your_flask_appは上記のFlaskコードが保存されているPythonファイル名に置き換えてください。

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    @patch('requests.get')
    def test_run_script_json_get(self, mock_get):
        # tests/test_data.json を読み込んでtextに設定
        with open('tests/test_data.json', 'r') as f:
            test_data = f.read()
        mock_get.return_value = Mock(status_code=200, text=test_data)
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            mock_get.assert_called_with('https://noricha-vr.github.io/toGithubPagesJson/sample.json')

    @patch('subprocess.run')
    def test_run_script_wget(self, mock_run):
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            mock_run.assert_any_call("wget https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png?ex=6515e050&is=65148ed0&hm=d38605afe58edb724807225da74bb8dbeaed0f9f7b7d11aebbc9ec2fad111fb9 -O 000.png", shell=True)

    @patch('subprocess.call')
    def test_run_script_ffmpeg(self, mock_call):
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            mock_call.assert_called()

    @patch('google.cloud.storage.Client')
    def test_run_script_gcs_upload(self, mock_client):
        mock_instance = mock_client.return_value
        mock_bucket = Mock()
        mock_instance.bucket.return_value = mock_bucket
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob

        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            mock_blob.upload_from_filename.assert_called_with('output.mp4')
