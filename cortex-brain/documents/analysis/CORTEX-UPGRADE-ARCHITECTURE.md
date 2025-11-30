# CORTEX Upgrade Architecture Design

**Version:** 1.0  
**Status:** 🎯 PROPOSED (Awaiting Approval)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Created:** 2025-11-23

---

## 🎯 Executive Summary

**Problem:** Users deploy CORTEX into repos where brain learns patterns, captures conversations, and builds workspace-specific knowledge. When CORTEX releases updates (bug fixes, new features, enhanced templates), users face a dilemma:

1. **Manual Update:** Copy new files → Risk overwriting learned brain data
2. **Skip Update:** Keep working brain → Miss critical fixes and features
3. **Hybrid Approach:** Selective file copying → Error-prone, incomplete upgrades

**Proposed Solution:** Smart upgrade system with 3-layer architecture that separates upgradeable core from preserved brain data.

**Key Innovation:** Database schema migrations + YAML config merging + brain integrity validation = Zero data loss upgrades.

---

## 🏗️ Architecture Overview

### 3-Layer Separation Model

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: CORTEX CORE (Upgradeable)                          │
│ • Scripts (src/*, scripts/*)                                 │
│ • Templates (response-templates.yaml)                        │
│ • Schemas (schema.sql, migration scripts)                    │
│ • Entry Points (.github/prompts/CORTEX.prompt.md)           │
│ • Capabilities (capabilities.yaml base)                      │
│                                                              │
│ ✅ Safe to overwrite                                         │
│ ✅ Version-controlled                                        │
│ ✅ No user data                                              │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: BRAIN DATA (Preserved)                             │
│ • Conversations (tier1/*.db)                                 │
│ • Learned Patterns (tier2/knowledge_graph.db)                │
│ • Development Context (tier3/*.db)                           │
│ • User Dictionary (user-dictionary.yaml)                     │
│ • Workspace Config (cortex.config.json)                      │
│                                                              │
│ ❌ NEVER overwrite                                           │
│ ✅ User-specific                                             │
│ ✅ Workspace-learned                                         │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: MERGED CONFIGS (Intelligent Merge)                 │
│ • Response Templates (merge local overrides)                 │
│ • Capabilities (merge workspace extensions)                  │
│ • Operations Config (merge custom operations)                │
│                                                              │
│ ⚙️ 3-way merge: Base + Local + Upgrade                       │
│ ✅ Preserve customizations                                   │
│ ✅ Add new features                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Design Principles

### 1. Zero Data Loss Guarantee
- **Pre-upgrade backup:** Full brain snapshot before upgrade
- **Rollback mechanism:** Restore previous version if upgrade fails
- **Validation gates:** Database integrity checks at each step
- **Abort on conflict:** Never auto-resolve destructive conflicts

### 2. Backward Compatibility
- **Schema migrations:** Auto-apply database schema upgrades (additive only)
- **Config versioning:** Detect version mismatches, apply migrations
- **Deprecation warnings:** Flag obsolete features, provide migration path
- **Graceful degradation:** New features fail silently if dependencies missing

### 3. Transparency & Control
- **Dry-run mode:** Preview all changes before applying
- **Change manifest:** Show exactly what will be modified
- **User approval gates:** Require confirmation for destructive operations
- **Audit trail:** Log all upgrade actions with timestamps

### 4. Atomic Operations
- **Transaction-based:** All database changes in single transaction
- **File staging:** Copy to temp directory, validate, then swap
- **Cleanup on failure:** Automatic rollback if any step fails
- **Idempotent:** Safe to run upgrade multiple times

---

## 📊 Current State Analysis

### CORTEX Deployment Structure (User Workspace)

```
user-project/
├── .github/
│   ├── prompts/
│   │   └── CORTEX.prompt.md          ← CORE (upgrade)
│   └── copilot-instructions.md       ← CORE (upgrade)
├── cortex-brain/
│   ├── tier1/
│   │   ├── working_memory.db         ← DATA (preserve)
│   │   └── smart_recommendations.db  ← DATA (preserve)
│   ├── tier2/
│   │   ├── knowledge_graph.db        ← DATA (preserve)
│   │   └── planning-tracker.db       ← DATA (preserve)
│   ├── tier3/
│   │   └── (development context)     ← DATA (preserve)
│   ├── response-templates.yaml       ← CONFIG (merge)
│   ├── capabilities.yaml             ← CONFIG (merge)
│   ├── user-dictionary.yaml          ← DATA (preserve)
│   ├── schema.sql                    ← CORE (upgrade)
│   └── documents/                    ← DATA (preserve)
├── src/                              ← CORE (upgrade)
├── scripts/                          ← CORE (upgrade)
├── cortex.config.json                ← DATA (preserve)
└── requirements.txt                  ← CORE (upgrade)
```

### Version Tracking (Missing - Must Add)

**Current:** No version tracking in deployed CORTEX  
**Needed:**
1. **Version File:** `cortex-brain/.cortex-version` (JSON)
2. **Migration Registry:** `cortex-brain/migrations/applied.json`
3. **Schema Versions:** Database `pragma user_version` tracking

---

## 🚀 Upgrade Command Design

### Natural Language Interface

```bash
# User says:
"upgrade cortex"
"update cortex to latest"
"check for cortex updates"
"cortex upgrade --dry-run"
```

### Command Flow

```
User: "upgrade cortex"
    ↓
┌──────────────────────────────────────────────┐
│ Phase 1: Pre-Flight Checks                  │
│ • Detect installed version                  │
│ • Fetch latest version from GitHub          │
│ • Compare versions (skip if up-to-date)     │
│ • Check for breaking changes                │
│ • Validate brain integrity                  │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 2: Backup & Safety                    │
│ • Create timestamped backup:                │
│   cortex-brain/backups/pre-upgrade-{date}/  │
│ • Snapshot databases (SQLite backup API)    │
│ • Save config files                         │
│ • Export brain patterns (YAML)              │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 3: Dry Run (Optional)                 │
│ • Show change manifest                      │
│ • List new features                         │
│ • Identify config conflicts                 │
│ • Estimate migration time                   │
│ • User approval: Continue? (Y/N)            │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 4: Core Upgrade                       │
│ • Download latest CORTEX package            │
│ • Extract to temp directory                 │
│ • Validate package integrity (SHA256)       │
│ • Replace core files (src/, scripts/)       │
│ • Update entry points (.github/prompts/)    │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 5: Schema Migration                   │
│ • Detect schema version mismatches          │
│ • Apply migrations (tier1, tier2, tier3)    │
│ • Validate foreign key integrity            │
│ • Update schema version markers             │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 6: Config Merge                       │
│ • Merge response-templates.yaml             │
│ • Merge capabilities.yaml                   │
│ • Update operations-config.yaml             │
│ • Preserve user-dictionary.yaml             │
│ • Update .cortex-version                    │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 7: Validation & Cleanup               │
│ • Run health checks                         │
│ • Test brain queries                        │
│ • Verify file integrity                     │
│ • Clean temp files                          │
│ • Generate upgrade report                   │
└──────────────────────────────────────────────┘
    ↓
✅ UPGRADE COMPLETE
   cortex-brain/documents/reports/UPGRADE-REPORT-{date}.md
```

---

## 🔧 Technical Implementation

### 1. Version Detection System

**File:** `cortex-brain/.cortex-version`

```json
{
  "cortex_version": "5.2.0",
  "schema_version": "1.0",
  "installed_date": "2025-11-15T10:30:00Z",
  "last_upgrade": "2025-11-15T10:30:00Z",
  "upgrade_history": [
    {
      "from_version": "5.1.0",
      "to_version": "5.2.0",
      "date": "2025-11-15T10:30:00Z",
      "migrations_applied": ["migration_001", "migration_002"]
    }
  ],
  "workspace_id": "a7b3c4d5e6f7",  // Hash of workspace path
  "customizations": {
    "response_templates": true,
    "capabilities": true,
    "operations": false
  }
}
```

**Storage Locations:**
- Database: `PRAGMA user_version` in each .db file
- YAML: `version` field in config files
- Git: `.cortex-version` file (tracked, not in user .gitignore)

---

### 2. Schema Migration System

**Structure:**
```
cortex-brain/migrations/
├── applied.json              # Migration registry
├── 001_add_ado_tables.sql
├── 002_add_feedback_tables.sql
├── 003_add_brain_exports.sql
└── migration_template.sql
```

**Migration File Format:**
```sql
-- Migration: 001_add_ado_tables.sql
-- Version: 5.2.0
-- Date: 2025-11-15
-- Author: Asif Hussain
-- Description: Add ADO planning tables to tier2

-- Forward migration
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS tier2_ado_work_items (
    ado_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Update schema version
PRAGMA user_version = 2;

COMMIT;

-- Rollback migration (if needed)
-- DROP TABLE IF EXISTS tier2_ado_work_items;
-- PRAGMA user_version = 1;
```

**Migration Runner:**
```python
class SchemaUpgrader:
    """Handles database schema upgrades."""
    
    def apply_migrations(self, db_path: Path, target_version: int) -> bool:
        """Apply all pending migrations to database."""
        current_version = self._get_schema_version(db_path)
        
        if current_version >= target_version:
            return True  # Already up-to-date
        
        # Get pending migrations
        migrations = self._get_pending_migrations(current_version, target_version)
        
        # Create backup before migration
        backup_path = self._backup_database(db_path)
        
        try:
            for migration in migrations:
                self._apply_migration(db_path, migration)
                self._log_migration(migration)
            
            # Validate integrity
            if not self._validate_database(db_path):
                raise Exception("Database validation failed")
            
            return True
            
        except Exception as e:
            # Rollback on failure
            self._restore_database(backup_path, db_path)
            logger.error(f"Migration failed: {e}")
            return False
```

---

### 3. Config Merge System

**3-Way Merge Strategy:**
```
Base Config (CORTEX v5.1.0)
    +
Local Config (User's workspace)
    +
Upgrade Config (CORTEX v5.2.0)
    =
Merged Config (Preserved customizations + New features)
```

**Example: response-templates.yaml Merge**

```yaml
# Base (v5.1.0)
templates:
  help_table:
    triggers: ["help"]
  
# Local (User added custom trigger)
templates:
  help_table:
    triggers: ["help", "cortex help"]
  
# Upgrade (v5.2.0 adds new template)
templates:
  help_table:
    triggers: ["help"]
  admin_help:
    triggers: ["admin help"]

# MERGED RESULT
templates:
  help_table:
    triggers: ["help", "cortex help"]  ← Preserved user addition
  admin_help:
    triggers: ["admin help"]          ← Added from upgrade
```

**Merge Algorithm:**
```python
class ConfigMerger:
    """Intelligent YAML config merging."""
    
    def merge_yaml(self, base: dict, local: dict, upgrade: dict) -> dict:
        """3-way merge with conflict detection."""
        merged = copy.deepcopy(upgrade)  # Start with new version
        
        # Detect user customizations
        customizations = self._find_customizations(base, local)
        
        # Apply customizations to merged config
        for path, value in customizations.items():
            if not self._conflicts_with_upgrade(path, value, upgrade):
                self._set_nested_value(merged, path, value)
            else:
                # Log conflict for manual resolution
                self._log_conflict(path, local_value=value, 
                                  upgrade_value=self._get_nested_value(upgrade, path))
        
        return merged
```

---

### 4. Brain Integrity Validator

**Pre-Upgrade Checks:**
```python
class BrainValidator:
    """Validates brain integrity before/after upgrade."""
    
    def validate_pre_upgrade(self) -> ValidationReport:
        """Check brain health before upgrade."""
        report = ValidationReport()
        
        # Database integrity
        report.add_check("tier1_integrity", self._check_db_integrity(tier1_db))
        report.add_check("tier2_integrity", self._check_db_integrity(tier2_db))
        report.add_check("tier3_integrity", self._check_db_integrity(tier3_db))
        
        # File structure
        report.add_check("config_files", self._check_required_files())
        
        # Schema versions
        report.add_check("schema_versions", self._check_schema_versions())
        
        # Disk space (need 2x brain size for backup)
        report.add_check("disk_space", self._check_disk_space())
        
        return report
    
    def validate_post_upgrade(self) -> ValidationReport:
        """Verify brain functionality after upgrade."""
        report = ValidationReport()
        
        # Query tests
        report.add_check("conversation_query", self._test_conversation_query())
        report.add_check("pattern_query", self._test_pattern_query())
        
        # Foreign key integrity
        report.add_check("foreign_keys", self._check_foreign_keys())
        
        # Config loading
        report.add_check("config_load", self._test_config_loading())
        
        return report
```

---

## 🎨 User Experience Design

### Upgrade Scenarios

#### Scenario 1: Simple Upgrade (No Conflicts)

```
User: "upgrade cortex"

CORTEX:
  🔍 Checking for updates...
  
  ✅ Update available: v5.1.0 → v5.2.0
  
  📦 Changes in v5.2.0:
     • New feature: ADO Planning System 2.0
     • Enhancement: Response templates expanded
     • Bug fix: Schema migration validation
  
  🔒 Safety checks:
     ✅ Brain backup will be created
     ✅ No breaking changes detected
     ✅ Rollback available if needed
  
  ⏱️ Estimated time: 2-3 minutes
  
  Continue with upgrade? (Y/N)

User: "Y"

CORTEX:
  ⚡ Phase 1/7: Creating backup...
     ✅ Backed up to cortex-brain/backups/pre-upgrade-20251123_143000/
  
  ⚡ Phase 2/7: Downloading CORTEX v5.2.0...
     ✅ Package verified (SHA256: a7b3c4...)
  
  ⚡ Phase 3/7: Upgrading core files...
     ✅ Updated 47 files
  
  ⚡ Phase 4/7: Migrating databases...
     ✅ Applied 2 migrations to tier2
  
  ⚡ Phase 5/7: Merging configs...
     ✅ No conflicts detected
  
  ⚡ Phase 6/7: Running validation...
     ✅ All health checks passed
  
  ⚡ Phase 7/7: Cleanup...
     ✅ Temp files removed
  
  ✅ UPGRADE COMPLETE
  
  🎉 CORTEX v5.2.0 is ready!
  
  📊 Upgrade Report: cortex-brain/documents/reports/UPGRADE-REPORT-20251123.md
  
  🔄 Your brain is intact:
     • 127 conversations preserved
     • 43 learned patterns retained
     • 12 custom templates merged
  
  🆕 New features available:
     • /ado planning - ADO work item planning
     • Enhanced response templates
     • Improved schema validation
  
  Type "help" to see what's new!
```

---

#### Scenario 2: Upgrade with Config Conflicts

```
User: "upgrade cortex"

CORTEX:
  🔍 Checking for updates...
  
  ✅ Update available: v5.1.0 → v5.2.0
  
  ⚠️ CONFLICTS DETECTED:
  
  1. response-templates.yaml
     Your version: Custom trigger "cortex help" for help_table
     Upgrade version: New trigger "what can cortex do"
     Resolution: Keep both triggers (merged)
  
  2. capabilities.yaml
     Your version: Added custom operation "my_custom_op"
     Upgrade version: Operation structure changed
     Resolution: Manual review required
  
  📋 Options:
     1. Auto-merge (recommended) - Keep your customizations + add new features
     2. Manual review - Review conflicts before applying
     3. Abort - Cancel upgrade
  
  Choose option (1/2/3):

User: "1"

CORTEX:
  ✅ Auto-merge selected
  
  ⚙️ Merge plan:
     • response-templates.yaml: Merge triggers (keep both)
     • capabilities.yaml: Preserve custom operation, update structure
  
  Continue? (Y/N)

User: "Y"

CORTEX:
  [... upgrade proceeds as normal ...]
  
  ✅ UPGRADE COMPLETE with merged configs
  
  ⚠️ ACTION REQUIRED:
  
  Your custom operation "my_custom_op" uses old structure.
  Update guide: cortex-brain/documents/reports/UPGRADE-REPORT-20251123.md#migration-guide
  
  Run "validate my_custom_op" to test compatibility.
```

---

#### Scenario 3: Dry Run Mode

```
User: "upgrade cortex --dry-run"

CORTEX:
  🔍 Checking for updates (DRY RUN MODE)...
  
  ✅ Update available: v5.1.0 → v5.2.0
  
  📋 CHANGES PREVIEW (No files will be modified)
  
  ┌─────────────────────────────────────────────────────┐
  │ CORE FILES (47 files to update)                     │
  ├─────────────────────────────────────────────────────┤
  │ src/tier1/working_memory.py       v5.1.0 → v5.2.0  │
  │ src/tier2/knowledge_graph.py      v5.1.0 → v5.2.0  │
  │ .github/prompts/CORTEX.prompt.md  Updated           │
  │ cortex-brain/schema.sql           2 migrations     │
  │ ... (43 more files)                                 │
  └─────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────┐
  │ BRAIN DATA (PRESERVED - No changes)                 │
  ├─────────────────────────────────────────────────────┤
  │ cortex-brain/tier1/*.db           ✅ Preserved      │
  │ cortex-brain/tier2/*.db           ✅ Preserved      │
  │ user-dictionary.yaml              ✅ Preserved      │
  │ cortex.config.json                ✅ Preserved      │
  └─────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────┐
  │ CONFIG FILES (MERGED)                               │
  ├─────────────────────────────────────────────────────┤
  │ response-templates.yaml:                            │
  │   • 12 custom triggers preserved                    │
  │   • 8 new templates added                           │
  │                                                     │
  │ capabilities.yaml:                                  │
  │   • 1 custom operation preserved                    │
  │   • 3 new operations added                          │
  └─────────────────────────────────────────────────────┘
  
  ┌─────────────────────────────────────────────────────┐
  │ DATABASE MIGRATIONS                                 │
  ├─────────────────────────────────────────────────────┤
  │ tier2/knowledge_graph.db:                           │
  │   • Migration 001: Add ado_work_items table         │
  │   • Migration 002: Add feedback_reports table       │
  └─────────────────────────────────────────────────────┘
  
  📊 IMPACT SUMMARY:
     Files updated: 47
     Brain data preserved: 100%
     Config files merged: 2
     Migrations to apply: 2
     Estimated time: 2-3 minutes
     Rollback available: Yes
  
  Ready to proceed? Run "upgrade cortex" to apply.
```

---

## 🛡️ Safety Mechanisms

### 1. Atomic Transactions

**Database Upgrades:**
```python
def upgrade_database(db_path: Path, migrations: List[Migration]) -> bool:
    """Apply migrations atomically."""
    conn = sqlite3.connect(db_path)
    conn.execute("BEGIN EXCLUSIVE TRANSACTION")
    
    try:
        for migration in migrations:
            conn.executescript(migration.sql)
        
        conn.execute("COMMIT")
        return True
        
    except Exception as e:
        conn.execute("ROLLBACK")
        logger.error(f"Migration failed: {e}")
        return False
    
    finally:
        conn.close()
```

### 2. Backup Strategy

**Pre-Upgrade Backup:**
```
cortex-brain/backups/pre-upgrade-20251123_143000/
├── .cortex-version                  # Version snapshot
├── tier1/
│   ├── working_memory.db
│   └── smart_recommendations.db
├── tier2/
│   ├── knowledge_graph.db
│   └── planning-tracker.db
├── tier3/
│   └── (development context)
├── response-templates.yaml
├── capabilities.yaml
└── cortex.config.json
```

**Backup Retention:**
- Keep last 5 upgrade backups
- Auto-delete backups older than 30 days
- Option to export backup to external location

### 3. Rollback Mechanism

```
User: "rollback cortex"

CORTEX:
  🔍 Checking for rollback options...
  
  ✅ Found backup: pre-upgrade-20251123_143000
     From version: v5.2.0
     To version: v5.1.0
     Backup date: 2025-11-23 14:30:00
  
  ⚠️ WARNING: Rolling back will:
     • Restore CORTEX core to v5.1.0
     • Restore brain databases from backup
     • Restore config files
     • LOSE any work done since upgrade
  
  Continue with rollback? (Y/N)

User: "Y"

CORTEX:
  ⚡ Phase 1/3: Restoring core files...
     ✅ Restored src/, scripts/, .github/
  
  ⚡ Phase 2/3: Restoring brain databases...
     ✅ Restored tier1, tier2, tier3
  
  ⚡ Phase 3/3: Restoring configs...
     ✅ Restored response-templates.yaml, capabilities.yaml
  
  ✅ ROLLBACK COMPLETE
  
  CORTEX v5.1.0 restored successfully.
```

---

## 🔍 Validation Gates

### Pre-Upgrade Validation

```python
class PreUpgradeValidator:
    """Validates system before upgrade."""
    
    def validate(self) -> ValidationReport:
        """Run all pre-upgrade checks."""
        report = ValidationReport()
        
        # Check 1: Brain integrity
        report.add_check("brain_integrity", self._check_brain_integrity())
        # Result: ✅ All databases healthy
        
        # Check 2: Disk space (need 2x brain size)
        brain_size = self._calculate_brain_size()  # 150 MB
        available = self._get_available_space()     # 5 GB
        required = brain_size * 2                   # 300 MB
        report.add_check("disk_space", available >= required)
        # Result: ✅ 5 GB available (need 300 MB)
        
        # Check 3: File permissions
        report.add_check("file_permissions", self._check_write_permissions())
        # Result: ✅ Write access to all required directories
        
        # Check 4: Git status (warn if uncommitted changes)
        report.add_check("git_status", self._check_git_status())
        # Result: ⚠️ 3 uncommitted files (recommend commit first)
        
        # Check 5: Python dependencies
        report.add_check("dependencies", self._check_python_dependencies())
        # Result: ✅ All required packages installed
        
        return report
```

### Post-Upgrade Validation

```python
class PostUpgradeValidator:
    """Validates system after upgrade."""
    
    def validate(self) -> ValidationReport:
        """Run all post-upgrade checks."""
        report = ValidationReport()
        
        # Check 1: Brain functionality
        report.add_check("brain_queries", self._test_brain_queries())
        # Result: ✅ All query types working
        
        # Check 2: Database integrity
        report.add_check("db_integrity", self._check_db_integrity())
        # Result: ✅ Foreign keys valid, no corruption
        
        # Check 3: Config loading
        report.add_check("config_load", self._test_config_loading())
        # Result: ✅ All configs parse correctly
        
        # Check 4: Agent functionality
        report.add_check("agents", self._test_agents())
        # Result: ✅ All 7 specialist agents operational
        
        # Check 5: Version consistency
        report.add_check("version_consistency", self._check_version_consistency())
        # Result: ✅ All components on v5.2.0
        
        return report
```

---

## 📦 Upgrade Package Distribution

### GitHub Release Strategy

**Release Assets:**
```
CORTEX v5.2.0 Release
├── cortex-v5.2.0-full.zip        # Complete package (new installs)
├── cortex-v5.2.0-upgrade.zip     # Upgrade-only package (smaller)
├── CHANGELOG.md                  # Human-readable changes
├── UPGRADE-GUIDE.md              # Migration instructions
├── SHA256SUMS.txt                # Package integrity hashes
└── migrations/
    ├── 001_add_ado_tables.sql
    └── 002_add_feedback_tables.sql
```

**Upgrade Package Contents:**
```
cortex-v5.2.0-upgrade.zip
├── src/                          # Core source code
├── scripts/                      # User scripts
├── .github/prompts/              # Entry points
├── cortex-brain/
│   ├── schema.sql                # Schema definitions
│   ├── migrations/               # Migration scripts
│   ├── response-templates.yaml   # Base templates
│   └── capabilities.yaml         # Base capabilities
├── requirements.txt              # Python dependencies
├── .cortex-version               # Version metadata
└── UPGRADE-NOTES.md              # Version-specific notes
```

**Size Comparison:**
- Full package: ~15 MB (includes docs, tests, examples)
- Upgrade package: ~5 MB (core files only)
- Reduction: 67% smaller downloads for upgrades

---

## 🎯 Alternative Solutions Comparison

### Option A: Git Submodule (Rejected)

**How It Works:**
```bash
# Initial setup
git submodule add https://github.com/asifhussain60/CORTEX.git cortex-core
cd cortex-core
git checkout v5.2.0
```

**Pros:**
- Native git integration
- Easy version tracking
- Standard git workflows

**Cons:**
- ❌ Requires git expertise from users
- ❌ Submodule conflicts are notoriously painful
- ❌ No intelligent config merging
- ❌ No database migration automation
- ❌ Accidental commits of brain data to CORTEX repo

**Verdict:** ⛔ Rejected - Too complex for non-git-expert users

---

### Option B: Package Manager (npm/pip) (Rejected)

**How It Works:**
```bash
# Install as npm package
npm install -g @asifhussain/cortex

# Upgrade
npm update -g @asifhussain/cortex
```

**Pros:**
- Familiar package manager workflow
- Dependency management built-in
- Version constraints supported

**Cons:**
- ❌ Python + Node.js dual dependency
- ❌ No brain data preservation logic
- ❌ Package size limits (npm: 100 MB)
- ❌ No custom config merging
- ❌ Global install isolates from workspace

**Verdict:** ⛔ Rejected - Doesn't solve brain preservation problem

---

### Option C: Docker Container (Rejected)

**How It Works:**
```bash
# Run CORTEX in container
docker run -v $(pwd):/workspace asifhussain/cortex:5.2.0

# Upgrade
docker pull asifhussain/cortex:5.2.0
```

**Pros:**
- Isolated environment
- Easy version switching
- Cross-platform consistency

**Cons:**
- ❌ Requires Docker knowledge
- ❌ Brain data in volumes (harder to inspect)
- ❌ VS Code Copilot integration complex
- ❌ Performance overhead
- ❌ Overkill for file-based tool

**Verdict:** ⛔ Rejected - Too heavy, integration issues

---

### Option D: Smart Upgrade System (RECOMMENDED) ✅

**How It Works:**
```bash
# User says in VS Code Copilot Chat:
"upgrade cortex"

# CORTEX handles:
# 1. Download upgrade package from GitHub
# 2. Backup brain data
# 3. Replace core files
# 4. Apply database migrations
# 5. Merge configs intelligently
# 6. Validate integrity
# 7. Rollback if failure
```

**Pros:**
- ✅ Natural language interface (no commands to remember)
- ✅ Brain preservation built-in
- ✅ Intelligent config merging
- ✅ Automated database migrations
- ✅ Rollback on failure
- ✅ No external dependencies (git, npm, docker)
- ✅ User-friendly (single command)

**Cons:**
- ⚠️ Requires implementation (~2-3 days)
- ⚠️ Needs robust testing

**Verdict:** ✅ RECOMMENDED - Best balance of simplicity, safety, and power

---

## 🏆 Recommended Solution: Smart Upgrade System

### Why This Wins

**1. Simplicity:**
- Single natural language command
- No git/npm/docker knowledge required
- Works in GitHub Copilot Chat (native environment)

**2. Safety:**
- Automatic backups before upgrade
- Rollback mechanism on failure
- Validation gates at every step
- Atomic database transactions

**3. Intelligence:**
- Detects user customizations
- Merges configs (doesn't overwrite)
- Applies schema migrations automatically
- Preserves brain data

**4. Transparency:**
- Dry-run mode shows preview
- Detailed upgrade reports
- Clear rollback instructions
- Audit trail of all changes

**5. Efficiency:**
- Smaller upgrade packages (5 MB vs 15 MB)
- Fast downloads (GitHub Releases)
- Incremental migrations (not full replacement)
- Reuses existing brain data

---

## 📐 Implementation Plan

### Phase 1: Version System (Week 1)
- [ ] Create `.cortex-version` file structure
- [ ] Add version detection to entry point
- [ ] Implement `PRAGMA user_version` tracking
- [ ] Create version comparison utilities

### Phase 2: Backup System (Week 1)
- [ ] Implement atomic backup creation
- [ ] Add SQLite database backup API
- [ ] Create backup restoration logic
- [ ] Add backup retention policy

### Phase 3: Migration System (Week 2)
- [ ] Design migration file format
- [ ] Create migration runner
- [ ] Implement rollback logic
- [ ] Add migration registry tracking

### Phase 4: Config Merge System (Week 2)
- [ ] Implement 3-way merge for YAML
- [ ] Add conflict detection
- [ ] Create merge preview UI
- [ ] Handle array/object merging

### Phase 5: Upgrade Command (Week 3)
- [ ] Natural language command detection
- [ ] GitHub release fetching
- [ ] Upgrade orchestrator
- [ ] Dry-run mode implementation

### Phase 6: Validation & Testing (Week 3)
- [ ] Pre-upgrade validation suite
- [ ] Post-upgrade validation suite
- [ ] Integration tests
- [ ] User acceptance testing

### Phase 7: Documentation (Week 4)
- [ ] Upgrade command documentation
- [ ] Migration guide for developers
- [ ] Rollback procedures
- [ ] Troubleshooting guide

**Total Estimated Time:** 4 weeks (1 developer)

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test version detection
def test_version_detection():
    assert get_cortex_version() == "5.2.0"

# Test backup creation
def test_backup_creation():
    backup_path = create_backup()
    assert backup_path.exists()
    assert validate_backup(backup_path)

# Test migration application
def test_migration_application():
    db = create_test_db()
    apply_migration(db, "001_add_ado_tables.sql")
    assert table_exists(db, "tier2_ado_work_items")

# Test config merging
def test_config_merge():
    base = {"key": "value1"}
    local = {"key": "value2"}
    upgrade = {"key": "value3", "new_key": "new_value"}
    merged = merge_configs(base, local, upgrade)
    assert merged["key"] == "value2"  # Local preserved
    assert merged["new_key"] == "new_value"  # Upgrade added
```

### Integration Tests
```python
# Test full upgrade workflow
def test_full_upgrade():
    # Setup: Install v5.1.0
    install_cortex("5.1.0")
    
    # Create test brain data
    create_test_conversations()
    add_test_patterns()
    
    # Run upgrade
    result = upgrade_cortex("5.2.0")
    
    # Validate
    assert result.success
    assert get_cortex_version() == "5.2.0"
    assert test_conversations_exist()  # Data preserved
    assert test_patterns_exist()       # Data preserved
    assert new_features_available()    # Features added

# Test rollback
def test_rollback():
    original_version = get_cortex_version()
    upgrade_cortex("5.3.0")  # Simulate upgrade
    
    # Trigger rollback
    result = rollback_cortex()
    
    # Validate
    assert result.success
    assert get_cortex_version() == original_version
    assert brain_data_intact()
```

---

## 📊 Success Metrics

### Pre-Launch Metrics
- [ ] 100% test coverage for upgrade system
- [ ] Successfully upgrade 5 real-world CORTEX deployments
- [ ] Zero data loss in all test scenarios
- [ ] Rollback success rate: 100%
- [ ] Average upgrade time: <3 minutes

### Post-Launch Metrics
- [ ] User upgrade success rate: >95%
- [ ] Average upgrade time: <3 minutes
- [ ] Rollback usage: <5% (indicates confidence)
- [ ] User satisfaction: >4.5/5 stars
- [ ] Zero critical bugs reported in first month

---

## 🚦 Rollout Plan

### Phase 1: Internal Testing (Week 1)
- Test on CORTEX development repo
- Simulate upgrades from v5.0, v5.1, v5.2
- Validate with corrupted databases, large brains

### Phase 2: Alpha Testing (Week 2)
- Release to 5-10 trusted users
- Collect feedback on UX
- Fix critical bugs
- Refine error messages

### Phase 3: Beta Release (Week 3)
- Release to 50-100 users
- Monitor upgrade success rates
- Create FAQ based on support tickets
- Optimize performance

### Phase 4: General Availability (Week 4)
- Announce in README, GitHub Releases
- Update installation guide
- Create video tutorial
- Monitor GitHub Issues

---

## ⚠️ Risks & Mitigations

### Risk 1: Data Loss During Upgrade
**Probability:** Low  
**Impact:** Critical  
**Mitigation:**
- Mandatory backup before upgrade
- Atomic transactions for database changes
- Extensive validation tests
- Easy rollback mechanism

### Risk 2: Config Merge Conflicts
**Probability:** Medium  
**Impact:** Medium  
**Mitigation:**
- 3-way merge algorithm (tested with complex YAMLs)
- Manual review option for conflicts
- Conflict preview before applying
- Preserve-local fallback option

### Risk 3: Network Failures During Download
**Probability:** Medium  
**Impact:** Low  
**Mitigation:**
- Resume download support (partial downloads)
- SHA256 checksum validation
- Fallback to cached package if available
- Clear error messages with retry instructions

### Risk 4: Breaking Changes in New Version
**Probability:** Low  
**Impact:** High  
**Mitigation:**
- Breaking change detection in pre-flight
- Migration guides for deprecated features
- Gradual deprecation (warnings first, remove later)
- Rollback option

---

## 📖 Documentation Requirements

### User Documentation
1. **Upgrade Guide:** Step-by-step instructions for "upgrade cortex"
2. **Rollback Guide:** How to revert to previous version
3. **Migration Guide:** How to adapt custom code to new APIs
4. **Troubleshooting:** Common upgrade issues and solutions

### Developer Documentation
1. **Migration File Format:** How to write schema migrations
2. **Config Merge Logic:** How 3-way merge works
3. **Upgrade Architecture:** System design and components
4. **Testing Guide:** How to test upgrades locally

---

## 🎯 Conclusion

**Recommended Solution:** Implement Smart Upgrade System (Option D)

**Key Benefits:**
- ✅ Zero data loss guarantee
- ✅ Single command upgrade
- ✅ Intelligent config merging
- ✅ Automated database migrations
- ✅ Rollback on failure
- ✅ Transparent and user-friendly

**Implementation Timeline:** 4 weeks  
**Estimated Effort:** 1 developer, 160 hours  
**Risk Level:** Low (with proper testing)

**Next Steps:**
1. Approve architecture design
2. Begin Phase 1 implementation (version system)
3. Create test suite for upgrade workflows
4. Alpha test with internal deployments
5. Iterate based on feedback
6. General availability release

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Status:** 🎯 PROPOSED (Awaiting Approval)
