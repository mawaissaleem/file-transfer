import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QListWidget,
    QWidget,
)
from PySide6.QtCore import Qt
from .api_client import get_file_list, download_file
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QProgressBar
from .upload_worker import UploadWorker
from .download_worker import DownloadWorker


class MainWindow(QMainWindow):
    def __init__(self, backend_manager):
        super().__init__()

        self.backend_manager = backend_manager

        self.setWindowTitle("Local Wi-Fi File Transfer")
        self.setMinimumSize(600, 400)

        # UI Elements
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.upload_button = QPushButton("📤 Select File & Upload")
        self.upload_button.clicked.connect(self.select_and_upload_file)

        self.refresh_button = QPushButton("🔄 Refresh File List")
        self.refresh_button.clicked.connect(self.load_file_list)

        self.file_list = QListWidget()

        self.download_button = QPushButton("⬇ Download Selected File")
        self.download_button.clicked.connect(self.download_selected_file)

        self.upload_progress = QProgressBar()
        self.upload_progress.setValue(0)

        self.download_progress = QProgressBar()
        self.download_progress.setValue(0)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.file_list)
        layout.addWidget(self.download_button)
        layout.addWidget(self.upload_progress)
        layout.addWidget(self.download_progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_and_upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*)",
        )

        if not file_path:
            self.status_label.setText("No file selected")
            return

        # Reset UI
        self.upload_progress.setValue(0)
        self.status_label.setText("Uploading...")

        # Start background worker
        self.upload_worker = UploadWorker(file_path)
        self.upload_worker.progress.connect(self.upload_progress.setValue)
        self.upload_worker.success.connect(self.on_upload_success)
        self.upload_worker.error.connect(self.on_upload_error)
        self.upload_worker.start()

    def closeEvent(self, event):
        self.backend_manager.stop()
        event.accept()

    def load_file_list(self):
        try:
            files = get_file_list()
            self.file_list.clear()

            for f in files:
                self.file_list.addItem(f["name"])

            if not files:
                self.status_label.setText("No files available")
            else:
                self.status_label.setText("Files loaded")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # -------- Download --------

    def download_selected_file(self):
        item = self.file_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Select a file first")
            return

        filename = item.text()

        save_path, _ = QFileDialog.getSaveFileName(self, "Save File As", filename)
        if not save_path:
            return

        # Reset UI
        self.download_progress.setValue(0)
        self.status_label.setText("Downloading...")

        # Start worker
        self.download_worker = DownloadWorker(filename, save_path)
        self.download_worker.progress.connect(self.download_progress.setValue)
        self.download_worker.success.connect(self.on_download_success)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.start()

    def on_upload_success(self, message):
        self.status_label.setText(f"✅ {message}")
        self.upload_progress.setValue(100)
        self.load_file_list()  # refresh list after upload

    def on_upload_error(self, error):
        self.status_label.setText(f"❌ Upload failed: {error}")

    def on_download_success(self, message):
        self.status_label.setText(f"✅ {message}")
        self.download_progress.setValue(100)

    def on_download_error(self, error):
        self.status_label.setText(f"❌ Download failed: {error}")
