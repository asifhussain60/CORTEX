# CORTEX Review - Brittleness Analysis Prompt

**Role:** Identify structural weaknesses that fail under load, edge cases, or environmental changes.

---

## Brittleness Categories

| Category | Failure Mode | Risk | Detection |
|---|---|---|---|
| **Error Handling** | Bare `except:` or silent failures | CRITICAL | grep "except:" |
| **State Management** | Non-atomic writes, lost updates | CRITICAL | grep ".write(" without atomic |
| **Resource Leaks** | Unclosed files, connections | HIGH | grep "open(" without "with" |
| **Concurrency** | Race conditions, deadlocks | HIGH | grep "threading" or "multiprocessing" |
| **Timeouts** | Infinite waits, hangs | MEDIUM | grep "request\|connect" no timeout |

---

## Quick Commands

- `/brittleness` → List all brittleness issues
- `/brittleness <category>` → Deep dive
- `/brittle-fix <issue>` → Recommended fix
- `/brittleness-audit` → Scan codebase

---

## Detection Queries

```bash
# Bare except clauses (CORE-013 violation)
grep -rn "except:" src/ --include="*.py" | grep -v "except Exception\|except \w"

# Missing error handling
grep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" src/ --include="*.py" | grep -v "with " | head -20

# Unclosed resources
grep -rn "open(" src/ --include="*.py" | grep -v "with open"

# Missing timeouts
grep -rn "requests\.\|socket\.\|urlopen" src/ --include="*.py" | grep -v "timeout" | head -15

# Potential race conditions
grep -rn "if not .* and\|if .* is None" src/ --include="*.py" | head -15
```

---

## Brittleness Report Format

```
CATEGORY: Error Handling
━━━━━━━━━━━━━━━━━━━━━━━━━━━

ISSUE: Bare except clause
SEVERITY: CRITICAL
FILE: src/orchestrators/planning_orchestrator.py:142
CODE:
  try:
    execute_phase()
  except:
    pass

FAILURE MODE: All errors silently ignored, no logging
IMPACT: Debugging impossible, silent data loss
FIX: Change to: except Exception as e: logger.error(...)

─────────────────────────────────────

CATEGORY: Resource Management
ISSUE: Unclosed file handle
SEVERITY: HIGH
FILE: src/infrastructure/config_loader.py:78
FAILURE MODE: File descriptor leak on multiple reads
IMPACT: Eventually runs out of file descriptors
FIX: Use: with open(file) as f: data = f.read()
```

---

## Brittleness Risk Matrix

| Component | Fail Mode | Likelihood | Impact | Priority |
|---|---|---|---|---|
| Database | Connection leak | MEDIUM | HIGH | P1 |
| File I/O | Non-atomic write | MEDIUM | HIGH | P1 |
| API Client | No timeout | HIGH | MEDIUM | P1 |
| Orchestrator | Race condition | LOW | CRITICAL | P2 |
| Audit Trail | Lost entries | LOW | CRITICAL | P0 |

---

## Response Format

**✅ Preferred:**
- Issue table (component, failure mode, impact)
- 3-5 findings with severity
- Fix recommendations

**❌ Avoid:**
- Full code dumps
- Lengthy explanations
- Multiple categories mixed
