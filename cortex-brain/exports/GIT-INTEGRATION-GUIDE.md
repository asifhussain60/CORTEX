# CORTEX Brain Transfer - Git Integration Guide

**Version:** 2.0 (Git-Integrated)  
**Status:** ✅ Production Ready  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🌐 Git Integration (Default Behavior)

Brain export/import uses **Git integration by default** for seamless team collaboration.

---

## 🚀 Quick Start

### Export Brain (Git-Integrated - Default)

```bash
# Export and push to remote (automatic)
python3 scripts/brain_transfer_cli.py export brain
```

**What happens:**
1. ✅ Exports patterns to YAML
2. ✅ Stages file: `git add cortex-brain/exports/brain-export-*.yaml`
3. ✅ Commits: `git commit -m "brain: Share 54 workspace patterns (authentication)"`
4. ✅ Pushes: `git push origin [current-branch]`

**Output:**
```
🧠 CORTEX Brain Export
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scope: workspace
Min Confidence: 0.5
Git Integration: Yes (default)

✅ Brain exported successfully!

📁 Location: cortex-brain/exports/brain-export-20251117_143022.yaml
💾 Size: 42.3 KB

🔄 Git Integration:
   ✅ Staged: brain-export-20251117_143022.yaml
   ✅ Committed: brain: Share 54 workspace patterns (authentication, validation)
   ✅ Pushed to: origin/CORTEX-3.0

🌐 Brain shared successfully!
   Teammates can now run: cortex import brain
```

### Import Brain (Git-Integrated - Default)

```bash
# Pull and auto-import all new exports (automatic)
python3 scripts/brain_transfer_cli.py import brain
```

**What happens:**
1. ✅ Pulls from remote: `git pull origin [current-branch]`
2. ✅ Scans for new exports in `cortex-brain/exports/`
3. ✅ Auto-imports all unprocessed files
4. ✅ Tracks imported files (prevents re-import)

**Output:**
```
🧠 CORTEX Brain Import
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Pulling from remote...
   ✅ Pulled from: origin/CORTEX-3.0

📥 Found 2 unprocessed export(s)

   Importing: brain-export-20251117_143022.yaml
      ✅ 42 new, 8 merged
   Importing: brain-export-20251117_150315.yaml
      ✅ 15 new, 3 merged

✅ Import completed!
   Total patterns imported: 57
   Total patterns merged: 11
```

---

## 🤝 Team Collaboration Workflow

### Daily Workflow

**Developer A (Morning):**
```bash
# Get latest team knowledge
python3 scripts/brain_transfer_cli.py import brain

# Work on authentication feature
# ... (CORTEX learns patterns)

# Share what you learned
python3 scripts/brain_transfer_cli.py export brain
```

**Developer B (Afternoon):**
```bash
# Get A's knowledge
python3 scripts/brain_transfer_cli.py import brain
# Output: ✅ Imported 1 brain export, merged 54 patterns

# Work using A's knowledge
# CORTEX now knows authentication patterns!
```

### Multi-Developer Sync

**Team of 5 developers working on same project:**

```bash
# Everyone starts their day with:
python3 scripts/brain_transfer_cli.py import brain

# Everyone ends their day with:
python3 scripts/brain_transfer_cli.py export brain
```

**Result:** Team knowledge accumulates and improves over time!

---

## 🧠 Smart Commit Messages

CORTEX generates intelligent commit messages automatically by analyzing exported patterns.

### Examples

```
brain: Share 54 workspace patterns (authentication, validation)
brain: Share 12 cortex patterns (intent-routing, error-handling)
brain: Share 8 workspace patterns (general)
brain: Share 23 workspace patterns (api-integration, database-access)
```

### Format

```
brain: Share [count] [scope] patterns ([namespaces])
```

- **count:** Number of patterns exported
- **scope:** `workspace`, `cortex`, or `all`
- **namespaces:** Top 3 namespace categories (e.g., authentication, validation)

### How It Works

```python
# CORTEX analyzes your export:
- Scope: workspace
- Pattern count: 54
- Namespaces detected:
  - workspace.authentication (18 patterns)
  - workspace.validation (12 patterns)
  - workspace.error-handling (8 patterns)
  
# Generated message:
"brain: Share 54 workspace patterns (authentication, validation, error-handling)"
```

---

## 🛠️ Local-Only Operations

If you need to export/import **without Git operations**:

### Export (Local-Only)

```bash
python3 scripts/brain_transfer_cli.py export brain --local-only
```

**Output:**
```
🧠 CORTEX Brain Export
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scope: workspace
Min Confidence: 0.5
Git Integration: No (--local-only)

✅ Brain exported successfully!

📁 Location: cortex-brain/exports/brain-export-20251117_143022.yaml
💾 Size: 42.3 KB

📋 To share manually:
   git add cortex-brain/exports/brain-export-20251117_143022.yaml
   git commit -m 'brain: Share patterns'
   git push
```

### Import (Local-Only)

```bash
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml --local-only
```

**Use cases for --local-only:**
- Testing brain transfer without affecting git history
- Working offline without remote access
- Manual control over commit messages
- Exporting to external storage (USB drive, cloud)

---

## 🚨 Troubleshooting

### Problem: Not in Git Repository

**Symptom:**
```
⚠️  Not in git repository
   Brain exported locally: cortex-brain/exports/brain-export.yaml
   Tip: Initialize git repo or use with --local-only
```

**Solutions:**

**Option 1: Initialize Git Repository**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

**Option 2: Use --local-only**
```bash
python3 scripts/brain_transfer_cli.py export brain --local-only
```

---

### Problem: Merge Conflicts During Pull

**Symptom:**
```
⚠️  Git pull failed: CONFLICT (content): Merge conflict in cortex-brain/exports/brain-export.yaml
   Continuing with local import...
```

**Solution:**

```bash
# 1. Check conflicted files
git status

# 2. Resolve conflicts manually or use mergetool
git mergetool

# Or manually edit files and:
nano cortex-brain/exports/brain-export.yaml  # Fix conflicts
git add cortex-brain/exports/brain-export.yaml
git commit

# 3. Re-run import
python3 scripts/brain_transfer_cli.py import brain
```

**Prevention:**
- Export frequently (daily)
- Pull before starting work
- Use feature branches for experimental work

---

### Problem: Push Fails (Auth Issues)

**Symptom:**
```
⚠️  Git operation failed: failed to push some refs to 'origin'
   Brain exported locally: cortex-brain/exports/brain-export.yaml
   You can push manually: git push
```

**Solutions:**

**Option 1: Configure Git Credentials**
```bash
# For HTTPS:
git config --global credential.helper store
git push origin CORTEX-3.0  # Enter credentials once

# For SSH:
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub/GitLab SSH keys
```

**Option 2: Push Manually**
```bash
git push origin CORTEX-3.0
```

---

### Problem: No Unprocessed Exports

**Output:**
```
✅ All caught up!
   No new brain exports found.
```

**This is normal!** Means you're synchronized with team.

**What to check:**
- Teammates haven't exported yet today
- You've already imported all recent exports
- No new knowledge to learn right now

---

### Problem: Git Not Installed

**Symptom:**
```
⚠️  Git command not found
   Brain exported locally: cortex-brain/exports/brain-export.yaml
```

**Solution:**

```bash
# macOS:
brew install git

# Linux:
sudo apt-get install git  # Debian/Ubuntu
sudo yum install git      # RHEL/CentOS

# Windows:
# Download from: https://git-scm.com/download/win
```

---

## 📋 Command Reference

### Export Command

```bash
python3 scripts/brain_transfer_cli.py export brain [OPTIONS]
```

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--scope` | `workspace`, `cortex`, `all` | `workspace` | Pattern scope |
| `--min-confidence` | 0.0-1.0 | 0.5 | Min confidence threshold |
| `--output` | path | auto-generated | Custom output path |
| `--local-only` | flag | disabled | Skip git operations |

**Examples:**
```bash
# Default (git-integrated)
python3 scripts/brain_transfer_cli.py export brain

# High-confidence only
python3 scripts/brain_transfer_cli.py export brain --min-confidence=0.8

# Everything, git-integrated
python3 scripts/brain_transfer_cli.py export brain --scope=all

# Local-only (no git)
python3 scripts/brain_transfer_cli.py export brain --local-only
```

### Import Command

```bash
python3 scripts/brain_transfer_cli.py import brain [file] [OPTIONS]
```

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `file` | path | auto-detect | YAML file (optional) |
| `--strategy` | `auto`, `replace`, `skip` | `auto` | Merge strategy |
| `--dry-run` | flag | disabled | Preview only |
| `--local-only` | flag | disabled | Skip git operations |

**Examples:**
```bash
# Default (auto-detect, git-integrated)
python3 scripts/brain_transfer_cli.py import brain

# Specific file
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml

# Preview (dry-run)
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml --dry-run

# Local-only (no git)
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml --local-only
```

---

## 🔒 Security Considerations

### Safe Defaults

- **Automatic pulls are safe:** Only pulls export files, not code
- **Commit messages are informative:** No sensitive data exposed
- **Namespace isolation:** Workspace patterns don't mix with CORTEX core

### Best Practices

1. **Use SSH keys** for authentication (not HTTPS passwords)
2. **Review exports** before pushing (check YAML content)
3. **Use feature branches** for experimental work
4. **Backup frequently** before major imports

### What Gets Committed

**Committed:**
- ✅ `cortex-brain/exports/*.yaml` (brain exports)
- ✅ Commit messages with pattern counts

**Not Committed:**
- ❌ Conversation history (Tier 1)
- ❌ Development context (Tier 3)
- ❌ Database files (`.db`)
- ❌ Import history (`.import-history`)

---

## 📚 Related Documentation

- **Main User Guide:** `cortex-brain/exports/README.md`
- **Intelligent Conflict Resolution:** `cortex-brain/exports/README.md#intelligent-conflict-resolution`
- **File Format Specification:** `cortex-brain/exports/README.md#file-format`
- **Team Collaboration Guide:** Coming soon!

---

## ✅ Success Checklist

After reading this guide, you should be able to:

- [ ] Export brain with automatic git push
- [ ] Import brain with automatic git pull and auto-detect
- [ ] Understand smart commit message generation
- [ ] Use --local-only flag when needed
- [ ] Troubleshoot common git integration issues
- [ ] Collaborate with teammates using brain transfer

---

**Version:** 2.0 (Git-Integrated)  
**Last Updated:** November 17, 2025  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
