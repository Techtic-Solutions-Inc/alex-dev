#!/usr/bin/env python3
"""CLI wrapper for Alembic migrations across environments.

Usage:
    python scripts/migrate.py upgrade          # Apply all pending migrations
    python scripts/migrate.py upgrade REV      # Upgrade to a specific revision
    python scripts/migrate.py downgrade        # Roll back one migration
    python scripts/migrate.py downgrade base   # Roll back all migrations
    python scripts/migrate.py current          # Show current revision
    python scripts/migrate.py history          # Show migration history
    python scripts/migrate.py pending          # List pending migrations
    python scripts/migrate.py generate MSG     # Generate a new migration
    python scripts/migrate.py stamp REV        # Stamp DB at revision without migrating
    python scripts/migrate.py check            # Verify database connectivity
"""
import argparse
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv

load_dotenv(project_root / ".env")
load_dotenv(project_root / "src" / ".env", override=False)
load_dotenv(project_root / ".env.test", override=False)


def _env_banner() -> None:
    env = os.getenv("ENVIRONMENT", "development")
    db = os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "(not set)"
    safe_db = db.split("@")[-1] if "@" in db else db
    print(f"Environment : {env}")
    print(f"Database    : ...@{safe_db}")
    print()


def _handle_error(action: str, exc: Exception) -> None:
    """Print a user-friendly error message and exit."""
    print(f"ERROR: Failed to {action}.", file=sys.stderr)
    print(f"  {exc}", file=sys.stderr)
    sys.exit(1)


def cmd_upgrade(args: argparse.Namespace) -> None:
    from alembic import command
    from config.migrations import get_alembic_config, run_migrations

    _env_banner()
    try:
        if args.revision == "head":
            print("Applying all pending migrations...")
            run_migrations()
        else:
            print(f"Upgrading to revision: {args.revision}")
            cfg = get_alembic_config()
            command.upgrade(cfg, args.revision)
        print("Done.")
    except Exception as exc:
        _handle_error("apply migrations", exc)


def cmd_downgrade(args: argparse.Namespace) -> None:
    from config.migrations import downgrade_migrations

    _env_banner()
    try:
        print(f"Downgrading to: {args.revision}")
        downgrade_migrations(args.revision)
        print("Done.")
    except Exception as exc:
        _handle_error("downgrade migrations", exc)


def cmd_current(args: argparse.Namespace) -> None:
    from config.migrations import get_current_revision

    _env_banner()
    try:
        rev = get_current_revision()
        print(f"Current revision: {rev or '(none)'}")
    except Exception as exc:
        _handle_error("retrieve current revision", exc)


def cmd_history(args: argparse.Namespace) -> None:
    from config.migrations import get_migration_history

    _env_banner()
    try:
        history = get_migration_history()
    except Exception as exc:
        _handle_error("retrieve migration history", exc)
        return

    if not history:
        print("No migration scripts found.")
        return
    for entry in history:
        applied = "+" if entry["is_applied"] else " "
        current = "*" if entry.get("is_current") else " "
        marker = f"{applied}{current}"
        desc = entry["description"] or "(no description)"
        print(f" {marker} {entry['revision']} — {desc}")
    print()
    print("  + = applied, * = current database revision")


def cmd_pending(args: argparse.Namespace) -> None:
    from config.migrations import get_pending_migrations

    _env_banner()
    try:
        pending = get_pending_migrations()
    except Exception as exc:
        _handle_error("check pending migrations", exc)
        return

    if not pending:
        print("No pending migrations.")
    else:
        print(f"{len(pending)} pending migration(s):")
        for rev_id in pending:
            print(f"  - {rev_id}")


def cmd_generate(args: argparse.Namespace) -> None:
    from config.migrations import generate_revision

    _env_banner()
    try:
        print(f"Generating migration: {args.message}")
        rev_id = generate_revision(
            message=args.message,
            autogenerate=not args.empty,
        )
        print(f"Created revision: {rev_id}")
    except Exception as exc:
        _handle_error("generate migration", exc)


def cmd_stamp(args: argparse.Namespace) -> None:
    from config.migrations import stamp_revision

    _env_banner()
    try:
        print(f"Stamping database at: {args.revision}")
        stamp_revision(args.revision)
        print("Done.")
    except Exception as exc:
        _handle_error("stamp database", exc)


def cmd_check(args: argparse.Namespace) -> None:
    from config.migrations import check_database_connectivity

    _env_banner()
    if check_database_connectivity():
        print("Database is reachable.")
    else:
        print("ERROR: Cannot connect to database.", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Database migration management CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_upgrade = subparsers.add_parser("upgrade", help="Apply migrations")
    p_upgrade.add_argument("revision", nargs="?", default="head")
    p_upgrade.set_defaults(func=cmd_upgrade)

    p_downgrade = subparsers.add_parser("downgrade", help="Roll back migrations")
    p_downgrade.add_argument("revision", nargs="?", default="-1")
    p_downgrade.set_defaults(func=cmd_downgrade)

    p_current = subparsers.add_parser("current", help="Show current revision")
    p_current.set_defaults(func=cmd_current)

    p_history = subparsers.add_parser("history", help="Show migration history")
    p_history.set_defaults(func=cmd_history)

    p_pending = subparsers.add_parser("pending", help="List pending migrations")
    p_pending.set_defaults(func=cmd_pending)

    p_generate = subparsers.add_parser("generate", help="Generate a new migration")
    p_generate.add_argument("message", help="Migration description")
    p_generate.add_argument(
        "--empty",
        action="store_true",
        help="Create an empty migration instead of autogenerating",
    )
    p_generate.set_defaults(func=cmd_generate)

    p_stamp = subparsers.add_parser("stamp", help="Stamp DB at revision")
    p_stamp.add_argument("revision", nargs="?", default="head")
    p_stamp.set_defaults(func=cmd_stamp)

    p_check = subparsers.add_parser("check", help="Check database connectivity")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
