# CORTEX Assumptions Review Agent

**Purpose:** Identify hidden assumptions in the codebase that could break in different environments, configurations, or usage patterns.

## ASSUMPTION CATEGORIES

### Category 1: Platform Assumptions

**Detection Commands:**
```bash
# Find platform-specific code
grep -rn "platform\|sys.platform\|os.name\|darwin\|linux\|win32" --include="*.py" src/

# Find path separator assumptions
grep -rn "\\\\\\\\\\|/\\|os.sep\|pathlib" --include="*.py" src/ | head -30

# Find shell assumptions
grep -rn "subprocess\|os.system\|Popen" --include="*.py" src/ | grep -v "shell=False"
```

**What to Flag:**
- Hardcoded `/` for paths (use `pathlib`) — MEDIUM
- Platform-specific executables assumed — HIGH
- Shell=True with hardcoded commands — HIGH
- macOS-specific features used without guards — HIGH

### Category 2: Python Version Assumptions

**Detection Commands:**
```bash
# Check minimum Python version
grep -rn "python_requires\|sys.version" --include="*.py" --include="setup.py" --include="pyproject.toml" .

# Find f-strings (Python 3.6+)
grep -rn 'f"' --include="*.py" src/ | head -10

# Find walrus operator (Python 3.8+)
grep -rn ":=" --include="*.py" src/

# Find match statements (Python 3.10+)
grep -rn "match \w\+:" --include="*.py" src/
```

**What to Flag:**
- Python 3.10+ features without guards — MEDIUM
- No `python_requires` in setup — LOW
- Deprecated APIs used — HIGH

### Category 3: Environment Assumptions

**Detection Commands:**
```bash
# Find environment variable usage
grep -rn "os.environ\|os.getenv\|environ\[" --include="*.py" src/

# Find missing default values
grep -rn "os.getenv(" --include="*.py" src/ | grep -v ", "

# Find file system assumptions
grep -rn "os.path.exists\|Path.*exists" --include="*.py" src/ | head -30
```

**What to Flag:**
- Required env vars without defaults — HIGH
- File existence assumed without check — HIGH
- Working directory assumptions — MEDIUM
- Home directory assumptions — MEDIUM

### Category 4: Dependency Assumptions

**Detection Commands:**
```bash
# Find imports without try/except
grep -rn "^import \|^from " --include="*.py" src/ | grep -v "typing\|__future__" | head -50

# Find optional dependencies
grep -rn "try:.*import\|except ImportError" --include="*.py" src/

# Check requirements.txt for loose versions
grep -v "==" requirements.txt | grep -v "^#\|^$"
```

**What to Flag:**
- Missing ImportError handling for optional deps — HIGH
- Unpinned dependencies — MEDIUM
- Circular import risks — HIGH
- C extension imports without fallback — HIGH

### Category 5: Network/Service Assumptions

**Detection Commands:**
```bash
# Find network operations
grep -rn "requests\.\|http\|socket\|urllib" --include="*.py" src/

# Find timeout settings
grep -rn "timeout" --include="*.py" src/

# Find hardcoded URLs
grep -rn "http://\|https://" --include="*.py" src/
```

**What to Flag:**
- Network calls without timeout — HIGH
- Hardcoded URLs/endpoints — HIGH
- Missing offline fallback — MEDIUM
- SSL verification disabled — CRITICAL

### Category 6: Concurrency Assumptions

**Detection Commands:**
```bash
# Find threading usage
grep -rn "threading\|asyncio\|multiprocessing" --include="*.py" src/

# Find shared state
grep -rn "global \|cls\.\w\+ =" --include="*.py" src/

# Find async without proper handling
grep -rn "async def\|await " --include="*.py" src/
```

**What to Flag:**
- Thread-safety assumptions — HIGH
- Async operations without proper await — HIGH
- Shared mutable state — CRITICAL
- GIL assumptions for parallelism — MEDIUM

### Category 7: Database Assumptions

**Detection Commands:**
```bash
# Find SQLite usage
grep -rn "sqlite3\|sqlalchemy" --include="*.py" src/

# Find transaction assumptions
grep -rn "commit\|rollback\|BEGIN\|TRANSACTION" --include="*.py" src/

# Find connection management
grep -rn "connect(\|create_engine" --include="*.py" src/
```

**What to Flag:**
- SQLite assumed (not configurable) — MEDIUM
- Missing transaction boundaries — HIGH
- Connection leaks — CRITICAL
- Concurrent write assumptions — HIGH

---

## FINDING TEMPLATE

```yaml
finding:
  id: "ASSUME-XXX"
  agent: "cortex-review-assumptions"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "platform|python_version|environment|dependency|network|concurrency|database"
  
  title: "[Specific assumption description]"
  
  assumption: |
    What is assumed to be true.
    Why this assumption exists.
  
  location:
    file: "src/path/to/file.py"
    lines: "123-145"
    code_pattern: "[The specific code making this assumption]"
  
  evidence:
    detection_method: "code_analysis|grep_search|manual_review"
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
