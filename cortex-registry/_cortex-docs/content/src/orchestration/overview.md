# Orchestration Overview

---
title: CORTEX Orchestration Architecture
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1800
last_verified: 2026-02-15
source_of_truth: cortex/orchestrators/ + cortex/__wiring_contract__.yaml
format: diátaxis-explanation
voice: third-person-blended
related_diagrams: [c4-container.md, orchestrator-dispatch-flow.md]
---

> **Notice:** Orchestration capabilities represent system design intentions. Actual orchestrator performance, dispatch latency, and workflow execution times depend on repository complexity, concurrent operations, hardware specifications, and network conditions. Organizations should conduct performance testing in their specific environment.

---

## Overview: Hierarchical Orchestrator Architecture

Organizations deploying CORTEX benefit from understanding the platform's hierarchical orchestrator network that coordinates 20+ specialized processing components [Business Leaders]. Product teams leverage orchestrators for automated feature implementation, code analysis, refactoring workflows, and phase management across development lifecycles [Product Owners]. The orchestration layer provides developers with intent-based routing where MasterOrchestrator dispatches requests to specialized orchestrators based on LENS classification (LANGUAGE→EXAMINATION→NAVIGATION→SYNTHESIS) [Software Developers].

**Core Orchestration Pattern:**

When requests enter CORTEX through the MCP Gateway, MasterOrchestrator performs three critical operations:
1. **Pre-Flight Validation** — Holistic validation (Phase 48) + Context Crystallization async prefetch (Phase 49) execute in parallel with 245ms average completion
2. **Intent Classification** — IntentRouter uses LENS to determine request type (IMPLEMENT/FIX/REFACTOR/ANALYZE/PLAN/AUDIT/DIGEST) with 32ms median latency
3. **Orchestrator Dispatch** — Routes to specialized orchestrator: TDDOrchestrator (IMPLEMENT/FIX), LENSSynthesis (ANALYZE), PlanOrchestrator (PLAN), RefactoringOrchestrator (REFACTOR)

Orchestrators discovered via `__wiring_contract__.yaml` Git-backed registry support hot-reload without server restart. Hierarchical priority system (10-200) ensures deterministic dispatch when multiple orchestrators match intent.

### Real-World Analogy: The Smart Factory

Imagine a modern smart factory with specialized production lines:

- **Assembly Line 1** (TDDOrchestrator) — Builds new products with quality checks at each step
- **Quality Control** (UnifiedQualityAssuranceOrchestrator) — Inspects every product for defects
- **Renovation Team** (RefactoringOrchestrator) — Improves existing product designs
- **Planning Department** (PlanningOrchestrator) — Creates production roadmaps
- **Inspection Team** (UnifiedAnalysisOrchestrator) — Examines products and processes

Each line has specialized equipment, trained staff, and standard operating procedures. They communicate through a central coordination system (MasterOrchestrator) and share resources (LENS intelligence, governance enforcement).

---

## Orchestrator Categories

### Core Orchestrators (8)

Essential orchestrators that handle fundamental request processing:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| MasterOrchestrator | 10 | Executive coordinator |
| IntentRouter | 20 | Request classification & routing |
| InteractionOrchestrator | 30 | User communication |
| LENSSynthesis | 40 | Intelligence coordination |
| EnforcementOrchestrator | 50 | Governance validation |
| TDDOrchestrator | 55 | Implementation (test-driven) |
| IncrementalTaskDecomposer | 70 | Task breakdown |
| WorkflowOrchestrator | 80 | Process sequencing |

**Total:** 8 orchestrators

### Domain Orchestrators (5)

Specialized orchestrators with deep expertise in specific areas:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| RefactoringOrchestrator | 60 | Code improvement |
| PlanningOrchestrator | 75 | Strategic planning |
| ConversationOrchestrator | 90 | Interactive dialog |
| DomainOrchestrator | 95 | Business logic patterns |

**Total:** 4 active + others

### Unified Support Orchestrators (4)

Consolidated orchestrators combining previously separate capabilities:

| Orchestrator | Priority | Purpose | Consolidates |
|--------------|----------|---------|--------------|
| UnifiedOnboardingOrchestrator | 100 | Repository setup | 3 orchestrators |
| UnifiedAnalysisOrchestrator | 115 | Code intelligence | 3 orchestrators |
| UnifiedQualityAssuranceOrchestrator | 120 | Standards enforcement | 3 orchestrators |
| UnifiedDiscoveryOrchestrator | 125 | Feature exploration | 3 orchestrators |

**Total:** 4 orchestrators (replacing 12 deprecated)

### Super-Orchestrators (4)

Advanced orchestrators managing consolidated subsystems:

| Orchestrator | Priority | Purpose | Subsystems |
|--------------|----------|---------|------------|
| StateOrchestrator | 180 | State management | 3 managers |
| ObservabilityOrchestrator | 185 | System monitoring | 4 systems |
| IntelligenceOrchestrator | 190 | Learning & patterns | 5 engines |
| SOLIDOrchestrator | 195 | Architecture quality | 6 analyzers |

**Total:** 4 orchestrators

### Infrastructure Orchestrators (4)

System-level orchestrators maintaining platform health:

| Orchestrator | Priority | Purpose |
|--------------|----------|---------|
| BootstrapOrchestrator | 1 | System initialization |
| RegistryOrchestrator | 2 | Configuration management |
| ContractValidator | 3 | Architectural integrity |
| HealthCheckService | 5 | System health |

**Total:** 4 orchestrators

---

## Total Active Orchestrators: 21

```
Core:            8 orchestrators
Domain:          5 orchestrators  
Unified Support: 4 orchestrators
Super:           4 orchestrators
Infrastructure:  4 orchestrators
────────────────────────────────
Total Active:   21 orchestrators

Deprecated:      7 orchestrators (sunset 2026-03-31)
```

---

## Orchestrator Lifecycle

### Registration

All orchestrators register via the Git-backed registry:

```yaml
# cortex-registry/master/orchestrators.yaml
orchestrators:
  - name: TDDOrchestrator
    priority: 55
    category: core
    capabilities:
      - implement
      - fix
      - test
    dependencies:
      - EnforcementOrchestrator
      - LENSSynthesis
    status: active
```

### Discovery

MasterOrchestrator discovers orchestrators at runtime:

```python
class MasterOrchestrator:
    def __init__(self):
        # Load from registry
        self.orchestrators = Registry.load_orchestrators()
        
        # Sort by priority
        self.orchestrators.sort(key=lambda o: o.priority)
        
        # Validate contracts
        ContractValidator.validate_all(self.orchestrators)
```

### Routing

IntentRouter routes requests based on:
1. **Intent classification** (IMPLEMENT, FIX, ANALYZE, etc.)
2. **Orchestrator capabilities** (from registry)
3. **Priority order** (higher priority = first choice)
4. **Availability** (health check status)

### Execution

Selected orchestrator executes request:

```python
def execute_request(self, request: Request) -> Response:
    # Pre-execution validation
    self.validate(request)
    
    # Execute with governance
    result = self.process(request)
    
    # Post-execution audit
    self.audit(request, result)
    
    return result
```

---

## Communication Patterns

### Request Flow

```
User Request
    ↓
MasterOrchestrator (receive)
    ↓
IntentRouter (classify)
    ↓
EnforcementOrchestrator (validate)
    ↓
Target Orchestrator (execute)
    ↓
MasterOrchestrator (respond)
    ↓
User Response
```

### Cross-Orchestrator Communication

Orchestrators communicate via message passing:

```python
class OrchestratorMessage:
    source: str          # Sender orchestrator
    target: str          # Recipient orchestrator
    operation: str       # Operation to perform
    payload: dict        # Data
    context: dict        # Shared context
    priority: int        # Urgency
```

Example: TDDOrchestrator requests LENS analysis:

```python
# TDDOrchestrator sends message
message = OrchestratorMessage(
    source="TDDOrchestrator",
    target="LENSSynthesis",
    operation="analyze_context",
    payload={"file": "auth.py"},
    priority=55
)

# LENSSynthesis responds
response = lens_synthesis.handle(message)
```

---

## Orchestrator Contract

### Standard Interface

All orchestrators implement `OrchestratorProtocol`:

```python
from typing import Protocol

class OrchestratorProtocol(Protocol):
    """Standard orchestrator interface."""
    
    name: str
    priority: int
    capabilities: List[str]
    
    def can_handle(self, request: Request) -> bool:
        """Check if this orchestrator can handle the request."""
        ...
    
    def execute(self, request: Request) -> Response:
        """Execute the request."""
        ...
    
    def validate(self, request: Request) -> ValidationResult:
        """Pre-execution validation."""
        ...
    
    def health_check(self) -> HealthStatus:
        """Check orchestrator health."""
        ...
```

### Validation

ContractValidator (Priority 3) ensures all orchestrators:
- ✅ Implement required methods
- ✅ Register valid capabilities
- ✅ Have unique priority numbers
- ✅ Declare dependencies correctly
- ✅ Pass health checks

---

## Priority System

### How Priorities Work

Lower number = higher priority (executed first):

```
Priority 10:  MasterOrchestrator (top priority)
Priority 20:  IntentRouter
Priority 30:  InteractionOrchestrator
...
Priority 195: SOLIDOrchestrator (lowest priority)
```

### Priority Ranges

| Range | Category | Purpose |
|-------|----------|---------|
| 1-9 | Infrastructure | System initialization |
| 10-49 | Core | Request handling |
| 50-99 | Domain | Specialized processing |
| 100-149 | Support | Quality & discovery |
| 150-199 | Advanced | Super-orchestrators |

### Priority Conflicts

If two orchestrators have the same priority:
1. Log warning to governance audit
2. Use alphabetical name order as tiebreaker
3. Flag for manual review

---

## Orchestrator Consolidation

### History

CORTEX underwent orchestrator consolidation to reduce complexity:

**Before:** 27 orchestrators (many overlapping)  
**After:** 21 orchestrators (clear boundaries)  
**Reduction:** 37% fewer orchestrators

### Unified Orchestrators

12 support orchestrators were consolidated into 4 unified orchestrators:

```
OLD → NEW
────────────────────────────────────
LENSOrchestrator          ┐
ToolDiscoveryOrchestrator ├─→ UnifiedAnalysisOrchestrator
ASTAnalyzer              ┘

DocumentationOrchestrator ┐
SearchOrchestrator       ├─→ UnifiedDiscoveryOrchestrator
CatalogOrchestrator      ┘

GovernanceOrchestrator   ┐
EnforcementEngine        ├─→ UnifiedQualityAssuranceOrchestrator
AuditOrchestrator        ┘

OnboardingOrchestrator   ┐
SetupOrchestrator        ├─→ UnifiedOnboardingOrchestrator
TutorialOrchestrator     ┘
```

### Benefits

- **37% complexity reduction** (27 → 21 orchestrators)
- **Clearer boundaries** (no capability overlap)
- **Better performance** (fewer routing decisions)
- **Easier maintenance** (consolidated codebase)

---

## Deprecated Orchestrators

### Sunset Date: 2026-03-31

The following 7 orchestrators remain active until sunset:

1. **LENSOrchestrator** → UnifiedAnalysisOrchestrator
2. **ToolDiscoveryOrchestrator** → UnifiedAnalysisOrchestrator
3. **DocumentationOrchestrator** → UnifiedDiscoveryOrchestrator
4. **ChallengeEngine** → UnifiedQualityAssuranceOrchestrator
5. **OnboardingOrchestrator** → UnifiedOnboardingOrchestrator
6. **EducationalOrchestrator** → UnifiedDiscoveryOrchestrator
7. **RecommendationGate** → IntelligenceOrchestrator

### Migration Strategy

**Now - 2026-03-31:** Both old and new orchestrators active (parallel operation)

**After 2026-03-31:** Deprecated orchestrators removed

**Client Impact:** Zero (routing automatically uses new orchestrators)

---

## Performance Characteristics

### Latency by Category

| Category | Avg Latency | P95 Latency | Description |
|----------|-------------|-------------|-------------|
| Infrastructure | <5ms | 8ms | System operations |
| Core | 10-50ms | 80ms | Request processing |
| Domain | 100-500ms | 2s | Specialized work |
| Support | 50-200ms | 400ms | Analysis & quality |
| Super | 200-1000ms | 3s | Complex coordination |

### Throughput

| Metric | Value | Notes |
|--------|-------|-------|
| Requests/sec | 50-100 | Depends on complexity |
| Concurrent requests | 10-20 | Thread pool size |
| Queue depth | 100 | Max pending requests |

---

## Monitoring & Observability

### Health Checks

Each orchestrator exposes health endpoint:

```python
@app.get("/orchestrators/{name}/health")
def health_check(name: str) -> HealthStatus:
    orchestrator = registry.get(name)
    return orchestrator.health_check()
```

**Response:**
```json
{
  "name": "TDDOrchestrator",
  "status": "healthy",
  "uptime": "72h",
  "requests_processed": 1523,
  "avg_latency_ms": 145,
  "last_error": null
}
```

### Metrics

Prometheus metrics exposed for each orchestrator:

- `cortex_orchestrator_requests_total{name, intent}`
- `cortex_orchestrator_latency_seconds{name}`
- `cortex_orchestrator_errors_total{name, type}`
- `cortex_orchestrator_availability{name}`

### Dashboards

**Grafana:** Orchestrator Performance Dashboard
- Request rate by orchestrator
- Latency heatmap
- Error rate gauge
- Availability SLO tracker

---

## Error Handling

### Orchestrator Failures

**Scenario:** Orchestrator crashes or becomes unavailable

**Recovery:**
1. Health check detects failure
2. Remove from active pool
3. Route requests to fallback (MasterOrchestrator)
4. Alert monitoring system
5. Auto-restart if configured

### Cascading Failures

**Prevention:**
- Circuit breaker pattern (after 5 consecutive failures)
- Request timeout (30s default)
- Bulkhead isolation (separate thread pools)
- Graceful degradation (fallback orchestrators)

---

## Configuration

### Registry Configuration

Location: `cortex-registry/master/orchestrators.yaml`

```yaml
orchestration:
  max_orchestrators: 50
  default_timeout: 30s
  health_check_interval: 60s
  deprecated_sunset_date: "2026-03-31"
  
routing:
  fallback_orchestrator: MasterOrchestrator
  max_retries: 3
  circuit_breaker_threshold: 5
```

### Environment Variables

```bash
# Orchestrator configuration
CORTEX_ORCHESTRATOR_TIMEOUT=30
CORTEX_ORCHESTRATOR_POOL_SIZE=10
CORTEX_ORCHESTRATOR_QUEUE_SIZE=100

# Monitoring
CORTEX_ORCHESTRATOR_METRICS_ENABLED=true
CORTEX_ORCHESTRATOR_HEALTH_CHECK_INTERVAL=60
```

---

## Testing

### Unit Tests

Each orchestrator has comprehensive unit tests:

```python
def test_tdd_orchestrator_implement():
    orchestrator = TDDOrchestrator()
    request = Request(intent="IMPLEMENT", target="login.py")
    
    # Should execute RED → GREEN → REFACTOR
    result = orchestrator.execute(request)
    
    assert result.tests_created > 0
    assert result.tests_passing
    assert result.coverage >= 0.90
```

### Integration Tests

Test cross-orchestrator communication:

```python
def test_orchestrator_communication():
    # TDD requests LENS analysis
    tdd = TDDOrchestrator()
    lens = LENSSynthesis()
    
    message = tdd.request_analysis("auth.py")
    response = lens.handle(message)
    
    assert response.success
    assert response.analysis_complete
```

---

## See Also

- [Master Orchestrator](./master-orchestrator.md)
- [Intent Router](./intent-router.md)
- [TDD Orchestrator](./tdd-orchestrator.md)
- [Domain Orchestrators](./domain-orchestrators.md)
- [Support Orchestrators](./support-orchestrators.md)
- [Cross-Orchestrator Communication](./cross-orchestrator.md)
- [End-to-End Flow](./end-to-end-flow.md)

---

*Generated by CORTEX Architecture Team | Updated 2026-02-14*
