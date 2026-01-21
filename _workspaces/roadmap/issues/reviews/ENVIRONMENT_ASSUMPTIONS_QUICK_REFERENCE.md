# CORTEX Environment Assumptions - Quick Reference Checklist

## Status Overview

- ✅ = Good/Implemented
- ⚠️ = Needs Attention  
- ❌ = Issue Found

---

## Platform Compatibility

| Assumption | Status | Notes |
|-----------|--------|-------|
| Windows path handling | ✅ | Using pathlib.Path - cross-platform safe |
| Line ending conventions | ⚠️ | Git history parsing - consider binary mode |
| Shell/Git availability | ❌ | REQUIRED but not documented |
| Platform detection | ✅ | Properly checks sys.platform |
| Temp directory access | ✅ | Using standard tempfile module |
| Database directory | ✅ | Auto-created with mkdir(parents=True) |

---

## Python Version Requirements

| Feature | Status | Requirement | Notes |
|---------|--------|-------------|-------|
| Type hints (Optional/Union) | ✅ | Python 3.7+ | Good minimum version |
| Walrus operator | ✅ | Not used | Maintains 3.7+ compat |
| Match statements | ✅ | Not used | Maintains 3.7+ compat |
| Timezone-aware datetime | ❌ | Partially implemented | Scripts use naive datetime |
| SQLite support | ✅ | Python stdlib | Always available |
| F-strings | ✅ | Python 3.6+ | Standard approach |

---

## External Service Dependencies

| Service | Status | Location | Details |
|---------|--------|----------|---------|
| SQLite Database | ✅ | cortex_brain/state/governance.db | Local, auto-created |
| Git Command | ❌ | System PATH | REQUIRED, not documented |
| MCP Server | ✅ | localhost:8000 | Documented in config |
| GitHub API | ✅ | CI/CD workflows | Expected for GitHub projects |
| Prometheus | ✅ | deployment/ | Optional monitoring |

---

## File System Requirements

| Requirement | Status | Details |
|------------|--------|---------|
| Write access to database dir | ✅ | Auto-created if missing |
| Temp directory access | ✅ | Handled by tempfile module |
| Parent dir creation | ✅ | mkdir(parents=True, exist_ok=True) |
| Permission checks | ⚠️ | No explicit pre-flight validation |

---

## Environment Variables

| Variable | Status | Purpose | Default |
|----------|--------|---------|---------|
| CORTEX_ROOT | ⚠️ | Project root override | Git root or cwd |
| Database path | ✅ | DB location override | cortex_brain/state/governance.db |
| MCP endpoint | ✅ | MCP server location | http://127.0.0.1:8000 |

---

## Timezone & Locale

| Issue | Status | Severity | Details |
|-------|--------|----------|---------|
| Naive datetime in scripts | ❌ | HIGH | regenerate_audit_log.py & ac_fix_db_persist_001.py |
| String encoding | ✅ | LOW | UTF-8 assumed (standard for Python 3) |

---

## Priority Action Items

### 🔴 IMMEDIATE (Do First)

```
1. Create SYSTEM_REQUIREMENTS.md
   - Document git requirement
   - List Python version requirement
   - Note platform compatibility

2. Update scripts/regenerate_audit_log.py line 134
   - Replace: datetime.now().isoformat()
   - With: datetime.now(timezone.utc).isoformat()

3. Update scripts/ac_fix_db_persist_001.py lines 125, 296
   - Replace: datetime.now()
   - With: datetime.now(timezone.utc)

4. Update README.md
   - Add "System Requirements" section
   - Link to SYSTEM_REQUIREMENTS.md
   - Mention CORTEX_ROOT variable
```

### 🟡 SHORT TERM (Next 1-2 weeks)

```
1. Create INSTALLATION_GUIDE.md
2. Add pre-flight checks for git availability
3. Add CI/CD matrix testing (3 OS × 4 Python versions)
4. Create environment variable documentation
```

### 🟢 LONG TERM (Next 1-2 months)

```
1. Standardize all datetime to UTC
2. Consider GitPython library alternative
3. Add environment validation on startup
4. Security audit: review database permissions
```

---

## Files Created by This Analysis

1. **ENVIRONMENT_ASSUMPTIONS_ANALYSIS.yaml** (769 lines)
   - Structured YAML report with all findings
   - Includes file paths, line numbers, impact analysis
   - Organized by category

2. **ENVIRONMENT_ASSUMPTIONS_SUMMARY.md** (550+ lines)
   - Executive summary and detailed analysis
   - Actionable recommendations
   - Code examples for fixes
   - Compliance notes

3. **ENVIRONMENT_ASSUMPTIONS_QUICK_REFERENCE.md** (this file)
   - Quick checklist format
   - Status overview
   - Priority action items

---

## Known Good Patterns in CORTEX

Copy these patterns when making changes:

### ✅ Database Connection (Correct Pattern)
```python
from cortex.infrastructure.database import DatabaseManager

db = DatabaseManager()
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    # Auto-commits on success, rolls back on error
```

### ✅ Path Resolution (Correct Pattern)
```python
from cortex.brain.core.path_resolver import resolve_path
from pathlib import Path

db_path = resolve_path("cortex_brain", "state", "governance.db")
db_path.parent.mkdir(parents=True, exist_ok=True)
```

### ✅ Timezone-Aware Datetime (Correct Pattern)
```python
from datetime import datetime, timezone

# Always use timezone-aware UTC
now_utc = datetime.now(timezone.utc)
timestamp = now_utc.isoformat()  # 2026-01-21T23:30:00+00:00
```

### ✅ Configuration with Defaults (Correct Pattern)
```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Config:
    db_path: Path = field(default_factory=lambda: resolve_path("cortex_brain", "state"))
    timeout: float = 30.0
    
    def __post_init__(self):
        self.db_path = Path(self.db_path)
```

---

## Verification Checklist

- [ ] SYSTEM_REQUIREMENTS.md created and linked from README
- [ ] scripts/regenerate_audit_log.py updated with UTC datetime
- [ ] scripts/ac_fix_db_persist_001.py updated with UTC datetime
- [ ] README.md includes System Requirements section
- [ ] CORTEX_ROOT environment variable documented
- [ ] Git requirement documented
- [ ] Pre-flight checks added for critical dependencies
- [ ] CI/CD matrix testing configured
- [ ] All datetime operations use timezone.utc
- [ ] Database permissions reviewed (should be 0600)

---

## Test Commands

```bash
# Verify git is installed
git --version

# Verify Python version
python --version

# Run environment assumption tests
pytest tests/unit/test_environment_*.py -v

# Verify database initialization
python -c "from cortex.infrastructure.database import DatabaseManager; db = DatabaseManager(); db.initialize()"

# Check for timezone-naive datetime usage
grep -r "datetime\.now()" --include="*.py" | grep -v "timezone.utc"
```

---

## References

- **Main Analysis:** ENVIRONMENT_ASSUMPTIONS_ANALYSIS.yaml (769 lines)
- **Summary:** ENVIRONMENT_ASSUMPTIONS_SUMMARY.md (550+ lines)
- **Code References:**
  - cortex/infrastructure/database.py - Database management
  - cortex/brain/core/path_resolver.py - Path resolution logic
  - scripts/regenerate_audit_log.py - Audit logging (needs timezone fix)
  - scripts/ac_fix_db_persist_001.py - Database repair (needs timezone fix)

---

**Analysis Date:** January 21, 2026  
**Confidence Level:** High (based on grep of 1000+ Python files)  
**Last Updated:** As of timestamp above

