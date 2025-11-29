# Upgrade Orchestrator Guide

**Purpose:** Universal auto-upgrade system with brain preservation and safety features

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

---

## Overview

The Upgrade Orchestrator provides automated CORTEX upgrades from the remote repository with comprehensive safety features, brain data preservation, and rollback capabilities.

**Key Features:**
- **Universal Compatibility:** Works for standalone and embedded installations
- **Auto-Detection:** Identifies installation type and applies appropriate upgrade method
- **Brain Preservation:** Automatic backup of all knowledge graphs, conversations, configs
- **Safety Validation:** Path validation prevents files escaping CORTEX directory
- **Rollback Support:** Automatic backup before upgrade, easy rollback on failure
- **Migration System:** Runs database schema updates automatically
- **Post-Upgrade Validation:** Comprehensive test suite ensures functionality

---

## Usage

### Basic Usage

```python
from src.orchestrators.upgrade_orchestrator import UpgradeOrchestrator

# Initialize with optional cortex path
orchestrator = UpgradeOrchestrator(cortex_path="/path/to/CORTEX")

# Check for updates
update_info = orchestrator.check_for_updates()
if update_info['update_available']:
    print(f"New version available: {update_info['latest_version']}")
    
    # Perform upgrade
    result = orchestrator.upgrade()
    
    if result['success']:
        print(f"✅ Upgraded to {result['new_version']}")
    else:
        print(f"❌ Upgrade failed: {result['error']}")
        # Automatic rollback performed
else:
    print("✅ CORTEX is up to date")
```

### Natural Language Commands

**Commands:**
- `upgrade` or `upgrade cortex` - Check and apply upgrades
- `cortex version` or `check version` - Show current version
- `update cortex` - Alias for upgrade

**Examples:**
```
User: "upgrade cortex"
CORTEX: Checking for CORTEX updates...
        
        Current Version: 3.2.0
        Latest Version: 3.3.0
        Update Available: Yes
        
        Starting upgrade process...
        [1/8] Detecting installation type... ✅ Embedded
        [2/8] Creating brain backup... ✅ Backup saved
        [3/8] Downloading updates... ✅ Latest code fetched
        [4/8] Validating file paths... ✅ All paths safe
        [5/8] Applying updates... ✅ Files copied
        [6/8] Running migrations... ✅ Schemas updated
        [7/8] Post-upgrade validation... ✅ All tests passed
        [8/8] Cleanup... ✅ Complete
        
        ✅ Successfully upgraded to v3.3.0
           Brain data preserved
           Backup location: CORTEX/backups/pre-upgrade-20251125_143022/
```

---

## API Reference

### Class: `UpgradeOrchestrator`

Orchestrates CORTEX auto-upgrade from remote repository.

#### Methods

**`__init__(cortex_path: str = None)`**

Initialize upgrade orchestrator.

**Parameters:**
- `cortex_path` (str, optional): Path to CORTEX directory. Auto-detected if not provided.

**Returns:**
- `UpgradeOrchestrator`: Initialized orchestrator instance

---

**`check_for_updates() -> dict`**

Check if newer CORTEX version available.

**Parameters:**
- None

**Returns:**
- `dict`: Update information:
  ```python
  {
      'current_version': '3.2.0',
      'latest_version': '3.3.0',
      'update_available': True,
      'release_notes_url': 'https://github.com/asifhussain60/CORTEX/releases/tag/v3.3.0'
  }
  ```

---

**`upgrade(force: bool = False, skip_backup: bool = False) -> dict`**

Perform CORTEX upgrade with safety checks.

**Parameters:**
- `force` (bool, optional): Skip version check and force upgrade. Default False.
- `skip_backup` (bool, optional): Skip brain backup (NOT RECOMMENDED). Default False.

**Returns:**
- `dict`: Upgrade result:
  ```python
  {
      'success': True,
      'old_version': '3.2.0',
      'new_version': '3.3.0',
      'backup_path': 'CORTEX/backups/pre-upgrade-20251125_143022/',
      'migrations_applied': ['add_element_mappings_schema.py'],
      'validation_passed': True
  }
  ```

---

**`list_backups() -> list`**

List all available brain backups.

**Parameters:**
- None

**Returns:**
- `list`: Backup information:
  ```python
  [
      {'date': '2025-11-25 14:30:22', 'path': 'backups/pre-upgrade-...', 'size_mb': 45.2},
      {'date': '2025-11-20 09:15:10', 'path': 'backups/manual-...', 'size_mb': 42.8}
  ]
  ```

---

### Internal Methods

**`_get_current_version() -> str`**

Read current version from VERSION file.

**`_get_remote_version() -> str`**

Fetch latest version from GitHub repository.

**`_compare_versions(current: str, remote: str) -> bool`**

Compare semantic versions (returns True if remote is newer).

**`_get_current_branch() -> str`**

Get current git branch name.

**`_create_backup() -> str`**

Create timestamped backup of cortex-brain directory.

**`_rollback(backup_path: str) -> bool`**

Restore from backup on upgrade failure.

**`_run_migrations() -> list`**

Execute database migration scripts in migrations/ directory

---

## Configuration

**cortex.config.json:**

```json
{
  "upgrade": {
    "auto_check": true,
    "check_interval": "daily",
    "auto_backup": true,
    "backup_retention_days": 30,
    "skip_validation": false,
    "remote_url": "https://github.com/asifhussain60/CORTEX.git",
    "remote_branch": "main"
  }
}
```

**Required:**
- Git installed and accessible
- Network connectivity to GitHub
- Write permissions to CORTEX directory

**Optional:**
- .cortex-embedded marker file (for explicit embedded detection)

---

## Examples

### Example 1: Check for Updates

```python
from src.orchestrators.upgrade_orchestrator import UpgradeOrchestrator

orchestrator = UpgradeOrchestrator()
info = orchestrator.check_for_updates()

if info['update_available']:
    print(f"Update available: {info['current_version']} → {info['latest_version']}")
    print(f"Release notes: {info['release_notes_url']}")
else:
    print("✅ CORTEX is up to date")
```

**Output:**
```
Update available: 3.2.0 → 3.3.0
Release notes: https://github.com/asifhussain60/CORTEX/releases/tag/v3.3.0
```

### Example 2: Perform Upgrade

```python
from src.orchestrators.upgrade_orchestrator import UpgradeOrchestrator

orchestrator = UpgradeOrchestrator()

# Check first
if orchestrator.check_for_updates()['update_available']:
    # Upgrade with automatic backup
    result = orchestrator.upgrade()
    
    if result['success']:
        print(f"✅ Upgraded: {result['old_version']} → {result['new_version']}")
        print(f"Backup: {result['backup_path']}")
    else:
        print(f"❌ Upgrade failed: {result['error']}")
        print("Rollback automatically performed")
```

### Example 3: List and Restore Backups

```python
from src.orchestrators.upgrade_orchestrator import UpgradeOrchestrator

orchestrator = UpgradeOrchestrator()

# List available backups
backups = orchestrator.list_backups()
for backup in backups:
    print(f"{backup['date']}: {backup['path']} ({backup['size_mb']} MB)")

# Rollback to specific backup (if needed)
if backups:
    orchestrator._rollback(backups[0]['path'])
```

---

## Integration

**Entry Points:**
- `upgrade` or `upgrade cortex` - Natural language command
- `cortex version` - Show current version
- `update cortex` - Alias for upgrade

**Dependencies:**
- Git (for fetching updates)
- Network connectivity (GitHub access)
- File system permissions (read/write CORTEX directory)

**Response Template:**
- Template ID: `upgrade_cortex`
- Triggers: `upgrade`, `upgrade cortex`, `cortex version`, `check version`

**Safety Features:**
- Auto-detects standalone vs embedded installation
- Validates all file paths before copying
- Creates automatic brain backup
- Runs post-upgrade validation tests
- Automatic rollback on failure

**See Also:**
- Upgrade Guide (modules/upgrade-guide.md) - Detailed upgrade documentation
- System Alignment Guide - Post-upgrade validation
- Brain Protection Rules - What gets preserved

---

## Troubleshooting

**Issue:** "Git merge failed - unrelated histories"  
**Solution:** System auto-detects this and switches to safe file-copy method. No action needed.

**Issue:** "Files would escape CORTEX directory"  
**Solution:** Path validation detected unsafe upgrade. Report this to GitHub issues - indicates upstream repository structure problem.

**Issue:** "Network error fetching updates"  
**Solution:** Check internet connectivity. Verify GitHub accessible: `git ls-remote https://github.com/asifhussain60/CORTEX.git`

**Issue:** "Permission denied during upgrade"  
**Solution:** Ensure write permissions to CORTEX directory. Windows: Check folder properties → Security tab. Linux/Mac: `chmod -R 755 CORTEX/`

**Issue:** "Post-upgrade validation failed"  
**Solution:** Check validation output in logs. Automatic rollback should have restored previous version. Try upgrade again or report issue.

**Issue:** "Brain data missing after upgrade"  
**Solution:** This should never happen (brain is backed up automatically). Restore from backup:
```python
orchestrator.list_backups()  # Find latest backup
orchestrator._rollback(backup_path)  # Restore
```

**Issue:** "Embedded installation not detected"  
**Solution:** Create `.cortex-embedded` marker file:
```bash
cd CORTEX
echo "# CORTEX Embedded Installation" > .cortex-embedded
```

---

## Safety Guarantees

**What's Protected:**
- ✅ All brain databases (Tier 1, Tier 2)
- ✅ User configurations (cortex.config.json)
- ✅ Custom capabilities and templates
- ✅ Planning documents and reports
- ✅ Conversation history

**What Gets Updated:**
- ✅ Core CORTEX code (orchestrators, agents, workflows)
- ✅ Documentation files
- ✅ Response templates (merged with existing)
- ✅ Database schemas (via migrations)

**Automatic Actions on Failure:**
- ✅ Rollback to previous version
- ✅ Restore brain data from backup
- ✅ Notify user of failure reason
- ✅ Preserve backup for manual recovery

---

**Last Updated:** November 25, 2025  
**Version:** 1.0
