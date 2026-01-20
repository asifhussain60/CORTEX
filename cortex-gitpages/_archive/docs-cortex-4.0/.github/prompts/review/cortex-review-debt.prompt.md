# CORTEX Review - Technical Debt Analysis Prompt

**Role:** Identify technical debt—shortcuts taken, incomplete implementations, deferred work.

---

## Debt Categories

| Category | Indicator | Payoff Cost | Example |
|---|---|---|---|
| **TODOs** | `# TODO`, `# FIXME` | 2-4h per item | Incomplete error handling |
| **Skipped Tests** | `@pytest.mark.skip` | 1-2h per test | Edge case not tested |
| **Type Stubs** | Type `Any`, bare `type()` | 1-2h per func | Untyped parameters |
| **Duplicated Code** | Copy-pasted blocks | 2-4h per occurrence | Orchestrator patterns |
| **Missing Docs** | No docstring, outdated | 30m-2h per item | Undocumented APIs |
| **Deprecated APIs** | Old patterns, superseded | 1-3h per API | Obsolete imports |
| **Hardcoded Values** | Magic numbers, paths | 30m-1h per value | Configuration coupling |

---

## Quick Commands

- `/debt` → List all technical debt
- `/debt <category>` → Filter by category
- `/debt-payoff <item>` → How much to fix
- `/debt-priority` → Sorted by payoff/effort ratio
- `/debt-blocking` → Debt blocking other work

---

## Detection Queries

```bash
# TODO/FIXME markers
grep -rn "TODO\|FIXME\|HACK\|XXX" src/ --include="*.py"

# Skipped tests
grep -rn "@pytest.mark.skip\|@skip" tests/ --include="*.py"

# Type: Any usage
grep -rn ": Any" src/ --include="*.py"

# Missing docstrings
grep -rn "def " src/ --include="*.py" -A 1 | grep -v '"""' | grep -v "^--$"

# Duplicated code blocks (simple heuristic)
find src/ -name "*.py" -exec awk 'NR==FNR{a[$0]++; next} a[$0] > 1' {} +

# Hardcoded values
grep -rn "= ['\"][^\"]*CORTEX\|= ['\"]\/Users\|= ['\"]\/home" src/ --include="*.py"
```

---

## Debt Report Format

```
ITEM: Handle edge case in LENS protocol
CATEGORY: Incomplete Implementation
FILE: src/orchestrators/intent_router.py:234
SEVERITY: MEDIUM
EFFORT: 3h
PAYOFF: Prevents crashes on malformed input

STATUS: TODO - Deferred from PHASE-16
BLOCKER: No (nice-to-have)
NOTES: See comment on line 234; low-frequency edge case

─────────────────────────────────────

ITEM: Type hints for orchestrator dispatch
CATEGORY: Type Stubs
FILE: src/orchestrators/master_orchestrator.py
SEVERITY: LOW
EFFORT: 2h
PAYOFF: Better IDE support, fewer runtime errors

STATUS: Partial (5/12 functions)
BLOCKER: No (dev experience only)
```

---

## Debt Prioritization Matrix

| Item | Effort | Payoff | Priority | Status |
|---|---|---|---|---|
| LENS edge case | 3h | HIGH | P2 | TODO |
| Type hints (master) | 2h | MEDIUM | P3 | Partial |
| Orchestrator duplication | 4h | HIGH | P1 | TODO |
| Missing docstrings | 6h | MEDIUM | P2 | TODO |
| Hardcoded paths | 1h | HIGH | P1 | TODO |

---

## Debt Management Rules

- **P0 (Blocking):** Fix before phase lock
- **P1 (High ROI):** Target this sprint
- **P2 (Medium ROI):** Target next sprint
- **P3 (Nice-to-have):** Backlog

---

## Response Format

**✅ Preferred:**
- Debt table (item, effort, payoff, priority)
- 3-5 critical items highlighted
- Prioritization summary

**❌ Avoid:**
- Long narratives
- Full code context
- Non-prioritized lists
