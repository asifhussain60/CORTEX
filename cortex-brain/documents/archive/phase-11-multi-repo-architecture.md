# Phase 11: Multi-Repo Architecture Enhancement

**Version:** 1.0 | **Author:** Asif Hussain | **Created:** December 20, 2025

**Status:** 📋 PLANNED | **Dependencies:** Phase 3 Complete | **Duration:** 1 week

---

## 🎯 Overview

Transform CORTEX from single-installation, prompt-based system to true multi-repo workspace-aware architecture where one CORTEX installation serves multiple user repositories with intelligent context switching.

**Vision:** Developers install CORTEX once, use it on N repos, upgrade with simple `git pull`

**Current State:** CORTEX already has 70% of needed infrastructure (workspace detection, repo boundary enforcement, Copilot integration) but lacks orchestrator-level multi-repo awareness.

---

## 📊 Gap Analysis: Current vs Vision

### ✅ Already Implemented (70% Complete)

**Infrastructure Layer:**
- ✅ `WorkspaceContextManager` - Project discovery, test/source mapping
- ✅ `CopilotIntegration` - Active file detection, workspace folder detection
- ✅ `RepoBoundaryEnforcer` - Multi-repo isolation rules (Tier 0)
- ✅ `NamespaceDetector` - CORTEX vs workspace code detection
- ✅ `WorkspaceTopologyCrawler` - Fast multi-app workspace detection
- ✅ IDE Detection - VSCode/Visual Studio workspace awareness

**Brain Layer:**
- ✅ Tier 3 stores development context (can be repo-specific)
- ✅ Tier 2 knowledge graph (can store cross-repo patterns)
- ✅ Tier 1 conversation history (FIFO, can be tagged by repo)

**Configuration:**
- ✅ `cortex.config.json` supports multiple paths
- ✅ `.cortex-implants/` for repo-specific rules (documented)

### ❌ Missing Components (30% Remaining)

**Orchestrator Integration:**
- ❌ Orchestrators hardcoded to CORTEX directory
- ❌ No workspace detection at orchestrator entry points
- ❌ File operations always target CORTEX, not active workspace

**Brain Enhancement:**
- ❌ Tier 3 not segmented by workspace ID
- ❌ No automatic workspace context in brain queries
- ❌ Pattern learning not workspace-aware

**Configuration:**
- ❌ GIT_ISOLATION_ENFORCEMENT prevents writing to user repos
- ❌ No `.cortex/config.json` convention in user repos
- ❌ No upgrade command mechanism

**User Experience:**
- ❌ No visual indicator of active workspace
- ❌ No workspace-switching command
- ❌ No per-workspace operation history

---

## 🏗️ Target Architecture

### Workspace Structure

```
WORKSPACE/
├── CORTEX/                          # Single installation
│   ├── src/                         # Python code
│   ├── cortex-brain/                # Shared knowledge
│   │   ├── tier1/                   # Conversations (all repos)
│   │   ├── tier2/                   # Cross-repo pattern learning
│   │   ├── tier3/                   # Per-workspace context
│   │   │   ├── workspace-{uuid1}/   # User repo A context
│   │   │   ├── workspace-{uuid2}/   # User repo B context
│   │   │   └── workspace-cortex/    # CORTEX self-context
│   │   └── config/
│   │       └── workspace-registry.yaml  # All known workspaces
│   ├── .venv/
│   └── cortex.config.json           # Central config
│
├── UserApp1/                        # User repository
│   ├── .cortex/                     # Workspace-specific config
│   │   ├── config.json              # Points to CORTEX installation
│   │   └── workspace-id.txt         # UUID for brain tier3
│   ├── .cortex-implants/            # Repo-specific rules (optional)
│   ├── src/                         # User code (CORTEX writes HERE)
│   ├── tests/                       # User tests (CORTEX writes HERE)
│   └── .git/
│
├── UserApp2/                        # Another user repository
│   ├── .cortex/
│   ├── src/
│   └── .git/
│
└── workspace.code-workspace         # VSCode workspace definition
```

### Context Flow (Cross-IDE)

**VSCode:**
```
1. User opens file in UserApp1/src/login.py
   ↓
2. VSCode API: vscode.window.activeTextEditor → UserApp1 detected
   ↓
3. CORTEX loads .cortex/config.json → Gets workspace UUID
   ↓
4. Brain Tier 3 loads context from workspace-{uuid}/
   ↓
5. Orchestrator writes files to UserApp1/ (NOT CORTEX/)
   ↓
6. Brain saves patterns to Tier 2 (shared) + Tier 3 (workspace-specific)
```

**Visual Studio 2019+:**
```
1. User opens file in UserApp1/Services/LoginService.cs
   ↓
2. VS API: DTE2.ActiveDocument → UserApp1 detected
   ↓
3. CORTEX loads .cortex/config.json → Gets workspace UUID
   ↓
4. Brain Tier 3 loads context from workspace-{uuid}/
   ↓
5. Orchestrator writes files to UserApp1/ (NOT CORTEX/)
   ↓
6. Brain saves patterns to Tier 2 (shared) + Tier 3 (workspace-specific)
```

**Fallback (Both IDEs):**
```
If IDE API unavailable → Parse CWD → Find .cortex/ directory → Load workspace
```

---

## 📋 Implementation Plan

### Package 1: Workspace Registry & Detection (2 days)

**Goal:** Central registry of all known workspaces with auto-detection

**Tasks:**
1. Create `WorkspaceRegistry` class
   - Location: `src/core/workspace_registry.py`
   - Stores: UUID, path, last_accessed, project_type
   - Auto-discovers workspaces on first CORTEX run
   - Persists to: `cortex-brain/config/workspace-registry.yaml`

2. Create workspace initialization command
   - Command: `cortex init workspace` (run in user repo)
   - Creates: `.cortex/config.json`, `.cortex/workspace-id.txt`
   - Registers workspace in central registry

3. Add workspace detection utility
   - Function: `detect_active_workspace() -> WorkspaceInfo`
   - Priority order:
     1. **VSCode API** (`vscode.workspace.workspaceFolders` + `vscode.window.activeTextEditor`)
     2. **Visual Studio API** (`DTE2.ActiveDocument` + solution parser)
     3. **Copilot Chat context** (GitHub Copilot integration)
     4. **Fallback to CWD** (parse directory tree for `.cortex/`)
   - Returns: workspace_id, path, project_type, ide_type

**Tests:**
- `tests/core/test_workspace_registry.py` (20 tests, updated from 15)
- Test multi-workspace discovery
- Test registration/deregistration
- Test UUID collision handling
- **NEW:** Test VSCode detection scenarios
- **NEW:** Test Visual Studio 2019+ detection scenarios
- **NEW:** Test IDE fallback chain

### Package 2: Brain Tier 3 Segmentation (2 days)

**Goal:** Separate development context per workspace

**Tasks:**
1. Refactor Tier 3 structure
   - Old: `cortex-brain/tier3/code-hotspots.yaml`
   - New: `cortex-brain/tier3/workspace-{uuid}/code-hotspots.yaml`
   - Migration script for existing data

2. Add workspace context to all Tier 3 queries
   - Modify: `src/tier3/*.py` (all 5 modules)
   - Add: `workspace_id` parameter to all read/write operations
   - Default: "workspace-cortex" for CORTEX self-operations

3. Update Brain query API
   - Change: `brain.get_context()` → `brain.get_context(workspace_id)`
   - Add: Auto-detection if workspace_id not provided

**Tests:**
- `tests/tier3/test_workspace_segmentation.py` (20 tests)
- Test context isolation between workspaces
- Test migration from old structure
- Test fallback to default workspace

### Package 3: Remove GIT_ISOLATION_ENFORCEMENT (1 day)

**Goal:** Allow orchestrators to write to user repos

**Tasks:**
1. Update brain protection rules
   - File: `cortex-brain/core/brain-protection-rules.yaml`
   - Action: REMOVE `GIT_ISOLATION_ENFORCEMENT` rule
   - Replace with: `WORKSPACE_AWARE_OPERATIONS` (validates target)

2. Create workspace operation validator
   - Class: `WorkspaceOperationValidator`
   - Location: `src/tier0/workspace_operation_validator.py`
   - Validates: Target path matches active workspace
   - Prevents: Writing to wrong workspace or CORTEX directory

3. Update RepoBoundaryEnforcer
   - Modify: `src/tier0/repo_boundary_enforcer.py`
   - Change: Allow CORTEX → User repo writes
   - Block: User repo → User repo writes (still isolated)

**Tests:**
- `tests/tier0/test_workspace_operation_validator.py` (12 tests)
- Test valid workspace operations
- Test cross-workspace prevention
- Test CORTEX directory protection

### Package 4: Orchestrator Workspace Integration (2 days)

**Goal:** All orchestrators workspace-aware

**Tasks:**
1. Add workspace detection to BaseOrchestrator
   - File: `src/orchestrators/base_orchestrator.py`
   - Add: `self.workspace_info = detect_active_workspace()`
   - Add: `self.target_directory = workspace_info.path`

2. Update 4 completed orchestrators
   - ExecutionOrchestrator: Change output directory
   - DocumentationOrchestrator: Write to workspace docs/
   - TDDOrchestrator: Write tests to workspace tests/
   - PlanningOrchestrator: Write plans to workspace planning/

3. Add workspace context to logging
   - All log messages include: `[workspace:{name}]`
   - Brain Tier 1 tags conversations with workspace_id

**Tests:**
- `tests/orchestrators/test_workspace_integration.py` (25 tests)
- Test each orchestrator writes to correct workspace
- Test workspace switching mid-operation
- Test error handling for invalid workspace

### Package 5: Upgrade Mechanism (1 day)

**Goal:** Simple `upgrade cortex` command

**Tasks:**
1. Create upgrade orchestrator
   - File: `src/orchestrators/system/upgrade_orchestrator.py`
   - Steps: Git pull → pip install -r requirements.txt → healthcheck
   - Safety: Backup brain before upgrade, rollback on failure

2. Add upgrade command
   - Command: `upgrade cortex` (Copilot Chat)
   - Triggers: CLI wrapper → upgrade orchestrator
   - Output: Version change, new features summary

3. Add version compatibility check
   - Compare: Current version vs workspace .cortex/min-cortex-version
   - Warn: If workspace requires newer CORTEX version

**Tests:**
- `tests/orchestrators/system/test_upgrade_orchestrator.py` (10 tests)
- Test upgrade happy path
- Test rollback on failure
- Test version compatibility warnings

---

## 🎯 Success Metrics

**Functional:**
- ✅ One CORTEX installation serves 3+ user repos
- ✅ Orchestrators write to active workspace (not CORTEX)
- ✅ Brain Tier 3 context isolated per workspace
- ✅ Upgrade command works without breaking workspaces

**Quality:**
- ✅ 90%+ test coverage on new components
- ✅ All existing tests pass (no regressions)
- ✅ Zero cross-workspace data leakage

**User Experience:**
- ✅ Workspace auto-detected in <200ms
- ✅ Visual feedback shows active workspace
- ✅ No manual configuration required after `cortex init workspace`

---

## 🔗 Dependencies

**Requires Complete:**
- Phase 3: BaseOrchestrator, Brain Tier 1-3, IDE Detection

**Enables:**
- Phase 12 (Future): MCP Server Architecture (can build on this)
- Phase 13 (Future): Remote CORTEX (central server model)

**Blocks:**
- None (fully isolated phase)

---

## 📚 Documentation Updates Required

**New Documents:**
1. `cortex-brain/documents/implementation-guides/multi-repo-setup-guide.md`
   - How to initialize workspace
   - How to switch between workspaces
   - Troubleshooting workspace detection

2. `cortex-brain/documents/architecture/workspace-architecture.md`
   - Workspace registry design
   - Brain segmentation rationale
   - Cross-repo pattern learning

**Updated Documents:**
1. `CORTEX.prompt.md`
   - Add workspace-aware operation examples
   - Update architecture diagrams
   - Add upgrade command

2. `.github/copilot-instructions.md`
   - Remove GIT_ISOLATION warning
   - Add workspace detection section

3. `README.md`
   - Add multi-repo setup instructions
   - Update quick start for workspace initialization

4. `cortex-brain/core/brain-protection-rules.yaml`
   - Document WORKSPACE_AWARE_OPERATIONS rule
   - Archive GIT_ISOLATION_ENFORCEMENT with deprecation note

---

## 🚨 Risks & Mitigations

**Risk 1: Breaking existing single-repo usage**
- Mitigation: Backward compatibility - if no `.cortex/`, assume single-repo mode
- Fallback: Use "workspace-default" for non-initialized repos

**Risk 2: Brain data migration complexity**
- Mitigation: Migration script with dry-run mode
- Rollback: Keep backup of tier3/ before migration

**Risk 3: Performance degradation with workspace detection**
- Mitigation: Cache workspace info for 5 minutes
- Optimization: Load workspace context async in background

**Risk 4: User confusion about which repo is active**
- Mitigation: Always show workspace name in responses
- Visual: `[workspace:UserApp1]` prefix in all operations

---

## ✅ Acceptance Criteria

**Must Have:**
1. ✅ Developer installs CORTEX once, uses on 3 different repos
2. ✅ Orchestrators correctly detect active workspace (95% accuracy)
3. ✅ Files created in correct workspace directory (100% accuracy)
4. ✅ Brain context isolated per workspace (zero leakage)
5. ✅ Upgrade command updates CORTEX without breaking workspaces
6. ✅ All existing tests pass (zero regressions)
7. ✅ 90%+ test coverage on new components

**Should Have:**
1. ✅ Workspace detection < 200ms
2. ✅ Visual feedback shows active workspace
3. ✅ Documentation covers common scenarios

**Nice to Have:**
1. ⚪ Workspace switcher command in Copilot Chat
2. ⚪ Cross-repo pattern suggestions ("You did X in App1, try it in App2?")
3. ⚪ Workspace health dashboard showing all registered workspaces

---

## 📝 Implementation Notes

**Technology Choices:**
- Workspace IDs: UUID v4 (collision-proof)
- Registry format: YAML (human-readable, git-friendly)
- Detection priority: VSCode API > Copilot > CWD

**Code Style:**
- Follow existing CORTEX patterns
- Type hints required on all new functions
- Docstrings follow Google style guide

**Testing Strategy:**
- Unit tests: Each component isolated
- Integration tests: Multi-workspace scenarios
- E2E tests: Full workflow from Copilot Chat

---

## 🔄 Rollback Plan

If phase fails, rollback sequence:

1. Restore `GIT_ISOLATION_ENFORCEMENT` in brain-protection-rules.yaml
2. Revert BaseOrchestrator changes (git checkout)
3. Delete workspace registry file
4. Keep new code (src/core/workspace_registry.py) but disable via feature flag
5. Update CORTEX.prompt.md to remove workspace-aware examples

**Rollback Time:** 30 minutes  
**Data Loss:** None (brain tier3 migration is additive)

---

## 📞 Contact

**Phase Owner:** Asif Hussain  
**Start Date:** TBD (after Phase 6-10 complete)  
**Estimated Completion:** 1 week (5 packages, 8 days effort)
