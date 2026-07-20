import bcrypt
import jwt
from datetime import datetime, timedelta
from src.config.settings import settings

# Mock user database
users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": bcrypt.hashpw("testpassword".encode('utf-8'), bcrypt.gensalt())
    }
}

def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['hashed_password']):
        return user
    return None

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt