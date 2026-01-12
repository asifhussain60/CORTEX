# CORTEX Prompt Integration Guide (v7.0)

**Purpose:** Unified documentation for how all prompts work together  
**Version:** 7.0.0  
**Date:** 2026-01-12  
**Status:** Active

---

## 🎯 Executive Summary

All CORTEX prompts are designed to work as a **cohesive system**:

| Prompt | Role | Invoked When |
|--------|------|--------------|
| `CORTEX.prompt.md` | Gateway/Router | Every user request |
| `cortex-exec.prompt.md` | Autonomous Executor | "execute", "implement", "continue" |
| `cortex-evidence-validator.prompt.md` | Evidence Validator | "validate", "check status", "run tests" |
| `cortex-brittleness-review.prompt.md` | Risk Analyzer | "brittleness", "risk review" |
| `output-standards.md` | Standards Reference | All prompts (internal) |

---

## 🔗 Data Flow (Single Direction)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          CORTEX DATA FLOW                                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   master-plan.yaml     AC-INDEX.yaml    progress-tracker.json            │
│         │                    │                   │                       │
│         │ (phase defs)       │ (AC-IDs)         │ (completion)           │
│         ▼                    ▼                   ▼                       │
│   ┌─────────────────────────────────────────────────────────────┐       │
│   │              sync_plan_viewer_data.py                        │       │
│   └─────────────────────────────────────────────────────────────┘       │
│                              │                                           │
│                              ▼                                           │
│                   plan-viewer-data.json                                  │
│                              │                                           │
│                              ▼                                           │
│                      plan-viewer.html                                    │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

**Rule:** Data flows ONE DIRECTION. Never edit `plan-viewer-data.json` directly.

---

## 📋 Prompt Responsibilities

### CORTEX.prompt.md (Gateway)

**Reads:**
- User intent
- `progress-tracker.json` (current state)
- `AC-INDEX.yaml` (AC definitions)

**Writes:**
- Audit logs (routing decisions)

**Routes To:**
- `cortex-exec.prompt.md` for implementation
- `cortex-evidence-validator.prompt.md` for validation
- `cortex-brittleness-review.prompt.md` for risk analysis

**Regression Check:** YES (pre-routing)

---

### cortex-exec.prompt.md (Executor)

**Reads:**
- `AC-INDEX.yaml` (what to implement)
- `progress-tracker.json` (where we are)
- `master-plan.yaml` (phase sequence)

**Writes:**
- `src/` (implementation code)
- `tests/` (test files)
- `progress-tracker.json` (completion updates)
- Evidence bundles

**Triggers:**
- `sync_plan_viewer_data.py` (after every progress update)

**Regression Check:** YES (pre-implementation, post-implementation)

---

### cortex-evidence-validator.prompt.md (Validator)

**Reads:**
- Test execution results
- `AC-INDEX.yaml` (what should exist)
- `progress-tracker.json` (claimed completion)

**Writes:**
- `progress-tracker.json` (verified counts)
- Validation reports (optional)

**Triggers:**
- `sync_plan_viewer_data.py` (after validation)

**Regression Check:** YES (pre-validation)

---

### cortex-brittleness-review.prompt.md (Analyst)

**Reads:**
- Entire codebase
- `AC-INDEX.yaml` (existing AC-IDs)
- `master-plan.yaml` (phases)

**Writes:**
- `AC-INDEX.yaml` (APPEND new AC-IDs - never separate files)
- `progress-tracker.json` (add planned work)

**Triggers:**
- `sync_plan_viewer_data.py` (after AC-ID addition)

**Regression Check:** YES (pre-analysis, post-append)

---

## 🛡️ Regression Prevention

**All prompts include identical regression checks:**

### Pre-Execution (MANDATORY)

```bash
# Every prompt starts with this
python3 << 'EOF'
import yaml, json, sys
errors = []

try:
    yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'))
except Exception as e:
    errors.append(f"AC-INDEX.yaml: {e}")

try:
    json.load(open('cortex-brain/tier1/tracking/progress-tracker.json'))
except Exception as e:
    errors.append(f"progress-tracker.json: {e}")

try:
    yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml'))
except Exception as e:
    errors.append(f"master-plan.yaml: {e}")

if errors:
    print("❌ REGRESSION DETECTED - HALT")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
EOF
```

### Post-Execution

```bash
# Every prompt ends with sync verification
python3 scripts/sync_plan_viewer_data.py --check-only
```

### On Regression

1. **HALT** - Do not proceed
2. **LOG** - Write to `cortex-brain/audit-logs/regression-alerts.jsonl`
3. **REPORT** - Tell user what broke
4. **WAIT** - User must acknowledge before continuing

---

## 📊 Conflict Resolution

When sources disagree:

| Scenario | Resolution |
|----------|------------|
| AC-INDEX says AC-001 exists, tracker says implemented | Trust AC-INDEX definition, verify tracker with tests |
| master-plan says Phase 2, tracker says Phase 1 | Trust master-plan sequence, update tracker |
| plan-viewer shows 50%, tracker shows 60% | Run sync script, trust tracker |
| Two AC-IDs with same number | Error! Fix in AC-INDEX.yaml first |

**Authority Order:**
1. AC-INDEX.yaml (AC-ID definitions)
2. master-plan.yaml (phase sequence)
3. progress-tracker.json (completion status)
4. plan-viewer-data.json (derived display)

---

## 📁 Output Standards

**All prompts follow `output-standards.md`:**

### AC-IDs
- APPEND to AC-INDEX.yaml only
- Never create separate AC-ID files
- Check for duplicates before creating

### Evidence
- Store in `cortex-brain/tier1/evidence-bundles/AC-{ID}/`
- Include: manifest.yaml, test-results.json, audit-trace.jsonl

### Reports
- Store in `cortex-brain/documents/reports/{category}/`
- Use kebab-case naming (≤32 chars with date exception)

### Progress
- Update `progress-tracker.json` only
- Never edit `plan-viewer-data.json` directly
- Always run sync after updates

---

## 🔄 Architecture Enhancement Protocol

**When any prompt identifies need for new architecture:**

1. **Document** in `cortex-brain/documents/future-enhancements/`
2. **DO NOT** implement in current session
3. **Report** to user: "📋 Enhancement documented for future review"
4. **Continue** with current scope

**Why?** Prevents scope creep and maintains architectural integrity.

---

## ✅ Success Criteria

**Prompts working correctly when:**

1. ✅ All regression checks pass
2. ✅ AC-IDs always in AC-INDEX.yaml (never separate files)
3. ✅ Dashboard always synced after updates
4. ✅ Evidence always test-based
5. ✅ No architectural changes without documentation
6. ✅ All outputs follow naming/location standards

---

## 📚 File References

| Purpose | File |
|---------|------|
| Gateway Prompt | `.github/prompts/CORTEX.prompt.md` |
| Executor Prompt | `.github/prompts/cortex-exec.prompt.md` |
| Validator Prompt | `.github/prompts/cortex-evidence-validator.prompt.md` |
| Analyst Prompt | `.github/prompts/cortex-brittleness-review.prompt.md` |
| Standards | `.github/prompts/output-standards.md` |
| Integration Guide | `.github/prompts/PROMPT-INTEGRATION.md` (this file) |
| AC Registry | `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` |
| Progress | `cortex-brain/tier1/tracking/progress-tracker.json` |
| Master Plan | `cortex-brain/cx6-plan/master-plan.yaml` |

---

**Version History:**
- 7.0.0 (2026-01-12): Initial unified integration guide with regression prevention and cohesion model
