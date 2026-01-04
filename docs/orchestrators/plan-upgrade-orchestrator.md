# 🔄 CORTEX Plan Upgrade Orchestrator

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Autonomous migration of legacy plans to CORTEX-5.0 standards with comprehensive validation and archiving.

---

## ✨ Features

### Automated Analysis
- ✅ Scans legacy plan structure (directory or single file)
- ✅ Extracts phases, acceptance criteria, and key content
- ✅ Identifies compliance gaps against CORTEX-5.0 standards
- ✅ Generates compliance score (0-100%)

### Intelligent Migration
- ✅ Creates CORTEX-5.0 compliant folder structure
- ✅ Generates comprehensive `00-master-plan.md`
- ✅ Adds mandatory REFACTOR phase (18+ tasks)
- ✅ Injects visual progress trackers
- ✅ Documents GIT_NO_PUSH_ENFORCEMENT
- ✅ Creates `tracking/progress-tracker.json`

### Safe Archiving
- ✅ Archives legacy plan with timestamp
- ✅ Creates archive metadata for traceability
- ✅ Optional auto-archive mode
- ✅ Manual review option before archiving

### Comprehensive Reporting
- ✅ Migration report with before/after comparison
- ✅ Compliance issue documentation
- ✅ Next steps guidance
- ✅ Full migration audit trail

---

## 📋 CORTEX-5.0 Standards Enforced

### Folder Structure
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md          # Main plan document
├── context/                    # Context artifacts
├── reports/                    # Progress reports
│   └── migration-report.md     # Auto-generated
├── artifacts/                  # Supporting files
└── tracking/                   # Progress tracking
    └── progress-tracker.json   # Auto-generated
```

### Master Plan Requirements
- ✅ Visual progress tracker (ASCII bars)
- ✅ Phase breakdown with git checkpoints
- ✅ REFACTOR phase (18+ mandatory tasks)
- ✅ GIT_NO_PUSH_ENFORCEMENT documentation
- ✅ SKULL rules section
- ✅ Acceptance criteria (AC-01, AC-02, ...)
- ✅ Dependencies section
- ✅ Success criteria section
- ✅ Reference documentation

### REFACTOR Phase (18+ Tasks)
1. **Code Quality (6):** Duplicates, structure, complexity, SOLID, dead code, smells
2. **Documentation (4):** Docstrings, comments, links, READMEs
3. **Testing (3):** Missing tests, brittle tests, coverage
4. **Performance (3):** Queries, memory leaks, response times
5. **Security (2):** Debug code, input sanitization

### Git Workflow
- ✅ Git commit after every phase
- ❌ NEVER `git push` automated
- ✅ Checkpoint format: `cortex-phase-{number}`
- ✅ User controls when to push

---

## 🚀 Usage

### Command Line

```bash
# Basic upgrade (analyze + generate)
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/old-plan/

# Auto-archive legacy plan after upgrade
python cortex-upgrade-plan.py old-plan.md --archive

# Custom output location
python cortex-upgrade-plan.py old-plan/ --output new-plan-v5/

# Specify workspace root
python cortex-upgrade-plan.py old-plan/ --workspace /path/to/CORTEX/
```

### Python API

```python
from pathlib import Path
from src.orchestrators.plan_upgrade import PlanUpgradeOrchestrator

# Initialize orchestrator
workspace = Path("/Users/username/PROJECTS/CORTEX")
orchestrator = PlanUpgradeOrchestrator(workspace)

# Analyze legacy plan
legacy_plan = workspace / "cortex-brain/documents/planning/active/old-plan"
analysis = orchestrator.analyze_legacy_plan(legacy_plan)

print(f"Compliance Score: {analysis['compliance_score']}%")
print(f"Issues: {len(analysis['compliance_issues'])}")

# Generate upgraded plan
new_plan_dir = orchestrator.generate_upgraded_plan(analysis)
print(f"New plan: {new_plan_dir}")

# Archive legacy plan (optional)
archive_path = orchestrator.archive_legacy_plan(legacy_plan)
print(f"Archived: {archive_path}")

# Full workflow (analyze + upgrade + archive)
new_plan, analysis = orchestrator.execute_upgrade(
    legacy_plan,
    auto_archive=True
)
```

---

## 📊 Analysis Output

### Compliance Scoring

| Score | Assessment | Action |
|-------|------------|--------|
| 90-100% | ✅ Excellent | Minor updates only |
| 70-89% | ⚠️ Good | Upgrade recommended |
| 50-69% | 🔶 Needs Work | Upgrade required |
| 0-49% | 🚨 Non-Compliant | Full migration required |

### Common Compliance Issues

| Issue | Impact | Auto-Fixed |
|-------|--------|------------|
| Missing subfolders | 10% | ✅ Yes |
| No 00-master-plan.md | 10% | ✅ Yes |
| Missing progress tracker | 10% | ✅ Yes |
| No REFACTOR phase | 10% | ✅ Yes |
| REFACTOR <18 tasks | 10% | ✅ Yes |
| No git checkpoints | 10% | ✅ Yes |
| <3 phases defined | 10% | ⚠️ Partial |
| No acceptance criteria | 10% | ⚠️ Partial |
| Single file (not directory) | 10% | ✅ Yes |
| No context files | 10% | ⚠️ Manual |

---

## 🔍 What Gets Extracted

### From Legacy Plans

**Automatic Extraction:**
- ✅ Plan title
- ✅ Phases (via regex pattern matching)
- ✅ Acceptance criteria (AC-01, numbered lists)
- ✅ Progress tracker existence
- ✅ REFACTOR phase presence
- ✅ Git checkpoint references
- ✅ Context files (if directory-based)

**Preserved Content:**
- ✅ Problem/context statements (first 400 chars)
- ✅ All context files copied to new structure
- ✅ Phase descriptions (first 200 chars per phase)

**Generated New Content:**
- ✅ CORTEX-5.0 metadata (plan_id, timestamps)
- ✅ Visual progress tracker (ASCII bars)
- ✅ Comprehensive REFACTOR phase (18+ tasks)
- ✅ GIT_NO_PUSH_ENFORCEMENT section
- ✅ SKULL rules table
- ✅ Git checkpoint commands
- ✅ Progress tracking JSON
- ✅ Migration report

---

## 📁 Output Structure

After upgrade, you'll have:

```
cortex-brain/documents/planning/active/plan-name-v5/
├── 00-master-plan.md                    # ✅ CORTEX-5.0 compliant
├── context/
│   └── [copied from legacy plan]
├── reports/
│   └── migration-report.md              # ✅ Auto-generated
├── artifacts/
└── tracking/
    └── progress-tracker.json            # ✅ Auto-generated

cortex-brain/documents/planning/archived/plan-name-archived-20260104_103045/
└── [legacy plan preserved]
```

---

## ⚙️ Configuration

### CORTEX-5.0 Standards (Hardcoded)

```python
CORTEX_5_STANDARDS = {
    "folder_structure": {
        "root": "cortex-brain/documents/planning/active/",
        "subfolders": ["context/", "reports/", "artifacts/", "tracking/"]
    },
    "master_plan_file": "00-master-plan.md",
    "required_sections": [
        "Progress Tracker",
        "Strategic Context",
        "Dependencies",
        "Phase Breakdown",
        "REFACTOR Phase",
        "Success Criteria",
        "Git Checkpoints"
    ],
    "refactor_phase": {
        "minimum_tasks": 18,
        "mandatory_checks": [...]  # See full list in code
    },
    "git_workflow": {
        "commits_required": True,
        "push_forbidden": True,
        "checkpoint_format": "cortex-phase-{number}-{name}"
    }
}
```

### Customization

**Adjust standards by modifying:**
- `CORTEX_5_STANDARDS` dict in `plan_upgrade_orchestrator.py`
- Template strings in `_generate_master_plan_content()`
- Compliance checks in `_check_compliance()`

---

## 🛡️ Safety Features

### Non-Destructive by Default
- ✅ Original plan untouched unless `--archive` flag used
- ✅ Archive creates timestamped backup before deletion
- ✅ Archive metadata tracks original location
- ✅ Manual review opportunity before archiving

### Validation
- ✅ Path existence checks before processing
- ✅ Compliance scoring before migration
- ✅ Generated content validated against standards
- ✅ Migration report documents all changes

### Rollback
```bash
# Restore from archive
cp -r cortex-brain/documents/planning/archived/plan-name-archived-20260104_103045/ \
      cortex-brain/documents/planning/active/plan-name/
```

---

## 🧪 Testing

### Manual Test Workflow

```bash
# 1. Create test legacy plan
mkdir -p cortex-brain/documents/planning/active/test-legacy-plan
echo "# Test Plan" > cortex-brain/documents/planning/active/test-legacy-plan/plan.md

# 2. Run upgrade
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/test-legacy-plan/

# 3. Verify output
ls -la cortex-brain/documents/planning/active/test-legacy-plan-v5/
cat cortex-brain/documents/planning/active/test-legacy-plan-v5/00-master-plan.md

# 4. Check migration report
cat cortex-brain/documents/planning/active/test-legacy-plan-v5/reports/migration-report.md

# 5. Test archive
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/test-legacy-plan/ --archive
ls -la cortex-brain/documents/planning/archived/
```

### Unit Tests (TODO)

```python
# tests/orchestrators/plan_upgrade/test_plan_upgrade_orchestrator.py

def test_analyze_directory_plan():
    """Test analysis of directory-based legacy plan."""
    pass

def test_analyze_single_file_plan():
    """Test analysis of single-file legacy plan."""
    pass

def test_compliance_scoring():
    """Test compliance score calculation."""
    pass

def test_generate_upgraded_plan():
    """Test CORTEX-5.0 plan generation."""
    pass

def test_archive_legacy_plan():
    """Test safe archiving of legacy plan."""
    pass

def test_refactor_phase_generation():
    """Test REFACTOR phase has 18+ tasks."""
    pass
```

---

## 🐛 Troubleshooting

### Issue: "Plan path not found"
**Solution:** Check path is correct and file/directory exists

### Issue: "Permission denied" during archive
**Solution:** Ensure write permissions on `cortex-brain/documents/planning/archived/`

### Issue: Generated plan missing phases
**Solution:** Legacy plan may have non-standard phase headers. Check regex patterns in `_extract_phases()`

### Issue: REFACTOR phase incomplete
**Solution:** Generated REFACTOR phase is template-based. All 18 tasks should be present by default.

### Issue: Archive directory grows too large
**Solution:** Periodically clean old archives:
```bash
# Keep only last 30 days
find cortex-brain/documents/planning/archived/ -mtime +30 -type d -exec rm -rf {} \;
```

---

## 📚 Related Documentation

- [CORTEX-5.0 Master Plan](cortex-brain/documents/planning/active/CORTEX-5.0/00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md)
- [Sub-Plan 12: Production Validation Pipeline](cortex-brain/documents/planning/active/CORTEX-5.0/12-production-validation-pipeline/12-production-validation-pipeline.md)
- [Brain Protection Rules](cortex-brain/brain-protection-rules.yaml)
- [Final Acceptance Criteria](cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md)
- [Planning System 4.0 Manifest](cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml)

---

## 🎯 Future Enhancements

### Planned Features
- [ ] Batch upgrade (multiple plans at once)
- [ ] Interactive mode (prompt for placeholders)
- [ ] Pre-migration dry-run mode
- [ ] Diff visualization (before/after)
- [ ] Template customization via YAML config
- [ ] Integration with Planning System v5
- [ ] Automated AC extraction via LLM
- [ ] Phase dependency graph generation

### Advanced Features
- [ ] Git integration (auto-commit upgraded plans)
- [ ] CI/CD validation (check compliance in pipeline)
- [ ] Metrics dashboard (track upgrades over time)
- [ ] Rollback commands built-in
- [ ] Multi-version support (v4.0 → v5.0, v3.0 → v5.0)

---

## 💡 Tips & Best Practices

### Before Upgrade
1. ✅ Review legacy plan one last time
2. ✅ Backup workspace (`git commit -am "Pre-upgrade backup"`)
3. ✅ Run upgrade without `--archive` first (dry run)
4. ✅ Review generated plan for accuracy

### After Upgrade
1. ✅ Read migration report thoroughly
2. ✅ Update all placeholders marked with `*()*`
3. ✅ Verify phase breakdown matches original intent
4. ✅ Add missing context to Strategic Context section
5. ✅ Review and customize REFACTOR tasks
6. ✅ Validate acceptance criteria completeness

### Archive Management
1. ✅ Archive only after confirming new plan is correct
2. ✅ Keep archive metadata for audit trail
3. ✅ Periodically clean old archives (>30 days)
4. ✅ Document major migrations in CHANGELOG

---

## 📞 Support

**Issues:** Open GitHub issue with:
- Legacy plan path
- Generated compliance report
- Migration report
- Error messages (if any)

**Questions:** Reference this documentation first, then contact maintainer.

---

**Version:** 1.0.0  
**Last Updated:** January 4, 2026  
**Maintainer:** Asif Hussain

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
