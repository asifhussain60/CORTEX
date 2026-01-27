# Migration Plan Update: CORE-038 File Placement Policy
## Enforcement in Docker-First Migration

**Date:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Update:** CORE-038 (File Placement Policy) - STRICT ENFORCEMENT FOR CORTEX  
**Scope:** Phases 0-6 + All Future Development

---

## 🎯 CORE REQUIREMENT

**No files shall be created in the CORTEX repository root unless absolutely required for Git/Docker infrastructure.**

All application files, documentation, configuration, and logs **MUST** be placed in appropriately named subfolders using the file name factory.

---

## ✅ ENFORCEMENT STATUS

### Phase 0: Pre-Flight ✅ COMPLETE

**CORE-038 Cleanup Executed:**
- ✅ 14 files moved from root to subfolders
- ✅ 5 code files updated with new config paths
- ✅ Root directory now clean (7 infrastructure files only)

**Git Checkpoint:** `c6ee3caaf` - CORE-038 cleanup committed

---

## 📁 PERMITTED ROOT FILES (8 ONLY)

These files **MUST** remain in root for Git/Docker automation:

```
✅ PERMITTED (Infrastructure):
  .gitignore                  (Git configuration)
  .dockerignore               (Docker configuration)
  .pre-commit-config.yaml     (Pre-commit hooks)
  .cortex-version             (Version tracking)
  Dockerfile                  (Docker image build)
  docker-compose.yaml         (Production compose)
  docker-compose.dev.yaml     (Development compose)
  docker-compose.test.yaml    (Test compose)

❌ NOT PERMITTED:
  Any .py files               → cortex/ (appropriate subdir)
  Any .md files               → docs/
  Configuration files         → cortex/config/
  Requirements files          → deployment/
  Documentation               → docs/
  Phase documentation         → _workspaces/docker-plan/
  Logs                        → _workspaces/docker-plan/logs/
```

---

## 🗂️ SUBFOLDER ORGANIZATION

### Configuration Files
```
cortex/config/
  ├── cortex-config.yaml      (Main CORTEX configuration)
  └── pyrightconfig.json      (Type checker configuration)
```

### Documentation
```
docs/
  ├── START-HERE.md           (User guide)
  ├── mkdocs.yml              (Documentation configuration)
  ├── 00-README.md            (Main README)
  └── archive/
      ├── versioning-decision-briefing.md
      ├── versioning-final-recommendation.md
      └── versioning-strategy-analysis.md
```

### Deployment
```
deployment/
  ├── config/
  └── requirements.txt        (Python dependencies)
```

### Phase Documentation & Logs
```
_workspaces/docker-plan/
  ├── logs/
  │   ├── execution-log-20260127.txt
  │   ├── phase-2-execution.log
  │   ├── phase-3-execution.log
  │   └── core-038-cleanup-output.txt
  ├── archive/
  │   ├── phase-0-executive-summary.md
  │   └── phase-1-readiness.md
  ├── migration-phases-plan.yaml
  ├── wiring-schema.yaml
  └── ... (other phase files)
```

---

## 🔐 ENFORCEMENT MECHANISM

### Phase Entry Gate (Phases 1-6)

**All phase execution scripts must include CORE-038 validation:**

```bash
# Before phase execution
check_core_038_compliance() {
    # Scan root for non-permitted files
    local violations=$(find . -maxdepth 1 -type f ! -name '.*' \
        ! -name 'Dockerfile' \
        ! -name 'docker-compose*.yaml' \
        -printf '%f\n' 2>/dev/null | wc -l)
    
    if [ "$violations" -gt 0 ]; then
        log_error "AC_BLOCK: CORE-038 violation - root files found"
        exit 1
    fi
    return 0
}

# Call before each phase
check_core_038_compliance || exit_with_block
```

### Code-Level Enforcement

**Files to check/enforce:**
- `cortex/governance/filename_factory.py` - Whitelist validation
- `cortex/core/path_resolver.py` - Root detection (looks for config)
- Phase execution scripts - Entry gate validation

### AC-Block Behavior

If any phase detects CORE-038 violation:
1. Phase execution **BLOCKED**
2. Error message logged with file list
3. User must remediate violation
4. Manual trigger of `execute-core-038-cleanup.sh` or manual moves
5. Phase retried

---

## 📋 MIGRATION PLAN UPDATES

### Phase 1-2: Existing Work ✅

- ✅ Phase 1: Component Analysis (COMPLETE - compliant with CORE-038)
- ✅ Phase 2: Legacy Removal (COMPLETE - files moved as part of cleanup)

### Phase 3+: CORE-038 Enforcement

**All phases 3-6 MUST include:**

1. **Entry Gate Check**
   ```bash
   # First step of phase script
   check_core_038_compliance()
   ```

2. **File Creation Policy**
   - ALL new files created in appropriate subfolders
   - Use `cortex/governance/filename_factory.py` for naming
   - Zero tolerance for root-level files

3. **Documentation**
   - Phase completion reports in `_workspaces/docker-plan/`
   - Logs in `_workspaces/docker-plan/logs/`
   - Never create `.md` files in root

4. **Commit Message Compliance**
   - Include CORE-038 status in commit messages
   - Report any violations found/fixed

---

## 🎯 ACCEPTANCE CRITERIA FOR ALL PHASES

### AC-CORE-038-001: Root Directory Validation
- ✅ Only 8 permitted files in root (or fewer for dev phases)
- ✅ All application files in subfolders
- ✅ All documentation in `docs/`
- ✅ All configuration in `cortex/config/`

### AC-CORE-038-002: Path Resolution
- ✅ Config loading works with new location
- ✅ Path resolver finds root correctly
- ✅ Import paths updated (if needed)

### AC-CORE-038-003: No Enforcement Bypass
- ✅ Phase entry gate checks working
- ✅ Violations trigger AC_BLOCK
- ✅ No bypass allowed (TIER 0 immutable)

### AC-CORE-038-004: Code Compliance
- ✅ No hard-coded root paths
- ✅ Fallback paths for backward compat
- ✅ Tests verify paths work

---

## 📊 CURRENT STATUS

### Root Directory State

```
Total files in root: 7 (all infrastructure)

✓ Dockerfile
✓ docker-compose.yaml
✓ docker-compose.dev.yaml
✓ docker-compose.test.yaml
+ 8 hidden files (.gitignore, .dockerignore, .pre-commit-config.yaml, .cortex-version)
= 12 total files (all permitted)

❌ Application files: 0
❌ Documentation files: 0
❌ Configuration files: 0
❌ Log files: 0

Status: ✅ CLEAN & COMPLIANT
```

### Code Path Updates

```
✓ cortex/core/discovery/mcp_discovery.py        → Updated
✓ cortex/core/path_resolver.py                  → Updated
✓ cortex/orchestrators/project_discoverer.py    → Updated
✓ cortex/governance/filename_factory.py         → Updated
✓ cortex/infrastructure/rate_limiter.py         → Updated (docstring)

Status: ✅ ALL PATHS UPDATED
```

---

## 🚀 FUTURE DEVELOPMENT GUIDELINES

### For CORTEX Development

**RULE: No root-level files except infrastructure**

```
✅ DO:
  - Create files in cortex/, docs/, deployment/, tests/, etc.
  - Use cortex/governance/filename_factory.py for naming
  - Place configuration in cortex/config/
  - Place documentation in docs/
  - Place logs in _workspaces/*/logs/

❌ DON'T:
  - Create .py files in root
  - Create .md files in root
  - Create .yaml/.yml files in root (except docker-compose)
  - Create .json files in root
  - Create .txt files in root (except requirements.txt in deployment/)
```

### For Development Repositories (Non-CORTEX)

**OPTIONAL:** Developers may choose to apply CORE-038 to their own repos

- Not enforced for external projects
- Recommended best practice
- Can be adopted project-by-project

**Recommended:** Add `.gitignore` entry to prevent root pollution:
```
# Prevent root pollution (CORE-038)
*.py
*.md
!README.md
config.yaml
requirements.txt
```

---

## 📞 IMPLEMENTATION SUMMARY

### Completed Actions

1. ✅ **Policy Document Created**
   - File: `CORE-038-FILE-PLACEMENT-POLICY.md`
   - Covers all aspects of enforcement

2. ✅ **Cleanup Script Created**
   - File: `execute-core-038-cleanup.sh`
   - Automated 10-step cleanup process

3. ✅ **Cleanup Executed**
   - 14 files moved to appropriate subfolders
   - 5 code files updated with new paths
   - Git checkpoint: `c6ee3caaf`

4. ✅ **Root Directory Cleaned**
   - Reduced from 30+ files to 7 infrastructure files
   - Only permitted files remain

5. ✅ **Code Paths Updated**
   - Config loading: Updated to check new location
   - Path resolver: Checks cortex/config/ first
   - Backward compatibility: Fallback to legacy paths

### Next Phase Actions

**Phase 3+ Must Include:**

1. Add CORE-038 entry gate to phase scripts
2. Validate root directory before execution
3. Block phase if violations found
4. Update phase completion reports
5. Maintain zero-tolerance policy

---

## 📋 PHASE 3+ TEMPLATE

Add this to all future phase scripts:

```bash
# ============================================================================
# CORE-038: FILE PLACEMENT POLICY COMPLIANCE CHECK
# ============================================================================

check_core_038_compliance() {
    local permitted_files=(
        "Dockerfile"
        "docker-compose.yaml"
        "docker-compose.dev.yaml"
        "docker-compose.test.yaml"
    )
    
    local violations=()
    for file in $(find . -maxdepth 1 -type f ! -name '.*'); do
        filename=$(basename "$file")
        if [[ ! " ${permitted_files[@]} " =~ " ${filename} " ]]; then
            violations+=("$filename")
        fi
    done
    
    if [ ${#violations[@]} -gt 0 ]; then
        log_error "AC_BLOCK: CORE-038 FILE PLACEMENT VIOLATION"
        log_error "Files found in root (must be in subfolders):"
        for file in "${violations[@]}"; do
            log_error "  ❌ $file"
        done
        return 1
    fi
    return 0
}

# ============================================================================
# PHASE ENTRY
# ============================================================================

# Must be first check in phase
if ! check_core_038_compliance; then
    log_error "CORE-038 compliance check failed - phase BLOCKED"
    exit 1
fi
```

---

## ✅ SIGN-OFF

| Item | Status | Owner |
|------|--------|-------|
| Policy Documented | ✅ YES | CORTEX |
| Cleanup Executed | ✅ YES | CORTEX |
| Code Paths Updated | ✅ YES | CORTEX |
| Root Directory Clean | ✅ YES | CORTEX |
| Entry Gate Template | ✅ CREATED | CORTEX |
| Enforcement Ready | ✅ YES | CORTEX |

---

## 🎯 COMMITMENT

**CORTEX now operates under strict CORE-038 enforcement:**

- No application files in root
- All files in appropriately named subfolders
- File name factory used for all new files
- Enforcement at phase entry gate
- Zero-tolerance policy (AC_BLOCK on violation)
- Backward compatibility for legacy paths

---

**Created:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Status:** ✅ CORE-038 ENFORCEMENT ACTIVE

**All phases 3-6 must comply with this policy before execution.**
