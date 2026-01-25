# CORTEX Prompts

This directory contains all CORTEX system prompts organized by category.

## 📁 Structure

### Root Directory - Production Prompts
Primary prompts used in active CORTEX operations:

- **cortex-review.prompt.md** - Code review & governance analysis (v5.2)
- **cortex-total-recall.prompt.md** - Feature discovery & verification (v7.1)
- **cortex-doc.prompt.md** - Documentation generation
- **cortex-enforcement.prompt.md** - Governance rule enforcement
- **cortex-builder.prompt.md** - Build orchestration
- **cortex-git-commit.prompt.md** - Git commit generation
- **CORTEX.prompt.md** - Master orchestrator prompt

### `/archived` - Old Versions
Previous versions kept for reference only:

- **cortex-review-enhanced-v51.prompt.md** - Old review version (superseded by v5.2)
- **cortex-vacuum.prompt.md** - Vacuum operations (obsolete post-cleanup)
- **CORTEX-VACUUM-REGISTRY.md** - Vacuum registry (archived)
- **cortex-vacuum-manifest.yaml** - Vacuum manifest (archived)
- **cortex-vacuum-operations.yaml** - Vacuum operations (archived)
- **cortex-vacuum-agents.md** - Vacuum agents (archived)

### `/guides` - Documentation & Guides
Reference materials and operational guides:

- **AC-PERMANENT-FIX-*.md** - Permanent fix documentation (3 files)
- **DOCUMENTATION-ORCHESTRATION-IMPLEMENTATION-GUIDE.md** - Doc generation guide
- **ORCHESTRATOR-OPERATIONAL-STATUS-*.md** - Status reports
- **START-HERE.md** - Quick start guide
- Various README and delivery reports

## 🎯 Usage

### For Active Development
Use prompts from root directory (all .prompt.md files).

### For Reference
Check `/guides/` for operational documentation and `/archived/` for previous versions.

## 📋 Deduplication Status

✅ **cortex-review** deduplication: 
- Archived: `archived/cortex-review-enhanced-v51.prompt.md` (v5.1 - old)
- Active: `cortex-review.prompt.md` (v5.2 - canonical/most current)

✅ **cortex-total-recall**: Single canonical (v7.1)

✅ **cortex-vacuum**: Archived and removed (obsolete post-cleanup)

## 🔄 Adding New Prompts

1. Create in root directory as `.prompt.md`
2. Add to this README
3. Old versions → `/archived/` with version suffix
4. Mark old versions as reference-only

---
**Last Updated:** 2026-01-25
