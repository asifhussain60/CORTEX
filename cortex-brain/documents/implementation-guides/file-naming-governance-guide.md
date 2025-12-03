# File Naming Governance Guide

**CORTEX 3.7.0** - Automated file naming validation and enforcement

---

## 🎯 Overview

CORTEX File Naming Governance system enforces consistent naming conventions across the codebase, automatically validates file names, suggests corrections, and prevents commits with naming violations.

**Benefits:**
- 🎯 **Consistent naming** across all file types
- ⚡ **Automatic validation** on save and commit
- 🔄 **Auto-rename utility** for bulk fixes
- 🛡️ **Git pre-commit hooks** prevent violations
- 📊 **Workspace reports** identify all violations

---

## 📐 Naming Conventions

### Python Files (.py)

**Convention:** `snake_case`

**Rules:**
- Lowercase letters only
- Words separated by underscores
- Numbers allowed
- No hyphens, spaces, or special characters

**Valid:**
```
user_service.py
test_user_service.py
api_client_v2.py
__init__.py
```

**Invalid:**
```
userService.py      # camelCase
UserService.py      # PascalCase
user-service.py     # kebab-case
user service.py     # spaces
```

### Markdown Files (.md)

**Convention:** `kebab-case`

**Rules:**
- Lowercase letters (except special files like README.md)
- Words separated by hyphens
- Numbers allowed
- No underscores, spaces, or special characters

**Valid:**
```
user-guide.md
api-documentation.md
shared-environment-setup.md
README.md           # Exception (uppercase allowed)
```

**Invalid:**
```
user_guide.md       # snake_case
userGuide.md        # camelCase
user guide.md       # spaces
```

### Configuration Files (.yaml, .yml, .json, .txt)

**Convention:** `kebab-case`

**Rules:**
- Same as markdown files
- Lowercase with hyphens
- Numbers allowed

**Valid:**
```
docker-compose.yaml
ci-config.yml
package-lock.json
cortex-config.json
```

**Invalid:**
```
docker_compose.yaml  # snake_case
ciConfig.yml         # camelCase
```

### General Rules (All Files)

1. **No spaces** - Always use snake_case or kebab-case
2. **Max length** - 100 characters including extension
3. **Allowed characters** - Only `a-z`, `0-9`, `_`, `-`, `.`
4. **No special characters** - No `@`, `#`, `$`, `%`, etc.

---

## 🚀 Usage

### Manual Validation

```bash
# Validate single file
cortex naming validate user_service.py

# Output:
# ✅ user_service.py: Valid (snake_case)

# Invalid file
cortex naming validate userService.py

# Output:
# ❌ userService.py: Invalid
# - Python files must use snake_case (found: userService)
# Suggested: user_service.py
```

### Workspace Scan

```bash
# Scan entire workspace
cortex naming scan

# Output:
# 📊 Naming Validation Report
#
# Total files scanned: 247
# Valid files: 235 (95.1%)
# Invalid files: 12 (4.9%)
#
# Violations:
# ❌ src/services/userService.py → user_service.py
# ❌ docs/user_guide.md → user-guide.md
# ❌ config/docker_compose.yaml → docker-compose.yaml
# ...
```

### Auto-Rename

```bash
# Dry-run (preview changes)
cortex naming fix --dry-run

# Output:
# 🔍 Dry-Run Mode (no changes will be made)
#
# Would rename:
# - src/services/userService.py → user_service.py
# - docs/user_guide.md → user-guide.md
# - config/docker_compose.yaml → docker-compose.yaml
#
# 3 files would be renamed

# Actually rename
cortex naming fix

# Output:
# ✅ Renamed: userService.py → user_service.py
# ✅ Renamed: user_guide.md → user-guide.md
# ✅ Renamed: docker_compose.yaml → docker-compose.yaml
#
# 3 files renamed successfully
```

### Batch Operations

```python
from src.governance.auto_rename_utility import AutoRenameUtility

utility = AutoRenameUtility()

# Rename multiple files
files = [
    "userService.py",
    "testUser.py",
    "apiClient.py"
]

results = utility.batch_rename(files, dry_run=False)

for filename, result in results.items():
    if result["success"]:
        print(f"✅ {filename} → {result['new_path']}")
    else:
        print(f"❌ {filename}: {result['error']}")
```

---

## 🔗 Git Integration

### Pre-Commit Hook

CORTEX automatically validates staged files before commit:

```bash
# Try to commit files with violations
git add userService.py
git commit -m "Add user service"

# Output:
# ❌ Commit blocked: Naming violations detected
#
# Invalid files:
# - userService.py (should be: user_service.py)
#
# Fix violations and try again, or use --no-verify to bypass
```

### Bypass (Emergency Only)

```bash
# Bypass validation (NOT RECOMMENDED)
git commit -m "Emergency fix" --no-verify
```

---

## 🎯 Exception Management

### Built-in Exceptions

Some files are automatically allowed regardless of convention:

```python
ALLOWED_EXCEPTIONS = {
    'LICENSE',
    'VERSION',
    'README.md',
    'CHANGELOG.md',
    'Makefile',
    '.gitignore',
    '.gitattributes',
    'Dockerfile',
    'Procfile'
}
```

### Custom Exceptions

Add project-specific exceptions:

```python
from src.governance.naming_exception_manager import NamingExceptionManager

manager = NamingExceptionManager()

# Add custom exception
manager.add_exception("MySpecialFile.txt")

# Check if file is exception
if manager.is_exception("LICENSE"):
    print("This file is allowed")
```

---

## 📊 Reporting

### Generate Violation Report

```bash
# Generate detailed report
cortex naming report --output violations.md

# Report contents:
```

### violations.md
```markdown
# Naming Violations Report

**Generated:** 2025-12-03 14:32:15
**Total Files:** 247
**Violations:** 12 (4.9%)

## By File Type

### Python (.py) - 5 violations
| File | Violation | Suggested |
|------|-----------|-----------|
| src/services/userService.py | camelCase | user_service.py |
| src/models/UserModel.py | PascalCase | user_model.py |
| tests/testUser.py | camelCase | test_user.py |

### Markdown (.md) - 4 violations
| File | Violation | Suggested |
|------|-----------|-----------|
| docs/user_guide.md | snake_case | user-guide.md |
| docs/api_docs.md | snake_case | api-docs.md |

### Config (.yaml) - 3 violations
| File | Violation | Suggested |
|------|-----------|-----------|
| docker_compose.yaml | snake_case | docker-compose.yaml |
| ci_config.yml | snake_case | ci-config.yml |
```

---

## 🛠️ Programmatic API

### Validation

```python
from src.governance.file_naming_validator import FileNameValidator

validator = FileNameValidator()

# Validate file
if validator.validate("user_service.py"):
    print("Valid")
else:
    # Get specific violations
    violations = validator.get_violations("userService.py")
    for v in violations:
        print(f"- {v}")
```

### Enforcement

```python
from src.governance.naming_convention_enforcer import NamingConventionEnforcer

enforcer = NamingConventionEnforcer()

# Check file
if not enforcer.check("userService.py"):
    # Get suggested name
    suggested = enforcer.suggest_name("userService.py")
    print(f"Rename to: {suggested}")

# Batch check
files = ["user_service.py", "userService.py", "user-guide.md"]
results = enforcer.check_batch(files)

for filename, result in results.items():
    print(f"{filename}: {'✅' if result['valid'] else '❌'}")
```

### Auto-Rename

```python
from src.governance.auto_rename_utility import AutoRenameUtility

utility = AutoRenameUtility()

# Check for collisions
if utility.would_collide("userService.py"):
    print("Warning: Target file already exists")

# Rename file
try:
    new_path = utility.rename("userService.py", dry_run=False)
    print(f"Renamed to: {new_path}")
except FileExistsError as e:
    print(f"Error: {e}")
```

---

## 🚨 Troubleshooting

### False Positives

**Problem:** Valid file flagged as invalid

**Solution:**
```bash
# Add to exceptions
cortex naming exception add MyFile.txt

# Or update exception list in code
```

### Bulk Rename Conflicts

**Problem:** Auto-rename fails with collision errors

**Solution:**
```bash
# Run dry-run to preview
cortex naming fix --dry-run

# Manually resolve conflicts
# Then run fix again
cortex naming fix
```

### Pre-Commit Hook Not Working

**Problem:** Hook not blocking invalid commits

**Solution:**
```bash
# Ensure hook is executable
chmod +x .git/hooks/pre-commit

# Verify hook exists
ls -la .git/hooks/pre-commit

# Re-install if missing
cortex naming install-hook
```

---

## 📚 Related Documentation

- **File Naming Validator:** `src/governance/file_naming_validator.py`
- **Naming Convention Enforcer:** `src/governance/naming_convention_enforcer.py`
- **Auto-Rename Utility:** `src/governance/auto_rename_utility.py`
- **Git Hook Validator:** `src/governance/git_hook_validator.py`
- **Report Generator:** `src/governance/naming_report_generator.py`

---

**Version:** 3.7.0  
**Last Updated:** 2025-12-03  
**Author:** Asif Hussain
