FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Builder stage ---
FROM base AS builder

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# --- Final stage ---
FROM base AS final

COPY --from=builder /install /usr/local

# Non-root user
RUN groupadd --gid 1001 waygo && useradd --uid 1001 --gid waygo --shell /bin/bash waygo
RUN mkdir -p /app/media && chown -R waygo:waygo /app

COPY --chown=waygo:waygo . .

USER waygo

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--loop", "uvloop", "--http", "httptools"]
