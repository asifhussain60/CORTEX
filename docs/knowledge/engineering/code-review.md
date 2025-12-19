# Code Review Best Practices

**Version:** 1.0 | **Author:** CORTEX Knowledge Library
**Source:** Industry standards (OWASP, Google Code Review, Microsoft Code Review)

**Description:** Comprehensive code review checklist with automated detection rules

---

## Security Review

### SECURITY_001: Input Validation

**Severity:** `CRITICAL` | **Category:** `security`

**Description:** All external inputs must be validated before use

#### Checklist

- [ ] Validate all user inputs (forms, APIs, CLI args)
- [ ] Use allowlists over denylists
- [ ] Sanitize inputs before database queries (prevent SQL injection)
- [ ] Sanitize inputs before rendering (prevent XSS)
- [ ] Validate file uploads (type, size, content)

#### Detection Rules

**Patterns to detect:**

- `request.args.get() without validation`
- `request.form.get() without validation`
- `request.json without schema validation`
- `raw SQL with string concatenation`
- `eval() or exec() on user input`

**Recommended tools:**

- **Bandit:** `bandit -r src/`
- **Semgrep:** `semgrep --config=p/security-audit`

❌ **Bad Example:**
```python
# Python
user_id = request.args.get('user_id')
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!

# C#
string query = "SELECT * FROM users WHERE id = " + userId;  // SQL injection!
```

✅ **Good Example:**
```python
# Python
user_id = request.args.get('user_id', type=int)
if not user_id or user_id <= 0:
    abort(400, "Invalid user_id")
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))  # Parameterized query

# C#
int userId = int.Parse(Request.QueryString["userId"]);
string query = "SELECT * FROM users WHERE id = @userId";
cmd.Parameters.AddWithValue("@userId", userId);  // Parameterized query
```

---

### SECURITY_002: Authentication & Authorization

**Severity:** `CRITICAL` | **Category:** `security`

**Description:** Verify authentication and authorization checks are present

#### Checklist

- [ ] Authentication required for all protected endpoints
- [ ] Authorization checks before sensitive operations
- [ ] Role-based access control (RBAC) enforced
- [ ] Session management secure (timeout, regeneration)
- [ ] Password policies enforced (complexity, hashing)

#### Detection Rules

**Patterns to detect:**

- `API endpoint without @login_required or @authorize`
- `Sensitive operation without permission check`
- `Plain text passwords in logs or database`
- `Weak hashing (MD5, SHA1)`

**Recommended tools:**

- **Bandit:** `None`

❌ **Bad Example:**
```python
# No authentication check
@app.route('/admin/delete_user/<user_id>')
def delete_user(user_id):
    User.delete(user_id)  # Anyone can delete!
```

✅ **Good Example:**
```python
@app.route('/admin/delete_user/<user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    if not current_user.can_delete_user(user_id):
        abort(403, "Insufficient permissions")
    User.delete(user_id)
```

---

### SECURITY_003: Sensitive Data Exposure

**Severity:** `CRITICAL` | **Category:** `security`

**Description:** Prevent leaking sensitive data in logs, errors, or responses

#### Checklist

- [ ] PII never logged (emails, SSNs, credit cards)
- [ ] Secrets not hardcoded (API keys, passwords)
- [ ] Error messages don't expose internal details
- [ ] Debug mode disabled in production
- [ ] Stack traces not exposed to users

#### Detection Rules

**Patterns to detect:**

- `logger.info containing email, password, ssn, credit_card`
- `Hardcoded API_KEY, SECRET_KEY, PASSWORD`
- `DEBUG = True in production config`
- `Exception details in API responses`

**Recommended tools:**

- **TruffleHog:** `trufflehog git file://.`
- **Detect-Secrets:** `detect-secrets scan`

❌ **Bad Example:**
```python
# Logging PII
logger.info(f"User login: {user.email} with password {password}")

# Hardcoded secret
API_KEY = "sk-1234567890abcdef"

# Exposing stack trace
except Exception as e:
    return {"error": str(e), "traceback": traceback.format_exc()}
```

✅ **Good Example:**
```python
# Hash PII in logs
logger.info(f"User login: {hash(user.email)}")

# Use environment variables
API_KEY = os.environ["API_KEY"]

# Generic error message
except Exception as e:
    logger.exception("Error processing request")
    return {"error": "internal_error", "message": "Please contact support"}
```

---

### SECURITY_004: Cryptography

**Severity:** `HIGH` | **Category:** `security`

**Description:** Use strong cryptography and secure random number generation

#### Checklist

- [ ] Use bcrypt/Argon2 for password hashing (NOT MD5/SHA1)
- [ ] Use secure random for tokens (secrets.token_urlsafe, NOT random)
- [ ] Encrypt sensitive data at rest (AES-256)
- [ ] Use TLS 1.2+ for data in transit
- [ ] Verify certificates in HTTPS requests

#### Detection Rules

**Patterns to detect:**

- `hashlib.md5() or hashlib.sha1() for passwords`
- `random.random() for security tokens`
- `requests.get(..., verify=False)`

**Recommended tools:**

- **Bandit:** `None`

❌ **Bad Example:**
```python
import hashlib
import random

# Weak hashing
password_hash = hashlib.md5(password.encode()).hexdigest()

# Insecure random
token = ''.join(random.choice(string.ascii_letters) for _ in range(32))
```

✅ **Good Example:**
```python
import secrets
from werkzeug.security import generate_password_hash

# Strong hashing
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# Secure random
token = secrets.token_urlsafe(32)
```

---

## Code Quality Review
