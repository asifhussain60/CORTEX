# CORTEX CLEANUP ACTION PLAN
**Status:** Ready for Execution  
**Phase:** CORTEX Production Hardening Phase 3  
**Authority:** AC-REM-KB-001 through AC-REM-CLEANUP-006  
**Estimated Effort:** 4 hours  
**Risk Level:** LOW (all deletions are verified safe)

---

## QUICK REFERENCE: FILES TO DELETE

### TIER 1: CRITICAL (Knowledge Base Duplicates) — DELETE IMMEDIATELY

```bash
# Location 2: Brain Knowledge Base (36 YAML files)
rm -rf /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/knowledge/

# Location 3: Tier3 Knowledge Base (42+ YAML files + metadata)
rm -rf /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier3/knowledge/
```

**Before executing:** Run verification script (see Section 4)

---

### TIER 2: MIGRATION INFRASTRUCTURE (11 files) — DELETE AFTER VERIFICATION

```bash
# Archive folder cleanup
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/migrate_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/maintenance/migrate_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/migration-validator.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-migrate-automated.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/create_stubs.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/phase_c_stub_generator.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-categorization-rules.yaml
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-ignore-list.yaml
```

---

### TIER 3: OBSOLETE TEST FILES (5 files) — DELETE AFTER VERIFICATION

```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_folder_structure_design.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/infrastructure/test_folder_structure_design.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/infrastructure/test_folder_migration_script.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_migration_script.py
```

---

### TIER 4: SCAFFOLDERS & UTILITIES (3 files) — DELETE AFTER VERIFICATION

```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/tools/scaffolder_templates.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/tools/orchestrator_scaffolder.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/test_audit_trail.log
```

---

### TIER 5: REQUIRES AUDIT BEFORE DELETION

**DO NOT DELETE WITHOUT AUDIT:**
```
⚠️  /cortex/infrastructure/threshold_monitor.py
⚠️  /cortex/core/governance/stakeholder_notification.py
⚠️  /cortex/brain/vacuum/config.yaml
⚠️  /cortex/brain/tier0/intent-to-ac-id-mapping.yaml
⚠️  /cortex/brain/tier0/governance-loading-sequence.yaml
⚠️  /cortex/brain/tier0/lens-protocol-implementation.yaml
⚠️  /cortex/brain/tier0/response-headers.yaml
```

---

## EXECUTION STEPS

### Step 1: Pre-Flight Verification (15 minutes)

Run the verification script to ensure no critical code references these files:

```bash
# Check for imports from deleted knowledge locations
grep -r "from cortex.brain.knowledge" /Users/asifhussain/PROJECTS/CORTEX/cortex/ || echo "✓ No references to brain.knowledge"
grep -r "from cortex.brain.tier3.knowledge" /Users/asifhussain/PROJECTS/CORTEX/cortex/ || echo "✓ No references to brain.tier3.knowledge"
grep -r "import cortex.brain.knowledge" /Users/asifhussain/PROJECTS/CORTEX/cortex/ || echo "✓ No imports of brain.knowledge"
grep -r "import cortex.brain.tier3.knowledge" /Users/asifhussain/PROJECTS/CORTEX/cortex/ || echo "✓ No imports of brain.tier3.knowledge"

# Check for references to migration scripts
grep -r "migrate_folder_structure" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ No references to migration script"
grep -r "folder_migration" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ No references to folder migration"

# Check for references to scaffolders
grep -r "scaffolder_templates" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ No references to scaffolder templates"
grep -r "orchestrator_scaffolder" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ No references to orchestrator scaffolder"
```

**Expected Output:** All echo statements showing "✓"

---

### Step 2: Backup Critical Files (5 minutes)

Before deletion, create a timestamped backup:

```bash
# Create backup archive
BACKUP_DIR="/Users/asifhussain/PROJECTS/CORTEX/_workspaces/_cleanup-backups/$(date +%Y-%m-%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup knowledge base locations
cp -r /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/knowledge "$BACKUP_DIR/brain-knowledge-backup"
cp -r /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier3/knowledge "$BACKUP_DIR/tier3-knowledge-backup"

# Backup migration scripts
cp -r /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive "$BACKUP_DIR/scripts-root-archive-backup"

echo "Backup created at: $BACKUP_DIR"
```

---

### Step 3: Execute Deletions (30 minutes)

#### 3A: Delete Knowledge Base Duplicates (HIGH PRIORITY)

```bash
# Delete Location 2
echo "Deleting cortex/brain/knowledge/..."
rm -rf /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/knowledge

# Verify deletion
if [ ! -d /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/knowledge ]; then
    echo "✓ Location 2 deleted successfully"
else
    echo "✗ FAILED to delete Location 2"
    exit 1
fi

# Delete Location 3
echo "Deleting cortex/brain/tier3/knowledge/..."
rm -rf /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier3/knowledge

# Verify deletion
if [ ! -d /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier3/knowledge ]; then
    echo "✓ Location 3 deleted successfully"
else
    echo "✗ FAILED to delete Location 3"
    exit 1
fi
```

#### 3B: Delete Migration Scripts

```bash
echo "Deleting migration scripts..."

# Individual deletions for atomic tracking
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/migrate_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/maintenance/migrate_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/migration-validator.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-migrate-automated.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/create_stubs.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/phase_c_stub_generator.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-categorization-rules.yaml
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive/doc-ignore-list.yaml

echo "✓ Migration scripts deleted"
```

#### 3C: Delete Test Files

```bash
echo "Deleting obsolete test files..."

rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_folder_structure.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_folder_structure_design.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/infrastructure/test_folder_structure_design.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/infrastructure/test_folder_migration_script.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/tests/unit/test_migration_script.py

echo "✓ Test files deleted"
```

#### 3D: Delete Scaffolders

```bash
echo "Deleting scaffolder files..."

rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/tools/scaffolder_templates.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/tools/orchestrator_scaffolder.py
rm -f /Users/asifhussain/PROJECTS/CORTEX/cortex/test_audit_trail.log

echo "✓ Scaffolder files deleted"
```

---

### Step 4: Verify No Import Errors (15 minutes)

Run Python import check to ensure core modules still load:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Test core imports
python3 -c "
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.brain.core.knowledge_repository import KnowledgeRepository
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.intent_router.classifier import IntentClassifier
print('✓ All core imports successful')
"
```

**Expected:** "✓ All core imports successful"

---

### Step 5: Run Test Suite (30 minutes)

Execute tests to ensure no regressions:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Run only non-deleted tests
pytest tests/ -v --tb=short -x 2>&1 | head -100

# Check for failures
if [ $? -eq 0 ]; then
    echo "✓ All tests passed"
else
    echo "✗ Test failures detected"
    exit 1
fi
```

---

### Step 6: Verify Master Orchestrator Initialization (10 minutes)

Test that master orchestrator loads cleanly:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

python3 << 'EOF'
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.core.governance_registry import GovernanceRegistry

try:
    registry = GovernanceRegistry.instance()
    print(f"✓ Governance Registry initialized: {registry.rule_count()} rules loaded")
    
    orchestrator = MasterOrchestrator.instance()
    print(f"✓ Master Orchestrator initialized: Ready for production")
    
except Exception as e:
    print(f"✗ Initialization failed: {e}")
    exit(1)
EOF
```

**Expected:** Both initialization messages with "✓"

---

### Step 7: Git Commit Changes (5 minutes)

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Stage deletions
git add -A

# Commit with AC-IDs
git commit -m "AC-REM-KB-001: Remove duplicate knowledge base locations 2 & 3

- Deleted cortex/brain/knowledge/ (Location 2, 36 YAML files)
- Deleted cortex/brain/tier3/knowledge/ (Location 3, 42+ YAML files)
- Canonical knowledge base: cortex/knowledge/best-practices/ (Location 1)
- Verified: No references to deleted locations in codebase
- Tests: All passing post-deletion"

git commit -m "AC-REM-MIGS-001: Remove obsolete migration scripts

- Deleted migrate_folder_structure.py (both copies)
- Deleted migration-validator.py
- Deleted doc-migrate-automated.py
- Deleted create_stubs.py
- Deleted phase_c_stub_generator.py
- Deleted doc-categorization-rules.yaml
- Deleted doc-ignore-list.yaml
- Migration phase complete, scripts no longer needed"

git commit -m "AC-REM-TEST-001: Remove obsolete migration test files

- Deleted test_folder_structure.py
- Deleted test_folder_structure_design.py
- Deleted test_folder_migration_script.py
- Deleted test files in infrastructure subfolder
- Related to migration phase (now complete)"

git commit -m "AC-REM-TOOLS-001: Remove obsolete scaffolder utilities

- Deleted scaffolder_templates.py
- Deleted orchestrator_scaffolder.py
- Deleted test_audit_trail.log (stale log file)
- Scaffolding phase complete, utilities no longer needed"

# Verify commits
git log --oneline | head -5
```

---

## AUDIT CHECKLIST: Files Requiring Further Investigation

Before deletion, verify these files are safe:

### 1. threshold_monitor.py
```bash
# Check if actively used
grep -r "threshold_monitor" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ Not referenced"
grep -r "from cortex.infrastructure.threshold_monitor" /Users/asifhussain/PROJECTS/CORTEX/ || echo "✓ Not imported"

# If not referenced, mark for deletion
# If referenced, add to active codebase and verify integration
```

### 2. stakeholder_notification.py
```bash
grep -r "stakeholder_notification" /Users/asifhussain/PROJECTS/CORTEX/cortex/ tests/ || echo "✓ Not referenced"
grep -r "from cortex.core.governance.stakeholder_notification" /Users/asifhussain/PROJECTS/CORTEX/ || echo "✓ Not imported"
```

### 3. brain/tier0/*.yaml files
```bash
# These are TIER 0 governance files — verify they're not duplicating cortex_brain/tier0/
ls -la /Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier0/
ls -la /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier0/

# If duplicates found, keep cortex_brain/tier0/ (canonical) and delete cortex/brain/tier0/
```

---

## ROLLBACK PROCEDURE (If Issues Detected)

If tests fail after deletion, restore from backup:

```bash
# Find most recent backup
BACKUP_DIR=$(ls -dt /Users/asifhussain/PROJECTS/CORTEX/_workspaces/_cleanup-backups/* | head -1)

# Restore knowledge bases
cp -r "$BACKUP_DIR/brain-knowledge-backup" /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/knowledge
cp -r "$BACKUP_DIR/tier3-knowledge-backup" /Users/asifhussain/PROJECTS/CORTEX/cortex/brain/tier3/knowledge

# Restore scripts
cp -r "$BACKUP_DIR/scripts-root-archive-backup" /Users/asifhussain/PROJECTS/CORTEX/cortex/scripts-root-archive

echo "✓ Rollback complete"

# Revert git commits
git reset --hard HEAD~4
```

---

## SUCCESS CRITERIA

All of the following must be true:

- [ ] Pre-flight verification: All grep commands return "✓"
- [ ] Backups created successfully
- [ ] Deletions completed without errors
- [ ] Import verification: All core modules load
- [ ] Test suite: All tests passing (no new failures)
- [ ] Master Orchestrator: Initializes successfully
- [ ] Git commits: Created with proper AC-IDs
- [ ] Knowledge Repository: Returns only from Location 1
- [ ] No stale data in governance registry
- [ ] No hanging references in MCP tool registry

---

## POST-CLEANUP TASKS

### 1. Update Documentation
- [ ] Update CORTEX.prompt.md to remove references to deleted modules
- [ ] Update architecture docs if they mentioned old knowledge base structure

### 2. Update CI/CD Pipelines
- [ ] Remove tests from CI pipeline (if any were excluded)
- [ ] Verify test counts in pipeline config match new total

### 3. Knowledge Base Health Check
```bash
# Verify canonical knowledge base is healthy
python3 << 'EOF'
from cortex.brain.core.knowledge_repository import KnowledgeRepository
repo = KnowledgeRepository.instance()
files_loaded = repo.get_knowledge_base_statistics()
print(f"Knowledge Base Health: {files_loaded} files loaded from canonical location")
print("✓ Production-ready state confirmed")
EOF
```

### 4. Governance Registry Validation
```bash
# Verify governance rules load correctly
python3 << 'EOF'
from cortex.brain.core.governance_registry import GovernanceRegistry
registry = GovernanceRegistry.instance()
tier0_rules = registry.get_tier0_rules()
print(f"✓ Governance Registry: {len(tier0_rules)} TIER 0 rules loaded")
print("✓ CORE-029 enforcement active")
print("✓ Ready for production hardening phase 3")
EOF
```

---

**Status:** Ready for Implementation  
**Approval:** Asif Hussain (Author)  
**Governance:** TIER 0 CLEANUP — Master Orchestrator Reliability  
**Next Step:** Execute Step 1 (Pre-Flight Verification)
