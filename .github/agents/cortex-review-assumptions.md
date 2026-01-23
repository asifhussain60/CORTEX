# CORTEX Review Agent: Assumptions Analysis
## Hidden Environment & Platform Dependencies

**Purpose:** Identify unstated assumptions about environment, platforms, services, and dependencies.

---

## CHECKS PERFORMED

### 1. Platform Dependencies (macOS vs Linux vs Windows)

**What to look for:**
- os.name, sys.platform checks
- Path separators hardcoded
- Home directory assumptions
- Shell-specific commands

**Search patterns:**
```bash
# Platform-specific code
grep -rn "os.name\|sys.platform\|platform.system" cortex/ --include="*.py"
grep -rn "\\\\|/\|os.sep" cortex/ --include="*.py" | grep -v "os.path"
grep -rn "~\|/home/\|/Users/\|C:\\\\" cortex/ --include="*.py"

# Shell commands
grep -rn "os.system\|subprocess.*shell" cortex/ --include="*.py"
grep -rn "sh\|bash\|cmd.exe" cortex/ --include="*.py"
```

**Examples that are problematic:**
```python
# Assumes Unix/Linux path separator
config_path = f"{user_home}/.cortex/config.yaml"  # ← Fails on Windows

# Uses home directory without Path handling
import os
cortex_root = os.path.expanduser("~/.cortex")  # ← Better but still assumes ~

# Subprocess with shell-specific syntax
subprocess.run("grep pattern file.txt", shell=True)  # ← Fails on Windows
```

**Files to check:**
- `cortex/config/` - Configuration paths
- `cortex/deployment/` - Deployment scripts
- `cortex/scripts/` - Utility scripts
- `cortex/cli/` - CLI commands

---

### 2. Python Version Assumptions

**What to look for:**
- Features only in Python 3.10+
- f-strings (OK for 3.6+)
- Walrus operator (3.8+)
- match/case (3.10+)
- Type hints features

**Search patterns:**
```bash
# Match/case statements (Python 3.10+)
grep -rn "match\|case:" cortex/ --include="*.py"

# Walrus operator (Python 3.8+)
grep -rn ":=" cortex/ --include="*.py"

# Type hints requiring 3.10+
grep -rn "list\[.*\]\|dict\[.*\]\|tuple\[.*\]" cortex/ --include="*.py" | grep -v "List\|Dict\|Tuple"

# Check requirements.txt
cat requirements.txt | grep -i python
```

**Issue:** requirements.txt says Python 3.9+ but code uses 3.10+ features

**Solution:**
- Use `List[T]` from typing instead of `list[T]`
- Avoid `match` statements
- Use `Union[A, B]` instead of `A | B`

---

### 3. External Service Requirements

**What to look for:**
- API endpoints hardcoded
- Service availability assumed
- No fallback when service unavailable
- Authentication method not documented

**Search patterns:**
```bash
# Hardcoded URLs/endpoints
grep -rn "http\|api\|endpoint\|url" cortex/ --include="*.py" | grep "=" | head -20

# API calls
grep -rn "requests\.\|httpx\.\|urllib" cortex/ --include="*.py"

# Service assumptions
grep -rn "db\.\|database\.\|cache\." cortex/ --include="*.py" | grep -v "test\|mock"
```

**Examples:**
```python
# Hardcoded API endpoint
API_URL = "https://api.openai.com/v1/chat/completions"  # ← What if service down?

# Database required to run
db = Database.connect()  # ← Fails if no DB running
```

**Critical services:**
- OpenAI API (if using)
- Anthropic API (if using)
- Database (PostgreSQL/SQLite)
- Cache (Redis/Memcached)
- Message queue (if async)

---

### 4. File System Permissions

**What to look for:**
- Assumes write permissions
- Assumes specific directory ownership
- No fallback for read-only FS
- Temporary file creation assumptions

**Search patterns:**
```bash
# File write operations
grep -rn "open(.*'w'\|open(.*'a'" cortex/ --include="*.py"

# Directory creation
grep -rn "mkdir\|makedirs" cortex/ --include="*.py"

# Temporary files
grep -rn "tempfile\|tmp\|/tmp/" cortex/ --include="*.py"
```

**Issues:**
```python
# Assumes write permission to current directory
log_file = open("cortex.log", "w")  # ← Fails if run from read-only location

# Assumes /tmp exists and is writable
temp_dir = "/tmp/cortex"  # ← Doesn't exist on Windows
```

---

### 5. Network Connectivity

**What to look for:**
- Assumes internet connection
- No offline mode
- No connection retry logic
- Long timeouts block execution

**Search patterns:**
```bash
# Network dependencies
grep -rn "requests\.\|httpx\.\|socket" cortex/ --include="*.py" | grep -v timeout

# Hard dependency on online resources
grep -rn "download\|fetch\|pull" cortex/ --include="*.py" | head -20

# Missing retry logic
grep -rn "requests\.\|httpx\." cortex/ --include="*.py" | grep -v "retry\|Retry"
```

**Issues:**
```python
# Fails if network unavailable
response = requests.get("https://api.github.com/user")

# No timeout = infinite wait
response = requests.get(url)  # ← Default 30s timeout is OK but document it
```

---

### 6. Environment Variables

**What to look for:**
- Required env vars not documented
- No defaults
- Case sensitivity issues
- Missing validation

**Search patterns:**
```bash
# Environment variable usage
grep -rn "os.environ\|os.getenv\|getenv" cortex/ --include="*.py"

# Missing documentation
grep -rn "getenv.*)" cortex/ --include="*.py" | grep -v "#"
```

**Examples:**
```python
# Required but not documented
api_key = os.environ["OPENAI_API_KEY"]  # ← Will crash if not set

# Better with default and documentation
api_key = os.environ.get("OPENAI_API_KEY")  # ← Returns None, better but still unclear

# Best: explicit requirement
api_key = os.environ.get("OPENAI_API_KEY") or ""
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable required")
```

**Document required env vars in:**
- README.md
- .env.example
- config/DEFAULT_CONFIG.yaml

---

### 7. Timezone & Locale Assumptions

**What to look for:**
- Time operations without timezone
- String comparisons assuming locale
- Number formatting assumptions
- Date parsing without timezone

**Search patterns:**
```bash
# Timezone-naive datetime
grep -rn "datetime.now()\|datetime.utcnow()\|timezone" cortex/ --include="*.py"

# Locale assumptions
grep -rn "locale\|encoding\|utf" cortex/ --include="*.py"

# Time formatting
grep -rn "strftime\|strptime" cortex/ --include="*.py"
```

**Issues:**
```python
# Timezone-naive (problematic in distributed systems)
now = datetime.now()  # ← No timezone info

# Better: explicit UTC
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
```

---

### 8. Development Tools Required

**What to look for:**
- Tools called by scripts
- Build tools assumed
- Database tools required
- Testing frameworks

**Search patterns:**
```bash
# Tools called by scripts
grep -rn "subprocess\|os.system" cortex/ --include="*.py" | grep -v "pytest\|python"

# Build tool requirements
cat requirements.txt | grep -E "build|wheel|setuptools"

# Testing requirements
cat requirements.txt | grep -E "pytest|pytest-"
```

**Examples of tool dependencies:**
- pytest (testing)
- Docker (containerization)
- PostgreSQL (database)
- Redis (cache)
- Git (version control)

---

## OUTPUT FORMAT

Create: `_workspaces/roadmap/issues/findings-assumptions-YYYYMMDD.yaml`

```yaml
assumptions_findings:
  metadata:
    review_date: "YYYYMMDD"
    total_assumptions: X
    by_category:
      platform: Y
      python_version: Z
      services: A
      permissions: B
      network: C
      environment: D
      timezone: E
      tools: F
    
  critical_assumptions:
    - assumption_id: "ASS-001"
      category: "PYTHON_VERSION"
      severity: "CRITICAL"
      description: "Code uses Python 3.10+ features but requirements.txt says 3.9+"
      evidence:
        - "cortex/brain/tier2/resilience/__init__.py uses match/case"
        - "requirements.txt: Python 3.9+"
      impact: "Code fails on Python 3.9"
      remediation: "Either update requirements.txt to 3.10+ or replace match/case with if/elif"
      
    - assumption_id: "ASS-002"
      category: "EXTERNAL_SERVICE"
      severity: "HIGH"
      description: "Requires OpenAI API to be available; no offline mode"
      evidence:
        - "cortex/execution/llm_engine.py calls OpenAI API directly"
        - "No fallback if API unavailable"
      impact: "System non-functional if OpenAI service down"
      remediation: "Add offline mode or graceful degradation when API unavailable"
      
    - assumption_id: "ASS-003"
      category: "PLATFORM"
      severity: "HIGH"
      description: "Assumes Unix/Linux path separators"
      evidence:
        - 'cortex/config/loader.py: config_path = f"{home}/.cortex/config.yaml"'
        - "Fails on Windows (no .cortex folder convention)"
      impact: "Cannot run on Windows"
      remediation: "Use pathlib.Path for platform-agnostic paths"
      
  recommendations:
    - "Document all environment variable requirements"
    - "Add .env.example with all required vars"
    - "Use pathlib.Path everywhere for cross-platform support"
    - "Add offline mode or circuit breaker for external APIs"
    - "Document minimum Python version clearly"
    - "Add startup checks for all required services"
```

---

## DECISION TREE

```
For each assumption:

Q1: Is requirement not documented?
  → YES: HIGH severity (user won't know)
  
Q2: Will failure be silent?
  → YES: CRITICAL severity (hard to debug)
  
Q3: Is there no fallback?
  → YES: HIGH severity (complete system failure)
  
Q4: Are multiple platforms affected?
  → YES: CRITICAL severity (many users blocked)
```

---

## VALIDATION

Before finalizing findings:
- [ ] Assumption is clearly stated (not vague)
- [ ] Evidence includes code location and pattern
- [ ] Impact describes failure mode clearly
- [ ] Remediation is specific (not "make it portable")
- [ ] Severity matches actual user impact
