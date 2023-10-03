import glob
import shutil
import subprocess
from threading import Thread
from typing import List
from google.cloud import storage
import requests
import os
import logging
import sys
from PIL import Image

from settings import BUKECT_NAME, DEFAULT_IMAGE_URL
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def upload_blob(source_file_name: str, gcs_file_path: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUKECT_NAME)
    blob = bucket.blob(gcs_file_path)
    blob.upload_from_filename(source_file_name)


class MovieConfig:
    def __init__(self, encode_speed: str, output_movie_path: str, image_type='png', frame_rate=6, width=720):
        self.frame_rate = frame_rate
        self.width = width
        self.encode_speed = encode_speed
        self.output_movie_path = output_movie_path
        self.image_type = image_type


def to_image_urls(data: dict) -> list:
    images = []
    for i, item in enumerate(data):
        poster_url = item.get("ポスター", '')
        if poster_url == '':
            images.append(DEFAULT_IMAGE_URL)
        else:
            images.append(poster_url)
    return images


def download_images(image_urls: list[str]) -> list:
    # imgフォルダがない場合、作成する
    if not os.path.exists("img"):
        os.makedirs("img")
    else:
        # すでにimgフォルダがある場合、中身を削除する
        for f in glob.glob("img/*"):
            os.remove(f)
    file_names = []
    for i, image_url in enumerate(image_urls):
        image_file_name = f"img/{i:03d}.png"
        # requestsを使用して画像をダウンロード
        try:
            response = requests.get(image_url, timeout=3)
            response.raise_for_status()  # エラーレスポンスを確認し、エラーの場合は例外を発生させる
            with open(image_file_name, 'wb') as f:
                f.write(response.content)
            file_names.append(image_file_name)
        except requests.RequestException as e:
            print(f"画像のダウンロードに失敗しました: {e}")
    return file_names


def process_images(image_paths: List[str]) -> List[str]:
    for i, path in enumerate(image_paths):
        # 画像をロード
        image = Image.open(path)

        # 画像を左に90度回転
        rotated_image = image.rotate(90, expand=1)

        # アスペクト比を維持しながらリサイズ
        target_size = (1280, 720)
        rotated_image.thumbnail(target_size)

        # 背景を黒で作成
        background = Image.new('RGBA', target_size, (0, 0, 0, 255))

        # リサイズした画像を背景の中央に配置
        bg_w, bg_h = background.size
        img_w, img_h = rotated_image.size
        offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)

        # アルファチャンネルの有無を確認
        if rotated_image.mode == 'RGBA':
            mask = rotated_image.split()[3]
        else:
            mask = None

        # ペースト
        background.paste(rotated_image, offset, mask=mask)

        # 最終的な画像で上書き保存
        background.save(path)
    return image_paths


def copy_images_for_frame_rate(image_paths: List[str], frame_rate) -> None:
    """
    Copy files to create images for frame rate.
    :param image_paths:
    :param frame_rate:
    :return:
    """
    # copy images framerate times -1
    threads = []
    for i in range(1, frame_rate):
        for image_path in image_paths:
            # copy image. ex) image.png -> image_01.png
            new_image_path = image_path.replace(
                f'.{image_path.split(".")[-1]}',
                f'_{i:02d}.{image_path.split(".")[-1]}')

            t = Thread(target=shutil.copy,
                       args=(
                           image_path,
                           new_image_path))
            t.start()
            threads.append(t)
    [thread.join() for thread in threads]


def image_to_movie(movie_config: MovieConfig, image_paths: List[str]) -> None:
    """
    Create image_dir files to movie.
    :param movie_config:
    :return None:
    """
    # create movie dir
    if not os.path.exists("movie"):
        os.makedirs("movie")
    if len(image_paths) == 0:
        raise Exception("No image files.")
    img_dir = 'img/*.' + movie_config.image_type
    logging.info(f'img_dir: {img_dir}')
    copy_images_for_frame_rate(image_paths, movie_config.frame_rate)
    commands = ['ffmpeg',
                '-framerate', f'{movie_config.frame_rate}',
                # Select image_dir/*.file_type
                '-pattern_type', 'glob', '-i', img_dir,
                # iw is input width, -2 is auto height
                '-vf', f"scale='min({movie_config.width},iw)':-2",
                '-c:v', 'h264',  # codec
                '-pix_fmt', 'yuv420p',
                '-profile:v', 'baseline',  # Baseline Profile を使う
                '-bf', '0',  # Bidirectional Predictive Frame を使わない
                '-preset', movie_config.encode_speed,
                '-tune', 'stillimage',  # tune for still image
                '-y',  # overwrite output file
                f'{movie_config.output_movie_path}']
    logging.info(f'commands: {commands}')
    try:
        subprocess.run(commands, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr
        logging.error(f'Error: {error_message}')
