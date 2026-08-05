import os
from pathlib import Path

from dotenv import load_dotenv

_settings_dir = Path(__file__).resolve().parent
_project_root = _settings_dir.parent.parent
load_dotenv(_project_root / ".env")
load_dotenv(_settings_dir.parent / ".env", override=False)

JWT_SECRET = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600")))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
