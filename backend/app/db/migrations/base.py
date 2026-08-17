"""Contracts and errors used by MongoDB migrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from pymongo.database import Database


class MigrationError(RuntimeError):
    """Base exception raised when a migration cannot be completed safely."""


class MigrationStateError(MigrationError):
    """Raised when the migration ledger does not match the known revisions."""


class MigrationLockError(MigrationError):
    """Raised when another migration process currently owns the database lock."""


class Migration(ABC):
    """A versioned, reversible change to a MongoDB database."""

    revision: Final[str]
    description: Final[str]

    @abstractmethod
    def upgrade(self, database: Database) -> None:
        """Apply this migration."""

    @abstractmethod
    def downgrade(self, database: Database) -> None:
        """Revert this migration."""
