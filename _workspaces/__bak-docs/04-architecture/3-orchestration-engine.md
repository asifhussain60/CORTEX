# Orchestration Engine

**Last Updated:** 2026-01-20  
**Audience:** Architects, Developers  
**Prerequisites:** [System Overview](1-system-overview.md)

## Overview

The CORTEX Orchestration Engine coordinates execution of business processes through domain-specific orchestrators. It implements the ConversationProtocol pattern for explicit, testable turn-by-turn execution with built-in governance, resilience, and audit trail capabilities.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     User Request (REST/MCP/CLI/Chat)                         │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │    LENS Protocol        │
                         │  (Intent Comprehension) │
                         │  ├─ Language Phase      │
                         │  ├─ Examination Phase   │
                         │  ├─ Navigation Phase    │
                         │  └─ Synthesis Phase     │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │   Governance Validation (Tier 0)  │
                    │   ├─ CORE rules check             │
                    │   ├─ Blocklist validation         │
                    │   └─ Audit: AC_START logged       │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │   Complexity Assessment (2.5)     │
                    │   ├─ Calculate complexity score   │
                    │   ├─ Apply approval matrix        │
                    │   └─ Auto-approve or escalate     │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │      Master Orchestrator          │
                    │   (ConversationProtocol)          │
                    │   ├─ Stage 1: Context Building    │
                    │   ├─ Stage 2: Intent Routing      │
                    │   ├─ Stage 2.5: Confirmation Gate │
                    │   ├─ Stage 3: Execution           │
                    │   └─ Stage 4: Response Composition│
                    └─────────────────┬─────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│  Planning Domain    │   │  Analysis Domain    │   │  Integration Domain │
│  Orchestrators      │   │  Orchestrators      │   │  Orchestrators      │
├─────────────────────┤   ├─────────────────────┤   ├─────────────────────┤
│ • Onboarding        │   │ • Gap Detection     │   │ • Domain Brain      │
│ • Challenge Integ   │   │ • Complexity Assess │   │ • BKIO (Knowledge)  │
│ • Context Builder   │   │ • Hallucination Det │   │ • Template Tools    │
└─────────────────────┘   └─────────────────────┘   └─────────────────────┘
          │                           │                           │
          └───────────────────────────┴───────────────────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │   Response Composition  │
                         │   ├─ 6 Response Modes   │
                         │   ├─ 5 Tone Options     │
                         │   ├─ 5 Format Profiles  │
                         │   └─ Template System    │
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │    Result (Success)     │
                         │    or Error/Rollback    │
                         │    + Audit Trail        │
                         └────────────────────────┘
```

## ConversationProtocol (Turn-by-Turn Execution)

The ConversationProtocol replaces imperative loops with explicit, testable turn-by-turn orchestration.

### ContinuationDecision Pattern

Each turn returns a `ContinuationDecision` with explicit continuation reason:

```python
@dataclass
class ContinuationDecision:
    """Explicit decision about orchestrator continuation."""
    should_continue: bool
    reason: ContinuationReason
    next_operation: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
class ContinuationReason(Enum):
    """Terminal events that break the orchestration loop."""
    COMPLETION = "goal_achieved"
    USER_REJECTION = "user_rejected_result"
    TOKEN_LIMIT = "approaching_token_budget"
    GOVERNANCE_HALT = "rule_violation_detected"
    MAX_ROUNDS_REACHED = "safety_limit_exceeded"
    ERROR_UNRECOVERABLE = "fatal_error_occurred"
    INTERACTION_REQUIRED = "waiting_for_user_input"
    CONFIRMATION_REQUESTED = "complexity_gate_triggered"
```

**Implementation:** PHASE-16-ORCHESTRATOR-CONTINUATION (155 tests passing)

### Stage Execution Flow

| Stage | Component | Function | Audit Event |
|-------|-----------|----------|-------------|
| **1** | HolisticContextBuilder | Load orchestrator context | - |
| **2** | LENS Protocol | Route intent to orchestrator | AC_START |
| **2.5** | ComplexityAssessment | Evaluate complexity, apply approval matrix | - |
| **3** | Domain Orchestrator | Execute business logic | AC_EXECUTE |
| **4** | ResponseComposer | Format and return result | AC_COMPLETE |

## Complexity-Aware Confirmation Gate (Stage 2.5)

The Confirmation Gate evaluates operation complexity before execution:

### Complexity Scoring

```
Complexity Score = 
    (LENS Confidence × 0.25) +
    (Files Affected × 0.35) +
    (Dependency Depth × 0.25) +
    (Operation Scope × 0.15)
```

### Approval Matrix

| Score Range | Level | Action |
|-------------|-------|--------|
| ≤0.15 | TRIVIAL | Auto-approve, no interaction |
| 0.15-0.35 | SIMPLE | Auto-approve with summary |
| 0.35-0.60 | MODERATE | Request user confirmation |
| 0.60-0.85 | COMPLEX | Confirm + show alternatives |
| ≥0.85 | CRITICAL | Escalate with executive summary |

**Implementation:** PHASE-23-COMPLEXITY-AWARE-CONFIRMATION

### Governance Rules (Tier 1)

| Rule ID | Description |
|---------|-------------|
| CONF-GATE-001 | Trivial operations auto-approve (≤0.15 score) |
| CONF-GATE-002 | Confidence-based approval matrix enforcement |
| CONF-GATE-003 | Alternative recommendations for COMPLEX/CRITICAL |
| CONF-GATE-004 | User goal enhancement with best recommendation |
| CONF-GATE-005 | Audit trail enrichment with complexity factors |

## Response Composition (Stage 4)

Multi-mode response generation with per-turn isolation:

### Response Modes

| Mode | Use Case | Format |
|------|----------|--------|
| CHAT | Interactive conversation | Natural language |
| COMMAND | CLI output | Structured text |
| VISUALIZATION | Dashboard/UI | Chart-ready data |
| JSON_API | External integrations | JSON response |
| MARKDOWN | Documentation | Formatted markdown |
| STREAM | Real-time updates | Chunked output |

### Tone Options

| Tone | Audience | Style |
|------|----------|-------|
| FORMAL | Business stakeholders | Professional, precise |
| CASUAL | Developers | Friendly, concise |
| TECHNICAL | Engineers | Detailed, exact |
| EXECUTIVE | Leadership | High-level summary |
| EDUCATIONAL | Learners | Explanatory, examples |

### Formatting Profiles

| Profile | Verbosity | Use Case |
|---------|-----------|----------|
| COMPACT | Minimal | Status updates |
| STANDARD | Balanced | General responses |
| VERBOSE | Detailed | Deep explanations |
| MINIMAL | Essential only | Quick answers |
| RICH | Full formatting | Documentation |

**Implementation:** PHASE-24-RESPONSE-COMPOSITION (172 tests)

## Orchestrator Registry

Domain orchestrators are registered and discovered through the OrchestratorRegistry:

### Registration

```python
# Registration via decorator
@register_orchestrator(domain="planning", name="onboarding")
class OnboardingOrchestrator:
    """Handles user onboarding workflows."""
    pass

# Or programmatic registration
registry.register(
    domain="analysis",
    name="complexity_assessment",
    orchestrator_class=ComplexityAssessmentOrchestrator
)
```

### Discovery

```python
# Find orchestrator by domain
orchestrator = registry.get_orchestrator("planning", "onboarding")

# List all orchestrators in domain
planning_orchestrators = registry.list_by_domain("planning")

# Get orchestrator metadata
metadata = registry.get_metadata("analysis", "complexity_assessment")
```

### Orchestrator Domains

| Domain | Purpose | Example Orchestrators |
|--------|---------|----------------------|
| **Planning** | Workflow coordination | Onboarding, Challenge, Context |
| **Analysis** | Code/data analysis | Gap Detection, Complexity, Hallucination |
| **Integration** | External system integration | Domain Brain, BKIO, Template Tools |
| **Validation** | Quality assurance | Governance, Coherence, Security |
| **Execution** | Task execution | TDD, Implementation, Deployment |

## Resilience Patterns

The orchestration engine includes built-in resilience:

### Circuit Breaker

```
Request → Check Circuit State
    │
    ├─ CLOSED: Forward request
    │   └─ Success → Stay closed
    │   └─ Failure → Track, check threshold
    │       └─ If failure_rate > 50% → OPEN
    │
    ├─ OPEN: Reject immediately (fail fast)
    │   └─ After timeout (30s) → HALF_OPEN
    │
    └─ HALF_OPEN: Allow test request
        └─ Success (2 requests) → CLOSED
        └─ Failure → OPEN
```

### Partial Functionality Mode

When components fail, degrade gracefully:

```
Normal: Full orchestrator execution
  │
  ▼
Domain Brain unavailable?
  └─ Use cached knowledge
  └─ Mark response as "partial"
  └─ Continue with degraded capability
  │
  ▼
Return result with warnings
```

### Automatic Retry

- **Exponential Backoff:** 100ms → 200ms → 400ms → 800ms
- **Max Retries:** 3 (configurable per orchestrator)
- **Jitter:** Random variance to prevent thundering herd

### Rollback Capability

Failed transactions are rolled back atomically:

1. Execute steps 1..N
2. If error at step K: Rollback steps 1..K-1
3. Log rollback with transaction ID
4. Return error with audit trail

## Audit Trail Integration

Every orchestrator execution generates audit entries:

```
AC_START (intent_id, orchestrator, timestamp, hash_n)
    │
    ▼
AC_EXECUTE (intent_id, step, result, timestamp, hash_n+1)
    │
    ▼
AC_COMPLETE (intent_id, outcome, duration, timestamp, hash_n+2)
```

**Database:** `cortex_brain/state/governance.db`
**Hash Chain:** Global chronological, tamper-evident

## Configuration

### Orchestrator Configuration

```yaml
# cortex-config.yaml
orchestrator:
  max_rounds: 10
  timeout_seconds: 300
  retry:
    max_attempts: 3
    backoff_multiplier: 2.0
    initial_delay_ms: 100
  circuit_breaker:
    failure_threshold: 0.5
    reset_timeout_seconds: 30
    success_threshold: 2
```

### Complexity Gate Configuration

```yaml
complexity_gate:
  thresholds:
    trivial: 0.15
    simple: 0.35
    moderate: 0.60
    complex: 0.85
  weights:
    lens_confidence: 0.25
    files_affected: 0.35
    dependency_depth: 0.25
    operation_scope: 0.15
```

## Related Documentation

- [System Overview](1-system-overview.md) - Architecture overview
- [Resilience Patterns](5-resilience-patterns.md) - Detailed resilience configuration
- [Domain Brain](4-domain-brain.md) - Knowledge integration
- [MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md) - Tool exposure
- [Troubleshooting](../04-guides/operations/4-troubleshooting.md) - Common issues
