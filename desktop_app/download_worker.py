import requests
from PySide6.QtCore import QThread, Signal


class DownloadWorker(QThread):
    progress = Signal(int)
    success = Signal(str)
    error = Signal(str)

    def __init__(self, filename, save_path):
        super().__init__()
        self.filename = filename
        self.save_path = save_path

    def run(self):
        try:
            url = f"http://127.0.0.1:8000/files/{self.filename}"
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()

                total_size = r.headers.get("Content-Length")
                total_size = int(total_size) if total_size else None

                downloaded = 0

                with open(self.save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

                            # Only calculate percentage if total size is known
                            if total_size:
                                percent = int((downloaded / total_size) * 100)
                                self.progress.emit(percent)

            self.success.emit("Download completed")

        except Exception as e:
            self.error.emit(str(e))
