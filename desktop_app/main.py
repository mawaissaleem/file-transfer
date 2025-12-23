import sys
import logging
from PySide6.QtWidgets import QApplication
from desktop_app.backend_manager import BackendManager
from desktop_app.main_window import MainWindow

# Basic logging for desktop app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    app = QApplication(sys.argv)

    backend = BackendManager()
    backend.start()

    window = MainWindow(backend)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
