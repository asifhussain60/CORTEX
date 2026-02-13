# MCP-First Architecture: Service-Oriented Design

**Authority:** CORTEX Architect v13.1  
**Created:** 2026-02-05  
**Status:** PRODUCTION  
**Related:** ENH-043 (MCP Architecture Documentation Enhancement)

---

## 🎯 Executive Summary

**CORTEX is NOT a monolithic application.** It operates as a **service-oriented architecture** where all functionality is exposed through the Model Context Protocol (MCP) server. Each of the 28 orchestrators functions as an independent service, communicating via MCP JSON-RPC protocol.

**Key Characteristics:**
- ✅ **28 Independent Services:** Each orchestrator is a distinct MCP tool
- ✅ **Protocol-Driven Communication:** MCP JSON-RPC (language-agnostic)
- ✅ **Independent Scaling:** Orchestrators scale horizontally via MCP proxy
- ✅ **Service Isolation:** No direct Python imports between orchestrators
- ✅ **Dynamic Discovery:** Tools register at runtime, enabling hot-reload

---

## 🏗️ Architecture Overview

### Service Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP Server (Port 8000)                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           MCP Gateway (cortex_process_request)          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    │   Intent Router   │                       │
│                    └─────────┬─────────┘                       │
│                              │                                  │
│        ┌────────────────────┼────────────────────┐            │
│        ▼                     ▼                     ▼            │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐        │
│  │  Core    │        │  Domain  │        │ Support  │        │
│  │  (8)     │        │  (6)     │        │  (14)    │        │
│  └──────────┘        └──────────┘        └──────────┘        │
│        │                     │                     │            │
│        └────────────────────┴─────────────────────┘            │
│                              │                                  │
│                    28 Independent Services                      │
└─────────────────────────────────────────────────────────────────┘
```

### Communication Flow

```
Client (GitHub Copilot, Claude Desktop, VS Code)
    │
    │ MCP JSON-RPC Request
    ▼
MCP Server (:8000)
    │
    │ cortex_process_request
    ▼
MasterOrchestrator (Gateway)
    │
    ├─→ InteractionOrchestrator (comprehension)
    ├─→ IntentRouter (classification)
    ├─→ TDDOrchestrator (execution)
    └─→ EnforcementOrchestrator (governance)
         │
         │ MCP Internal Calls
         ▼
    Domain Orchestrators (6)
    Support Orchestrators (14)
```

---

## 📊 Service Catalog

### Core Services (8)

| Service | MCP Tool | Purpose | Tier |
|---------|----------|---------|------|
| **MasterOrchestrator** | `cortex_process_request` | Gateway & coordination | 1 |
| **InteractionOrchestrator** | `cortex_interactive_mode` | User comprehension (LENS) | 1 |
| **IntentRouter** | *(internal)* | Intent classification | 1 |
| **LENSSynthesis** | `cortex_lens_analyze` | LENS synthesis + DoR gate | 1 |
| **EnforcementOrchestrator** | *(internal)* | Governance (7-agent system) | 1 |
| **TDDOrchestrator** | *(internal)* | Test-driven development | 1 |
| **IncrementalTaskDecomposer** | *(internal)* | Task breakdown (10K tokens) | 1 |
| **WorkflowOrchestrator** | *(internal)* | Workflow execution | 1 |

### Domain Services (6)

| Service | MCP Tool | Purpose | Tier |
|---------|----------|---------|------|
| **RefactoringOrchestrator** | `cortex_refactor` | Code improvement | 2 |
| **PlanningOrchestrator** | `cortex_plan` | Phase planning | 2 |
| **DocumentationOrchestrator** | `cortex_document` | Doc generation | 2 |
| **ConversationOrchestrator** | *(internal)* | Context tracking | 2 |
| **CodeLevelPlanner** | *(internal)* | Code-level specs | 2 |
| **CoherenceValidator** | *(internal)* | Cross-layer validation | 2 |

### Support Services (14)

| Service | MCP Tool | Purpose | Tier |
|---------|----------|---------|------|
| **OnboardingOrchestrator** | `cortex_onboard_repository` | Repository onboarding | 3 |
| **ToolDiscoveryOrchestrator** | `cortex_tools_catalog` | Tool discovery | 3 |
| **VacuumOrchestrator** | `cortex_vacuum` | Markdown cleanup | 3 |
| **DebuggingOrchestrator** | `cortex_debug_*` | Smart debugging | 3 |
| **ArchitectureGuard** | `cortex_validate_architecture` | Pre-implementation gate | 3 |
| *(9 more support services)* | *(various tools)* | Various support functions | 3 |

**Total:** 28 independent services

---

## 🆚 Monolithic vs MCP-First Comparison

| Aspect | Monolithic Architecture | MCP-First CORTEX |
|--------|------------------------|------------------|
| **Service Boundaries** | Tightly coupled modules in single process | 28 independent orchestrators as MCP tools |
| **Communication** | Direct function calls (Python imports) | MCP JSON-RPC protocol (language-agnostic) |
| **Scaling** | Vertical (scale entire application) | Horizontal (scale individual orchestrators) |
| **Deployment** | Single monolithic container | Docker Compose (28+ containers) / Kubernetes |
| **Language Binding** | Python-only | Any language (MCP protocol standard) |
| **Service Discovery** | Static imports | Dynamic registration at runtime |
| **Testing** | Difficult (integration tests required) | Easy (unit test each service independently) |
| **Failure Isolation** | Failure affects entire app | Circuit breaker per orchestrator |
| **Versioning** | Single version for entire app | Independent versioning per orchestrator |
| **Observability** | Custom logging per module | Centralized MCP tracing + Prometheus metrics |

---

## 🚀 Scaling Model

### Independent Orchestrator Scaling

Each orchestrator can scale independently based on load:

```yaml
# docker-compose.yml (simplified)
services:
  mcp-server:
    image: cortex-mcp-server
    ports: ["8000:8000"]
    environment:
      MCP_SERVER_HOST: 0.0.0.0
      MCP_SERVER_PORT: 8000
  
  # Scale MasterOrchestrator (high traffic)
  orchestrator-master:
    image: cortex-orchestrator
    replicas: 5  # Scale to 5 instances
    environment:
      ORCHESTRATOR_TYPE: master
      MCP_SERVER_URL: http://mcp-server:8000
  
  # Scale TDDOrchestrator (heavy workload)
  orchestrator-tdd:
    image: cortex-orchestrator
    replicas: 10  # Scale to 10 instances
    environment:
      ORCHESTRATOR_TYPE: tdd
      MCP_SERVER_URL: http://mcp-server:8000
  
  # Scale InteractionOrchestrator (user-facing)
  orchestrator-interaction:
    image: cortex-orchestrator
    replicas: 8  # Scale to 8 instances
    environment:
      ORCHESTRATOR_TYPE: interaction
      MCP_SERVER_URL: http://mcp-server:8000
  
  # ... 25 more orchestrator services
```

### Load Balancing

MCP Server acts as load balancer:
- Round-robin distribution across orchestrator replicas
- Health checks every 30 seconds
- Circuit breaker on 3 consecutive failures
- Automatic removal of unhealthy instances

### Resource Optimization

| Orchestrator | CPU | Memory | Replicas | Load Pattern |
|-------------|-----|--------|----------|--------------|
| MasterOrchestrator | 0.5 | 512MB | 5 | Steady |
| TDDOrchestrator | 1.0 | 1GB | 10 | Burst |
| InteractionOrchestrator | 0.3 | 256MB | 8 | Steady |
| RefactoringOrchestrator | 0.8 | 768MB | 3 | Occasional |
| OnboardingOrchestrator | 1.5 | 2GB | 2 | Infrequent |

**Total Resources:**
- CPU: ~20 cores
- Memory: ~30GB
- Services: 28+ containers

---

## 🔌 MCP Protocol Benefits

### 1. Language Agnostic

Clients can be written in any language:

```typescript
// TypeScript Client
import { MCPClient } from '@modelcontextprotocol/sdk';

const client = new MCPClient('http://localhost:8000');
const result = await client.call('cortex_process_request', {
  user_request: 'implement cache layer',
  context: { target: 'knowledge_repository.py' }
});
```

```python
# Python Client
from mcp import MCPClient

client = MCPClient('http://localhost:8000')
result = client.call('cortex_process_request', {
    'user_request': 'implement cache layer',
    'context': {'target': 'knowledge_repository.py'}
})
```

### 2. Dynamic Discovery

Tools register at runtime:

```python
# Orchestrator auto-discovery
@mcp_tool(
    name="cortex_refactor",
    description="Refactor code for improved quality",
    category="domain",
    authorization_level=AuthLevel.STANDARD
)
def refactor_code(target: str, strategy: str) -> RefactorResult:
    # Implementation
    pass
```

MCP Server discovers all `@mcp_tool` decorators at startup, enabling:
- Hot-reload of orchestrators without server restart
- A/B testing of new orchestrator implementations
- Gradual rollout via feature flags

### 3. Versioning

Each tool can version independently:

```python
@mcp_tool(
    name="cortex_refactor_v2",
    description="Enhanced refactoring with AI",
    version="2.0.0"
)
def refactor_code_v2(target: str, strategy: str, ai_mode: bool) -> RefactorResult:
    # New implementation
    pass
```

Clients can request specific versions:

```json
{
  "tool": "cortex_refactor",
  "version": "2.0.0",
  "parameters": {...}
}
```

### 4. Observability

Centralized tracing via MCP:

```
Request ID: req_abc123
  ├─ cortex_process_request (50ms)
  │   ├─ IntentRouter.classify (20ms)
  │   └─ MasterOrchestrator.coordinate (30ms)
  │       ├─ TDDOrchestrator.generate_tests (150ms)
  │       └─ EnforcementOrchestrator.validate (40ms)
  └─ Total: 240ms
```

Prometheus metrics:
- `cortex_tool_invocations_total{tool="cortex_process_request"}`
- `cortex_tool_duration_seconds{tool="cortex_process_request"}`
- `cortex_tool_errors_total{tool="cortex_process_request"}`

---

## 🏭 Deployment Strategies

### Development (Docker Compose)

```bash
# Start all services
docker-compose up -d

# Scale specific orchestrator
docker-compose up -d --scale orchestrator-tdd=5

# View logs
docker-compose logs -f mcp-server
```

### Production (Kubernetes)

```yaml
# k8s/mcp-server-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cortex-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cortex-mcp-server
  template:
    metadata:
      labels:
        app: cortex-mcp-server
    spec:
      containers:
      - name: mcp-server
        image: cortex-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: MCP_SERVER_PORT
          value: "8000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: cortex-mcp-server
spec:
  selector:
    app: cortex-mcp-server
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

---

## 🔍 Service Isolation

### No Direct Imports

**Anti-Pattern (Monolithic):**
```python
# ❌ WRONG: Direct import creates tight coupling
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

def my_function():
    tdd = TDDOrchestrator()
    result = tdd.generate_tests(...)
```

**MCP-First Pattern:**
```python
# ✅ CORRECT: MCP tool invocation
from cortex.mcp.client import mcp_client

def my_function():
    result = mcp_client.call('cortex_tdd_generate_tests', {
        'target': 'knowledge_repository.py',
        'test_type': 'unit'
    })
```

### Benefits of Service Isolation

1. **Independent Testing:** Each orchestrator tested in isolation
2. **Parallel Development:** Teams work on different orchestrators without conflicts
3. **Failure Isolation:** TDD orchestrator crash doesn't affect Interaction orchestrator
4. **Independent Deployment:** Update TDD orchestrator without redeploying entire system
5. **Technology Flexibility:** Replace Python orchestrator with Rust/Go implementation

---

## 📈 Performance Characteristics

### Latency Breakdown

| Operation | Latency | Notes |
|-----------|---------|-------|
| MCP Server Overhead | 5-10ms | JSON-RPC parsing |
| Tool Discovery | <1ms | Cached registry |
| Intent Routing | 20-50ms | IntentRouter classification |
| Orchestrator Execution | Variable | Depends on operation |
| Total (Simple Request) | 100-200ms | e.g., tool catalog |
| Total (Complex Request) | 1-5s | e.g., TDD workflow |

### Throughput

| Configuration | Requests/Second | Notes |
|--------------|----------------|-------|
| Single Instance | 10-20 | Baseline |
| 3 MCP Server Replicas | 50-80 | Load balanced |
| 5 Orchestrator Replicas | 150-200 | Per orchestrator |
| Fully Scaled (28 services × 5 replicas) | 500+ | Production |

---

## 🛡️ Resilience Patterns

### Circuit Breaker

```python
# MCP Server implements circuit breaker per orchestrator
@circuit_breaker(
    failure_threshold=3,
    recovery_timeout=30,
    fallback=fallback_orchestrator
)
def call_orchestrator(tool_name: str, params: dict):
    # Invoke orchestrator
    pass
```

States:
- **CLOSED:** Normal operation
- **OPEN:** 3 failures → stop calling orchestrator for 30s
- **HALF_OPEN:** After timeout, try 1 request → if success, go to CLOSED

### Health Checks

Each orchestrator exposes health endpoint:

```bash
curl http://localhost:8000/health/orchestrators

{
  "status": "healthy",
  "orchestrators": {
    "MasterOrchestrator": {"status": "healthy", "uptime": "5h 23m"},
    "TDDOrchestrator": {"status": "healthy", "uptime": "5h 23m"},
    "InteractionOrchestrator": {"status": "degraded", "uptime": "2m"}
  }
}
```

### Graceful Degradation

If orchestrator unavailable:
1. Circuit breaker opens
2. Fallback to dummy orchestrator (limited functionality)
3. User notified of degraded service
4. Request queued for retry when service recovers

---

## 🔗 Related Documentation

- [System Overview](../02-architecture/1-system-overview.md)
- [MCP Tools Catalog](../11-mcp-tools/)
- [Orchestrator Registry](../02-orchestrators/)
- [Deployment Guide](../14-deployment/)

---

## 📚 Further Reading

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Microservices Patterns (Martin Fowler)](https://martinfowler.com/microservices/)
- [12-Factor App](https://12factor.net/)

---

**Conclusion:** CORTEX's MCP-first architecture provides service-oriented benefits (independent scaling, failure isolation, language agnostic) while maintaining simplicity through protocol-driven communication. This design enables CORTEX to evolve as an enterprise-grade AI orchestration platform.
