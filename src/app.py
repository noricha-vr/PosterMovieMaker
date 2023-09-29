from flask import Flask
import json
import requests
from movie import image_to_movie, MovieConfig, download_images, upload_blob

app = Flask(__name__)

bucket_name = "TaAGatheringListSystem"
source_file_name = "movie/output.mp4"
destination_blob_name = "TaAGatheringList.mp4"
json_url = 'https://noricha-vr.github.io/toGithubPagesJson/sample.json'

@app.route('/')
def run_script():
    response = requests.get(json_url)
    data = json.loads(response.text)
    
    images = download_images(data)
    movie_config = MovieConfig(frame_rate='1', width='640', encode_speed='fast', output_movie_path='movie/output.mp4', image_type='png')
    image_to_movie(movie_config, images)


    upload_blob(bucket_name, source_file_name, destination_blob_name)

    return "Process completed"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
