from src.config.settings import Settings

def _build_password_reset_link(settings: Settings, token: str) -> str:
    base_url = settings.app_base_url.rstrip("/")
    return f"{base_url}/api/password-recovery/validate/{token}"

# Other functions and logic related to email service
