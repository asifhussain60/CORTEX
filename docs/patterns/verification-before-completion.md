# Verification-Before-Completion Pattern

**Pattern Type:** Quality Assurance  
**Domain:** All Implementations  
**Status:** ✅ Governance Rule (enforced)  
**Source:** chat01.md DIGEST (2026-02-05)  
**Related:** ENH-016, ENH-022

---

## Problem

Success is reported prematurely before verifying the implementation actually works, leading to:
- ❌ False "production-ready" declarations
- ❌ Issues discovered by user, not system
- ❌ Lost confidence in CORTEX outputs

**Anti-Pattern Detected:**
```
Implementation complete → Report success ✅
                              ↓
                         [No verification]
                              ↓
                         User discovers issues ❌
```

---

## Solution

**Mandatory Cycle:** Detect → Fix → **Verify** → Report

### Implementation Steps

1. **Complete the implementation**
2. **Run verification checks** (automated where possible)
3. **Parse verification results** (programmatic, not manual)
4. **Report success ONLY if verification passes**
5. **Include verification evidence** in completion message

---

## Verification Types

### Code Verification

```python
# Automated verification script
import json
from pathlib import Path

def verify_dashboard(dashboard_path):
    """Verify dashboard has required components."""
    
    if not Path(dashboard_path).exists():
        return {"status": "FAIL", "reason": "File not found"}
    
    with open(dashboard_path, 'r') as f:
        content = f.read()
    
    checks = {}
    
    # Check 1: Embedded data exists
    checks['embedded_data'] = '"dashboard-data"' in content
    
    # Check 2: Data is valid JSON
    if checks['embedded_data']:
        try:
            start = content.find('id="dashboard-data">') + 20
            end = content.find('</script>', start)
            data = json.loads(content[start:end])
            checks['valid_json'] = True
            checks['has_metrics'] = 'metrics' in data
        except:
            checks['valid_json'] = False
    
    # Check 3: Tab navigation present
    checks['has_tabs'] = 'tab-button' in content
    
    # Check 4: No external dependencies
    checks['no_external_deps'] = 'src="../../assets' not in content
    
    all_passed = all(checks.values())
    
    return {
        "status": "PASS" if all_passed else "FAIL",
        "checks": checks
    }

# Run verification
result = verify_dashboard('company/dashboards/repos/ksessions/index.html')

if result['status'] == 'PASS':
    print("✅ Verification passed - ready to report success")
else:
    print(f"❌ Verification failed: {result['checks']}")
```

### Test Verification

```bash
# Verify tests pass before reporting
pytest tests/unit/orchestrators/test_new_feature.py --tb=short

if [ $? -eq 0 ]; then
    echo "✅ Tests passing - ready to report"
else
    echo "❌ Tests failing - fix before reporting"
    exit 1
fi
```

### Integration Verification

```bash
# Verify system integration
curl -s http://localhost:8000/health | jq -e '.status == "healthy"'

if [ $? -eq 0 ]; then
    echo "✅ System healthy - ready to report"
else
    echo "❌ System unhealthy - investigate"
    exit 1
fi
```

---

## Completion Message Format

### ✅ Good (Evidence-Based)

```markdown
## 🚀 Implementation Complete

**Verification Status:** PASS ✅

### Automated Checks
| Check | Status | Evidence |
|-------|--------|----------|
| Embedded Data | ✅ | dashboard-data script tag found |
| Valid JSON | ✅ | Parsed successfully |
| Tab Navigation | ✅ | 4 tab-button elements found |
| No External Deps | ✅ | 0 external script references |
| Tests Passing | ✅ | 15/15 tests pass |

**Evidence:** Verification script output saved to `_workspaces/verification-output.txt`

**Files Modified:**
- company/dashboards/repos/ksessions/index.html

**Next Steps:** Dashboard ready for production use.
```

### ❌ Bad (No Verification)

```markdown
## 🚀 Implementation Complete

✅ Dashboard created successfully!

**Files Modified:**
- company/dashboards/repos/ksessions/index.html

[No verification performed - user discovers issues later ❌]
```

---

## Decision Tree

```
Implementation finished?
      ↓
  YES → Run verification checks
      ↓
  Checks passed?
      ├─ YES → Report success ✅ (with evidence)
      └─ NO → Fix issues → Re-verify → Report
```

---

## CORTEX Integration

### AUDIT Mode

```markdown
### ✅ COMPLETION (Autonomous)

**Cycle:** Detect → Fix → Verify → Report

- [x] Issues detected (P0: 2, P1: 5, P2: 12)
- [x] Fixes applied (auto-fix enabled)
- [x] Verification run (all checks passed)
- [x] Report generated

**Status:** 100% Production-Ready ✅
```

### DESIGN Mode

```markdown
### ✅ COMPLETION (Post-Approval)

**Cycle:** Implement → Test → Verify → Report

- [x] Implementation complete (3 files modified)
- [x] Tests passing (23/23 tests pass)
- [x] Verification passed (automated checks)
- [x] Architecture validated (wiring coherent)

**Status:** Ready for Merge ✅
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Fix |
|--------------|---------|-----|
| **Manual verification only** | Human error, inconsistent | Automate checks |
| **Assume success** | No evidence | Always verify programmatically |
| **Partial verification** | Some checks skipped | Run full suite |
| **Verification after report** | User sees premature success | Verify BEFORE reporting |

---

## Enforcement

### Prompt-Level (cortex-architect.prompt.md)

```markdown
## ✅ COMPLETION

**CRITICAL:** Success reported ONLY when ALL issues resolved.

**AUDIT COMPLETION:**
- ✅ 100% Production-Ready: Report success only when P0=0, P1=0, P2=0, P3 auto-fixed
- ❌ Issues Remaining: Auto-fix all detected issues BEFORE reporting
- 🔄 Autonomous Cycle: Detect → Fix → Verify → Report
```

### Agent-Level (cortex-auditor.md)

```markdown
## Output Rules

- ✅ Autonomous fixing before reporting (detect → fix → verify cycle)
- ❌ No premature success declaration (wait until all issues resolved)
```

---

## Examples from Chat01

### ❌ Early Attempt (No Verification)

```
User: Fix KSESSIONS dashboard
Assistant: ✅ Dashboard fixed!
[User checks manually - tabs invisible ❌]
```

### ✅ Final Success (With Verification)

```
User: Fix KSESSIONS dashboard
Assistant: [Implementation]
         [Verification script runs]
         [Checks: embedded data ✅, tabs ✅, CSS ✅]
         ✅ Verification passed - Dashboard ready!
[User checks - everything works ✅]
```

---

## Related Patterns

- [Implementation Truth (CORE-030)](../../.github/copilot-instructions.md#core-rules) — Evidence-based reporting
- [Autonomous Execution](../anti-patterns/premature-success-declaration.md) — Fix before reporting
- [TDD Cycle](../patterns/tdd-red-green-refactor.md) — Test verification

---

## Metrics

From chat01.md analysis:
- **Without verification:** 2 correction cycles, 40% time wasted
- **With verification:** 0 correction cycles, success on first try

**ROI:** 40% time savings + 100% confidence in completion

---

**Last Updated:** 2026-02-05  
**Chat Session:** chat01.md  
**Governance:** Enforced in AUDIT and DESIGN modes
