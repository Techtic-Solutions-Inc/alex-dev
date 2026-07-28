import os

from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET: str = os.getenv("AUTH0_CLIENT_SECRET", "")
AUTH0_CONNECTION: str = os.getenv("AUTH0_CONNECTION", "Username-Password-Authentication")
DASHBOARD_URL: str = os.getenv("DASHBOARD_URL", "/dashboard")
