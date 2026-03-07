from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import os
from datetime import datetime
import mimetypes
import logging
from pathlib import Path
import uuid
import secrets
from datetime import timedelta, datetime
import qrcode
from singleton_variables import active_sessions

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("file-transfer")

# -----------------------------
# Configuration
# -----------------------------
STORAGE_DIR = Path("shared")

if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

logger.info(f"Storage directory set to: {os.path.abspath(STORAGE_DIR)}")

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(title="Local Wi-Fi File Transfer - Backend")


# -----------------------------
# Helper Functions
# -----------------------------
def generate_safe_filename(original_name: str) -> str:
    name, ext = os.path.splitext(original_name)
    name = name.replace(" ", "_")
    name = "".join(c for c in name if c.isalnum() or c in ["_", "-"])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
    return f"{name}_{timestamp}{ext}"


def file_streamer(path: str, chunk_size: int = 1024 * 1024):
    with open(path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk


# -----------------------------
# Upload Endpoint
# -----------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Upload started: {file.filename}")

    try:
        filename = generate_safe_filename(file.filename)
        file_path = os.path.join(STORAGE_DIR, filename)
        total_bytes = 0

        with open(file_path, "wb") as buffer:
            while content := await file.read(1024 * 1024):
                buffer.write(content)
                total_bytes += len(content)

        logger.info(
            f"Upload completed: {filename} ({total_bytes / (1024*1024):.2f} MB)"
        )

        return JSONResponse({"status": "success", "filename": filename})

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        return JSONResponse(
            {"status": "error", "detail": "Upload failed"}, status_code=500
        )


# -----------------------------
# Download Endpoint
# -----------------------------
@app.get("/files/{filename}")
def download_file(filename: str):
    file_path = os.path.join(STORAGE_DIR, filename)

    if not os.path.exists(file_path):
        logger.warning(f"Download failed (not found): {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    logger.info(f"Download started: {filename}")

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        file_streamer(file_path), media_type=content_type, headers=headers
    )


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def root():
    return {"status": "backend running"}


# -----------------------------
# List Files Endpoint
# -----------------------------
@app.get("/files")
def list_files():
    try:

        files = []
        for file in STORAGE_DIR.iterdir():
            if file.is_file():
                files.append({"name": file.name, "size": file.stat().st_size})

        return files
    except Exception as e:
        print("Error listing files:", e)
        return []  # Return empty list instead of 500


# ------------------------------
# pair (when andriod device scans the qr code and hit this endpoint)
# ------------------------------
@app.post("/pair")
def pair(session: str, token, expiry_at):
    pass
    # get the things from andriod and then checks if they exist in the global singleton or not


# -----------------------------
# generate qrcode
# ----------------------------
@app.post("/generate_qrcode")
def generate_qrcode(expiry_mins: int) -> qrcode:
    session, token, expiry_at = create_unqiue_session_token_expiry_time(
        expiry_mins=expiry_mins
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    # fix the ip and port thing
    qr.add_data(
        f"myapp://pair?ip=193.168.1.42&port=8080&session={session}$token={token}&exp={expiry_at}"
    )
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # adding into singleton
    active_sessions[session] = {"token": token, "expiry_at": expiry_at}

    return img
    # img.save("qr_code.png")


# should generate and return the qr code to the frontend to show the user

# myapp://pair?ip=193.168.1.42&port=8080&session=abc123&token=xyz789&exp=1700000000


def create_unqiue_session_token_expiry_time(expiry_mins: int = 30) -> tuple:
    """
    returns the unqiue session token and the expiry at time
    """
    return (
        str(uuid.uuid4()),
        secrets.token_urlsafe(16),
        datetime.now() + timedelta(minutes=expiry_mins),
    )
