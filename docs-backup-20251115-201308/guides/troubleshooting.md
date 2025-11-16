---
title: Troubleshooting Guide
description: Common issues and solutions for CORTEX
author: 
generated: true
version: ""
last_updated: 
---

# Troubleshooting Guide

**Purpose:** Solutions for common CORTEX issues  
**Audience:** All users  
**Version:**   
**Last Updated:** 

---

## Installation Issues

### Python Not Found

**Symptom:** `python: command not found`

**Solution:**

```bash
# Windows
python --version
# If not found, install Python 3.9.6+

# macOS/Linux
python3 --version
# If not found: brew install python3 (Mac)
```

### Dependencies Installation Failed

**Symptom:** `pip install -r requirements.txt` fails

**Solution:**

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Try individual packages
pip install pytest pyyaml numpy
```

### Permission Denied

**Symptom:** `PermissionError: [Errno 13]`

**Solution:**

```bash
# Windows: Run PowerShell as Administrator

# macOS/Linux: Fix permissions
chmod -R 755 $CORTEX_ROOT/cortex-brain
```

---

## Memory Issues

### Conversations Not Saved

**Symptom:** `cortex query` returns no results

**Diagnosis:**

```bash
# Check Tier 1 database
ls cortex-brain/tier1/conversations.db

# Check tracking status
cortex daemon status
```

**Solutions:**

1. **Tracking not enabled:**
   ```bash
   cortex daemon start
   ```

2. **Database corrupted:**
   ```bash
   python scripts/brain_init.py --reinit
   ```

3. **Permissions issue:**
   ```bash
   chmod 644 cortex-brain/tier1/conversations.db
   ```

### FIFO Queue Full

**Symptom:** Old conversations not deleting

**Solution:**

```json
// Edit cortex.config.json
"tier1": {
  "maxConversations": 20,
  "fifoMode": true,
  "autoArchive": true
}
```

```bash
# Manually trigger cleanup
cortex cleanup --tier1
```

---

## Agent Issues

### Intent Not Detected

**Symptom:** "I don't understand what you want"

**Diagnosis:**

```bash
# Check intent router confidence
cortex test-intent "your request here"
```

**Solutions:**

1. **Be more explicit:**
   ```
   ❌ "do something"
   ✅ "plan a feature"
   ```

2. **Lower threshold (not recommended):**
   ```json
   "intentRouter": {
     "confidenceThreshold": 0.6  // Default 0.75
   }
   ```

### TDD Enforcement Blocking

**Symptom:** "Cannot proceed without tests"

**Solution:**

```json
// Temporarily disable (not recommended)
"codeExecutor": {
  "enforceTDD": false
}
```

**Better Solution:** Write tests first (follow TDD)

---

## Performance Issues

### Slow Database Queries

**Symptom:** Tier 1/2/3 queries > 1 second

**Diagnosis:**

```bash
# Check database size
ls -lh cortex-brain/tier1/conversations.db

# Run VACUUM
sqlite3 cortex-brain/tier1/conversations.db "VACUUM;"
```

**Solutions:**

1. **Archive old data:**
   ```bash
   cortex archive --older-than 90
   ```

2. **Rebuild indexes:**
   ```bash
   python scripts/rebuild_indexes.py
   ```

3. **Optimize configuration:**
   ```json
   "performance": {
     "cacheEnabled": true,
     "cacheSizeMB": 200
   }
   ```

### High Memory Usage

**Symptom:** CORTEX using > 500MB RAM

**Solutions:**

1. **Reduce cache:**
   ```json
   "performance": {
     "cacheSizeMB": 50
   }
   ```

2. **Limit worker threads:**
   ```json
   "performance": {
     "maxWorkerThreads": 2
   }
   ```

---

## Git Analysis Issues

### Commits Not Analyzed

**Symptom:** Tier 3 shows 0 commits

**Diagnosis:**

```bash
# Check git repository
git log --oneline | head -10

# Check Tier 3 database
sqlite3 cortex-brain/tier3/context-intelligence.db \
  "SELECT COUNT(*) FROM git_commits;"
```

**Solutions:**

1. **Reinitialize Tier 3:**
   ```bash
   python scripts/init_tier3.py --force
   ```

2. **Check configuration:**
   ```json
   "tier3": {
     "gitAnalysis": {
       "enabled": true,
       "maxCommits": 1000
     }
   }
   ```

---

## Testing Issues

### Tests Failing

**Symptom:** `pytest tests/ -v` shows failures

**Diagnosis:**

```bash
# Run specific test
pytest tests/test_specific.py -v

# Show full output
pytest tests/ -v -s
```

**Common Causes:**

1. **Missing fixtures:**
   ```bash
   pytest --fixtures
   ```

2. **Environment issues:**
   ```bash
   python -m pytest tests/ -v
   ```

3. **Database state:**
   ```bash
   # Reset test databases
   rm tests/fixtures/*.db
   ```

---

## Documentation Generation Issues

### Templates Not Found

**Symptom:** "Template not found: installation.md.j2"

**Diagnosis:**

```bash
# List templates
ls cortex-brain/templates/doc-templates/
```

**Solution:**

```bash
# Verify all 20 templates exist
python scripts/validate_templates.py
```

### Mermaid Diagrams Not Rendering

**Symptom:** Diagrams show as code blocks

**Solution:**

1. **Check MkDocs configuration:**
   ```yaml
   # mkdocs.yml
   markdown_extensions:
     - pymdownx.superfences:
         custom_fences:
           - name: mermaid
             class: mermaid
   ```

2. **Install mermaid plugin:**
   ```bash
   pip install mkdocs-mermaid2-plugin
   ```

---

## Common Error Messages

### "YAML syntax error"

**Cause:** Malformed YAML file

**Solution:**

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('file.yaml'))"

# Common issues:
# - Incorrect indentation
# - Missing quotes around special characters
# - Tab characters (use spaces)
```

### "Database is locked"

**Cause:** Multiple processes accessing database

**Solution:**

```bash
# Check running processes
ps aux | grep cortex

# Kill stale processes
pkill -f cortex_daemon
```

### "ModuleNotFoundError"

**Cause:** Missing Python package

**Solution:**

```bash
# Install missing package
pip install <package-name>

# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Getting Help

### Diagnostics

Run full diagnostics:

```bash
cortex diagnose
```

### Logs

Check logs:

```bash
# All logs
tail -f logs/cortex.log

# Specific component
tail -f logs/tier1.log
```

### Support

1. **Check documentation:** `docs/`
2. **Search GitHub issues:** [CORTEX Issues](https://github.com/asifhussain60/CORTEX/issues)
3. **Create new issue:** Include diagnostics output

---

## Related Documentation

- **Installation:** [Installation Guide](../getting-started/installation.md)
- **Configuration:** [Config Reference](../reference/config-reference.md)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 