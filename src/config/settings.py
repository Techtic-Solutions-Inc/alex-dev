import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY") or os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRY", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "3600")))

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")
