from PySide6.QtCore import QThread, Signal
import requests
from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
    MultipartEncoderMonitor,
)
import os

BASE_URL = "http://127.0.0.1:8000"


class UploadWorker(QThread):
    progress = Signal(int)
    success = Signal(str)
    error = Signal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            filename = os.path.basename(self.file_path)

            encoder = MultipartEncoder(
                fields={
                    "file": (
                        filename,
                        open(self.file_path, "rb"),
                        "application/octet-stream",
                    )
                }
            )

            monitor = MultipartEncoderMonitor(encoder, self._progress_callback)

            headers = {"Content-Type": monitor.content_type}

            response = requests.post(
                f"{BASE_URL}/upload",
                data=monitor,
                headers=headers,
                timeout=60,
            )

            response.raise_for_status()
            self.progress.emit(100)
            self.success.emit("Upload completed")

        except Exception as e:
            self.error.emit(str(e))

    def _progress_callback(self, monitor):
        percent = int((monitor.bytes_read / monitor.len) * 100)
        self.progress.emit(percent)
