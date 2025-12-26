# CORTEX Deployment Mechanisms

**Version:** 1.0  
**Status:** 🎯 PROPOSED (Awaiting Approval)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Created:** 2025-11-23

---

## 🎯 Executive Summary

**Current Problem:** Manual folder copy from `publish/` to user repos is error-prone and doesn't distinguish between:
1. **Initial Setup** (fresh install, no brain data exists)
2. **Upgrade** (preserve existing brain, update core)

**Solution:** Two separate automated workflows with intelligent detection.

---

## 📊 Real-World Deployment Analysis

### NOOR CANVAS CORTEX Structure (Active Brain)

Based on your production deployment at `D:\PROJECTS\NOOR CANVAS\CORTEX`:

```
NOOR CANVAS/
└── CORTEX/
    ├── .github/
    │   └── prompts/
    │       └── CORTEX.prompt.md
    ├── cortex-brain/
    │   ├── brain-protection-rules.yaml
    │   ├── capabilities.yaml
    │   ├── conversation-history.db        ← ACTIVE BRAIN DATA
    │   ├── development-context.yaml
    │   ├── knowledge-graph.yaml
    │   ├── migrate_brain_db.py
    │   ├── publish-config.yaml
    │   ├── response-templates.yaml
    │   └── documents/                     ← USER DOCUMENTS
    ├── scripts/
    ├── src/
    └── workflows/
```

**Key Observations:**
- ✅ Has active conversation history database
- ✅ Has learned patterns in knowledge-graph.yaml
- ✅ Has user-generated documents
- ✅ This is a WORKING BRAIN that must be preserved during upgrades

---

## 🚀 Deployment Workflows

### Workflow 1: Initial Setup (Fresh Install)

**Trigger:** No CORTEX folder exists in target repo

**User Action:**
```bash
# In user's project repo (e.g., D:\PROJECTS\MY-NEW-APP)
cortex setup
```

**Or via natural language in GitHub Copilot Chat:**
```
"setup cortex in this workspace"
"install cortex"
"initialize cortex"
```

**What Happens:**

```
User: "setup cortex"
    ↓
┌──────────────────────────────────────────────┐
│ Phase 1: Detection                           │
│ • Check if CORTEX/ folder exists             │
│ • Result: Not found → Initial setup mode     │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 2: Download Package                    │
│ • Fetch latest release from GitHub           │
│ • Package: cortex-v5.2.0-full.zip           │
│ • Validate SHA256 checksum                   │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 3: Extract & Setup                     │
│ • Extract to CORTEX/ folder                  │
│ • Initialize empty brain databases:          │
│   - tier1/working_memory.db (empty)          │
│   - tier2/knowledge_graph.db (empty)         │
│   - tier3/development-context.db (empty)     │
│ • Create .cortex-version file                │
│ • Create cortex.config.json (workspace)      │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 4: Workspace Integration               │
│ • Add .github/copilot-instructions.md        │
│ • Update user's .gitignore:                  │
│   CORTEX/*.db                                │
│   CORTEX/tier*/                              │
│   CORTEX/logs/                               │
│ • Create CORTEX/.gitignore (selective)       │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 5: Validation & Welcome                │
│ • Run health check                           │
│ • Test brain connectivity                    │
│ • Generate setup report                      │
│ • Display welcome message                    │
└──────────────────────────────────────────────┘
    ↓
✅ SETUP COMPLETE
```

**Output Structure:**
```
MY-NEW-APP/
├── .github/
│   └── copilot-instructions.md         ← Points to CORTEX
├── .gitignore                          ← Updated
├── CORTEX/                             ← NEW
│   ├── .cortex-version                 ← Version: 5.2.0
│   ├── .gitignore                      ← Selective tracking
│   ├── .github/
│   │   └── prompts/
│   ├── cortex-brain/
│   │   ├── tier1/
│   │   │   └── working_memory.db       ← Empty (0 KB)
│   │   ├── tier2/
│   │   │   └── knowledge_graph.db      ← Empty (0 KB)
│   │   ├── tier3/
│   │   ├── response-templates.yaml     ← Base templates
│   │   ├── capabilities.yaml           ← Base capabilities
│   │   ├── user-dictionary.yaml        ← Empty
│   │   └── documents/                  ← Empty
│   ├── src/
│   ├── scripts/
│   └── workflows/
└── cortex.config.json                  ← Workspace config
```

---

### Workflow 2: Upgrade (Preserve Brain)

**Trigger:** CORTEX folder exists with `.cortex-version` file

**User Action:**
```bash
# In user's project repo (e.g., D:\PROJECTS\NOOR CANVAS)
cortex upgrade
```

**Or via natural language:**
```
"upgrade cortex"
"update cortex to latest"
"check for cortex updates"
```

**What Happens:**

```
User: "upgrade cortex"
    ↓
┌──────────────────────────────────────────────┐
│ Phase 1: Detection                           │
│ • Check if CORTEX/ folder exists             │
│ • Result: Found → Upgrade mode               │
│ • Read .cortex-version: v5.1.0               │
│ • Latest available: v5.2.0                   │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 2: Brain Inventory                     │
│ • Scan existing brain data:                  │
│   ✅ conversation-history.db (15 MB)         │
│   ✅ knowledge-graph.yaml (50 KB)            │
│   ✅ documents/ (127 files)                  │
│   ✅ user-dictionary.yaml (5 KB)             │
│ • Total brain size: 20 MB                    │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 3: Pre-Upgrade Backup                  │
│ • Create backup:                             │
│   CORTEX/cortex-brain/backups/               │
│     pre-upgrade-20251123_143000/             │
│ • Backup size: 20 MB                         │
│ • Backup time: 5 seconds                     │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 4: Download Upgrade Package            │
│ • Fetch: cortex-v5.2.0-upgrade.zip          │
│ • Size: 5 MB (67% smaller than full)         │
│ • Validate SHA256                            │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 5: Core Upgrade (Preserve Brain)       │
│ • Extract to temp: CORTEX-temp/              │
│ • Replace core files:                        │
│   ✅ src/ (overwrite)                        │
│   ✅ scripts/ (overwrite)                    │
│   ✅ .github/prompts/ (overwrite)            │
│ • Preserve brain data:                       │
│   ⏩ cortex-brain/*.db (skip)                │
│   ⏩ cortex-brain/documents/ (skip)          │
│   ⏩ cortex-brain/user-dictionary.yaml (skip)│
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 6: Config Merge                        │
│ • Merge response-templates.yaml:             │
│   Base (v5.1.0) + Local + Upgrade (v5.2.0)  │
│   → Merged (keep custom + add new)           │
│ • Merge capabilities.yaml (same logic)       │
│ • Update .cortex-version → 5.2.0            │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 7: Schema Migration                    │
│ • Detect schema mismatches:                  │
│   tier2/knowledge_graph.db: v1 → v2          │
│ • Apply migration: 001_add_ado_tables.sql    │
│ • Validate foreign keys                      │
└──────────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────────┐
│ Phase 8: Validation                          │
│ • Test brain queries                         │
│ • Verify file integrity                      │
│ • Check agent functionality                  │
│ • Generate upgrade report                    │
└──────────────────────────────────────────────┘
    ↓
✅ UPGRADE COMPLETE
   Brain preserved: 20 MB, 127 conversations, 43 patterns
```

---

## 🔍 Intelligent Detection Logic

### How CORTEX Knows: Setup vs Upgrade

```python
class DeploymentDetector:
    """Detects deployment type and validates state."""
    
    def detect_deployment_type(self, workspace_path: Path) -> DeploymentType:
        """Determine if this is setup or upgrade."""
        cortex_dir = workspace_path / "CORTEX"
        version_file = cortex_dir / ".cortex-version"
        
        # Case 1: No CORTEX folder → Initial Setup
        if not cortex_dir.exists():
            return DeploymentType.INITIAL_SETUP
        
        # Case 2: CORTEX exists but no version file → Legacy Setup
        if not version_file.exists():
            return DeploymentType.LEGACY_UPGRADE  # Need migration
        
        # Case 3: Version file exists → Upgrade
        current_version = self._read_version(version_file)
        latest_version = self._fetch_latest_version()
        
        if current_version == latest_version:
            return DeploymentType.UP_TO_DATE
        else:
            return DeploymentType.UPGRADE
    
    def validate_brain_integrity(self, cortex_dir: Path) -> BrainHealthReport:
        """Check if brain data exists and is valid."""
        report = BrainHealthReport()
        
        # Check databases
        tier1_db = cortex_dir / "cortex-brain/tier1/working_memory.db"
        tier2_db = cortex_dir / "cortex-brain/tier2/knowledge_graph.db"
        
        report.has_conversations = tier1_db.exists() and tier1_db.stat().st_size > 0
        report.has_patterns = tier2_db.exists() and tier2_db.stat().st_size > 0
        
        # Check documents
        docs_dir = cortex_dir / "cortex-brain/documents"
        if docs_dir.exists():
            report.document_count = len(list(docs_dir.rglob("*.md")))
        
        return report
```

---

## 📦 Package Distribution Strategy

### GitHub Release Assets

**Full Package (Initial Setup):**
```
Release: CORTEX v5.2.0
├── cortex-v5.2.0-full.zip          (15 MB)
│   ├── CORTEX/
│   │   ├── .cortex-version
│   │   ├── .github/
│   │   ├── cortex-brain/           (Empty databases)
│   │   ├── src/
│   │   ├── scripts/
│   │   └── workflows/
│   └── INSTALL.md
└── SHA256SUMS.txt
```

**Upgrade Package (Existing Deployments):**
```
Release: CORTEX v5.2.0
├── cortex-v5.2.0-upgrade.zip       (5 MB)
│   ├── src/                        (Core code only)
│   ├── scripts/                    (User scripts)
│   ├── .github/prompts/            (Entry points)
│   ├── cortex-brain/
│   │   ├── migrations/             (Schema upgrades)
│   │   ├── response-templates.yaml (Base)
│   │   ├── capabilities.yaml       (Base)
│   │   └── schema.sql              (Latest schema)
│   ├── .cortex-version
│   └── UPGRADE-NOTES.md
└── SHA256SUMS.txt
```

---

## 🔧 Implementation: Setup Command

### Entry Point Script

**File:** `scripts/cortex_setup.py`

```python
"""
CORTEX Setup/Upgrade Script
Intelligently detects deployment type and executes appropriate workflow.

Usage:
    python scripts/cortex_setup.py
    
Or via natural language in GitHub Copilot Chat:
    "setup cortex"
    "upgrade cortex"
"""

import sys
from pathlib import Path
from enum import Enum
from typing import Optional

class DeploymentType(Enum):
    INITIAL_SETUP = "initial_setup"
    UPGRADE = "upgrade"
    LEGACY_UPGRADE = "legacy_upgrade"  # Upgrade from pre-version-tracking
    UP_TO_DATE = "up_to_date"

class CortexDeploymentOrchestrator:
    """Orchestrates CORTEX setup and upgrades."""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        """Initialize orchestrator."""
        self.workspace_path = workspace_path or Path.cwd()
        self.cortex_dir = self.workspace_path / "CORTEX"
        self.detector = DeploymentDetector()
        self.setup_handler = InitialSetupHandler()
        self.upgrade_handler = UpgradeHandler()
    
    def execute(self) -> bool:
        """Main entry point - detect and execute."""
        print("🧠 CORTEX Deployment Orchestrator")
        print("Author: Asif Hussain | © 2024-2025\n")
        
        # Detect deployment type
        deployment_type = self.detector.detect_deployment_type(self.workspace_path)
        
        if deployment_type == DeploymentType.INITIAL_SETUP:
            return self._run_initial_setup()
        
        elif deployment_type == DeploymentType.UPGRADE:
            return self._run_upgrade()
        
        elif deployment_type == DeploymentType.LEGACY_UPGRADE:
            return self._run_legacy_upgrade()
        
        elif deployment_type == DeploymentType.UP_TO_DATE:
            print("✅ CORTEX is already up-to-date!")
            return True
        
        return False
    
    def _run_initial_setup(self) -> bool:
        """Execute initial setup workflow."""
        print("🎯 Deployment Type: INITIAL SETUP")
        print("Creating fresh CORTEX installation...\n")
        
        # Phase 1: Download
        print("⚡ Phase 1/5: Downloading CORTEX package...")
        package_path = self.setup_handler.download_full_package()
        print(f"   ✅ Downloaded: {package_path}\n")
        
        # Phase 2: Extract
        print("⚡ Phase 2/5: Extracting files...")
        self.setup_handler.extract_package(package_path, self.cortex_dir)
        print(f"   ✅ Extracted to: {self.cortex_dir}\n")
        
        # Phase 3: Initialize Brain
        print("⚡ Phase 3/5: Initializing brain databases...")
        self.setup_handler.initialize_brain(self.cortex_dir)
        print("   ✅ Created empty databases\n")
        
        # Phase 4: Workspace Integration
        print("⚡ Phase 4/5: Integrating with workspace...")
        self.setup_handler.integrate_workspace(self.workspace_path)
        print("   ✅ Updated .gitignore")
        print("   ✅ Created .github/copilot-instructions.md\n")
        
        # Phase 5: Validation
        print("⚡ Phase 5/5: Running validation...")
        if self.setup_handler.validate_installation(self.cortex_dir):
            print("   ✅ All checks passed\n")
            self._show_success_message(is_setup=True)
            return True
        else:
            print("   ❌ Validation failed\n")
            return False
    
    def _run_upgrade(self) -> bool:
        """Execute upgrade workflow."""
        print("🎯 Deployment Type: UPGRADE")
        
        # Get version info
        current_version = self.detector.get_current_version(self.cortex_dir)
        latest_version = self.detector.get_latest_version()
        print(f"Upgrading: v{current_version} → v{latest_version}\n")
        
        # Brain inventory
        print("🔍 Analyzing brain data...")
        brain_report = self.detector.validate_brain_integrity(self.cortex_dir)
        print(f"   • Conversations: {brain_report.conversation_count}")
        print(f"   • Learned patterns: {brain_report.pattern_count}")
        print(f"   • Documents: {brain_report.document_count}")
        print(f"   • Brain size: {brain_report.size_mb} MB\n")
        
        # Confirmation
        response = input("Continue with upgrade? (Y/N): ")
        if response.upper() != 'Y':
            print("Upgrade cancelled.")
            return False
        
        # Phase 1: Backup
        print("\n⚡ Phase 1/7: Creating backup...")
        backup_path = self.upgrade_handler.create_backup(self.cortex_dir)
        print(f"   ✅ Backup: {backup_path}\n")
        
        # Phase 2: Download
        print("⚡ Phase 2/7: Downloading upgrade package...")
        package_path = self.upgrade_handler.download_upgrade_package(latest_version)
        print(f"   ✅ Downloaded: {package_path}\n")
        
        # Phase 3: Core Upgrade
        print("⚡ Phase 3/7: Upgrading core files...")
        files_updated = self.upgrade_handler.upgrade_core_files(
            package_path, self.cortex_dir, preserve_brain=True
        )
        print(f"   ✅ Updated {files_updated} files\n")
        
        # Phase 4: Config Merge
        print("⚡ Phase 4/7: Merging configurations...")
        conflicts = self.upgrade_handler.merge_configs(self.cortex_dir, latest_version)
        if conflicts:
            print(f"   ⚠️  {len(conflicts)} conflicts detected (auto-resolved)")
        else:
            print("   ✅ No conflicts\n")
        
        # Phase 5: Schema Migration
        print("⚡ Phase 5/7: Applying database migrations...")
        migrations_applied = self.upgrade_handler.apply_migrations(self.cortex_dir)
        print(f"   ✅ Applied {migrations_applied} migrations\n")
        
        # Phase 6: Validation
        print("⚡ Phase 6/7: Running validation...")
        if self.upgrade_handler.validate_upgrade(self.cortex_dir):
            print("   ✅ All checks passed\n")
        else:
            print("   ❌ Validation failed - rolling back...")
            self.upgrade_handler.rollback(backup_path, self.cortex_dir)
            return False
        
        # Phase 7: Cleanup
        print("⚡ Phase 7/7: Cleanup...")
        self.upgrade_handler.cleanup_temp_files()
        print("   ✅ Temp files removed\n")
        
        self._show_success_message(is_setup=False, brain_report=brain_report)
        return True
    
    def _show_success_message(self, is_setup: bool, brain_report=None):
        """Display success message with next steps."""
        if is_setup:
            print("=" * 60)
            print("✅ CORTEX SETUP COMPLETE")
            print("=" * 60)
            print("\n🎉 CORTEX is ready to use!")
            print("\n📚 Quick Start:")
            print("   • Type 'help' in GitHub Copilot Chat")
            print("   • Say 'onboard this application' to start")
            print("   • Ask CORTEX anything!")
            print("\n📖 Documentation:")
            print("   • README: CORTEX/README.md")
            print("   • Entry Point: CORTEX/.github/prompts/CORTEX.prompt.md")
        else:
            print("=" * 60)
            print("✅ CORTEX UPGRADE COMPLETE")
            print("=" * 60)
            print(f"\n🎉 CORTEX v{self.detector.get_current_version(self.cortex_dir)} is ready!")
            print("\n🔄 Your brain is intact:")
            print(f"   • {brain_report.conversation_count} conversations preserved")
            print(f"   • {brain_report.pattern_count} learned patterns retained")
            print(f"   • {brain_report.document_count} documents preserved")
            print("\n📊 Upgrade Report:")
            print(f"   CORTEX/cortex-brain/documents/reports/UPGRADE-REPORT-*.md")

def main():
    """Main entry point."""
    orchestrator = CortexDeploymentOrchestrator()
    success = orchestrator.execute()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

---

## 🎨 User Experience Examples

### Example 1: Fresh Install (New Project)

```
Developer: Working on new project "E-Commerce Platform"
Location: D:\PROJECTS\E-COMMERCE
Status: No CORTEX installed

User (in GitHub Copilot Chat): "setup cortex"

CORTEX:
  🧠 CORTEX Deployment Orchestrator
  Author: Asif Hussain | © 2024-2025
  
  🎯 Deployment Type: INITIAL SETUP
  Creating fresh CORTEX installation...
  
  ⚡ Phase 1/5: Downloading CORTEX package...
     • Fetching: cortex-v5.2.0-full.zip
     • Size: 15 MB
     • SHA256: a7b3c4d5... ✅ Valid
     ✅ Downloaded: cortex-v5.2.0-full.zip
  
  ⚡ Phase 2/5: Extracting files...
     ✅ Extracted to: D:\PROJECTS\E-COMMERCE\CORTEX
  
  ⚡ Phase 3/5: Initializing brain databases...
     • Created tier1/working_memory.db (empty)
     • Created tier2/knowledge_graph.db (empty)
     • Created tier3/development-context.db (empty)
     ✅ Created empty databases
  
  ⚡ Phase 4/5: Integrating with workspace...
     • Added .github/copilot-instructions.md
     • Updated .gitignore (CORTEX/*.db, CORTEX/tier*/)
     ✅ Updated .gitignore
     ✅ Created .github/copilot-instructions.md
  
  ⚡ Phase 5/5: Running validation...
     • Brain connectivity: ✅
     • File structure: ✅
     • Agent functionality: ✅
     ✅ All checks passed
  
  ============================================================
  ✅ CORTEX SETUP COMPLETE
  ============================================================
  
  🎉 CORTEX is ready to use!
  
  📚 Quick Start:
     • Type 'help' in GitHub Copilot Chat
     • Say 'onboard this application' to start
     • Ask CORTEX anything!
  
  📖 Documentation:
     • README: CORTEX/README.md
     • Entry Point: CORTEX/.github/prompts/CORTEX.prompt.md
```

---

### Example 2: Upgrade (Existing Project with Brain)

```
Developer: Working on "NOOR CANVAS" project
Location: D:\PROJECTS\NOOR CANVAS
Status: CORTEX v5.1.0 installed, active brain (20 MB, 127 conversations)

User (in GitHub Copilot Chat): "upgrade cortex"

CORTEX:
  🧠 CORTEX Deployment Orchestrator
  Author: Asif Hussain | © 2024-2025
  
  🎯 Deployment Type: UPGRADE
  Upgrading: v5.1.0 → v5.2.0
  
  🔍 Analyzing brain data...
     • Conversations: 127
     • Learned patterns: 43
     • Documents: 89
     • Brain size: 20 MB
  
  Continue with upgrade? (Y/N): Y
  
  ⚡ Phase 1/7: Creating backup...
     • Backup location: CORTEX/cortex-brain/backups/pre-upgrade-20251123_143000/
     • Backup size: 20 MB
     • Backup time: 5 seconds
     ✅ Backup: pre-upgrade-20251123_143000
  
  ⚡ Phase 2/7: Downloading upgrade package...
     • Fetching: cortex-v5.2.0-upgrade.zip
     • Size: 5 MB (67% smaller than full package)
     • SHA256: b8c4d5e6... ✅ Valid
     ✅ Downloaded: cortex-v5.2.0-upgrade.zip
  
  ⚡ Phase 3/7: Upgrading core files...
     • Replacing src/ (overwrite)
     • Replacing scripts/ (overwrite)
     • Replacing .github/prompts/ (overwrite)
     • Preserving cortex-brain/*.db (skip)
     • Preserving cortex-brain/documents/ (skip)
     ✅ Updated 47 files
  
  ⚡ Phase 4/7: Merging configurations...
     • response-templates.yaml: Merged (12 custom triggers preserved)
     • capabilities.yaml: Merged (1 custom operation preserved)
     ✅ No conflicts
  
  ⚡ Phase 5/7: Applying database migrations...
     • tier2/knowledge_graph.db: v1 → v2
     • Applied migration: 001_add_ado_tables.sql
     • Applied migration: 002_add_feedback_tables.sql
     ✅ Applied 2 migrations
  
  ⚡ Phase 6/7: Running validation...
     • Brain queries: ✅
     • Database integrity: ✅
     • Agent functionality: ✅
     • Version consistency: ✅
     ✅ All checks passed
  
  ⚡ Phase 7/7: Cleanup...
     • Removed temp files
     ✅ Temp files removed
  
  ============================================================
  ✅ CORTEX UPGRADE COMPLETE
  ============================================================
  
  🎉 CORTEX v5.2.0 is ready!
  
  🔄 Your brain is intact:
     • 127 conversations preserved
     • 43 learned patterns retained
     • 89 documents preserved
  
  🆕 New features available:
     • ADO Planning System
     • Enhanced response templates
     • Brain import/export
  
  📊 Upgrade Report:
     CORTEX/cortex-brain/documents/reports/UPGRADE-REPORT-20251123_143000.md
  
  Type "help" to see what's new!
```

---

## 🔒 Selective Git Tracking

### User Repo .gitignore (Auto-Updated)

**File:** `.gitignore` (in user's project root, e.g., `D:\PROJECTS\NOOR CANVAS\.gitignore`)

```gitignore
# CORTEX Brain Data (local only, not committed)
CORTEX/*.db
CORTEX/*.db-shm
CORTEX/*.db-wal
CORTEX/tier1/
CORTEX/tier2/
CORTEX/tier3/
CORTEX/logs/
CORTEX/cortex-brain/backups/
CORTEX/cortex-brain/documents/  # Optional: Allow committing user docs

# CORTEX Core (tracked - can be committed)
# Allows sharing CORTEX setup with team
!CORTEX/.cortex-version
!CORTEX/.github/
!CORTEX/cortex-brain/response-templates.yaml
!CORTEX/cortex-brain/capabilities.yaml
!CORTEX/src/
!CORTEX/scripts/
```

**Result:**
- ✅ Brain data stays local (conversations, patterns)
- ✅ Core CORTEX code can be committed (optional, for team sharing)
- ✅ Version file tracked (helps detect upgrades)

---

### CORTEX Internal .gitignore

**File:** `CORTEX/.gitignore` (inside CORTEX folder)

```gitignore
# Brain Data (never commit)
*.db
*.db-shm
*.db-wal
tier1/
tier2/
tier3/
logs/
cortex-brain/backups/

# Workspace-Specific (never commit)
cortex.config.json

# Temporary Files
*.tmp
*.temp
crawler-temp/
sweeper-logs/

# Allow tracking core files
!.cortex-version
!.github/
!cortex-brain/*.yaml
!cortex-brain/schema.sql
!cortex-brain/migrations/
!src/
!scripts/
!workflows/
```

---

## 📊 Comparison: Old vs New

### Old Method (Manual Copy)

```powershell
# Manual process (error-prone)
cd D:\PROJECTS\CORTEX
.\scripts\build_package.py  # Build publish package

# Copy to user repo
cd D:\PROJECTS\NOOR CANVAS
Remove-Item CORTEX -Recurse -Force  # ⚠️ DELETES BRAIN DATA
Copy-Item D:\PROJECTS\CORTEX\publish\CORTEX .\ -Recurse

# Result: Brain data lost, manual restore needed
```

**Problems:**
- ❌ Deletes active brain data
- ❌ No version tracking
- ❌ No config merging
- ❌ No schema migrations
- ❌ Manual process (requires remembering steps)

---

### New Method (Automated)

```
# In user repo
User: "upgrade cortex"

# CORTEX automatically:
# 1. Detects it's an upgrade (not setup)
# 2. Backs up brain data
# 3. Downloads upgrade package
# 4. Replaces core, preserves brain
# 5. Merges configs intelligently
# 6. Applies database migrations
# 7. Validates everything
# 8. Rolls back if failure

# Result: Brain preserved, core upgraded, zero data loss
```

**Benefits:**
- ✅ Zero data loss (automatic backup)
- ✅ Version tracking (knows what to upgrade)
- ✅ Config merging (keeps customizations)
- ✅ Schema migrations (auto-applied)
- ✅ Single command (natural language)
- ✅ Rollback on failure (safety net)

---

## 🚦 Decision Matrix

### When to Use Setup vs Upgrade

| Scenario | Command | Package | Brain Handling |
|----------|---------|---------|----------------|
| **New project, no CORTEX** | `setup cortex` | Full (15 MB) | Create empty databases |
| **Existing CORTEX, no brain data** | `setup cortex` | Full (15 MB) | Create empty databases |
| **Existing CORTEX, active brain** | `upgrade cortex` | Upgrade (5 MB) | Preserve 100% of data |
| **Broken CORTEX, want fresh start** | `setup cortex --force` | Full (15 MB) | Backup old, create new |
| **Test new version, keep old** | `upgrade cortex --dry-run` | None (preview) | No changes |

---

## 🎯 Implementation Checklist

### Phase 1: Detection System (Week 1)
- [ ] Create `DeploymentDetector` class
- [ ] Implement `.cortex-version` file reading/writing
- [ ] Add brain integrity validation
- [ ] Test detection logic with real repos

### Phase 2: Setup Handler (Week 1)
- [ ] Create `InitialSetupHandler` class
- [ ] Implement GitHub release fetching
- [ ] Add package extraction logic
- [ ] Workspace integration (.gitignore updates)
- [ ] Validation suite

### Phase 3: Upgrade Handler (Week 2)
- [ ] Create `UpgradeHandler` class
- [ ] Implement backup creation
- [ ] Selective file replacement (preserve brain)
- [ ] Config merge logic (3-way merge)
- [ ] Schema migration runner
- [ ] Rollback mechanism

### Phase 4: Entry Points (Week 2)
- [ ] Natural language command detection
- [ ] GitHub Copilot Chat integration
- [ ] CLI script (`cortex_setup.py`)
- [ ] Progress reporting (phases 1/7, 2/7, etc.)
- [ ] Success/error messages

### Phase 5: Testing (Week 3)
- [ ] Unit tests for detection
- [ ] Integration tests for setup
- [ ] Integration tests for upgrade
- [ ] Real-world testing (NOOR CANVAS repo)
- [ ] Edge case testing (corrupted brain, network failures)

### Phase 6: Documentation (Week 3)
- [ ] User guide (setup vs upgrade)
- [ ] Developer guide (extend/customize)
- [ ] Troubleshooting guide
- [ ] Video tutorials

---

## 📖 Next Steps

1. **Approve Deployment Mechanisms** - Review this design
2. **Implement Detection System** - Start with `DeploymentDetector`
3. **Test on Real Repos** - Use NOOR CANVAS as test case
4. **Iterate Based on Feedback** - Refine based on real usage
5. **Document Everything** - User-facing and developer docs

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0  
**Status:** 🎯 PROPOSED (Awaiting Approval)
