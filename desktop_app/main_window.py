import requests
from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, backend_manager):
        super().__init__()

        self.backend_manager = backend_manager

        self.setWindowTitle("Local Wi-Fi File Transfer")
        self.setMinimumSize(500, 300)

        # UI Elements
        self.status_label = QLabel("Select a file to upload")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.upload_button = QPushButton("Select File & Upload")
        self.upload_button.clicked.connect(self.select_and_upload_file)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.upload_button)

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
