# CORTEX Registry Structure Correction

**Date:** 2026-02-17  
**Authority:** Phase 103 Recovery  
**Issue:** Critical namespace collision between CORTEX meta-system plans and user repository plans

---

## 🚨 Problem Statement

**Phase 103 Stage 6-8 implementation incorrectly merged two semantically distinct namespaces:**

### Before (CORRECT - Preserved):
```
cortex-registry/
├── _cortex-master/              ← CORTEX META-SYSTEM (Develops CORTEX itself)
│   ├── phases/
│   │   ├── planned/             ← phase-103, phase-104, etc
│   │   ├── completed/           ← phase-90, phase-27, etc
│   │   └── deferred/
│   ├── core/                    ← CORTEX governance, wiring, config
│   ├── knowledge/               ← CORTEX tech stack knowledge
│   ├── baselines/               ← CORTEX development baselines
│   └── CORTEX-STATUS-*.yaml     ← CORTEX system status
│
└── planning/                    ← USER REPOSITORIES (Uses CORTEX)
    └── phases/
        └── planned/             ← User repo onboarding/analysis plans
```

### After Phase 103 S6-S8 (INCORRECT - Rolled Back):
```
cortex-registry/
└── planning/                    ❌ MIXED NAMESPACE
    ├── phases/
    │   ├── planned/             ← CORTEX + User phases mixed
    │   └── consolidated/        ← Legacy consolidations
    └── metrics/                 ← CORTEX status files moved here
```

**Critical Loss:**  
Cannot distinguish between:
- **CORTEX development plans** (for developing CORTEX via cortex-architect agent)
- **User repository plans** (for repositories CORTEX manages)

---

## ✅ Corrected Structure (MANDATORY)

### Semantic Separation Restored:

```
cortex-registry/
│
├── _cortex-master/              🔵 CORTEX META-SYSTEM (Read-only by user agents)
│   │
│   ├── phases/                  ← CORTEX development lifecycle
│   │   ├── planned/             ← phase-103, phase-104 (CORTEX features)
│   │   │   └── phase-103-registry-intelligence-consolidation.yaml
│   │   ├── completed/           ← phase-90, phase-27 (finished)
│   │   └── deferred/            ← Postponed CORTEX features
│   │
│   ├── core/                    ← CORTEX system contracts
│   │   ├── governance/          ← core-rules.yaml, audit-checklist.yaml
│   │   ├── config/              ← master-plan.yaml, workflows-index.yaml
│   │   ├── wiring/              ← contract.yaml, wiring.yaml
│   │   └── specifications/      ← exec-flow.yaml, intent-routing.yaml
│   │
│   ├── knowledge/               ← CORTEX tech stack knowledge
│   │   ├── architecture/        ← DDD, REST, GraphQL patterns
│   │   ├── security/            ← OWASP, Azure, secrets best practices
│   │   ├── testing/             ← TDD, BDD, integration testing
│   │   └── ...
│   │
│   ├── baselines/               ← CORTEX development snapshots
│   │   ├── phase-25-baseline-20260216.json
│   │   └── production-readiness-report-20260216.json
│   │
│   ├── dashboard/               ← CORTEX meta-dashboard data
│   │   └── data/
│   │       └── plan-summary.json
│   │
│   ├── archive/                 ← Deprecated CORTEX artifacts
│   │
│   ├── CORTEX-STATUS-2026-02-16.yaml      ← System health status
│   ├── DEFERRED-PHASES-ROADMAP.yaml       ← Postponed features
│   └── master-index.yaml                  ← Central registry index
│
├── planning/                    🟢 USER REPOSITORIES (Writable by CORTEX)
│   ├── phases/
│   │   └── planned/             ← User repo onboarding/analysis plans
│   │       ├── phase-registry-consolidation.yaml    ← Example user repo plan
│   │       └── registry-consolidation-migration.yaml
│   │
│   ├── repos/                   🆕 User repo metadata
│   │   └── [repo_name]/
│   │       ├── onboarding.yaml
│   │       ├── phase-plan.yaml
│   │       └── compliance-report.yaml
│   │
│   └── templates/               ← User repo plan templates
│       ├── onboarding-template.yaml
│       └── audit-template.yaml
│
├── domains/                     🟣 COMPANY KNOWLEDGE (External integration)
│   └── [Company domains loaded at runtime]
│
├── governance/                  🟡 SHARED GOVERNANCE (CORTEX + User)
│   ├── core-rules.yaml          ← Symlink to _cortex-master/core/governance/
│   └── audit-checklist.yaml     ← Symlink to _cortex-master/core/governance/
│
├── integration/                 🔶 RUNTIME INTEGRATION
│   ├── mcp-gateway/
│   └── orchestrator-bindings/
│
├── patterns/                    🟠 REUSABLE PATTERNS
│   ├── architecture/
│   └── refactoring/
│
├── templates/                   🟤 CORTEX TEMPLATES (Not user)
│   ├── orchestrator-spec-template.yaml
│   └── phase-template.yaml
│
├── workflows/                   ⚪ CORTEX WORKFLOWS
│   ├── onboarding-workflow.yaml
│   └── audit-workflow.yaml
│
├── master/                      🔵 LEGACY (Deprecated - Use _cortex-master/)
│
├── index.html                   🌐 Registry web viewer
└── manifest.yaml                📋 Registry configuration
```

---

## 🔐 Access Control Rules

| Folder | CORTEX Architect | User Agents | MCP Tools |
|--------|------------------|-------------|-----------|
| `_cortex-master/` | READ + WRITE | READ ONLY | READ ONLY |
| `planning/` | READ + WRITE | READ + WRITE | READ + WRITE |
| `domains/` | READ ONLY | READ ONLY | READ ONLY |
| `governance/` | READ ONLY | READ ONLY | READ ONLY |

**Enforcement:**
- `_cortex-master/` modifications ONLY via `cortex-architect` agent
- `planning/` modifications by any CORTEX agent
- Phase files in `_cortex-master/phases/planned/` are CORTEX development plans
- Phase files in `planning/phases/planned/` are user repository plans

---

## 🧪 Golden Tests (MANDATORY)

### Test 1: Namespace Isolation

```python
def test_cortex_master_isolation():
    """Verify _cortex-master contains only CORTEX development plans."""
    cortex_phases = Path("cortex-registry/_cortex-master/phases/planned").glob("*.yaml")
    
    for phase_file in cortex_phases:
        with open(phase_file) as f:
            content = yaml.safe_load(f)
            
        # CORTEX phases must reference CORTEX architecture
        assert "cortex" in content.get("title", "").lower() or \
               "phase" in content.get("phase_id", ""), \
               f"{phase_file} is not a CORTEX meta-system phase"
        
        # CORTEX phases should NOT reference user repo names
        assert not any(repo in str(content) for repo in ["acme-corp", "user-repo", "client-project"])
```

### Test 2: User Plan Separation

```python
def test_user_planning_isolation():
    """Verify planning/ contains only user repository plans."""
    user_phases = Path("cortex-registry/planning/phases/planned").glob("*.yaml")
    
    for phase_file in user_phases:
        with open(phase_file) as f:
            content = yaml.safe_load(f)
        
        # User plans must reference external repositories
        assert "repository" in content or "repo_url" in content, \
               f"{phase_file} missing repository context"
        
        # User plans should NOT modify CORTEX internals
        forbidden_keywords = ["cortex/orchestrators", "cortex/mcp", ".github/agents"]
        assert not any(kw in str(content) for kw in forbidden_keywords), \
               f"{phase_file} references CORTEX internals (should use _cortex-master/)"
```

### Test 3: File Count Validation

```python
def test_phase_file_counts():
    """Verify phase files in correct namespaces."""
    cortex_planned = len(list(Path("cortex-registry/_cortex-master/phases/planned").glob("*.yaml")))
    user_planned = len(list(Path("cortex-registry/planning/phases/planned").glob("*.yaml")))
    
    # CORTEX should have active development phases
    assert cortex_planned >= 1, "Missing CORTEX development phases in _cortex-master/"
    
    # User planning may be empty (no user repos yet)
    assert user_planned >= 0, "Negative user phase count (impossible)"
    
    # Log counts for audit
    print(f"✅ CORTEX phases: {cortex_planned}")
    print(f"✅ User phases: {user_planned}")
```

### Test 4: Symlink Integrity

```python
def test_governance_symlinks():
    """Verify governance/ symlinks point to _cortex-master/."""
    core_rules = Path("cortex-registry/governance/core-rules.yaml")
    
    if core_rules.exists():
        # Should be symlink to _cortex-master/core/governance/
        assert core_rules.is_symlink(), "core-rules.yaml should be symlink"
        target = core_rules.resolve()
        assert "_cortex-master/core/governance" in str(target), \
               f"Symlink points to wrong location: {target}"
```

### Test 5: Access Pattern Validation

```python
def test_cortex_architect_writes_to_master():
    """Verify cortex-architect agent writes to _cortex-master/ only."""
    # Scan .github/agents/core/cortex-architect.md for file paths
    with open(".github/agents/core/cortex-architect.md") as f:
        content = f.read()
    
    # Should reference _cortex-master/ for CORTEX plans
    assert "_cortex-master/phases" in content, \
           "cortex-architect should write to _cortex-master/"
    
    # Should NOT write to planning/ for CORTEX development
    if "planning/phases" in content:
        # Verify context is about user repos, not CORTEX
        assert "user repository" in content.lower() or "external repo" in content.lower()
```

---

## 📊 Migration Impact

### Files Affected:
- **Python imports:** 0 (no code references _cortex-master path)
- **YAML references:** ~15 (phase references, dashboard data)
- **Agent documentation:** 3 files (.github/agents/core/)
- **Test files:** 5 new golden tests

### Risk Level: **LOW**
- Structure preserved (no files moved)
- Only documentation/golden tests added
- Rollback confirmed (phase-103-migration branch abandoned)

---

## 🎯 Implementation Checklist

- [x] Rollback phase-103-migration branch (git reset to 1caf4d662)
- [x] Document corrected structure (this file)
- [ ] Create golden tests in tests/integration/registry/
- [ ] Update .github/agents/core/cortex-architect.md (namespace rules)
- [ ] Update .github/agents/core/CORTEX.md (intent routing rules)
- [ ] Create cortex-registry/planning/repos/ structure
- [ ] Verify all symlinks in governance/ point to _cortex-master/
- [ ] Run golden tests (100% pass required)
- [ ] Update Phase 103 specification with corrected Stage 6
- [ ] Mark Phase 103 as "blocked" until structure validated

---

**Status:** ✅ Structure documented, golden tests designed  
**Next:** Implement golden tests → Validate → Update Phase 103 spec
