import os
from pathlib import Path

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage"))
DEMO_MODE = os.getenv("DEMO_MODE", "mock")

UPLOADS_DIR = STORAGE_DIR / "uploads"
JSON_OUT_DIR = STORAGE_DIR / "outputs" / "json"
XML_OUT_DIR = STORAGE_DIR / "outputs" / "xml"

for d in [UPLOADS_DIR, JSON_OUT_DIR, XML_OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)
