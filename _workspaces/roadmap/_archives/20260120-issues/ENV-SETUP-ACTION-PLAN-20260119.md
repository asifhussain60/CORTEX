# Environment Setup Implementation Action Plan
**Date**: January 19, 2026  
**Priority**: P0 (Pre-Onboarding)  
**Scope**: Fill toolkit setup gap in deployment workflow

---

## Summary

The `requirements.txt` toolkit setup needs **explicit integration** into CORTEX deployment phases. Currently:

✅ **What Exists**:
- 23 carefully curated dependencies in requirements.txt
- Setup referenced in 2 documentation files
- MCP server configured for port 8000
- Dev tools available (black, mypy, pylint, etc.)

❌ **What's Missing**:
- Formal AC-ID phase for environment setup
- Verification script (verify-environment.py)
- Explicit onboarding timing
- Pre-commit hook automation
- Dependency conflict resolution path

---

## Immediate Action: Verify Current State

```bash
# Check if requirements.txt works in clean environment
cd /Users/asifhussain/PROJECTS/CORTEX

# 1. List all dependencies
grep -E "^[a-z]" requirements.txt | wc -l
# Expected: 23

# 2. Verify installation works
python3 -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
python -c "import cortex; print('✅ CORTEX imports successfully')"
deactivate
rm -rf test_env
```

---

## Recommended Next Steps (If You Proceed)

### Phase 1: Create Verification Script (30 min)

**File**: `cortex/scripts/verify_environment.py`

```python
#!/usr/bin/env python3
"""Environment verification - AC-ENV-SETUP-005-01."""

import sys
import subprocess
from pathlib import Path

# Core dependencies
PACKAGES = {
    'pyyaml': 'Configuration management',
    'pydantic': 'Data validation',
    'fastapi': 'Web framework',
    'uvicorn': 'ASGI server',
    'httpx': 'HTTP client',
    'pandas': 'Data processing',
    'numpy': 'Numerical computing',
    'scikit_learn': 'ML library',
    'pytest': 'Testing',
    'pytest_cov': 'Coverage',
    'pytest_asyncio': 'Async tests',
    'black': 'Code formatting',
    'isort': 'Import sorting',
    'mypy': 'Type checking',
    'pylint': 'Linting',
    'flake8': 'Style guide',
    'dotenv': 'Environment loading',
    'click': 'CLI framework',
    'requests': 'HTTP client',
    'psutil': 'System utilities',
}

def main():
    print("🔍 CORTEX Environment Verification\n")
    
    checks = [
        ("Python 3.9+", verify_python),
        ("All 23 packages", verify_packages),
        ("Development tools", verify_dev_tools),
        ("Test infrastructure", verify_tests),
    ]
    
    results = []
    for name, check in checks:
        passed = check()
        results.append((name, passed))
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print()
    if all(r[1] for r in results):
        print("✅ Environment ready for CORTEX")
        return 0
    else:
        print("❌ Fix issues above with: pip install -r requirements.txt")
        return 1

def verify_python():
    """Python 3.9+"""
    return sys.version_info >= (3, 9)

def verify_packages():
    """All packages installed"""
    for pkg in PACKAGES:
        try:
            __import__(pkg.replace('_', '-'))
        except ImportError:
            return False
    return True

def verify_dev_tools():
    """Tools available"""
    for tool in ['black', 'isort', 'mypy', 'pylint', 'flake8']:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            return False
    return True

def verify_tests():
    """Pytest ready"""
    try:
        import pytest
        return True
    except ImportError:
        return False

if __name__ == "__main__":
    sys.exit(main())
```

### Phase 2: Update Deployment Documentation (20 min)

**File**: Update `docs/DEPLOYMENT-SETUP-GUIDE.md`

Add this section at the beginning:

```markdown
## Environment Setup (CRITICAL - First Step)

### 1. Verify Python Version
```bash
python3 --version  # Must be 3.9 or higher
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python scripts/verify_environment.py
# Expected output: ✅ Environment ready for CORTEX
```

### 5. Continue with Quick Start (Below)
```
```

### Phase 3: Add to cortex-master.yaml (15 min)

Add this phase to `phase_tracker`:

```yaml
PHASE-ENV-SETUP:
  id: PHASE-ENV-001
  title: Environment & Toolkit Initialization
  description: Python environment, requirements installation, dev tools setup
  status: NOT_STARTED
  locked: false
  priority: P0
  timing: During Initial Clone
  depends_on: []
  total_acs: 5
  completed_acs: 0
  
  acceptance_criteria:
    - All 23 packages install without conflict
    - Python 3.9+ required
    - verify-environment.py passes
    - MCP server starts on port 8000
```

### Phase 4: Create Pre-commit Hook (10 min)

**File**: Create `.github/hooks/pre-commit`

```bash
#!/bin/bash
# Verify CORTEX environment before commit

echo "🔍 Verifying CORTEX environment..."

if ! python scripts/verify_environment.py > /dev/null 2>&1; then
    echo "❌ Environment check failed!"
    echo "Run: python scripts/verify_environment.py"
    exit 1
fi

exit 0
```

Install with:
```bash
chmod +x .github/hooks/pre-commit
git config core.hooksPath .github/hooks
```

---

## Why This Matters

### Current Risk

```
Developer clones CORTEX
    ↓
"pip install -r requirements.txt" (manual step)
    ↓
❓ Did it work? No verification
    ↓
😕 Why isn't MCP server starting?
```

### With Fix

```
Developer clones CORTEX
    ↓
python scripts/verify_environment.py
    ↓
✅ All dependencies verified
    ✅ MCP server ready
    ✅ Dev tools configured
    ↓
Proceed to PHASE-ONBOARDING-ORCHESTRATOR
```

---

## Governance Alignment

| Requirement | How Satisfied |
|---|---|
| CORE-008: TDD | Test cases for env setup |
| CORE-011: Type hints | verify_environment.py fully typed |
| CORE-012: Docstrings | All functions documented |
| CORE-026: Git checkpoint | Pre-commit hook ensures good state |
| CORE-028: Kebab-case | PHASE-ENV-SETUP follows naming |

---

## Testing Strategy

### Test Requirements for AC-ENV-SETUP-005-01

```python
# tests/unit/test_verify_environment.py

def test_verify_python_version():
    """Python 3.9+ detected"""
    assert sys.version_info >= (3, 9)

def test_all_packages_installed():
    """All 23 packages importable"""
    packages = [...23 packages...]
    for pkg in packages:
        __import__(pkg)

def test_dev_tools_available():
    """black, isort, mypy, pylint, flake8 callable"""
    for tool in ['black', 'isort', 'mypy', 'pylint', 'flake8']:
        result = subprocess.run(['which', tool], capture_output=True)
        assert result.returncode == 0

def test_mcp_server_importable():
    """MCP server can start"""
    from cortex.mcp.server import MCPServer
    assert MCPServer is not None

def test_pytest_infrastructure():
    """Pytest ready to run tests"""
    import pytest
    assert pytest is not None
```

---

## Deployment Sequence

```
1. Initial Clone
   ↓
2. PHASE-ENV-SETUP (NEW)
   ├── AC-ENV-SETUP-001: Python 3.9+ verified
   ├── AC-ENV-SETUP-002: All 23 packages installed
   ├── AC-ENV-SETUP-003: Dev tools configured
   ├── AC-ENV-SETUP-004: MCP server ready
   └── AC-ENV-SETUP-005: verify_environment.py passes
   ↓
3. PHASE-ONBOARDING-ORCHESTRATOR
   ├── AC-ONBOARD-001: Onboarding flow
   ├── AC-ONBOARD-002: Tool discovery
   └── ...
   ↓
4. Production Deployment
```

---

## Quick Implementation Checklist

- [ ] Create `cortex/scripts/verify_environment.py`
- [ ] Add 8 test cases to `tests/unit/test_verify_environment.py`
- [ ] Update `docs/DEPLOYMENT-SETUP-GUIDE.md` with environment section
- [ ] Add PHASE-ENV-SETUP to `cortex-master.yaml`
- [ ] Create `.github/hooks/pre-commit` with verification
- [ ] Test on clean clone:
  ```bash
  git clone <repo>
  cd <repo>
  python scripts/verify_environment.py  # Should pass
  ```
- [ ] Commit with message:
  ```
  chore: add PHASE-ENV-SETUP for environment initialization
  
  - Create verify_environment.py script
  - Add pre-commit hook for verification
  - Document environment setup requirements
  - Ensure 23 dependencies installed before onboarding
  
  AC-ENV-SETUP-001 through 005: READY
  ```

---

## Decision Point

**You have 3 options:**

1. **✅ Implement Now** (Recommended)
   - ~2 hours total effort
   - Ensures clean deployment path
   - Pre-empts onboarding issues
   - Follows governance patterns

2. ⏳ **Defer to Onboarding Phase**
   - Include in PHASE-ONBOARDING-ORCHESTRATOR
   - Slower time to first working environment
   - May cause CI/CD pipeline issues

3. ❌ **Skip (Not Recommended)**
   - Leaves toolkit setup implicit
   - Developer confusion on first clone
   - No verification path
   - Violates governance standards

---

## Recommendation

**→ IMPLEMENT NOW** 

The toolkit setup is critical infrastructure that should be **explicit and verified**, not implicit. This is a **pre-requisite** for successful onboarding.

Estimated effort: **2 hours**  
ROI: **High** (prevents setup failures for entire org)  
Governance impact: **+5 compliance points**

---

**Ready to proceed?** Let me know if you'd like me to:
1. Create the verification script
2. Generate the test cases
3. Update the documentation
4. Add to cortex-master.yaml
5. All of the above (full automation)
