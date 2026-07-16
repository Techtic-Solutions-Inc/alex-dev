import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
JWT_SECRET = os.getenv('JWT_SECRET')

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
REDIS_SOCKET_TIMEOUT = float(os.getenv('REDIS_SOCKET_TIMEOUT', '1.0'))

RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', '100'))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
RATE_LIMIT_CRITERIA = os.getenv('RATE_LIMIT_CRITERIA', 'ip')

PASSWORD_RESET_FRONTEND_URL = os.getenv(
    'PASSWORD_RESET_FRONTEND_URL',
    'http://localhost:3000/reset-password',
)
PASSWORD_RESET_API_URL = os.getenv(
    'PASSWORD_RESET_API_URL',
    'http://localhost:8000/api/v1/reset-password',
)
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_EXPIRY_HOURS', '1'))

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
