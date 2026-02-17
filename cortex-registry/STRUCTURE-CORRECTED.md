# CORTEX Registry Structure - Corrected (Phase 103)

**Date:** 2026-02-17  
**Status:** ✅ CORRECTED  
**Issue:** Phase 103 incorrectly moved `` contents to `planning/`, violating separation of concerns

---

## 🎯 Core Principle: Two Distinct Domains

### 1️⃣ `` - CORTEX Internal Development

**Purpose:** Plans, phases, governance, and knowledge **FOR DEVELOPING CORTEX ITSELF**  
**Consumer:** `cortex-architect.prompt.md` + CORTEX agents (TDDOrchestrator, etc.)  
**Scope:** CORTEX framework enhancement (Phase 1-150, CORE rules, orchestrator specs)

```
cortex-registry/
└──            # ✅ PRESERVED - CORTEX self-development
    ├── core/
    │   ├── governance/       # CORE-001 to CORE-056 rules
    │   ├── config/           # master-plan.yaml, workflows-index.yaml
    │   ├── meta/             # modes.yaml, response-format.yaml
    │   ├── specifications/   # orchestrator-dispatch.yaml, intent-routing.yaml
    │   └── wiring/           # contract.yaml, wiring.yaml
    ├── phases/
    │   ├── planned/          # phase-103+.yaml (future CORTEX phases)
    │   ├── completed/        # phase-1 to phase-102.yaml
    │   └── deferred/         # Postponed CORTEX phases
    ├── knowledge/            # CORTEX-specific KB (orchestrator_specs.json, etc.)
    ├── baselines/            # pre-phase38-baseline-*.json
    ├── dashboard/data/       # plan-summary.json
    ├── archive/              # Historical CORTEX plans
    ├── master-index.yaml     # CORTEX plan catalog
    ├── CORTEX-STATUS-*.yaml  # CORTEX development metrics
    └── DEFERRED-PHASES-ROADMAP.yaml
```

**Key Files:**
- `phases/planned/phase-103-registry-intelligence-consolidation.yaml` ← **STAYS HERE**
- `core/governance/core-rules.yaml` ← CORE-001 to CORE-056
- `knowledge/config/orchestrator_specs.json` ← TDDOrchestrator specs

---

### 2️⃣ `planning/` - User Production Work

**Purpose:** Plans for **USER'S PRODUCTION GITHUB REPOS** (NOT CORTEX)  
**Consumer:** Users planning work on their business applications  
**Scope:** Production repo features, migrations, infrastructure work

```
cortex-registry/
└── planning/                 # ✅ USER-FACING - Production repo plans
    ├── phases/               # User-defined phases for their repos
    ├── workflows/            # User workflow templates
    └── templates/            # User planning templates
```

**Example Use Case:**
```yaml
# cortex-registry/planning/phases/user-api-v2-migration.yaml
id: "api-v2-migration"
repo: "mycompany/production-api"
stages:
  - id: "S1"
    name: "GraphQL Schema Update"
    repo: "mycompany/production-api"  # ← External repo, NOT CORTEX
```

---

## 🚨 What Went Wrong in Phase 103 (Corrected)

### ❌ Original Migration (INCORRECT)

```bash
# VIOLATION: Moved CORTEX internal phases to user planning/
mv cortex-registry/phases/consolidated/*.yaml \
   cortex-registry/planning/phases/consolidated/

# VIOLATION: Broke  structure
rmdir cortex-registry/phases/
rmdir cortex-registry/
```

**Result:** Lost separation between CORTEX self-development and user production work.

### ✅ Corrected Structure (VALID)

```bash
# CORRECT:  stays intact
ls cortex-registry/phases/planned/phase-103*.yaml
# → phase-103-registry-intelligence-consolidation.yaml ✅

# CORRECT: planning/ is empty or contains only user plans
ls cortex-registry/planning/phases/
# → (empty) or user-defined phases only, NO phase-*.yaml ✅
```

---

## 📐 Directory Structure (Final)

```
cortex-registry/
├──            # ✅ CORTEX internal (cortex-architect.prompt.md)
│   ├── core/
│   │   ├── governance/       # core-rules.yaml (CORE-001 to CORE-056)
│   │   ├── config/           # master-plan.yaml, workflows-index.yaml
│   │   ├── meta/             # modes.yaml, response-format.yaml
│   │   ├── specifications/   # orchestrator-dispatch.yaml, intent-routing.yaml
│   │   └── wiring/           # contract.yaml, wiring.yaml
│   ├── phases/
│   │   ├── planned/          # phase-103-registry-intelligence-consolidation.yaml
│   │   ├── completed/        # phase-1 to phase-102.yaml
│   │   └── deferred/         # Postponed CORTEX phases
│   ├── knowledge/            # CORTEX KB (orchestrator_specs.json, etc.)
│   │   ├── architecture/     # engineering-design-patterns.yaml
│   │   ├── cloud/            # aws-best-practices.yaml
│   │   ├── config/           # orchestrator_specs.json
│   │   ├── security/         # azure-security.yaml
│   │   └── testing/          # tdd-guidelines.yaml
│   ├── baselines/            # pre-phase38-baseline-20260215-*.json
│   ├── dashboard/data/       # plan-summary.json
│   ├── archive/              # Historical CORTEX plans
│   ├── master-index.yaml     # CORTEX plan catalog
│   ├── CORTEX-STATUS-2026-02-16.yaml
│   └── DEFERRED-PHASES-ROADMAP.yaml
│
├── planning/                 # ✅ USER production repo plans
│   ├── phases/               # User-defined phases (NOT phase-*.yaml)
│   ├── workflows/            # User workflow templates
│   └── templates/            # User planning templates
│
├── knowledge-base/           # ✅ Onboarded repo KB (LENS-extracted)
│   └── (user repos)/         # Generated by cortex_onboard_repository_v3
│
├── governance/               # ✅ User repo governance rules
│   └── rules.yaml            # (User-specific, NOT CORE-001)
│
├── domains/                  # ✅ User domain models
├── templates/                # ✅ User templates
├── artifacts/                # ✅ User generated artifacts
├── metrics/                  # ✅ User metrics
└── master-index.yaml         # Registry catalog
```

---

## 🧪 Golden Tests (Enforcing Separation)

**File:** `tests/unit/registry/test_phase_103_structure.py`

### Test 1: `` Structure Preserved

```python
def test_cortex_master_structure_preserved(self):
    """Verify  internal structure remains intact."""
    required_paths = [
        "core/governance",
        "core/config",
        "phases/planned",
        "phases/completed",
        "knowledge",
        "baselines",
    ]
    
    for path in required_paths:
        assert (registry / path).exists()
```

### Test 2: `planning/` Separation

```python
def test_planning_folder_separation(self):
    """Verify planning/ folder is separate from ."""
    # CORTEX internal phases stay in 
    cortex_phase = registry / "phases/planned/phase-103*.yaml"
    assert cortex_phase.exists()
    
    # User planning/ should NOT contain CORTEX phases
    planning_phases = registry / "planning/phases"
    cortex_phases_in_planning = list(planning_phases.glob("phase-*.yaml"))
    assert len(cortex_phases_in_planning) == 0
```

### Test 3: No Duplicate Governance

```python
def test_no_duplicate_governance_rules(self):
    """Ensure governance rules exist only in core/governance."""
    cortex_gov = registry / "core/governance/core-rules.yaml"
    user_gov = registry / "governance/rules.yaml"
    
    assert cortex_gov.exists()
    
    if user_gov.exists():
        # Check for rule ID overlap (CORE-001 should only be in CORTEX gov)
        cortex_rules = yaml.safe_load(cortex_gov.read_text())
        user_rules = yaml.safe_load(user_gov.read_text())
        
        cortex_ids = {r["id"] for r in cortex_rules["rules"]}
        user_ids = {r["id"] for r in user_rules["rules"]}
        
        overlap = cortex_ids & user_ids
        assert len(overlap) == 0
```

### Test 4: Knowledge Base Separation

```python
def test_knowledge_base_structure(self):
    """Verify CORTEX internal KB stays in knowledge."""
    cortex_kb = registry / "knowledge"
    assert cortex_kb.exists()
    assert (cortex_kb / "config/orchestrator_specs.json").exists()
    
    # User KB is separate (for onboarded repos)
    user_kb = registry / "knowledge-base"
    if user_kb.exists():
        # Should NOT contain CORTEX orchestrator specs
        assert not (user_kb / "config/orchestrator_specs.json").exists()
```

---

## 🔗 Reference Updates

### Python Imports (Correct)

```python
# ✅ CORRECT: Load CORTEX governance rules
from cortex.registry.registry import GitBackedRegistry

registry = GitBackedRegistry(base_path="cortex-registry")
rules = registry.load_yaml("core/governance/core-rules.yaml")
```

### YAML References (Correct)

```yaml
# ✅ CORRECT: Reference CORTEX phase in orchestrator
phases:
  - path: "phases/planned/phase-103-registry-intelligence-consolidation.yaml"
    status: "ACTIVE"
```

---

## 📊 Validation Commands

```bash
# 1. Verify  structure
find cortex-registry/_cortex-master -type d | sort

# 2. Check CORTEX phases stay in 
ls cortex-registry/phases/planned/*.yaml

# 3. Verify planning/ is for user work only
ls cortex-registry/planning/phases/
# Should be empty or contain only user plans (NOT phase-*.yaml)

# 4. Run golden tests
pytest tests/unit/registry/test_phase_103_structure.py -v

# 5. Check Python imports reference correct paths
grep -r "_cortex-master" cortex/ --include="*.py" | head -5
```

---

## ✅ Phase 103 Corrected Checklist

- [x] `` folder structure preserved
- [x] CORTEX phases stay in `phases/planned/`
- [x] `planning/` folder is empty or contains only user plans
- [x] Governance rules remain in `core/governance/`
- [x] Knowledge stays in `knowledge/`
- [x] Golden tests validate separation
- [x] Python imports use `` prefix correctly
- [x] YAML references use `` paths

---

## 🎓 Key Learnings

1. **`` is for CORTEX self-development** (like `.github/` for CI)
2. **`planning/` is for user production repo work** (NOT CORTEX phases)
3. **Separation prevents confusion** between framework development and user work
4. **Golden tests enforce this boundary** in CI/CD

**SSOT:** This document supersedes any previous Phase 103 migration instructions.
