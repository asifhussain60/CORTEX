# CORTEX Brittleness Review Agent

**Purpose:** Systematically identify structural weaknesses that break under load, edge cases, or environmental changes.

## BRITTLENESS CATEGORIES

### Category 1: Error Handling Brittleness

**Detection Commands:**
```bash
# Find bare except clauses (CORE-013 violation)
grep -rn "except:" --include="*.py" src/ | grep -v "except Exception\|except \w"

# Find generic Exception catches
grep -rn "except Exception:" --include="*.py" src/

# Find missing error handling in critical paths
grep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" --include="*.py" src/ | head -50
```

**What to Flag:**
- `except:` (bare except) — CRITICAL
- `except Exception:` without re-raise — HIGH
- `pass` in except blocks — HIGH
- Missing try/except around I/O operations — MEDIUM

### Category 2: State Management Brittleness

**Detection Commands:**
```bash
# Find file writes without atomic patterns
grep -rn "\.write(" --include="*.py" src/ | grep -v "tempfile\|atomic"

# Find concurrent access without locking
grep -rn "threading\|multiprocessing" --include="*.py" src/

# Find state stored in memory-only
grep -rn "self\.\w+ = \[\]\|self\.\w+ = {}" --include="*.py" src/
```

**What to Flag:**
- Non-atomic file writes — HIGH
- Missing file locks for shared resources — HIGH
- In-memory state without persistence — MEDIUM
- No transaction boundaries — CRITICAL

### Category 3: Resource Management Brittleness

**Detection Commands:**
```bash
# Find unclosed resources
grep -rn "open(" --include="*.py" src/ | grep -v "with open"

# Find connection leaks
grep -rn "sqlite3.connect\|create_engine" --include="*.py" src/ | grep -v "with\|contextmanager"

# Find missing cleanup in __del__
grep -rn "def __del__" --include="*.py" src/
```

**What to Flag:**
- File handles without context manager — HIGH
- DB connections without proper close — CRITICAL
- Network connections without timeout — HIGH
- Missing `finally` blocks for cleanup — MEDIUM

### Category 4: Concurrency Brittleness

**Detection Commands:**
```bash
# Find shared mutable state
grep -rn "global " --include="*.py" src/

# Find potential race conditions
grep -rn "if not .* and\|if .* is None" --include="*.py" src/ | head -30

# Find lock patterns
grep -rn "Lock()\|RLock()\|Semaphore" --include="*.py" src/
```

**What to Flag:**
- Global mutable state — CRITICAL
- Check-then-act patterns without locking — HIGH
- Shared resources without synchronization — HIGH
- Deadlock-prone lock ordering — CRITICAL

### Category 5: Dependency Brittleness

**Detection Commands:**
```bash
# Find hardcoded dependencies
grep -rn "import \w\+\s*$" --include="*.py" src/ | grep -v "from\|typing\|__future__"

# Find version-sensitive APIs
grep -rn "sys.version\|platform\." --include="*.py" src/

# Find missing dependency checks
grep -rn "try:.*import\|ImportError" --include="*.py" src/
```

**What to Flag:**
- Missing version guards — MEDIUM
- Optional dependencies without fallback — HIGH
- Circular import patterns — HIGH
- Unguarded C extension imports — MEDIUM

---

## AUDIT LOG QUERIES FOR BRITTLENESS

```sql
-- Find components with high failure rates
SELECT component, 
       COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) as failures,
       COUNT(CASE WHEN operation = 'AC_COMPLETE' THEN 1 END) as successes,
       ROUND(100.0 * COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) / 
             COUNT(*), 2) as failure_rate
FROM audit_log
WHERE operation IN ('AC_EXECUTE_FAILED', 'AC_COMPLETE')
GROUP BY component
HAVING failure_rate > 5
ORDER BY failure_rate DESC;

-- Find repeated failures (same AC failing multiple times)
SELECT ac_id, COUNT(*) as failure_count, 
       GROUP_CONCAT(timestamp, ', ') as failure_times
FROM audit_log
WHERE operation = 'AC_EXECUTE_FAILED'
GROUP BY ac_id
HAVING failure_count > 1
ORDER BY failure_count DESC;

-- Find long-running operations (potential timeout risks)
SELECT a1.ac_id,
       julianday(a2.timestamp) - julianday(a1.timestamp) as duration_days
FROM audit_log a1
JOIN audit_log a2 ON a1.ac_id = a2.ac_id
WHERE a1.operation = 'AC_START' 
  AND a2.operation = 'AC_COMPLETE'
  AND duration_days > 0.01  -- More than ~15 minutes
ORDER BY duration_days DESC
LIMIT 20;
```

---

## HISTORICAL BRITTLENESS PATTERNS

### From CORTEX 4.0 Analysis (2026-01-02)

1. **No Transactional State Updates**
   - All state in YAML/JSON without ACID
   - Crashes mid-workflow = corrupted state
   - **CHECK:** Is governance.db properly using transactions?

2. **No Checkpoint System**
   - No state snapshots before phases
   - No rollback capability
   - **CHECK:** Is CORE-026 (git checkpoints) enforced?

3. **Manifest Hybrid Problem**
   - Config + natural language instructions mixed
   - Cannot be parsed programmatically
   - **CHECK:** Are tier2 templates pure data?

### From CORTEX 5.0/5.5 Analysis

1. **Intent Classification Fragility**
   - Keyword-based matching easily broken
   - Synonyms not handled
   - **CHECK:** Is LLMIntentClassifier primary?

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

Copyright © 2025-2026 Asif Hussain. All rights reserved.
