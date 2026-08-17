"""Command-line entry point for MongoDB migrations."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.db.migrations import MIGRATIONS, MigrationRunner
from app.db.migrations.base import MigrationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage MongoDB schema migrations.")
    parser.add_argument(
        "action", choices=("upgrade", "downgrade", "status"), help="Migration operation."
    )
    parser.add_argument(
        "--target",
        help=(
            "Revision to stop at. Upgrade defaults to the latest revision; "
            "downgrade defaults to base."
        ),
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Execute a migration action and return a process exit code."""
    args = _parser().parse_args(arguments)
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=10_000)
    try:
        client.admin.command("ping")
        runner = MigrationRunner(client[settings.DB_NAME], MIGRATIONS)
        if args.action == "status":
            for migration in runner.status():
                state = "applied" if migration.applied else "pending"
                print(f"{migration.revision}  {state:7}  {migration.description}")
            return 0

        revisions = (
            runner.upgrade(args.target)
            if args.action == "upgrade"
            else runner.downgrade(args.target)
        )
        print("No migrations to run." if not revisions else "\n".join(revisions))
        return 0
    except (MigrationError, PyMongoError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
