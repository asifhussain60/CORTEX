# CORTEX 6.0 Acceptance Criteria - Canonical Location

**Status:** ✅ AUTHORITATIVE  
**Last Updated:** 2026-01-09  
**Version:** 12.0.0

---

## 📁 File Structure

```
cortex-brain/documents/planning/active/cortex6/acceptance-criteria/
├── cortex-ac.yaml   # Source of Truth (382 AC)
├── remediation-plan.yaml                             # Active remediation
├── snowball-strategy.yaml                            # Prioritization framework
├── plan-viewer-dashboard-requirements.yaml           # Plan Viewer Dashboard specs
├── README.md                                         # This file
└── archive/                                          # Historical artifacts
    ├── remediation-plan-{YYYY-MM-DD}.yaml           # Archived remediations
    └── search-findings-{YYYYMMDD}.yaml              # Archived findings
```

---

## 🎯 Single Source of Truth

**ALL acceptance criteria for CORTEX 6.0 are in:**
```
cortex-ac.yaml
```

This consolidates:
- ✅ All feature requirements (feat01-feat09)
- ✅ Governance framework (4-category + 61 SKULL rules)
- ✅ Orchestrator specifications (10+ orchestrators)
- ✅ TDD requirements (RED→GREEN→REFACTOR)
- ✅ Knowledge base validation
- ✅ Audit logging & compliance
- ✅ Performance SLAs
- ✅ Security requirements
- ✅ MCP integration criteria
- ✅ Version-agnostic design criteria
- ✅ Unified test suite criteria
- ✅ Plan Viewer Dashboard criteria (AC-PLAN-DASH-*)

---

## 📊 Key Metrics (v9.0.0)

| Metric | Value |
|--------|-------|
| **Total Criteria** | 350+ |
| **P0_CRITICAL** | 70+ |
| **Validation Gates** | 12 |
| **Blocking Gates** | 8 |
| **Plan Dashboard Criteria** | 7 |

---

## 🔗 Referenced By

| File | Purpose |
|------|---------|
| `.github/prompts/cortex-search.prompt.md` | Gap detection against AC |
| `.github/prompts/cortex-align.prompt.md` | Remediation planning |
| `.github/prompts/CORTEX.prompt.md` | Master entry point |

---

## 🔄 Lifecycle Management

### Remediation Plans
- **Active:** `remediation-plan.yaml` (singular, no timestamp)
- **Archive:** `archive/remediation-plan-{YYYY-MM-DD}.yaml`
- **Rule:** Archive before regenerate (preserve history)

### Search Findings
- **Location:** `search-findings-{timestamp}.yaml`
- **Consumed by:** `cortex-align.prompt.md`

---

## ⚠️ Deprecated Locations

The following locations are **NO LONGER USED** for acceptance criteria:

- ❌ `.asif/AI-Learning/cortex6/acceptance/` - DEPRECATED
- ❌ `.asif/AI-Learning/cortex6/cortex-ac.yaml` - DEPRECATED
- ❌ `cortex-brain/config/acceptance-criteria.yaml` - DELETED (was v5.0)
- ❌ Any `00-*-TRACKER.yaml` files in cortex6-fixes - DELETED

---

## 🚀 Usage

### Run Search (Gap Detection)
```
/CORTEX search
```

### Run Align (Remediation Planning)
```
/CORTEX align
```

### Epic Review
```
/CORTEX epic review
```

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
