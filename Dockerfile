# CORTEX — Multi-stage production Dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Runtime image
FROM python:3.13-slim AS runtime

LABEL maintainer="Asif Hussain <asif@cortex.dev>"
LABEL org.opencontainers.image.title="CORTEX"
LABEL org.opencontainers.image.description="CORTEX AI Engineering Framework — MCP Server"
LABEL org.opencontainers.image.version="14.0.0"
LABEL org.opencontainers.image.source="https://github.com/asifhussain60/CORTEX"

WORKDIR /app

# Non-root user for security
RUN groupadd --gid 1001 cortex \
    && useradd --uid 1001 --gid cortex --shell /bin/bash --create-home cortex

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=cortex:cortex cortex/ ./cortex/
COPY --chown=cortex:cortex cortex-registry/ ./cortex-registry/
COPY --chown=cortex:cortex pyproject.toml ./
COPY --chown=cortex:cortex requirements.txt ./

# Runtime directories with correct ownership
RUN mkdir -p .cortex-runtime/traces .cortex-runtime/logs \
    && chown -R cortex:cortex .cortex-runtime/

USER cortex

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CORTEX_ENV=production \
    CORTEX_SKIP_PREFLIGHT=false

# Health check — verifies MCP server imports cleanly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import cortex; print(cortex.__version__)" || exit 1

# MCP stdio transport (no port — stdin/stdout for VS Code Copilot)
CMD ["python3", "-m", "cortex.mcp"]
