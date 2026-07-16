import uuid

from sqlalchemy import Column

from src.models.types import GUID


class UUIDPrimaryKeyMixin:
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
