# 🎨 Glassmorphism Validation Toolkit - Quick Reference

**Version:** 1.0.0 | **Author:** Asif Hussain

---

## 🚀 Common Commands

### Validate HTML Files
```powershell
# Basic validation
python src/validation/glassmorphism_toolkit.py validate

# With report output
python src/validation/glassmorphism_toolkit.py validate --report-file validation-report.md

# Fail on warnings (CI/CD)
python src/validation/glassmorphism_toolkit.py validate --fail-on-warnings
```

### Fix Violations
```powershell
# Fix all violations
python src/validation/glassmorphism_toolkit.py remediate --all

# Fix specific issues
python src/validation/glassmorphism_toolkit.py remediate --fix-inline-styles
python src/validation/glassmorphism_toolkit.py remediate --add-headers
python src/validation/glassmorphism_toolkit.py remediate --add-footers
python src/validation/glassmorphism_toolkit.py remediate --remove-t3-animations
python src/validation/glassmorphism_toolkit.py remediate --rename-files
```

### Install Pre-Commit Hook
```powershell
python src/validation/glassmorphism_toolkit.py install-hook
```

---

## 🛡️ Enforced Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `NO_INLINE_STYLES` | CRITICAL | ZERO `style=""` attributes |
| `NO_LEVEL_3` | CRITICAL | No Level 3 navigation |
| `HEADER_FOOTER_STANDARD` | ERROR | Glass header/footer required |
| `T1_ANIMATIONS_ONLY` | ERROR | Only subtle animations (Level 1/2) |
| `PRODUCTION_FILE_NAMING` | CRITICAL | No `-new.html`, `-v2.html` |
| `RESPONSIVE_MANDATORY` | WARNING | 375px, 768px, 1440px breakpoints |

---

## 🔄 Master Plan Integration

### Phase 0 (Discovery & CSS Foundation)
```powershell
# Baseline validation
python src/validation/glassmorphism_toolkit.py validate --report-file phase0-baseline.md
```

### Phase 1-3 (Implementation)
```powershell
# After each phase completion
python src/validation/glassmorphism_toolkit.py validate --report-file phase{N}-validation.md

# Fix violations if any
python src/validation/glassmorphism_toolkit.py remediate --all

# Re-validate
python src/validation/glassmorphism_toolkit.py validate
```

### Phase 4 (Inline Styles Cleanup)
```powershell
# Dedicated inline style cleanup
python src/validation/glassmorphism_toolkit.py remediate --fix-inline-styles

# Verify cleanup
python src/validation/glassmorphism_toolkit.py validate
```

### Phase 7 (Final Validation)
```powershell
# Comprehensive final check (must pass with ZERO issues)
python src/validation/glassmorphism_toolkit.py validate --fail-on-warnings --report-file final-validation.md
```

### Phase 8 (REFACTOR)
```powershell
# Verify SKULL rule compliance
python src/validation/glassmorphism_toolkit.py validate

# Expected output: 0 violations
```

---

## 📊 Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Success | All checks passed |
| `1` | Failure | CRITICAL or ERROR issues found |
| `2` | Warnings | Warnings found (with `--fail-on-warnings`) |

---

## 🛠️ Remediation Actions

| Flag | Action | Destructive | Backup |
|------|--------|-------------|--------|
| `--fix-inline-styles` | Remove `style=""` attributes | Yes | ✅ |
| `--add-headers` | Add glass headers | Yes | ✅ |
| `--add-footers` | Add glass footers | Yes | ✅ |
| `--remove-t3-animations` | Remove T3 keyframes | Yes | ✅ |
| `--rename-files` | Rename to production names | Yes | ✅ |
| `--all` | Apply all fixes | Yes | ✅ |

**Backup Location:** `backups/glassmorphism_YYYYMMDD_HHMMSS/`

---

## 🪝 Pre-Commit Hook

**Installation:**
```powershell
python src/validation/glassmorphism_toolkit.py install-hook
```

**Behavior:**
- ✅ Runs automatically before every commit
- ❌ Blocks commits with CRITICAL/ERROR issues
- ⚠️ Allows commits with warnings
- 💡 Provides fix suggestions

**Bypass (not recommended):**
```powershell
git commit --no-verify
```

---

## 📖 Full Documentation

See: `cortex-brain/documents/standards/glassmorphism-validation-toolkit.md`

---

**Quick Help:**
```powershell
python src/validation/glassmorphism_toolkit.py --help
```
