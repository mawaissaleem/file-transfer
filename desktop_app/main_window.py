from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, backend_manager):
        super().__init__()

        self.backend_manager = backend_manager

        self.setWindowTitle("Local Wi-Fi File Transfer")
        self.setMinimumSize(500, 300)

        label = QLabel("Backend is running in background")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

    def closeEvent(self, event):
        self.backend_manager.stop()
        event.accept()
