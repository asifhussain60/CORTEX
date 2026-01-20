# CORTEX Assumptions Review Agent# CORTEX Assumptions Review Agent



**Purpose:** Identify hidden assumptions in the codebase that could break in different environments, configurations, or usage patterns.**Purpose:** Identify hidden assumptions in the codebase that could break in different environments, configurations, or usage patterns.



**SSOT Source**: `_workspaces/roadmap/cortex-master.yaml` (ONLY master plan)---



---## ⚠️ OUTPUT GUIDELINES



## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)**Copilot Instructions:**

- ✅ Output findings to terminal (human-readable)

**Unified policy enforced across ALL agents (no exceptions):**- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-ASM-YYYYMMDD.yaml`

- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)

### Forbidden File Patterns (ZERO TOLERANCE)- ❌ DO NOT create markdown (.md) report files

| What | Why | Action |- ❌ DO NOT output to root or `.github/` directories

|------|-----|--------|- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

| `.md` files anywhere except `docs/` | SSOT conflict | FIX IMMEDIATELY |

| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

| Multiple cortex-*.yaml files | Truth conflict | DELETE extra files |

| `.md` findings outside `docs/` | Authority confusion | DELETE immediately |**Default Behavior:** Terminal output + YAML report (no extra MD files)

| `.py` scripts in root | Cleanup violation | DELETE at end of session |

---

### ✅ Findings Output Locations (YAML ONLY)

- Primary: `_workspaces/roadmap/issues/Findings-ASM-YYYYMMDD.yaml`## ASSUMPTION CATEGORIES

- If MD needed: `docs/FILENAME.md` (only for complex execution guides)

- Terminal: Default (human-readable analysis)### Category 1: Platform Assumptions



---**Detection Commands:**

```bash

## 🎯 VALIDATION CHECKLIST - Before Each Output# Find platform-specific code

grep -rn "platform\|sys.platform\|os.name\|darwin\|linux\|win32" --include="*.py" src/

```

BEFORE creating findings:# Find path separator assumptions

[ ] Creating .md report? → STOP - Use YAML + terminal outputgrep -rn "\\\\\\\\\\|/\\|os.sep\|pathlib" --include="*.py" src/ | head -30

[ ] Creating docs_md/? → STOP - FORBIDDEN

[ ] Multiple YAML sources? → STOP - Use cortex-master.yaml ONLY# Find shell assumptions

[ ] Wrong file locations? → STOP - FIX pathsgrep -rn "subprocess\|os.system\|Popen" --include="*.py" src/ | grep -v "shell=False"

[ ] .py scripts in root? → DELETE before commit```

```

**What to Flag:**

**Red Flag 🚩 = STOP & FIX**- Hardcoded `/` for paths (use `pathlib`) — MEDIUM

- `.md` findings files outside `docs/`- Platform-specific executables assumed — HIGH

- `docs_md/` folder created- Shell=True with hardcoded commands — HIGH

- Multiple cortex-*.yaml in use- macOS-specific features used without guards — HIGH

- Stray files in root

### Category 2: Python Version Assumptions

---

**Detection Commands:**

## ⚠️ OUTPUT GUIDELINES```bash

# Check minimum Python version

**Copilot Instructions:**grep -rn "python_requires\|sys.version" --include="*.py" --include="setup.py" --include="pyproject.toml" .

- ✅ Output findings to terminal (human-readable, default)

- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-ASM-YYYYMMDD.yaml`# Find f-strings (Python 3.6+)

- ✅ Create MD documentation to `docs/` (only if absolutely required)grep -rn 'f"' --include="*.py" src/ | head -10

- ❌ DO NOT create markdown (.md) report files

- ❌ DO NOT output to root or `.github/` directories# Find walrus operator (Python 3.8+)

- ❌ DO NOT create `docs_md/` foldergrep -rn ":=" --include="*.py" src/

- ❌ NEVER leave `.py` scripts in root after session

# Find match statements (Python 3.10+)

**Default Behavior:** Terminal output + optional YAML findings (minimal file creation)grep -rn "match \w\+:" --include="*.py" src/

```

---

**What to Flag:**

## ASSUMPTION CATEGORIES- Python 3.10+ features without guards — MEDIUM

- No `python_requires` in setup — LOW

### Category 1: Platform Assumptions- Deprecated APIs used — HIGH



**Detection Commands:**### Category 3: Environment Assumptions

```bash

# Find platform-specific code**Detection Commands:**

grep -rn "platform\|sys.platform\|os.name\|darwin\|linux\|win32" --include="*.py" src/```bash

# Find environment variable usage

# Find path separator assumptionsgrep -rn "os.environ\|os.getenv\|environ\[" --include="*.py" src/

grep -rn "\\\\\\\|/\|os.sep\|pathlib" --include="*.py" src/ | head -30

# Find missing default values

# Find shell assumptionsgrep -rn "os.getenv(" --include="*.py" src/ | grep -v ", "

grep -rn "subprocess\|os.system\|Popen" --include="*.py" src/ | grep -v "shell=False"

```# Find file system assumptions

grep -rn "os.path.exists\|Path.*exists" --include="*.py" src/ | head -30

**What to Flag:**```

- Hardcoded `/` for paths (use `pathlib`) — MEDIUM

- Platform-specific executables assumed — HIGH**What to Flag:**

- Shell=True with hardcoded commands — HIGH- Required env vars without defaults — HIGH

- macOS-specific features used without guards — HIGH- File existence assumed without check — HIGH

- Working directory assumptions — MEDIUM

### Category 2: Python Version Assumptions- Home directory assumptions — MEDIUM



**Detection Commands:**### Category 4: Dependency Assumptions

```bash

# Check minimum Python version**Detection Commands:**

grep -rn "python_requires\|sys.version" --include="*.py" --include="setup.py" --include="pyproject.toml" .```bash

# Find imports without try/except

# Find version-specific importsgrep -rn "^import \|^from " --include="*.py" src/ | grep -v "typing\|__future__" | head -50

grep -rn "from __future__\|typing_extensions\|backports" --include="*.py" src/ | head -20

# Find optional dependencies

# Find f-string usage (Python 3.6+)grep -rn "try:.*import\|except ImportError" --include="*.py" src/

grep -rn 'f".*{.*}"\|f'"'"'.*{.*}'"'"'' --include="*.py" src/ | wc -l

```# Check requirements.txt for loose versions

grep -v "==" requirements.txt | grep -v "^#\|^$"

**What to Flag:**```

- No python_requires in setup.py — MEDIUM

- Type hints with no Python 3.5+ note — MEDIUM**What to Flag:**

- F-strings without Python 3.6+ requirement — LOW- Missing ImportError handling for optional deps — HIGH

- Unpinned dependencies — MEDIUM

### Category 3: Dependency Assumptions- Circular import risks — HIGH

- C extension imports without fallback — HIGH

**Detection Commands:**

```bash### Category 5: Network/Service Assumptions

# Find optional imports without try/except

grep -rn "^import\|^from" --include="*.py" src/ | head -30**Detection Commands:**

```bash

# Find hardcoded versions# Find network operations

grep -rn "== [0-9]\|< [0-9]\|> [0-9]" --include="setup.py" --include="requirements.txt" --include="pyproject.toml"grep -rn "requests\.\|http\|socket\|urllib" --include="*.py" src/



# Find missing requirements.txt entries# Find timeout settings

```grep -rn "timeout" --include="*.py" src/



**What to Flag:**# Find hardcoded URLs

- Missing try/except for optional dependencies — MEDIUMgrep -rn "http://\|https://" --include="*.py" src/

- Pinned versions causing compatibility issues — LOW```

- Missing from requirements.txt — CRITICAL

**What to Flag:**

### Category 4: Environment Assumptions- Network calls without timeout — HIGH

- Hardcoded URLs/endpoints — HIGH

**Detection Commands:**- Missing offline fallback — MEDIUM

```bash- SSL verification disabled — CRITICAL

# Find hardcoded environment paths

grep -rn "/home/\|/Users/\|C:\\\\\|/var/\|/opt/" --include="*.py" src/### Category 6: Concurrency Assumptions



# Find hardcoded server addresses**Detection Commands:**

grep -rn "localhost\|127.0.0.1\|hardcoded.*host\|hardcoded.*port" --include="*.py" src/ | head -20```bash

# Find threading usage

# Find database path assumptionsgrep -rn "threading\|asyncio\|multiprocessing" --include="*.py" src/

grep -rn "\.db\|\.sqlite\|data\.db" --include="*.py" src/ | grep -v "tests/" | head -20

```# Find shared state

grep -rn "global \|cls\.\w\+ =" --include="*.py" src/

**What to Flag:**

- Hardcoded user paths — HIGH# Find async without proper handling

- localhost assumptions for APIs — MEDIUMgrep -rn "async def\|await " --include="*.py" src/

- Hardcoded DB paths — HIGH```

- No environment variable fallbacks — MEDIUM

**What to Flag:**

### Category 5: Permission Assumptions- Thread-safety assumptions — HIGH

- Async operations without proper await — HIGH

**Detection Commands:**- Shared mutable state — CRITICAL

```bash- GIL assumptions for parallelism — MEDIUM

# Find write operations assuming permissions

grep -rn "\.write(\|mkdir\|rmdir" --include="*.py" src/ | head -30### Category 7: Database Assumptions



# Find directory assumptions**Detection Commands:**

grep -rn "getcwd\|chdir" --include="*.py" src/```bash

# Find SQLite usage

# Find file permission assumptionsgrep -rn "sqlite3\|sqlalchemy" --include="*.py" src/

grep -rn "chmod\|0o[0-7]{3}" --include="*.py" src/

```# Find transaction assumptions

grep -rn "commit\|rollback\|BEGIN\|TRANSACTION" --include="*.py" src/

**What to Flag:**

- Write operations without permission checks — MEDIUM# Find connection management

- Directory assumptions without fallback — MEDIUMgrep -rn "connect(\|create_engine" --include="*.py" src/

- No error handling for permission denied — HIGH```



### Category 6: Runtime State Assumptions**What to Flag:**

- SQLite assumed (not configurable) — MEDIUM

**Detection Commands:**- Missing transaction boundaries — HIGH

```bash- Connection leaks — CRITICAL

# Find state assumptions (module-level)- Concurrent write assumptions — HIGH

grep -rn "^[A-Z_]* = \[\]\|^[A-Z_]* = {}" --include="*.py" src/

---

# Find singleton assumptions

grep -rn "class.*Singleton\|instance = None\|_instance" --include="*.py" src/ | head -20## FINDING TEMPLATE



# Find cache assumptions```yaml

grep -rn "@cache\|@lru_cache\|cache = {}" --include="*.py" src/finding:

```  id: "ASSUME-XXX"

  agent: "cortex-review-assumptions"

**What to Flag:**  severity: "CRITICAL|HIGH|MEDIUM|LOW"

- Global mutable state — CRITICAL  category: "platform|python_version|environment|dependency|network|concurrency|database"

- Singleton pattern without thread safety — HIGH  

- Unbounded caches — MEDIUM  title: "[Specific assumption description]"

- Module-level initialization side effects — HIGH  

  assumption: |

---    What is assumed to be true.

    Why this assumption exists.

## Assumption Severity Levels  

  location:

| Level | Definition | Action |    file: "src/path/to/file.py"

|-------|-----------|--------|    lines: "123-145"

| CRITICAL | Breaks in different environment | Must fix immediately |    code_pattern: "[The specific code making this assumption]"

| HIGH | May break in some scenarios | Fix in next phase |  

| MEDIUM | Potential issue, needs verification | Document assumption |  evidence:

| LOW | Minor inconsistency | Consider for next pass |    detection_method: "code_analysis|grep_search|manual_review"

    command: |
      [Command used to find this]
    output: |
      [Actual output]
  
  breaks_when:
    - scenario: "Running on Windows"
      failure_mode: "Path separator causes FileNotFoundError"
    - scenario: "Running on Python 3.9"
      failure_mode: "match statement causes SyntaxError"
  
  environments_affected:
    - "Windows"
    - "Linux CI/CD"
    - "Python 3.9"
    - "Air-gapped network"
  
  current_handling: "None|Partial|Adequate"
  handling_details: |
    What guards currently exist (if any).
  
  impact:
    failure_visibility: "Immediate crash|Silent failure|Degraded performance"
    user_experience: "How users experience this when broken"
    recovery_path: "How to recover if this breaks"
  
  remediation:
    effort: "1h|4h|1d|1w"
    approach: |
      1. Add platform check at [location]
      2. Provide fallback for [scenario]
      3. Add test for [environment]
    test_required: true
    test_environments: ["Windows", "Linux", "Python 3.9"]
```

---

## ASSUMPTIONS FROM HISTORY

### CORTEX 4.0/5.0/5.5 Historical Assumptions That Broke:

1. **macOS-only Development**
   - Hardcoded `/Users/asifhussain/` paths
   - Broke: Any other developer, CI/CD
   - Fix: CORE-005 (path portability)

2. **Python 3.10+ Assumed**
   - match/case statements used
   - Broke: Python 3.9 environments
   - Fix: Version guards

3. **SQLite Always Available**
   - No fallback database
   - Broke: None yet, but risk exists
   - Fix: Configurable database backend

4. **Network Always Available**
   - LLM calls without offline handling
   - Broke: Air-gapped environments
   - Fix: Graceful degradation

5. **Single User Assumption**
   - No concurrent access handling
   - Broke: Shared development environments
   - Fix: File locking (partially done)

---

## QUICK CHECK SCRIPT

```python
#!/usr/bin/env python3
"""Check for hidden assumptions in CORTEX."""

import subprocess
import re

def check_platform_assumptions():
    """Find platform-specific code."""
    result = subprocess.run(
        ["grep", "-rn", "darwin\\|win32\\|linux", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    lines = [l for l in result.stdout.split('\n') if l]
    return {
        "check": "platform_assumptions",
        "platform_specific_code": len(lines),
        "details": lines[:10]
    }

def check_env_vars():
    """Find environment variable usage."""
    result = subprocess.run(
        ["grep", "-rn", "os.getenv\\|os.environ", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    
    # Find those without defaults
    no_default = [
        l for l in result.stdout.split('\n')
        if 'getenv' in l and l.count(',') == 0 and l  # No second arg = no default
    ]
    
    return {
        "check": "env_vars",
        "total_env_usage": len([l for l in result.stdout.split('\n') if l]),
        "without_defaults": len(no_default),
        "details": no_default[:10]
    }

def check_network_timeouts():
    """Find network calls without timeouts."""
    result = subprocess.run(
        ["grep", "-rn", "requests\\.", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    
    # Find those without timeout parameter
    no_timeout = [
        l for l in result.stdout.split('\n')
        if l and 'timeout' not in l.lower()
    ]
    
    return {
        "check": "network_timeouts",
        "network_calls": len([l for l in result.stdout.split('\n') if l]),
        "without_timeout": len(no_timeout),
        "details": no_timeout[:10]
    }

if __name__ == "__main__":
    import json
    
    checks = [
        check_platform_assumptions(),
        check_env_vars(),
        check_network_timeouts(),
    ]
    
    print(json.dumps({"assumption_checks": checks}, indent=2))
```

---

## COPYRIGHT

Copyright © 2025-2026 Asif Hussain. All rights reserved.
