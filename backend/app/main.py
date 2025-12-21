# backend/app/main.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from datetime import datetime

# -----------------------------
# Configuration
# -----------------------------
STORAGE_DIR = "shared"

# Ensure storage directory exists
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI(title="Local Wi-Fi File Transfer - Backend")

# -----------------------------
# Helper Functions
# -----------------------------
def generate_safe_filename(original_name: str) -> str:
    """
    Convert original filename into a safe format:
    - Replace spaces with _
    - Keep only letters, numbers, _ and -
    - Append timestamp YYYYMMDD_HHMMSSfff
    - Preserve original extension
    """
    name, ext = os.path.splitext(original_name)
    # Replace spaces with underscore
    name = name.replace(" ", "_")
    # Keep only letters, numbers, _ and -
    name = "".join(c for c in name if c.isalnum() or c in ["_", "-"])
    # Append timestamp with milliseconds
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
    return f"{name}_{timestamp}{ext}"

# -----------------------------
# Upload Endpoint
# -----------------------------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        filename = generate_safe_filename(file.filename)
        file_path = os.path.join(STORAGE_DIR, filename)

        # Stream file in chunks to avoid memory issues
        with open(file_path, "wb") as buffer:
            while content := await file.read(1024*1024):  # 1 MB chunks
                buffer.write(content)

        return JSONResponse({"status": "success", "filename": filename})

    except Exception as e:
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=500)

# -----------------------------
# Test Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"status": "backend running"}

