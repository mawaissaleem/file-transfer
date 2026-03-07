import requests
import os
from dotenv import load_dotenv


def get_file_list():
    # load_dotenv("./../config/.env")
    load_dotenv()
    response = requests.get(f"{os.getenv('BASE_URL')}/files")
    response.raise_for_status()
    return response.json()


def download_file(filename, save_path):
    load_dotenv()
    with requests.get(f"{os.getenv('BASE_URL')}/files/{filename}", stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
