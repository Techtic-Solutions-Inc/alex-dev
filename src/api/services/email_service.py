def _build_password_reset_link(settings: Settings, token: str) -> str:
    base = settings.frontend_base_url.rstrip("/")
    return f"{base}/reset-password?token={token}"

# Other existing code in the file
