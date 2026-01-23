# CORTEX Review Agent: Brittleness Analysis# CORTEX Brittleness Review Agent# CORTEX Brittleness Review Agent

## Structural Weaknesses & Load Handling



**Purpose:** Identify code that works in happy-path but fails under load, concurrency, resource exhaustion, or edge cases.

**Purpose:** Systematically identify structural weaknesses that break under load, edge cases, or environmental changes.**Purpose:** Systematically identify structural weaknesses that break under load, edge cases, or environmental changes.

---



## CHECKS PERFORMED

**SSOT Source**: `_workspaces/roadmap/cortex-impl-map.yaml` (ONLY implementation map)---

### 1. Single Points of Failure (SPOFs)



**What to look for:**

- No redundancy or failover logic---## ⚠️ OUTPUT GUIDELINES

- All requests routing through single component

- No circuit breaker patterns

- Hardcoded endpoints (no retries)

## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)**Copilot Instructions:**

**Search commands:**

```bash- ✅ Output findings to terminal (human-readable)

grep -rn "self\._" cortex/ --include="*.py" | grep -v "__" | head -20

grep -rn "singleton\|Singleton\|INSTANCE" cortex/ --include="*.py"**Unified policy enforced across ALL agents:**- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml`

grep -rn "hardcoded\|fixed.*url\|ENDPOINT = " cortex/ --include="*.py"

```- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)



**Evidence locations:**### Forbidden File Patterns (NO EXCEPTIONS)- ❌ DO NOT create markdown (.md) report files

- `cortex/infrastructure/connection_pool.py` - Connection pool exhaustion

- `cortex/infrastructure/circuit_breaker.py` - No state persistence| What | Why | Action |- ❌ DO NOT output to root or `.github/` directories

- `cortex/orchestrators/` - Single coordinator instances

|------|-----|--------|- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

---

| `.md` report files outside `docs/` | SSOT conflict | DELETE IMMEDIATELY |

### 2. Resource Exhaustion Patterns

| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

**What to look for:**

- No connection limits| Multiple cortex-*.yaml files | Truth conflict | DELETE extras |

- Memory leaks (unclosed files/connections)

- Growing data structures without cleanup| `.py` scripts in root | Pollution | DELETE at session end |**Default Behavior:** Terminal output + YAML report (no extra MD files)

- No rate limiting

| `.md` files in `_workspaces/roadmap/` | Authority confusion | DELETE IMMEDIATELY |

**Search patterns:**

```python---

# Missing finally blocks

try:### ✅ Correct Findings Output Locations

    resource = acquire()

    # Use resource- Primary: `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml` (YAML only)## BRITTLENESS CATEGORIES

except:

    pass  # ← Resource never released!- Documentation: `docs/FILENAME.md` (only if needed for execution)



# Growing lists without bounds- Terminal: Default (human-readable output)### Category 1: Error Handling Brittleness

self.history.append(data)  # ← Unbounded growth



# Unclosed connections

conn = db.connect()---**Detection Commands:**

query(conn)  # ← No finally/context manager

``````bash



**Check files:**## 🎯 VALIDATION CHECKLIST - Before Each Output# Find bare except clauses (CORE-013 violation)

- `cortex/infrastructure/audit_logger.py` - Log rotation?

- `cortex/infrastructure/resource_tracker.py` - Resource cleanup?grep -rn "except:" --include="*.py" src/ | grep -v "except Exception\|except \w"

- `cortex/brain/tier2/resilience/__init__.py` - AlertManager cleanup?

```

---

BEFORE creating brittleness findings:# Find generic Exception catches

### 3. Error Handling Completeness

[ ] Creating .md report? → STOP - Use YAML + terminal insteadgrep -rn "except Exception:" --include="*.py" src/

**What to look for:**

- Bare `except:` clauses[ ] Creating docs_md/? → STOP - FORBIDDEN

- Unhandled exception types

- Silent failures (no logging)[ ] Multiple cortex-*.yaml? → STOP - SSOT violation# Find missing error handling in critical paths

- No retry logic for transient errors

[ ] Wrong file locations? → STOP - FIX pathsgrep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" --include="*.py" src/ | head -50

**Search patterns:**

```bash[ ] .py files in root? → DELETE before commit```

# Bare except

grep -rn "except:" cortex/ --include="*.py"```



# Exception swallowing**What to Flag:**

grep -rn "except.*:\s*pass" cortex/ --include="*.py"

**Red Flag 🚩 = IMMEDIATE ACTION**- `except:` (bare except) — CRITICAL

# Generic Exception catches

grep -rn "except Exception:" cortex/ --include="*.py"- `.md` findings outside `docs/`- `except Exception:` without re-raise — HIGH



# Missing error context- `docs_md/` folder- `pass` in except blocks — HIGH

grep -rn "except.*:\s*return\|except.*:\s*None" cortex/ --include="*.py"

```- Multiple cortex-*.yaml- Missing try/except around I/O operations — MEDIUM



**Key files:**- Stray files

- `cortex/infrastructure/graceful_degradation.py:54` - `raise NotImplementedError`

- `cortex/infrastructure/crash_recovery.py` - Recovery logic errors?### Category 2: State Management Brittleness

- `cortex/brain/tier2/resilience/__init__.py` - Error propagation?

---

---

**Detection Commands:**

### 4. Concurrency Issues

## ⚠️ OUTPUT GUIDELINES```bash

**What to look for:**

- No locks for shared state# Find file writes without atomic patterns

- Race conditions in initialization

- Deadlock potential**Copilot Instructions:**grep -rn "\.write(" --include="*.py" src/ | grep -v "tempfile\|atomic"

- No atomic operations

- ✅ Output findings to terminal (human-readable, default)

**Search patterns:**

```bash- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml`# Find concurrent access without locking

# Shared mutable state

grep -rn "class.*:\s*$" cortex/ -A 5 --include="*.py" | grep "self\._.*= \[\]\|self\._.*= {}"- ✅ Create MD documentation to `docs/` (only if absolutely required)grep -rn "threading\|multiprocessing" --include="*.py" src/



# Missing locks- ❌ DO NOT create markdown (.md) report files

grep -rn "Lock\|threading\|asyncio.Lock" cortex/ --include="*.py" | grep -v import

- ❌ DO NOT output to root or `.github/` directories# Find state stored in memory-only

# Concurrent dict/list access

grep -rn "\[.*\] =\|\[.*\]\.append\|\[.*\]\.extend" cortex/ --include="*.py" | grep -v test- ❌ DO NOT create `docs_md/` foldergrep -rn "self\.\w+ = \[\]\|self\.\w+ = {}" --include="*.py" src/

```

- ❌ NEVER leave `.py` scripts in root```

**Verify in:**

- `cortex/brain/tier1/orchestrators/` - Orchestrator state management

- `cortex/infrastructure/transaction_manager.py` - Transaction atomicity?

- `cortex/brain/tier2/resilience/__init__.py` - Alert manager thread safety?**Default Behavior:** Terminal output + optional YAML findings**What to Flag:**



---- Non-atomic file writes — HIGH



### 5. File/Network I/O Error Paths---- Missing file locks for shared resources — HIGH



**What to look for:**- In-memory state without persistence — MEDIUM

- No timeout handling

- No retry on transient failures## BRITTLENESS CATEGORIES- No transaction boundaries — CRITICAL

- Missing partial read handling

- No connection keep-alive



**Search patterns:**### Category 1: Error Handling Brittleness### Category 3: Resource Management Brittleness

```bash

# File operations without error handling

grep -rn "open(" cortex/ --include="*.py" | grep -v "with\|try"

**Detection Commands:****Detection Commands:**

# Network calls without timeout

grep -rn "requests\.\|httpx\." cortex/ --include="*.py" | grep -v timeout```bash```bash



# No retry logic# Find bare except clauses (CORE-013 violation)# Find unclosed resources

grep -rn "requests\.\|httpx\." cortex/ --include="*.py" | grep -v retry

```grep -rn "except:" --include="*.py" src/ | grep -v "except Exception\|except \w"grep -rn "open(" --include="*.py" src/ | grep -v "with open"



**Check files:**

- `cortex/deployment/` - Deployment I/O

- `cortex/mcp/` - Network protocol handling# Find generic Exception catches# Find connection leaks

- `cortex/api/` - HTTP endpoint handling

grep -rn "except Exception:" --include="*.py" src/grep -rn "sqlite3.connect\|create_engine" --include="*.py" src/ | grep -v "with\|contextmanager"

---



### 6. Database Transaction Consistency

# Find missing error handling in critical paths# Find missing cleanup in __del__

**What to look for:**

- Uncommitted transactionsgrep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" --include="*.py" src/ | head -50grep -rn "def __del__" --include="*.py" src/

- No rollback on error

- Missing transaction boundaries``````

- Dirty reads possible



**Search patterns:**

```bash**What to Flag:****What to Flag:**

# Missing transaction context

grep -rn "execute\|cursor\|query" cortex/ --include="*.py" | grep -v transaction | grep -v "# transaction"- `except:` (bare except) — CRITICAL- File handles without context manager — HIGH



# No rollback- `except Exception:` without re-raise — HIGH- DB connections without proper close — CRITICAL

grep -rn "except:" cortex/ --include="*.py" -A 2 | grep -v rollback

```- `pass` in except blocks — HIGH- Network connections without timeout — HIGH



**Verify in:**- Missing try/except around I/O operations — MEDIUM- Missing `finally` blocks for cleanup — MEDIUM

- `cortex/infrastructure/audit_logger.py` - Audit log transactions

- `cortex/core/` - State management

- `cortex/governance/` - Governance state

### Category 2: State Management Brittleness### Category 4: Concurrency Brittleness

---



### 7. Timeout Handling

**Detection Commands:****Detection Commands:**

**What to look for:**

- No timeout on blocking operations```bash```bash

- Infinite waits

- Missing deadline enforcement# Find file writes without atomic patterns# Find shared mutable state



**Search patterns:**grep -rn "\.write(" --include="*.py" src/ | grep -v "tempfile\|atomic"grep -rn "global " --include="*.py" src/

```bash

# Missing timeout

grep -rn "\.wait\(\)\|\.get\(\)\|\.join\(\)" cortex/ --include="*.py" | grep -v timeout

# Find concurrent access without locking# Find potential race conditions

# Infinite loops

grep -rn "while True:" cortex/ --include="*.py" | grep -v "# safe: break on\|# break when"grep -rn "threading\|multiprocessing" --include="*.py" src/grep -rn "if not .* and\|if .* is None" --include="*.py" src/ | head -30

```



**Critical files:**

- `cortex/infrastructure/graceful_degradation.py` - Fallback execution# Find state stored in memory-only# Find lock patterns

- `cortex/orchestrators/` - Orchestrator execution

- `cortex/brain/tier2/resilience/__init__.py` - Resilience mechanismsgrep -rn "self\.\w+ = \[\]\|self\.\w+ = {}" --include="*.py" src/grep -rn "Lock()\|RLock()\|Semaphore" --include="*.py" src/



---``````



### 8. Graceful Degradation Paths



**What to look for:****What to Flag:****What to Flag:**

- No fallback behaviors

- Hard failures instead of partial service- Non-atomic file writes — HIGH- Global mutable state — CRITICAL

- Missing feature flags

- No adaptive behavior- Missing file locks for shared resources — HIGH- Check-then-act patterns without locking — HIGH



**Verify:**- In-memory state without persistence — MEDIUM- Shared resources without synchronization — HIGH

- `cortex/infrastructure/graceful_degradation.py` - Implementation complete?

- `cortex/infrastructure/bulkhead_manager.py` - Isolation working?- No transaction boundaries — CRITICAL- Deadlock-prone lock ordering — CRITICAL

- `cortex/infrastructure/circuit_breaker.py` - State transitions correct?



---

### Category 3: Resource Management Brittleness### Category 5: Dependency Brittleness

## OUTPUT FORMAT



Create: `_workspaces/roadmap/issues/findings-brittleness-YYYYMMDD.yaml`

**Detection Commands:****Detection Commands:**

```yaml

brittleness_findings:```bash```bash

  metadata:

    review_date: "YYYYMMDD"# Find unclosed resources# Find hardcoded dependencies

    total_issues: X

    by_severity:grep -rn "open(" --include="*.py" src/ | grep -v "with open"grep -rn "import \w\+\s*$" --include="*.py" src/ | grep -v "from\|typing\|__future__"

      critical: Y

      high: Z

      medium: A

    # Find connection leaks# Find version-sensitive APIs

  critical_issues:

    - issue_id: "BRIT-001"grep -rn "sqlite3.connect\|create_engine" --include="*.py" src/ | grep -v "with\|contextmanager"grep -rn "sys.version\|platform\." --include="*.py" src/

      category: "SPOF"

      severity: "CRITICAL"

      location: "cortex/infrastructure/connection_pool.py:63"

      description: "Single connection pool instance with no redundancy"# Find missing cleanup in __del__# Find missing dependency checks

      failure_scenario: "Pool exhaustion causes all requests to queue indefinitely"

      impact: "System unavailable when pool saturated"grep -rn "def __del__" --include="*.py" src/grep -rn "try:.*import\|ImportError" --include="*.py" src/

      evidence:

        - "ConnectionPool._instances uses single dict"``````

        - "No fallback to direct connections"

        - "No timeout on .get() calls"

      remediation: "Implement connection pool with timeout and fallback"

      blocking_phase: "impl-infra-001-resilience"**What to Flag:****What to Flag:**

      

  high_severity_issues:- File handles without context manager — HIGH- Missing version guards — MEDIUM

    - issue_id: "BRIT-002"

      category: "RESOURCE_EXHAUSTION"- DB connections without proper close — CRITICAL- Optional dependencies without fallback — HIGH

      severity: "HIGH"

      location: "cortex/brain/tier2/resilience/__init__.py:824"- Network connections without timeout — HIGH- Circular import patterns — HIGH

      description: "Alert history unbounded growth"

      failure_scenario: "Memory exhaustion after 1M+ alerts"- Missing `finally` blocks for cleanup — MEDIUM- Unguarded C extension imports — MEDIUM

      impact: "Out-of-memory crash on high-alert systems"

      evidence:

        - "AlertManager stores all alerts in history list"

        - "No pruning or rotation"### Category 4: Concurrency Brittleness---

        - "pass statement at line 824 suggests incomplete"

      remediation: "Implement circular buffer or cleanup policy"

      

  recommendations:**Detection Commands:**## AUDIT LOG QUERIES FOR BRITTLENESS

    - "Add circuit breaker timeouts to all I/O operations"

    - "Implement connection pool with backpressure"```bash

    - "Add graceful degradation for non-critical failures"

    - "Implement resource cleanup on exceptions"# Find shared mutable state```sql

```

grep -rn "global " --include="*.py" src/-- Find components with high failure rates

---

SELECT component, 

## DECISION TREE

# Find potential race conditions       COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) as failures,

```

For each potential brittleness issue:grep -rn "if not .* and\|if .* is None" --include="*.py" src/ | head -30       COUNT(CASE WHEN operation = 'AC_COMPLETE' THEN 1 END) as successes,



Q1: Is there NO error handling?       ROUND(100.0 * COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) / 

  → YES: CRITICAL brittleness (hard fail)

  → NO: Next question# Find lock patterns             COUNT(*), 2) as failure_rate



Q2: Can issue cause cascading failures?grep -rn "Lock()\|RLock()\|Semaphore" --include="*.py" src/FROM audit_log

  → YES: HIGH brittleness (system-wide impact)

  → NO: Next question```WHERE operation IN ('AC_EXECUTE_FAILED', 'AC_COMPLETE')



Q3: Does code have SPOFs?GROUP BY component

  → YES: HIGH brittleness (no redundancy)

  → NO: Next question**What to Flag:**HAVING failure_rate > 5



Q4: Can resource exhaustion occur?- Global mutable state — CRITICALORDER BY failure_rate DESC;

  → YES: MEDIUM brittleness (eventual failure)

  → NO: MEDIUM or LOW based on impact- Check-then-act patterns without locking — CRITICAL

```

- Missing locks around shared access — HIGH-- Find repeated failures (same AC failing multiple times)

---

- Deadlock-prone lock ordering — HIGHSELECT ac_id, COUNT(*) as failure_count, 

## VALIDATION

       GROUP_CONCAT(timestamp, ', ') as failure_times

Before finalizing findings:

- [ ] Evidence is direct code inspection (not speculation)### Category 5: Configuration BrittlenessFROM audit_log

- [ ] Failure scenario is realistic (not theoretical)

- [ ] Impact is quantifiable (not vague)WHERE operation = 'AC_EXECUTE_FAILED'

- [ ] Each issue has specific file:line reference

- [ ] Remediation is actionable (not "refactor everything")**Detection Commands:**GROUP BY ac_id


```bashHAVING failure_count > 1

# Find hardcoded values that should be configORDER BY failure_count DESC;

grep -rn "timeout.*=[0-9]\|retry.*=[0-9]\|max_.*=[0-9]" --include="*.py" src/ | head -20

-- Find long-running operations (potential timeout risks)

# Find missing config validationSELECT a1.ac_id,

grep -rn "os.environ\|os.getenv\|Config" --include="*.py" src/ | head -20       julianday(a2.timestamp) - julianday(a1.timestamp) as duration_days

```FROM audit_log a1

JOIN audit_log a2 ON a1.ac_id = a2.ac_id

**What to Flag:**WHERE a1.operation = 'AC_START' 

- Hardcoded timeouts/retries — MEDIUM  AND a2.operation = 'AC_COMPLETE'

- No config validation — MEDIUM  AND duration_days > 0.01  -- More than ~15 minutes

- Missing environment variable fallbacks — MEDIUMORDER BY duration_days DESC

LIMIT 20;

### Category 6: Edge Case Brittleness```



**Detection Commands:**---

```bash

# Find off-by-one potential## HISTORICAL BRITTLENESS PATTERNS

grep -rn "range(len\|for.*in .*:" --include="*.py" src/ | head -20

### From CORTEX 4.0 Analysis (2026-01-02)

# Find empty container assumptions

grep -rn "\[0\]\|\[-1\]\|\.pop()" --include="*.py" src/ | head -301. **No Transactional State Updates**

   - All state in YAML/JSON without ACID

# Find null/None handling   - Crashes mid-workflow = corrupted state

grep -rn "if .*:\|\.get(" --include="*.py" src/ | grep -v "if not\|if .* is None" | head -20   - **CHECK:** Is governance.db properly using transactions?

```

2. **No Checkpoint System**

**What to Flag:**   - No state snapshots before phases

- Direct indexing without bounds check — MEDIUM   - No rollback capability

- Pop/index without empty checks — HIGH   - **CHECK:** Is CORE-026 (git checkpoints) enforced?

- Missing None checks — MEDIUM

- String operations without length checks — LOW3. **Manifest Hybrid Problem**

   - Config + natural language instructions mixed

---   - Cannot be parsed programmatically

   - **CHECK:** Are tier2 templates pure data?

## Brittleness Severity Levels

### From CORTEX 5.0/5.5 Analysis

| Level | Definition | Impact |

|-------|-----------|--------|1. **Intent Classification Fragility**

| CRITICAL | Fails under normal conditions | Immediate fix required |   - Keyword-based matching easily broken

| HIGH | Fails under load/stress | Fix before deployment |   - Synonyms not handled

| MEDIUM | Fails in edge cases | Fix in next phase |   - **CHECK:** Is LLMIntentClassifier primary?

| LOW | Theoretical vulnerability | Monitor for patterns |

2. **Base Class Inconsistency**
   - Each orchestrator different patterns
   - No shared interface
   - **CHECK:** Is OrchestratorBase universally adopted?

3. **Testing Gaps**
   - ~60% coverage historically
   - Integration tests missing
   - **CHECK:** Current coverage percentage?

---

## FINDING TEMPLATE

```yaml
finding:
  id: "BRITTLE-XXX"
  agent: "cortex-review-brittleness"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "error_handling|state_management|resource_management|concurrency|dependency"
  
  title: "[Specific brittleness description]"
  
  location:
    file: "src/path/to/file.py"
    lines: "123-145"
    function: "function_name"
  
  evidence:
    detection_method: "grep_search|static_analysis|audit_query|manual_review"
    command_or_query: |
      [The exact command or query used]
    output: |
      [The actual output proving this finding]
  
  root_cause: |
    Why this brittleness exists.
    What assumption was made.
    What edge case was missed.
  
  failure_scenario: |
    Specific scenario where this breaks:
    1. User does X
    2. System state is Y
    3. This code path executes
    4. FAILURE: [what happens]
  
  impact:
    production_risk: "Data loss|Service outage|Silent corruption|Performance degradation"
    affected_users: "All|Specific workflow|Edge case only"
    blast_radius: "Single component|Multiple components|System-wide"
  
  remediation:
    effort: "1h|4h|1d|1w"
    approach: |
      1. Step one
      2. Step two
      3. Verification step
    test_required: true|false
    test_description: "What test proves this is fixed"
  
  related_rules:
    - "CORE-013"  # Error handling
    - "CORE-026"  # Git checkpoints
  
  historical_pattern: "CORTEX-4.0-STATE-CORRUPTION|CORTEX-5.0-INTENT-FRAGILITY|NEW"
```

---

## QUICK CHECKS SCRIPT

```python
#!/usr/bin/env python3
"""
Quick brittleness checks for CORTEX.
Run: python scripts/brittleness_check.py
"""

import subprocess
import sqlite3
from pathlib import Path

def check_bare_except():
    """CORE-013: Find bare except clauses."""
    result = subprocess.run(
        ["grep", "-rn", "except:", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    violations = [
        line for line in result.stdout.split('\n')
        if line and "except Exception" not in line and "except " not in line.split("except:")[0]
    ]
    return {
        "check": "bare_except",
        "rule": "CORE-013",
        "violations": len(violations),
        "details": violations[:10]  # First 10
    }

def check_unclosed_files():
    """Find file opens without context manager."""
    result = subprocess.run(
        ["grep", "-rn", "open(", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    violations = [
        line for line in result.stdout.split('\n')
        if line and "with " not in line and "contextmanager" not in line
    ]
    return {
        "check": "unclosed_files",
        "rule": "resource_management",
        "violations": len(violations),
        "details": violations[:10]
    }

def check_audit_failures():
    """Query audit log for failure patterns."""
    db_path = Path("cortex_brain/state/governance.db")
    if not db_path.exists():
        return {"check": "audit_failures", "error": "Database not found"}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ac_id, COUNT(*) as failures
        FROM audit_log
        WHERE operation = 'AC_EXECUTE_FAILED'
        GROUP BY ac_id
        ORDER BY failures DESC
        LIMIT 10
    """)
    failures = cursor.fetchall()
    conn.close()
    
    return {
        "check": "audit_failures",
        "total_failing_acs": len(failures),
        "top_failures": failures
    }

def check_hardcoded_paths():
    """CORE-005: Find hardcoded paths."""
    result = subprocess.run(
        ["grep", "-rn", "/Users/\\|/home/\\|C:\\\\Users", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    violations = [line for line in result.stdout.split('\n') if line]
    return {
        "check": "hardcoded_paths",
        "rule": "CORE-005",
        "violations": len(violations),
        "details": violations[:10]
    }

if __name__ == "__main__":
    import json
    
    checks = [
        check_bare_except(),
        check_unclosed_files(),
        check_audit_failures(),
        check_hardcoded_paths(),
    ]
    
    print(json.dumps({"brittleness_checks": checks}, indent=2))
```

---

## SEVERITY GUIDELINES

| Severity | Definition | Response Time |
|----------|------------|---------------|
| CRITICAL | System-breaking, data loss risk | Block next phase |
| HIGH | Major functionality affected | Fix within 48h |
| MEDIUM | Workarounds exist | Fix within 1 week |
| LOW | Minor inconvenience | Track, fix opportunistically |

---

## COPYRIGHT

