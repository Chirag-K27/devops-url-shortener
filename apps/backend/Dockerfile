# ── Stage 1: Builder ────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production ────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
