# CORTEX Review Sub-Agents
**Version:** 4.0 | **Updated:** 2026-01-24 | **Role:** 8 Specialized Analysis Agents

---

## Overview

These 8 sub-agents work together under the **ReviewOrchestrator** to provide comprehensive code analysis.

---

## Agent 1: Brittleness (BRIT)

### Focus
- Single points of failure (SPOFs)
- Error handling gaps
- Resource exhaustion paths
- Edge case handling
- Load/stress behavior

### Detection Patterns
```yaml
patterns:
  - Unbounded loops/recursion
  - Missing timeouts
  - Uncapped collections
  - Single-threaded bottlenecks
  - Missing circuit breakers
  - No retry logic
```

### Output: `Findings-BRIT.yaml`

---

## Agent 2: Hallucination (HALL)

### Focus
- Unvalidated LLM output
- Prompt injection vectors
- AI safety boundaries
- Output validation
- Confidence thresholds

### Detection Patterns
```yaml
patterns:
  - Raw LLM output usage
  - Missing output validation
  - Injection-vulnerable prompts
  - Unchecked confidence scores
  - Boundary bypasses
```

### Output: `Findings-HALL.yaml`

---

## Agent 3: Governance (GOV)

### Focus
- CORE rule compliance
- Audit trail completeness
- Type hint coverage
- Docstring coverage
- TDD compliance

### Detection Patterns
```yaml
patterns:
  - CORE-008: No tests before code
  - CORE-011: Missing type hints
  - CORE-012: Missing docstrings
  - CORE-013: Bare except clauses
  - CORE-027: Missing audit trail
```

### Output: `Findings-GOV.yaml`

---

## Agent 4: Assumptions (ASM)

### Focus
- Platform dependencies
- Environment assumptions
- Service availability
- Version constraints
- Configuration assumptions

### Detection Patterns
```yaml
patterns:
  - Hardcoded paths (/Users/, /home/)
  - Platform-specific code
  - Undeclared dependencies
  - Implicit ordering
  - Missing fallbacks
```

### Output: `Findings-ASM.yaml`

---

## Agent 5: Technical Debt (DEBT)

### Focus
- Code duplication
- Deprecated patterns
- Missing abstractions
- TODO/FIXME density
- Test coverage gaps

### Detection Patterns
```yaml
patterns:
  - Copy-paste code
  - Deprecated API usage
  - Long methods (>50 lines)
  - High cyclomatic complexity
  - Untested code paths
```

### Output: `Findings-DEBT.yaml`

---

## Agent 6: State/Concurrency (STATE)

### Focus
- Race conditions
- Deadlocks
- Atomicity violations
- Global state abuse
- Thread safety

### Detection Patterns
```yaml
patterns:
  - Unprotected shared state
  - Lock ordering issues
  - Non-atomic operations
  - Global mutable state
  - Missing synchronization
```

### Output: `Findings-STATE.yaml`

---

## Agent 7: Architecture (ARCH)

### Focus
- SOLID violations
- Design pattern misuse
- Coupling issues
- Cohesion problems
- Dependency direction

### Detection Patterns
```yaml
patterns:
  - Single Responsibility violations
  - Interface segregation issues
  - Circular dependencies
  - God classes
  - Feature envy
```

### Output: `Findings-ARCH.yaml`

---

## Agent 8: Integration/Observability (INTEG)

### Focus
- System boundaries
- Monitoring gaps
- Health check coverage
- Logging adequacy
- Tracing coverage

### Detection Patterns
```yaml
patterns:
  - Missing health endpoints
  - Untraced operations
  - Insufficient logging
  - Missing metrics
  - Undocumented APIs
```

### Output: `Findings-INTEG.yaml`

---

## Severity Classification

| Level | Badge | Action Required |
|-------|-------|-----------------|
| CRITICAL | 🔴 | Immediate fix |
| HIGH | 🟠 | Fix before next phase |
| MEDIUM | 🟡 | Should fix |
| LOW | 🔵 | Nice to have |
| INFO | ⚪ | No action |

---

## Execution

```yaml
batch_1_parallel: [BRIT, HALL, GOV]
batch_2_parallel: [ASM, DEBT, STATE, ARCH, INTEG]
```

All agents run in parallel within their batch, producing independent findings files.
