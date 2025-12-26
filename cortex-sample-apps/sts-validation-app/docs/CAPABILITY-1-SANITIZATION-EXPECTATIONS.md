# Capability 1: Code Sanitization - Validation Expectations

## 🧠 CORTEX Capability 1 Testing
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

**Purpose:** Define expected behavior for CORTEX Code Sanitization capability when processing STS validation app.

**Created:** 2025-12-25 | **Phase:** 13B Week 1 Day 3

---

## 📋 Hardcoded Secrets Catalog

Based on STS-MANIFEST.json and code analysis, the following hardcoded secrets must be detected and sanitized:

### 1. SEC-01: JWT Secret Key
- **Location:** `src/api/auth.py:27`
- **Current Code:**
  ```python
  JWT_SECRET = "super_secret_key_12345"
  ```
- **Severity:** CRITICAL (CWE-798)
- **OWASP:** A02:2021 - Cryptographic Failures
- **Detection Pattern:** `JWT_SECRET = "`

### 2. SEC-08-A: SMTP Credentials (Orders)
- **Location:** `src/api/orders.py:406`
- **Current Code:**
  ```python
  server.login("orders@example.com", "hardcoded_password_123")
  ```
- **Severity:** CRITICAL (CWE-798)
- **OWASP:** A02:2021 - Cryptographic Failures
- **Detection Pattern:** `login\([^,]+,\s*["'][^"']+["']\)`

### 3. SEC-08-B: SMTP Credentials (Users)
- **Location:** `src/api/users.py:103`
- **Current Code:**
  ```python
  self.smtp_password = "hardcoded_email_password_123"
  ```
- **Severity:** HIGH (CWE-798)
- **OWASP:** A02:2021 - Cryptographic Failures
- **Detection Pattern:** `smtp_password = "`

### 4. SEC-08-C: SMTP Server Configuration (Users)
- **Location:** `src/api/users.py:100-102`
- **Current Code:**
  ```python
  self.smtp_server = "smtp.gmail.com"
  self.smtp_port = 587
  self.smtp_user = "admin@example.com"
  ```
- **Severity:** MEDIUM (configuration in code)
- **Detection Pattern:** `smtp_server = "|smtp_user = "`

### 5. Implicit: Database Path
- **Location:** `src/data/database.py` (DATABASE_PATH)
- **Severity:** LOW (not a secret, but configuration)
- **Should Be:** Environment variable for deployment flexibility

---

## 🎯 Sanitization Transformation Expectations

### Expected Transformations (BEFORE → AFTER)

#### 1. JWT Secret
**BEFORE:**
```python
JWT_SECRET = "super_secret_key_12345"
```

**AFTER:**
```python
import os
JWT_SECRET = os.getenv('JWT_SECRET', 'default_dev_key')  # Default for dev only
```

**Mapping Entry:**
```json
{
  "original_value": "super_secret_key_12345",
  "placeholder": "JWT_SECRET",
  "env_variable": "JWT_SECRET",
  "location": "src/api/auth.py:27"
}
```

#### 2. SMTP Password (Orders)
**BEFORE:**
```python
server.login("orders@example.com", "hardcoded_password_123")
```

**AFTER:**
```python
smtp_user = os.getenv('SMTP_USER', 'orders@example.com')
smtp_password = os.getenv('SMTP_PASSWORD')
server.login(smtp_user, smtp_password)
```

**Mapping Entry:**
```json
{
  "original_value": "hardcoded_password_123",
  "placeholder": "SMTP_PASSWORD",
  "env_variable": "SMTP_PASSWORD",
  "location": "src/api/orders.py:406"
}
```

#### 3. SMTP Configuration (Users)
**BEFORE:**
```python
self.smtp_server = "smtp.gmail.com"
self.smtp_port = 587
self.smtp_user = "admin@example.com"
self.smtp_password = "hardcoded_email_password_123"
```

**AFTER:**
```python
self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
self.smtp_user = os.getenv('SMTP_USER', 'admin@example.com')
self.smtp_password = os.getenv('SMTP_PASSWORD')
```

**Mapping Entries:**
```json
[
  {
    "original_value": "admin@example.com",
    "placeholder": "SMTP_USER",
    "env_variable": "SMTP_USER",
    "location": "src/api/users.py:102"
  },
  {
    "original_value": "hardcoded_email_password_123",
    "placeholder": "SMTP_PASSWORD",
    "env_variable": "SMTP_PASSWORD",
    "location": "src/api/users.py:103"
  }
]
```

---

## 📄 Expected Artifacts

### 1. Sanitization Mapping (.mapping.json)
**File:** `sts-validation-app/.mapping.json`

**Structure:**
```json
{
  "metadata": {
    "sanitization_date": "2025-12-25T...",
    "cortex_version": "4.0.0",
    "total_secrets_found": 5,
    "total_secrets_sanitized": 5
  },
  "secrets": [
    {
      "id": "SECRET-001",
      "type": "jwt_secret",
      "original_value": "super_secret_key_12345",
      "placeholder": "JWT_SECRET",
      "env_variable": "JWT_SECRET",
      "file": "src/api/auth.py",
      "line": 27,
      "severity": "CRITICAL",
      "owasp": "A02:2021",
      "cwe": "CWE-798"
    },
    {
      "id": "SECRET-002",
      "type": "smtp_password",
      "original_value": "hardcoded_password_123",
      "placeholder": "SMTP_PASSWORD",
      "env_variable": "SMTP_PASSWORD",
      "file": "src/api/orders.py",
      "line": 406,
      "severity": "CRITICAL"
    },
    {
      "id": "SECRET-003",
      "type": "smtp_password",
      "original_value": "hardcoded_email_password_123",
      "placeholder": "SMTP_PASSWORD",
      "env_variable": "SMTP_PASSWORD",
      "file": "src/api/users.py",
      "line": 103,
      "severity": "HIGH"
    },
    {
      "id": "SECRET-004",
      "type": "smtp_user",
      "original_value": "admin@example.com",
      "placeholder": "SMTP_USER",
      "env_variable": "SMTP_USER",
      "file": "src/api/users.py",
      "line": 102,
      "severity": "MEDIUM"
    },
    {
      "id": "SECRET-005",
      "type": "smtp_server",
      "original_value": "smtp.gmail.com",
      "placeholder": "SMTP_SERVER",
      "env_variable": "SMTP_SERVER",
      "file": "src/api/users.py",
      "line": 100,
      "severity": "LOW"
    }
  ]
}
```

### 2. Environment Template (.env.template)
**File:** `sts-validation-app/.env.template`

**Content:**
```bash
# JWT Configuration
JWT_SECRET=your_jwt_secret_here

# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_smtp_user@example.com
SMTP_PASSWORD=your_smtp_password_here

# Database Configuration (optional)
DATABASE_PATH=./data/ecommerce.db
```

### 3. Environment Example (.env.example)
**File:** `sts-validation-app/.env.example`

**Content:**
```bash
# Example configuration for local development
JWT_SECRET=dev_secret_key_for_testing_only
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@example.com
SMTP_PASSWORD=dev_password
DATABASE_PATH=./data/ecommerce_dev.db
```

---

## ✅ Success Criteria

### Detection (40 points)
- ✅ **100% Detection Rate:** All 5 hardcoded secrets must be identified
- ✅ **Correct Severity:** Each secret classified with appropriate severity level
- ✅ **Accurate Location:** File path and line numbers must be exact
- ✅ **Pattern Recognition:** Detection patterns must match STS-MANIFEST.json

### Transformation (40 points)
- ✅ **Complete Replacement:** All hardcoded values replaced with environment variables
- ✅ **Import Addition:** `import os` added where needed
- ✅ **Fallback Handling:** Development defaults provided for non-critical secrets
- ✅ **Code Functionality:** Application builds and runs after sanitization

### Mapping (20 points)
- ✅ **Mapping Accuracy:** .mapping.json contains all 5 secrets with correct metadata
- ✅ **Template Generation:** .env.template created with all required variables
- ✅ **Example Configuration:** .env.example created for development reference
- ✅ **Documentation:** Clear instructions for restoring original values if needed

---

## 🧪 Validation Test Plan

### Test 1: Detection Accuracy
**Command:** (Simulated CORTEX sanitize scan)
```bash
# In real CORTEX: cortex sanitize scan sts-validation-app/
# Manual simulation: grep for hardcoded patterns
```

**Expected Output:**
```
🔍 Scanning for hardcoded secrets...
✅ Found 5 hardcoded secrets:
  - CRITICAL: JWT_SECRET in src/api/auth.py:27
  - CRITICAL: SMTP password in src/api/orders.py:406
  - HIGH: SMTP password in src/api/users.py:103
  - MEDIUM: SMTP user in src/api/users.py:102
  - LOW: SMTP server in src/api/users.py:100
```

### Test 2: Transformation Correctness
**Command:** (Simulated CORTEX sanitize apply)
```bash
# In real CORTEX: cortex sanitize apply sts-validation-app/
# Manual simulation: Apply transformations, verify syntax
```

**Expected Output:**
- All Python files remain syntactically valid
- No hardcoded strings remain in flagged locations
- `os.getenv()` calls present with appropriate defaults

### Test 3: Application Functionality
**Command:**
```bash
cd sts-validation-app
python3 -m pytest tests/
```

**Expected Output:**
```
===== test session starts =====
collected 3 items

tests/test_api.py::test_health_endpoint PASSED
tests/test_api.py::test_auth_login PASSED
tests/test_api.py::test_products_list PASSED

===== 3 passed in 0.5s =====
```

### Test 4: Mapping Validation
**Command:**
```bash
cat .mapping.json | python3 -m json.tool
```

**Expected Output:**
- Valid JSON structure
- 5 secret entries with complete metadata
- Severity levels match STS-MANIFEST.json classifications

---

## 📊 Scoring Rubric

| Criterion | Points | Validation Method |
|-----------|--------|------------------|
| **Detection Rate** | 20 | 5/5 secrets found = 20 pts, 4/5 = 16 pts, etc. |
| **Severity Accuracy** | 10 | All severities correct = 10 pts, 1 wrong = 8 pts |
| **Location Accuracy** | 10 | All locations exact = 10 pts, 1 wrong = 8 pts |
| **Transformation Complete** | 20 | All secrets replaced = 20 pts, 1 missed = 16 pts |
| **Code Validity** | 15 | Builds without errors = 15 pts, syntax errors = 0 pts |
| **Tests Pass** | 10 | 3/3 tests pass = 10 pts, 2/3 = 6 pts, 1/3 = 3 pts |
| **Mapping Accuracy** | 10 | All 5 in mapping = 10 pts, 4/5 = 8 pts, etc. |
| **Template Quality** | 5 | .env.template complete and correct |
| **TOTAL** | **100** | Pass threshold: ≥85/100 |

---

## 🎯 Expected Baseline → Post-Sanitization Delta

### Security Score
- **Before:** 25/100 (12 security flaws)
- **After:** 45/100 (7 security flaws remaining)
- **Delta:** +20 points (5 hardcoded secrets eliminated)

### Flaw Count
- **Before:** 61 total flaws (12 SEC, 15 SOL, 20 CQ, 8 PERF, 3 TEST, 8 DOC)
- **After:** 56 total flaws (7 SEC, 15 SOL, 20 CQ, 8 PERF, 3 TEST, 8 DOC)
- **Delta:** -5 SEC flaws (SEC-01, SEC-08 variants eliminated)

### Test Coverage
- **Before:** 15% (placeholder tests)
- **After:** 15% (unchanged - sanitization doesn't add tests)
- **Delta:** No change

---

## 🚨 Common Failure Modes to Avoid

### ❌ False Positive Detection
- **Issue:** Detecting comments or strings that aren't actual secrets
- **Example:** `# TODO: Add JWT_SECRET configuration` should NOT be flagged
- **Prevention:** Pattern matching must validate actual assignment/usage

### ❌ Incomplete Transformation
- **Issue:** Replacing only some occurrences of a secret
- **Example:** JWT_SECRET replaced in auth.py but not in token verification
- **Prevention:** Search entire codebase for all references

### ❌ Breaking Changes
- **Issue:** Application fails after sanitization
- **Example:** Missing `import os` causes NameError
- **Prevention:** Syntax validation and test execution required

### ❌ Missing Documentation
- **Issue:** No .env.template or instructions for users
- **Example:** User doesn't know what environment variables to set
- **Prevention:** Generate complete templates and documentation

---

## 📝 Next Steps After Validation

1. **Execute transformation** (manually simulate CORTEX behavior)
2. **Verify all 5 secrets replaced** (grep for original values)
3. **Run test suite** (pytest to confirm functionality)
4. **Create validation report** (document detection rate, transformation accuracy, scoring)
5. **Update sts-baseline.json** (record new security score)
6. **Move to Capability 2** (Planning System validation)

---

**Status:** ✅ Expectations defined - Ready for transformation execution
