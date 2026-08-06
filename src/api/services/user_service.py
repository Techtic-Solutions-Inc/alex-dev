import logging
from sqlalchemy.exc import SQLAlchemyError
from src.email import send_confirmation_email
from src.database import db_session
from src.exceptions import InternalServerError

logger = logging.getLogger(__name__)

async def register_user(user_data):
    try:
        # Start a new database session
        async with db_session() as session:
            async with session.begin():
                # Add user to the database
                user = User(**user_data)
                session.add(user)
                
                # Attempt to send confirmation email
                try:
                    confirmation_link = await send_confirmation_email(user.email)
                except Exception as e:
                    logger.error(f"Failed to send confirmation email: {e}")
                    session.rollback()
                    raise InternalServerError(message="Unable to send confirmation email. Please try again.")

                # Commit the transaction only if email was sent successfully
                session.commit()

    except SQLAlchemyError as e:
        logger.error(f"Database error during user registration: {e}")
        raise InternalServerError(message="An error occurred during registration. Please try again.")

    return user