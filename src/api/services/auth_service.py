from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from src.config.settings import settings

async def login_user(email: str, password: str) -> str:
    """Authenticate user with Auth0 and return JWT token."""
    auth0 = Auth0(settings.AUTH0_DOMAIN, settings.AUTH0_CLIENT_ID, settings.AUTH0_CLIENT_SECRET)
    try:
        token = auth0.authentication().login(email, password)
        return token['id_token']
    except Exception as e:
        raise ValueError("Invalid credentials") from e

async def get_user_session(token: str) -> dict:
    """Retrieve user session details from Auth0."""
    auth0 = Auth0(settings.AUTH0_DOMAIN, settings.AUTH0_CLIENT_ID, settings.AUTH0_CLIENT_SECRET)
    try:
        user_info = auth0.users.get(token)
        return user_info
    except Exception as e:
        raise ValueError("Invalid session token") from e
