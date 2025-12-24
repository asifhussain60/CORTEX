# CORTEX Upgrade Guide

**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Last Updated:** 2025-11-23

---

## 🎯 Overview

The CORTEX Upgrade System safely updates your CORTEX installation while preserving:
- ✅ Conversation history and learned patterns
- ✅ Workspace-specific configurations
- ✅ User-created documents and planning files
- ✅ Custom templates and operations

---

## 🚀 Quick Start

### Method 1: Command Line (Recommended)

```bash
# Navigate to CORTEX directory
cd "D:\PROJECTS\CORTEX"

# Run upgrade
python scripts/cortex-upgrade.py
```

### Method 2: From User Workspace

```bash
# Navigate to your project
cd "D:\PROJECTS\MY-PROJECT"

# Run upgrade on CORTEX subdirectory
python CORTEX/scripts/cortex-upgrade.py
```

### Method 3: GitHub Copilot Chat

```
/CORTEX upgrade
```

---

## 📋 Upgrade Options

### Standard Upgrade (Latest Version)

```bash
python scripts/cortex-upgrade.py
```

### Preview Upgrade (Dry Run)

```bash
python scripts/cortex-upgrade.py --dry-run
```

Shows exactly what will change without modifying files.

### Specific Version

```bash
python scripts/cortex-upgrade.py --version 5.4.0
```

### Skip Backup (Not Recommended)

```bash
python scripts/cortex-upgrade.py --skip-backup
```

Only use if you have an external backup system.

---

## 🔄 Upgrade Process

The upgrade system follows 8 steps:

### [1/8] Version Detection
- Detects current CORTEX version
- Checks for available upgrades
- Validates `.cortex-version` file

### [2/8] Creating Backup
- Full backup of brain data (tier1, tier2, tier3, documents)
- Backup location: `cortex-brain/backups/pre-upgrade-{timestamp}/`
- Includes configuration files

### [3/8] Fetching Release
- Downloads latest release from GitHub
- Extracts package to temporary directory
- Verifies download integrity

### [4/8] Updating Core Files
- **PRESERVES:** Database files (*.db), conversation logs, user documents
- **UPDATES:** Scripts, prompts, templates, schemas
- **MERGES:** Configuration files (capabilities, response-templates)

### [5/8] Merging Configurations
- 3-way merge of YAML configurations
- Preserves custom templates and operations
- Adds new features from upgrade

### [6/8] Applying Schema Migrations
- Updates database schemas if needed
- Applies migrations in sequence
- Tracks version with PRAGMA user_version

### [7/8] Validating Brain Integrity
- Verifies all brain databases exist
- Checks document directories
- Validates configuration files

### [8/8] Updating Version File
- Updates `.cortex-version` with new version
- Records upgrade in history
- Preserves workspace ID

---

## 🛡️ What Gets Preserved

### Brain Data (NEVER Overwritten)
- `cortex-brain/tier1/*.db` - Working memory
- `cortex-brain/tier2/*.db` - Knowledge graph
- `cortex-brain/tier3/*.db` - Development context
- `cortex-brain/documents/**/*` - User planning documents
- `cortex-brain/user-dictionary.yaml` - Custom terminology
- `cortex.config.json` - Machine-specific config
- `.cortex-version` - Version tracking

### Intelligently Merged
- `cortex-brain/response-templates.yaml` - Adds new templates, preserves custom
- `cortex-brain/capabilities.yaml` - Adds new operations, preserves custom
- `cortex-brain/operations-config.yaml` - Merges configurations

### Upgraded (Safe to Overwrite)
- `.github/prompts/**/*` - Entry points and modules
- `scripts/**/*` - Automation scripts
- `src/**/*` - Source code
- `cortex-brain/brain-protection-rules.yaml` - Governance rules
- `cortex-brain/schema.sql` - Database schema

---

## ♻️ Rollback

If upgrade fails, automatic rollback occurs:

```
♻️  Rolling back upgrade...
   ✅ Restored tier1
   ✅ Restored tier2
   ✅ Restored tier3
   ✅ Restored documents
✅ Rollback successful
```

### Manual Rollback

If needed, manually restore from backup:

```bash
python scripts/operations/brain_preserver.py restore \
  "D:\PROJECTS\CORTEX" \
  "D:\PROJECTS\CORTEX\cortex-brain\backups\pre-upgrade-20251123-143022"
```

---

## 🧪 Testing Upgrade (Recommended)

Before upgrading production workspace:

### 1. Preview Changes (Dry Run)

```bash
python scripts/cortex-upgrade.py --dry-run
```

### 2. Test on Development Copy

```bash
# Copy CORTEX to test location
cp -r "D:\PROJECTS\CORTEX" "D:\TEMP\CORTEX-TEST"

# Test upgrade
cd "D:\TEMP\CORTEX-TEST"
python scripts/cortex-upgrade.py

# Verify functionality
# If successful, upgrade production copy
```

---

## 📊 Upgrade Example (NOOR CANVAS)

### Before Upgrade

```
D:\PROJECTS\NOOR CANVAS\CORTEX\
├── .cortex-version (v5.2.0)
├── cortex-brain/
│   ├── tier1/ (127 conversations)
│   ├── tier2/ (3,247 patterns)
│   └── documents/ (52 planning files)
```

### Run Upgrade

```bash
cd "D:\PROJECTS\NOOR CANVAS\CORTEX"
python scripts/cortex-upgrade.py
```

### After Upgrade

```
D:\PROJECTS\NOOR CANVAS\CORTEX\
├── .cortex-version (v5.3.0) ✅ Updated
├── cortex-brain/
│   ├── tier1/ (127 conversations) ✅ Preserved
│   ├── tier2/ (3,247 patterns) ✅ Preserved
│   ├── documents/ (52 files) ✅ Preserved
│   ├── backups/
│   │   └── pre-upgrade-20251123-143022/ (Full backup)
│   ├── response-templates.yaml ✅ Merged (added 5 new templates)
│   └── capabilities.yaml ✅ Merged (added 2 new operations)
├── .github/prompts/ ✅ Updated
└── scripts/ ✅ Updated
```

**Result:** 
- ✅ New CORTEX features available
- ✅ All brain data preserved
- ✅ Custom configurations maintained
- ✅ Rollback backup available

---

## ⚠️ Troubleshooting

### Error: "No existing CORTEX installation found"

**Solution:** Run from CORTEX directory or specify path:

```bash
python scripts/cortex-upgrade.py --cortex-path "D:\PROJECTS\MY-APP\CORTEX"
```

### Error: "GitHub API rate limit exceeded"

**Solution:** Set GitHub token for higher limits:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_github_token_here"
python scripts/cortex-upgrade.py

# Or permanently set in environment variables
```

### Error: "Download failed"

**Solution:** Check internet connection, retry, or download manually:

1. Go to https://github.com/asifhussain60/CORTEX/releases
2. Download latest release ZIP
3. Extract and manually copy files (see manual upgrade guide)

### Warnings: "Conflicts detected during config merge"

**Solution:** Review merge report:

```bash
# Check merge conflicts
cat cortex-brain/merge-report.json

# Edit merged files manually if needed
code cortex-brain/response-templates.yaml
```

---

## 📖 Manual Upgrade (Fallback)

If automated upgrade fails:

### 1. Backup Brain Data

```bash
cp -r cortex-brain cortex-brain-backup
```

### 2. Download New CORTEX

```bash
git clone https://github.com/asifhussain60/CORTEX.git cortex-new
cd cortex-new
git checkout CORTEX-3.0
```

### 3. Selective Copy

```bash
# Update core files only
cp -r cortex-new/.github .
cp -r cortex-new/scripts .
cp -r cortex-new/src .

# DO NOT copy: cortex-brain/tier1, tier2, tier3, documents
```

### 4. Merge Configurations

```bash
# Manually merge response-templates.yaml and capabilities.yaml
# Add new templates/operations while preserving your customizations
```

---

## 🎓 Best Practices

### Before Upgrading

- ✅ Read release notes: https://github.com/asifhussain60/CORTEX/releases
- ✅ Test with `--dry-run` first
- ✅ Close GitHub Copilot Chat sessions
- ✅ Ensure no CORTEX operations are running

### After Upgrading

- ✅ Verify brain integrity (automatic)
- ✅ Test basic commands (`/CORTEX help`)
- ✅ Check conversation history preserved
- ✅ Remove old backup after 7-30 days

### Backup Strategy

- **Automatic:** Upgrade system creates backup before each upgrade
- **Manual:** Create backup before major changes
- **External:** Consider backing up entire CORTEX directory to cloud/external drive
- **Retention:** Keep last 3-5 upgrade backups

---

## 📞 Support

### If Upgrade Fails

1. Check error message carefully
2. Try `--verbose` flag for details
3. Review this troubleshooting guide
4. Manually restore from backup if needed

### Getting Help

- **Documentation:** `cortex-brain/documents/`
- **GitHub:** https://github.com/asifhussain60/CORTEX
- **Issues:** https://github.com/asifhussain60/CORTEX/issues (read-only, no contributions)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX
