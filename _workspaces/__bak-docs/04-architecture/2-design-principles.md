# Design Principles

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready  
**Audience:** Architects, Tech Leads, Developers

## Overview

CORTEX embodies a set of core design principles that inform every architectural decision. These principles emerged from building a system that handles AI-assisted development in governance-heavy, safety-critical contexts. Understanding these principles helps you work effectively with CORTEX and extend it appropriately.

---

## Table of Contents

1. [Governance-First Architecture](#1-governance-first-architecture)
2. [Orchestration as Conversation](#2-orchestration-as-conversation)
3. [Resilience by Design](#3-resilience-by-design)
4. [Knowledge-Driven Operations](#4-knowledge-driven-operations)
5. [Separation of Concerns](#5-separation-of-concerns)
6. [Observability as a Feature](#6-observability-as-a-feature)
7. [Intent Before Implementation](#7-intent-before-implementation)
8. [Explicit Over Implicit](#8-explicit-over-implicit)
9. [Progressive Disclosure](#9-progressive-disclosure)
10. [Safety Through Auditability](#10-safety-through-auditability)

---

## 1. Governance-First Architecture

**"Safety is not a feature—it's the foundation."**

CORTEX places governance at the core of the architecture, not as an afterthought. Every operation must pass through the governance framework before execution.

### Multi-Tier Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                      TIER 0 - SKULL Rules                       │
│         29 CORE rules, immutable, always enforced               │
│         Example: CORE-001 "Safe Operations Only"                │
├─────────────────────────────────────────────────────────────────┤
│                      TIER 1 - Architectural                     │
│         Structural constraints, versioned, admin-only           │
│         Example: "All database writes require audit entry"      │
├─────────────────────────────────────────────────────────────────┤
│                      TIER 2 - Templates                         │
│         80+ scaffolding templates, user-extendable              │
│         Example: "Python orchestrator template"                 │
├─────────────────────────────────────────────────────────────────┤
│                      TIER 3 - Knowledge                         │
│         Domain knowledge, context, business rules               │
│         Example: "Company coding standards"                     │
└─────────────────────────────────────────────────────────────────┘
```

### Key Implications

- **Rule evaluation is mandatory**: No operation bypasses governance
- **Higher tiers cannot override lower**: Tier 0 rules are absolute
- **Rules are declarative**: Express what, not how
- **Audit is automatic**: Every rule evaluation is logged

### Code Example

```python
# Governance check is built into orchestrator base
class OrchestratorBase:
    async def execute(self, intent: str, context: dict) -> Result:
        # Governance check happens automatically
        violations = await self.governance.evaluate(intent, context)
        if violations:
            return self._blocked_result(violations)
        
        # Only then does execution proceed
        return await self._do_execute(intent, context)
```

---

## 2. Orchestration as Conversation

**"Complex operations are dialogues, not commands."**

CORTEX models execution as multi-turn conversations using the `ConversationProtocol` pattern. This enables:

- **Iterative refinement**: Users can clarify intent across turns
- **Explicit termination**: Every turn ends with a clear `ContinuationDecision`
- **Testable flows**: Each turn is independently testable

### ConversationProtocol Pattern

```
Turn 1: User provides initial intent
        → System comprehends via LENS
        → Decision: NEEDS_INPUT (clarification required)

Turn 2: User provides clarification
        → System updates context
        → Decision: NEEDS_APPROVAL (high complexity detected)

Turn 3: User approves
        → System executes
        → Decision: COMPLETE (task finished)
```

### ContinuationDecision Types

| Reason | Description | User Action |
|--------|-------------|-------------|
| `COMPLETE` | Task finished successfully | None |
| `NEEDS_INPUT` | More information required | Provide clarification |
| `NEEDS_APPROVAL` | Confirmation required | Approve or cancel |
| `ERROR` | Processing failed | Fix and retry |
| `GOVERNANCE_BLOCK` | Rule violation | Modify request |
| `MAX_TURNS` | Turn limit reached | Start new conversation |

### Why Conversations?

1. **Safety**: High-risk operations require explicit approval
2. **Clarity**: Ambiguous intent is clarified before action
3. **Auditability**: Every turn is recorded
4. **UX**: Progressive disclosure reduces cognitive load

---

## 3. Resilience by Design

**"Plan for failure—it will happen."**

CORTEX assumes components will fail and builds resilience into the core:

### Resilience Patterns

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Circuit Breaker** | Fail fast when service is down | Configurable threshold and timeout |
| **Partial Mode** | Degrade gracefully | Cache fallback, simplified logic |
| **Retry with Backoff** | Handle transient failures | Exponential + jitter |
| **Rollback** | Atomic failure recovery | Transaction-based with audit |

### Failure Hierarchy

```
Level 1: Transient Failure
├── Retry automatically (3 attempts)
├── Exponential backoff (100ms → 200ms → 400ms)
└── Success or escalate

Level 2: Persistent Failure  
├── Circuit breaker opens
├── Fail fast for timeout period
└── Partial mode engagement

Level 3: Critical Failure
├── Emergency shutdown
├── Audit trail preserved
└── Admin notification
```

### Design Implication

Every external call, every I/O operation is wrapped in resilience logic. You never call a service directly—you call through the resilience layer.

---

## 4. Knowledge-Driven Operations

**"Decisions should be informed, not assumed."**

CORTEX's Domain Brain provides contextual knowledge to all operations:

### Knowledge Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Processing                       │
│                                                                  │
│  1. Intent Received                                              │
│     ↓                                                           │
│  2. LENS Comprehension ←── Domain Brain Query (context)         │
│     ↓                                                           │
│  3. Governance Check ←── Domain Brain Query (rules)             │
│     ↓                                                           │
│  4. Execution ←── Domain Brain Query (procedures)               │
│     ↓                                                           │
│  5. Response Composition ←── Domain Brain Query (templates)     │
└─────────────────────────────────────────────────────────────────┘
```

### Key Concepts

- **BKIO (Business Knowledge Ingestion Organization)**: Structured knowledge format
- **Semantic Search**: Find relevant knowledge by meaning, not keywords
- **Conflict Resolution**: When knowledge conflicts, hierarchy resolves it
- **Knowledge Freshness**: Stale knowledge is flagged, not used blindly

---

## 5. Separation of Concerns

**"One component, one responsibility."**

CORTEX strictly separates different concerns:

### Governance ≠ Execution

```
┌─────────────┐     ┌─────────────┐
│ Governance  │     │  Execution  │
│  Framework  │     │   Engine    │
├─────────────┤     ├─────────────┤
│ What rules  │     │ How to do   │
│ Must pass   │     │ The work    │
│ Who decides │     │ When done   │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └───────┬───────────┘
               │
       ┌───────▼───────┐
       │  Orchestrator │
       │  (Combines)   │
       └───────────────┘
```

### API ≠ Protocol

All interfaces (REST, MCP, CLI) are equal-privilege citizens:

```python
# Same orchestrator, different entry points
@app.post("/api/orchestrate")      # REST
async def api_orchestrate(request): 
    return await orchestrator.execute(request.intent)

def handle_mcp_call(params):        # MCP
    return orchestrator.execute(params["intent"])

@cli.command()                       # CLI
def orchestrate(intent: str):
    return orchestrator.execute(intent)
```

### Config ≠ Code

All configuration is externalized:

```yaml
# cortex-config.yaml - No config in code
governance:
  tier: 0
  rules_path: ./cortex_brain/tier0/

orchestrators:
  master:
    max_turns: 10
    timeout: 30.0
```

### Prompt ≠ Runtime Data Access

**Critical Pattern**: Prompts define behavior, orchestrators access data at runtime.

```
┌──────────────────────┐
│ Design-Time Prompts  │ ← Define standards, patterns, rules
│ (cortex-architect)   │ ← Contains detailed YAML documentation
└──────────┬───────────┘
           │ references (behavior only)
           ↓
┌──────────────────────┐
│ Production Prompts   │ ← Define rules ONLY (e.g., CORE-036)
│ (CORTEX, copilot)    │ ← NO implementation details
└──────────┬───────────┘
           │ invoke
           ↓
┌──────────────────────┐
│ MCP Tools            │ ← Protocol layer
└──────────┬───────────┘
           │ use
           ↓
┌──────────────────────┐
│ Orchestrators        │ ← Access knowledge YAMLs at runtime
└──────────┬───────────┘
           │ load
           ↓
┌──────────────────────┐
│ Knowledge YAMLs      │ ← 45+ authoritative sources
│ (cortex_brain/tier3) │
└──────────────────────┘
```

**Why This Matters:**

| Anti-Pattern | Problem | Correct Pattern |
|--------------|---------|-----------------|
| Production prompt contains YAML locations | Coupling, maintenance burden | Rule reference → orchestrator loads |
| Prompt documents implementation | Design-time concerns leak to runtime | Behavior in prompt, data via orchestrator |
| Hardcoded knowledge in prompts | Can't update without prompt changes | Dynamic knowledge access |

**Example (CORRECT):**

```python
# Production prompt: CORE-036 says "verify standards compliance"
# Runtime: Orchestrator decides HOW to verify
class TDDOrchestrator:
    def validate_standards(self, code: str) -> List[Violation]:
        # Load knowledge YAMLs dynamically
        tdd_rules = self.knowledge.load("TESTING-VALIDATION/tdd-best-practices.yaml")
        solid_rules = self.knowledge.load("ARCHITECTURE/solid-principles.yaml")
        
        # Apply rules at runtime
        return self._check_compliance(code, tdd_rules + solid_rules)
```

**Example (INCORRECT):**

```python
# ❌ Production prompt hardcodes: "Check TESTING-VALIDATION/tdd-best-practices.yaml"
# Problem: Adding new YAML requires prompt update
```

**Principles:**
- **12-Factor (III. Config)**: Data sources (YAMLs) are configuration, not code (prompts)
- **SOLID (SRP)**: Prompts = behavior definition, orchestrators = data access
- **SOLID (DIP)**: Depend on abstraction ("standards exist"), not concrete YAML paths
- **Clean Code**: Low coupling between prompts and implementation details

---

## 6. Observability as a Feature

**"If you can't see it, you can't fix it."**

CORTEX treats observability as a first-class feature, not an add-on:

### Three Pillars

| Pillar | Implementation | Purpose |
|--------|----------------|---------|
| **Logs** | Structured JSON with context | Debugging, audit |
| **Metrics** | Prometheus-compatible | Performance, SLAs |
| **Traces** | Distributed tracing | Request flows |

### Audit Trail

Every significant action produces an audit entry:

```json
{
  "entry_id": "AUD-00001234",
  "timestamp": "2026-01-20T14:23:45.678Z",
  "orchestrator": "master-orchestrator",
  "intent": "Analyze repository",
  "governance_result": "PASSED",
  "rules_evaluated": ["CORE-001", "CORE-002"],
  "execution_time_ms": 234,
  "session_id": "sess-abc123",
  "hash": "sha256:a1b2c3...",
  "previous_hash": "sha256:x9y8z7..."
}
```

### Hash Chain Integrity

Audit entries form a hash chain—any tampering is detectable:

```
Entry 1 → Hash(Entry 1) 
Entry 2 → Hash(Entry 2 + Previous Hash)
Entry 3 → Hash(Entry 3 + Previous Hash)
...
```

---

## 7. Intent Before Implementation

**"Understand what before deciding how."**

CORTEX uses the LENS Protocol to comprehend intent before execution:

### LENS Protocol Phases

```
┌─────────────────────────────────────────────────────────────────┐
│  L - LANGUAGE     Canonicalize intent, extract keywords         │
├─────────────────────────────────────────────────────────────────┤
│  E - EXAMINATION  Identify patterns, classify operation type    │
├─────────────────────────────────────────────────────────────────┤
│  N - NAVIGATION   Map to capabilities, determine orchestrator   │
├─────────────────────────────────────────────────────────────────┤
│  S - SYNTHESIS    Generate execution plan, merge context        │
└─────────────────────────────────────────────────────────────────┘
```

### Why Intent-First?

1. **Prevents misunderstanding**: Ambiguous requests are clarified
2. **Enables governance**: Rules are applied to intent, not implementation
3. **Improves UX**: System explains what it will do before doing it
4. **Supports audit**: Intent is logged separately from action

---

## 8. Explicit Over Implicit

**"Magic is the enemy of understanding."**

CORTEX prefers explicit declarations over implicit conventions:

### Examples

| Implicit (Avoid) | Explicit (Prefer) |
|------------------|-------------------|
| Auto-detect config location | Require `CORTEX_CONFIG` env var |
| Assume default database | Require explicit `--db-path` |
| Implicit rule priorities | Explicit tier numbers (0-3) |
| Magic method names | Decorated `@orchestrator.step` |

### Code Example

```python
# Implicit (Avoid)
class MyOrchestrator:
    def _before_execute(self):  # Magic method name
        pass

# Explicit (Prefer)
class MyOrchestrator:
    @orchestrator.lifecycle("before_execute")
    def prepare_execution(self):
        pass
```

---

## 9. Progressive Disclosure

**"Show complexity when needed, hide it when not."**

CORTEX reveals complexity progressively based on user need:

### Complexity Layers

```
Layer 1: Simple Use (80% of users)
├── cortex run "Analyze this"
└── Single command, sensible defaults

Layer 2: Configuration (15% of users)
├── cortex-config.yaml customization
└── Override defaults, add rules

Layer 3: Extension (5% of users)
├── Custom orchestrators
├── New governance rules
└── Protocol integrations
```

### Response Composition

Responses adapt to context:

| Mode | Detail Level | Audience |
|------|--------------|----------|
| `concise` | Minimal | Experts |
| `standard` | Balanced | Most users |
| `detailed` | Comprehensive | New users |
| `debug` | Full trace | Developers |

---

## 10. Safety Through Auditability

**"An unaudited action is an unsafe action."**

CORTEX ensures safety by making everything auditable:

### Audit Completeness

| What | Audited? | Details |
|------|----------|---------|
| User intent | ✅ | Full text, context |
| Governance decisions | ✅ | Rules applied, results |
| Execution steps | ✅ | Each step with timing |
| Errors | ✅ | Full stack trace |
| Configuration changes | ✅ | Before/after values |
| Admin actions | ✅ | Who, what, when |

### Tamper Evidence

The hash chain audit trail provides:

- **Detection**: Any modification breaks the chain
- **Non-repudiation**: Entries cannot be denied
- **Compliance**: Meets GDPR, HIPAA, SOC2 requirements

---

## Applying These Principles

### When Building New Features

Ask yourself:

1. Does it respect the governance tier hierarchy?
2. Is it modeled as a conversation if complex?
3. Does it handle failures gracefully?
4. Is it knowledge-driven or assumption-driven?
5. Are concerns properly separated?
6. Is it observable and auditable?

### When Reviewing Code

Check for:

- Governance bypass (never acceptable)
- Implicit state or configuration
- Missing error handling
- Unlogged significant actions
- Hidden complexity

---

## Related Documents

- [System Overview](1-system-overview.md) - Architecture implementation
- [Orchestration Engine](3-orchestration-engine.md) - ConversationProtocol details
- [Resilience Patterns](5-resilience-patterns.md) - Failure handling
- [Domain Brain](4-domain-brain.md) - Knowledge integration

---

**These principles are not just guidelines—they are the foundation of CORTEX's reliability and safety.**
