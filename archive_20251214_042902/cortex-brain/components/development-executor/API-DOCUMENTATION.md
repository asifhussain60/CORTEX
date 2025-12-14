# Development Executor API Documentation
**Version:** 1.0  
**Last Updated:** 2025-11-19  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## Overview

The **Development Executor** is a standalone component that enforces clean code, TDD practices, and security gates during feature implementation. It can work:
- **Standalone:** Direct implementation without formal planning
- **Integrated:** As part of the sequential planning → development pipeline

---

## Architecture

```
┌────────────────────────────────────────────────┐
│         Development Executor Component         │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  1. Clean Code Gates (Pre-Commit)        │ │
│  │     - PyLint: Unused imports/variables   │ │
│  │     - Radon: Complexity checks           │ │
│  │     - Commented code detection           │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  2. TDD Framework (Red-Green-Refactor)   │ │
│  │     - Quality tiers (simple/medium/complex) │
│  │     - Max 3 refactor cycles              │ │
│  │     - Coverage targets: 80-90%           │ │
│  └──────────────────────────────────────────┘ │
│                                                │
│  ┌──────────────────────────────────────────┐ │
│  │  3. Security Gates (Pre-Commit/Pre-Merge)│ │
│  │     - detect-secrets: Hardcoded secrets  │ │
│  │     - Bandit: SAST analysis              │ │
│  │     - pip-audit: CVE scanning            │ │
│  └──────────────────────────────────────────┘ │
│                                                │
└────────────────────────────────────────────────┘
```

---

## Component Files

| File | Purpose | Location |
|------|---------|----------|
| `clean-code-gates.yaml` | PyLint, Radon, commented code rules | `cortex-brain/components/development-executor/` |
| `tdd-framework.yaml` | Quality tiers, Red-Green-Refactor workflow | `cortex-brain/components/development-executor/` |
| `security-gates.yaml` | OWASP checks, secret detection, CVE scanning | `cortex-brain/components/development-executor/` |
| `.git/hooks/pre-commit` | Git hook enforcing TDD + security gates | `.git/hooks/` |

---

## Usage Patterns

### Pattern 1: Standalone Implementation (No Planning)

**User Says:** "add login button"

**CORTEX Actions:**
1. **Auto-generates** simple acceptance criteria:
   ```yaml
   acceptance_criteria:
     - "Button labeled 'Login' appears on page"
     - "Button triggers authentication flow on click"
     - "Button is accessible (ARIA labels present)"
   ```

2. **Routes to Development Executor:**
   - Loads `clean-code-gates.yaml`
   - Loads `tdd-framework.yaml` (auto-detects "Simple" tier)
   - Loads `security-gates.yaml`

3. **Writes code** following gates:
   ```python
   # Example: login_button.py
   def create_login_button():
       """Create accessible login button"""
       return {
           'label': 'Login',
           'onclick': 'authenticate()',
           'aria_label': 'Login to account'
       }
   ```

4. **Writes tests first** (TDD Red phase):
   ```python
   # Example: test_login_button.py
   def test_login_button_has_label():
       button = create_login_button()
       assert button['label'] == 'Login'
   
   def test_login_button_has_onclick():
       button = create_login_button()
       assert button['onclick'] == 'authenticate()'
   
   def test_login_button_accessible():
       button = create_login_button()
       assert 'aria_label' in button
   ```

5. **Runs clean code gates:**
   - PyLint: Check for unused imports
   - Radon: Check complexity (target: ≤5 for simple)
   - Commented code: No commented-out code allowed

6. **Runs security gates:**
   - detect-secrets: No hardcoded credentials
   - Bandit: No security issues (HIGH/CRITICAL block commit)

7. **Git pre-commit hook** validates before commit

---

### Pattern 2: Integrated with Planning (Sequential Pipeline)

**User Says:** "approve plan" (after planning authentication)

**CORTEX Actions:**
1. **Loads approved planning document:**
   ```yaml
   acceptance_criteria:
     - "User can login with email/password"
     - "Invalid credentials show error message"
     - "Successful login redirects to dashboard"
     - "Session expires after 1 hour"
   
   risks:
     - "Brute force attacks (rate limiting needed)"
     - "Session hijacking (secure cookies)"
   
   security_requirements:
     - "A01: Implement auth decorators for protected routes"
     - "A02: Use bcrypt for password hashing"
     - "A07: Lock account after 5 failed attempts"
   ```

2. **Routes to Development Executor** with enriched context

3. **Auto-detects complexity tier:** "Complex" (authentication = security-critical)
   ```yaml
   quality_tier: complex
   coverage_target: 90%
   max_refactor_cycles: 3
   complexity_threshold: 10
   ```

4. **Implements with TDD workflow:**
   - **Red:** Write failing tests for each AC
   - **Green:** Write minimal code to pass tests
   - **Refactor:** Improve code quality (max 3 cycles)

5. **Enforces security gates:**
   - Bandit HIGH/CRITICAL: BLOCKING
   - pip-audit CVE check: BLOCKING (CRITICAL/HIGH)
   - detect-secrets: BLOCKING

6. **Validates before commit:**
   - Test coverage ≥90% (complex tier)
   - Complexity ≤10 per function
   - No security issues (HIGH/CRITICAL)
   - No unused code

---

## Quality Tiers (Auto-Detection)

### Tier 1: Simple (80% coverage, complexity ≤5)

**Triggers:**
- "button", "label", "config", "constant"
- Simple UI elements
- Data classes without logic

**Example:** Add login button, create config file, define constants

**Gates:**
- Coverage: 80% minimum
- Complexity: ≤5 per function
- Refactor cycles: 1 max

---

### Tier 2: Medium (85% coverage, complexity ≤8)

**Triggers:**
- "form", "validation", "api endpoint", "service"
- Business logic without security concerns
- CRUD operations

**Example:** Create user registration form, implement API endpoint

**Gates:**
- Coverage: 85% minimum
- Complexity: ≤8 per function
- Refactor cycles: 2 max

---

### Tier 3: Complex (90% coverage, complexity ≤10)

**Triggers:**
- "authentication", "payment", "security", "encryption"
- Security-critical features
- Financial transactions
- Data integrity operations

**Example:** Implement authentication, payment processing, encryption

**Gates:**
- Coverage: 90% minimum
- Complexity: ≤10 per function
- Refactor cycles: 3 max
- Security review: MANDATORY

---

## Clean Code Gates

### Gate 1: Unused Code Detection (BLOCKING)

**Tool:** PyLint

**What it checks:**
- Unused imports (`import os` but never use `os`)
- Unused variables (`x = 5` but `x` never used)
- Unused function arguments

**Severity:** BLOCKING (commit fails)

**Example:**
```python
# ❌ FAIL
import os  # Unused import
import sys

def login(username, password, remember_me):  # `remember_me` unused
    return authenticate(username, password)

# ✅ PASS
import sys

def login(username, password):
    return authenticate(username, password)
```

---

### Gate 2: Commented Code Detection (BLOCKING)

**What it checks:**
- Commented-out code blocks (except TODO/FIXME/HACK)

**Exceptions allowed:**
- `# TODO: Implement feature X`
- `# FIXME: Bug with edge case Y`
- `# HACK: Workaround for library Z issue`

**Severity:** BLOCKING (commit fails)

**Example:**
```python
# ❌ FAIL
def login(username, password):
    # old_method(username)  # Commented-out code
    return new_method(username, password)

# ✅ PASS
def login(username, password):
    # TODO: Add remember-me functionality
    return new_method(username, password)
```

---

### Gate 3: Complexity Check (WARNING → BLOCKING)

**Tool:** Radon

**Thresholds:**
| Tier | Complexity Threshold | Enforcement |
|------|---------------------|-------------|
| Simple | ≤5 | WARNING (first commit), BLOCKING (PR) |
| Medium | ≤8 | WARNING (first commit), BLOCKING (PR) |
| Complex | ≤10 | WARNING (first commit), BLOCKING (PR) |

**Pragmatic approach:** First commit allows complexity warnings (but logs them). PR review enforces BLOCKING.

**Example:**
```python
# ❌ FAIL (Complexity = 12)
def process_payment(amount, currency, card, cvv, address, retry_count):
    if currency == 'USD':
        if amount > 1000:
            if retry_count < 3:
                if validate_card(card):
                    if validate_cvv(cvv):
                        if validate_address(address):
                            return charge_card(amount, card)
    return None

# ✅ PASS (Complexity = 4) - Refactored
def process_payment(payment_request):
    if not payment_request.is_valid():
        return None
    return charge_card(payment_request)
```

---

## TDD Framework

### Red-Green-Refactor Cycle

**Red Phase: Write Failing Tests**
```python
# test_authentication.py
def test_login_with_valid_credentials():
    result = authenticate('user@example.com', 'correct_password')
    assert result['success'] is True
    assert 'token' in result

def test_login_with_invalid_credentials():
    result = authenticate('user@example.com', 'wrong_password')
    assert result['success'] is False
    assert result['error'] == 'Invalid credentials'
```

**Green Phase: Write Minimal Code**
```python
# authentication.py
def authenticate(email, password):
    user = db.get_user_by_email(email)
    if user and user.check_password(password):
        return {'success': True, 'token': generate_token(user)}
    return {'success': False, 'error': 'Invalid credentials'}
```

**Refactor Phase: Improve Quality (Max 3 Cycles)**
```python
# authentication.py (Refactored - Cycle 1)
class AuthenticationService:
    def __init__(self, user_repository):
        self.user_repo = user_repository
    
    def authenticate(self, email, password):
        user = self.user_repo.find_by_email(email)
        if self._is_valid_login(user, password):
            return self._success_response(user)
        return self._error_response('Invalid credentials')
    
    def _is_valid_login(self, user, password):
        return user is not None and user.check_password(password)
    
    def _success_response(self, user):
        return {'success': True, 'token': self._generate_token(user)}
    
    def _error_response(self, message):
        return {'success': False, 'error': message}
```

**Refactor Cycle Limit:** Max 3 cycles to prevent infinite refactoring loops

**Escalation:** After 3 cycles, if quality still not met → Document issues, continue (pragmatic approach)

---

## Security Gates

### Gate 1: Secret Detection (BLOCKING)

**Tool:** detect-secrets

**What it checks:**
- Hardcoded passwords
- API keys
- Private keys
- Database credentials
- AWS secrets

**Severity:** BLOCKING (commit fails immediately)

**Example:**
```python
# ❌ FAIL
DB_PASSWORD = "super_secret_123"
API_KEY = "sk_live_abc123xyz"

# ✅ PASS
import os
DB_PASSWORD = os.environ.get('DB_PASSWORD')
API_KEY = os.environ.get('API_KEY')
```

---

### Gate 2: SAST Analysis (BLOCKING for HIGH/CRITICAL)

**Tool:** Bandit

**What it checks:**
- SQL injection vulnerabilities
- Command injection
- Insecure deserialization (pickle)
- Weak cryptography (MD5, SHA1)
- Unsafe YAML loading

**Severity:**
- HIGH/CRITICAL: BLOCKING
- MEDIUM: WARNING
- LOW: INFO

**Example:**
```python
# ❌ FAIL (SQL Injection - HIGH severity)
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ PASS
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
```

---

### Gate 3: CVE Scanning (BLOCKING for CRITICAL/HIGH)

**Tool:** pip-audit

**What it checks:**
- Known CVEs in dependencies
- Outdated packages with security fixes

**Severity:**
- CRITICAL/HIGH: BLOCKING
- MEDIUM: WARNING
- LOW: INFO

**Scheduled:** Daily scans + pre-merge checks

**Example:**
```bash
# ❌ FAIL
requests==2.25.0  # CVE-2023-32681 (HIGH)

# ✅ PASS
requests==2.31.0  # Patched version
```

---

## Git Pre-Commit Hook

### What It Does

1. **TDD Violation Detection:**
   - Checks if source files modified without test updates
   - Format: `src/module.py` modified → `tests/test_module.py` must be modified too

2. **Runs Security Gates:**
   - detect-secrets: Scan staged files
   - Bandit: HIGH severity check only (pre-commit)

3. **Runs Clean Code Gates:**
   - PyLint: Unused imports/variables
   - Radon: Complexity check (warning only, not blocking pre-commit)

4. **Exit Codes:**
   - `0` = All checks passed → Commit proceeds
   - `1` = Checks failed → Commit blocked

### Bypass (Emergency Only)

```bash
git commit --no-verify -m "Emergency fix (skip hooks)"
```

**Note:** Bypass requires justification in commit message and will be flagged in PR review

---

## API Reference

### Python API (Development Executor)

**Not yet implemented** - Phase 4 deliverable will include:

```python
from cortex.components.development_executor import DevelopmentExecutor

# Standalone mode
executor = DevelopmentExecutor()
result = executor.implement(
    user_request="add login button",
    auto_generate_ac=True  # Generate simple acceptance criteria
)

# Integrated mode (with planning document)
executor = DevelopmentExecutor()
result = executor.implement_from_plan(
    planning_document_path="cortex-brain/documents/planning/features/PLAN-2025-11-17-authentication.md"
)
```

---

## Configuration

### Default Settings

**File:** `cortex-brain/components/development-executor/config.yaml` (not yet created)

```yaml
clean_code:
  enforce_unused_detection: true
  enforce_commented_code: true
  complexity_mode: "warning_then_blocking"  # First commit = warning, PR = blocking

tdd:
  default_tier: "auto_detect"  # Auto-detect from keywords
  max_refactor_cycles: 3
  escalation_after_max_cycles: "document_and_continue"

security:
  detect_secrets: 
    enabled: true
    severity: "blocking"
  bandit:
    enabled: true
    pre_commit_severity: "high"  # Only HIGH+ blocks pre-commit
    pre_merge_severity: "medium"  # MEDIUM+ blocks pre-merge
  pip_audit:
    enabled: true
    pre_merge_severity: "high"  # CRITICAL/HIGH blocks pre-merge
    scheduled_scan: "daily"
```

---

## Metrics & Monitoring

### Metrics Tracked

**File:** `cortex-brain/metrics/development-executor-metrics.jsonl`

```jsonl
{
  "timestamp": "2025-11-19T10:30:00Z",
  "feature": "authentication",
  "quality_tier": "complex",
  "test_coverage": 92.5,
  "complexity_max": 8,
  "refactor_cycles": 2,
  "security_issues": 0,
  "clean_code_violations": 0,
  "implementation_time_minutes": 45,
  "planning_time_minutes": 30
}
```

---

## Error Handling

### Scenario 1: Test Coverage Below Threshold

**Error:**
```
❌ Test coverage (75%) below threshold (90% for complex tier)
```

**Resolution:**
1. Add missing test cases
2. Run `pytest --cov=src/module --cov-report=term-missing`
3. Identify untested lines
4. Write tests for untested code

---

### Scenario 2: Security Gate Failure

**Error:**
```
❌ Bandit found HIGH severity issue: SQL injection in src/api/users.py:45
```

**Resolution:**
1. Review Bandit output
2. Fix security issue (use parameterized queries)
3. Re-run Bandit: `bandit -r src/`
4. Commit after fix

---

### Scenario 3: Max Refactor Cycles Exceeded

**Error:**
```
⚠️ Max refactor cycles (3) exceeded. Complexity still 12 (target: ≤10)
```

**Resolution (Pragmatic):**
1. Document complexity issue in code comments:
   ```python
   # TODO: Refactor to reduce complexity from 12 to ≤10
   # Current blocker: Complex business logic in payment flow
   ```
2. Create technical debt ticket
3. Continue with implementation
4. Address in future refactoring sprint

---

## Integration with CORTEX Ecosystem

### Tier 1: Working Memory
- **Auto-inject planning documents** when user says "implement planned feature"
- Load AC, risks, security requirements into context

### Tier 2: Knowledge Graph
- **Learn from implementations:** Track patterns (feature type → quality tier → implementation time)
- Store successful implementations for future similarity matching

### Tier 3: Long-Term Memory
- **Store completed implementations** in `cortex-brain/archives/implementations/`
- Reference for future similar features

### Work Planner Agent
- **Delegate planning** when user says "plan [feature]"
- Auto-route to Development Executor after plan approval

---

## Examples

### Example 1: Simple Feature (Button)

**User:** "add logout button"

**Auto-detected Tier:** Simple (button = UI element)

**Generated AC:**
```yaml
- Button labeled "Logout" appears in navigation
- Button triggers logout flow on click
- Button is accessible (ARIA labels)
```

**Coverage Target:** 80%

**Complexity Target:** ≤5

**Result:**
```python
# src/components/logout_button.py
def create_logout_button():
    """Create accessible logout button"""
    return {
        'label': 'Logout',
        'onclick': 'logout()',
        'aria_label': 'Logout from account'
    }

# tests/test_logout_button.py
def test_logout_button_label():
    button = create_logout_button()
    assert button['label'] == 'Logout'

def test_logout_button_onclick():
    button = create_logout_button()
    assert button['onclick'] == 'logout()'

def test_logout_button_accessible():
    button = create_logout_button()
    assert 'aria_label' in button
```

**Gates Passed:**
- ✅ Coverage: 100% (target: 80%)
- ✅ Complexity: 2 (target: ≤5)
- ✅ Security: No issues
- ✅ Clean code: No violations

---

### Example 2: Complex Feature (Authentication)

**User:** "implement authentication" (after planning phase)

**Auto-detected Tier:** Complex (authentication = security-critical)

**Loaded from Planning Document:**
```yaml
acceptance_criteria:
  - User can login with email/password
  - Invalid credentials show error
  - Session expires after 1 hour
  - Account locks after 5 failed attempts

security_requirements:
  - A01: Auth decorators for protected routes
  - A02: bcrypt for password hashing
  - A07: Rate limiting (5 attempts/hour)
```

**Coverage Target:** 90%

**Complexity Target:** ≤10

**TDD Workflow:**

**Red Phase:**
```python
# tests/test_authentication.py
def test_login_success():
    result = auth.authenticate('user@example.com', 'correct_password')
    assert result['success'] is True

def test_login_failure():
    result = auth.authenticate('user@example.com', 'wrong_password')
    assert result['success'] is False

def test_account_lockout_after_5_failures():
    for _ in range(5):
        auth.authenticate('user@example.com', 'wrong')
    result = auth.authenticate('user@example.com', 'correct_password')
    assert result['error'] == 'Account locked'
```

**Green Phase:**
```python
# src/authentication.py
import bcrypt
from datetime import datetime, timedelta

class AuthenticationService:
    def authenticate(self, email, password):
        user = self.user_repo.find_by_email(email)
        
        if self._is_account_locked(user):
            return {'success': False, 'error': 'Account locked'}
        
        if user and self._verify_password(user, password):
            self._reset_failed_attempts(user)
            return {'success': True, 'token': self._generate_token(user)}
        
        self._increment_failed_attempts(user)
        return {'success': False, 'error': 'Invalid credentials'}
    
    def _is_account_locked(self, user):
        return user.failed_attempts >= 5 and \
               user.last_failed_attempt > datetime.now() - timedelta(hours=1)
    
    def _verify_password(self, user, password):
        return bcrypt.checkpw(password.encode(), user.password_hash)
```

**Gates Passed:**
- ✅ Coverage: 92% (target: 90%)
- ✅ Complexity: 8 (target: ≤10)
- ✅ Security: No issues (bcrypt used, rate limiting implemented)
- ✅ Clean code: No violations

---

## Troubleshooting

### Issue: Pre-commit hook not running

**Solution:**
```bash
# Make hook executable (Unix/Mac)
chmod +x .git/hooks/pre-commit

# Windows: No action needed (Git handles execution)
```

---

### Issue: False positive from detect-secrets

**Solution:**
```bash
# Create baseline file to ignore false positives
detect-secrets scan --baseline .secrets.baseline

# Update baseline when needed
detect-secrets scan --baseline .secrets.baseline --update .secrets.baseline
```

---

### Issue: Bandit flagging acceptable risk

**Solution:**
```python
# Add inline comment to suppress specific check
import pickle  # nosec B301 - Trusted data source only

# Or add to .bandit config
```

---

## Version History

### v1.0 (2025-11-19)
- Initial release
- Clean code gates (PyLint, Radon, commented code)
- TDD framework with quality tiers
- Security gates (detect-secrets, Bandit, pip-audit)
- Git pre-commit hook
- Integration with Intent Router

---

## Next Steps

1. **Python API Implementation** (Phase 4)
2. **Web UI Dashboard** (Future enhancement)
3. **IDE Integration** (VS Code extension)
4. **CI/CD Pipeline Integration** (GitHub Actions, Azure DevOps)

---

**End of Documentation**

For questions or contributions, see: `cortex-brain/documents/README.md`
