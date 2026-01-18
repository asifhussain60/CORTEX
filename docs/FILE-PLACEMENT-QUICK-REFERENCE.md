# CORTEX File Placement Quick Reference

**USE THIS FOR INSTANT GUIDANCE ON WHERE TO CREATE FILES**

---

## The Golden Rule

| What You're Creating | Where It Goes | Exception |
|---------------------|---------------|-----------|
| **Source Code (.py)** | `src/` | If utility/script: `scripts/` |
| **Test Code (.py)** | `tests/unit/` or `tests/integration/` | Never in root |
| **Documentation (.md)** | `docs/` | Never outside docs/ |
| **YAML Reports** | `_workspaces/roadmap/reports/` | Phase issues: `_workspaces/roadmap/issues/` |
| **Tier Modules** | `cortex-brain/tierX/` | Governance code only |
| **Toolkit Scripts** | `scripts/` | One-off utilities |

---

## File Type → Location (One-Liner)

```
.py source        → src/
.py tests         → tests/unit/ or tests/integration/
.py utilities     → scripts/
.py tier-0 rules  → cortex-brain/tier0/
.py tier-1+       → cortex-brain/tierX/
.md docs          → docs/
.yaml reports     → _workspaces/roadmap/reports/
.yaml findings    → _workspaces/roadmap/issues/
```

---

## Common Mistakes (DON'T DO)

| ❌ Mistake | ✅ Correct |
|-----------|----------|
| `./analysis.py` | `scripts/analysis.py` or `src/analysis.py` |
| `./report.md` | `docs/report.md` |
| `./.github/temp_script.py` | `scripts/temp_script.py` |
| `_workspaces/findings.md` | `docs/findings.md` |
| `./test_run.py` left behind | Move to `scripts/` or delete |

---

## Before-You-Create Checklist

```
□ What am I creating? (source, test, doc, report, utility)
□ Which location applies to this type?
□ Is this permanent or temporary?
   - Permanent: Put in proper home (src/, docs/, etc.)
   - Temporary: Delete after use OR move to scripts/
□ Should this be YAML instead of MD? (for reports/findings)
```

---

## Before-You-Commit Checklist

```bash
# Run this before git commit:
find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.md" \) | grep -v launch-dashboard

# Expected output: (empty or only launch-dashboard.py)
# If anything else: MOVE IT TO PROPER HOME or DELETE IT
```

---

## Directory Map

```
CORTEX/
├── src/                          ← Source code (.py)
├── tests/                        ← Test suites (.py)
│   ├── unit/
│   └── integration/
├── scripts/                      ← Utility scripts (.py)
├── docs/                         ← ALL documentation (.md)
├── cortex-brain/
│   ├── tier0/
│   │   └── governance/          ← Governance rules & config
│   ├── tier1/                   ← Core modules
│   ├── tier2/                   ← Advanced modules
│   └── tier3/                   ← Integration modules
├── _workspaces/roadmap/
│   ├── phases/                  ← Phase YAML
│   ├── reports/                 ← Status reports (YAML)
│   ├── issues/                  ← Investigation findings (YAML)
│   └── tools/                   ← Phase-specific tools
├── launch-dashboard.py          ← ✅ ALLOWED (whitelisted)
├── pytest.ini                   ← ✅ ALLOWED (config)
├── requirements.txt             ← ✅ ALLOWED (config)
└── verify_orchestrator_readiness.sh  ← ✅ ALLOWED (whitelisted)
```

---

## Examples by Scenario

### Scenario: Creating a New Analysis Utility

```
❌ Create ./analyze_impact.py
✅ Create scripts/analyze_impact.py

Later, if permanent:
→ mv scripts/analyze_impact.py src/tools/analyze_impact.py
```

### Scenario: Writing Implementation Guide

```
❌ Create ./AC-FIX-001-guide.md
✅ Create docs/AC-FIX-001-guide.md
```

### Scenario: Generating Investigation Findings

```
❌ Create ./findings.md
✅ Create _workspaces/roadmap/issues/FINDINGS-BRITTLENESS-20260118.yaml
   (Terminal output for readability)
```

### Scenario: Temporary Test Script

```
Option 1 (Temporary, delete after):
→ Create scripts/test_implementation.py
→ Run and verify
→ Delete: rm scripts/test_implementation.py

Option 2 (Keep for future):
→ Create tests/integration/test_implementation.py
→ Add to git repository
```

---

## Rules Summary

1. **MD files** → ALWAYS `docs/` folder
2. **PY files** → `src/`, `tests/`, `scripts/`, or `cortex-brain/tierX/` (NEVER root)
3. **YAML reports** → `_workspaces/roadmap/reports/`
4. **YAML findings** → `_workspaces/roadmap/issues/`
5. **Root clean** → Only launch-dashboard.py + config files
6. **Before commit** → Check for stray files in root

---

## Red Flags 🚩

If you see these, STOP and fix:
- `.py` file in root (except launch-dashboard.py)
- `.md` file outside `docs/`
- Temporary script not cleaned up
- Report files in root

**Fix:** Move to permanent home or delete

---

**Version:** 1.0  
**Last Updated:** 2026-01-18  
**Status:** ACTIVE - Use this for all file creation decisions
