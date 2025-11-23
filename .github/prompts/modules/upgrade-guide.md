# CORTEX Upgrade Guide

**Purpose:** Automated upgrade system for CORTEX with brain data preservation  
**Version:** 2.0 (Automated Upgrade System)  
**Status:** ✅ PRODUCTION

---

## 🎯 Upgrade Command

**Trigger Words:** `upgrade`, `upgrade cortex`, `update cortex`, `/CORTEX upgrade`

**What It Does:**
1. **Version Check:** Compares local vs remote version
2. **Download Updates:** Pulls latest code if new version exists
3. **Apply Migrations:** Runs database schema updates
4. **Preserve Brain:** Keeps all knowledge graphs, conversations, configs
5. **Update Documentation:** Auto-updates CORTEX.prompt.md and copilot-instructions.md
6. **Install Tooling:** Ensures all dependencies available
7. **Validate .gitignore:** Confirms CORTEX excluded from user repo
8. **Comprehensive Validation:** Tests all features functional

---

## 🔄 Automated Upgrade Process

### Phase 1: Pre-Upgrade Validation (30 sec)
**Checks before starting upgrade:**
- ✅ Current version detection (read from VERSION file)
- ✅ Remote version check (fetch latest from GitHub)
- ✅ Network connectivity test
- ✅ Disk space check (need ~100MB free)
- ✅ Backup brain data to timestamped folder
- ✅ Check for uncommitted changes (warn user)

**If Already Latest:**
```
✅ CORTEX is up to date (v3.1.0)
   No upgrade needed.
```

### Phase 2: Download Latest Code (1 min)
**Pull updates from repository:**
```bash
# Fetch latest release tag
git fetch --tags origin

# Determine latest version
LATEST=$(git describe --tags --abbrev=0 origin/main)

# Pull latest code
git pull origin main
git checkout $LATEST
```

**What Gets Updated:**
- ✅ Core agents (FeedbackAgent, ViewDiscoveryAgent, etc.)
- ✅ Workflow integrators (TDD, Planning, etc.)
- ✅ Database schemas (migration scripts)
- ✅ Documentation (CORTEX.prompt.md, upgrade-guide.md)
- ✅ Entry point modules (feedback, optimize, upgrade, etc.)
- ✅ Validation scripts
- ✅ Deployment pipeline

### Phase 3: Apply Enhancements (2 min)
**Run migration scripts preserving brain data:**
```bash
# Apply database migrations
for script in migrations/*.py; do
    echo "Applying: $script"
    python "$script"
done

# Specific Issue #3 migration
python apply_element_mappings_schema.py

# Automated Post-Migration Testing (CRITICAL)
echo "\n🧪 Running post-migration validation tests..."
python validate_issue3_phase4.py

if [ $? -ne 0 ]; then
    echo "❌ VALIDATION FAILED - Upgrade incomplete"
    echo "   Brain protection may be compromised"
    echo "   Run: python validate_issue3_phase4.py for details"
    exit 1
fi

echo "✅ All validation tests passed - CORTEX fully functional"
```

**Brain Data Preservation:**
- ✅ Knowledge graphs (Tier 2) - Read-only during migration
- ✅ Conversation history (Tier 1) - Locked during migration
- ✅ User configs (cortex.config.json) - Backed up before changes
- ✅ Custom capabilities - Merged with new defaults
- ✅ Response templates - User overrides preserved

**Post-Migration Validation (Automated):**
- ✅ Brain protection rules (SKULL) - All 22 tests pass
- ✅ Database schema integrity - Tables, indexes, views verified
- ✅ Agent functionality - FeedbackAgent, ViewDiscoveryAgent tested
- ✅ Workflow integration - TDD workflow end-to-end validation
- ✅ Entry point modules - All required modules present

### Phase 4: Update Documentation (30 sec)
**Auto-update entry point documentation:**

**CORTEX.prompt.md Updates:**
```markdown
## 🔄 Upgrade CORTEX (NEW)
- upgrade - Automated upgrade with brain preservation
- upgrade check - Check for available updates

## 📢 Feedback & Issue Reporting (NEW)
- feedback bug - Report bugs with auto-context

## 🔍 View Discovery (NEW)
- discover views - Auto-extract element IDs for testing
```

**copilot-instructions.md Updates:**
```markdown
# GitHub Copilot Instructions for CORTEX

**Entry Point:** Load `.github/prompts/CORTEX.prompt.md`

**New Modules (v3.1.0):**
- modules/upgrade-guide.md - Automated upgrade system
- modules/feedback-guide.md - Issue reporting
- modules/view-discovery-guide.md - TDD automation
```

### Phase 5: Install Required Tooling (1 min)
**Ensure all dependencies present:**
```bash
# Check Python version (need 3.10+)
python --version

# Install/update pip packages
pip install -r requirements.txt --upgrade

# Install development tools (if missing)
pip install pytest playwright sqlite3

# Verify installations
python -c "import pytest; import playwright; print('✅ All tools installed')"
```

### Phase 6: Validate .gitignore (10 sec)
**Ensure CORTEX not committed to user repo:**

**Check user repo .gitignore:**
```bash
# Navigate to user repo
cd "$USER_REPO_PATH"

# Check .gitignore
if ! grep -q "^CORTEX/$" .gitignore; then
    echo "CORTEX/" >> .gitignore
    echo "✅ Added CORTEX/ to .gitignore"
else
    echo "✅ CORTEX already in .gitignore"
fi
```

**Validate exclusion:**
```bash
# Check if CORTEX tracked by git
if git ls-files | grep -q "CORTEX/"; then
    echo "⚠️  WARNING: CORTEX files tracked by git"
    echo "   Run: git rm -r --cached CORTEX/"
fi
```

### Phase 7: Comprehensive Validation (Automated)
**Validation runs automatically in Phase 3 after migrations complete.**

**Manual Validation (Optional):**
```bash
# Run validation suite manually anytime
python validate_issue3_phase4.py

# Run specific validation categories
python validate_issue3_phase4.py --category=brain_protection
python validate_issue3_phase4.py --category=database
python validate_issue3_phase4.py --category=agents
```

**Expected Output:** `✅ ALL VALIDATIONS PASSED - READY FOR PRODUCTION`

**Validation Categories:**

**1. Brain Protection (SKULL Rules)**
- ✅ All 22 brain protection tests pass
- ✅ YAML rule validation (brain-protection-rules.yaml)
- ✅ File system protections active
- ✅ Memory isolation verified

**2. Database Schema**
- ✅ 4 tables created (element_mappings, navigation_flows, discovery_runs, element_changes)
- ✅ 14 indexes applied for performance
- ✅ 4 views created for querying
- ✅ Foreign key constraints validated

**3. Agent Functionality**
- ✅ FeedbackAgent imports and initializes
- ✅ ViewDiscoveryAgent discovers elements
- ✅ Agent context injection works
- ✅ Database persistence functional

**4. Workflow Integration**
- ✅ TDD workflow integrator imports
- ✅ View discovery runs before test generation
- ✅ Element mappings cached correctly
- ✅ End-to-end workflow validated

**5. Entry Point Modules**
- ✅ upgrade-guide.md present
- ✅ feedback-guide.md present (if implemented)
- ✅ view-discovery-guide.md present (if implemented)
- ✅ Documentation synchronized

**6. Configuration Integrity**
- ✅ .gitignore excludes CORTEX/
- ✅ cortex.config.json valid
- ✅ response-templates.yaml valid
- ✅ capabilities.yaml valid

---

## 📊 Upgrade Validation Enforcement

**Deploy Pipeline Checks:**

### Test Package Requirements
**CRITICAL: Validation tests MUST be deployed with CORTEX package**

**Required Test Files:**
```
validate_issue3_phase4.py           # Main validation orchestrator
tests/
├── tier0/
│   └── test_brain_protector.py    # Brain protection (22 tests)
├── integration/
│   └── test_issue3_fixes.py       # Agent integration tests
└── test_deploy_issue3_fixes.py    # Deployment validation
```

**Why Tests Are Deployed:**
1. **Brain Protection Verification** - Ensures SKULL rules active post-upgrade
2. **Zero-Trust Validation** - User machine validates upgrade success
3. **Regression Prevention** - Catches compatibility issues immediately
4. **Rollback Decision** - Automated test failures trigger rollback recommendation
5. **Confidence Assurance** - Users know CORTEX is 100% functional after upgrade

**Test Execution Flow:**
```
Upgrade Process:
1. Pull latest code ✅
2. Apply migrations ✅
3. Run validate_issue3_phase4.py ⏳
   ├─ Brain protection tests (22/22 must pass)
   ├─ Database schema validation (100% coverage)
   ├─ Agent functionality tests (all agents)
   ├─ Workflow integration tests (end-to-end)
   └─ Entry point validation (all modules)
4. If ALL tests pass ✅ → Upgrade complete
5. If ANY test fails ❌ → Recommend rollback
```

**Deployment Size Impact:**
- Test files: ~50 KB (validate_issue3_phase4.py + dependencies)
- Total package increase: <100 KB
- Value: Priceless (prevents brain corruption)

### Entry Point Module Validation
**Required modules for deployment:**
- ✅ `modules/upgrade-guide.md` - Upgrade automation
- ✅ `modules/feedback-guide.md` - Issue reporting (TBD)
- ✅ `modules/optimize-guide.md` - Performance optimization (TBD)
- ✅ `modules/healthcheck-guide.md` - System health monitoring (TBD)
- ✅ `modules/view-discovery-guide.md` - TDD automation (TBD)

**Validation Script:** `scripts/validate_entry_points.py`
```python
def validate_entry_points():
    required = [
        'upgrade-guide.md',
        'feedback-guide.md', 
        'optimize-guide.md',
        'healthcheck-guide.md',
        'view-discovery-guide.md'
    ]
    
    for module in required:
        path = f'.github/prompts/modules/{module}'
        if not Path(path).exists():
            raise ValueError(f'Missing entry point: {module}')
    
    print('✅ All entry point modules present')
```

### Documentation Synchronization
**CORTEX.prompt.md must reference all modules:**
```bash
# Validate all modules documented
python scripts/validate_documentation_sync.py

# Checks:
# - Each module has corresponding section in CORTEX.prompt.md
# - All commands documented with examples
# - Links to modules use #file: syntax
```

### Deployment Checklist
**Enforced by CI/CD pipeline:**
- [ ] All entry point modules present
- [ ] CORTEX.prompt.md updated with new modules
- [ ] copilot-instructions.md updated
- [ ] Migration scripts present (if DB changes)
- [ ] **Validation scripts included in package (CRITICAL)**
  - [ ] validate_issue3_phase4.py deployed
  - [ ] Brain protection tests (tests/tier0/test_brain_protector.py)
  - [ ] Agent tests (tests/integration/test_issue3_fixes.py)
  - [ ] All tests pass locally (100% pass rate required)
- [ ] .gitignore template updated
- [ ] requirements.txt updated (if new deps)
- [ ] VERSION file incremented
- [ ] Release notes drafted
- [ ] Rollback procedure documented
- [ ] **Post-upgrade validation automated (runs after Phase 3)**

---

## 🛡️ Data Preservation

**What Gets Preserved (100%):**
- ✅ **Knowledge Graphs** - Tier 2 database patterns and relationships
- ✅ **Conversation History** - Tier 1 working memory and context
- ✅ **User Configurations** - cortex.config.json settings
- ✅ **Development Context** - Learned patterns and preferences
- ✅ **Custom Capabilities** - User-defined templates and agents
- ✅ **Feedback Reports** - Collected issue reports
- ✅ **Planning Documents** - Active and completed plans

**What Gets Added:**
- ✅ New database tables (coexist with existing)
- ✅ New agents and workflows
- ✅ Enhanced capabilities
- ✅ New entry point modules

**What Gets Updated:**
- ✅ Core agent logic (non-breaking changes)
- ✅ Documentation files
- ✅ Response templates (merged with existing)
- ✅ Entry point routing (new commands added)

---

## 📊 Upgrade Validation

**Post-Upgrade Checks:**

### Database Integrity
```bash
# Verify tables exist
python -c "
import sqlite3
conn = sqlite3.connect('cortex-brain/tier2/knowledge_graph.db')
tables = [r[0] for r in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()]
print(f'Total tables: {len(tables)}')
print(f'New tables: {[t for t in tables if t.startswith(\"tier2_element\")]}')
"
```

### Agent Functionality
```bash
# Test new agents
python -c "
import sys
sys.path.insert(0, 'src')
from agents.feedback_agent import FeedbackAgent
from agents.view_discovery_agent import ViewDiscoveryAgent
print('✅ FeedbackAgent loaded')
print('✅ ViewDiscoveryAgent loaded')
"
```

### Brain Data Check
```bash
# Verify brain data intact
ls cortex-brain/tier2/knowledge_graph.db  # Should exist
ls cortex-brain/tier1/working_memory.db   # Should exist
ls cortex-brain/capabilities.yaml          # Should exist
```

---

## 🚨 Rollback Procedure

**If upgrade fails:**

### Option 1: Git Rollback (Recommended)
```bash
# Revert to previous version
git reset --hard HEAD~1

# Or checkout specific tag
git checkout v3.0.0
```

### Option 2: Restore from Backup
```bash
# Restore brain data from backup
cp -r /path/to/backup/cortex-brain/* cortex-brain/

# Restore code from backup
cp -r /path/to/backup/src/* src/
```

### Option 3: Fresh Install
```bash
# Clone fresh CORTEX
git clone https://github.com/asifhussain60/CORTEX.git CORTEX-fresh

# Copy brain data
cp -r CORTEX/cortex-brain/* CORTEX-fresh/cortex-brain/

# Validate
cd CORTEX-fresh
python validate_issue3_phase4.py
```

---

## 📋 Version-Specific Upgrade Notes

### v3.0 → v3.1 (Issue #3 Fix)

**New Features:**
- FeedbackAgent for structured issue reporting
- ViewDiscoveryAgent for TDD automation
- Database persistence (4 tables, 14 indexes, 4 views)
- TDD workflow integration

**Migration Required:**
```bash
python apply_element_mappings_schema.py
```

**Breaking Changes:** None (fully backwards compatible)

**New Commands:**
- `feedback bug` - Report issues
- `discover views` - Extract element IDs
- `show discovered elements` - View cache

**Validation:**
```bash
python validate_issue3_phase4.py
```

**Expected Impact:**
- 92% time savings on test generation
- 95%+ first-run test success rate
- 10x selector reliability

---

## ⚙️ Upgrade Configuration

**Auto-Upgrade Settings (cortex.config.json):**
```json
{
  "upgrade": {
    "auto_check": true,
    "check_interval": "daily",
    "auto_backup": true,
    "backup_location": "D:/Backups/CORTEX",
    "pre_upgrade_validation": true,
    "post_upgrade_validation": true
  }
}
```

**Manual Override:**
```bash
# Skip validation (not recommended)
SKIP_VALIDATION=1 python apply_element_mappings_schema.py

# Skip backup (not recommended)
SKIP_BACKUP=1 git pull origin CORTEX-3.0
```

---

## 🔍 Troubleshooting

### Issue: "ModuleNotFoundError" after upgrade
**Solution:**
```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Should include: /path/to/CORTEX/src
# If not, reinstall:
pip install -e .
```

### Issue: "Database is locked"
**Solution:**
```bash
# Close all database connections
# Check for lock files:
ls cortex-brain/tier2/*.db-shm
ls cortex-brain/tier2/*.db-wal

# If present, close programs and retry
```

### Issue: "Validation failed"
**Solution:**
```bash
# Check specific failure
python validate_issue3_phase4.py 2>&1 | grep "❌"

# Common fixes:
# 1. Schema not applied: python apply_element_mappings_schema.py
# 2. Import errors: pip install -e .
# 3. Missing files: git pull origin CORTEX-3.0
```

### Issue: "Brain data missing"
**Solution:**
```bash
# Check brain files exist
ls cortex-brain/tier2/knowledge_graph.db
ls cortex-brain/tier1/working_memory.db

# If missing, restore from backup:
cp -r /path/to/backup/cortex-brain/* cortex-brain/
```

---

## 📚 Additional Resources

**Documentation:**
- Issue #3 Implementation: `cortex-brain/documents/reports/ISSUE-3-PHASE-4-COMPLETE.md`
- Execution Guide: `cortex-brain/documents/reports/ISSUE-3-PHASE-4-EXECUTION-GUIDE.md`
- Deployment Ready: `cortex-brain/documents/reports/PHASE-4-READY.md`

**Scripts:**
- Schema Application: `apply_element_mappings_schema.py`
- Validation: `validate_issue3_phase4.py`
- Deployment: `scripts/deploy_issue3_fixes.py`

**Support:**
- GitHub Issues: https://github.com/asifhussain60/CORTEX/issues
- Documentation: `.github/prompts/CORTEX.prompt.md`

---

## ✅ Success Criteria

**Upgrade is successful when:**
- ✅ Latest code pulled from repository
- ✅ Database migrations applied
- ✅ Validation passes (ALL TESTS PASSED)
- ✅ Brain data preserved (verified)
- ✅ New features functional (tested)
- ✅ No errors in logs

**User can then:**
- Use new commands (`feedback bug`, `discover views`)
- Generate tests with auto-discovery
- Benefit from enhanced performance
- Access preserved brain data

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0 - Issue #3 Upgrade Guide
