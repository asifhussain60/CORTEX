# 🎨 Glassmorphism Validation Toolkit

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.

---

## 📋 Overview

The Glassmorphism Validation Toolkit enforces **glassmorphism-design-standard.md v4.0.0** compliance across all HTML views. It provides automated validation, remediation, and pre-commit hooks to ensure consistent design standards throughout the master plan execution.

**Key Features:**
- ✅ Validates HTML against design standard (ZERO inline styles, NO Level 3, etc.)
- 🛠️ Automatically fixes common violations
- 🪝 Pre-commit hook prevents non-compliant commits
- 📊 Generates comprehensive validation reports
- 🔄 Repeatable validation for iterative plan execution

---

## 🏗️ Architecture

### Components

| Component | File | Purpose |
|-----------|------|---------|
| **Validator** | `glassmorphism_validator.py` | Validates HTML against design standard |
| **Remediator** | `glassmorphism_remediation.py` | Automatically fixes violations |
| **Pre-Commit Hook** | `glassmorphism_pre_commit_hook.py` | Blocks non-compliant commits |
| **Unified Toolkit** | `glassmorphism_toolkit.py` | Single CLI interface for all tools |

### Enforced Rules (SKULL)

| Rule ID | Rule Name | Severity | Description |
|---------|-----------|----------|-------------|
| `NO_INLINE_STYLES` | No Inline Styles | CRITICAL | ZERO `style=""` attributes allowed |
| `NO_LEVEL_3` | No Level 3 Views | CRITICAL | Navigation stops at Level 2 |
| `HEADER_FOOTER_STANDARD` | Header/Footer Standard | ERROR | Standardized glass header/footer required |
| `T1_ANIMATIONS_ONLY` | T1 Animations Only | ERROR | Only subtle animations on Level 1/2 |
| `PRODUCTION_FILE_NAMING` | Production File Naming | CRITICAL | No `-new.html`, `-v2.html` suffixes |
| `RESPONSIVE_MANDATORY` | Responsive Breakpoints | WARNING | 375px, 768px, 1440px breakpoints required |

---

## 🚀 Quick Start

### 1. Validate All HTML Files

```powershell
# Basic validation
python src/validation/glassmorphism_toolkit.py validate

# With report output
python src/validation/glassmorphism_toolkit.py validate --report-file validation-report.md

# Fail on warnings (CI/CD)
python src/validation/glassmorphism_toolkit.py validate --fail-on-warnings
```

**Output:**
```
🎨 Glassmorphism Design Standard Validator v1.0.0
📁 Scanning: docs

📊 SUMMARY: 150 files scanned
   ✅ Passed: 142
   ❌ Failed: 8

   🔴 CRITICAL: 5
   🟠 ERROR: 12
   🟡 WARNING: 3

❌ VALIDATION FAILED
```

### 2. Automatically Fix Violations

```powershell
# Fix all violations
python src/validation/glassmorphism_toolkit.py remediate --all

# Fix specific issues
python src/validation/glassmorphism_toolkit.py remediate --fix-inline-styles --add-headers

# With custom backup directory
python src/validation/glassmorphism_toolkit.py remediate --all --backup-dir backups/my-backup
```

**Output:**
```
🛠️ Glassmorphism Remediation Engine v1.0.0
📁 Target: docs

📦 Backups will be saved to: backups/glassmorphism_20260101_120000
🔍 Found 150 HTML files

🧹 Removing inline styles...
📝 Adding missing headers...
📝 Adding missing footers...
🎬 Removing T3 animations...

✅ All fixes applied successfully
```

### 3. Install Pre-Commit Hook

```powershell
python src/validation/glassmorphism_toolkit.py install-hook
```

**Output:**
```
🪝 Installing Glassmorphism Pre-Commit Hook

✅ Hook installed: .git/hooks/pre-commit

🎯 Hook will now run before every commit to enforce:
   - NO_INLINE_STYLES
   - NO_LEVEL_3
   - HEADER_FOOTER_STANDARD
   - T1_ANIMATIONS_ONLY
   - PRODUCTION_FILE_NAMING
```

---

## 📖 Detailed Usage

### Validation

**Command:**
```powershell
python src/validation/glassmorphism_validator.py [OPTIONS] [docs_root]
```

**Options:**
- `docs_root` - Path to docs/ directory (default: `docs`)
- `--report-file PATH` - Output report to markdown file
- `--fail-on-warnings` - Exit with error code if warnings present

**Exit Codes:**
- `0` - All checks passed
- `1` - CRITICAL or ERROR issues found
- `2` - Warnings found (with `--fail-on-warnings`)

**Example Report:**

```markdown
# 🎨 Glassmorphism Design Standard Validation Report

## 📊 Summary

- **Total Files Scanned:** 150
- **Passed:** 142 ✅
- **Failed:** 8 ❌
- **Overall Status:** ❌ FAIL

### Issue Counts by Severity

- **CRITICAL:** 5 🔴
- **ERROR:** 12 🟠
- **WARNING:** 3 🟡

### Rule Violation Summary

- **Inline Styles (style=""):** 23
- **Level 3 Navigation:** 0
- **Missing Headers:** 8
- **Missing Footers:** 4
- **T3 Animation Violations:** 2

### View Hierarchy Breakdown

- **Level 0 (Home):** 1 files
- **Level 1 (Hubs):** 13 files (expected: 13)
- **Level 2 (Details):** 136 files (expected: 137)
- **Level 3 (FORBIDDEN):** 0 files ⚠️

## 🔍 Detailed Issues

### 🔴 CRITICAL Issues (5)

#### No Inline Styles (23 occurrences)

- **File:** `docs/security/index.html` (line 45)
  - **Issue:** Inline style attribute found: <div style="margin-top: 2rem;">
  - **Fix:** Extract to CSS class in glassmorphism.css
```

### Remediation

**Command:**
```powershell
python src/validation/glassmorphism_remediation.py [OPTIONS] [docs_root]
```

**Options:**
- `docs_root` - Path to docs/ directory (default: `docs`)
- `--backup-dir PATH` - Custom backup directory
- `--fix-inline-styles` - Remove inline style attributes
- `--add-headers` - Add missing glass headers
- `--add-footers` - Add missing glass footers
- `--remove-t3-animations` - Remove T3 dramatic animations
- `--rename-files` - Rename files with forbidden patterns
- `--all` - Apply all fixes
- `--report-file PATH` - Output report to file

**Backup Strategy:**
- Creates timestamped backup directory: `backups/glassmorphism_YYYYMMDD_HHMMSS/`
- Preserves original file structure
- Files backed up before modification
- Enables easy rollback if needed

**Example Report:**

```markdown
# 🛠️ Glassmorphism Remediation Report

**Backup Location:** backups/glassmorphism_20260101_120000
**Total Actions:** 42
**Successful:** 40
**Failed:** 2

## 📋 Actions Performed

### NO_INLINE_STYLES (23/23 successful)

✅ **index.html**: Removed 3 inline style attributes
   - Before: 3 inline styles
   - After: TODO comments added

✅ **security/index.html**: Removed 5 inline style attributes
   - Before: 5 inline styles
   - After: TODO comments added
```

### Pre-Commit Hook

**Installation:**
```powershell
# Via toolkit (recommended)
python src/validation/glassmorphism_toolkit.py install-hook

# Manual installation
Copy-Item src/validation/glassmorphism_pre_commit_hook.py .git/hooks/pre-commit
```

**Behavior:**
- Runs automatically before every `git commit`
- Validates all HTML files in `docs/`
- **BLOCKS commit** if CRITICAL or ERROR issues found
- **ALLOWS commit** if only warnings present
- Provides fix suggestions in rejection message

**Bypass (NOT RECOMMENDED):**
```powershell
git commit --no-verify
```

---

## 🔄 Repeatable Execution

The toolkit is designed for **repeatable execution** during iterative master plan development:

### Workflow Pattern

```powershell
# Phase 1: Initial validation
python src/validation/glassmorphism_toolkit.py validate --report-file phase1-validation.md

# Phase 2: Fix violations
python src/validation/glassmorphism_toolkit.py remediate --all

# Phase 3: Re-validate
python src/validation/glassmorphism_toolkit.py validate

# Phase 4: Commit (hook validates automatically)
git add .
git commit -m "Phase 1 complete"
```

### Integration with Master Plan

**Phase 0 (Discovery):**
```powershell
# Baseline validation
python src/validation/glassmorphism_toolkit.py validate --report-file phase0-baseline.md
```

**Phase 1-3 (Implementation):**
```powershell
# After each phase
python src/validation/glassmorphism_toolkit.py validate --report-file phase{N}-validation.md

# Fix issues
python src/validation/glassmorphism_toolkit.py remediate --all
```

**Phase 7 (Final Validation):**
```powershell
# Comprehensive final check
python src/validation/glassmorphism_toolkit.py validate --fail-on-warnings --report-file final-validation.md

# Must pass with ZERO issues
```

**Phase 8 (REFACTOR):**
```powershell
# Verify SKULL rule compliance
python src/validation/glassmorphism_toolkit.py validate

# Should show 0 violations
```

---

## 🛡️ SKULL Rule Enforcement

### NO_INLINE_STYLES

**Enforcement:**
- Scans for `style=""` attributes in HTML
- Detects variations (`style = ""`, `STYLE=`, etc.)
- Severity: **CRITICAL** (blocks deployment)

**Remediation:**
- Removes inline styles
- Adds TODO comments for manual CSS class creation
- Preserves original content in backup

**Example:**
```html
<!-- ❌ BEFORE (violation) -->
<div style="margin-top: 2rem; color: #00d4ff;">

<!-- ✅ AFTER (remediation) -->
<div class="mt-lg accent-primary-text">
```

### NO_LEVEL_3

**Enforcement:**
- Detects Level 3 file paths (`docs/domain/category/detail.html`)
- Identifies links pointing to Level 3 views
- Severity: **CRITICAL** (blocks deployment)

**Remediation:**
- Manual consolidation required (cannot be automated)
- Tool flags violations for review
- Suggests tab/accordion patterns for deep content

### HEADER_FOOTER_STANDARD

**Enforcement:**
- Checks for `<header class="glass-header">`
- Checks for `<footer class="glass-footer">`
- Level-aware validation (Level 0: footer only, Level 1/2: both)
- Severity: **ERROR**

**Remediation:**
- Adds standardized header template
- Adds standardized footer template
- Adjusts relative links based on file depth

### T1_ANIMATIONS_ONLY

**Enforcement:**
- Scans for T3 keyframes (`borderGlowSweep`, `blobMorph`, etc.)
- Detects animation property references
- Level 1/2 pages only (Level 0 allows T3)
- Severity: **ERROR**

**Remediation:**
- Removes T3 keyframe definitions
- Comments out animation properties
- Suggests T1 alternatives

---

## 📊 Validation Report Schema

```json
{
  "total_files_scanned": 150,
  "passed_files": 142,
  "failed_files": 8,
  "issues": [
    {
      "severity": "CRITICAL",
      "rule_id": "NO_INLINE_STYLES",
      "rule_name": "No Inline Styles",
      "file_path": "docs/security/index.html",
      "line_number": 45,
      "message": "Inline style attribute found",
      "fix_suggestion": "Extract to CSS class in glassmorphism.css"
    }
  ],
  "inline_style_count": 23,
  "level3_link_count": 0,
  "missing_header_count": 8,
  "missing_footer_count": 4,
  "t3_animation_violations": 2,
  "level0_files": ["docs/index.html"],
  "level1_files": ["docs/security/index.html", ...],
  "level2_files": ["docs/security/threat-modeling.html", ...],
  "level3_files": [],
  "is_valid": false
}
```

---

## 🔧 Toolkit Manager Integration

### Tool Registration

Tools are registered in `cortex-toolkit/tool-inventory.yaml`:

```yaml
- id: glassmorphism-validator
  name: "Glassmorphism Design Standard Validator"
  version: "1.0.0"
  category: validation
  lifecycle: active
  
  enforces_rules:
    - NO_INLINE_STYLES
    - NO_LEVEL_3
    - HEADER_FOOTER_STANDARD
    - T1_ANIMATIONS_ONLY
    - PRODUCTION_FILE_NAMING
    - RESPONSIVE_MANDATORY

- id: glassmorphism-remediation
  name: "Glassmorphism Remediation Engine"
  version: "1.0.0"
  category: validation
  lifecycle: active
  
  depends_on: [glassmorphism-validator]

- id: glassmorphism-pre-commit
  name: "Glassmorphism Pre-Commit Hook"
  version: "1.0.0"
  category: validation
  lifecycle: active
  
  depends_on: [glassmorphism-validator]
```

### Discovery

Tools can be discovered via Toolkit Manager:

```powershell
# List all validation tools
cortex-toolkit list --category validation

# Get tool details
cortex-toolkit info glassmorphism-validator

# Run tool via Toolkit Manager
cortex-toolkit run glassmorphism-validator --report-file report.md
```

---

## 🎯 Best Practices

### 1. Run Validation Early and Often

```powershell
# Before starting work
python src/validation/glassmorphism_toolkit.py validate

# After each phase
python src/validation/glassmorphism_toolkit.py validate --report-file phase{N}-validation.md

# Before commit (automatic with hook)
git commit
```

### 2. Use Backups

```powershell
# Create timestamped backup before remediation
python src/validation/glassmorphism_toolkit.py remediate --all --backup-dir backups/pre-fix-$(Get-Date -Format 'yyyyMMdd_HHmmss')

# Review changes
git diff

# Rollback if needed
git checkout docs/
```

### 3. Incremental Fixes

```powershell
# Fix one rule at a time for easier review
python src/validation/glassmorphism_toolkit.py remediate --fix-inline-styles
git add . && git commit -m "Fix: Remove inline styles"

python src/validation/glassmorphism_toolkit.py remediate --add-headers
git add . && git commit -m "Fix: Add glass headers"
```

### 4. CI/CD Integration

```yaml
# .github/workflows/validate-glassmorphism.yml
name: Glassmorphism Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Run Validation
        run: |
          python src/validation/glassmorphism_toolkit.py validate --fail-on-warnings
```

---

## 📚 Reference

### Related Documentation

- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` v4.0.0
- **Master Plan:** `cortex-brain/documents/planning/active/level-2-glassmorphism-standardization/00-master-plan.md`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`

### Tool Files

- `src/validation/glassmorphism_validator.py` - Core validation engine
- `src/validation/glassmorphism_remediation.py` - Auto-fix engine
- `src/validation/glassmorphism_pre_commit_hook.py` - Git hook
- `src/validation/glassmorphism_toolkit.py` - Unified CLI
- `cortex-toolkit/tool-inventory.yaml` - Tool registration

---

**Version:** 1.0.0  
**Last Updated:** January 1, 2026  
**Maintained By:** Asif Hussain
