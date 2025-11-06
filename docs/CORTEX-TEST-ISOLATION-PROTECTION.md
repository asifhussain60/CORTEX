# CORTEX Test Isolation & Protection

**Date:** November 6, 2025  
**Purpose:** Ensure CORTEX's internal test suite is completely isolated from target application test frameworks

---

## 🛡️ **Protection Requirements**

### **Problem Statement**
CORTEX operates on real-world applications that may use various test frameworks:
- **Python:** pytest, unittest, nose, tox
- **.NET:** NUnit, xUnit, MSTest
- **JavaScript:** Jest, Mocha, Jasmine, Karma
- **Java:** JUnit, TestNG
- **Ruby:** RSpec, Minitest

**CORTEX's internal health checks and agent validation MUST NOT:**
1. Interfere with target application tests
2. Be affected by target application test configurations
3. Require target application test dependencies
4. Execute or modify target application tests

---

## 🔒 **Isolation Mechanisms**

### **1. Directory Isolation**

**CORTEX Tests Location:**
```
CORTEX/
├── tests/           # ✅ ISOLATED - CORTEX internal tests only
│   ├── agents/      # Agent validation tests
│   ├── tier0/       # Tier 0 brain tests
│   ├── tier1/       # Tier 1 conversation tests
│   ├── tier2/       # Tier 2 knowledge graph tests
│   ├── tier3/       # Tier 3 context tests
│   └── conftest.py  # CORTEX-specific pytest fixtures
```

**Target Application (Example):**
```
/path/to/target-app/
├── tests/           # ❌ NEVER TOUCHED - Application's own tests
├── test/            # ❌ NEVER TOUCHED
├── spec/            # ❌ NEVER TOUCHED (Ruby/JS)
└── __tests__/       # ❌ NEVER TOUCHED (JavaScript)
```

**Protection Rule:** CORTEX tests ONLY run from `CORTEX/tests/` directory.

---

### **2. pytest Configuration Isolation**

**CORTEX pytest.ini:**
```ini
[pytest]
# Explicit test path restriction
testpaths = CORTEX/tests

# CORTEX-specific markers
markers =
    cortex_internal: Internal CORTEX health validation
    agent_test: Agent functionality tests
    brain_test: Brain tier tests
    
# Prevent discovery outside CORTEX
norecursedirs = 
    .git
    .tox
    dist
    build
    *.egg
    node_modules
    target
    bin
    obj
```

---

### **3. HealthValidator Isolation**

**Current Implementation:**
```python
# CORTEX/src/cortex_agents/health_validator.py (Line 306)
result = subprocess.run(
    ["python3", "-m", "pytest", "CORTEX/tests/", "--tb=no", "-q"],
    capture_output=True,
    text=True,
    timeout=30,
    cwd=os.getcwd()  # ⚠️ CURRENT WORKING DIRECTORY
)
```

**Protected Implementation:**
```python
# Always run from CORTEX root, never from target app
cortex_root = Path(__file__).parent.parent.parent  # Navigate to CORTEX root
result = subprocess.run(
    ["python3", "-m", "pytest", "CORTEX/tests/", "--tb=no", "-q"],
    capture_output=True,
    text=True,
    timeout=30,
    cwd=str(cortex_root)  # ✅ CORTEX ROOT ONLY
)
```

---

### **4. Test Execution Context**

**Environment Variable Protection:**
```python
# Set CORTEX-specific environment before running tests
import os
cortex_env = os.environ.copy()
cortex_env['CORTEX_INTERNAL_TEST'] = 'true'
cortex_env['PYTEST_CURRENT_TEST'] = ''  # Clear any target app pytest state

result = subprocess.run(
    ["python3", "-m", "pytest", "CORTEX/tests/"],
    env=cortex_env,  # ✅ ISOLATED ENVIRONMENT
    cwd=cortex_root
)
```

---

### **5. Python Path Isolation**

**Issue:** Target applications may modify `sys.path` or `PYTHONPATH`

**Protection:**
```python
import sys
from pathlib import Path

def get_cortex_python_path():
    """Get isolated Python path for CORTEX tests."""
    cortex_root = Path(__file__).parent.parent.parent
    return [
        str(cortex_root),  # CORTEX root
        str(cortex_root / "src"),  # CORTEX src
    ]

# Before running tests
original_path = sys.path.copy()
sys.path = get_cortex_python_path() + sys.path

# Run CORTEX tests...

# Restore original path
sys.path = original_path
```

---

## 🧪 **Test Framework Detection**

### **Application Test Framework Discovery**

**CORTEX should detect (but not interfere with) target app test frameworks:**

```python
def detect_application_test_framework(app_root: Path) -> Dict[str, Any]:
    """
    Detect target application's test framework WITHOUT executing.
    
    Returns:
        Framework detection results (for reporting only)
    """
    frameworks = {
        "pytest": ["pytest.ini", "setup.cfg", "pyproject.toml"],
        "unittest": ["unittest.cfg"],
        "nunit": ["*.csproj", "nunit.config"],
        "xunit": ["xunit.runner.json"],
        "jest": ["jest.config.js", "package.json"],
        "mocha": [".mocharc.json", "mocha.opts"],
        "junit": ["pom.xml", "build.gradle"]
    }
    
    detected = []
    for framework, config_files in frameworks.items():
        for config in config_files:
            if list(app_root.glob(f"**/{config}")):
                detected.append(framework)
                break
    
    return {
        "frameworks_detected": detected,
        "cortex_action": "NONE - Application tests are isolated"
    }
```

**Usage:**
- **Report:** "Target application uses Jest for testing"
- **Action:** NONE - CORTEX never executes application tests

---

## 📋 **Protection Checklist**

### **For Every CORTEX Component:**

- [ ] **HealthValidator**
  - [x] Tests run from CORTEX root only
  - [ ] Environment variables isolated
  - [ ] No dependency on target app test config
  
- [ ] **TestGenerator**
  - [x] Generates tests for target app
  - [x] NEVER executes generated tests
  - [ ] Templates don't assume pytest (support NUnit, xUnit, etc.)
  
- [ ] **CodeExecutor**
  - [x] Modifies target app code
  - [x] NEVER modifies CORTEX/tests/
  - [ ] Validation uses CORTEX's pytest only
  
- [ ] **ErrorCorrector**
  - [ ] Fixes target app errors
  - [ ] NEVER fixes CORTEX internal tests
  - [ ] Uses CORTEX tests for self-validation

---

## 🚨 **Protection Rules**

### **ABSOLUTE RULES - NEVER VIOLATE:**

1. **CORTEX tests are in `CORTEX/tests/` ONLY**
   - Path: `/Users/asifhussain/PROJECTS/CORTEX/CORTEX/tests/`
   - Pattern: `CORTEX/tests/**/*.py`

2. **CORTEX pytest runs with explicit path**
   - Command: `pytest CORTEX/tests/` (never just `pytest`)
   - Working Directory: CORTEX root (never target app root)

3. **Target application test directories are READ-ONLY to CORTEX**
   - May read: For analysis, pattern learning
   - NEVER write: No modifications, no executions

4. **Test execution is CORTEX-internal only**
   - HealthValidator runs CORTEX tests for system health
   - Application tests are target app's responsibility

5. **Framework independence**
   - CORTEX uses pytest internally
   - TestGenerator supports multiple frameworks
   - No assumption that target app uses pytest

---

## 🔧 **Implementation Updates Needed**

### **Priority 1: HealthValidator Fix**
```python
# File: CORTEX/src/cortex_agents/health_validator.py
# Lines: 290-320

def _check_tests(self, skip: bool = False) -> Dict[str, Any]:
    """Check CORTEX internal test suite (NOT application tests)."""
    if skip:
        return {"status": "skip", "message": "Test check skipped"}
    
    try:
        # Get CORTEX root directory
        cortex_root = Path(__file__).parent.parent.parent
        
        # Create isolated environment
        test_env = os.environ.copy()
        test_env['CORTEX_INTERNAL_TEST'] = 'true'
        
        # Run CORTEX tests ONLY
        result = subprocess.run(
            ["python3", "-m", "pytest", "CORTEX/tests/", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(cortex_root),  # ✅ ALWAYS CORTEX ROOT
            env=test_env
        )
        # ... rest of implementation
```

### **Priority 2: pytest.ini Update**
```ini
[pytest]
testpaths = CORTEX/tests  # ✅ Explicit restriction

# Prevent accidental discovery of application tests
norecursedirs = 
    **/tests  # Ignore all other 'tests' directories
    **/test
    **/__tests__
    **/spec
```

### **Priority 3: Documentation**
- Add to `cortex.config.json`: `"test_isolation": "strict"`
- Update CORTEX README with isolation guarantees
- Add warnings to ErrorCorrector about test file detection

---

## 📊 **Validation**

### **How to Verify Protection:**

1. **Run CORTEX tests from target app directory:**
   ```bash
   cd /path/to/target-application
   python3 -m pytest CORTEX/tests/  # Should work (absolute path)
   ```

2. **Verify no interference:**
   ```bash
   # CORTEX should not find these:
   cd /path/to/target-application
   python3 -m pytest  # Runs app tests, NOT CORTEX tests
   ```

3. **Check HealthValidator isolation:**
   ```python
   # In target app context
   from CORTEX.src.cortex_agents.health_validator import HealthValidator
   
   validator = HealthValidator("Test")
   result = validator._check_tests()
   # Should only test CORTEX, never target app
   ```

---

## 🎯 **Summary**

**CORTEX Test Isolation Guarantees:**

1. ✅ **CORTEX tests live in `CORTEX/tests/` exclusively**
2. ✅ **All pytest commands use explicit `CORTEX/tests/` path**
3. ✅ **Working directory is CORTEX root, not target app**
4. ⏳ **Environment variables isolated (needs implementation)**
5. ✅ **Target application test directories are never modified**
6. ✅ **TestGenerator supports multiple frameworks (not just pytest)**
7. ✅ **No dependencies on target app test configuration**

**Status:** 5/7 complete, 2 enhancements needed (Priority 1 & 2 above)

---

**Next Steps:**
1. Update `HealthValidator._check_tests()` with Path-based isolation
2. Update `pytest.ini` with stricter `norecursedirs`
3. Add `CORTEX_INTERNAL_TEST` environment variable
4. Document in main README
5. Add validation tests to prove isolation
