# =============================================================================
# F1 Data Engineering - Multi-stage Dockerfile with UV
# =============================================================================
# Stage 1: Build stage with UV and dependencies
# Stage 2: Runtime stage for Airflow integration
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder with UV
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY src/ ./src/
COPY dags/ ./dags/

# Install the project itself
RUN uv sync --frozen --no-dev

# -----------------------------------------------------------------------------
# Stage 2: Runtime
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv ./.venv

# Copy application code
COPY --from=builder /app/src ./src
COPY --from=builder /app/dags ./dags

# Create data directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/cache \
    && chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Default command
CMD ["python", "-c", "print('F1 Data Engineering Pipeline Ready')"]
