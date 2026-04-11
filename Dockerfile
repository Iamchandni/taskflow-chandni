# ============================================================
# Dockerfile — Multi-stage build for TaskFlow API
# ============================================================
# Stage 1 (builder): Install Python dependencies
# Stage 2 (runtime): Minimal image with only what's needed to run
# ============================================================

# ── Stage 1: Builder ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only runtime dependencies (libpq for asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x scripts/start.sh

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["scripts/start.sh"]
