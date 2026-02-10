FROM python:3.11-alpine AS builder
WORKDIR /app/build
RUN apk add --no-cache gcc musl-dev linux-headers git
COPY deployment/requirements.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-alpine
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 CORTEX_ENV=production CORTEX_MCP_PORT=8443
WORKDIR /app
RUN addgroup -g 1000 cortex && adduser -D -u 1000 -G cortex cortex && \
    apk add --no-cache curl ca-certificates tzdata
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache /app/wheels/* && rm -rf /app/wheels
COPY cortex /app/cortex
COPY cortex_brain /app/cortex_brain
COPY deployment /app/deployment
RUN mkdir -p /app/.cortex/logs /app/.cortex/state /app/metrics && \
    chown -R cortex:cortex /app
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8443/health || exit 1
USER cortex
EXPOSE 8443
CMD ["python", "-m", "cortex.mcp.server"]
