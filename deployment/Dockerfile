# ---------- builder ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# копируем только зависимости (кешируется)
COPY pyproject.toml .

RUN pip install --upgrade pip

# ⚠️ ВАЖНО: сначала устанавливаем deps
RUN pip install --prefix=/install .

# ---------- runtime ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd -m appuser

WORKDIR /app

# копируем установленный site-packages
COPY --from=builder /install /usr/local

COPY . .

USER appuser

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["bash", "deployment/entrypoints/app.sh"]
