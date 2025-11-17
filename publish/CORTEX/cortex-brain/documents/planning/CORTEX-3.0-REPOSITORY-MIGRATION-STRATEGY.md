# CORTEX 3.0 Repository Migration Strategy
**Date:** November 14, 2025  
**Target:** Clean CORTEX 3.0 aligned repository structure  
**Approach:** Structured migration with history preservation  
**Risk Level:** LOW (Reversible operations with archive preservation)  

## 🎯 Migration Objectives

1. **Clean Repository Root** - Reduce clutter while preserving valuable content
2. **Align with CORTEX 3.0** - Remove 2.0 references, strengthen 3.0 positioning  
3. **Organize Documentation** - Use cortex-brain/documents/ structure consistently
4. **Preserve History** - Archive rather than delete valuable architectural knowledge
5. **Maintain Functionality** - Zero disruption to active CORTEX 3.0 features

## 📋 Migration Plan: 5 Phases

### Phase 1: Create Archive Infrastructure (SAFE)
**Duration:** 5 minutes  
**Risk:** NONE  
**Purpose:** Create organized storage for legacy content

```bash
# Create archive structure
mkdir -p .archive/cortex-2.0-release
mkdir -p .archive/development-artifacts  
mkdir -p .archive/transition-docs
mkdir -p .archive/temp-files

# Create archive index
cat > .archive/README.md << 'EOF'
# CORTEX Archive
Archive of historical development artifacts organized by category.
All content preserved but moved from root for cleanliness.
EOF
```

### Phase 2: Archive Legacy Files (BENEFICIAL)  
**Duration:** 10 minutes  
**Risk:** LOW (files moved, not deleted)  
**Purpose:** Remove clear legacy artifacts from root

```bash
# Archive CORTEX 2.0 release artifacts
mv RELEASE-COMPLETE.md .archive/cortex-2.0-release/
mv CORTEX-3.0-INVESTIGATION-ARCHITECTURE-COMPLETE.md .archive/transition-docs/
mv INVESTIGATION-ROUTER-ENHANCEMENT-COMPLETE.md .archive/transition-docs/
mv INVESTIGATION-QUICK-REFERENCE.md .archive/transition-docs/
mv INTEGRATION-GUIDE.md .archive/transition-docs/
mv NOOR-CANVAS-INVESTIGATION-GUIDE.md .archive/transition-docs/

# Archive temporary development files
mv temp_file_scan.json .archive/temp-files/
mv pattern_analysis.json .archive/temp-files/
mv fix_response_headers.py .archive/development-artifacts/
mv run-cortex.sh .archive/development-artifacts/

# Archive demo files (keep them but organize)
mv demo_investigation_architecture.py .archive/development-artifacts/demo/
mv demo_investigation_plugins.py .archive/development-artifacts/demo/
mv test_investigation_integration.py .archive/development-artifacts/demo/
```

### Phase 3: Organize Brain Documentation (HIGH VALUE)
**Duration:** 20 minutes  
**Risk:** LOW (using existing organized structure)  
**Purpose:** Move unorganized docs to proper categories

```bash
# Move reports to reports/
mv cortex-brain/CORTEX-*-COMPLETE.md cortex-brain/documents/reports/
mv cortex-brain/PHASE-*-COMPLETION-REPORT.md cortex-brain/documents/reports/
mv cortex-brain/*-IMPLEMENTATION-COMPLETE.md cortex-brain/documents/reports/

# Move analysis documents to analysis/  
mv cortex-brain/*-ANALYSIS.md cortex-brain/documents/analysis/
mv cortex-brain/FILE-DEPENDENCY-ANALYSIS.md cortex-brain/documents/analysis/
mv cortex-brain/LEARNING-SYSTEM-ANALYSIS-*.md cortex-brain/documents/analysis/

# Move planning documents to planning/
mv cortex-brain/*-PLAN.md cortex-brain/documents/planning/
mv cortex-brain/*-PLANNING*.md cortex-brain/documents/planning/
mv cortex-brain/ROADMAP-*.md cortex-brain/documents/planning/

# Move summaries to summaries/
mv cortex-brain/*-SUMMARY*.md cortex-brain/documents/summaries/
mv cortex-brain/SESSION-*-SUMMARY.md cortex-brain/documents/summaries/
```

### Phase 4: Update Active Files for CORTEX 3.0 (VALUE-ADD)
**Duration:** 15 minutes  
**Risk:** LOW (version updates only)  
**Purpose:** Strengthen 3.0 positioning in active documentation

```bash
# Update README.md to emphasize CORTEX 3.0
sed -i '' 's/Version: 5.2.0/Version: 3.0.0/g' README.md
sed -i '' 's/Response Template Architecture/Investigation Architecture/g' README.md

# Update package.json version if needed
jq '.version = "3.0.0"' package.json > package.json.tmp && mv package.json.tmp package.json

# Update setup.py version
sed -i '' 's/version="[0-9.]*"/version="3.0.0"/g' setup.py
```

### Phase 5: Clean Remaining Artifacts (FOCUSED)
**Duration:** 10 minutes  
**Risk:** LOW (clear temporary files only)  
**Purpose:** Final cleanup of obvious development artifacts

```bash
# Remove empty directories if they exist
find . -type d -empty -delete

# Archive any remaining .json artifacts
mv *.json .archive/temp-files/ 2>/dev/null || true

# Keep check_brain_health.py in scripts/ (it's useful)
mv check_brain_health.py scripts/diagnostics/
```

## 🔒 Safety Mechanisms

### Rollback Procedures
```bash
# Emergency rollback for any phase
git checkout HEAD -- .  # Revert all changes
rm -rf .archive         # Remove archive directory
git clean -fd           # Clean untracked files
```

### Pre-Migration Backup
```bash
# Create full backup before starting
git commit -am "Pre-cleanup snapshot"
git tag "pre-cleanup-$(date +%Y%m%d)"
```

### Validation Checks
```bash
# After each phase, verify CORTEX 3.0 still works
python -c "from src.router import Router; print('✅ CORTEX 3.0 imports work')"
python -m pytest tests/core/ -v # Run core tests
```

## 📊 Expected Outcomes

### Repository Root (After Cleanup)
```
CORTEX/
├── .archive/                    # Historical artifacts (preserved)
├── .github/                     # Workflow automation
├── .gitignore
├── .venv/                       # Python virtual environment
├── CHANGELOG.md                 # Project changelog
├── LICENSE                      # License file
├── README.md                    # Updated for CORTEX 3.0
├── cortex-brain/               # Brain with organized documents/
├── cortex-extension/           # VS Code extension
├── cortex-operations.yaml      # Operations configuration
├── cortex.config.example.json  # Configuration examples
├── cortex.config.json          # Active configuration
├── cortex.config.template.json # Configuration template
├── docs/                       # Documentation site
├── examples/                   # Usage examples
├── logs/                       # Runtime logs
├── mkdocs.yml                  # Documentation config
├── package.json                # Node.js dependencies
├── prompts/                    # AI interaction prompts
├── pytest.ini                 # Test configuration
├── requirements.txt            # Python dependencies
├── scripts/                    # Utility scripts
├── setup.py                    # Python package setup
├── site/                       # Built documentation
├── src/                        # CORTEX 3.0 source code
├── tests/                      # Test suite
└── tsconfig.json              # TypeScript configuration
```

### Benefits Achieved
```yaml
organization:
  root_files_reduced: "45 → 25 files (44% reduction)"
  documentation_organized: "120+ docs properly categorized"
  version_consistency: "All active files reference CORTEX 3.0"
  
maintainability:
  clear_structure: "Obvious where new docs should go"
  reduced_confusion: "No mixed version references"
  easier_navigation: "Logical document organization"
  
preservation:
  history_intact: "All content preserved in .archive/"
  rollback_possible: "Complete migration is reversible"
  context_maintained: "Architectural evolution documented"
```

## ⚡ Quick Execution Option

If you approve this strategy, I can execute it with a single command sequence:

```bash
# Complete migration in one operation
./scripts/migrate_to_cortex_3.0.sh
```

This script would:
1. Create archive structure
2. Move files according to classification
3. Update version references
4. Run validation checks
5. Create migration log

## ⚠️ Pre-Migration Checklist

- [ ] **Backup created:** `git tag pre-cleanup-$(date +%Y%m%d)`
- [ ] **Tests passing:** `python -m pytest tests/core/ -q`
- [ ] **CORTEX 3.0 functional:** Verify current functionality works
- [ ] **Team notification:** Inform team of cleanup (if applicable)
- [ ] **Documentation review:** Identify any docs that should stay in root

## 🎯 Decision Point

**Option A: Full Migration** (Recommended)
- Execute all 5 phases for complete cleanup
- Clean, organized repository aligned with CORTEX 3.0
- All history preserved in archives

**Option B: Selective Migration**
- Execute only Phase 2 (archive clear legacy)
- Execute only Phase 3 (organize docs)
- Leave root structure mostly intact

**Option C: Documentation-Only**
- Execute only Phase 3 (organize cortex-brain docs)
- Leave root files untouched
- Focus on internal organization

Which approach would you prefer to proceed with?

---

**Migration Strategy Complete** | **Ready for Execution**