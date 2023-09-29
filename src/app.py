from flask import Flask
import json
import requests
import subprocess
import time
from pathlib import Path
from google.cloud import storage

app = Flask(__name__)

@app.route('/')
def run_script():

    response = requests.get('https://noricha-vr.github.io/toGithubPagesJson/sample.json')
    data = json.loads(response.text)


    for i, item in enumerate(data):
        poster_url = item.get("ポスター", "https://cdn.discordapp.com/attachments/1136630413054464070/1147808605660270642/10.png") 
        image_file_name = f"img/{i:03d}.png"
        subprocess.run(f"wget {poster_url} -O {image_file_name}", shell=True)

    movie_config = MovieConfig(frame_rate='1', width='640', encode_speed='fast', output_movie_path='movie/output.mp4', image_type='png')
    image_to_movie(movie_config)

    bucket_name = "TaAGatheringListSystem"
    source_file_name = "movie/output.mp4"
    destination_blob_name = "TaAGatheringList.mp4"

    upload_blob(bucket_name, source_file_name, destination_blob_name)

    return "Process completed"

class MovieConfig:
    def __init__(self, frame_rate, width, encode_speed, output_movie_path, image_type='png'):
        self.frame_rate = frame_rate
        self.width = width
        self.encode_speed = encode_speed
        self.output_movie_path = output_movie_path
        self.image_type = image_type
        self.input_image_dir = Path('./img')

def image_to_movie(movie_config: MovieConfig):
    image_paths = sorted(movie_config.input_image_dir.glob(f'*.{movie_config.image_type}'))
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
