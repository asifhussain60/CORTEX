# Planning Artifacts Organization System - Migration Guide

**Plan ID:** PLAN-2025-12-13-planning-artifacts-organization  
**Version:** 2.0.0  
**Date:** December 14, 2025  
**Author:** Asif Hussain

---

## 🎯 Purpose

Complete migration guide for reorganizing planning artifacts into hierarchical folder structure. **Simplified Git-based migration** with feature flag control and instant Git rollback capability.

---

## 📊 Complete Artifact Inventory

### Planning Documents to Migrate (323 files)
```
cortex-brain/documents/planning/
├── features/
│   ├── active/         → 15 files (YAML + MD)
│   ├── completed/      → 50 files
│   ├── archived/       → 230 files
│   ├── ado/            → 10 files
│   ├── orchestrators/  → 8 files
│   └── cortex-4.0/     → 10 files
├── Root-level plans/   → 15 files (need migration)
└── Sub-directories     → Various
```

### Cortex-Brain Root Files (47 files - KEEP IN PLACE)
**System Configuration (19 files):**
- `brain-protection-rules.yaml` ✅ KEEP
- `capabilities.yaml` ✅ KEEP
- `cleanup-rules.yaml` ✅ KEEP
- `compliance-tracking-schema.sql` ✅ KEEP
- `development-context.yaml` ✅ KEEP
- `doc-generation-rules.yaml` ✅ KEEP
- `file-relationships.yaml` ✅ KEEP
- `git-checkpoint-rules.yaml` ✅ KEEP
- `knowledge-graph.yaml` ✅ KEEP
- `lessons-learned.yaml` ✅ KEEP
- `module-definitions.yaml` ✅ KEEP
- `multilingual-templates.yaml` ✅ KEEP
- `operations-config.yaml` ✅ KEEP
- `publish-config.yaml` ✅ KEEP
- `reconciliation-config.yaml` ✅ KEEP
- `refactoring-rules.yaml` ✅ KEEP
- `response-*.yaml` (5 files) ✅ KEEP
- `schema.sql` ✅ KEEP
- `self-review-checklist.yaml` ✅ KEEP
- `token-optimization-rules.yaml` ✅ KEEP
- `TRUTH-SOURCES.yaml` ✅ KEEP
- `user-dictionary.yaml` ✅ KEEP

**System Databases (2 files):**
- `cortex-brain.db` ✅ KEEP
- `sessions.db` ✅ KEEP

**Quick Reference Guides (6 files - RELOCATE):**
- `CLEANUP-QUICK-REF.md` → `documents/quick-refs/`
- `DOCUMENT-CONVERTER-QUICK-REF.md` → `documents/quick-refs/`
- `HOLISTIC-DISCOVERY-QUICK-REF.md` → `documents/quick-refs/`
- `INLINE-CSS-PROHIBITION-QUICK-REF.md` → `documents/quick-refs/`
- `INTELLIGENT-TDD-QUICK-REF.md` → `documents/quick-refs/`
- `LAYER-8-QUICK-REF.md` → `documents/quick-refs/`
- `MASTER-PLANNER-VISUAL-TRACKER-QUICK-REF.md` → `documents/quick-refs/`
- `SUCCESS-TEMPLATE-USAGE-GUIDE.md` → `documents/quick-refs/`
- `README-ORGANIZATION.md` → `documents/quick-refs/`

**Planning Configs (1 file - MIGRATE):**
- `track-integration-plan.json` → Migrate to planning folder

**System Scripts (1 file):**
- `migrate_brain_db.py` ✅ KEEP

**Reports/Logs (3 files - RELOCATE):**
- `CLEANUP-DRY-RUN-REPORT.json` → `cleanup-reports/`
- `MILESTONE-0-BASELINE-COMPLETE.txt` → `documents/reports/milestones/`
- `obsolete-tests-manifest.json` → `documents/reports/`

**Temp/Cache Files (4 files):**
- `.platform_state.json` ✅ KEEP
- `conversation-context.jsonl` ✅ KEEP
- `hybrid-capture-simulation-results.json` → `analytics/`
- `knowledge-graph.yaml.lock` ✅ KEEP
- `mkdocs-refresh-config.yaml` → `config/`

### CORTEX Root Files (Analysis)
**Keep in Root:**
- `README.md` ✅ KEEP (project README)
- `CHANGELOG.md` ✅ KEEP (version history)
- `requirements.txt` ✅ KEEP (Python deps)
- `LICENSE` ✅ KEEP
- `pytest.ini` ✅ KEEP
- `cortex.config.json` ✅ KEEP
- `cortex.config.template.json` ✅ KEEP
- `cortex-operations.yaml` ✅ KEEP
- `CORTEX.code-workspace` ✅ KEEP

**Relocate:**
- `test_output.txt` → Delete (temporary test output)
- `test_results_summary.txt` → Delete or move to `cortex-brain/test-results/`

---

## 🏗️ Target Folder Structure

```
cortex-brain/documents/planning/features/
├── active/
│   └── PLAN-{date}-{name}/              # One folder per plan
│       ├── master-plan.md               # Master plan document
│       ├── README.md                    # Plan overview/navigation
│       ├── sub-plans/                   # Phase sub-plans
│       │   ├── phase-0-{name}.md
│       │   ├── phase-1-{name}.md
│       │   └── ...
│       ├── artifacts/                   # Generated artifacts
│       │   ├── feature-tracker.md
│       │   ├── progress-tracker.md
│       │   ├── dependency-graph.mermaid
│       │   └── visual-tracker.txt
│       ├── reports/                     # Status reports
│       │   ├── status-YYYYMMDD.md
│       │   ├── completion-report.md
│       │   └── phase-reports/
│       ├── tests/                       # Test plans/results
│       │   ├── test-plan.md
│       │   └── test-results.md
│       └── checkpoints/                 # Git checkpoints
│           └── checkpoint-metadata.yaml
├── completed/
│   └── {same structure}
└── archived/
    └── {same structure}

cortex-brain/documents/quick-refs/       # NEW: Quick reference guides
└── *.md files

cortex-brain/documents/reports/milestones/  # NEW: Milestone reports
└── MILESTONE-*.txt files
```

---

## 🛡️ Migration Strategy

### Feature Flag Control
```json
// cortex.config.json
{
  "planning": {
    "use_folder_structure": true  // Enable folder structure (default)
  }
}
```

**Benefits:**
- ✅ Simple on/off toggle
- ✅ No dual-mode code complexity
- ✅ Easy testing (flip flag, test behavior)
- ✅ Clean implementation

### Git-Based Safety
```bash
# Before migration: Create Git checkpoint
git add .
git commit -m "checkpoint: before planning migration"
git tag planning-migration-$(Get-Date -Format "yyyyMMdd_HHmmss")

# Run migration
python -m src.workflows.planning_migration_cli --execute

# If issues: Instant rollback
git reset --hard planning-migration-<timestamp>
# OR
git revert <migration-commit-hash>
```

**Why Git rollback > Dual-mode:**
- ✅ **Faster:** One Git command vs maintaining dual-mode code
- ✅ **Simpler:** No fallback logic in code
- ✅ **Cleaner:** Single source of truth
- ✅ **Reliable:** Git is proven, dual-mode adds bugs
- ✅ **Zero maintenance:** No backward compatibility code to remove later
### Migration Execution
```bash
# One-shot migration with validation
python -m src.workflows.planning_migration_cli --all --dry-run   # Preview
python -m src.workflows.planning_migration_cli --all --execute   # Execute
python -m src.workflows.planning_migration_cli --validate        # Validate

# Or staged if preferred
python -m src.workflows.planning_migration_cli --scope active --execute
python -m src.workflows.planning_migration_cli --scope completed --execute
python -m src.workflows.planning_migration_cli --scope archived --execute
```

### Validation
```python
# Automated validation
class MigrationValidator:
    def validate_migration(self) -> ValidationResult:
        checks = [
            self.check_no_data_loss(),        # All files accounted for
            self.check_no_duplicates(),       # No duplicate files
            self.check_references_intact(),   # Cross-references work  
            self.check_folder_structure(),    # Correct folder layout
            self.check_git_status(),          # Clean git state
        ]
        return ValidationResult(checks)
```
### Git Rollback (Instant)
```bash
# Option 1: Reset to pre-migration state (destructive)
git reset --hard <pre-migration-commit-or-tag>

# Option 2: Revert migration commit (preserves history)
git log --oneline  # Find migration commit hash
git revert <migration-commit-hash>

# Validate rollback
python -m src.workflows.planning_migration_cli --status
```

**Rollback time: ~5 seconds** (vs hours for dual-mode code maintenance)

---

## 👥 User Machine Onboarding Guide

### Scenario: Team Member Pulls Updated Code

When you pull the latest CORTEX code with the new folder structure:

#### Option A: Automatic Migration (Recommended)
```bash
# 1. Pull latest code
git pull origin CORTEX-3.0

# 2. Run auto-migration script
python -m src.workflows.planning_migration_cli --onboard

# What it does:
# - Detects your existing planning files
# - Creates backup
# - Migrates to new folder structure
# - Validates migration
# - Reports success/issues
```

#### Option B: Fresh Start (If No Local Plans)
```bash
# 1. Pull latest code
git pull origin CORTEX-3.0

# 2. No migration needed - new plans auto-use folder structure
# Your next 'plan [feature]' command will create folder structure
```

#### Option C: Manual Migration (Power Users)
```bash
# 1. Pull latest code
git pull origin CORTEX-3.0

# 2. Review what will be migrated
python -m src.workflows.planning_migration_cli --dry-run --all

# 3. Backup your plans
python -m src.workflows.planning_migration_cli --backup-only

# 4. Migrate step-by-step
python -m src.workflows.planning_migration_cli --scope active --execute
python -m src.workflows.planning_migration_cli --scope completed --execute

# 5. Validate
python -m src.workflows.planning_migration_cli --validate all
```

### Machine-Specific Files (Preserved)
Your machine-specific data is **NOT affected**:
- ✅ `cortex.config.json` - Your local paths preserved
- ✅ `cortex-brain.db` - Your local database intact
- ✅ `sessions.db` - Your session history preserved
- ✅ `.cortex-initialized` - Your setup marker intact

### Troubleshooting

**Issue: "Planning orchestrator can't find plans"**
```bash
# Check if migration completed
python -m src.workflows.planning_migration_cli --status

# If incomplete, resume migration
python -m src.workflows.planning_migration_cli --resume
```

**Issue: "Duplicate plans detected"**
```bash
# Run duplicate detection
python -m src.workflows.planning_migration_cli --find-duplicates

# Review duplicates
# Resolve manually or use auto-resolve
python -m src.workflows.planning_migration_cli --resolve-duplicates --strategy keep_newest
```

**Issue: "Git shows many untracked files"**
```bash
# This is normal during migration
# Complete the migration, then commit:
git add cortex-brain/documents/planning/
git commit -m "feat: migrate to folder-based planning structure"
```

---

## 📋 Pre-Migration Checklist

- [ ] **Backup created** - Full backup of cortex-brain/documents/planning/
- [ ] **Git checkpoint** - Committed current state with tag
- [ ] **Tests passing** - All existing tests pass before migration
- [ ] **No uncommitted changes** - Clean git status
- [ ] **Documentation reviewed** - Understand folder structure
- [ ] **Migration manifest generated** - Know what will be migrated
- [ ] **Rollback tested** - Confirm backup can be restored

---

## 🔬 Orchestrator & Capability Validation

### Critical Orchestrators Requiring Validation

**Planning Orchestrators (3 orchestrators):**
1. **PlanningOrchestrator** - Core planning system
   - Methods: save_plan(), execute_plan_autonomously(), generate_incremental_plan()
   - Impact: Creates/reads folder structure
   - Validation: Must work with folder structure (feature flag controlled)

2. **PlanExecutionOrchestratorV2** - Plan execution engine
   - Methods: execute_plan(), load_plan()
   - Impact: Loads plans from folders
   - Validation: Must discover folder-based plans

3. **PlanExecutionOrchestrator** (Legacy)
   - Impact: Backward compatibility
   - Validation: Must still work with old plans

**Supporting Orchestrators (10 orchestrators):**
4. **TDDImplementationOrchestrator** - TDD workflow
   - Impact: Saves test plans/results to plan's tests/ folder
   - Validation: Must use plan subfolders

5. **GitCheckpointOrchestrator** - Git checkpoints
   - Impact: Saves checkpoint metadata to plan's checkpoints/ folder
   - Validation: Must integrate with folder structure

6. **DebugWorkflowOrchestrator** - Debugging assistance
   - Impact: Creates debug reports in plan's reports/
   - Validation: Must save to correct subfolder

7. **DocumentationOrchestrator** - Documentation generation
   - Impact: References plans with new paths
   - Validation: Must handle folder-based references

8. **CrossMachineContextOrchestrator** - Multi-machine sync
   - Impact: Synchronizes folder-based plans
   - Validation: Must preserve folder structure

9. **ApplicationHealthOrchestrator** - Health monitoring
   - Impact: Generates health reports with plan references
   - Validation: Must load from folder structure

10. **ASTNarrativeOrchestrator** - Code narrative generation
11. **ManagerReportOrchestrator** - Manager reports
12. **OnboardingAcknowledgmentOrchestrator** - User onboarding
13. **EnvironmentDiagnosticsOrchestrator** - Environment checks

**Workflow Modules (5 critical modules):**
14. **PlanRegistry** - Plan indexing and search
    - Impact: Scans and indexes folder-based plans
    - Validation: Must find folder-based plans efficiently

15. **PlanOrganizer** - Plan movement (active/completed/archived)
    - Impact: Moves entire folder (not just master file)
    - Validation: Must preserve folder structure

16. **DocumentOrganizer** - Document categorization
    - Impact: Recognizes folder-based plans
    - Validation: Must not duplicate files

17. **StreamingPlanWriter** - Incremental plan writing
    - Impact: Writes to folder structure
    - Validation: Must use correct paths

18. **IncrementalPlanGenerator** - Sub-plan generation
    - Impact: Creates sub-plans in sub-plans/ folder
    - Validation: Must create folder structure

### Validation Test Matrix

| Orchestrator | Create | Read | Update | Delete | Folder Aware | Feature Flag |
|--------------|--------|------|--------|--------|--------------|-------------|
| PlanningOrchestrator | ✅ Required | ✅ Required | ✅ Required | N/A | ✅ YES | ✅ YES |
| PlanExecutionV2 | N/A | ✅ Required | ✅ Required | N/A | ✅ YES | N/A |
| TDDImplementation | ✅ Required | ✅ Required | ✅ Required | N/A | ✅ YES | N/A |
| GitCheckpoint | ✅ Required | ✅ Required | N/A | N/A | ✅ YES | N/A |
| PlanRegistry | N/A | ✅ Required | N/A | N/A | ✅ YES | N/A |
| PlanOrganizer | N/A | ✅ Required | ✅ Required | N/A | ✅ YES | N/A |### Validation Workflows

**Workflow 1: Complete Planning Cycle**
```bash
# Test: Create → Execute → Complete → Archive
python -m pytest tests/integration/test_folder_structure_planning_cycle.py

# Expected:
# 1. Plan created with folder structure
# 2. Artifacts saved to subfolders (sub-plans/, artifacts/, reports/)
# 3. Plan moved to completed/ with folder intact
# 4. All references updated correctly
```

**Workflow 2: TDD Integration**
```bash
# Test: Plan with TDD → Test execution → Checkpoint
python -m pytest tests/integration/test_folder_structure_tdd_integration.py

# Expected:
# 1. Test files in plan's tests/ folder
# 2. Test results saved to tests/
# 3. Checkpoint metadata in checkpoints/
```

**Workflow 3: Feature Flag Validation**
```bash
# Test: Feature flag controls folder structure
python -m pytest tests/integration/test_folder_structure_feature_flag.py

# Expected:
# 1. Flag enabled → folder structure created
# 2. Flag disabled → flat file fallback  
# 3. Toggle flag → behavior changes correctly
# 4. Migration preserves existing flat files
```

**Workflow 4: Cross-Machine Sync**
```bash
# Test: Sync folder-based plans across machines
python -m pytest tests/integration/test_folder_structure_cross_machine.py

# Expected:
# 1. Folder structure preserved during sync
# 2. All subfolders copied correctly
# 3. References remain intact
```

### Validation Checklist

**Pre-Migration Validation:**
- [ ] PlanningOrchestrator.save_plan() creates folder structure
- [ ] Feature flag enables/disables folder structure correctly
- [ ] PlanExecutionV2 discovers folder-based plans
- [ ] PlanRegistry indexes folder-based plans
- [ ] PlanOrganizer moves complete folders
- [ ] TDD orchestrator uses plan subfolders
- [ ] Git checkpoint saves to checkpoints/
- [ ] All tests pass with folder structure

**Post-Migration Validation:**
- [ ] All 323 plans accessible
- [ ] No broken references
- [ ] Plan execution works for all plans
- [ ] TDD workflow works
- [ ] Git checkpoints work
- [ ] Cross-machine sync works
- [ ] All orchestrators function correctly
- [ ] Performance acceptable (<5s per plan operation)

**Orchestrator-Specific Tests:**
```bash
# Run orchestrator validation suite
pytest tests/orchestrators/test_planning_orchestrator_folder_structure.py -v
pytest tests/orchestrators/test_plan_execution_v2_folder_structure.py -v
pytest tests/orchestrators/test_tdd_folder_integration.py -v
pytest tests/workflows/test_plan_registry_folder_structure.py -v
pytest tests/workflows/test_plan_organizer_folder_structure.py -v

# Run full integration suite
pytest tests/integration/test_folder_structure_complete.py -v --cov
```

---

## 🧪 Post-Migration Validation

### Automated Tests
```bash
# Run full test suite
pytest tests/workflows/test_plan_folder_manager.py
pytest tests/workflows/test_planning_migration.py
pytest tests/orchestrators/test_planning_orchestrator.py

# Run integration tests
pytest tests/test_planning_organization.py -v
```

### Manual Validation
```bash
# 1. Test planning orchestrator
python -c "
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
po = PlanningOrchestrator('.')
plans = po.list_active_plans()
print(f'Found {len(plans)} active plans')
"

# 2. Test plan execution
python -c "
from src.orchestrators.plan_execution_orchestrator_v2 import PlanExecutionOrchestratorV2
peo = PlanExecutionOrchestratorV2('.')
# Should load latest plan without errors
"

# 3. Verify document organizer
python -c "
from src.workflows.document_organizer import DocumentOrganizer
from pathlib import Path
do = DocumentOrganizer(Path('cortex-brain'))
# Should recognize folder-based plans
"
```

---

## 📊 Migration Metrics

Track these metrics during migration:

| Metric | Target | Actual |
|--------|--------|--------|
| Files migrated | 323 | ___ |
| Data loss | 0 files | ___ |
| Broken references | 0 | ___ |
| Duplicate files | 0 | ___ |
| Test failures | 0 | ___ |
| Migration time | <30 min | ___ |
| Rollback time | <5 min | ___ |

---

## 🚀 Execution Timeline

### Admin/First Machine (You)
**Day 1:**
- Phase 0: Git checkpoint (5 min)
- Phase 1: Implement folder structure (2 hours)
- Phase 2: Migration system (4 hours)
- Phase 3: Vacuum & cleanup (2 hours)
- **Subtotal: ~8 hours**

**Day 2:**
- Phase 4: Testing & Validation (2 hours)
- Phase 5: Orchestrator Validation (4 hours)
- **Subtotal: ~6 hours**

**Day 3:**
- Phase 6: Migration execution (2 hours)
- Documentation updates (1 hour)
- Push to CORTEX-3.0 branch
- Team notification
- **Subtotal: ~3 hours**

**Total Admin Time: ~17 hours (2-3 days)**

**Time saved by removing dual-mode: ~4 hours**
- No dual-mode implementation (saved 2h)
- No dual-mode testing (saved 1h)
- No dual-mode documentation (saved 1h)

### Team Member Machines (Others)
**Day 4+:**
- Pull latest code (2 min)
- Run auto-migration (10 min)
- Validate (5 min)
- **Total: ~17 minutes per machine**

---

## 🔧 Implementation Files

**New Files:**
- `src/workflows/plan_folder_manager.py` - Folder structure manager
- `src/workflows/planning_artifacts_scanner.py` - Scans existing artifacts
- `src/workflows/planning_migration_engine.py` - Migration execution
- `src/workflows/planning_migration_cli.py` - CLI tool
- `src/workflows/duplicate_detector.py` - Duplicate detection
- `src/workflows/planning_vacuum.py` - Cleanup utilities

**Modified Files:**
- `src/orchestrators/planning_orchestrator.py` - Uses PlanFolderManager
- `src/workflows/plan_registry.py` - Folder-aware plan tracking
- `src/workflows/plan_organizer.py` - Folder-aware organization
- `src/workflows/document_organizer.py` - Recognizes folder plans
- 8 test files - Updated assertions

---

## 📞 Support

**Issues during migration?**
1. Check migration log: `cortex-brain/logs/migration-{timestamp}.log`
2. Run validation: `python -m src.workflows.planning_migration_cli --validate`
3. If stuck: `python -m src.workflows.planning_migration_cli --rollback`
4. Report issue with log file

**Questions?**
- Check this guide: `PLANNING-ARTIFACTS-ORGANIZATION-SYSTEM-MIGRATION-GUIDE.md`
- Check main plan: `PLANNING-ARTIFACTS-ORGANIZATION-SYSTEM.yaml`
- Contact: migration@cortex (or team channel)

---

## ✅ Success Criteria

Migration is complete when:
- ✅ All 323 planning documents organized in folders
- ✅ Zero data loss (validation passes)
- ✅ Zero broken references
- ✅ All tests passing (16 updated test files)
- ✅ Planning orchestrator works with folder structure
- ✅ Feature flag controls behavior correctly
- ✅ Plan execution works
- ✅ Git history clean (migration committed)
- ✅ Team members successfully onboarded
- ✅ Rollback tested and working (Git-based)

---

**SIMPLIFIED MIGRATION:** Feature flag controls folder structure. Git rollback provides instant recovery. No dual-mode code complexity.

---

**Version:** 2.0.0  
**Last Updated:** December 14, 2025  
**Author:** Asif Hussain
