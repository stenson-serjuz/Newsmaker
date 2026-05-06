# ---------- builder ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_PREFER_BINARY=1

WORKDIR /build

# minimal setup (no heavy toolchain)
RUN pip install --upgrade pip

# dependency layer (cached)
COPY pyproject.toml .

# install dependencies into isolated prefix
RUN pip install --prefix=/install .

# ---------- runtime ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# runtime deps only
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 appuser

WORKDIR /app

# copy installed dependencies
COPY --from=builder /install /usr/local

# copy source AFTER deps (cache-friendly)
COPY . .

RUN chown -R appuser:appuser /app

USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["bash", "deployment/entrypoints/app.sh"]
