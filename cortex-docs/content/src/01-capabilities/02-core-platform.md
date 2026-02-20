# Core Platform Capabilities

---
title: CORTEX Core Platform - Foundation Infrastructure
type: explanation
audience: [Software Developers, Architects, Product Owners]
word_count: 2203
last_verified: 2026-02-15
source_of_truth: cortex/api/ + cortex/core/ + cortex/config/ + cortex/observability/
format: diátaxis-explanation
voice: third-person-neutral
feature: Production ()
diagrams: ASCII service architecture, sequence diagrams
order: 2
---

> **Notice:** Core Platform capabilities represent the foundational infrastructure upon which all CORTEX functionality is built. Organizations may customize configuration and deployment patterns while retaining standardized service interfaces. Performance characteristics reflect production deployment patterns as of .

---

## Executive Summary

The Core Platform provides the foundational infrastructure enabling CORTEX's intelligent development capabilities. Organizations benefit from enterprise-grade service reliability, zero-downtime deployments, and comprehensive observability without custom infrastructure investment [Business Leaders]. Product teams gain consistent request processing, state management, and configuration control across all CORTEX features [Product Owners]. The platform implements service-oriented architecture with MCP Gateway, Tool Registry, State Management, Configuration Management, and Health Monitoring [Software Developers].

**Core Platform Components:**
- **MCP Gateway** — Single entry point implementing Model Context Protocol (JSON-RPC 2.0)
- **Service Router** — Intent-based routing to 20+ specialized orchestrators
- **Tool Registry** — 10 MCP tools exposing 90+ operations with hot-reload capability
- **State Management** — Operation tracking, checkpoint recovery, rollback support
- **Configuration Management** — Layered config with env vars > files > wiring > defaults
- **Health Monitoring** — Circuit breakers, health checks, Prometheus metrics integration

**Performance Targets:** Gateway latency P50: 5ms, P95: 15ms, P99: 25ms. Tool discovery <50ms. Health checks <100ms. State lookup <5ms.

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

The Core Platform capabilities provide the foundation upon which all CORTEX functionality is built. Organizations deploy CORTEX as a coordinated system of services handling request reception, service coordination, state management, configuration, and health monitoring without requiring custom infrastructure development [Business Leaders].

**Platform Responsibilities:**

**Request Reception** — Accepting and validating incoming MCP requests (JSON-RPC 2.0)
- **Protocol Validation:** JSON-RPC 2.0 schema validation (5-10ms)
- **Authentication:** API key validation Iteration 11 (JWT tokens)
- **Rate Limiting:** 60 requests/minute default (configurable)
- **Request Parsing:** Parameter extraction and type checking

**Service Coordination** — Routing requests to appropriate handlers
- **Intent Classification:** LENS-based routing (20-40ms)
- **Load Balancing:** Round-robin across orchestrator instances
- **Circuit Breaking:** Fault isolation for failing services
- **Request Queuing:** Async processing for long operations

**State Management** — Tracking operation progress and recovery
- **In-Memory State:** Fast access for short operations (<30s)
- **Persistent State:** SQLite storage for long operations (>30s)
- **Checkpoint System:** Recovery points for multi-step workflows
- **Audit Trail:** AC markers + timestamps + orchestrator decisions

**Configuration** — Managing runtime settings and feature flags
- **Layered Config:** env vars > files > wiring > defaults
- **Hot Reload:** Configuration changes without service restart
- **Feature Flags:** Runtime capability toggling
- **Secrets Management:** Environment variable isolation

**Health Monitoring** — Ensuring system reliability and availability
- **Health Endpoints:** `/health`, `/health/wiring`, `/health/orchestrators`
- **Circuit Breakers:** Automatic fault isolation (3 failures → OPEN)
- **Prometheus Metrics:** Request count, latency histograms, error rates
- **Grafana Dashboards:** Real-time visualization (Iteration 11)

**Architecture Principles:**
1. **Stateless Processing** — No session affinity required (horizontal scaling)
2. **Container-First** — Docker-native design (Iteration 11)
3. **Zero Database Runtime** — Git-backed config eliminates PostgreSQL/MongoDB
4. **Dual Transport** — stdio (dev) + HTTP (prod Iteration 11)
5. **Observability-First** — OpenTelemetry tracing built-in

---

## Service-Oriented Architecture

### Architecture Pattern

CORTEX implements a service-oriented architecture (SOA) where each orchestrator operates as an independent service. Organizations benefit from independent scaling, fault isolation, and zero-downtime deployments without monolithic dependencies [Business Leaders]. Product teams gain flexibility to update individual orchestrators without full system redeployments [Product Owners]. Each orchestrator exposes capabilities via standardized MCP tools with hot-reload support [Software Developers].

```
┌────────────────────────────────────────────────────────────────┐
│                        MCP GATEWAY (PORT 8000)                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Service Router                         │ │
│  │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │ │
│  │   │  Auth   │  │  Rate   │  │ Health  │  │  Load   │   │ │
│  │   │ Checker │  │ Limiter │  │ Monitor │  │Balancer │   │ │
│  │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │ │
│  │  (JWT Iteration 11) (60/min)    (Circuit Break)  (RoundRobin)│ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │  TDD    │          │  LENS   │          │  Plan   │
   │Orchestr.│          │Synthesis│          │Orchestr.│
   │(Replica)│          │(Replica)│          │(Replica)│
   └─────────┘          └─────────┘          └─────────┘
   Wiring          Wiring            Wiring 
   Hot-Reload OK       Hot-Reload OK         Hot-Reload OK
```

### Key Benefits

| Benefit | Description | Impact |
|---------|-------------|--------|
| **Independent Scaling** | Each orchestrator scales based on its load | Cost optimization: scale TDD 3x, LENS 2x, others 1x |
| **Fault Isolation** | Failures don't cascade across services | Circuit breaker prevents cascade (3 failures → OPEN for 30s) |
| **Independent Deployment** | Update one service without affecting others | Zero-downtime: update wiring contracts, reload within 1 request cycle |
| **Technology Flexibility** | Services can use different technologies | Python core + TypeScript extensions + C# analyzers supported |
| **Resource Efficiency** | Right-size compute per service | TDD needs 2GB RAM, LENS needs 4GB (AST cache), Plan needs 512MB |

### Orchestrator Categories (20+ Total)

| Category | Count | Purpose | Examples | Resource Profile |
|----------|-------|---------|----------|------------------|
| **Core** | 8 | Central coordination | MasterOrchestrator (pre-flight), IntentRouter (LENS classification), TDDOrchestrator (RED-GREEN-REFACTOR), EnforcementOrchestrator (7 agents) | CPU-intensive (validation cycles) |
| **Domain** | 6 | Domain-specific logic | RefactoringOrchestrator (code improvement), PlanningOrchestrator (feature lifecycle), ConversationOrchestrator (multi-turn) | Memory-intensive (context storage) |
| **Support** | 6+ | Support functions | OnboardingOrchestrator (repo scanning), ToolDiscoveryOrchestrator (capability mapping), RecommendationGate (REJ-* validation) | I/O-intensive (git operations) |

**Wiring Discovery:** Orchestrators auto-discovered via `cortex-registry/master/__wiring_contract__.yaml` on startup (200-400ms). Hot-reload detects file changes and reloads affected orchestrators within 1 request cycle (no service restart required).

**Service Communication:** Event-driven messaging via internal event bus (Iteration 11). Current implementation uses direct Python imports with async/await (zero network latency).

---

## MCP Gateway

### Purpose

The MCP Gateway serves as the single entry point for all AI assistant interactions (VS Code Copilot, Claude Desktop, Cursor). Organizations benefit from standardized protocol implementation reducing integration complexity [Business Leaders]. Product teams gain consistent request validation, authentication, and routing without custom gateway development [Product Owners]. The gateway implements JSON-RPC 2.0 over stdio (development) and HTTP (production Iteration 11) with <10ms latency overhead [Software Developers].

### Protocol Details

**Protocol:** JSON-RPC 2.0 (specification-compliant)  
**Transport (Current):** stdio (stdin/stdout) with <5ms latency  
**Transport (Iteration 11):** HTTP/HTTPS with Nginx reverse proxy  
**Default Port:** 8000 (production), N/A (stdio development)  
**Authentication:** API Key via `X-CORTEX-API-KEY` header (Iteration 11), none required (stdio)  
**Rate Limiting:** 60 requests/minute default (configurable via env vars)

**Why stdio First?** Zero network latency (local process communication), simplified debugging (stderr for logs), no port conflicts, auto-started by VS Code (Pylance-style architecture).

**Why HTTP for Production?** Horizontal scaling via Nginx load balancer, standard web authentication (JWT tokens), CORS support for web clients, network-level rate limiting, SSL/TLS termination.

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "cortex_process_request",
    "arguments": {
      "operation": "implement",
      "target": "src/payment_service.py",
      "request": "Add Stripe payment integration with webhook support",
      "mode": "TDD"
    }
  },
  "id": "req-12345"
}
```

**Required Fields:**
- `jsonrpc`: Must be "2.0" (spec compliance)
- `method`: Always "tools/call" for MCP invocations
- `params.name`: One of 10 MCP tool names
- `params.arguments`: Tool-specific parameters (validated against schema)
- `id`: Unique request identifier for response correlation

### Response Format

**Success Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "completed",
    "files_modified": ["src/payment_service.py", "tests/test_payment_service.py"],
    "tests_passed": "18/18",
    "coverage": "92%",
    "duration_ms": 1850,
    "audit_trail": "AC_COMPLETE: AC-IMPLEMENT-042"
  },
  "id": "req-12345"
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "field": "target",
      "issue": "File not found: src/payment_service.py",
      "suggestion": "Run `cortex_lens_analyze` to discover existing files"
    }
  },
  "id": "req-12345"
}
```

**JSON-RPC Error Codes:**
- `-32700`: Parse error (invalid JSON)
- `-32600`: Invalid request (missing required fields)
- `-32601`: Method not found (unknown tool name)
- `-32602`: Invalid params (validation failed)
- `-32603`: Internal error (orchestrator exception)

### Gateway Performance

| Operation | Latency Target | Measured P50 | Measured P95 | Measured P99 |
|-----------|---------------|--------------|--------------|--------------|
| Request Validation | <10ms | 5ms | 12ms | 18ms |
| Tool Routing | <5ms | 2ms | 8ms | 15ms |
| Response Serialization | <5ms | 3ms | 7ms | 12ms |
| Total Gateway Overhead | <15ms | 10ms | 20ms | 30ms |

**Note:** Total request latency includes gateway overhead + orchestrator processing time (500-2000ms for TDD workflows) + tool execution time (varies by operation).

### Health Check

**Endpoint:** `/health` (HTTP) or special stdin message `{"method": "health"}` (stdio)

**Response:**
```json
{
  "status": "healthy",
  "version": "8.1",
  "transport": "stdio",
  "orchestrators": 20,
  "tools": 10,
  "uptime_seconds": 86400,
  "cache_hit_rate": 0.75
}
```

---
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
| `/04-mcp/tools` | GET | List available tools |
| `/04-mcp/execute` | POST | Execute tool |
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

- [MCP Overview](../04-mcp/01-overview.md) — Protocol details
- [Tool Registry](../06-toolkit/tool-registry.md) — Tool management
- [Infrastructure Overview](../05-infrastructure/01-overview.md) — Deployment details
- [Observability](../05-infrastructure/observability.md) — Monitoring details

---

*Part of CORTEX Architecture Documentation*
