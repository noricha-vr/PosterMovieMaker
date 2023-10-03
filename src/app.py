from flask import Flask
import json
import requests
from utils import image_to_movie, MovieConfig, download_images, upload_blob
import logging
import sys
from settings import GCS_FILE_PATH, JSON_RUL

from utils import process_images, to_image_urls
fm = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(fm)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


app = Flask(__name__)


@app.route('/')
def run_script():
    try:
        # JSONを取得
        response = requests.get(JSON_RUL)
        data = json.loads(response.text)
        # 画像をダウンロード・加工
        image_urls = to_image_urls(data)
        image_paths = download_images(image_urls)
        logging.info(image_urls)
        image_paths = process_images(image_paths)
        logging.info(image_paths)
        # 動画作成
        movie_config = MovieConfig(
            encode_speed="veryslow", output_movie_path="movie/poster.mp4")
        image_to_movie(movie_config, image_paths)
        # 動画をGCSにアップロード
        upload_blob(movie_config.output_movie_path, GCS_FILE_PATH)
        return "Process completed"
    except Exception as e:
        logger.error(e)
        return "Process failed"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
