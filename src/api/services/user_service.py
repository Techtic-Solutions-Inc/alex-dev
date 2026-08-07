from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.config.settings import settings

async def create_user_with_confirmation(request):
    """Create a new user and send a confirmation email."""
    # Validate and create user logic here
    if user_exists(request.email):
        raise ValueError("Email already exists")
    user_id = create_user(request)
    send_confirmation_email(request.email)
    return user_id

async def send_confirmation_email(email: str):
    """Send confirmation email using SendGrid."""
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=email,
        subject='Confirm your registration',
        html_content='<strong>Thank you for registering. Please confirm your email.</strong>')
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        raise ValueError("Failed to send confirmation email") from e
