import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/rajkamal_jewellers")
    UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rajkamal.test")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
