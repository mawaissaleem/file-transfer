import requests

BASE_URL = "http://127.0.0.1:8000"


def get_file_list():
    response = requests.get(f"{BASE_URL}/files")
    response.raise_for_status()
    return response.json()


def download_file(filename, save_path):
    with requests.get(f"{BASE_URL}/files/{filename}", stream=True) as r:
        r.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
