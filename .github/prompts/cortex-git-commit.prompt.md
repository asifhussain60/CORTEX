# CORTEX Git Commit Protocol
**Version:** 4.0 | **Updated:** 2026-01-24 | **Authority:** CORE-026, CORE-027 | **Status:** ✅ PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Git
**Author:** Asif Hussain | **Phase:** Git Operations | **Orchestrator:** GitOrchestrator ✅

---
```

---

## 🎯 Purpose

**CORTEX Git Protocol** ensures clean, auditable commits with:

1. **Pre-commit validation** (SSOT, file placement)
2. **Checkpoint creation** (CORE-026)
3. **Audit trail logging** (CORE-027)
4. **Machine-specific commits** (multi-machine development)
5. **Merge conflict resolution**

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### Before EVERY Git Operation:

**Step 1: Intent Classification**
```markdown
### 📋 Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `DEPLOY` (Git operations) |
| **Handler** | `GitOrchestrator` |
| **Confidence** | 🟢 High (95%) |
| **Scope** | `SYSTEM` |
| **Impact** | 🟡 Medium |
| **Operation** | `{commit|checkpoint|push|merge}` |
| **Rules** | CORE-026, CORE-027 |

---
**⏳ Awaiting approval to proceed...**
```

---

## 🚀 Quick Commands

| Command | Action |
|---------|--------|
| `/git-checkpoint` | Create checkpoint before major change |
| `/git-commit {msg}` | Commit with validation |
| `/git-status` | Show git status with SSOT validation |
| `/git-push` | Push with pre-push checks |
| `/git-merge {branch}` | Merge with conflict resolution |

---

## 🚫 File Placement Policy (Pre-Commit)

### Forbidden Patterns (BLOCK COMMIT)
| Pattern | Why | Action |
|---------|-----|--------|
| `.md` outside `docs/` | SSOT conflict | DELETE |
| `docs_md/` folder | Structure violation | DELETE |
| `.py` in root | Pollution | DELETE |
| Multiple cortex-*.yaml | Truth conflict | DELETE |
| Hardcoded paths | Machine-specific | FIX |

### Pre-Commit Validation
```bash
# Run before every commit
pre_commit_checks:
  1. No .md files outside docs/
  2. No docs_md/ folder
  3. No .py files in root
  4. No hardcoded paths (/Users/, /home/, C:\)
  5. No multiple cortex-*.yaml files
```

---

## 📋 Commit Message Format

### Standard Commit
```
{type}: {AC-ID} {description}

Types: impl, test, fix, refactor, docs, chore
Example: impl: AC-IMPL-001 - CircuitBreaker with retry logic
```

### Machine-Specific Commit
```
{machine}: {phase-id}: {description}

Example: mac: transform-001: Wired 6 core orchestrators
Example: win: impl-validation: E2E tests passing
```

### Checkpoint Commit
```
checkpoint: before {AC-ID}

Example: checkpoint: before AC-IMPL-005
```

---

## 🔄 Git Workflows

### Checkpoint Before Major Change (CORE-026)
```bash
git add .
git commit -m "checkpoint: before {AC-ID}"
```

### Standard Implementation Commit
```bash
# After TDD cycle complete
git add .
git commit -m "impl: {AC-ID} - {description}"
```

### Merge Protocol
```yaml
conflict_resolution:
  yaml_files:
    - Preserve ALL acceptance criteria
    - Later timestamps win
    - Merge notes fields
  
  python_files:
    - Preserve ALL functions
    - Keep version with more tests
    - Run tests after merge
  
  sqlite_files:
    - DO NOT MERGE
    - Regenerate from YAML
```

---

## 📊 Audit Trail Integration

### Log Git Operations (CORE-027)
```python
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()

# Before commit
logger.log_operation_start(
    ac_id="AC-GIT-001",
    operation="GIT_COMMIT",
    details={"message": commit_msg}
)

# After commit
logger.log_operation_complete(
    ac_id="AC-GIT-001",
    operation="GIT_COMMIT",
    success=True,
    details={"commit_hash": hash}
)
```

---

## ✅ Pre-Commit Checklist

- [ ] No `.md` files outside `docs/`?
- [ ] No `docs_md/` folder?
- [ ] No `.py` files in root?
- [ ] No hardcoded paths?
- [ ] Commit message follows format?
- [ ] Checkpoint exists for major changes?
- [ ] Audit trail logged?
