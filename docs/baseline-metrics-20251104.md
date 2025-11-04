# KDS Baseline Metrics - Pre-Independence Migration

**Date:** November 4, 2025  
**Audit Tool:** `scripts/audit/audit-dependencies.ps1`  
**Purpose:** Baseline snapshot before KDS Independence refactoring

---

## 📊 File Statistics

| Metric | Count |
|--------|-------|
| **Total Files Scanned** | 267 |
| **Scripts (.ps1, .sh)** | 60 |
| **Documentation (.md)** | 185 |
| **Configuration (.json, .yaml)** | 22 |
| **Other** | 0 |

---

## 🚨 Dependency Issues (Current State)

### Critical Issues

| Issue Type | Count | Severity |
|------------|-------|----------|
| **Hard-Coded Paths** | 246 | 🔴 Critical |
| **Application-Specific References** | 2,153 | 🟡 High |
| **Hard-Coded Configuration** | 107 | 🟠 Medium |
| **Total Issues** | 2,506 | - |

### Files Affected

- **Files with Issues:** 137 out of 267 (51.3%)
- **Clean Files:** 130 out of 267 (48.7%)

---

## 📉 Independence Score

**Current Score:** 0/100

**Score Calculation:**
- Base Score: 100
- Path Penalty: -50 (246 hard-coded paths × 0.8, capped at 50)
- Application Penalty: -30 (2,153 app-specific refs × 0.5, capped at 30)
- Config Penalty: -20 (107 hard-coded configs × 0.3, capped at 20)
- **Final Score:** 0

**Target Score:** 95+/100

**Score Improvement Required:** +95 points

---

## 🔥 Top Offending Files

| Rank | File | Issues | Primary Concern |
|------|------|--------|-----------------|
| 1 | `context/ui-components.json` | 441 | Noor Canvas component references |
| 2 | `context/knowledge-graph.json` | 366 | Application-specific patterns |
| 3 | `context/routes.json` | 267 | Hard-coded route definitions |
| 4 | `docs/KDS-INDEPENDENCE-REVIEW.md` | 75 | Documentation examples |
| 5 | `context/database.json` | 70 | Database schema references |
| 6 | `prompts/user/kds.md` | 48 | User documentation examples |
| 7 | `docs/architecture/KDS-DESIGN-PLAN.md` | 46 | Architecture examples |
| 8 | `sessions/20251103-kds-independence-plan.json` | 40 | Session data |
| 9 | `prompts/internal/context-brain.md` | 37 | BRAIN prompt examples |
| 10 | `sessions/KDS-INDEPENDENCE-PLAN-SUMMARY.md` | 36 | Plan documentation |

---

## 🎯 Critical Patterns Detected

### Hard-Coded Paths (246 instances)

**Most Common:**
- `D:\PROJECTS\` - 180 instances
- `D:\PROJECTS\NOOR CANVAS` - 42 instances
- `D:\PROJECTS\DevProjects` - 24 instances

**Files Affected:**
- Scripts: 35 files
- Documentation: 18 files
- Configuration: 5 files

**Impact:** 
- ❌ Cannot deploy to different machines
- ❌ Cannot use in CI/CD pipelines
- ❌ Hard to test in isolated environments

### Application-Specific References (2,153 instances)

**Most Common:**
- `Noor Canvas` / `NOOR CANVAS` / `NoorCanvas` - 1,247 instances
- `HostControlPanel` - 389 instances
- `UserRegistrationLink` - 267 instances
- `session-212` - 128 instances
- `localhost:9091` - 122 instances

**Files Affected:**
- Context files: 1,144 references
- Documentation: 752 references
- BRAIN knowledge: 257 references

**Impact:**
- ❌ Cannot reuse in other projects
- ❌ Confusing for new users
- ❌ BRAIN learns application-specific patterns

### Hard-Coded Configuration (107 instances)

**Most Common:**
- `localhost:*` URLs - 68 instances
- `https://localhost:9091` - 22 instances
- `127.0.0.1:*` - 17 instances

**Impact:**
- ❌ Port conflicts on different machines
- ❌ Cannot customize for different environments
- ❌ Hard to run multiple instances

---

## 📂 Directory Analysis

### Most Independent Directories
1. `tests/Unit/` - 0 issues (clean)
2. `scripts/lib/` - 2 issues (mostly clean)
3. `templates/` - 5 issues (minimal coupling)

### Most Coupled Directories
1. `context/` - 1,144 issues (extreme coupling)
2. `docs/` - 387 issues (heavy examples)
3. `sessions/` - 203 issues (application data)
4. `prompts/` - 178 issues (documentation coupling)
5. `scripts/` - 156 issues (path hardcoding)

---

## 🔍 Detailed Breakdown by Category

### Scripts (60 files, 156 issues)

**Top Issues:**
- Path resolution: 89 instances
- Application references: 42 instances
- Configuration: 25 instances

**Files Needing Refactoring:**
- `brain-amnesia.ps1` - 12 paths
- `collect-development-context.ps1` - 8 paths
- `migrate-kds-to-new-repo.ps1` - 15 paths
- `run-migration.ps1` - 1 path
- `setup-v6-brain-structure.ps1` - 7 paths
- `validate-kds-references.ps1` - 1 path

### Documentation (185 files, 1,139 issues)

**Top Issues:**
- Example code: 687 instances
- File paths: 289 instances
- Application names: 163 instances

**Files Needing Updates:**
- `kds.md` - 48 references
- `KDS-DESIGN-PLAN.md` - 46 references
- `KDS-INDEPENDENCE-REVIEW.md` - 75 references
- Architecture docs: 187 references

### Configuration (22 files, 1,211 issues)

**Top Issues:**
- Context files: 1,144 instances (ui-components, routes, database, knowledge-graph)
- Config files: 45 instances
- Template files: 22 instances

**Files Needing Migration:**
- `ui-components.json` - 441 refs → Extract to integration
- `knowledge-graph.json` - 366 refs → Template-based
- `routes.json` - 267 refs → Extract to integration
- `database.json` - 70 refs → Extract to integration

---

## 📋 Migration Impact Assessment

### Phase 0: Pre-Flight (Current)
- ✅ Audit complete
- ✅ Mock project created
- ⏳ Baseline documented (in progress)
- ⬜ Backup strategy

### Phase 1: Dynamic Path Resolution
- **Files to Modify:** 60 scripts
- **Hard-Coded Paths to Fix:** 246
- **Estimated Impact:** High (all scripts will change)

### Phase 2: BRAIN Abstraction
- **Files to Modify:** 5 context files
- **Patterns to Extract:** 2,153
- **Estimated Impact:** Critical (knowledge graph restructure)

### Phase 3: Configuration Templates
- **Files to Convert:** 22 configs
- **Templates to Create:** 15
- **Estimated Impact:** Medium (new files created)

### Phase 4: Setup Wizard
- **New Files:** 3 scripts
- **Detection Logic:** Project type detection
- **Estimated Impact:** Low (new functionality)

### Phase 5: Documentation
- **Files to Update:** 185 docs
- **Examples to Generalize:** 687
- **Estimated Impact:** High (all docs will change)

### Phase 6: Git Workflow
- **Files to Update:** 2 hooks
- **Configuration Changes:** Branch name
- **Estimated Impact:** Low

### Phase 7: Integration Testing
- **Test Projects:** 2 (mock .NET + React)
- **Test Scripts:** 2
- **Estimated Impact:** Medium (validation phase)

---

## 📈 Success Metrics (Targets)

| Metric | Current | Target | Change Required |
|--------|---------|--------|-----------------|
| Independence Score | 0 | 95+ | +95 |
| Hard-Coded Paths | 246 | 0 | -246 |
| App-Specific Refs | 2,153 | 0 (default) | -2,153 |
| Files with Issues | 137 | <10 | -127 |
| Setup Time | N/A | <5 min | New feature |
| Project Types Supported | 1 (Noor Canvas) | 3+ | +2 |

---

## 🚀 Estimated Effort

Based on the baseline metrics:

| Phase | Files | Issues | Hours |
|-------|-------|--------|-------|
| 0 | 4 new | N/A | 2.5 ✅ |
| 1 | 60 | 246 paths | 3.0 |
| 2 | 5 | 2,153 refs | 3.5 |
| 3 | 22 | 107 configs | 2.5 |
| 4 | 3 new | N/A | 3.5 |
| 5 | 185 | 687 examples | 2.5 |
| 6 | 2 | Minor | 1.0 |
| 7 | 2 new | N/A | 2.5 |
| **Total** | **283** | **3,193** | **21.0** |

**Revised Estimate:** 21 hours (was 18.5)  
**Timeline:** 3-5 days

---

## 🔄 Comparison Template

After migration completion, re-run audit and compare:

```powershell
# Re-run audit
.\scripts\audit\audit-dependencies.ps1 -OutputPath "reports\audit\post-migration-audit.json"

# Compare results
$baseline = Get-Content "reports\audit\audit-report-20251104-085441.json" | ConvertFrom-Json
$postMigration = Get-Content "reports\audit\post-migration-audit.json" | ConvertFrom-Json

# Calculate improvements
$pathImprovement = $baseline.IssuesFound.HardCodedPaths.Count - $postMigration.IssuesFound.HardCodedPaths.Count
$appImprovement = $baseline.IssuesFound.ApplicationSpecific.Count - $postMigration.IssuesFound.ApplicationSpecific.Count
$scoreImprovement = $postMigration.Summary.IndependenceScore - $baseline.Summary.IndependenceScore

Write-Host "Path Issues Resolved: $pathImprovement"
Write-Host "App-Specific Resolved: $appImprovement"
Write-Host "Independence Score Change: +$scoreImprovement"
```

---

## 📝 Notes

**Key Insights:**
1. Context files (`ui-components.json`, `routes.json`) are the biggest offenders (1,144 issues)
2. These should be extracted to `integrations/noor-canvas/` package
3. Documentation has 687 examples that need generalization
4. Scripts need systematic path resolution refactoring
5. Effort estimate increased by 2.5 hours due to issue volume

**Risk Areas:**
1. BRAIN knowledge graph restructure (Phase 2) - high impact
2. Documentation updates (Phase 5) - high volume
3. Breaking changes to context files - requires Noor Canvas integration package

**Recommendations:**
1. Complete Phase 0 (backup) before starting refactoring
2. Test workspace resolver thoroughly before mass refactoring (Phase 1)
3. Keep Noor Canvas integration package well-documented
4. Run integration tests after each phase

---

**Audit Report:** `reports/audit/audit-report-20251104-085441.json`  
**Audit Summary:** `reports/audit/audit-report-20251104-085441.md`  
**Next Task:** Phase 0.4 - Create rollback strategy

---

*Generated as part of KDS Independence Project - Phase 0.3*
