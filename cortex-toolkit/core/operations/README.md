# CORTEX Toolkit - System Operations

System operations and orchestration tools for CORTEX workflows.

## Tools

### review (`cortex-review`)

**Purpose:** Code review orchestration and management.

**Usage:**
```bash
python cortex-toolkit/core/operations/review.py
python cortex-toolkit/shared/toolkit_registry.py invoke review
```

**Implementation:** `cli/wrappers/review_wrapper.py`

---

### deploy (`cortex-deploy`)

**Purpose:** Deployment to publish directory with validation.

**Usage:**
```bash
python cortex-toolkit/core/operations/deploy.py
python cortex-toolkit/shared/toolkit_registry.py invoke deploy
```

**Requires:** Admin privileges

**Implementation:** `cli/wrappers/deploy_wrapper.py`

---

### sanitize (`cortex-sanitize`)

**Purpose:** Code sanitization for sharing (removes company-specific data).

**Usage:**
```bash
python cortex-toolkit/core/operations/sanitize.py [directory]
python cortex-toolkit/shared/toolkit_registry.py invoke sanitize [directory]
```

**Implementation:** `cli/wrappers/sanitize_wrapper.py`

**Features:**
- Remove company-specific data
- Transform domain terminology
- Validate builds and tests
- Generate audit report

---

## Architecture

System operations use CLI wrappers for consistent error handling and logging.

## Security

- Deploy operations require admin privileges
- All operations log to audit trail: `logs/toolkit-audit.log`
- Sensitive data sanitized in logs
