from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.config import settings

async def create_user_with_confirmation(request, db):
    # Validate and create user in DB
    if user_exists(request.email, db):
        raise ValueError("Email already exists")
    # Send confirmation email
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=request.email,
        subject='Confirm your registration',
        html_content='<strong>Thank you for registering</strong>')
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        raise Exception("Failed to send confirmation email")
    return {"id": "user_id", "email": request.email}