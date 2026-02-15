# Model Context Protocol (MCP) Overview

---
title: CORTEX MCP Gateway Architecture
type: explanation
audience: [Product Owners, Software Developers, Architects]
word_count: 1800
last_verified: 2026-02-15
source_of_truth: cortex/mcp/ + deployment/mcp-gateway-config.yaml
format: diátaxis-explanation
voice: third-person-blended
related_diagrams: [c4-container.md, mcp-request-lifecycle.md]
protocol_version: 2.0.0
transport_modes: [stdio, http]
---

> **Notice:** MCP capabilities represent system design intentions. Actual protocol performance, tool discovery reliability, and transport latency depend on network conditions, IDE configuration, client implementation, and concurrent request patterns. Organizations should validate MCP integration with their specific development environments.

---

## Overview: Pylance-Style Local Architecture

Organizations benefit from understanding CORTEX's MCP architecture, which operates locally within VS Code similar to the Pylance language server [Business Leaders]. Product teams leverage MCP's JSON-RPC 2.0 protocol for seamless integration with multiple IDE clients (VS Code, Cursor, Claude Desktop) without manual server management [Product Owners]. The MCP Gateway auto-starts when Copilot Chat invokes cortex_* tools, providing 10 core MCP tools that expose 20+ orchestrator capabilities through standardized interfaces [Software Developers].

**Key Architectural Principles:**

1. **Auto-Start Architecture** — VS Code launches MCP server automatically when cortex_* tools invoked, no manual `python -m cortex.mcp.server` required. Similar to Pylance Python language server auto-start behavior.

2. **Stdio Transport (Development)** — JSON-RPC 2.0 messages over standard input/output for local IDE integration. Zero network overhead, sub-5ms gateway validation latency, simplified debugging with `--verbose` flag.

3. **HTTP Transport (Production - Phase 11)** — RESTful JSON-RPC endpoint at `http://localhost:9000/mcp` for multi-client scenarios, load balancing, and horizontal scaling. Nginx reverse proxy with rate limiting and authentication.

4. **Native Tool Gate (CORE-049)** — Enforces MCP-first architecture by blocking direct file operations for IMPLEMENT/FIX/REFACTOR intents. Validates intent classification before dispatch to prevent governance bypass.

**MCP Tools (10 Core):**
- `cortex_process_request` — Main workflow processing (IMPLEMENT/FIX/REFACTOR)
- `cortex_lens_analyze` — Unified code intelligence (ANALYZE)
- `cortex_plan_setup/resolve/sync` — Phase lifecycle management (PLAN)
- `cortex_challenge` — Challenge generation (DESIGN)
- `cortex_audit` — Health scans (AUDIT)
- `cortex_digest_session` — Learning extraction (DIGEST)
- `cortex_total_recall` — Feature discovery
- `cortex_git_history` — 24h context retrieval
- `cortex_detect_duplicates` — CORE-035 violation detection
- `cortex_onboard_repository` — Repository initialization + security scan

### Key Benefits

| Benefit | Description | Brain Analogy |
|---------|-------------|---------------|
| **Universal Compatibility** | Works with GitHub Copilot, Claude, Cursor, and any MCP client | Like how any sensory organ can send signals through the same nervous system |
| **Standardized Interface** | JSON-RPC 2.0 protocol ensures consistency | Like the electrochemical standard of nerve impulses |
| **Tool Discovery** | Clients can discover all 26 consolidated tools (90+ operations) dynamically | Like proprioception — knowing what capabilities are available |
| **Type Safety** | Structured arguments with JSON Schema validation | Like neurotransmitter lock-and-key specificity |
| **Scalability** | Support stdio (development) and HTTP (production) | Like the peripheral vs central nervous system |

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
│  │  • 26 consolidated tools (90+ operations)         │   │
│  │  • Dynamic discovery                             │   │
│  │  • Schema validation                             │   │
│  │  • Handler routing                               │   │
│  └───────────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────┐   │
│  │              Tool Handlers                         │   │
│  │  • cortex_process_request → MasterOrchestrator   │   │
│  │  • cortex_lens → LENSSynthesis (5 operations)    │   │
│  │  • cortex_challenge → ChallengeEngine            │   │
│  │  • ... 23 more tools                             │   │
│  └───────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
                      │
┌─────────────────────┼─────────────────────────────────────┐
│         CORTEX ORCHESTRATION LAYER                        │
│              (21 orchestrators: 14 active + 4 super + 7 deprecated)  │
└───────────────────────────────────────────────────────────┘
```

---

## Pylance-Style Architecture (Current)

### Key Insight: Zero Manual Server Startup

**CORTEX MCP works like Pylance** — the Python language server in VS Code. Just as Pylance automatically starts when you open a Python file (no `python -m pylance` command needed), CORTEX MCP automatically starts when you invoke a CORTEX tool in VS Code Copilot Chat.

This is a fundamental shift from traditional "start the server first" architectures to a **just-in-time, transparent activation** model.

### How Auto-Start Works

```
┌────────────────────────────────────────────────────────────────────┐
│                    PYLANCE-STYLE MCP FLOW                         │
│                                                                    │
│  1. User opens VS Code + Copilot Chat                             │
│     └─→ .vscode/settings.json defines MCP servers                │
│                                                                    │
│  2. User types: "analyze cortex/mcp/server.py"                    │
│     └─→ Copilot detects cortex_* tool invocation                 │
│                                                                    │
│  3. VS Code auto-launches MCP server (if not running)             │
│     └─→ python -m cortex.mcp (stdio transport)                   │
│     └─→ Server starts in <500ms                                  │
│                                                                    │
│  4. Copilot sends JSON-RPC request                                │
│     └─→ cortex_lens_analyze(file_path="cortex/mcp/server.py")    │
│                                                                    │
│  5. CORTEX processes, returns response                            │
│     └─→ Server stays alive for subsequent requests               │
│                                                                    │
│  6. Server auto-terminates on VS Code close (graceful shutdown)   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Detection Methods (3-Tier Cascade)

When CORTEX needs to verify MCP availability, it uses a 3-tier cascade:

| Tier | Method | Check | Speed | Reliability |
|------|--------|-------|-------|-------------|
| **1** | Environment Variables | `MCP_SERVER_URL`, `CORTEX_MCP_ENABLED` | <1ms | High |
| **2** | Settings File | `.vscode/settings.json` configured | <10ms | High |
| **3** | Network Probe | `localhost:9000` health check | <100ms | Definitive |

**Detection Flow:**
```python
def detect_mcp_availability():
    # Tier 1: Environment
    if os.getenv("CORTEX_MCP_ENABLED") == "true":
        return True
    
    # Tier 2: Settings file
    if Path(".vscode/settings.json").exists():
        settings = json.load(open(".vscode/settings.json"))
        if "cortex" in settings.get("mcpServers", {}):
            return True
    
    # Tier 3: Network probe
    try:
        response = requests.get("http://localhost:9000/health", timeout=0.1)
        return response.status_code == 200
    except:
        return False
```

### Cross-Platform Python Path Resolution

**Critical:** `.vscode/settings.json` must use platform-specific Python paths:

| Platform | Python Path | Virtual Env |
|----------|-------------|-------------|
| **Windows** | `.venv\Scripts\python.exe` | `.venv\Scripts\activate.ps1` |
| **macOS/Linux** | `.venv/bin/python` | `.venv/bin/activate` |

**Auto-Generated by `setup-mcp.py`:**
```python
# setup-mcp.py generates correct path for current platform
import sys
from pathlib import Path

venv_path = Path(".venv")
if sys.platform == "win32":
    python_path = str(venv_path / "Scripts" / "python.exe")
else:
    python_path = str(venv_path / "bin" / "python")

# Writes to .vscode/settings.json
settings = {
    "mcpServers": {
        "cortex": {
            "command": python_path,
            "args": ["-m", "cortex.mcp"]
        }
    }
}
```

**CORE-051 Enforcement:** `.vscode/settings.json` MUST NOT be committed to git (contains platform-specific paths). The `.githooks/post-checkout` hook auto-regenerates it via `setup-mcp.py`.

### Troubleshooting MCP Detection Failures

**Common Issues & Fixes:**

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing settings.json | "MCP tools not available" | `python .cortex/setup-mcp.py` |
| Wrong Python path | Server fails to start | Re-run `setup-mcp.py` on correct platform |
| Deps not installed | Import errors in server | `pip install -r requirements.txt` |
| Port conflict | "Address already in use" | Kill existing process on 9000 |
| VS Code cache | Tools not appearing | Reload Window (Cmd+Shift+P) |

### Benefits Over Traditional Architecture

| Aspect | Traditional (Manual Start) | Pylance-Style (Auto-Start) |
|--------|---------------------------|---------------------------|
| **Setup Friction** | High (remember to start server) | Zero (automatic) |
| **Developer UX** | "Why isn't this working?" | Just works™ |
| **Resource Usage** | Server always running | On-demand lifecycle |
| **Error Recovery** | Manual restart | Auto-restart on crash |
| **Cross-Platform** | Manual path config | Auto-detected |

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
  "tools_registered": 24,
  "total_operations": 86,
  "orchestrators_loaded": 17
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

**Last Updated:** 2026-02-13
**MCP Specification:** https://modelcontextprotocol.io
**CORTEX MCP Version:** 2.0.0

---

## See Also

**MCP Documentation:**
- [Tools Catalog](./tools-catalog.md) — All 26 consolidated tools with 90+ operations
- [MCP Protocol](./protocol.md) — JSON-RPC 2.0 specification details
- [MCP Integration](./integration.md) — VS Code, Claude, Cursor setup
- [MCP Versioning](./versioning.md) — Version management strategy

**Orchestration:**
- [Orchestration Overview](../orchestration/overview.md) — The 21 orchestrators (14 active + 4 super + 7 deprecated)
- [Master Orchestrator](../orchestration/master-orchestrator.md) — Primary entry point
- [End-to-End Flow](../orchestration/end-to-end-flow.md) — Complete request lifecycle

**Architecture:**
- [Architecture Index](../index.md) — Full documentation navigation
- [CORTEX Glossary](../glossary.md) — Term definitions (MCP, Pylance-Style, etc.)
- [Governance Compliance](../capabilities/governance-compliance.md) — Enforcement layer
**CORTEX MCP Version:** 2.0.0
