# CORTEX 6.0 Acceptance Criteria - Canonical Location

**Status:** ✅ AUTHORITATIVE  
**Last Updated:** 2026-01-09  
**Version:** 7.5.0

---

## 📁 File Structure

```
cortex-brain/documents/planning/active/cortex6/acceptance-criteria/
├── 00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml   # Source of Truth
├── remediation-plan.yaml                             # Active remediation
├── snowball-strategy.yaml                            # Prioritization framework
├── README.md                                         # This file
└── archive/                                          # Historical remediations
    └── remediation-plan-{YYYY-MM-DD}.yaml
```

---

## 🎯 Single Source of Truth

**ALL acceptance criteria for CORTEX 6.0 are in:**
```
00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml
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

---

## 📊 Key Metrics (v7.5.0)

| Metric | Value |
|--------|-------|
| **Total Criteria** | 340+ |
| **P0_CRITICAL** | 65+ |
| **Validation Gates** | 12 |
| **Blocking Gates** | 8 |

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
- ❌ `.asif/AI-Learning/cortex6/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml` - DEPRECATED
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
