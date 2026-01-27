# CORE-038: File Placement Policy - STRICT ENFORCEMENT
## CORTEX Root Directory Cleanup & Enforcement

**Date:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Rule:** CORE-038 (File Placement Policy) - TIER 0 IMMUTABLE  
**Status:** IMPLEMENTATION PLAN  

---

## 🎯 POLICY STATEMENT

### Core Rule: CORE-038

**No files shall be created in the root of the CORTEX repository unless absolutely required for Git/Docker infrastructure.**

All application files, documentation, configuration, and logs must be placed in appropriately named subfolders.

---

## 📋 FILE CATEGORIZATION & PLACEMENT

### Category 1: Git/Docker Infrastructure (ROOT ALLOWED)

These files are **REQUIRED** in root and are EXEMPT from subfolding:

| File | Purpose | Placement | Status |
|------|---------|-----------|--------|
| `.gitignore` | Git exclusions | ✅ ROOT | KEEP |
| `.dockerignore` | Docker exclusions | ✅ ROOT | KEEP |
| `.pre-commit-config.yaml` | Pre-commit hooks | ✅ ROOT | KEEP |
| `Dockerfile` | Docker image build | ✅ ROOT | KEEP |
| `docker-compose.yaml` | Production docker-compose | ✅ ROOT | KEEP |
| `docker-compose.dev.yaml` | Development docker-compose | ✅ ROOT | KEEP |
| `docker-compose.test.yaml` | Test docker-compose | ✅ ROOT | KEEP |
| `.cortex-version` | Version tracking | ✅ ROOT | KEEP |

**Rationale:** Docker and Git require these at root for CI/CD automation.

---

### Category 2: Configuration Files (MUST MOVE TO SUBFOLDERS)

These files should be moved to `cortex/config/` or `deployment/config/`:

| File | Current | New Location | Purpose |
|------|---------|--------------|---------|
| `cortex-config.yaml` | ROOT | `cortex/config/cortex-config.yaml` | Main configuration |
| `pyrightconfig.json` | ROOT | `cortex/config/pyrightconfig.json` | Type checker config |
| `mkdocs.yml` | ROOT | `docs/mkdocs.yml` | Documentation config |

---

### Category 3: Documentation Files (MUST MOVE TO `docs/`)

These files should be moved to `docs/`:

| File | Current | New Location | Purpose |
|------|---------|--------------|---------|
| `START-HERE.md` | ROOT | `docs/START-HERE.md` | User guide |
| `requirements.txt` | ROOT | `deployment/requirements.txt` | Python dependencies |

---

### Category 4: Phase Documentation (MUST MOVE TO `_workspaces/docker-plan/`)

These files should be moved to `_workspaces/docker-plan/`:

| File | Current | New Location | Purpose |
|------|---------|--------------|---------|
| `DOCKER-PLAN-EXECUTION-LOG.txt` | ROOT | `_workspaces/docker-plan/logs/execution-log-20260127.txt` | Phase execution log |
| `DOCKER-PLAN-INDEX.md` | ROOT | `_workspaces/docker-plan/docker-plan-index.md` | Already in correct location |
| `DOCKER-PLAN-PHASE-0-EXECUTIVE-SUMMARY.md` | ROOT | `_workspaces/docker-plan/archive/phase-0-executive-summary.md` | Phase 0 archive |
| `PHASE-1-READINESS-DOCKER-PLAN.md` | ROOT | `_workspaces/docker-plan/archive/phase-1-readiness.md` | Phase 1 archive |
| `phase2-execution.log` | ROOT | `_workspaces/docker-plan/logs/phase-2-execution.log` | Phase 2 log |
| `phase3-execution.log` | ROOT | `_workspaces/docker-plan/logs/phase-3-execution.log` | Phase 3 log |

---

### Category 5: Decision/Strategy Documents (MUST MOVE TO `docs/`)

These files should be moved to `docs/`:

| File | Current | New Location | Purpose |
|------|---------|--------------|---------|
| `VERSIONING-DECISION-BRIEFING.md` | ROOT | `docs/archive/versioning-decision-briefing.md` | Decision docs |
| `VERSIONING-FINAL-RECOMMENDATION.md` | ROOT | `docs/archive/versioning-final-recommendation.md` | Recommendations |
| `VERSIONING-STRATEGY-ANALYSIS.md` | ROOT | `docs/archive/versioning-strategy-analysis.md` | Analysis |

---

## 🔧 CLEANUP EXECUTION PLAN

### Step 1: Create Destination Directories

```bash
# Create config subdirectory
mkdir -p cortex/config/

# Create deployment config subdirectory (if not exists)
mkdir -p deployment/config/
mkdir -p deployment/

# Create docs archive
mkdir -p docs/archive/

# Create _workspaces logs and archive
mkdir -p _workspaces/docker-plan/logs/
mkdir -p _workspaces/docker-plan/archive/
```

### Step 2: Move Configuration Files

```bash
# Move cortex-config.yaml
mv cortex-config.yaml cortex/config/cortex-config.yaml

# Move pyrightconfig.json
mv pyrightconfig.json cortex/config/pyrightconfig.json

# Move mkdocs.yml
mv mkdocs.yml docs/mkdocs.yml

# Move requirements.txt
mv requirements.txt deployment/requirements.txt
```

### Step 3: Move Documentation

```bash
# Move START-HERE.md
mv START-HERE.md docs/START-HERE.md

# Move versioning documents to archive
mv VERSIONING-DECISION-BRIEFING.md docs/archive/versioning-decision-briefing.md
mv VERSIONING-FINAL-RECOMMENDATION.md docs/archive/versioning-final-recommendation.md
mv VERSIONING-STRATEGY-ANALYSIS.md docs/archive/versioning-strategy-analysis.md
```

### Step 4: Move Phase Documentation

```bash
# Move phase logs
mv DOCKER-PLAN-EXECUTION-LOG.txt _workspaces/docker-plan/logs/execution-log-20260127.txt
mv phase2-execution.log _workspaces/docker-plan/logs/phase-2-execution.log
mv phase3-execution.log _workspaces/docker-plan/logs/phase-3-execution.log

# Move phase documentation to archive
mv DOCKER-PLAN-PHASE-0-EXECUTIVE-SUMMARY.md _workspaces/docker-plan/archive/phase-0-executive-summary.md
mv PHASE-1-READINESS-DOCKER-PLAN.md _workspaces/docker-plan/archive/phase-1-readiness.md
```

---

## 🎯 ENFORCED POLICY FOR CORTEX

### Phase 2 & Beyond: File Placement Enforcement

**All new files created during Phases 2-6 MUST comply with CORE-038:**

```yaml
policy_enforcement:
  applies_to: "CORTEX repository only"
  scope: "All new files created"
  enforcement_level: "STRICT (TIER 0 - BLOCKS EXECUTION)"
  
  permitted_root_files:
    - ".gitignore"
    - ".dockerignore"
    - ".pre-commit-config.yaml"
    - "Dockerfile"
    - "docker-compose.yaml"
    - "docker-compose.dev.yaml"
    - "docker-compose.test.yaml"
    - ".cortex-version"
  
  all_other_files:
    placement: "MUST be in appropriate subfolder"
    examples:
      - "Documentation → docs/"
      - "Configuration → cortex/config/ or deployment/config/"
      - "Logs → _workspaces/docker-plan/logs/"
      - "Archives → docs/archive/ or _workspaces/docker-plan/archive/"
  
  violation_consequence: "AC_BLOCK - Operation fails, violation reported"
```

---

## 📂 FOLDER STRUCTURE AFTER CLEANUP

```
CORTEX (Root)
├── .gitignore                          ✅ KEEP (Git infra)
├── .dockerignore                       ✅ KEEP (Docker infra)
├── .pre-commit-config.yaml             ✅ KEEP (Git infra)
├── .cortex-version                     ✅ KEEP (Version tracking)
├── Dockerfile                          ✅ KEEP (Docker infra)
├── docker-compose.yaml                 ✅ KEEP (Docker infra)
├── docker-compose.dev.yaml             ✅ KEEP (Docker infra)
├── docker-compose.test.yaml            ✅ KEEP (Docker infra)
│
├── cortex/
│   ├── config/
│   │   ├── cortex-config.yaml          ← MOVED HERE
│   │   └── pyrightconfig.json          ← MOVED HERE
│   ├── __init__.py
│   ├── api/
│   ├── brain/
│   ├── orchestrators/
│   └── ... (all application code)
│
├── deployment/
│   ├── config/
│   ├── requirements.txt                ← MOVED HERE
│   └── ... (deployment configs)
│
├── docs/
│   ├── mkdocs.yml                      ← MOVED HERE
│   ├── START-HERE.md                   ← MOVED HERE
│   ├── 00-README.md
│   ├── archive/
│   │   ├── versioning-decision-briefing.md        ← MOVED HERE
│   │   ├── versioning-final-recommendation.md     ← MOVED HERE
│   │   └── versioning-strategy-analysis.md        ← MOVED HERE
│   └── ... (all documentation)
│
├── _workspaces/
│   └── docker-plan/
│       ├── logs/
│       │   ├── execution-log-20260127.txt         ← MOVED HERE
│       │   ├── phase-2-execution.log              ← MOVED HERE
│       │   └── phase-3-execution.log              ← MOVED HERE
│       ├── archive/
│       │   ├── phase-0-executive-summary.md       ← MOVED HERE
│       │   └── phase-1-readiness.md               ← MOVED HERE
│       ├── migration-phases-plan.yaml
│       ├── wiring-schema.yaml
│       └── ... (all docker-plan files)
│
└── tests/
    └── ... (all tests)
```

---

## 📋 CLEANUP CHECKLIST

### Pre-Cleanup Validation

- [ ] Git working tree is clean
- [ ] All commits are pushed
- [ ] Current branch is CORTEX
- [ ] No active development on root files

### Cleanup Steps

- [ ] Create all destination directories
- [ ] Move configuration files (cortex-config.yaml, pyrightconfig.json, mkdocs.yml)
- [ ] Move documentation files (START-HERE.md, versioning-*.md)
- [ ] Move phase documentation and logs
- [ ] Verify all moves successful
- [ ] Verify no broken imports/references
- [ ] Update any hard-coded file paths in code

### Post-Cleanup Validation

- [ ] Root directory only has 8 permitted files
- [ ] All references updated (config loading, imports, etc.)
- [ ] Test suite still passes
- [ ] Documentation still accessible
- [ ] Git status clean

### Git Operations

- [ ] Stage all file moves
- [ ] Commit with message: "chore: enforce CORE-038 file placement policy - move root files to appropriate subfolders"
- [ ] Verify commit

---

## 🔐 POLICY ENFORCEMENT IN MIGRATION

### Phase 2-6 Compliance

**All phases must enforce CORE-038:**

```python
# In phase execution scripts (phase-2-execute.sh, phase-3-execute.sh, etc.):

# Check for root-level violations
check_root_violations() {
    local permitted_files=(
        ".gitignore"
        ".dockerignore"
        ".pre-commit-config.yaml"
        "Dockerfile"
        "docker-compose.yaml"
        "docker-compose.dev.yaml"
        "docker-compose.test.yaml"
        ".cortex-version"
    )
    
    local violations=()
    for file in $(find . -maxdepth 1 -type f ! -name '.*' -name '*.py' -o -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.txt' -o -name '*.json'); do
        filename=$(basename "$file")
        if [[ ! " ${permitted_files[@]} " =~ " ${filename} " ]]; then
            violations+=("$file")
        fi
    done
    
    if [ ${#violations[@]} -gt 0 ]; then
        log_error "CORE-038 VIOLATION: Root-level files found (must be in subfolders)"
        for file in "${violations[@]}"; do
            log_error "  Violation: $file"
        done
        return 1
    fi
    return 0
}

# Call before each phase
if ! check_root_violations; then
    log_error "AC_BLOCK: CORE-038 enforcement failed"
    exit 1
fi
```

---

## 📊 IMPACT ANALYSIS

### Files Affected

| Category | Count | Action |
|----------|-------|--------|
| Configuration | 3 | Move to `cortex/config/` + `deployment/` |
| Documentation | 6 | Move to `docs/` + `docs/archive/` |
| Phase Logs | 3 | Move to `_workspaces/docker-plan/logs/` |
| Phase Docs | 2 | Move to `_workspaces/docker-plan/archive/` |
| **Total** | **14** | **Move to subfolders** |
| **Keep in Root** | **8** | Docker/Git infrastructure |

### Code Changes Required

| Component | Changes |
|-----------|---------|
| Config Loading | Update paths (cortex-config.yaml → cortex/config/cortex-config.yaml) |
| Pyright Config | Update path references (pyrightconfig.json → cortex/config/pyrightconfig.json) |
| MkDocs Config | Update path references (mkdocs.yml → docs/mkdocs.yml) |
| Documentation Links | Update markdown links in docs |
| Deployment Scripts | Update requirements.txt path references |

---

## ✅ ENFORCEMENT GATES

### Phase Entry Gate (All Phases 2-6)

```yaml
phase_entry_gate:
  name: "CORE-038 File Placement Validation"
  enforcement: "STRICT (TIER 0 - BLOCKS)"
  
  checks:
    - name: "Root Directory Scan"
      validation: "No .py, .md, .yaml, .txt, .json files except permitted"
      failure_action: "BLOCK phase execution"
      
    - name: "File Reference Validation"
      validation: "All paths updated in code"
      failure_action: "BLOCK phase execution"
      
    - name: "Import Validation"
      validation: "cortex.config imports work correctly"
      failure_action: "BLOCK phase execution"
  
  bypass_allowed: false  # No bypass for CORE-038
```

---

## 📋 ACCEPTANCE CRITERIA

### AC-ROOT-CLEANUP-001: Cleanup Execution
- ✅ All 14 files moved to appropriate subfolders
- ✅ Destination directories created
- ✅ File moves verified successful

### AC-ROOT-CLEANUP-002: Code Updates
- ✅ All hard-coded paths updated
- ✅ Config loading verified
- ✅ Documentation links updated

### AC-ROOT-CLEANUP-003: Validation
- ✅ Root contains only 8 permitted files
- ✅ All imports working
- ✅ Test suite passing
- ✅ No broken references

### AC-ROOT-CLEANUP-004: Policy Enforcement
- ✅ CORE-038 enforcement added to phase scripts
- ✅ Entry gate checks implemented
- ✅ Violation detection working

---

## 🚀 EXECUTION PLAN

### Immediate Actions

1. **Review this policy** ← You are here
2. **Execute cleanup:**
   ```bash
   bash _workspaces/docker-plan/execute-core-038-cleanup.sh
   ```
3. **Update code paths** (automated by cleanup script)
4. **Validate all changes** (run test suite)
5. **Commit cleanup**
   ```bash
   git add -A
   git commit -m "chore: enforce CORE-038 file placement policy - move root files to subfolders"
   ```

### Phase 2+ Implementation

All phase scripts must include CORE-038 validation before execution.

---

## 📖 REFERENCES

| Document | Authority |
|----------|-----------|
| CORE-038 File Placement Policy | cortex_brain/tier0/governance/ |
| Migration Plan | _workspaces/docker-plan/migration-phases-plan.yaml |
| Docker Plan | _workspaces/docker-plan/docker-plan-index.md |

---

**Created:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Status:** ✅ POLICY DOCUMENTED

**→ Ready for cleanup execution**
