import uuid

from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import Session, relationship

from src.api.v1.models.enums import AccountStatus
from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'users'

    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    account_status = Column(
        Enum(AccountStatus),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )

    password_reset_tokens = relationship(
        'PasswordResetToken',
        back_populates='user',
        cascade='all, delete-orphan',
    )

    @classmethod
    def get_by_id(cls, db: Session, user_id: uuid.UUID) -> 'User | None':
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def update_account_status(
        cls,
        db: Session,
        user_id: uuid.UUID,
        status: AccountStatus,
    ) -> 'User | None':
        user = cls.get_by_id(db, user_id)
        if user is None:
            return None

        user.account_status = status
        db.commit()
        db.refresh(user)
        return user
