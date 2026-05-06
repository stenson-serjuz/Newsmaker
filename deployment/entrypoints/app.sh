#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] verifying runtime dependencies..."

python - <<'PY'
import asyncpg
import sqlalchemy.ext.asyncio
import redis.asyncio
print("✅ dependencies OK")
PY

echo "[entrypoint] waiting for dependencies..."

python - <<'PY'
import asyncio, os, asyncpg, redis.asyncio as redis

async def wait():
    pg = os.environ.get("POSTGRES_DSN")
    rd = os.environ.get("REDIS_URL")

    for _ in range(30):
        try:
            if pg:
                conn = await asyncpg.connect(dsn=pg, timeout=2)
                await conn.close()
            if rd:
                r = redis.from_url(rd)
                await r.ping()
                await r.aclose()
            return
        except Exception:
            await asyncio.sleep(1)
    raise RuntimeError("Dependencies not ready")

asyncio.run(wait())
PY

# 🔥 КЛЮЧЕВОЙ FIX
export ALEMBIC_CONFIG=alembic.ini

# --- migrations ---
if [[ "${RUN_MIGRATIONS:-true}" == "true" ]]; then
  echo "[entrypoint] running migrations..."

  # ЯВНО указываем конфиг
  alembic -c alembic.ini upgrade head
fi

echo "[entrypoint] starting app..."

exec python -m app.main
