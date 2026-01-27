# CORTEX File Naming - Quick Start Guide

## One-Minute Overview

**File naming is now configurable in ONE place:**

```
.cortex/standards/file-naming-config.yaml  ← Change here once
         ↓
cortex/tools/file_naming_factory.py        ← All tools use this
         ↓
All future files follow same standards
```

---

## Standard Naming Patterns

### Documentation Files
```python
from cortex.tools.file_naming_factory import documentation

doc = documentation("guide", "deployment")
# → deployment-guide.md

doc = documentation("reference", "api")
# → api-reference.md

doc = documentation("inventory", "component")
# → component-inventory.md
```

### Configuration Files
```python
from cortex.tools.file_naming_factory import configuration

cfg = configuration("docker")
# → docker-config.yaml

cfg = configuration("prometheus", "production")
# → prometheus-production-config.yaml

cfg = configuration("database", "staging", "yml")
# → database-staging-config.yml
```

### Shell Scripts
```python
from cortex.tools.file_naming_factory import script

sh = script("deploy", "kubernetes")
# → deploy-kubernetes.sh

sh = script("migrate", "docker")
# → migrate-docker.sh

sh = script("validate", "syntax")
# → validate-syntax.sh
```

### Python Modules
```python
from cortex.tools.file_naming_factory import python_module

py = python_module("orchestrator", "migration")
# → migration_orchestrator.py  (snake_case, PEP 8)

py = python_module("validator", "wiring")
# → wiring_validator.py

py = python_module("config", "docker")
# → docker_config.py
```

### Test Files
```python
from cortex.tools.file_naming_factory import test

tst = test("orchestrator", "integration")
# → test_integration_orchestrator.py

tst = test("api", "rest")
# → test_rest_api.py
```

### Plan Files
```python
from cortex.tools.file_naming_factory import plan

pln = plan("migration", "phases")
# → migration-phases-plan.yaml

pln = plan("roadmap", "project")
# → project-roadmap-plan.yaml
```

---

## Naming Rules Summary

| Aspect | Rule | Examples |
|--------|------|----------|
| **Case** | kebab-case (except Python: snake_case) | deployment-guide.md, wiring_validator.py |
| **Length** | 16-32 optimal, 8-55 max | component-inventory-reference.md |
| **Pattern** | {purpose}-{context} | docker-configuration-guide.md |
| **Verbs** | {verb}-{noun} for scripts | deploy-kubernetes.sh |
| **Config** | {service}-config.ext | prometheus-production-config.yaml |
| **Tests** | test_{context}_{noun}.py | test_integration_orchestrator.py |

---

## ❌ Never Do This

```python
# ❌ WRONG - Adjectives
documentation("new", "guide")          # → new-guide.md ❌
documentation("enhanced", "docker")    # → enhanced-docker.md ❌
documentation("executive", "summary")  # → executive-summary.md ❌

# ❌ WRONG - Version numbers
"docker-config-v2.1.yaml"             # Version in filename ❌
"guide-2.0.md"                         # Version in filename ❌
"api-reference-v1.md"                  # Version in filename ❌

# ❌ WRONG - Snake_case (except Python)
"deployment-guide.md" ❌ (WRONG)  vs  deployment_guide.md (OK for Python only)

# ❌ WRONG - Dates
"2026-01-27-deployment-guide.md"       # Date in filename ❌
"deployment-guide-20260127.md"         # Date in filename ❌

# ❌ WRONG - Author names
"asif-docker-config.yaml"              # Author in filename ❌
"hussain-deployment-guide.md"          # Author in filename ❌

# ❌ WRONG - Status
"migration-guide-draft.md"             # Status in filename ❌
"docker-config-final.yaml"             # Status in filename ❌
"wiring-spec-complete.md"              # Status in filename ❌
```

---

## Configuration Change Process

**If you need to change naming standards:**

```bash
# 1. Update configuration
nano .cortex/standards/file-naming-config.yaml

# 2. Update governance docs
nano cortex_brain/tier0/governance/file-naming-standards.md

# 3. Update factory if adding new file type
nano cortex/tools/file_naming_factory.py

# 4. Commit changes
git commit -m "standards: Update file naming [description]"

# 5. Tag for checkpoint
git tag -a "file-naming-standards-update-2026-02-01" \
  -m "Updated naming standards"

# That's it! All future files automatically follow new standards
```

---

## Validation

```python
from cortex.tools.file_naming_factory import validate

# Check if filename is compliant
result = validate("my-file-name.md")

if not result["is_valid"]:
    print("Issues:")
    for issue in result["issues"]:
        print(f"  - {issue}")
    
    print("Suggestions:")
    for suggestion in result["suggestions"]:
        print(f"  - {suggestion}")

# Output example:
# Issues:
#   - Contains prohibited adjective: new
# Suggestions:
#   - Remove 'new' or use more descriptive term
#   - Length 28 outside optimal 16-32
```

---

## Where Standards Live

| What | Where |
|------|-------|
| **Configuration** | `.cortex/standards/file-naming-config.yaml` |
| **Governance** | `cortex_brain/tier0/governance/file-naming-standards.md` |
| **Implementation** | `cortex/tools/file_naming_factory.py` |
| **Deployment Info** | `docs/GLOBAL-FILE-NAMING-STANDARDS-DEPLOYMENT.md` |

---

## Integration Example

Use in your generators:

```python
# cortex/documentation/generator.py
from cortex.tools.file_naming_factory import documentation

def generate_api_docs():
    filename = documentation("reference", "api")
    filepath = f"docs/{filename}"
    
    with open(filepath, "w") as f:
        f.write(generate_content())
    
    return filepath

# Result: docs/api-reference.md (always standards-compliant)
```

---

## Quick Facts

- ✅ **ONE config file** – Change standards in one place
- ✅ **ALL tools affected** – No duplication, no inconsistency
- ✅ **Easy validation** – Built-in error messages and suggestions
- ✅ **PEP 8 compliant** – Python follows snake_case correctly
- ✅ **Future-proof** – Easy to extend for new file types
- ✅ **Fully reversible** – Git rollback anytime
- ✅ **Governance compliant** – CORE-035 (Single Canonical Implementation)

---

## Still Have Questions?

- **How to use factory:** `cortex_brain/tier0/governance/file-naming-standards.md`
- **All configuration options:** `.cortex/standards/file-naming-config.yaml`
- **Technical details:** `cortex/tools/file_naming_factory.py`
- **Full deployment info:** `docs/GLOBAL-FILE-NAMING-STANDARDS-DEPLOYMENT.md`

---

**Key Takeaway:** All future CORTEX files follow consistent standards, configurable in one place.
