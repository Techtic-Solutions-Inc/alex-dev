import uuid


class UUIDPrimaryKeyMixin:
    """Mixin convention for MongoDB document models using UUID primary keys."""

    id: uuid.UUID
