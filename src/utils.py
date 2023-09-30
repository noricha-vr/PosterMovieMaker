import pathlib
import shutil
import subprocess
from threading import Thread
from typing import List
from google.cloud import storage
import time
import requests
import os
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

bucket_name = "TaAGatheringListSystem"
source_file_name = "movie/output.mp4"
destination_blob_name = "TaAGatheringList.mp4"
json_url = 'https://noricha-vr.github.io/toGithubPagesJson/sample.json'

class MovieConfig:
    def __init__(self, frame_rate, width, encode_speed, output_movie_path, image_type='png'):
        self.frame_rate = frame_rate
        self.width = width
        self.encode_speed = encode_speed
        self.output_movie_path = output_movie_path
        self.image_type = image_type

def to_image_urls(data:dict)->list:
    images = []
    default_image_url = "https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png"
    for i, item in enumerate(data):
        poster_url = item.get("ポスター", '')
        if poster_url == '':
            images.append(default_image_url)
        else:
            images.append(poster_url)
    return images
    

def download_images(image_urls:list[str])->list:
    # imgフォルダがない場合、作成する
    if not os.path.exists("img"):
        os.makedirs("img")
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


def image_to_movie(movie_config: MovieConfig,image_paths:List[str]) -> None:
    """
    Create image_dir files to movie.
    :param movie_config:
    :return None:
    """
    if len(image_paths) == 0:
        raise Exception("No image files.")
    img_dir = str(pathlib.Path(image_paths[0]).parent) + '/*.' + movie_config.image_type
    logger.info(f'img_dir: {img_dir}')
    commands = ['ffmpeg',
                    '-framerate', f'{movie_config.frame_rate}',
                    # Select image_dir/*.file_type
                    '-pattern_type', 'glob', '-i', img_dir,
                    '-vf', f"scale='min({movie_config.width},iw)':-2",  # iw is input width, -2 is auto height
                    '-c:v', 'h264',  # codec
                    '-pix_fmt', 'yuv420p',  # pixel format (color space)
                    '-preset', movie_config.encode_speed,
                    '-tune', 'stillimage',  # tune for still image
                    '-y',  # overwrite output file
                    f'{movie_config.output_movie_path}']
    logger.info(f'commands: {commands}')
    try:
        result = subprocess.run(commands, check=True, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr
        print(f'Error: {error_message}')
    

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
