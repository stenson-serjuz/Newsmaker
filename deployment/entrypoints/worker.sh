#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] worker starting..."

# dependency wait
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

exec python -m workers.run
