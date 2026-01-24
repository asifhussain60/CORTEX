# CORTEX Review System - 8-Agent Comprehensive Analysis
**Version:** 4.0 | **Updated:** 2026-01-24 | **Authority:** cortex-impl-map.yaml v3.0 | **Status:** ✅ PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Review
**Author:** Asif Hussain | **Phase:** Analysis | **Orchestrator:** ReviewOrchestrator ✅

---
```

---

## 🎯 Purpose

**CORTEX Review** performs comprehensive code quality and architecture analysis using 8 specialized agents:

1. **Brittleness** - Structural weaknesses, SPOFs
2. **Hallucination** - AI safety, unvalidated outputs
3. **Governance** - CORE rule compliance
4. **Assumptions** - Hidden dependencies
5. **Debt** - Technical debt, TODOs
6. **State/Concurrency** - Race conditions, deadlocks
7. **Architecture** - SOLID violations, coupling
8. **Integration/Observability** - Monitoring gaps

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### Before EVERY Review:

**Step 1: Intent Classification**
```markdown
### 📋 Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `ANALYZE` |
| **Handler** | `ReviewOrchestrator` |
| **Confidence** | 🟢 High (92%) |
| **Scope** | `{FILE|MODULE|SYSTEM}` |
| **Impact** | 🔵 Low |
| **Agents** | {selected agents} |
| **Rules** | CORE-027 (audit trail) |

---
**⏳ Awaiting approval to proceed...**
```

**Step 2: Wait for User Approval**

**Step 3: Execute Review**

---

## 🚀 Quick Commands

| Command | Action | Output |
|---------|--------|--------|
| `/review` | Full 8-agent review | Comprehensive findings |
| `/review {file}` | Review specific file | File-level findings |
| `/review-brittleness` | Brittleness agent only | BRIT findings |
| `/review-hallucination` | Hallucination agent | HALL findings |
| `/review-governance` | Governance compliance | GOV findings |
| `/review-assumptions` | Hidden assumptions | ASM findings |
| `/review-debt` | Technical debt | DEBT findings |
| `/review-state` | State/concurrency | STATE findings |
| `/review-arch` | Architecture quality | ARCH findings |
| `/review-integration` | Integration gaps | INTEG findings |

---

## 🤖 8-Agent Architecture

### Agent 1: Brittleness (BRIT)
```yaml
focus:
  - Single points of failure (SPOFs)
  - Error handling gaps
  - Resource exhaustion paths
  - Edge case handling
  - Load/stress behavior

detection:
  - Unbounded loops
  - Missing timeouts
  - Uncapped collections
  - Single-threaded bottlenecks
  - Missing circuit breakers

output: Findings-BRIT.yaml
```

### Agent 2: Hallucination (HALL)
```yaml
focus:
  - Unvalidated LLM output
  - Prompt injection vectors
  - AI safety boundaries
  - Output validation
  - Confidence thresholds

detection:
  - Raw LLM output usage
  - Missing output validation
  - Injection-vulnerable prompts
  - Unchecked confidence scores
  - Boundary bypasses

output: Findings-HALL.yaml
```

### Agent 3: Governance (GOV)
```yaml
focus:
  - CORE rule compliance
  - Audit trail completeness
  - Type hint coverage
  - Docstring coverage
  - TDD compliance

detection:
  - CORE-008 violations (no test first)
  - CORE-011 violations (missing types)
  - CORE-012 violations (missing docs)
  - CORE-013 violations (bare except)
  - CORE-027 violations (no audit trail)

output: Findings-GOV.yaml
```

### Agent 4: Assumptions (ASM)
```yaml
focus:
  - Platform dependencies
  - Environment assumptions
  - Service availability
  - Version constraints
  - Configuration assumptions

detection:
  - Hardcoded paths
  - Platform-specific code
  - Undeclared dependencies
  - Implicit ordering
  - Missing fallbacks

output: Findings-ASM.yaml
```

### Agent 5: Debt (DEBT)
```yaml
focus:
  - Code duplication
  - Deprecated patterns
  - Missing abstractions
  - TODO/FIXME density
  - Test coverage gaps

detection:
  - Copy-paste code
  - Deprecated API usage
  - Long methods (>50 lines)
  - High cyclomatic complexity
  - Untested code paths

output: Findings-DEBT.yaml
```

### Agent 6: State/Concurrency (STATE)
```yaml
focus:
  - Race conditions
  - Deadlocks
  - Atomicity violations
  - Global state abuse
  - Thread safety

detection:
  - Unprotected shared state
  - Lock ordering issues
  - Non-atomic operations
  - Global mutable state
  - Missing synchronization

output: Findings-STATE.yaml
```

### Agent 7: Architecture (ARCH)
```yaml
focus:
  - SOLID violations
  - Design pattern misuse
  - Coupling issues
  - Cohesion problems
  - Dependency direction

detection:
  - Single Responsibility violations
  - Interface segregation issues
  - Circular dependencies
  - God classes
  - Feature envy

output: Findings-ARCH.yaml
```

### Agent 8: Integration/Observability (INTEG)
```yaml
focus:
  - System boundaries
  - Monitoring gaps
  - Health check coverage
  - Logging adequacy
  - Tracing coverage

detection:
  - Missing health endpoints
  - Untraced operations
  - Insufficient logging
  - Missing metrics
  - Undocumented APIs

output: Findings-INTEG.yaml
```

---

## 📊 Review Workflow

### Phase 0: Pre-Review Validation (5 min)
```yaml
gates:
  0A: Data freshness (last entry < 24 hours)
  0B: Audit trail completeness (≥ 2000 entries)
  0C: Hash chain integrity (0 violations)
  0D: Test fixture isolation (≤ 6 fixtures)

action:
  ALL pass → Proceed to Phase 1
  ANY fail → Investigate before proceeding
```

### Phase 1: Gap Inventory (10 min)
```yaml
tasks:
  - Read cortex-impl-map.yaml status
  - Verify COMPLETED phases have code
  - Identify FALSE_COMPLETED phases
  - Create review-gap-inventory.yaml
```

### Phase 2: Stub Detection (10 min)
```yaml
tasks:
  - Find NotImplementedError
  - Find empty pass statements
  - Find TODO blockers
  - Find mock/hardcoded returns
  - Create review-stubs.yaml
```

### Phase 3: 8-Agent Analysis (30 min)
```yaml
batch_1_parallel:
  - Agent 1: Brittleness
  - Agent 2: Hallucination
  - Agent 3: Governance

batch_2_parallel:
  - Agent 4: Assumptions
  - Agent 5: Debt
  - Agent 6: State/Concurrency
  - Agent 7: Architecture
  - Agent 8: Integration
```

### Phase 4: Consolidation (10 min)
```yaml
tasks:
  - Merge all Findings-*.yaml
  - Prioritize by severity
  - Generate remediation plan
  - Create review-consolidated.yaml
```

---

## 📁 Output Locations

### Timestamped Artifacts
```
_workspaces/roadmap/issues/{TIMESTAMP}/
├── review-gap-inventory.yaml
├── review-stubs.yaml
├── Findings-BRIT.yaml
├── Findings-HALL.yaml
├── Findings-GOV.yaml
├── Findings-ASM.yaml
├── Findings-DEBT.yaml
├── Findings-STATE.yaml
├── Findings-ARCH.yaml
├── Findings-INTEG.yaml
└── remediation-plan.yaml
```

### Reports
```
_workspaces/roadmap/reports/
└── review-consolidated-{TIMESTAMP}.yaml
```

---

## 🎯 Finding Severity Levels

| Level | Badge | Criteria |
|-------|-------|----------|
| **CRITICAL** | 🔴 | Blocks production, security risk |
| **HIGH** | 🟠 | Major issue, needs fix before next phase |
| **MEDIUM** | 🟡 | Should fix, not blocking |
| **LOW** | 🔵 | Nice to have, technical hygiene |
| **INFO** | ⚪ | Observation, no action required |

---

## 📋 Example Review Output

```yaml
## 🧠 CORTEX Review
**Author:** Asif Hussain | **Phase:** Analysis | **Orchestrator:** ReviewOrchestrator ✅

---

### Review Summary

| Agent | Findings | Critical | High | Medium |
|-------|----------|----------|------|--------|
| BRIT | 3 | 0 | 1 | 2 |
| HALL | 2 | 1 | 1 | 0 |
| GOV | 5 | 0 | 2 | 3 |
| ASM | 4 | 0 | 0 | 4 |
| DEBT | 8 | 0 | 3 | 5 |
| STATE | 1 | 0 | 1 | 0 |
| ARCH | 2 | 0 | 1 | 1 |
| INTEG | 3 | 0 | 1 | 2 |
| **Total** | **28** | **1** | **10** | **17** |

### Critical Findings

| ID | Agent | Issue | Location |
|----|-------|-------|----------|
| HALL-001 | Hallucination | Unvalidated LLM output | `cortex/ai/responder.py:45` |

### Recommended Actions

1. **Immediate (Critical):**
   - Add output validation to `responder.py`

2. **High Priority:**
   - Add circuit breaker to external API calls
   - Fix CORE-011 violations in 5 files
   - Add retry logic to database operations

3. **Medium Priority:**
   - Reduce code duplication in orchestrators
   - Add missing docstrings
```

---

## 🔗 Integration Points

### Review Orchestrator
```python
from cortex.orchestrators.review.review_orchestrator import ReviewOrchestrator

reviewer = ReviewOrchestrator()
results = reviewer.full_review(scope="cortex/")
```

### Governance Registry
```python
from cortex.brain.core.governance_registry import GovernanceRegistry

registry = GovernanceRegistry()
compliance = registry.check_compliance(path="cortex/")
```

### Audit Logger
```python
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()
logger.log_operation_start(operation="REVIEW", scope="cortex/")
```

---

## ✅ Review Checklist

### Before Review
- [ ] DoR displayed and approved?
- [ ] Scope defined (file, module, system)?
- [ ] Agents selected?
- [ ] Output directory created?

### During Review
- [ ] All agents running?
- [ ] Findings being collected?
- [ ] No timeout issues?

### After Review
- [ ] Findings consolidated?
- [ ] Severity assigned?
- [ ] Remediation plan created?
- [ ] Results reported?
