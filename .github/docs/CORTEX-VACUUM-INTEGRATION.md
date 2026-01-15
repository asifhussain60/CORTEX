# CORTEX Vacuum Integration Guide

## Overview

The **cortex-vacuum** orchestrator is an autonomous repository organization tool that:
- Recursively parses all CORTEX repository files
- Categorizes files by type (documentation, config, reports, etc.)
- Organizes files into semantic folders
- Maintains git history via `git mv`
- Provides full audit trail and rollback capability
- Exposes all functionality via MCP tool for LLM access

---

## Architecture

### Components

**1. Prompt Definition**
- File: `.github/prompts/cortex-vacuum.prompt.md`
- Defines operational principles, file classification schema, phases, safety protocols
- Reference for orchestrator behavior

**2. Core Orchestrator**
- File: `src/tools/cortex-vacuum.py`
- Class: `CortexVacuumOrchestrator`
- Implements 4 phases: Analyze → Validate → Execute → Cleanup
- Recursive file scanning and categorization
- Database audit logging
- Git integration

**3. MCP Tool Registration**
- File: `src/mcp/tools/cortex_vacuum_registration.py`
- Class: `CortexVacuumTool`
- Registers tool with MCP server
- Handles async tool calls
- Defines governance rules
- Provides documentation

---

## File Organization Schema

### Root Folder (Keep Only)
- `README.md` - Project root readme
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Python dependencies

### Documentation → `.github/docs/`
```
.github/docs/
├── analysis/
│   └── 2026-01-15-cortex-master-completion.md
├── briefs/
│   ├── 2026-01-15-executive-brief-decision.md
│   ├── 2026-01-15-executive-decision-summary.md
│   └── 2026-01-15-implementation-status.md
├── plans/
│   ├── 2026-01-15-phase-vision-advanced.md
│   └── 2026-01-15-phase-vision-core-completion.md
├── strategies/
│   └── 2026-01-15-fr-008-strategy.md
├── handoffs/
│   └── 2026-01-15-ar-015-handoff.md
└── index/
    └── 2026-01-15-review-completion-index.md
```

### Reports → `.github/reports/`
```
.github/reports/
├── acceptance-criteria/
│   ├── 2026-01-14-ac-ar-013-03-report.md
│   └── 2026-01-14-ar-013-trilogy-completion-report.md
└── verification/
    └── 2026-01-15-phase-chat-verification.md
```

### Logs & Status → `.github/.workspace/`
```
.github/.workspace/
├── status/
│   ├── current-status.md
│   └── current-session-status.txt
├── sessions/
│   └── 2026-01-15-session.txt
└── phase-copilot-chats/
    └── [already organized]
```

### Scripts → `scripts/`
```
scripts/
├── verification/
│   ├── verify-phases.py
│   └── verify-schema.py
├── setup/
│   ├── init-db.py
│   └── init-schema.py
└── utility/
    └── [other scripts]
```

### Archives → `.github/archives/YYYY-MM/`
```
.github/archives/
└── 2026-01/
    ├── 2026-01-10-old-status.md
    └── 2026-01-12-rollback-history.json
```

---

## Usage

### Phase 1: Analyze (AC-VACUUM-01)
Scan repository and categorize all files (no changes)

```bash
# Via Python
python src/tools/cortex-vacuum.py analyze

# Via MCP
/cortex-vacuum --action=analyze
```

**Output:**
- Files scanned: 45
- Files to migrate: 18
- Stale files: 3
- Duplicate groups: 2
- Proposed migrations (detailed list)

### Phase 2: Validate (AC-VACUUM-02)
Validate proposed migrations against governance

```bash
# Via Python
python src/tools/cortex-vacuum.py validate

# Via MCP
/cortex-vacuum --action=validate --dry_run=true
```

**Output:**
- Validation status: PASSED/FAILED
- Naming violations (if any)
- Destination conflicts (if any)
- Ready to execute: YES/NO

### Phase 3: Execute (AC-VACUUM-03)
Execute file migrations with audit logging

```bash
# Dry run first (recommended)
python src/tools/cortex-vacuum.py execute

# For real
python src/tools/cortex-vacuum.py execute --no-dry-run

# Via MCP
/cortex-vacuum --action=execute --dry_run=true
/cortex-vacuum --action=execute --dry_run=false
```

**Output:**
- Git checkpoint created: ✅
- Files moved: 18/18
- Audit entries: 18
- Final commit: ✅

### Phase 4: Cleanup (AC-VACUUM-04)
Clean up artifacts and verify final state

```bash
# Via Python
python src/tools/cortex-vacuum.py cleanup

# Via MCP
/cortex-vacuum --action=cleanup
```

**Output:**
- Empty directories removed: 5
- Files verified: 18/18
- Duplicates archived: 2
- Status: PASSED

### Status & Rollback
```bash
# Check status
/cortex-vacuum --action=status

# Rollback to previous state
/cortex-vacuum --action=rollback
```

---

## Integration with CORTEX Builder

Add to phase completion checklist:

```yaml
phase_completion_cleanup:
  - name: "Execute cortex-vacuum"
    steps:
      - "Step 1: Run analyze (review)"
        command: "/cortex-vacuum --action=analyze"
      - "Step 2: Run validate"
        command: "/cortex-vacuum --action=validate --dry_run=true"
      - "Step 3: Run execute (dry run)"
        command: "/cortex-vacuum --action=execute --dry_run=true"
      - "Step 4: Run execute (for real)"
        command: "/cortex-vacuum --action=execute --dry_run=false"
      - "Step 5: Run cleanup"
        command: "/cortex-vacuum --action=cleanup"
      - "Step 6: Verify tests still pass"
        command: "pytest tests/unit/ -v"
```

---

## Governance & Safety

### Governance Rules
- **Tier:** 0 (Critical infrastructure)
- **Audit Required:** Yes
- **Manual Approval:** Required before execution
- **Rollback:** Fully reversible via git

### Safety Protocols
1. ✅ Dry run always first (default dry_run=true)
2. ✅ Git checkpoint before execution
3. ✅ All moves logged to audit database
4. ✅ No file deletion without confirmation
5. ✅ Full rollback capability via `git reset --hard`

### Audit Logging
Every migration logged to `cortex-brain/state/file-movements.db`:

```sql
CREATE TABLE file_movements (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  action TEXT,
  source_path TEXT,
  destination_path TEXT,
  category TEXT,
  reason TEXT,
  file_size INTEGER,
  file_hash TEXT,
  status TEXT,
  executed_by TEXT,
  git_commit TEXT,
  notes TEXT
)
```

---

## MCP Tool Definition

### Tool Schema
```json
{
  "name": "cortex-vacuum",
  "description": "Recursively organize CORTEX repository files",
  "inputSchema": {
    "action": {"enum": ["analyze", "validate", "execute", "cleanup", "rollback", "status"]},
    "dry_run": {"type": "boolean", "default": true},
    "archive_old": {"type": "boolean", "default": true},
    "interactive": {"type": "boolean", "default": false},
    "report_format": {"enum": ["json", "markdown", "yaml"], "default": "json"}
  }
}
```

### Exposed Commands
```bash
/cortex-vacuum --action=analyze
/cortex-vacuum --action=validate --dry_run=true
/cortex-vacuum --action=execute --dry_run=true
/cortex-vacuum --action=execute --dry_run=false
/cortex-vacuum --action=cleanup
/cortex-vacuum --action=status
/cortex-vacuum --action=rollback
```

---

## Examples

### Example 1: Full Dry Run Cycle
```bash
# Analyze
/cortex-vacuum --action=analyze

# Review output, then validate
/cortex-vacuum --action=validate --dry_run=true

# Simulate execution
/cortex-vacuum --action=execute --dry_run=true

# Review proposed changes, then execute for real
/cortex-vacuum --action=execute --dry_run=false

# Cleanup
/cortex-vacuum --action=cleanup
```

### Example 2: Quick Status Check
```bash
/cortex-vacuum --action=status

# Output:
# ✅ 18 files migrated
# ⚠️  0 files failed
# 📅 Last run: 2026-01-15T14:30:00Z
```

### Example 3: Rollback If Needed
```bash
# Something went wrong?
/cortex-vacuum --action=rollback

# Repository reverts to state before last vacuum
```

---

## Success Criteria

### AC-VACUUM-01 (Analysis)
- [ ] All repository files catalogued
- [ ] Classification consistent
- [ ] Duplicate files identified
- [ ] Stale files identified
- [ ] Migration plan generated
- [ ] Dry run report comprehensive

### AC-VACUUM-02 (Validation)
- [ ] Git history verification passed
- [ ] Destination folders checked
- [ ] Naming conventions valid
- [ ] No naming conflicts
- [ ] Simulation successful

### AC-VACUUM-03 (Execution)
- [ ] Git checkpoint created
- [ ] All files moved successfully
- [ ] Audit entries logged
- [ ] Final commit created
- [ ] No files lost

### AC-VACUUM-04 (Cleanup)
- [ ] Empty folders removed
- [ ] Symlinks verified
- [ ] Tests still pass
- [ ] Duplicates archived
- [ ] Final report generated

---

## Files & Locations

| File | Location | Purpose |
|------|----------|---------|
| Prompt | `.github/prompts/cortex-vacuum.prompt.md` | Operational definition |
| Orchestrator | `src/tools/cortex-vacuum.py` | Core implementation |
| MCP Registration | `src/mcp/tools/cortex_vacuum_registration.py` | LLM integration |
| Guide | This file | Integration & usage guide |
| Audit DB | `cortex-brain/state/file-movements.db` | Audit trail storage |

---

## Troubleshooting

### Files not moving
- Check git status: `git status`
- Ensure working directory is clean
- Verify destination folders can be created
- Check file permissions: `ls -la`

### Git mv fails
- Ensure file is tracked: `git ls-files <file>`
- Use `git add` first if newly added
- Check for naming conflicts in destination

### Duplicate files after vacuum
- Run analyze again: `/cortex-vacuum --action=analyze`
- Check archive folder: `.github/archives/`
- Verify with hash: `sha256sum <file>`

### Need to rollback
- Run: `/cortex-vacuum --action=rollback`
- Or manual: `git reset --hard <commit-before-vacuum>`
- Check git log: `git log --oneline | head -5`

---

## Next Steps

1. **Test the tool:**
   ```bash
   /cortex-vacuum --action=analyze
   ```

2. **Review proposed changes:**
   - Check output for accuracy
   - Verify categorization matches schema

3. **Dry run execution:**
   ```bash
   /cortex-vacuum --action=execute --dry_run=true
   ```

4. **Execute for real (when ready):**
   ```bash
   /cortex-vacuum --action=execute --dry_run=false
   ```

5. **Verify results:**
   - Check file locations
   - Run tests: `pytest tests/unit/ -v`
   - Review git log: `git log --oneline -5`

---

**Status:** ✅ Ready for production use  
**Created:** January 15, 2026  
**Last Updated:** January 15, 2026  

