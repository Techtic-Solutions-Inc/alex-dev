import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.api.v1.models.enums import AccountStatus
from src.api.v1.models.user import User
from src.api.v1.schemas.admin import AdminUpdateUserRequest, AdminUpdateUserResponse

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def update_user_account_status(
        self,
        request: AdminUpdateUserRequest,
    ) -> AdminUpdateUserResponse:
        if request.status not in AccountStatus:
            raise ValueError('Invalid account status')

        try:
            updated_user = User.update_account_status(
                self.db,
                request.user_id,
                request.status,
            )
        except SQLAlchemyError as exc:
            self.db.rollback()
            logger.exception(
                'Failed to update account status for user %s',
                request.user_id,
            )
            raise RuntimeError('Failed to update user account status') from exc

        if updated_user is None:
            raise ValueError('User not found')

        return AdminUpdateUserResponse()
