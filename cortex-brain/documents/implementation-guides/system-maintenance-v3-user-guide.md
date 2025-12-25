# System Maintenance v3 User Guide

**Version:** 3.0  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Last Updated:** December 25, 2025  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

**System Maintenance v3** is CORTEX's automated health and optimization orchestrator that performs 7-phase maintenance workflows to keep your CORTEX installation running at peak performance.

**Key Innovation:** Intelligent auto-fix with tiered routing - detects and resolves common issues automatically, escalating complex problems with actionable remediation plans.

---

## 🚀 Quick Start

### Run Complete Maintenance

```bash
# In Copilot Chat or terminal
system maintenance
```

**What happens:**
1. **Pre-Healthcheck** - Scans 32+ components, establishes baseline
2. **Align** - Auto-fixes misalignments using Planning System 3.0 tiered routing
3. **Cleanup** - Organizes files, updates references, removes duplicates
4. **Optimize** - Compresses tokens, clears caches, optimizes performance
5. **Vacuum** - Compacts SQLite databases, AST cleanup
6. **Refresh Prompts** - Regenerates `.github/prompts/` from truth sources
7. **Post-Healthcheck** - Validates improvements, calculates delta

**Duration:** 2-10 minutes (depending on project size)

**Output:** Health report + completion summary with metrics

---

## 📊 The 7-Phase Workflow

### Phase 1: Pre-Healthcheck (Baseline)

**Purpose:** Establish system health baseline before changes

**Checks 32+ Components:**

| Category | Components | Example Checks |
|----------|------------|----------------|
| **File System** | 8 | Directory structure, file counts, disk usage |
| **Databases** | 6 | SQLite integrity, connection tests, size metrics |
| **Git** | 4 | Repository status, uncommitted changes, branch info |
| **Configuration** | 5 | cortex.config.json, YAML manifests, version sync |
| **Dependencies** | 4 | Python packages, missing imports, version conflicts |
| **Documentation** | 3 | Broken links, outdated content, completeness |
| **Tests** | 2 | Test pass rate, coverage percentage |

**Example Output:**
```markdown
## 🏥 Pre-Healthcheck Results

### Overall Health: 87/100 (GOOD)

**File System:** ✅ HEALTHY (100/100)
- Directory structure: ✅ Valid
- File count: 3,262 markdown files
- Disk usage: 2.3 GB / 50 GB (5%)

**Databases:** ⚠️ WARNING (75/100)
- cortex-brain.db: ✅ Valid (42.5 MB)
- conversation-history.db: ⚠️ Fragmented (150 MB, 40% overhead)
- cortex_status.db: ✅ Valid (1.2 MB)

**Git Repository:** ✅ HEALTHY (95/100)
- Branch: CORTEX-4.0
- Uncommitted changes: 2 files
- Last commit: 5 minutes ago

**Configuration:** ✅ HEALTHY (100/100)
- cortex.config.json: ✅ Valid
- Version sync: ✅ All modules 4.0.0

**Dependencies:** ⚠️ WARNING (80/100)
- Python 3.9.6: ✅ Compatible
- Missing packages: 0
- Outdated packages: 3 (pytest, mypy, black)

**Tests:** ✅ HEALTHY (97/100)
- Pass rate: 97.6% (2,811/2,879 tests)
- Coverage: 14.11%
```

**Duration:** 30-60 seconds

---

### Phase 2: Align (Auto-Fix with Tiered Routing)

**Purpose:** Automatically fix common issues, escalate complex problems

**Intelligence:** Uses **Planning System 3.0 tiered routing** to classify fixes:

| Tier | Complexity | Execution | Example Issues |
|------|------------|-----------|----------------|
| **1 - INSTANT** | <2s | Auto-fix | Formatting, imports, broken symlinks |
| **2 - LIGHTWEIGHT** | <10s | Auto-fix | File organization, reference updates |
| **3 - STANDARD** | <60s | Auto-fix + validation | Configuration sync, dependency updates |
| **4 - COMPLEX** | >60s | Manual review | Architecture changes, breaking changes |

**Auto-Fix Capabilities:**

1. **File System Issues**
   - ✅ Missing directories → Create automatically
   - ✅ Broken symlinks → Recreate or remove
   - ✅ Duplicate files → Deduplicate with verification
   - ✅ Incorrect permissions → Restore defaults

2. **Configuration Issues**
   - ✅ Version mismatches → Synchronize from cortex.config.json
   - ✅ Invalid YAML → Fix syntax errors
   - ✅ Missing keys → Add with default values
   - ✅ Path inconsistencies → Update to absolute paths

3. **Git Issues**
   - ✅ Uncommitted changes → Checkpoint (with backup)
   - ✅ Merge conflicts → Detect and report (manual resolution)
   - ✅ Detached HEAD → Return to branch

4. **Dependency Issues**
   - ✅ Missing packages → Install via pip
   - ✅ Outdated packages → Upgrade (with compatibility check)
   - ✅ Conflicting versions → Resolve with latest compatible

**Example Execution:**
```markdown
## 🔧 Align Phase Results

### Auto-Fixes Applied: 8

✅ **File System**
- Created missing directory: cortex-brain/documents/reports/ (Tier 1, <1s)
- Removed broken symlink: docs/api/legacy → api-docs/ (Tier 1, <1s)

✅ **Configuration**
- Synchronized version: src/core/version.py 3.9.0 → 4.0.0 (Tier 2, 5s)
- Fixed YAML syntax: cortex-operations.yaml line 42 (Tier 1, <1s)

✅ **Dependencies**
- Installed missing package: pytest-asyncio 0.24.0 (Tier 2, 8s)
- Upgraded package: mypy 1.0.0 → 1.8.0 (Tier 3, 12s)

⚠️ **Manual Review Required: 2**

❌ **Git Conflict** (Tier 4)
- File: src/orchestrators/planning/planning_orchestrator.py
- Issue: Merge conflict (branch: CORTEX-4.0)
- Remediation: Run `git mergetool` and resolve manually

❌ **Architecture Change** (Tier 4)
- File: cortex-operations.yaml
- Issue: 5 operations missing execution_method classification
- Remediation: See CLI-WRAPPER-PHASE-3-4-COMPLETION.md for guidance
```

**Rollback Safety:**
- ✅ Git checkpoint created before changes
- ✅ Backup files stored in `cortex-brain/backups/align-[timestamp]/`
- ✅ Rollback command: `git reset --hard [checkpoint-id]`

**Duration:** 1-3 minutes

---

### Phase 3: Cleanup (File Organization)

**Purpose:** Organize workspace, remove duplicates, update references

**Cleanup Operations:**

1. **File Organization**
   - ✅ Move misplaced docs: Root → `cortex-brain/documents/[category]/`
   - ✅ Archive old reports: `reports/` → `archive/reports-[date]/`
   - ✅ Organize test files: Separate CORTEX tests (`tests/`) vs app tests (user repo)

2. **Duplicate Detection & Removal**
   - ✅ Scan for duplicate files (content hash comparison)
   - ✅ Keep newest version, archive duplicates
   - ✅ Update references to point to canonical file

3. **Reference Updates**
   - ✅ Fix broken imports: Update file paths after moves
   - ✅ Update documentation links: Adjust relative paths
   - ✅ Synchronize manifest references: Reflect new file locations

4. **Obsolete File Cleanup**
   - ✅ Remove empty directories
   - ✅ Delete `.pyc` files, `__pycache__` directories
   - ✅ Clean up temporary files (`*.tmp`, `*.log.old`)

**Example Output:**
```markdown
## 🧹 Cleanup Phase Results

### Files Organized: 12
- Moved: CORTEX/summary.md → cortex-brain/documents/summaries/cortex-summary.md
- Moved: test_utils.py → tests/utils/test_utils.py
- Archived: old_report.md → archive/reports-2025-12/old_report.md

### Duplicates Removed: 5
- planning-orchestrator.md (3 copies) → Kept latest in documents/architecture/
- test_base_orchestrator.py (2 copies) → Kept version in tests/orchestrators/

### References Updated: 18
- Updated imports: 8 files
- Updated doc links: 10 markdown files

### Obsolete Files Removed: 23
- Empty directories: 3
- __pycache__: 15 directories
- Temporary files: 5 (.log.old, .tmp)
```

**Safety:**
- ✅ Backup created: `cortex-brain/backups/cleanup-[timestamp]/`
- ✅ Dry-run mode available: `system maintenance --dry-run` (shows changes without applying)

**Duration:** 1-2 minutes

---

### Phase 4: Optimize (Performance Tuning)

**Purpose:** Compress tokens, clear caches, optimize performance

**Optimization Strategies:**

1. **Token Compression (95% Reduction)**
   - ✅ Split large plans: >20KB → index + modules
   - ✅ Extract common patterns: Reusable YAML fragments
   - ✅ Remove redundant metadata: Keep only active fields

2. **Cache Cleanup**
   - ✅ Clear Brain Tier 1 cache (70-conversation FIFO)
   - ✅ Vacuum SQLite WAL files
   - ✅ Delete expired session data
   - ✅ Prune old conversation captures (>90 days)

3. **Performance Profiling**
   - ✅ Identify slow operations (>1s execution)
   - ✅ Generate optimization recommendations
   - ✅ Track performance trends

**Example Output:**
```markdown
## ⚡ Optimize Phase Results

### Token Compression
- Plans optimized: 12 → 95% token reduction
  - 00-MASTER-PLAN.md: 42KB → 1.2KB (index only)
  - phase-08-testing-validation.md: 28KB → 2.5KB
- Total savings: 520KB → 26KB (95% reduction)

### Cache Cleanup
- Tier 1 cache: 150 conversations → 70 (FIFO purge)
- SQLite WAL: 42 MB → 0 MB (vacuumed)
- Session data: 500 entries → 120 (expired purged)
- Conversation captures: 200 files → 80 (>90 days deleted)

### Performance Analysis
- Slow operations detected: 3
  1. grep_search with max_results=5000 (avg 2.5s) → Recommend max_results=1000
  2. semantic_search without filters (avg 1.8s) → Recommend file path filters
  3. list_dir recursive on root (avg 1.2s) → Recommend target subdirectories

### Disk Space Recovered
- Before: 2.8 GB
- After: 2.1 GB
- Savings: 700 MB (25%)
```

**Duration:** 30-90 seconds

---

### Phase 5: Vacuum (Database Compaction)

**Purpose:** Compact SQLite databases, AST cleanup, reclaim space

**Vacuum Operations:**

1. **SQLite Database Compaction**
   - ✅ VACUUM command: Rebuilds database files
   - ✅ Reclaims unused space (deleted records)
   - ✅ Optimizes query performance (defragmentation)

2. **AST Cleanup**
   - ✅ Remove orphaned AST nodes
   - ✅ Reindex code structures
   - ✅ Validate syntax trees

3. **Index Optimization**
   - ✅ Rebuild database indexes
   - ✅ Update query plans
   - ✅ Analyze table statistics

**Example Output:**
```markdown
## 🗜️ Vacuum Phase Results

### SQLite Databases Compacted: 6

**cortex-brain.db**
- Before: 42.5 MB
- After: 38.2 MB
- Savings: 4.3 MB (10%)

**conversation-history.db**
- Before: 150 MB (40% fragmented)
- After: 90 MB
- Savings: 60 MB (40%) ✅ HIGH IMPACT

**cortex_status.db**
- Before: 1.2 MB
- After: 1.0 MB
- Savings: 200 KB (17%)

### AST Cleanup
- Orphaned nodes removed: 45
- Syntax trees validated: 1,247 files
- Reindexing complete: ✅ All code structures current

### Performance Impact
- Query speed improvement: 15-25% faster
- Disk I/O reduction: 30% fewer seeks
```

**Duration:** 30-60 seconds

---

### Phase 6: Refresh Prompts (Regeneration)

**Purpose:** Regenerate `.github/prompts/` from truth sources

**Regeneration Process:**

1. **Load Truth Sources**
   - `cortex-brain/TRUTH-SOURCES.yaml` (master configuration)
   - Operation manifests (`cortex-operations.yaml`)
   - Response templates (`response-templates-v4.yaml`)
   - Brain protection rules (`brain-protection-rules.yaml`)

2. **Generate Prompts**
   - `CORTEX.prompt.md` - Universal entry point
   - Module guides (planning, TDD, sanitization, etc.)
   - Response format specifications

3. **Validate Consistency**
   - ✅ Cross-reference manifests
   - ✅ Verify command documentation
   - ✅ Check for outdated references

**Example Output:**
```markdown
## 🔄 Refresh Prompts Results

### Prompts Regenerated: 8

✅ **.github/prompts/CORTEX.prompt.md**
- Source: TRUTH-SOURCES.yaml + cortex-operations.yaml
- Changes: Updated Phase 8 completion status (90% → 100%)
- Validation: ✅ All 62 operations documented

✅ **modules/planning-orchestrator-guide.md**
- Source: planning-system-4.0-manifest.yaml
- Changes: Added DoR/DoD compliance section
- Validation: ✅ All 4 complexity tiers documented

✅ **modules/tdd-mastery-guide.md**
- Source: tdd-orchestrator-v4-manifest.yaml
- Changes: Updated with v4.0 adaptive learning features
- Validation: ✅ RED→GREEN→REFACTOR workflow complete

### Validation Results
- Cross-reference check: ✅ PASS (0 inconsistencies)
- Command documentation: ✅ PASS (all commands have examples)
- Outdated references: ✅ PASS (0 found)
```

**Duration:** 15-30 seconds

---

### Phase 7: Post-Healthcheck (Validation)

**Purpose:** Validate improvements, calculate delta, generate report

**Validation Process:**

1. **Re-run Health Checks** (same 32+ components as Phase 1)
2. **Calculate Delta** (Before vs After)
3. **Generate Report** (Improvements, remaining issues, recommendations)

**Example Output:**
```markdown
## 🎉 Post-Healthcheck Results

### Overall Health: 87/100 → 95/100 (+8 points)

**Improvements:**

✅ **File System:** 100/100 (no change)
- All directories valid
- 12 files organized ✅

✅ **Databases:** 75/100 → 95/100 (+20 points)
- conversation-history.db: 40% fragmented → 0% (vacuumed)
- All databases compacted: 193.7 MB → 129.2 MB (33% savings)

✅ **Git Repository:** 95/100 → 98/100 (+3 points)
- Uncommitted changes: 2 → 0 (checkpoint created)

✅ **Configuration:** 100/100 (no change)
- All versions synchronized

✅ **Dependencies:** 80/100 → 95/100 (+15 points)
- Outdated packages: 3 → 0 (all upgraded)

✅ **Tests:** 97/100 (no change)
- Pass rate: 97.6% (2,811/2,879)

### Remaining Issues: 2 (Manual Review Required)

⚠️ **Git Conflict** (Phase 2 escalation)
- File: src/orchestrators/planning/planning_orchestrator.py
- Action: Run `git mergetool`

⚠️ **Low Test Coverage** (Informational)
- Current: 14.11%
- Target: 80%+
- Recommendation: See Phase 8 Task 8.2 (Unit Test Expansion)

### Performance Gains
- Disk space: 2.8 GB → 2.1 GB (700 MB saved, 25%)
- Database size: 193.7 MB → 129.2 MB (64.5 MB saved, 33%)
- Query performance: +15-25% faster
- Token usage: 520KB → 26KB (95% reduction)
```

**Duration:** 30-60 seconds

---

## 🎯 Execution Modes

### 1. Standard Mode (Default)

```bash
system maintenance
```

**Behavior:**
- Executes all 7 phases sequentially
- Auto-fixes Tier 1-3 issues
- Escalates Tier 4 issues with remediation plans
- Skips non-critical phases on failures

---

### 2. Dry-Run Mode

```bash
system maintenance --dry-run
```

**Behavior:**
- Shows what WOULD be done (no changes applied)
- Useful for reviewing before execution
- Generates preview report

**Example Output:**
```markdown
## 🔍 Dry-Run Results

### Planned Changes (No changes applied)

**Phase 2 (Align):**
- Would create: cortex-brain/documents/reports/
- Would synchronize: 3 version mismatches
- Would install: pytest-asyncio 0.24.0

**Phase 3 (Cleanup):**
- Would move: 12 files
- Would remove: 5 duplicates
- Would update: 18 references

**Phase 4 (Optimize):**
- Would compress: 12 plans (520KB → 26KB)
- Would clear: Tier 1 cache (80 conversations)

**Phase 5 (Vacuum):**
- Would compact: 6 databases (193.7 MB → ~130 MB)

**Total Impact:**
- Disk savings: ~700 MB
- Files organized: 12
- Performance gain: +15-25%
```

---

### 3. Selective Phase Execution

```bash
# Run specific phases only
system maintenance --phases align,cleanup

# Skip specific phases
system maintenance --skip vacuum,refresh-prompts
```

**Use cases:**
- Quick fixes: `--phases align` (auto-fix only)
- Space recovery: `--phases vacuum` (database compaction only)
- Organization: `--phases cleanup` (file organization only)

---

### 4. Automated Scheduling

```bash
# Setup cron job (runs daily at 2 AM)
crontab -e

# Add line:
0 2 * * * cd /Users/asifhussain/PROJECTS/CORTEX && system maintenance --automated
```

**`--automated` Flag:**
- Runs silently (minimal output)
- Logs to `logs/maintenance-[date].log`
- Sends notification on critical failures
- Generates weekly summary report

---

## 🛠️ Troubleshooting

### Issue: Maintenance fails in Phase 2 (Align)

**Symptoms:** Auto-fix errors, rollback triggered

**Solutions:**
1. Check logs: `tail -f logs/cortex.log`
2. Review checkpoint: `git log --oneline -5`
3. Manual rollback: `git reset --hard [checkpoint-id]`
4. Re-run with dry-run: `system maintenance --dry-run` to preview
5. Skip phase: `system maintenance --skip align` (fix manually later)

---

### Issue: Databases not compacting (Phase 5)

**Symptoms:** "VACUUM failed" error

**Solutions:**
1. Check database locks: `lsof | grep cortex-brain.db`
2. Close connections: Stop running CORTEX processes
3. Repair database: `sqlite3 cortex-brain.db "PRAGMA integrity_check;"`
4. Re-run vacuum: `system maintenance --phases vacuum`

---

### Issue: Prompts not regenerating (Phase 6)

**Symptoms:** "Source file not found" error

**Solutions:**
1. Verify truth sources exist: `ls cortex-brain/TRUTH-SOURCES.yaml`
2. Check manifest validity: `python -c "import yaml; yaml.safe_load(open('cortex-operations.yaml'))"`
3. Manual regeneration: `python scripts/regenerate_prompts.py`

---

## 📊 Performance Benchmarks

| Project Size | Duration | Disk Savings | DB Compression | Performance Gain |
|--------------|----------|--------------|----------------|------------------|
| **Small** (<1K files) | 2-3 min | 200-500 MB | 20-30% | +10-15% |
| **Medium** (1-5K files) | 3-5 min | 500-1000 MB | 30-40% | +15-25% |
| **Large** (>5K files) | 5-10 min | 1-2 GB | 40-50% | +25-35% |

**CORTEX Repository Metrics:**
- **Files:** 3,262 markdown + 1,247 Python
- **Duration:** 5-7 minutes
- **Disk Savings:** 700 MB (25%)
- **DB Compression:** 64.5 MB (33%)
- **Performance Gain:** +15-25%

---

## 🎓 Best Practices

### ✅ DO

1. **Run weekly:** Schedule maintenance every Sunday at 2 AM
2. **Dry-run first:** Use `--dry-run` before major changes
3. **Check health:** Review post-healthcheck report for trends
4. **Backup before:** Maintenance creates automatic backups, but extra safety never hurts
5. **Monitor performance:** Track query speed improvements over time

### ❌ DON'T

1. **Run during active development:** Wait for commit checkpoint
2. **Interrupt mid-phase:** Can leave system in inconsistent state
3. **Skip phases repeatedly:** Issues compound over time
4. **Ignore Tier 4 escalations:** Manual review required for complex fixes
5. **Run multiple instances:** Can cause database locks

---

## 📚 Related Documentation

- **Architecture:** `cortex-brain/documents/archive/system-maintenance-architecture-completion.md`
- **Planning System 3.0:** `cortex-brain/documents/implementation-guides/planning-system-2.0-user-guide.md`
- **Tiered Routing:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
- **CLI Wrappers:** `cortex-brain/documents/reports/CLI-WRAPPER-PHASE-3-4-COMPLETION.md`

---

## 🔮 Future Enhancements (CORTEX 5.0)

- **Predictive Maintenance** - AI predicts failures before they occur
- **Real-Time Monitoring** - Live health dashboard with alerts
- **Multi-Workspace Optimization** - Coordinate maintenance across all workspaces
- **Performance Profiling** - Deep dive into bottlenecks with flame graphs
- **Automated Upgrades** - Self-updating CORTEX with rollback safety

---

**Document Version:** 1.0.0  
**Status:** ✅ PRODUCTION  
**Next Update:** v3.1 with Predictive Maintenance (CORTEX 5.0)
