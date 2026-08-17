"""Versioned, rollback-capable MongoDB migration runner."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from logging import getLogger
from uuid import uuid4

from pymongo import ASCENDING, ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.config import settings
from app.db.migrations.base import Migration, MigrationLockError, MigrationStateError

logger = getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MigrationStatus:
    """Current state of one known migration revision."""

    revision: str
    description: str
    applied: bool


class MigrationRunner:
    """Apply ordered migrations while recording revision state in MongoDB."""

    def __init__(
        self,
        database: Database,
        migrations: Sequence[Migration],
        *,
        ledger_collection: str = settings.MIGRATIONS_COLLECTION,
        lock_collection: str = settings.MIGRATIONS_LOCK_COLLECTION,
        lock_timeout_seconds: int = settings.MIGRATION_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        self._database = database
        self._migrations = tuple(migrations)
        self._ledger = database[ledger_collection]
        self._locks = database[lock_collection]
        self._lock_timeout = timedelta(seconds=lock_timeout_seconds)
        self._validate_migrations()

    def status(self) -> list[MigrationStatus]:
        """Return every known revision with its applied state."""
        applied = self._applied_revisions()
        return [
            MigrationStatus(
                revision=migration.revision,
                description=migration.description,
                applied=migration.revision in applied,
            )
            for migration in self._migrations
        ]

    def upgrade(self, target: str | None = None) -> list[str]:
        """Apply every pending migration through *target* (or the latest revision)."""
        target_index = self._target_index(target, default_to_latest=True)
        token = self._acquire_lock()
        try:
            applied = self._validated_applied_revisions()
            applied_count = len(applied)
            completed: list[str] = []
            for migration in self._migrations[applied_count : target_index + 1]:
                logger.info("Applying MongoDB migration %s", migration.revision)
                migration.upgrade(self._database)
                self._ledger.insert_one(
                    {
                        "_id": migration.revision,
                        "description": migration.description,
                        "checksum": self._checksum(migration),
                        "applied_at": datetime.now(UTC),
                    }
                )
                completed.append(migration.revision)
            return completed
        finally:
            self._release_lock(token)

    def downgrade(self, target: str | None = None) -> list[str]:
        """Rollback to *target*, or to the base schema when target is ``None``."""
        target_index = self._target_index(target, default_to_latest=False)
        token = self._acquire_lock()
        try:
            applied = self._validated_applied_revisions()
            completed: list[str] = []
            for migration in reversed(self._migrations[target_index + 1 : len(applied)]):
                logger.info("Rolling back MongoDB migration %s", migration.revision)
                migration.downgrade(self._database)
                self._ledger.delete_one({"_id": migration.revision})
                completed.append(migration.revision)
            return completed
        finally:
            self._release_lock(token)

    def _validate_migrations(self) -> None:
        revisions = [migration.revision for migration in self._migrations]
        if not revisions or len(revisions) != len(set(revisions)):
            raise MigrationStateError("Migration revisions must be non-empty and unique.")
        if self._lock_timeout <= timedelta():
            raise MigrationStateError("Migration lock timeout must be greater than zero.")

    def _target_index(self, target: str | None, *, default_to_latest: bool) -> int:
        if target is None:
            return len(self._migrations) - 1 if default_to_latest else -1
        for index, migration in enumerate(self._migrations):
            if migration.revision == target:
                return index
        raise MigrationStateError(f"Unknown migration revision: {target}.")

    def _applied_revisions(self) -> dict[str, dict[str, object]]:
        return {
            document["_id"]: document
            for document in self._ledger.find({}, projection={"_id": 1, "checksum": 1})
        }

    def _validated_applied_revisions(self) -> list[str]:
        applied = self._applied_revisions()
        expected = [migration.revision for migration in self._migrations[: len(applied)]]
        if set(applied) != set(expected):
            raise MigrationStateError(
                "The migration ledger is not a contiguous prefix of known revisions."
            )
        for migration in self._migrations[: len(applied)]:
            if applied[migration.revision].get("checksum") != self._checksum(migration):
                raise MigrationStateError(
                    f"Migration checksum mismatch for {migration.revision}."
                )
        return expected

    def _acquire_lock(self) -> str:
        token = str(uuid4())
        now = datetime.now(UTC)
        expires_at = now + self._lock_timeout
        self._locks.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

        result = self._locks.find_one_and_update(
            {"_id": "migration-runner", "expires_at": {"$lte": now}},
            {"$set": {"token": token, "expires_at": expires_at}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            try:
                self._locks.insert_one(
                    {"_id": "migration-runner", "token": token, "expires_at": expires_at}
                )
            except DuplicateKeyError as exc:
                raise MigrationLockError(
                    "A migration process is already running for this database."
                ) from exc
        return token

    def _release_lock(self, token: str) -> None:
        self._locks.delete_one({"_id": "migration-runner", "token": token})

    @staticmethod
    def _checksum(migration: Migration) -> str:
        payload = f"{migration.revision}:{migration.description}".encode()
        return sha256(payload).hexdigest()
