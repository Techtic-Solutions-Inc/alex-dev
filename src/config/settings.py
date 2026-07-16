import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@example.com")
EMAIL_CONFIRMATION_BASE_URL = os.getenv(
    "EMAIL_CONFIRMATION_BASE_URL", "http://localhost:8000/api/v1/auth/confirm-email"
)
EMAIL_CONFIRMATION_EXPIRATION_HOURS = int(
    os.getenv("EMAIL_CONFIRMATION_EXPIRATION_HOURS", "24")
)
