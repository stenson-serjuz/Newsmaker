#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] verifying runtime dependencies..."

python - <<'PY'
import asyncpg
import sqlalchemy.ext.asyncio
import redis.asyncio

print("✅ asyncpg OK")
print("✅ sqlalchemy async OK")
print("✅ redis async OK")
PY

echo "[entrypoint] starting app..."

exec python -m app.main
