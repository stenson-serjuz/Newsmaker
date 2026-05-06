# ---------- builder ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# system deps for building wheels (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# copy only dependency manifests first (better caching)
COPY pyproject.toml ./
# optional: if you have a lock file, copy it as well
# COPY requirements.lock ./

# build wheels into a local wheelhouse (deterministic)
RUN python -m pip install --upgrade pip wheel setuptools \
    && pip wheel --wheel-dir /wheels .

# ---------- runtime ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# create non-root user
RUN useradd -m -u 10001 appuser

WORKDIR /app

# runtime system deps (keep minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl tini \
    && rm -rf /var/lib/apt/lists/*

# copy wheels and install into venv
COPY --from=builder /wheels /wheels

RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

ENV PATH="/opt/venv/bin:$PATH"

# copy app source
COPY . .

# permissions
RUN chown -R appuser:appuser /app /opt/venv
USER appuser

# tini for signal forwarding
ENTRYPOINT ["/usr/bin/tini", "--"]

# default command (can be overridden per role)
CMD ["bash", "deployment/entrypoints/app.sh"]
