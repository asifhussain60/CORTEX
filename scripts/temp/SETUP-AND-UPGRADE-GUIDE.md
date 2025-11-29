# CORTEX Setup & Upgrade Guide

**Version:** 3.2.0+  
**Distribution Method:** Git-based (origin/main)  
**Last Updated:** 2024-11-25

---

## 📦 Installation Methods

### Method 1: Fresh Installation (Recommended for New Users)

```bash
# Clone CORTEX repository
git clone https://github.com/asifhussain60/CORTEX.git

# Navigate to CORTEX
cd CORTEX

# Verify installation
cat VERSION
```

**What you get:**
- Latest stable release from `main` branch
- Complete CORTEX package with brain, templates, and orchestrators
- Ready to use immediately with GitHub Copilot

---

### Method 2: Add to Existing Project

```bash
# In your project directory
mkdir .cortex
cd .cortex

# Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git

# Copy copilot instructions to project root
cp .cortex/CORTEX/.github/copilot-instructions.md ../.github/

# Update path in copilot-instructions.md to point to .cortex/CORTEX/
```

---

## 🔄 Upgrading CORTEX

### Automatic Upgrade (Easiest)

Just ask CORTEX to upgrade itself:

```
upgrade cortex
```

or

```
check for cortex updates
```

CORTEX will:
1. Check origin/main for newer version
2. Create backup of your brain data
3. Pull updates from origin/main
4. Run database migrations
5. Confirm successful upgrade

---

### Manual Upgrade (CLI)

```bash
cd CORTEX

# Check if updates available
python src/orchestrators/upgrade_orchestrator.py --check

# Upgrade (with automatic backup)
python src/orchestrators/upgrade_orchestrator.py --upgrade

# Upgrade without backup (not recommended)
python src/orchestrators/upgrade_orchestrator.py --upgrade --no-backup
```

---

### Traditional Git Pull

```bash
cd CORTEX

# Fetch latest changes
git fetch origin main

# Pull updates
git pull origin main

# Verify new version
cat VERSION
```

**Note:** This method does NOT create automatic backups or run migrations.

---

## 💾 Backup & Rollback

### List Backups

```bash
python src/orchestrators/upgrade_orchestrator.py --list-backups
```

### Rollback to Previous Version

```bash
python src/orchestrators/upgrade_orchestrator.py --rollback <BACKUP_ID>

# Example:
python src/orchestrators/upgrade_orchestrator.py --rollback 20241125_143022
```

### Manual Backup

Important files to backup before upgrade:
- `cortex-brain/feedback/` - Your feedback data
- `cortex-brain/working_memory.db` - Conversation history
- `cortex-brain/config/` - Custom configurations
- `cortex-brain/documents/planning/` - Your feature plans
- `logs/` - Historical logs

```bash
# Create manual backup
tar -czf cortex-backup-$(date +%Y%m%d).tar.gz \
  cortex-brain/feedback \
  cortex-brain/working_memory.db \
  cortex-brain/config \
  cortex-brain/documents/planning \
  logs
```

---

## 🔧 Configuration

### GitHub Token (for Feedback & Upgrades)

Set environment variable for automatic feedback uploads:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN="your_personal_access_token"

# Linux/Mac
export GITHUB_TOKEN="your_personal_access_token"
```

To create a token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `gist` (for feedback upload), `repo` (for private repos)
4. Copy token and set as environment variable

---

## 📊 Verifying Installation

### Check Version

```bash
cat CORTEX/VERSION
```

### Test CORTEX

In GitHub Copilot Chat:
```
help
```

Expected response: CORTEX help table with available commands

### Check Database

```bash
sqlite3 cortex-brain/working_memory.db "SELECT COUNT(*) FROM conversations;"
```

---

## 🚨 Troubleshooting

### "Failed to check for updates"

**Cause:** No internet connection or GitHub authentication issue

**Solution:**
```bash
# Test GitHub connection
git ls-remote https://github.com/asifhussain60/CORTEX.git

# Check if you have permission
git fetch origin main
```

### "Upgrade failed: merge conflict"

**Cause:** Local modifications conflict with updates

**Solution:**
```bash
# Stash local changes
git stash

# Retry upgrade
python src/orchestrators/upgrade_orchestrator.py --upgrade

# Reapply your changes
git stash pop
```

### "Rollback failed"

**Cause:** Backup corrupted or missing

**Solution:**
```bash
# List available backups
python src/orchestrators/upgrade_orchestrator.py --list-backups

# Try different backup ID
# Or restore from manual backup
tar -xzf cortex-backup-YYYYMMDD.tar.gz
```

### "Migrations failed"

**Cause:** Database locked or corrupted

**Solution:**
```bash
# Close all CORTEX processes
# Check database integrity
sqlite3 cortex-brain/working_memory.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
```

---

## 🔐 Data Privacy

### What Gets Upgraded

✅ **Updated:**
- CORTEX source code (`src/`)
- Response templates (`cortex-brain/response-templates.yaml`)
- System documentation (`.github/prompts/`)
- Migration scripts (`cortex-brain/migrations/`)

🔒 **Preserved:**
- Your conversation history (`cortex-brain/working_memory.db`)
- Your feedback data (`cortex-brain/feedback/`)
- Your feature plans (`cortex-brain/documents/planning/`)
- Your custom configurations (`cortex-brain/config/*.local.*`)
- Your logs (`logs/`)

### What Gets Backed Up

Automatic backups include:
- `cortex-brain/feedback/`
- `cortex-brain/working_memory.db`
- `cortex-brain/config/`
- `cortex-brain/documents/planning/`
- `logs/`
- `VERSION`

---

## 📱 Distribution to Team

### Option 1: Git Repository (Recommended)

Team members clone from your fork:
```bash
# Fork CORTEX on GitHub
# Team members clone your fork
git clone https://github.com/YOUR_USERNAME/CORTEX.git
```

### Option 2: Shared Network Drive

```bash
# Copy CORTEX to shared location
cp -r CORTEX /shared/network/drive/CORTEX

# Team members create symlink
ln -s /shared/network/drive/CORTEX ~/CORTEX
```

### Option 3: Package Distribution

```bash
# Create distribution package
cd CORTEX
tar -czf cortex-v$(cat VERSION).tar.gz \
  --exclude='.git' \
  --exclude='logs' \
  --exclude='cortex-brain/working_memory.db' \
  .

# Distribute cortex-v3.2.0.tar.gz
```

---

## 🎯 Best Practices

### For Individual Users

- ✅ Always keep GITHUB_TOKEN as environment variable (not in files)
- ✅ Upgrade regularly (weekly) to get bug fixes
- ✅ Let automatic backup run before upgrades
- ✅ Report feedback using `provide feedback` command
- ❌ Don't modify CORTEX source files directly

### For Teams

- ✅ Use a shared Git fork for consistency
- ✅ Test upgrades in staging environment first
- ✅ Announce upgrades to team in advance
- ✅ Maintain team-specific configurations separately
- ❌ Don't mix different CORTEX versions in same team

### For Contributors

**Note:** CORTEX is Source-Available (use allowed, no contributions accepted per license)

- ✅ Fork for personal experimentation
- ✅ Share improvements via feedback system
- ✅ Document your customizations
- ❌ Don't submit pull requests (license restriction)

---

## 📚 Related Documentation

- **Main Prompt:** `.github/prompts/CORTEX.prompt.md`
- **Response Format:** `.github/prompts/modules/response-format.md`
- **Planning System:** `.github/prompts/modules/planning-system.md`
- **Feedback System:** `cortex-brain/documents/reports/PHASE-2-3-COMPLETION-SUMMARY.md`
- **License:** `LICENSE`

---

## 🆘 Support

### Self-Service

1. Check VERSION file to confirm installation
2. Review logs in `logs/` directory
3. Test with `help` command in GitHub Copilot

### Report Issues

Use CORTEX's built-in feedback system:
```
provide feedback: [describe issue]
```

Feedback automatically uploaded to GitHub Gists for review.

### Manual Issue Reporting

If feedback system is unavailable:
- GitHub Issues: https://github.com/asifhussain60/CORTEX/issues
- Email: asif.hussain@example.com (check LICENSE for actual contact)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available - See LICENSE file  
**Repository:** https://github.com/asifhussain60/CORTEX
