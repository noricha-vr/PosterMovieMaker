import subprocess
from google.cloud import storage
import time
class MovieConfig:
    def __init__(self, frame_rate, width, encode_speed, output_movie_path, image_type='png'):
        self.frame_rate = frame_rate
        self.width = width
        self.encode_speed = encode_speed
        self.output_movie_path = output_movie_path
        self.image_type = image_type

class MovieMaker:

    def download_images(data)->list:
        # ダウンロードした画像ファイルのパスを返す
        images = []
        default_image_url = "https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png"
        for i, item in enumerate(data):
            poster_url = item.get("ポスター", default_image_url)
            image_file_name = f"img/{i:03d}.png"
            subprocess.run(f"wget {poster_url} -O {image_file_name}", shell=True)
            images.append(image_file_name)
        return image_file_name
            
    def image_to_movie(movie_config: MovieConfig, image_paths: list):
        if len(image_paths) == 0:
            raise Exception("No image files.")
        
        start = time.time()
        subprocess.call(['ffmpeg',
                        '-framerate', f'{movie_config.frame_rate}',
                        '-pattern_type', 'glob', '-i', f'img/*.{movie_config.image_type}',
                        '-vf', f"scale='min({movie_config.width},iw)':-2",
                        '-c:v', 'h264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', movie_config.encode_speed,
                        '-tune', 'stillimage',
                        '-y',
                        f'{movie_config.output_movie_path}'])
        print(f"image_to_movie: {time.time() - start} sec")

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
