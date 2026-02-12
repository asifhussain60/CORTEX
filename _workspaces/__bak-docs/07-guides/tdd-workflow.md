# TDD Workflow with CORTEX
**Authority:** CORE-008, CORE-019 | **Updated:** 2026-02-03

---

## Overview

CORTEX enforces **Test-Driven Development (TDD)** through multiple layers of governance. This guide explains how to properly implement features using the TDD workflow.

---

## ⚠️ CRITICAL RULES

| Rule | Requirement |
|------|-------------|
| **CORE-008** | Tests BEFORE code (RED → GREEN → REFACTOR) |
| **CORE-019** | ALL implementation intents route through TDDOrchestrator |
| **MCP-GATE** | Use `cortex_process_request` MCP tool (NO direct file creation) |

**Violation Impact:**
- ❌ Pre-commit hook blocks commits without tests
- ❌ CI/CD pipeline fails PR validation
- ❌ TDDOrchestrator rejects non-MCP invocations
- ❌ Cross-layer misalignments (Phase 21 type issues)

---

## TDD Enforcement Layers

### Layer 1: Pre-Commit Hook
```bash
# Automatically installed at .git/hooks/pre-commit
# Blocks commits where implementation exists without tests
```

**When it triggers:**
- Committing Python files in `cortex/` without corresponding `tests/` files
- Implementation-first workflow (waterfall violation)

**How to fix:**
```bash
# 1. Create test file FIRST
# 2. Write failing tests (RED)
# 3. Implement minimal code (GREEN)
# 4. Refactor (REFACTOR)
# 5. Commit both test + implementation together
```

### Layer 2: TDDOrchestrator MCP Gate
```python
# Rejects direct invocations (must route through MCP)
if context.get("source") != "mcp_gateway":
    return Err("MCP-GATE VIOLATION: Use cortex_process_request tool")
```

**When it triggers:**
- Direct file creation via GitHub Copilot chat
- Bypassing MCP gateway

**How to fix:**
```python
# ❌ WRONG: Direct chat command
"Create cortex/auth/service.py with user authentication"

# ✅ CORRECT: Use MCP tool
cortex_process_request(
    request="Implement user authentication service",
    context={
        "module_path": "cortex/auth/service.py",
        "domain": "authentication",
        "source": "mcp_gateway"  # Required
    }
)
```

### Layer 3: CI/CD Pipeline
```yaml
# .github/workflows/tdd-gate.yml
# Runs on all PRs/pushes to CORTEX/main branches
```

**Validates:**
- TDD gate compliance (tests exist)
- Cross-layer schema alignment (CORE-035)
- Import correctness (schema as SSOT)

---

## Correct TDD Workflow

### Step 1: RED Phase (Write Failing Test)

**Via MCP Tool:**
```python
cortex_process_request(
    request="Create tests for user authentication service",
    context={
        "module_path": "cortex/auth/service.py",
        "domain": "authentication",
        "phase": "RED",
        "source": "mcp_gateway"
    }
)
```

**Creates:**
```python
# tests/unit/auth/test_service.py
import pytest
from cortex.auth.service import UserAuthService

def test_authenticate_user_with_valid_credentials():
    """Test successful authentication with valid credentials."""
    service = UserAuthService()
    result = service.authenticate("user@example.com", "secure_password")
    
    assert result.is_ok()
    assert result.unwrap().user_id == 123
    assert result.unwrap().session_token is not None

def test_authenticate_user_with_invalid_credentials():
    """Test authentication fails with invalid credentials."""
    service = UserAuthService()
    result = service.authenticate("user@example.com", "wrong_password")
    
    assert result.is_err()
    assert "Invalid credentials" in str(result.unwrap_err())

def test_authenticate_user_with_nonexistent_email():
    """Test authentication fails with nonexistent email."""
    service = UserAuthService()
    result = service.authenticate("nobody@example.com", "any_password")
    
    assert result.is_err()
    assert "User not found" in str(result.unwrap_err())
```

**Run tests (should FAIL):**
```bash
pytest tests/unit/auth/test_service.py -v
# Expected: All tests fail (module doesn't exist yet)
```

### Step 2: GREEN Phase (Minimal Implementation)

**Via MCP Tool:**
```python
cortex_process_request(
    request="Implement UserAuthService to pass tests",
    context={
        "module_path": "cortex/auth/service.py",
        "domain": "authentication",
        "phase": "GREEN",
        "test_file": "tests/unit/auth/test_service.py",
        "source": "mcp_gateway"
    }
)
```

**Creates:**
```python
# cortex/auth/service.py
"""User Authentication Service."""

from typing import Optional
from cortex.core.result import Result, Ok, Err

class AuthResult:
    """Authentication result with user info."""
    def __init__(self, user_id: int, session_token: str):
        self.user_id = user_id
        self.session_token = session_token

class UserAuthService:
    """
    Handles user authentication.
    
    CORE-008: TDD implementation
    CORE-011: Type hints on all methods
    CORE-012: Google-style docstrings
    """
    
    def __init__(self):
        """Initialize authentication service."""
        self.users = {
            "user@example.com": {"id": 123, "password": "secure_password"}
        }
    
    def authenticate(
        self, 
        email: str, 
        password: str
    ) -> Result[AuthResult]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Result with AuthResult on success, error message on failure
        """
        # Check if user exists
        if email not in self.users:
            return Err("User not found")
        
        # Verify password
        user = self.users[email]
        if user["password"] != password:
            return Err("Invalid credentials")
        
        # Create session
        auth_result = AuthResult(
            user_id=user["id"],
            session_token=f"session_{user['id']}_abc123"
        )
        
        return Ok(auth_result)
```

**Run tests (should PASS):**
```bash
pytest tests/unit/auth/test_service.py -v
# Expected: All tests pass
```

### Step 3: REFACTOR Phase (Improve Design)

**Via MCP Tool:**
```python
cortex_process_request(
    request="Refactor UserAuthService: extract password hashing, add database layer",
    context={
        "module_path": "cortex/auth/service.py",
        "domain": "authentication",
        "phase": "REFACTOR",
        "test_file": "tests/unit/auth/test_service.py",
        "source": "mcp_gateway"
    }
)
```

**Refactors:**
- Extract `PasswordHasher` class
- Add `UserRepository` abstraction
- Improve error types (custom exceptions)
- Add logging (CORE-024)

**Run tests again (should STILL PASS):**
```bash
pytest tests/unit/auth/test_service.py -v
# Expected: All tests still pass after refactoring
```

### Step 4: Commit Both Test + Implementation

```bash
git add tests/unit/auth/test_service.py cortex/auth/service.py
git commit -m "feat(auth): Implement user authentication service

TDD workflow: RED → GREEN → REFACTOR

Tests:
- test_authenticate_user_with_valid_credentials
- test_authenticate_user_with_invalid_credentials  
- test_authenticate_user_with_nonexistent_email

Implementation:
- UserAuthService with email/password authentication
- Result-based error handling
- Session token generation

CORE-008: Tests written first
CORE-011: Type hints 100%
CORE-012: Google-style docstrings
AC-ID: AC-AUTH-SERVICE-001"

# Pre-commit hook validates TDD compliance
# Push triggers CI/CD validation
git push origin CORTEX
```

---

## Cross-Layer Integration

### Problem: Phase 21 Misalignment

**What happened:**
```python
# cortex/models/dashboard_schema_v3.py
class Severity(str, Enum):
    CRITICAL = 'critical'
    HIGH = 'high'

# cortex/mcp/tools/repository_onboarding_v3_tool.py
from cortex.models.dashboard_schema_v3 import SeverityLevel  # ❌ WRONG
# Should be: Severity
```

**Root cause:**
- Tool invented enum names instead of importing from schema
- No cross-layer integration tests
- TDD Orchestrator never invoked (direct chat implementation)

### Solution: Contract Tests

```python
# tests/integration/test_phase21_contracts.py
def test_schema_is_single_source_of_truth():
    """CORE-035: Schema is ONLY place enums are defined."""
    schema_file = Path("cortex/models/dashboard_schema_v3.py")
    tool_file = Path("cortex/mcp/tools/repository_onboarding_v3_tool.py")
    
    schema_content = schema_file.read_text()
    tool_content = tool_file.read_text()
    
    # Schema DEFINES enums
    assert "class Severity(str, Enum):" in schema_content
    
    # Tool IMPORTS enums (never defines)
    assert "from cortex.models.dashboard_schema_v3 import" in tool_content
    assert "class SeverityLevel" not in tool_content  # ❌ Forbidden
```

**Automated validation:**
```bash
pytest tests/integration/test_phase21_contracts.py -v
# Catches enum misalignments, field name inconsistencies
```

---

## Best Practices

### ✅ DO

1. **Use MCP tools for implementation**
   ```python
   cortex_process_request(request="...", context={...})
   ```

2. **Write tests FIRST (RED phase)**
   - Define expected behavior
   - Include happy path + error cases + edge cases

3. **Minimal implementation (GREEN phase)**
   - Just enough code to pass tests
   - No premature optimization

4. **Refactor with confidence (REFACTOR phase)**
   - Tests protect against regressions
   - Improve design without fear

5. **Commit test + implementation together**
   - Both in same commit
   - Atomic changes

6. **Import from schema (CORE-035)**
   ```python
   from cortex.models.dashboard_schema_v3 import Severity
   ```

### ❌ DON'T

1. **❌ Direct file creation via chat**
   - Bypasses TDD enforcement
   - No cross-layer validation
   - No security gates

2. **❌ Implementation before tests**
   - Waterfall violation
   - Pre-commit hook blocks

3. **❌ Invent enum names**
   ```python
   class SeverityLevel(str, Enum):  # ❌ Should import Severity
   ```

4. **❌ Skip cross-layer tests**
   - Unit tests validate structure
   - Integration tests validate alignment

5. **❌ Commit implementation without tests**
   - Pre-commit hook will block
   - CI/CD will fail

---

## Troubleshooting

### Issue: Pre-commit hook blocks my commit

**Error:**
```
❌ TDD GATE VIOLATION - Tests must precede implementation (CORE-008)
📄 cortex/auth/service.py
   ⚠️  No corresponding test file found
   💡 Expected: tests/unit/auth/test_*.py
```

**Fix:**
1. Create `tests/unit/auth/test_service.py` first
2. Write failing tests (RED)
3. Implement minimal code (GREEN)
4. Commit both together

### Issue: TDDOrchestrator rejects my request

**Error:**
```
❌ MCP-GATE VIOLATION (CORE-019)
Implementation requests MUST route through MCP gateway.
```

**Fix:**
Use `cortex_process_request` MCP tool instead of direct chat:
```python
cortex_process_request(
    request="implement feature X",
    context={"source": "mcp_gateway", ...}
)
```

### Issue: CI/CD pipeline fails on schema alignment

**Error:**
```
FAILED test_schema_is_single_source_of_truth
AssertionError: Tool must import from schema: {'SeverityLevel'}
```

**Fix:**
1. Check `cortex/models/dashboard_schema_v3.py` for correct enum names
2. Update tool to import (not define):
   ```python
   from cortex.models.dashboard_schema_v3 import Severity  # Not SeverityLevel
   ```
3. Run contract tests:
   ```bash
   pytest tests/integration/test_phase21_contracts.py -v
   ```

---

## References

- **CORE-008:** Tests BEFORE code (TDD)
- **CORE-019:** Route through TDDOrchestrator
- **CORE-035:** Single source of truth
- **MCP-GATE:** Use cortex_process_request tool
- **Phase 21 RCA:** [chat02.txt](../../_workspaces/.chats/chat02.txt)
- **Contract Tests:** [test_phase21_contracts.py](../../tests/integration/test_phase21_contracts.py)
- **TDDOrchestrator:** [tdd_orchestrator.py](../../cortex/orchestrators/core/tdd_orchestrator.py)

---

**Questions?** See [CORTEX.prompt.md](../.github/prompts/CORTEX.prompt.md) for full protocol.
