# CORTEX Documentation Index

## 📚 Documentation Structure

All documentation has been reorganized and archived under `docs/_archive/` for cleaner repository root.

### 📁 Organized Categories

#### `phases/` - Phase Completion Reports
Phase-specific documentation including progress, completion, and readiness reports:
- Phase 02: Codebase coherence (latest)
- Phase 03-05: Completion summaries
- Phase remediation: Issue fixes and learnings

#### `ac-reports/` - Acceptance Criteria
Detailed AC documentation and implementations:
- AC-AR-010: Design, migration, imports
- AC-BRITTLE: Brittleness analysis and fixes
- Implementation tracking and completion records

#### `analyses/` - Technical Analysis
Deep dives into technical issues and solutions:
- Race condition analysis and fixes
- Hanging condition isolation reports
- Investigation summaries

#### `summaries/` - Plans & Designs
Strategic and technical documentation:
- FOLDER_STRUCTURE_DESIGN: The unified cortex/ architecture
- MIGRATION_PLAN: 4-phase migration strategy
- Implementation guides and roadmaps
- Gap remediation audits

### 🗂️ File Organization Quick Reference

| File | Category | Purpose |
|------|----------|---------|
| `FOLDER_STRUCTURE_DESIGN.md` | Design | Unified cortex/ structure rationale |
| `MIGRATION_PLAN.md` | Design | Migration strategy and approach |
| `PHASE-0X-*.md` | Phases | Phase-specific documentation |
| `*-ANALYSIS.md` | Analysis | Technical problem investigation |
| `*-REPORT.md` | Summaries | Completion and status reports |

### 📝 Key Documents by Purpose

#### Getting Started
- `README.md` (root) - Start here
- `START-HERE.md` - Quick navigation guide
- `QUICK-START-*.md` - Phase-specific quick starts

#### Architecture & Design
- `PROJECT-OVERVIEW-AND-VISION.md` - Long-term vision
- `FOLDER_STRUCTURE_DESIGN.md` - Current structure rationale
- `CONSOLIDATED-IMPLEMENTATION-ROADMAP.md` - Full roadmap

#### Phase Progress
- `PHASE-02-CODEBASE-COHERENCE-COMPLETION.md` - Latest phase lock
- `PHASE-02-AUTONOMOUS-COMPLETION-REPORT.md` - Full completion report
- `PHASE-03-PROGRESS.md` - Next phase status

#### Technical References
- `BEFORE-AFTER-COMPARISON.md` - Structure changes visualization
- `DETAILED-AC-INVENTORY.md` - Complete AC catalog
- `CORTEX-MASTER-YAML-CONSOLIDATION-SUMMARY.md` - Config consolidation

### 🔍 Finding Documentation

**By Phase**: Check `docs/_archive/phases/`
```bash
ls docs/_archive/phases/PHASE-0*.md
```

**By Issue**: Check `docs/_archive/analyses/`
```bash
ls docs/_archive/analyses/*-ANALYSIS.md
```

**By Topic**: Search across all docs
```bash
grep -r "topic" docs/_archive/
```

### 📊 Documentation Statistics

- **Total files**: 50+ markdown files
- **Total lines**: 50,000+ lines of documentation
- **Categories**: 4 major categories
- **Coverage**: Complete project lifecycle documentation

### 🚀 Scripts Reference

All scripts have been organized in `scripts/`:

#### `scripts/maintenance/`
- `migrate_folder_structure.py` - Migration automation
- `update_imports.py` - Import path updates
- `log_*.py`, `record_*.py` - Audit and logging

#### `scripts/validation/`
- `validate_phase_sync.py` - Phase consistency
- `validate_phase_deliverables.py` - Delivery validation
- `check_*.py` - Various checks

#### `scripts/deployment/`
- `verify_orchestrator_readiness.sh` - Deployment verification
- `pre-push-check.sh` - Pre-push validation

#### `scripts/utilities/`
- `launch-dashboard.py` - Dashboard launcher
- `dashboard-health-check.py` - Health monitoring
- `run-cortex-vacuum.py` - Maintenance automation

### 📎 Related Files

- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration
- `.pre-commit-config.yaml` - Git hooks configuration

### ⚙️ Maintenance

**To add new documentation**:
1. Create in `docs/_archive/` under appropriate category
2. Update this index if creating new category
3. Consider which developers need this doc

**To reorganize**:
1. Move files to appropriate `docs/_archive/` subfolder
2. Update links in related documentation
3. Commit with clear message about reorganization

---

**Last Updated**: 2026-01-18  
**Archive Created**: Phase 02 Completion  
**Status**: Fully organized and indexed
