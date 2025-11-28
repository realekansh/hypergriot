#!/usr/bin/env bash
set -euo pipefail

# Basic sqlite backup script. If you're using Postgres, use pg_dump instead (not included).

DB_PATH="./hypergriot.db"
BACKUP_DIR="./extras/backups"
mkdir -p "$BACKUP_DIR"

if [ ! -f "$DB_PATH" ]; then
  echo "No sqlite DB found at $DB_PATH"
  exit 1
fi

TS=$(date +"%Y%m%d_%H%M%S")
OUT="$BACKUP_DIR/hypergriot_${TS}.db"

cp "$DB_PATH" "$OUT"
echo "Backup created: $OUT"
