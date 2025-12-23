import sys
import subprocess
import signal
import logging

logger = logging.getLogger("desktop-backend")


class BackendManager:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.process = None

    def start(self):
        if self.process is not None:
            logger.warning("Backend already running")
            return

        logger.info("Starting backend server")

        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.app.main:app",
                "--host",
                self.host,
                "--port",
                str(self.port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(self):
        if self.process:
            logger.info("Stopping backend server")
            self.process.send_signal(signal.SIGTERM)
            self.process.wait()
            self.process = None
