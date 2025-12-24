# Token Optimization CLI - Quick Reference

**NEW: Unified Command Structure**

---

## 🚀 Quick Start (Three Ways)

### Method 1: Unified CLI (RECOMMENDED)
```bash
# Check current token usage
python3 -m src.operations.optimize tokens status

# Auto-optimize (lets CORTEX decide)
python3 -m src.operations.optimize tokens auto

# Quick wins only (~1 hour)
python3 -m src.operations.optimize tokens quick

# Full optimization (~3-4 hours)
python3 -m src.operations.optimize tokens full

# Undo last optimization
python3 -m src.operations.optimize tokens rollback

# Optimize everything (tokens + files)
python3 -m src.operations.optimize all
```

### Method 2: Shell Script (SHORTEST)
```bash
# Add scripts/ to PATH or run directly
./scripts/optimize tokens status
./scripts/optimize tokens auto
./scripts/optimize all
```

### Method 3: Direct Module (ORIGINAL)
```bash
# Still works for backwards compatibility
python3 -m src.operations.optimize_tokens status
python3 -m src.operations.optimize_tokens auto
```

---

## 📋 Commands

### `status`
Shows current token usage vs budgets + optimization history

**Output:**
- Current token usage for all 4 governance files
- Budget compliance status
- Last 5 optimization runs
- Next steps recommendations

### `auto`
Intelligent optimization - auto-selects best strategy

**Decision Logic:**
- `>50% over budget` → Run FULL optimization (~3-4 hours, 75% reduction)
- `20-50% over budget` → Run QUICK optimization (~1 hour, 35% reduction)  
- `<20% over budget` → SKIP (monitoring recommended)

**Current state:** 306% over budget → Will run FULL

### `quick`
High-impact optimizations only

**Strategy:**
1. Extract 10 largest templates from brain-protection-rules.yaml
2. Implement YAML anchors in response-templates.yaml
3. Move 3 largest sections from CORTEX.prompt.md to guides

**Time:** ~1 hour  
**Reduction:** ~35% (~24K tokens)  
**Risk:** Low (partial optimization)

### `full`
Complete optimization to reach 17K token target

**Strategy:**
1. Extract ALL remaining templates from brain-protection-rules.yaml
2. Implement comprehensive YAML anchors
3. Template inheritance for response-templates.yaml
4. Module-based architecture for CORTEX.prompt.md

**Time:** ~3-4 hours  
**Reduction:** ~75% (~52K tokens)  
**Risk:** Medium (extensive changes)

### `rollback`
Undo the most recent optimization

**Behavior:**
- Restores files from automatic backup
- Removes optimization from history
- Validates restoration success

**Safety:** Always creates backup before optimization

### `validate`
Check token budgets without optimizing

**Output:** Same as `align governance-tokens validate`

---

## 🛡️ Safety Features

### Automatic Backups
Every optimization creates timestamped backup:
```
cortex-brain/backups/token-optimization/
  └── 20251201_143022_before_quick_optimization/
      ├── CORTEX.prompt.md
      ├── brain-protection-rules.yaml
      ├── response-templates.yaml
      └── copilot-instructions.md
```

### YAML Validation
After every optimization:
- Validates YAML syntax
- Rolls back if validation fails
- Ensures no corruption

### Operation History
All optimizations logged:
```json
// cortex-brain/token-optimization-history.json
{
  "timestamp": "2025-12-01T14:30:22",
  "strategy": "quick",
  "success": true,
  "before_tokens": 69039,
  "after_tokens": 45000,
  "tokens_saved": 24039,
  "reduction_percent": 34.8,
  "files_modified": ["brain-protection-rules.yaml"],
  "backup_path": "cortex-brain/backups/..."
}
```

---

## 📊 Token Budgets

| File | Budget | Current | Over By |
|------|--------|---------|---------|
| **CORTEX.prompt.md** | 5,000 | 11,836 | +6,836 (+137%) |
| **brain-protection-rules.yaml** | 8,000 | 31,035 | +23,035 (+288%) |
| **response-templates.yaml** | 3,000 | 22,752 | +19,752 (+658%) |
| **copilot-instructions.md** | 1,000 | 3,416 | +2,416 (+242%) |
| **TOTAL** | **17,000** | **69,039** | **+52,039 (+306%)** |

---

## 🎯 Optimization Strategy Guide

### When to Use `quick`
- Need immediate improvement
- Limited time available
- Testing optimization impact
- First-time optimization

### When to Use `full`
- Have 3-4 hours available
- Want to reach 17K target
- Comprehensive solution needed
- After quick optimization proved helpful

### When to Use `auto`
- Unsure which strategy to choose
- Let CORTEX decide
- Want intelligent routing

---

## 💡 Common Workflows

### First-Time Optimization (RECOMMENDED)
```bash
# Using unified CLI
python3 -m src.operations.optimize tokens status
python3 -m src.operations.optimize tokens auto
python3 -m src.operations.optimize tokens status

# Using shell script (shorter)
./scripts/optimize tokens status
./scripts/optimize tokens auto
./scripts/optimize tokens status
```

### Optimize Everything (Tokens + Files)
```bash
# One command to rule them all
python3 -m src.operations.optimize all

# This runs:
#   1. Token optimization (auto strategy)
#   2. File system optimization (organization/archives/cache)
```

### Testing Impact
```bash
# 1. Quick optimization
./scripts/optimize tokens quick

# 2. Test conversation capacity
# (Use Copilot for extended conversation)

# 3. If not enough, continue
./scripts/optimize tokens full

# 4. Or rollback if issues
./scripts/optimize tokens rollback
```

### Emergency Rollback
```bash
# Undo last optimization immediately
./scripts/optimize tokens rollback

# Verify restoration
./scripts/optimize tokens status
```

---

## 🎯 New: Unified Optimization

### Optimize All Command
```bash
python3 -m src.operations.optimize all
```

**What it does:**
1. Runs token optimization (auto strategy)
2. Runs file system optimization (all targets)
3. Consolidates databases
4. Cleans caches

**Use when:** You want comprehensive CORTEX optimization in one command

### File System Optimization
```bash
# Optimize file organization only
python3 -m src.operations.optimize files organization

# Clean archives
python3 -m src.operations.optimize files archives

# Clear caches
python3 -m src.operations.optimize files cache

# Everything
python3 -m src.operations.optimize files all
```

---

## 🛠️ Command Structure

### Unified CLI Pattern
```
python3 -m src.operations.optimize <category> <command> [options]

Categories:
  tokens   - Token optimization (governance files)
  files    - File system optimization (organization/archives/cache)
  all      - Run all optimizations

Token Commands:
  status    - Check current usage
  auto      - Auto-select strategy
  quick     - Fast optimization
  full      - Complete optimization
  rollback  - Undo last
  validate  - Check only

File Commands:
  all              - Optimize everything
  organization     - Organize documents
  archives         - Clean archives
  cortex           - CORTEX internal files
  cache            - Clear caches
  consolidation    - Consolidate databases
```

---

## ⚠️ Known Limitations

### Not Yet Implemented
The following features show "⚠️ implementation pending" warnings:

1. **YAML anchors implementation** - Stub only
2. **Section extraction from CORTEX.prompt.md** - Stub only  
3. **Template inheritance** - Stub only
4. **Module conversion** - Stub only

**Current capability:** Only template extraction works (uses existing `extract_evidence_templates_v2.py`)

### Workarounds
- **Template extraction:** Fully functional via existing script
- **Other optimizations:** Manual implementation required
- **See:** Phase 2 plan in `token-optimization-phase1-results.md`

---

## 🔧 Troubleshooting

### "KeyError: 'current_tokens'"
**Fixed** - Update to latest version

### "YAML validation failed"
**Cause:** Syntax error in optimized file  
**Solution:** Automatic rollback triggered

### "Backup not found"
**Cause:** Backup path changed or deleted  
**Solution:** Use git to restore: `git checkout HEAD -- cortex-brain/`

### "No templates to extract"
**Cause:** All large templates already extracted  
**Solution:** Try other optimization strategies (YAML anchors, module-based)

---

## 📚 Related Documentation

- **Phase 1 Results:** `cortex-brain/documents/reports/token-optimization-phase1-results.md`
- **Token Validation:** `python3 -m src.operations.align governance-tokens validate`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Governance Token Module:** `src/operations/modules/admin/governance_tokens.py`

---

**Created:** 2025-12-01  
**Version:** 1.0.0  
**Status:** Production-ready (template extraction only)
