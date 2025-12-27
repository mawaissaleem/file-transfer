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

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.file_list)
        layout.addWidget(self.download_button)

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

        self.status_label.setText("Uploading...")

        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    "http://127.0.0.1:8000/upload",
                    files={"file": f},
                    timeout=10,
                )

            if response.status_code == 200:
                self.status_label.setText("✅ Upload successful")
            else:
                self.status_label.setText(f"❌ Upload failed ({response.status_code})")

        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")

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

        self.status_label.setText("Downloading...")

        try:
            download_file(filename, save_path)
            self.status_label.setText("✅ Download complete")
        except Exception as e:
            self.status_label.setText(f"❌ Download failed: {str(e)}")
