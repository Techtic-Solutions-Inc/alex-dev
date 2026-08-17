"""MongoDB persistence for user and refresh-session records."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError


class UserRepository:
    """Encapsulate account and refresh-token persistence."""

    def __init__(self, database: Database) -> None:
        self._users = database["users"]
        self._sessions = database["auth_sessions"]

    def create_user(
        self, first_name: str, last_name: str, email: str, password_hash: str
    ) -> dict[str, Any] | None:
        """Create a unique normalized account, returning None on duplicate email."""
        user = {
            "id": str(uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "email": email.lower(),
            "password_hash": password_hash,
            "is_active": True,
            "email_verified": False,
            "created_at": datetime.now(UTC),
        }
        try:
            self._users.insert_one(user)
        except DuplicateKeyError:
            return None
        return user

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        """Find an account by its normalized email."""
        return self._users.find_one({"email": email.lower()})

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        """Find an account by its public UUID."""
        return self._users.find_one({"id": user_id})

    def verify_email(self, user_id: str) -> bool:
        """Mark an existing account's email address as verified."""
        result = self._users.update_one(
            {"id": user_id},
            {"$set": {"email_verified": True, "email_verified_at": datetime.now(UTC)}},
        )
        return result.matched_count == 1

    def store_refresh_token(
        self, token_id: str, user_id: str, expires_at: datetime
    ) -> None:
        """Store only a hash of a refresh token identifier."""
        self._sessions.insert_one(
            {
                "token_id_hash": self._hash_token_id(token_id),
                "user_id": user_id,
                "expires_at": expires_at,
                "revoked_at": None,
                "created_at": datetime.now(UTC),
            }
        )

    def consume_refresh_token(self, token_id: str, user_id: str) -> bool:
        """Atomically revoke one refresh credential and report whether it was live."""
        result = self._sessions.update_one(
            {
                "token_id_hash": self._hash_token_id(token_id),
                "user_id": user_id,
                "revoked_at": None,
                "expires_at": {"$gt": datetime.now(UTC)},
            },
            {"$set": {"revoked_at": datetime.now(UTC)}},
        )
        return result.modified_count == 1

    def revoke_all_sessions(self, user_id: str) -> None:
        """Invalidate every outstanding refresh credential after suspected replay."""
        self._sessions.update_many(
