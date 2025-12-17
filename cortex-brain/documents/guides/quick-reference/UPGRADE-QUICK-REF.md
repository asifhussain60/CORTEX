# CORTEX Upgrade Feature - Quick Reference

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Package:** cortex-v5.2.0.zip

---

## 🚀 What's New

The CORTEX v5.2.0 deployment package now includes a complete **automated upgrade system** with brain data protection.

---

## 📋 Available Commands

### Check for Updates
```bash
# Via Copilot Chat
upgrade cortex
check for updates
update cortex

# Via CLI
python scripts/cli_wrappers/upgrade_wrapper.py --check-only
```

### Full Upgrade
```bash
# Via Copilot Chat (Recommended)
upgrade cortex
upgrade to latest version

# Via CLI
python scripts/cli_wrappers/upgrade_wrapper.py
```

### Backup Only
```bash
python scripts/cli_wrappers/upgrade_wrapper.py --backup-only
```

### List Available Backups
```bash
python scripts/cli_wrappers/upgrade_wrapper.py --list-backups
```

### Force Upgrade
```bash
python scripts/cli_wrappers/upgrade_wrapper.py --force
```

---

## 🔄 7-Phase Upgrade Workflow

**Phase 1: Version Check**
- Fetch latest from `origin/main`
- Compare current vs. remote version
- Display update availability

**Phase 2: Brain Backup**
- Backup `cortex-brain/feedback`
- Backup `working_memory.db`
- Backup configuration files
- Create metadata with verification

**Phase 3: Git Pull**
- Pull latest changes from `origin/main`
- Merge strategy: fast-forward preferred
- Conflict detection and handling

**Phase 4: Dependency Updates**
- Run `pip install -r requirements.txt --upgrade`
- Validate core dependencies
- Check optional dependencies

**Phase 5: Schema Migrations**
- Auto-detect and run migration scripts
- Track applied migrations
- Verify database integrity

**Phase 6: Operational Validation**
- Test CORTEX functionality
- Verify tier operations
- Run test suite discovery
- Check bootstrap files

**Phase 7: What's New**
- Generate feature discovery summary
- Display version changelog
- Show new capabilities

---

## 🛡️ Safety Features

✅ **Brain Data Protection**
- Automatic backup before upgrade
- Backup verification with integrity checks
- Easy rollback with restore support

✅ **Rollback Support**
- Keep last 5 backups
- Metadata tracking (version, timestamp, size)
- One-command restore

✅ **Dependency Safety**
- Core dependency validation
- Optional dependency checks
- Requirements.txt synchronization

✅ **Operational Readiness**
- Post-upgrade health checks
- Test suite validation
- Bootstrap file verification

---

## 📦 What Gets Backed Up

**Always Backed Up:**
- `cortex-brain/feedback/` - User feedback data
- `cortex-brain/working_memory.db` - Conversation history
- `cortex-brain/config/` - User configuration
- `cortex-brain/documents/planning/active/` - Active plans

**Never Backed Up:**
- Test files
- Temporary files
- Cache directories
- Log files (except critical ones)

---

## 🔍 Backup Locations

**Backup Directory:**
```
cortex-brain/backups/upgrades/
└── backup-20251216-120000/
    ├── metadata.json
    ├── feedback/
    ├── working_memory.db
    ├── config/
    └── planning/
```

**Metadata Includes:**
- Backup ID and timestamp
- Source version
- Source branch
- Backed up items list
- Total size
- Verification status

---

## ⚠️ Important Notes

**Before Upgrading:**
1. Commit any uncommitted changes
2. Close all Copilot Chat sessions
3. Ensure stable internet connection
4. Have at least 500MB free disk space

**During Upgrade:**
- Do NOT interrupt the process
- Do NOT modify files manually
- Do NOT start new Copilot sessions

**After Upgrade:**
- Restart VS Code to reload extensions
- Run `/CORTEX help` to see new features
- Check `What's New` summary

---

## 🐛 Troubleshooting

**"No updates available" but I know there are:**
```bash
# Force fetch
cd CORTEX
git fetch origin main --force
python scripts/cli_wrappers/upgrade_wrapper.py --check-only
```

**Upgrade failed midway:**
```bash
# List backups
python scripts/cli_wrappers/upgrade_wrapper.py --list-backups

# Restore from backup (manual)
cd cortex-brain/backups/upgrades/
# Copy files from latest backup
```

**Dependencies won't install:**
```bash
# Manual dependency install
pip install -r requirements.txt --upgrade --force-reinstall
```

**Git conflicts during pull:**
```bash
# Abort and retry
git merge --abort
python scripts/cli_wrappers/upgrade_wrapper.py --force
```

---

## 📊 Version History

**v5.2.0** (December 16, 2025)
- ✅ Added automated upgrade system
- ✅ 7-phase upgrade workflow
- ✅ Brain data backup/restore
- ✅ Dependency auto-updates
- ✅ Schema migration support
- ✅ What's New feature discovery

---

## 🔗 Related Commands

- `system maintenance` - Run full 7-phase maintenance
- `healthcheck` - System health diagnostics
- `align` - System alignment
- `help` - Show all commands

---

**Quick Start:** Just say "upgrade cortex" in Copilot Chat!

**Safety First:** All upgrades include automatic brain backup with verified restore support.
