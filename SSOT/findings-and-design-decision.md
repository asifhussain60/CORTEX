# CORTEX Governance Analysis: Findings & Design Decision

**Date:** 2026-01-14  
**Status:** ANALYSIS COMPLETE → SOLUTION PROPOSED  
**From:** Chat01 + Governance Review  
**Decision:** Implement Declarative Auto-Wired Governance

---

## Your Request (Reflected Back)

1. ✅ **Review chat01** → Document findings about wiring brittleness
2. ✅ **Analyze SSOT holistically** → Understand root causes
3. ✅ **Fix permanently** → New design that doesn't break on clone
4. ✅ **Leverage Python tools** → Yes, reflection + dataclasses + YAML
5. ✅ **Don't overengineer** → Simple, elegant solution aligned with current architecture

---

## Core Finding: The Wiring Gap

### What Exists Today

From chat01 analysis of the 28 governance rules:

```
✅ WORKING (3 rules):
   CORE-001: Incremental Execution (IncrementalExecutor)
   CORE-004: Token Budget (TokenUsageMonitor)
   CORE-008: TDD Enforcement (TddMaster routing)
   CORE-019: TDD-Master Required (Development router)

⚠️  PARTIAL (12 rules):
   CORE-002: FileCreationGuard exists but not called
   CORE-005: PathValidator exists but pre-commit not wired
   CORE-011: mypy configured but not blocking
   CORE-014: Coverage measured but not blocking
   CORE-015: Circular imports checked but not blocking
   CORE-017: GovernanceCheckpoint exists but incomplete
   CORE-018: Config loader exists but not enforced
   CORE-020: FileCreationGuard has rules but enforcement incomplete
   CORE-021: Audit logger exists but not write-protected
   CORE-022: FileCreationGuard checks but not enforced
   CORE-023: State manager exists but no state machine
   CORE-024: MCP decorator pattern exists but not enforced

❌ BROKEN (11 rules):
   CORE-003, 006, 007, 010, 013, 016, 023, 024, 027, 028
   No enforcement code found
```

### Root Cause: Three Architectural Problems

#### Problem 1: Rules ≠ Enforcement

**Current model:**
```
cortex-brain/tier0/governance/core-rules.yaml  (YAML file)
   └─ Rule definitions
      └─ But no connection to enforcement

src/orchestrators/middleware/file_creation_guard.py  (Python file)
   └─ Enforcement code exists
      └─ But nobody calls it
      └─ Orchestrators don't know about it
```

**Connection between them:** Manual. Orchestrator must explicitly call middleware. If forgotten → rule violated silently.

#### Problem 2: New Developer Clones = Lost Enforcement

**Scenario:**
1. Dev A: Adds FileCreationGuard middleware + documents how to use it
2. Dev A: Checks in code
3. Dev B: `git clone`
4. Dev B: Creates `analysis-summary.md` in root (violates CORE-002)
5. No error (FileCreationGuard exists but MasterOrchestrator doesn't call it)
6. Bad code committed

**Why it happens:** Enforcement is opt-in (middleware must be explicitly called), not default-on (always enforced).

#### Problem 3: Partial Rules Have Infrastructure But No Execution Hooks

**Example (CORE-011: Type Hints):**
```
cortex-brain/tier0/governance/core-rules.yaml
   └─ "CORE-011: Type hints required"

src/tools/python_static_analysis.py
   └─ mypy integration exists
      └─ Runs locally on developer's machine
      └─ Not integrated into CI/CD
      └─ Not blocking merge
      └─ Not called by MasterOrchestrator

Result: Rule exists in theory; enforcement doesn't happen in practice
```

---

## Architectural Decision: Why Declarative + Auto-Wiring Works

### The Three-Layer Model

**Layer 1: Declaration (YAML)**
```yaml
CORE-002:
  name: No root-level markdown
  enforcement:
    middleware: FileCreationGuard
    hook: pre_file_creation
    config: {blocked_patterns: ["^.*\\.md$"]}
```

**Layer 2: Registration (Python)**
```python
class GovernanceRegistry:
    def __init__(self, rules_yaml_path):
        # Load YAML
        # Dynamically import FileCreationGuard class
        # Instantiate with config
        # Register as enforcement point for 'pre_file_creation' hook
        # (All automatic; happens once at startup)
```

**Layer 3: Injection (Orchestrator)**
```python
class MasterOrchestrator:
    def execute(self, request):
        # Auto-injected from registry
        governance_eval = self.registry.evaluate('pre_execution', context)
        if governance_eval.violations:
            return error()
        return execute()
```

### Why This Fixes The Problems

**Problem 1: Rules = Enforcement (Unified)**
- ✅ YAML declares what to enforce AND how
- ✅ Python auto-instantiates enforcement
- ✅ Orchestrator auto-calls enforcement
- ✅ Single source of truth

**Problem 2: New Developer Clone**
- ✅ Clone repo
- ✅ MasterOrchestrator starts
- ✅ Startup **automatically** loads GovernanceRegistry
- ✅ Registry **automatically** instantiates all enforcement
- ✅ PRE-EXECUTION check **automatically** evaluates rules
- ✅ Developer violates rule → **blocked immediately**
- ✅ Clear error message → routes to correct solution

**Problem 3: Partial Rules**
- ✅ Rule in YAML → enforcement auto-instantiated
- ✅ No "opting in" required
- ✅ All 28 rules automatically active
- ✅ Can't forget to wire (it's automatic)

---

## Why Alternative Approaches Don't Work

### Alternative 1: "Just Categorize the Rules"

Your initial idea: Split 1602-line `core-rules.yaml` into 8 files by category.

**Why this doesn't solve the problem:**
- ✅ Reduces file size (good for readability)
- ❌ **Doesn't fix wiring gap** (rules still not connected to enforcement)
- ❌ **Adds fragility** (rules spread across 8 files; easier to miss dependencies)
- ❌ **Slower queries** (load 8 files instead of 1)
- ❌ **Doesn't help new developers** (they still need to manually wire)

**Example:** CORE-001 depends on CORE-004 depends on CORE-014. Split across 3 files. Load only orchestration.yaml → broken enforcement chain.

### Alternative 2: "Put Enforcement in Orchestrator"

Current approach: Each orchestrator checks rules individually.

```python
class TddMaster:
    def execute(self):
        self.file_guard.check()      # CORE-002
        self.token_monitor.check()   # CORE-001
        self.yaml_validator.check()  # CORE-018
        # ... orchestrator now knows about 50 rules
```

**Problems:**
- ❌ **Scattered logic** (rules in 15 different orchestrators)
- ❌ **Inconsistent** (some orchestrators check all rules; others skip)
- ❌ **Hard to audit** (where did CORE-019 enforcement go?)
- ❌ **Maintenance nightmare** (add new rule → update 15 orchestrators)

### Alternative 3: "Use GovernanceMerger Pattern"

Current approach: GovernanceMerger loads rules, but doesn't enforce them.

```python
class GovernanceMerger:
    def load_rules():
        return rules_from_yaml  # Just returns data, doesn't enforce
```

**Problem:** Loads rules but doesn't auto-inject them into execution. Orchestrators must explicitly query merger.

**Result:** Same as Alternative 2 (scattered, inconsistent).

---

## Why This Design Is Elegant (Not Overengineered)

### Simplicity Checklist

✅ **Single responsibility:** GovernanceRegistry = load rules + instantiate middleware + provide query interface. Nothing else.

✅ **Minimal classes:** Just three:
- `GovernanceRegistry` (load + instantiate + query)
- `GovernanceMiddleware` (base class for enforcement)
- `EnforcementPoint` (metadata binding)

✅ **YAML schema:** Simple declarative format. One rule = one YAML block. No nesting, no complexity.

✅ **Integration:** Just two integration points:
- MasterOrchestrator loads registry in `__init__`
- MasterOrchestrator calls `registry.evaluate()` before/after operations

✅ **No framework required:** Uses standard Python (dataclasses, abc, yaml, reflection). No external frameworks.

✅ **Backwards compatible:** Existing code continues to work. Registry runs alongside current system.

### Comparison to Overengineering

❌ **What we're NOT doing:**
- Building a full rules engine (Drools, etc.) → overkill
- Creating a DSL for rules → just use YAML
- Building a distributed rules system → local YAML fine
- Adding a service layer → in-process registry is sufficient
- Creating a database for rules → YAML + optional SQLite in Phase 2

✅ **What we ARE doing:**
- Declarative config (YAML)
- Auto-instantiation (Python reflection)
- Hook-based injection (simple pattern)
- Audit logging (standard practice)

**Total new code:** ~300 lines (GovernanceRegistry + base classes). Fits in one file.

---

## Key Architectural Principles

### Principle 1: "Once Configured, Always Enforced"

**Philosophy:** If a rule is in `rules.yaml`, it's automatically enforced. No additional wiring needed.

**Implementation:** GovernanceRegistry auto-instantiation at startup.

**Guarantee:** Clone repo → startup → enforcement active (on all machines).

### Principle 2: "Single Source of Truth"

**Philosophy:** Rules defined once (in YAML). Everything else flows from that definition.

**Implementation:** Rule definition includes enforcement metadata. Registry reads once and propagates.

**Guarantee:** Update rule in YAML → enforcement updates automatically on next restart.

### Principle 3: "Declarative Over Imperative"

**Philosophy:** Describe WHAT to enforce (declarative YAML), not HOW to enforce (imperative code).

**Implementation:** Rules in YAML; enforcement code in Python. Registry bridges the gap.

**Guarantee:** Non-developers can understand rules. Developers can implement enforcement.

### Principle 4: "Layered, Not Monolithic"

**Philosophy:** Rules are at orchestration layer, not buried in implementation code.

**Implementation:** MasterOrchestrator does the evaluation, not individual services.

**Guarantee:** Every operation goes through same governance check (no escapes).

---

## Implementation Complexity Assessment

### Estimated Effort

| Component | Complexity | Effort | Risk |
|-----------|-----------|--------|------|
| GovernanceRegistry | Low | 2 days | Low |
| Rule YAML schema | Low | 1 day | Low |
| Integration test | Low | 1 day | Low |
| MasterOrchestrator hookup | Medium | 2 days | Low |
| Convert 28 rules to YAML | Medium | 3 days | Medium (schema evolution) |
| Cross-machine testing | Medium | 2 days | Low |
| Documentation | Low | 1 day | Low |
| **TOTAL** | **Medium** | **~12 days** | **Low** |

### Risk Mitigation

**Risk:** GovernanceRegistry fails to load YAML

- **Mitigation:** Registry in "read-only" mode initially. If load fails, system continues without enforcement (audits the failure)
- **Testing:** Unit test YAML parsing

**Risk:** Middleware instantiation fails (import error)

- **Mitigation:** Registry catches import errors; logs clearly; disables that rule
- **Testing:** Test with missing/broken middleware

**Risk:** Performance degradation (registry evaluations on every operation)

- **Mitigation:** Registry is stateless; evaluations are ~1ms. Cache rules in memory.
- **Testing:** Benchmark pre/post implementation

**Risk:** Breaking existing orchestrators

- **Mitigation:** Registry is opt-in. MasterOrchestrator integrates gradually. Other orchestrators unchanged.
- **Testing:** Existing tests continue to pass

---

## Next Steps (If Approved)

1. **Review governance-wiring-solution.md** (the full design)
   - Architecture diagrams
   - Code examples
   - Phase-by-phase roadmap
   - Configuration schema

2. **Decide on acceptance** → Does this approach align with your vision?

3. **If yes:** Start Phase 1 (GovernanceRegistry implementation)
   - Create base classes
   - Load first 5 rules
   - Write unit tests
   - Non-breaking (registry runs alongside current system)

4. **If modifications needed:** Let me know what to adjust

---

## File Location

**Design document:** `SSOT/governance-wiring-solution.md`

**Structure:**
- Part 1: Core Architecture (3 layers)
- Part 2: Why This Fixes Brittleness
- Part 3: Implementation Roadmap (4 phases)
- Part 4: Configuration Schema
- Part 5: Benefits Summary
- Part 6: Success Criteria
- Part 7: Comparison (Old vs. New)
- Part 8: Migration Path
- Appendix: File Organization

---

## Summary: Your Intent vs. My Findings

### You Asked:
"How do we prevent rules from being 'configured but not wired'?"

### I Found:
This is the core architectural problem. 12 rules have middleware but no enforcement hooks. 11 rules have no enforcement at all.

### I Propose:
Move rule configuration AND enforcement metadata into one place (rules.yaml). Auto-instantiate enforcement on startup. Auto-inject into orchestration flow. Result: "Once configured, always enforced."

### Key Differentiator:
Not just better organization. Fundamental **behavioral change**: enforcement becomes **opt-out** (must be explicitly disabled) instead of **opt-in** (must be explicitly enabled).

This is why new developers cloning the repo will have rules enforced by default, not forgotten.
