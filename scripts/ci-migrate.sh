#!/usr/bin/env bash
set -euo pipefail

if [ -z "${MIGRATIONS_DATABASE_URL:-}" ] && [ -z "${DATABASE_URL:-}" ]; then
  echo "Set MIGRATIONS_DATABASE_URL or DATABASE_URL before running migrations." >&2
  exit 1
fi

if [ ! -f dist/database/migrations/migration.cli.js ]; then
  echo "Compiled migration CLI not found. Run npm run build first." >&2
  exit 1
fi

export MIGRATION_RUNNER_ID="${MIGRATION_RUNNER_ID:-manual-$(hostname)-$$}"

echo "Migration status (before):"
npm run migration:status:prod

echo "Applying pending migrations..."
npm run migration:up:prod

echo "Migration status (after):"
npm run migration:status:prod