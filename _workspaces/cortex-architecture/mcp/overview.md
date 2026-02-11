# Model Context Protocol (MCP) Overview

**Version:** 2.0.0 | **Updated:** 2026-02-11  
**Protocol:** JSON-RPC 2.0 | **Transport:** stdio / HTTP  
**Tools Exposed:** 86

---

## What is MCP?

The **Model Context Protocol (MCP)** is an open protocol that standardizes how AI assistants interact with external tools and services. CORTEX implements MCP to expose its cognitive capabilities to any MCP-compatible client.

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Universal Compatibility** | Works with GitHub Copilot, Claude, Cursor, and any MCP client |
| **Standardized Interface** | JSON-RPC 2.0 protocol ensures consistency |
| **Tool Discovery** | Clients can discover all 86 available tools dynamically |
| **Type Safety** | Structured arguments with JSON Schema validation |
| **Scalability** | Support stdio (development) and HTTP (production) |

---

## CORTEX MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP CLIENTS                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Copilot  │  │  Claude  │  │  Cursor  │  │  Custom  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │         │
│       └─────────────┴─────────────┴─────────────┘         │
│                     │ JSON-RPC 2.0                        │
└─────────────────────┼─────────────────────────────────────┘
                      │
┌─────────────────────┼─────────────────────────────────────┐
│              CORTEX MCP SERVER                            │
│  ┌───────────────────────────────────────────────────┐   │
│  │                 Transport Layer                    │   │
│  │  ┌──────────────┐         ┌──────────────┐       │   │
│  │  │ stdio        │         │ HTTP         │       │   │
│  │  │ (dev mode)   │         │ (production) │       │   │
│  │  │ stdin/stdout │         │ Port 8000    │       │   │
│  │  └──────────────┘         └──────────────┘       │   │
│  └───────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────┐   │
│  │              Protocol Handler                      │   │
│  │  • JSON-RPC 2.0 parser                           │   │
│  │  • Request validation                            │   │
│  │  • Response serialization                        │   │
│  │  • Error handling                                │   │
│  └───────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────┐   │
│  │              Tool Registry                         │   │
│  │  • 86 tools registered         │   │
│  │  • Dynamic discovery                             │   │
│  │  • Schema validation                             │   │
│  │  • Handler routing                               │   │
│  └───────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────┐   │
│  │              Tool Handlers                         │   │
│  │  • cortex_process_request → MasterOrchestrator   │   │
│  │  • cortex_lens_analyze → LENSSynthesis          │   │
│  │  • cortex_challenge → ChallengeEngine            │   │
│  │  • ... 83 more tools                    │   │
│  └───────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┼─────────────────────────────────────┐
│         CORTEX ORCHESTRATION LAYER                        │
│              (60 orchestrators)              │
└───────────────────────────────────────────────────────────┘
```

---

## MCP Protocol Flow

### Tool Discovery

```json
// CLIENT REQUEST
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}

// SERVER RESPONSE
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "cortex_process_request",
        "description": "Primary entry point for CORTEX request processing",
        "inputSchema": {
          "type": "object",
          "properties": {
            "request": {"type": "string"},
            "enable_challenge": {"type": "boolean"}
          },
          "required": ["request"]
        }
      },
      // ... 85 more tools
    ]
  },
  "id": 1
}
```

### Tool Invocation

```json
// CLIENT REQUEST
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_lens_analyze",
    "arguments": {
      "target": "src/auth/",
      "analysis_type": "security"
    }
  },
  "id": 2
}

// SERVER RESPONSE
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Security Analysis Results:\n✅ No hardcoded secrets\n..."
      }
    ]
  },
  "id": 2
}
```

---

## Configuration

### VS Code (GitHub Copilot)

**File:** `.vscode/mcp.json`

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp"],
      "env": {
        "CORTEX_MODE": "production",
        "CORTEX_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Claude Desktop

**File:** `~/.config/claude-desktop/mcp.json` (Linux/Mac)  
**File:** `%APPDATA%\Claude\mcp.json` (Windows)

```json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "cortex.mcp"],
      "cwd": "/path/to/CORTEX"
    }
  }
}
```

### Cursor IDE

**File:** `.cursor/mcp.json`

```json
{
  "servers": {
    "cortex": {
      "transport": "stdio",
      "command": ["python", "-m", "cortex.mcp"],
      "autoStart": true
    }
  }
}
```

---

## Production Deployment

### HTTP Mode (Recommended for Production)

```bash
# Start MCP server in HTTP mode
python -m cortex.mcp --transport http --port 8000

# With SSL (production)
python -m cortex.mcp --transport http --port 8000   --cert /path/to/cert.pem   --key /path/to/key.pem
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "cortex.mcp", "--transport", "http", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cortex-mcp
  template:
    metadata:
      labels:
        app: cortex-mcp
    spec:
      containers:
      - name: cortex-mcp
        image: cortex:latest
        ports:
        - containerPort: 8000
        env:
        - name: CORTEX_MODE
          value: "production"
---
apiVersion: v1
kind: Service
metadata:
  name: cortex-mcp-service
spec:
  selector:
    app: cortex-mcp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Monitoring & Observability

### Health Checks

```bash
# Check server health
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "tools_registered": 86,
  "orchestrators_loaded": 60
}
```

### Prometheus Metrics

```
# HELP cortex_mcp_requests_total Total MCP requests processed
# TYPE cortex_mcp_requests_total counter
cortex_mcp_requests_total{tool="cortex_process_request"} 1247

# HELP cortex_mcp_request_duration_seconds Request duration in seconds
# TYPE cortex_mcp_request_duration_seconds histogram
cortex_mcp_request_duration_seconds_bucket{le="0.1"} 342
cortex_mcp_request_duration_seconds_bucket{le="0.5"} 891
cortex_mcp_request_duration_seconds_bucket{le="1.0"} 1156
cortex_mcp_request_duration_seconds_bucket{le="5.0"} 1247
```

---

## Security

### Authentication

```python
# Enable API key authentication
export CORTEX_API_KEY="your-secret-key"

# Client must include in headers
{"Authorization": "Bearer your-secret-key"}
```

### Rate Limiting

```python
# Configure in cortex/mcp/config.py
RATE_LIMIT = {
    "requests_per_minute": 60,
    "burst": 10
}
```

### HTTPS/TLS

```bash
# Generate self-signed cert (development)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Start with TLS
python -m cortex.mcp --transport http --port 8000   --cert cert.pem --key key.pem
```

---

## Performance Tuning

| Parameter | Default | Tuning |
|-----------|---------|--------|
| **Max Concurrent Requests** | 50 | Increase for high load |
| **Request Timeout** | 30s | Increase for long operations |
| **Tool Cache TTL** | 300s | Adjust based on tool stability |
| **Max Response Size** | 10MB | Limit to prevent memory issues |

---

**Last Updated:** 2026-02-11 06:41:25  
**MCP Specification:** https://modelcontextprotocol.io  
**CORTEX MCP Version:** 2.0.0
