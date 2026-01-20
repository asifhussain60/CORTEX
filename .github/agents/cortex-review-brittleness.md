# CORTEX Brittleness Review Agent# CORTEX Brittleness Review Agent



**Purpose:** Systematically identify structural weaknesses that break under load, edge cases, or environmental changes.**Purpose:** Systematically identify structural weaknesses that break under load, edge cases, or environmental changes.



**SSOT Source**: `_workspaces/roadmap/cortex-impl-map.yaml` (ONLY implementation map)---



---## ⚠️ OUTPUT GUIDELINES



## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)**Copilot Instructions:**

- ✅ Output findings to terminal (human-readable)

**Unified policy enforced across ALL agents:**- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml`

- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)

### Forbidden File Patterns (NO EXCEPTIONS)- ❌ DO NOT create markdown (.md) report files

| What | Why | Action |- ❌ DO NOT output to root or `.github/` directories

|------|-----|--------|- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

| `.md` report files outside `docs/` | SSOT conflict | DELETE IMMEDIATELY |

| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

| Multiple cortex-*.yaml files | Truth conflict | DELETE extras |

| `.py` scripts in root | Pollution | DELETE at session end |**Default Behavior:** Terminal output + YAML report (no extra MD files)

| `.md` files in `_workspaces/roadmap/` | Authority confusion | DELETE IMMEDIATELY |

---

### ✅ Correct Findings Output Locations

- Primary: `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml` (YAML only)## BRITTLENESS CATEGORIES

- Documentation: `docs/FILENAME.md` (only if needed for execution)

- Terminal: Default (human-readable output)### Category 1: Error Handling Brittleness



---**Detection Commands:**

```bash

## 🎯 VALIDATION CHECKLIST - Before Each Output# Find bare except clauses (CORE-013 violation)

grep -rn "except:" --include="*.py" src/ | grep -v "except Exception\|except \w"

```

BEFORE creating brittleness findings:# Find generic Exception catches

[ ] Creating .md report? → STOP - Use YAML + terminal insteadgrep -rn "except Exception:" --include="*.py" src/

[ ] Creating docs_md/? → STOP - FORBIDDEN

[ ] Multiple cortex-*.yaml? → STOP - SSOT violation# Find missing error handling in critical paths

[ ] Wrong file locations? → STOP - FIX pathsgrep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" --include="*.py" src/ | head -50

[ ] .py files in root? → DELETE before commit```

```

**What to Flag:**

**Red Flag 🚩 = IMMEDIATE ACTION**- `except:` (bare except) — CRITICAL

- `.md` findings outside `docs/`- `except Exception:` without re-raise — HIGH

- `docs_md/` folder- `pass` in except blocks — HIGH

- Multiple cortex-*.yaml- Missing try/except around I/O operations — MEDIUM

- Stray files

### Category 2: State Management Brittleness

---

**Detection Commands:**

## ⚠️ OUTPUT GUIDELINES```bash

# Find file writes without atomic patterns

**Copilot Instructions:**grep -rn "\.write(" --include="*.py" src/ | grep -v "tempfile\|atomic"

- ✅ Output findings to terminal (human-readable, default)

- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-BRIT-YYYYMMDD.yaml`# Find concurrent access without locking

- ✅ Create MD documentation to `docs/` (only if absolutely required)grep -rn "threading\|multiprocessing" --include="*.py" src/

- ❌ DO NOT create markdown (.md) report files

- ❌ DO NOT output to root or `.github/` directories# Find state stored in memory-only

- ❌ DO NOT create `docs_md/` foldergrep -rn "self\.\w+ = \[\]\|self\.\w+ = {}" --include="*.py" src/

- ❌ NEVER leave `.py` scripts in root```



**Default Behavior:** Terminal output + optional YAML findings**What to Flag:**

- Non-atomic file writes — HIGH

---- Missing file locks for shared resources — HIGH

- In-memory state without persistence — MEDIUM

## BRITTLENESS CATEGORIES- No transaction boundaries — CRITICAL



### Category 1: Error Handling Brittleness### Category 3: Resource Management Brittleness



**Detection Commands:****Detection Commands:**

```bash```bash

# Find bare except clauses (CORE-013 violation)# Find unclosed resources

grep -rn "except:" --include="*.py" src/ | grep -v "except Exception\|except \w"grep -rn "open(" --include="*.py" src/ | grep -v "with open"



# Find generic Exception catches# Find connection leaks

grep -rn "except Exception:" --include="*.py" src/grep -rn "sqlite3.connect\|create_engine" --include="*.py" src/ | grep -v "with\|contextmanager"



# Find missing error handling in critical paths# Find missing cleanup in __del__

grep -rn "open(\|sqlite3.connect\|requests\.\|subprocess" --include="*.py" src/ | head -50grep -rn "def __del__" --include="*.py" src/

``````



**What to Flag:****What to Flag:**

- `except:` (bare except) — CRITICAL- File handles without context manager — HIGH

- `except Exception:` without re-raise — HIGH- DB connections without proper close — CRITICAL

- `pass` in except blocks — HIGH- Network connections without timeout — HIGH

- Missing try/except around I/O operations — MEDIUM- Missing `finally` blocks for cleanup — MEDIUM



### Category 2: State Management Brittleness### Category 4: Concurrency Brittleness



**Detection Commands:****Detection Commands:**

```bash```bash

# Find file writes without atomic patterns# Find shared mutable state

grep -rn "\.write(" --include="*.py" src/ | grep -v "tempfile\|atomic"grep -rn "global " --include="*.py" src/



# Find concurrent access without locking# Find potential race conditions

grep -rn "threading\|multiprocessing" --include="*.py" src/grep -rn "if not .* and\|if .* is None" --include="*.py" src/ | head -30



# Find state stored in memory-only# Find lock patterns

grep -rn "self\.\w+ = \[\]\|self\.\w+ = {}" --include="*.py" src/grep -rn "Lock()\|RLock()\|Semaphore" --include="*.py" src/

``````



**What to Flag:****What to Flag:**

- Non-atomic file writes — HIGH- Global mutable state — CRITICAL

- Missing file locks for shared resources — HIGH- Check-then-act patterns without locking — HIGH

- In-memory state without persistence — MEDIUM- Shared resources without synchronization — HIGH

- No transaction boundaries — CRITICAL- Deadlock-prone lock ordering — CRITICAL



### Category 3: Resource Management Brittleness### Category 5: Dependency Brittleness



**Detection Commands:****Detection Commands:**

```bash```bash

# Find unclosed resources# Find hardcoded dependencies

grep -rn "open(" --include="*.py" src/ | grep -v "with open"grep -rn "import \w\+\s*$" --include="*.py" src/ | grep -v "from\|typing\|__future__"



# Find connection leaks# Find version-sensitive APIs

grep -rn "sqlite3.connect\|create_engine" --include="*.py" src/ | grep -v "with\|contextmanager"grep -rn "sys.version\|platform\." --include="*.py" src/



# Find missing cleanup in __del__# Find missing dependency checks

grep -rn "def __del__" --include="*.py" src/grep -rn "try:.*import\|ImportError" --include="*.py" src/

``````



**What to Flag:****What to Flag:**

- File handles without context manager — HIGH- Missing version guards — MEDIUM

- DB connections without proper close — CRITICAL- Optional dependencies without fallback — HIGH

- Network connections without timeout — HIGH- Circular import patterns — HIGH

- Missing `finally` blocks for cleanup — MEDIUM- Unguarded C extension imports — MEDIUM



### Category 4: Concurrency Brittleness---



**Detection Commands:**## AUDIT LOG QUERIES FOR BRITTLENESS

```bash

# Find shared mutable state```sql

grep -rn "global " --include="*.py" src/-- Find components with high failure rates

SELECT component, 

# Find potential race conditions       COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) as failures,

grep -rn "if not .* and\|if .* is None" --include="*.py" src/ | head -30       COUNT(CASE WHEN operation = 'AC_COMPLETE' THEN 1 END) as successes,

       ROUND(100.0 * COUNT(CASE WHEN operation = 'AC_EXECUTE_FAILED' THEN 1 END) / 

# Find lock patterns             COUNT(*), 2) as failure_rate

grep -rn "Lock()\|RLock()\|Semaphore" --include="*.py" src/FROM audit_log

```WHERE operation IN ('AC_EXECUTE_FAILED', 'AC_COMPLETE')

GROUP BY component

**What to Flag:**HAVING failure_rate > 5

- Global mutable state — CRITICALORDER BY failure_rate DESC;

- Check-then-act patterns without locking — CRITICAL

- Missing locks around shared access — HIGH-- Find repeated failures (same AC failing multiple times)

- Deadlock-prone lock ordering — HIGHSELECT ac_id, COUNT(*) as failure_count, 

       GROUP_CONCAT(timestamp, ', ') as failure_times

### Category 5: Configuration BrittlenessFROM audit_log

WHERE operation = 'AC_EXECUTE_FAILED'

**Detection Commands:**GROUP BY ac_id

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

Copyright © 2025-2026 Asif Hussain. All rights reserved.
