# Planning Registry Structure Evolution
**CORTEX Versions 4.0 → 5.0 → 5.5 → Current (6.0)**

---

## 📊 Version Evolution Summary

### CORTEX-4.0 (Early)
**Structure:** YAML files scattered across multiple locations
- Prompts: `.github/prompts/planning/`
- Brain specs: `cortex/brain/tier2/domains/planning/`
- Governance: `cortex/core/governance/planning-rules.yaml`
- Orchestrators: `cortex/orchestrators/domain/planning_orchestrator.py`
- Tests: `tests/unit/` & `tests/integration/`

**Issues:** Fragmented, unclear hierarchy, no registry pattern

---

### CORTEX-5.0 (Evolution)
**Structure:** Initial registry pattern attempted
- Created `cortex-registry/planning/` root folder
- Stored legacy plans as YAML/JSON files
- Brain tier rules documented in metadata

**Issues:** 
- Files still scattered (legacy locations not consolidated)
- No standardized plan structure
- Duplication between old and new locations

---

### CORTEX-5.5 (Consolidation - AC-PERMANENT-FIX-011)
**Structure:** Standardized plan organization
```
cortex-registry/planning/
├── {plan-id}/                          # Kebab-case ID
│   ├── phase_spec/                     # Specification files
│   │   └── *.md
│   ├── phase_completion/               # Completion reports
│   │   └── *.md
│   ├── analysis/                       # Analysis documents
│   │   └── *.md
│   └── roadmap/                        # Roadmap artifacts
│       └── *.md
```

**Example Plans (CORTEX-5.5):**
- `cortex-registry/planning/phase-1-completion/`
- `cortex-registry/planning/phase-2-completion/`
- `cortex-registry/planning/phase-3-completion/`
- `cortex-registry/planning/phase-4-refactoring-spec/`

**Key Rules Enforced:**
- ✅ CORE-028: FilenameFactory for all names
- ✅ CORE-038: File placement enforcement
- ✅ CORE-040: Spec-driven execution paths
- ✅ Pre-commit hook blocks files outside registry

---

### Current State (CORTEX-6.0) - ⚠️ DEGRADED
**Structure:** Regression from CORTEX-5.5 standard
```
cortex-registry/planning/
├── README.md                                          # ❌ ROOT FILE
├── execution-config-refactor-plan-2026-01-26.yaml   # ❌ ROOT FILE (loose)
├── documentation/
│   └── doc-portal-001/
│       ├── metadata.yaml
│       └── plan.yaml
├── registry/
│   ├── index.yaml
│   └── metadata.yaml
└── system/
    └── execution-config-refactor/
        ├── metadata.yaml
        └── plan.yaml
```

**Problems Identified:**
1. ❌ **Files in root** (violates CORTEX-5.5 PERMANENT FIX)
   - `execution-config-refactor-plan-2026-01-26.yaml` should be in `system/execution-config-refactor/`
   - `README.md` should be at `cortex-registry/index.md` only

2. ❌ **Inconsistent nesting**
   - `documentation/doc-portal-001/` uses domain subdirectory
   - `system/execution-config-refactor/` uses domain + plan nesting
   - No standardized hierarchy

3. ❌ **Index files scattered**
   - `registry/index.yaml` should be `cortex-registry/planning/index.yaml` at root
   - Metadata files inconsistently placed

4. ❌ **Missing plan ID standardization**
   - CORTEX-5.5 enforced kebab-case: `phase-1`, `ac-010-status-phase-4-ready`
   - Current uses: `doc-portal-001`, `execution-config-refactor`
   - Inconsistent prefix patterns

---

## 🎯 Recommended Target Structure (Option 2 - Hybrid)

**Proposal:** Align with CORTEX-5.5 PERMANENT FIX + add domain-based organization

```
cortex-registry/planning/
├── index.yaml                             # ONLY root metadata (registry SSOT)
├── orchestration/
│   ├── index.yaml
│   └── {plan-id}/
│       ├── plan.yaml
│       ├── phases.yaml
│       ├── audit.yaml
│       └── artifacts/
│           ├── phase_spec/
│           ├── phase_completion/
│           ├── analysis/
│           └── roadmap/
├── documentation/
│   ├── index.yaml
│   └── {plan-id}/
│       ├── plan.yaml
│       ├── phases.yaml
│       └── artifacts/
│           └── ...
└── [future-domains]/
    └── {plan-id}/
        └── ...
```

**Key Features:**
- ✅ Root has **only** `index.yaml` (registry metadata SSOT)
- ✅ Plans organized by domain subdirectory
- ✅ Within each domain: flat `{plan-id}/` structure
- ✅ All plans follow identical internal hierarchy
- ✅ Kebab-case plan IDs enforced via NamingFactory
- ✅ Maximum nesting: 4 levels (`planning/domain/plan-id/artifact-type/`)

---

## 🔄 Migration Path (CORTEX-6.0 → Target)

### Step 1: Consolidate Root
```
❌ DELETE:   cortex-registry/planning/README.md
❌ MOVE:     execution-config-refactor-plan-2026-01-26.yaml 
              → system/execution-config-refactor/plan.yaml
✅ CREATE:   cortex-registry/planning/index.yaml (registry metadata only)
```

### Step 2: Organize by Domain
```
Current: documentation/doc-portal-001/
Target:  documentation/{kebab-case-plan-id}/
  ├── plan.yaml
  ├── phases.yaml
  ├── audit.yaml
  └── artifacts/

Current: system/execution-config-refactor/
Target:  orchestration/execution-config-refactor/ (or rename domain)
  ├── plan.yaml
  ├── phases.yaml
  └── artifacts/
```

### Step 3: Update Loader
```python
# PlanningRegistryLoader ready for new structure
planning_registry_loader.create_plan_folder()
  ├── Expects: registry_path / "planning" / domain / plan_name /
  ├── Ready to deploy (NO CODE CHANGES NEEDED)
  └── Respects NamingFactory for kebab-case conversion
```

---

## 📋 Comparison Matrix

| Aspect | CORTEX-4.0 | CORTEX-5.0 | CORTEX-5.5 | Current | Target |
|--------|-----------|-----------|-----------|---------|--------|
| **Registry Path** | Scattered | Emerging | ✅ Standardized | ⚠️ Mixed | ✅ Structured |
| **Root Clutter** | Yes | Partial | ❌ Blocked | ⚠️ Yes | ✅ None |
| **Plan Hierarchy** | Unclear | Informal | `{plan-id}/{type}/` | ❌ Inconsistent | ✅ Domain/{plan}/{type} |
| **Kebab-Case IDs** | No | No | ✅ Enforced | ⚠️ Partial | ✅ Enforced |
| **Enforcement** | No | No | ✅ Pre-commit hook | ❌ Disabled | ✅ Re-enabled |
| **Max Nesting** | N/A | 3+ | 3 levels | 4+ levels | ✅ 4 levels |
| **Loader Ready** | N/A | N/A | ✅ Full | ✅ Full | ✅ Full |
| **CORE Rules** | — | — | 3+ rules | ❌ Violated | ✅ Compliant |

---

## 🚀 Implementation Status

**Orchestrator Consolidation:** ✅ COMPLETE (Single v2.0, 901 LOC)
**Registry Loader:** ✅ PRODUCTION READY (No code changes needed)
**Structure Simplification:** ✅ PROPOSED (Option 2: Hybrid model)
**Migration Path:** ✅ DOCUMENTED (3-step consolidation)
**Governance Compliance:** ⚠️ PENDING (Pre-commit hook re-enablement)

---

## 💡 Key Insights

1. **CORTEX-5.5 Was Correct**: Flat `{plan-id}/{artifact-type}/` structure worked well
2. **Current Regression**: Added unnecessary domain nesting, creating inconsistency
3. **Option 2 Advantage**: Adds domain context WITHOUT breaking flat plan structure
4. **Loader Already Ready**: `PlanningRegistryLoader` compatible with target structure (no rewrite needed)
5. **Enforcement Critical**: CORTEX-5.5's pre-commit hook prevented this regression—should be re-enabled
