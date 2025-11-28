#!/usr/bin/env bash
set -euo pipefail

# Start-dev helper: loads .env (if present), creates sqlite tables and runs uvicorn
# Usage: ./scripts/start-dev.sh

# load .env if exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

echo "Using DATABASE_URL=${DATABASE_URL:-(not set)}"

# create sqlite DB & tables if using sqlite
if [[ "${DATABASE_URL:-}" == sqlite:* ]]; then
  echo "Ensuring sqlite DB & tables exist..."
  python - <<'PY'
from db.session import engine, Base
from db import models
Base.metadata.create_all(bind=engine)
print("✅ DB tables created (or already existed).")
PY
fi

echo "Starting web dashboard (uvicorn) on http://127.0.0.1:8000"
uvicorn web.main:app --reload --port 8000
