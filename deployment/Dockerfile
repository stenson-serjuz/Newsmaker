# --- builder ---
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install --upgrade pip

COPY pyproject.toml .
RUN pip install --no-cache-dir .

# --- runtime ---
FROM python:3.12-slim

RUN useradd -m appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY . .

USER appuser

ENV PYTHONUNBUFFERED=1

CMD ["bash", "deployment/entrypoints/app.sh"]
