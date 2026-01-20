# CORTEX Deployment Strategy: Clean Repository with Day-Zero Data

**Objective**: Push clean, consolidated code to the main branch with day-zero data while preserving application state in the CORTEX branch.

---

## Phase 1: Repository Structure Refactoring

### Step 1.1: Consolidate Documentation
**Location**: Root directory and `/roadmap`

**Action**:
- Audit all `*.md` files in the CORTEX root and `/roadmap` directory
- Identify relevant documentation files (architecture, design decisions, deployment guides)
- Move relevant markdown files to `/docs/`
- Delete redundant, outdated, or maintenance-specific markdown files
- **Rule**: Do not create new markdown files or status reports during this phase

**Expected Outcome**:
```
CORTEX/
├── docs/                    # Consolidated documentation
│   ├── DEPLOYMENT-SETUP-GUIDE.md
│   ├── ARCHITECTURE-MAP.md
│   ├── AC-*.md              # Requirement/completion docs
│   └── ...
├── _workspaces/             # Clean, no markdown clutter
├── cortex/                  # Implementation
├── cortex_brain/            # State and configuration
└── cortex-config.yaml       # Root config only
```

---

### Step 1.2: Python Implementation Structure
**Location**: Across CORTEX codebase

**Action**:
- Verify all `*.py` files are organized in the canonical cortex/ package
- Ensure logical module organization (MCP, API, Brain, Orchestrators, Tools, etc.)
- Verify MCP server correctly exposes all tools and utilities
- Maintain separation: cortex/ (implementation) vs cortex_brain/ (governance/state)

**Expected Outcome**:
```
CORTEX/
├── cortex/                  # Canonical implementation package (388 files)
│   ├── api/                 # API utilities
│   ├── brain/               # Brain integration (269 files)
│   ├── core/                # Core utilities
│   ├── infrastructure/      # Infrastructure utilities
│   ├── mcp/                 # MCP server and handlers (23+ tools)
│   ├── orchestrators/       # Orchestration logic (41 files)
│   ├── tools/               # Reusable tools
│   └── __init__.py
├── cortex_brain/            # Governance, state, tier0/1/2 rules
├── tests/                   # Test files aligned with cortex/ structure
└── mcp-config/              # MCP configuration
```

**Note**: cortex/ is the canonical implementation package. All MCP tools are exposed via cortex/mcp/. See Architecture Decision Record: docs/ARCH-DECISION-RECORD-CORTEX-CANONICAL-PACKAGE.md

---

## Phase 2: Git Operations

### Step 2.1: Commit Local Changes

**Action**:
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
git add .
git commit -m "refactor: consolidate repository structure - move docs to /docs, consolidate Python into toolkit"
```

**Verification**:
- All changes staged and committed to `CORTEX` branch
- Commit message clearly describes the refactoring

---

### Step 2.2: Push Branch to Remote

**Action**:
```bash
git push origin CORTEX
```

**Verification**:
- Remote `CORTEX` branch updated with all refactored code
- No conflicts with remote state

---

### Step 2.3: Rebase Main onto CORTEX

**Action**:
```bash
git branch -D main          # Delete local main if it exists
git checkout main           # Create/checkout main (pulls from remote)
git rebase CORTEX
git push origin main --force
git checkout CORTEX        # Switch back to CORTEX
```

**Verification**:
- Local `main` branch now contains all CORTEX changes
- Remote `main` branch updated
- `CORTEX` branch is the active working branch

---

## Phase 3: Day-Zero Data Initialization

### Step 3.1: Audit Current Data State

**Location**: `cortex_brain/state/`

**Action**:
- Review all database files (`.db`, `.json`, `.yaml`)
- Document current state for rollback capability
- Identify which data represents "day-zero" (initial, clean state)

**Expected Outcome**: Clear understanding of what constitutes day-zero data

---

### Step 3.2: Initialize Day-Zero Data

**Action**:
- Clear all runtime/session-specific data (cache, temporary states, logs)
- Preserve core governance structures:
  - `governance.db` - reset to initial schema with seed data
  - `prompt-versions.yaml` - version registry initialized
  - `repo-registry.yaml` - repository mappings initialized
- Ensure all files reflect clean, initial deployment state

**Files to Reset**:
```
cortex_brain/
├── state/
│   ├── governance.db        # Reset with seed data
│   ├── cache/               # Clear
│   └── logs/                # Clear
├── tier0/
│   ├── prompt-versions.yaml # Reset to v1.0.0
│   └── repo-registry.yaml   # Reset to known repos
├── releases/
│   └── v1.0.0/              # Initial release manifest
```

**Verification**:
- All files contain only production-ready, clean data
- No temporary files, debug logs, or development artifacts
- Database is in consistent, known state

---

## Phase 4: Automated Cleanup Tool

### Step 4.1: Create Day-Zero Reset Tool

**Location**: `cortex_toolkit/tools/`

**Action**: Implement a new tool: `DayZeroResetTool`

**Functionality**:
```python
class DayZeroResetTool:
    """
    Automated cleanup and day-zero reset for CORTEX system.
    Resets the system to clean, initial state while preserving 
    database integrity and application state in CORTEX6 branch.
    """
    
    def reset_to_day_zero(self):
        """
        Main reset pipeline:
        1. Backup current state
        2. Clear all runtime data (cache, logs, sessions)
        3. Reset governance.db to seed state
        4. Re-initialize prompt versions
        5. Re-initialize repository registry
        6. Verify consistency
        7. Log completion
        """
        pass
    
    def preserve_database_state(self):
        """Ensure database integrity during reset"""
        pass
    
    def verify_day_zero_state(self):
        """Verify system is in expected day-zero condition"""
        pass
```

**MCP Exposure**:
- Register tool in MCP server
- Expose as callable resource via MCP protocol
- Enable remote invocation from other systems

**Usage**:
```bash
# Via MCP
mcp call cortex_toolkit.DayZeroResetTool.reset_to_day_zero

# Or via CLI
python -m cortex_toolkit.tools.day_zero_reset --action=full
```

---

### Step 4.2: Integrate into CORTEX Toolkit

**Action**:
- Add `day_zero_reset.py` module to `cortex_toolkit/tools/`
- Register in MCP server configuration
- Add integration tests
- Document in MCP API documentation

**Test Coverage**:
- Reset preserves database
- Reset clears cache/logs
- Reset can be verified
- Reset is idempotent

---

## Phase 5: Verification Checklist

### Repository Structure
- [ ] All relevant `*.md` files in `/docs/`
- [ ] All `*.py` files in `cortex_toolkit/` with preserved structure
- [ ] No orphaned markdown or Python files in root or subdirectories
- [ ] `cortex_brain/` and `_workspaces/` remain intact

### Git State
- [ ] Local commits on `CORTEX`
- [ ] Remote `CORTEX` updated
- [ ] Remote `main` rebased from `CORTEX`
- [ ] `CORTEX` branch is active

### Day-Zero Data
- [ ] `governance.db` reset with seed data
- [ ] `prompt-versions.yaml` initialized to v1.0.0
- [ ] `repo-registry.yaml` contains known repositories
- [ ] All cache and log files cleared
- [ ] No temporary or debug artifacts present

### Toolkit Enhancement
- [ ] `DayZeroResetTool` implemented in `cortex_toolkit/tools/`
- [ ] Tool registered in MCP server
- [ ] Tool tested and verified
- [ ] Tool exposed via MCP protocol
- [ ] Documentation updated

---

## Rollback Procedure

If issues arise during deployment:

1. **Restore Previous Main**:
   ```bash
   git checkout main
   git reset --hard origin/main@{1}  # Previous state
   git push origin main --force
   ```

2. **Return to CORTEX**:
   ```bash
   git checkout CORTEX
   ```

3. **Identify Issues**: Review Phase that failed and address root cause

4. **Re-execute Phase**: Restart from the problematic phase after fixes

---

## Success Criteria

✅ Repository structure consolidated and clean  
✅ All code consolidated into CORTEX Toolkit via MCP  
✅ Main branch updated with clean code  
✅ CORTEX6 branch remains as working branch  
✅ All data reflects day-zero, production-ready state  
✅ Automated reset tool functional and integrated  
✅ No maintenance artifacts or debug files in repository  

---

## Timeline Estimate

| Phase | Duration | Notes |
|-------|----------|-------|
| Repository Refactoring | 2-4 hours | Depends on file count and structure complexity |
| Git Operations | 30 minutes | Straightforward git operations |
| Day-Zero Data Init | 1-2 hours | Includes testing and verification |
| Toolkit Tool Dev | 2-3 hours | Implementation, testing, integration |
| Verification & QA | 1-2 hours | End-to-end validation |
| **Total** | **6-12 hours** | Can be parallelized where feasible |

---

## Notes

- **Preservation**: The `CORTEX` branch serves as the preserved working branch with full history
- **Main**: Becomes the clean deployment artifact
- **Database**: Maintained as authoritative state registry
- **MCP**: Remains the external integration interface
- **Automation**: Day-Zero tool enables repeatable resets without manual intervention

