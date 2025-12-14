# CORTEX Brain Transfer System - User Guide

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🎯 What Is Brain Transfer?

Brain Transfer allows you to **export your CORTEX knowledge patterns** (Tier 2) as a YAML file and **import them on another machine** with intelligent conflict resolution. This enables:

- 🔄 **Knowledge sharing** across multiple development machines
- 💾 **Brain backup** before major updates
- 🤝 **Team collaboration** (share learned patterns with colleagues)
- 🚀 **New machine setup** (bootstrap CORTEX with existing knowledge)

**What Gets Transferred:**
- ✅ Intent patterns (user phrases → detected intent)
- ✅ Validation insights (bugs caught, lessons learned)
- ✅ Workflow templates (proven multi-step processes)
- ✅ File relationships (files that change together)
- ✅ Metadata (confidence scores, access counts, namespaces)

**What Stays Local:**
- ❌ Conversation history (Tier 1 - machine-specific)
- ❌ Development context (Tier 3 - git analysis, file metrics)
- ❌ Decayed patterns (confidence < 0.3)

---

## 🚀 Quick Start

### Export Brain (Git-Integrated - Default)

```bash
# Export workspace patterns and push to remote (default)
python3 scripts/brain_transfer_cli.py export brain

# Export high-confidence patterns only
python3 scripts/brain_transfer_cli.py export brain --min-confidence=0.7

# Export everything (workspace + cortex patterns)
python3 scripts/brain_transfer_cli.py export brain --scope=all

# Local-only export (no git operations)
python3 scripts/brain_transfer_cli.py export brain --local-only
```

**Output (Git-Integrated):**
```
🧠 CORTEX Brain Export
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scope: workspace
Min Confidence: 0.5
Git Integration: Yes (default)

📖 Loading patterns from database...
✅ Brain exported successfully!

📁 Location: cortex-brain/exports/brain-export-20251117_143022.yaml
💾 Size: 42.3 KB

� Git Integration:
   ✅ Staged: brain-export-20251117_143022.yaml
   ✅ Committed: brain: Share 54 workspace patterns (authentication, validation)
   ✅ Pushed to: origin/CORTEX-3.0

🌐 Brain shared successfully!
   Teammates can now run: cortex import brain
```

### Import Brain (Git-Integrated - Default)

```bash
# Pull from remote and auto-import all new exports (default)
python3 scripts/brain_transfer_cli.py import brain

# Import specific file
python3 scripts/brain_transfer_cli.py import brain brain-export-20251117_143022.yaml

# Preview what would be imported (dry-run)
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml --dry-run

# Local-only import (no git operations)
python3 scripts/brain_transfer_cli.py import brain brain-export.yaml --local-only
```

**Output (Auto-Detect Mode):**
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

🧠 Intelligent Merges Applied:
   filesystem_validation_required:
     0.92 → 0.94
     Reason: Similar patterns (85%), applying weighted merge
```

---

## 📖 Detailed Usage

### Export Command

```bash
python scripts/brain_transfer_cli.py export brain [OPTIONS]
```

**Options:**

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--scope` | `workspace`, `cortex`, `all` | `workspace` | Pattern scope to export |
| `--min-confidence` | `0.0` - `1.0` | `0.5` | Minimum confidence threshold |
| `--output` | file path | auto-generated | Custom output path |

**Examples:**

```bash
# Export all workspace patterns (default)
python scripts/brain_transfer_cli.py export brain

# Export only high-confidence patterns (>0.8)
python scripts/brain_transfer_cli.py export brain --min-confidence=0.8

# Export CORTEX core patterns
python scripts/brain_transfer_cli.py export brain --scope=cortex

# Export everything to custom location
python scripts/brain_transfer_cli.py export brain --scope=all --output=~/backups/my-brain.yaml
```

**Scope Explained:**
- `workspace`: Your project-specific patterns (default)
- `cortex`: CORTEX framework patterns (shared across all projects)
- `all`: Both workspace and cortex patterns

### Import Command

```bash
python scripts/brain_transfer_cli.py import brain <file> [OPTIONS]
```

**Options:**

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--strategy` | `auto`, `replace`, `skip` | `auto` | Conflict resolution strategy |
| `--dry-run` | flag | disabled | Preview without applying changes |

**Strategies Explained:**

**`auto` (Recommended - Intelligent Sniffing):**
- Identical patterns (>98% match) → keep higher confidence
- Similar patterns (>80% match) → weighted merge
- Contradictory patterns → keep local (preserve your knowledge)
- New patterns → import directly

**`replace`:**
- Always overwrite existing patterns with imported ones
- Use when: Imported patterns are definitely more accurate

**`skip`:**
- Keep existing patterns unchanged
- Use when: You trust your local knowledge more

**Examples:**

```bash
# Preview what would happen (no changes applied)
python scripts/brain_transfer_cli.py import brain brain-export.yaml --dry-run

# Import with intelligent auto-merge (recommended)
python scripts/brain_transfer_cli.py import brain brain-export.yaml

# Import and overwrite all conflicts
python scripts/brain_transfer_cli.py import brain brain-export.yaml --strategy=replace

# Import only new patterns (skip conflicts)
python scripts/brain_transfer_cli.py import brain brain-export.yaml --strategy=skip
```

---

## 🧠 Intelligent Conflict Resolution

CORTEX automatically **sniffs pattern structure** and applies smart merge strategies:

### Example 1: Identical Patterns

**Scenario:** You exported from Machine A (confidence 0.92), importing to Machine B (confidence 0.88)

**Auto Strategy:**
```
Pattern: filesystem_validation_required
  Machine A: confidence 0.92, usage 15
  Machine B: confidence 0.88, usage 8
  
Decision: Keep higher confidence (0.92 from Machine A)
Reason: Near-identical (99% match), imported has higher confidence
```

### Example 2: Similar Patterns (Weighted Merge)

**Scenario:** Same pattern learned independently on both machines

**Auto Strategy:**
```
Pattern: api_null_check_required
  Machine A: confidence 0.85, usage 12
  Machine B: confidence 0.78, usage 5
  
Decision: Weighted merge
  Formula: (0.85 * 12 + 0.78 * 5) / (12 + 5) = 0.83
  New confidence: 0.83
  Reason: Similar patterns (88% match), applying weighted merge
```

### Example 3: Contradictory Patterns

**Scenario:** Patterns conflict significantly

**Auto Strategy:**
```
Pattern: test_strategy_preference
  Machine A: "Write integration tests first"
  Machine B: "Write unit tests first"
  
Decision: Keep local (Machine B)
Reason: Contradictory patterns (42% match), preserving local knowledge
```

---

## 📁 File Structure

```
cortex-brain/
├── tier2/
│   └── knowledge-graph.db          # Your brain database
├── exports/
│   ├── brain-export-20251117_143022.yaml
│   ├── brain-export-20251116_091245.yaml
│   └── README.md
├── imports/
│   ├── applied/
│   │   ├── brain-export-20251117_143022.yaml
│   │   └── brain-export-20251117_143022.log
│   └── rejected/
│       ├── corrupted-export.yaml
│       └── corrupted-export.log
```

**Directory Details:**

- **exports/**: YAML files you've exported (ready to transfer)
- **imports/applied/**: Successfully imported files with audit logs
- **imports/rejected/**: Failed imports with error logs

---

## 🔐 Safety Features

### 1. Signature Verification

Every export includes a SHA256 signature:

```yaml
signature: "a3f8c9d2e1b4a5f6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
```

**What it does:** Prevents importing corrupted or tampered files

**Error example:**
```
❌ Import failed!
Errors:
  - Signature verification failed - file may be corrupted
```

### 2. Namespace Validation

Prevents mixing `cortex.*` and `workspace.*` patterns incorrectly.

**Error example:**
```
❌ Import failed!
Errors:
  - Namespace violation: cortex.core pattern in workspace export
```

### 3. Audit Trail

Every import creates a log file:

```
Import completed: 2025-11-17T14:30:22Z
Statistics: {'total_patterns': 54, 'new_patterns': 42, ...}

Merge Decisions:
  filesystem_validation_required: weighted_merge - Similar patterns (85%)
  api_null_check_required: keep_local - Contradictory patterns (42%)
  test_first_workflow: new - No conflict
```

---

## 🎓 Common Workflows

### Workflow 1: New Machine Setup

**Scenario:** You got a new laptop, want to transfer your knowledge

```bash
# On old machine (Machine A)
python scripts/brain_transfer_cli.py export brain --scope=all --output=~/brain-backup.yaml

# Copy brain-backup.yaml to new machine

# On new machine (Machine B)
python scripts/brain_transfer_cli.py import brain ~/brain-backup.yaml
```

### Workflow 2: Periodic Backup

**Scenario:** Backup your brain weekly

```bash
# Create weekly backup
python scripts/brain_transfer_cli.py export brain --scope=workspace \
  --output=~/Dropbox/cortex-backups/brain-$(date +%Y%m%d).yaml

# Restore if needed
python scripts/brain_transfer_cli.py import brain ~/Dropbox/cortex-backups/brain-20251117.yaml
```

### Workflow 3: Team Collaboration

**Scenario:** Share learned patterns with your team

```bash
# Team member A exports high-confidence patterns
python scripts/brain_transfer_cli.py export brain --min-confidence=0.8 \
  --output=shared/team-patterns.yaml

# Commit to git
git add shared/team-patterns.yaml
git commit -m "feat(brain): Share high-confidence validation patterns"
git push

# Team member B imports
git pull
python scripts/brain_transfer_cli.py import brain shared/team-patterns.yaml --dry-run
# Review conflicts, then apply
python scripts/brain_transfer_cli.py import brain shared/team-patterns.yaml
```

---

## 🔧 Troubleshooting

### Problem: "Cannot auto-detect cortex-brain path"

**Solution:**
```bash
# Ensure you're running from CORTEX root directory
cd /path/to/CORTEX
python scripts/brain_transfer_cli.py export brain
```

### Problem: "File not found: cortex-brain/tier2/knowledge-graph.db"

**Solution:**
```bash
# Initialize brain database first
python scripts/initialize_brain.py
```

### Problem: "Signature verification failed"

**Cause:** YAML file was manually edited or corrupted

**Solution:**
```bash
# Re-export from source machine
python scripts/brain_transfer_cli.py export brain --output=brain-fixed.yaml
```

### Problem: All patterns marked as "keep_local" (nothing imported)

**Cause:** Your local patterns have higher confidence

**Solution:**
```bash
# Force replace with imported patterns
python scripts/brain_transfer_cli.py import brain brain-export.yaml --strategy=replace
```

---

## 📊 YAML Export Format

**Example export file:**

```yaml
# CORTEX Brain Export
# Generated: 2025-11-17T14:30:22Z
# Source: a3f8c9d2e1b4
# CORTEX Version: 3.0.0
# Total Patterns: 54

version: '1.0'
export_date: '2025-11-17T14:30:22Z'
source_machine_id: a3f8c9d2e1b4
cortex_version: 3.0.0
total_patterns: 54
scope: workspace

statistics:
  patterns_exported: 54
  confidence_range: [0.5, 0.95]
  namespaces: 
    - workspace.ksessions
    - workspace.authentication
  pattern_types:
    - validation_insight
    - workflow
    - intent
    - file_relationship
  oldest_pattern: '2025-10-15T09:00:00Z'
  newest_pattern: '2025-11-17T12:00:00Z'

patterns:
  filesystem_validation_required:
    pattern_type: validation_insight
    confidence: 0.95
    access_count: 12
    last_accessed: '2025-11-17T09:00:00Z'
    created_at: '2025-11-01T14:30:00Z'
    namespaces:
      - workspace.ksessions
      - cortex.core
    source: a3f8c9d2e1b4
    context:
      issue: "File generation operations report success without verifying..."
      root_cause: "Missing post-write validation..."
      solution: "Multi-layer validation after every file write..."

signature: a3f8c9d2e1b4a5f6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
```

---

## 🎯 Best Practices

1. **Export regularly** (weekly backups to cloud storage)
2. **Use `--dry-run`** before importing to preview conflicts
3. **Start with `auto` strategy** (intelligent sniffing)
4. **Review audit logs** after import (`imports/applied/*.log`)
5. **Keep exports in version control** for team collaboration
6. **Test import on fresh database** before overwriting production brain

---

## 📚 Related Documentation

- **Architecture Design:** `cortex-brain/documents/planning/BRAIN-IMPLANT-ARCHITECTURE.md`
- **Tier 2 API Reference:** `prompts/shared/technical-reference.md`
- **Knowledge Graph:** `src/tier2/knowledge_graph.py`

---

**Version:** 1.0  
**Last Updated:** November 17, 2025  
**Status:** ✅ Production Ready
