"""MongoDB schema and data migration framework."""

from app.db.migrations.auth_sessions_migration import AuthSessionsMigration
from app.db.migrations.initial_migration import InitialMigration
from app.db.migrations.runner import MigrationRunner, MigrationStatus

MIGRATIONS = (InitialMigration(), AuthSessionsMigration())

__all__ = ["MIGRATIONS", "MigrationRunner", "MigrationStatus"]
