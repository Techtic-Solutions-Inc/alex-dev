from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from src.api.exceptions import AuthException
from src.config import settings

async def login_user(email: str, password: str, db):
    auth0 = Auth0(settings.AUTH0_DOMAIN, settings.AUTH0_CLIENT_ID, settings.AUTH0_CLIENT_SECRET)
    try:
        token = auth0.authentication().login(email, password)
        # Store session or token in DB if needed
        return {"token": token['id_token']}
    except Exception as e:
        raise AuthException("Invalid credentials")

async def get_user_session(db):
    # Retrieve session details from DB
    session_data = {}
    if not session_data:
        raise AuthException("Session not found")
    return session_data