# Core Platform Capabilities

**Purpose:** Detailed documentation of CORTEX foundation capabilities  
**Audience:** Architects, Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Service-Oriented Architecture](#service-oriented-architecture)
- [MCP Gateway](#mcp-gateway)
- [Tool Registry](#tool-registry)
- [State Management](#state-management)
- [Configuration Management](#configuration-management)
- [Health Monitoring](#health-monitoring)
- [Related Documents](#related-documents)

---

## Overview

The Core Platform capabilities provide the foundation upon which all CORTEX functionality is built. These capabilities handle:

- **Request Reception** — Accepting and validating incoming requests
- **Service Coordination** — Routing requests to appropriate handlers
- **State Management** — Tracking operation progress and recovery
- **Configuration** — Managing runtime settings and feature flags
- **Health Monitoring** — Ensuring system reliability and availability

---

## Service-Oriented Architecture

### Architecture Pattern

CORTEX implements a service-oriented architecture (SOA) where each orchestrator operates as an independent service:

```
┌────────────────────────────────────────────────────────────────┐
│                        MCP GATEWAY                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Service Router                         │ │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │ │
│  │   │  Auth   │  │  Rate   │  │ Health  │  │  Load   │   │ │
│  │   │ Checker │  │ Limiter │  │ Monitor │  │Balancer │   │ │
│  │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │ Service │          │ Service │          │ Service │
   │    A    │          │    B    │          │    C    │
   │(Replica)│          │(Replica)│          │(Replica)│
   └─────────┘          └─────────┘          └─────────┘
```

### Key Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Independent Scaling** | Each orchestrator scales based on its load | Cost optimization |
| **Fault Isolation** | Failures don't cascade across services | High availability |
| **Independent Deployment** | Update one service without affecting others | Zero-downtime updates |
| **Technology Flexibility** | Services can use different technologies | Best tool for job |

### Orchestrator Categories

| Category | Count | Purpose | Examples |
|----------|-------|---------|----------|
| **Core** | 8 | Central coordination | MasterOrchestrator, IntentRouter, TDDOrchestrator |
| **Domain** | 6 | Domain-specific logic | RefactoringOrchestrator, PlanningOrchestrator |
| **Support** | 9 | Auxiliary functions | OnboardingOrchestrator, ToolDiscoveryOrchestrator |
| **Infrastructure** | 3 | System operations | DatabaseBackedRegistry, HealthChecker |

---

## MCP Gateway

### Purpose

The MCP Gateway serves as the single entry point for all client interactions, implementing the Model Context Protocol (MCP) specification.

### Protocol Details

**Protocol:** JSON-RPC 2.0  
**Transport:** HTTP/HTTPS  
**Default Port:** 8000  
**Authentication:** API Key (X-CORTEX-API-KEY header)

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_process_request",
    "arguments": {
      "user_request": "Implement user authentication",
      "context": {}
    }
  },
  "id": "req-12345"
}
```

### Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "type": "execution",
    "result": {
      "orchestrator": "TDDOrchestrator",
      "operation": "implement",
      "artifacts": ["tests/test_auth.py", "src/auth.py"]
    }
  },
  "id": "req-12345"
}
```

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/mcp/tools` | GET | List available tools |
| `/mcp/execute` | POST | Execute tool |
| `/metrics` | GET | Prometheus metrics |

### Rate Limiting

| Client Type | Requests/Minute | Burst |
|-------------|-----------------|-------|
| Standard | 60 | 10 |
| Premium | 120 | 20 |
| Enterprise | Unlimited | 100 |

---

## Tool Registry

### Purpose

The Tool Registry provides centralized management of all MCP tools with discovery, validation, and governance capabilities.

### Tool Registration

```python
from cortex.mcp.tool_registry import ToolRegistry, ToolMetadata, ToolCategory

registry = get_mcp_tool_registry()

metadata = ToolMetadata(
    id="my_custom_tool",
    name="My Custom Tool",
    category=ToolCategory.UTILITY,
    description="Performs custom operation",
    parameters={
        "input": {"type": "string", "required": True},
        "options": {"type": "object", "required": False}
    },
    auth_required=True,
    version="1.0.0"
)

registry.register(metadata)
```

### Tool Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| **GOVERNANCE** | Rules enforcement, compliance | cortex_audit, cortex_validate |
| **ORCHESTRATION** | Workflow management | cortex_process_request, cortex_challenge |
| **KNOWLEDGE** | Information retrieval | cortex_total_recall, cortex_lens_analyze |
| **UTILITY** | General helpers | cortex_git_history, cortex_detect_duplicates |

### Discovery API

```python
# List all tools
tools = registry.list_all()

# Filter by category
governance_tools = registry.by_category(ToolCategory.GOVERNANCE)

# Get tool metadata
metadata = registry.get("cortex_process_request")
```

---

## State Management

### Purpose

State Management tracks operation progress, enables recovery from failures, and supports long-running workflows.

### State Lifecycle

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│  CREATED  │───▶│ EXECUTING │───▶│ COMPLETED │    │  FAILED   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
                       │                                  ▲
                       └──────────────────────────────────┘
                                  (on error)
```

### State Storage

| Storage Type | Use Case | Durability |
|--------------|----------|------------|
| **In-Memory** | Short operations (<30s) | Non-durable |
| **Database** | Long operations (>30s) | Durable |
| **Checkpoint** | Multi-step workflows | Durable + versioned |

### Recovery Patterns

1. **Automatic Retry** — Transient failures retry with exponential backoff
2. **Checkpoint Recovery** — Long operations resume from last checkpoint
3. **Rollback** — Failed operations can trigger compensating actions

---

## Configuration Management

### Configuration Sources

| Source | Priority | Purpose |
|--------|----------|---------|
| **Environment Variables** | 1 (highest) | Secrets, runtime overrides |
| **Config Files** | 2 | Application settings |
| **Wiring Contract** | 3 | Orchestrator definitions |
| **Defaults** | 4 (lowest) | Fallback values |

### Key Configuration Areas

```yaml
# Example configuration structure
cortex:
  server:
    port: 8000
    host: "0.0.0.0"
    workers: 4
    
  mcp:
    version: "2024-11-05"
    auth_required: true
    rate_limit:
      enabled: true
      requests_per_minute: 60
      
  lens:
    cache_ttl: 3600
    max_file_size: 10485760  # 10MB
    
  governance:
    tdd_required: true
    audit_enabled: true
    security_gates: true
```

### Feature Flags

| Flag | Description | Default |
|------|-------------|---------|
| `CORTEX_TDD_ENABLED` | Enforce TDD workflow | true |
| `CORTEX_AUDIT_ENABLED` | Enable audit logging | true |
| `CORTEX_CHALLENGE_ENABLED` | Enable challenge system | true |
| `CORTEX_CACHE_ENABLED` | Enable LENS caching | true |

---

## Health Monitoring

### Health Check Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Overall health | 200 OK or 503 Unhealthy |
| `/health/wiring` | Orchestrator wiring | Wiring status |
| `/health/orchestrators` | Orchestrator status | Per-orchestrator health |

### Health Response Format

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-10T14:30:00Z",
  "components": {
    "mcp_gateway": "healthy",
    "tool_registry": "healthy",
    "lens_cache": "healthy",
    "database": "healthy"
  },
  "metrics": {
    "uptime_seconds": 86400,
    "requests_total": 15000,
    "error_rate": 0.001
  }
}
```

### Circuit Breaker Pattern

CORTEX implements circuit breakers for external dependencies:

| State | Behavior | Transition |
|-------|----------|------------|
| **CLOSED** | Normal operation | 3 failures → OPEN |
| **OPEN** | Fast-fail all requests | 30s timeout → HALF-OPEN |
| **HALF-OPEN** | Allow test request | Success → CLOSED, Failure → OPEN |

---

## Performance Characteristics

| Metric | Target | Measured |
|--------|--------|----------|
| **Gateway Latency** | < 10ms | 5ms (p50) |
| **Tool Discovery** | < 50ms | 20ms |
| **Health Check** | < 100ms | 30ms |
| **State Lookup** | < 5ms | 2ms |

---

## Related Documents

- [MCP Overview](../mcp/overview.md) — Protocol details
- [Tool Registry](../toolkit/tool-registry.md) — Tool management
- [Infrastructure Overview](../infrastructure/overview.md) — Deployment details
- [Observability](../infrastructure/observability.md) — Monitoring details

---

*Part of CORTEX Architecture Documentation*
