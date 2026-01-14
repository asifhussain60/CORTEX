# CORTEX Architecture Enforcement - Quick Reference

**Version:** 5.0.0 | **Status:** ✅ ACTIVE | **Compliance Required:** ≥95%

---

## 🎯 Purpose

This guide explains how CORTEX enforces architecture compliance through automated audits at multiple checkpoints.

---

## 🛡️ Enforcement Layers

### Layer 1: Pre-Commit Hook (Local)

**Status:** ✅ INSTALLED  
**Location:** `.git/hooks/pre-commit`  
**Trigger:** Every `git commit` command

**What It Does:**
- Runs architecture audit before commit is created
- Blocks commit if score <95%
- Provides instant feedback on violations

**Bypass (Emergency Only):**
```bash
git commit --no-verify -m "emergency fix"
```

⚠️ **WARNING:** Only use `--no-verify` for P0 production incidents. All bypassed commits MUST be fixed in next commit.

---

### Layer 2: CI/CD Pipeline (Remote)

**Status:** ✅ CONFIGURED  
**Location:** `.github/workflows/architecture-audit.yml`  
**Trigger:** Push to main/CORTEX-5.0/develop branches, all PRs

**What It Does:**
- Runs architecture audit on GitHub Actions
- Blocks PR merge if audit fails
- Uploads audit reports as artifacts
- Comments on PR with results

**Viewing Results:**
1. Go to GitHub Actions tab
2. Click on workflow run
3. Download "architecture-audit-report" artifact

---

### Layer 3: Manual Audit (On-Demand)

**Status:** ✅ AVAILABLE  
**Location:** `scripts/audit_master_orchestrator_architecture.py`  
**Trigger:** Manual execution

**Run Audit:**
```bash
python3 scripts/audit_master_orchestrator_architecture.py
```

**Output:**
- Console summary (pass/fail, score, grade)
- JSON report: `cortex-brain/documents/reports/master-orchestrator-architecture-audit-YYYY-MM-DD.json`
- Exit code: 0 (pass), 1 (fail)

---

## 📊 Audit Checks (8 Total)

| Check # | Requirement | Weight | Critical? |
|---------|-------------|--------|-----------|
| 1 | Master orchestrator is Python-based | 12.5% | ✅ YES |
| 2 | Work defined in YAML (no textual ambiguity) | 12.5% | ✅ YES |
| 3 | No text-based handoffs | 12.5% | ✅ YES |
| 4 | Epic/Feature/Phase plans use scripts | 12.5% | ✅ YES |
| 5 | Structured state management (SQLite) | 12.5% | ⚠️ High |
| 6 | YAML-based routing | 12.5% | ⚠️ High |
| 7 | YAML-defined priority | 12.5% | ⚠️ High |
| 8 | Handoff mechanism verification | 12.5% | ✅ YES |

**Passing Grade:** ≥95% (7.5/8 checks must pass)

---

## 🚨 What Happens When Audit Fails

### Local (Pre-Commit Hook)

```
❌ ARCHITECTURE AUDIT FAILED

The architecture audit detected issues that violate the CORTEX
Architecture Contract v5.0. Your commit has been blocked.

📋 Review the audit report:
   cortex-brain/documents/reports/master-orchestrator-architecture-audit-2026-01-05.json

🔧 Fix the issues and try again.
```

**Action:**
1. Review audit report
2. Fix violations (see Architecture Contract)
3. Re-run `git commit`

---

### CI/CD (GitHub Actions)

**PR Comment:**
```
## 🔍 CORTEX Architecture Audit Results

### ❌ AUDIT FAILED

This PR violates the CORTEX Architecture Contract v5.0.

**Action Required:** Fix architecture issues before merging.

📋 Review the audit report in the workflow artifacts.
```

**Action:**
1. Download audit report from workflow artifacts
2. Fix violations in new commits
3. Push fixes to PR branch
4. Wait for re-check

---

## 🔧 Common Fixes

### Fix 1: Text-Based Handoff Language

**Violation:** Using "hand-off complete", "autonomous execution"

**Fix:**
```markdown
❌ BEFORE:
⚠️ **HAND-OFF COMPLETE** - Python orchestrator executing...

✅ AFTER:
✅ **INVOKING PYTHON VIA TERMINAL** - `python3 -m src.main "{request}"`
```

**Files to Check:**
- `.github/copilot-instructions.md`
- `.github/prompts/*.prompt.md`

---

### Fix 2: Missing YAML Configuration

**Violation:** Hardcoded routing or priority in Python code

**Fix:**
```yaml
# cortex-brain/config/master-orchestrator.yaml
routing_rules:
  - pattern: "^(new pattern)"
    orchestrator: "new_orchestrator"
    priority: 25
    mode: "autonomous"
```

---

### Fix 3: State in Text Files

**Violation:** Storing critical state in JSON/text files

**Fix:**
```python
# Use SQLite instead
from src.database.planning_state_db import PlanningStateDB

db = PlanningStateDB()
db.save_phase_result(phase_result)  # Not JSON file
```

---

## 📚 Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Architecture Contract** | Mandatory principles | `cortex-brain/documents/architecture/CORTEX-ARCHITECTURE-CONTRACT.md` |
| **Audit Script** | Validation tool | `scripts/audit_master_orchestrator_architecture.py` |
| **Pre-Commit Hook** | Local enforcement | `.git/hooks/pre-commit` |
| **CI/CD Workflow** | Remote enforcement | `.github/workflows/architecture-audit.yml` |
| **Latest Audit Report** | Current compliance | `cortex-brain/documents/reports/master-orchestrator-architecture-audit-*.json` |

---

## 🔄 Maintenance

### Monthly Tasks

- [ ] Review audit reports for trends
- [ ] Update banned terminology list if needed
- [ ] Check for new anti-patterns

### Quarterly Tasks

- [ ] Review Architecture Contract (scheduled)
- [ ] Update audit checks if architecture evolves
- [ ] Analyze bypass frequency (should be <1%)

---

## ❓ FAQ

**Q: Can I disable the pre-commit hook?**  
A: Yes, but NOT recommended. Use `git commit --no-verify` only for emergencies.

**Q: What if the CI/CD audit fails but local passed?**  
A: Pull latest changes from main branch. Audit script may have been updated.

**Q: How do I see historical audit scores?**  
A: All audit reports are saved with timestamps in `cortex-brain/documents/reports/`

**Q: Who can approve architecture violations?**  
A: Only the Architecture Owner (Asif Hussain) can approve exceptions.

**Q: What's the current compliance score?**  
A: Run `python3 scripts/audit_master_orchestrator_architecture.py` to see latest score.

---

## 🆘 Emergency Bypass Procedure

**ONLY use for P0 production incidents:**

1. **Bypass Pre-Commit:**
   ```bash
   git commit --no-verify -m "P0: emergency fix for production incident"
   ```

2. **Document Exception:**
   - Create issue: "Architecture Exception: [incident]"
   - Link commit SHA
   - Describe why bypass was necessary

3. **Remediate ASAP:**
   - Fix architecture violation within 24 hours
   - Create follow-up commit with proper compliance
   - Close exception issue with fix commit SHA

**Bypass Audit Trail:**
- All `--no-verify` commits are tracked via git log
- Monthly report of bypasses sent to architecture owner
- >3 bypasses/month triggers mandatory review

---

## ✅ Success Metrics

**Current Status:**
- Score: 96.88% (EXCELLENT)
- Grade: COMPLIANT
- Last Audit: 2026-01-05

**Target:**
- Maintain ≥95% compliance
- Zero architecture violations in production
- <1% bypass rate monthly

---

**Questions?** See Architecture Contract or contact: asif@cortex.dev
