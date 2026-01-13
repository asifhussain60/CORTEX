# 🔄 CORTEX Git Commit Orchestrator (v1.0)

**Purpose:** Intelligent git operations with zero untracked files, orchestrator registration, and working copy synchronization.  
**Design goal:** Automated, intelligent file classification + orchestrator discovery + remote sync.  
**Version:** 1.0.0 | **Date:** 2026-01-13  
**Integration:** Works with MasterOrchestrator to maintain working tree consistency.

---

## 🎯 Philosophy

**Zero Untracked Files Policy:**
- Every untracked file is intentionally classified
- Classification: COMMIT (work output) vs IGNORE (build artifacts) vs RESET (temporary)
- After each operation: `git status` shows clean working tree
- All work is discoverable and auditable

**Orchestrator Registration:**
- Auto-discover completed orchestrators
- Wire in MCP tools for discovered capabilities
- Update orchestrator registry with phase completion
- Track implementation provenance

**Working Copy Sync:**
- Pull latest orchestrator code from remote
- Merge new capabilities into local orchestrator registry
- Update AC-INDEX with new work completed on remote
- Zero merge conflicts via intelligent merging

---

## 📋 Untracked File Classification Protocol

**When git shows untracked files, classify each:**

### Category 1: COMMIT (Work Output)
These files represent completed work that should be tracked.

| File Pattern | Action | Reason |
|--------------|--------|--------|
| `src/**/*.py` (new implementations) | COMMIT | New features/orchestrators |
| `tests/**/*.py` (new test files) | COMMIT | TDD evidence |
| `cortex-brain/tier*/orchestrators/*.yaml` | COMMIT | Orchestrator manifests |
| `cortex-brain/documents/reports/*.md` | COMMIT | Architecture/implementation docs |
| `README.md`, `ARCHITECTURE.md` | COMMIT | Project documentation |
| `.github/prompts/*.md` (new prompts) | COMMIT | New governance/routing prompts |
| `cortex-brain/tier*/governance/*.yaml` (new rules) | COMMIT | Governance rules |

### Category 2: IGNORE (Build/Analysis Artifacts)
These files are auto-generated and should never be tracked.

| File Pattern | Action | Reason |
|--------------|--------|--------|
| `.cortex/*.md` | IGNORE | Chat/analysis documents (already in .gitignore) |
| `cortex-brain/cx6-plan/viewer/*-backup-*.json` | IGNORE | Auto backups (already in .gitignore) |
| `cortex-brain/audit-logs/*.jsonl` | IGNORE | Live audit logs |
| `cortex-brain/documents/reports/architecture-audit-*.json` | IGNORE | Auto-generated audit reports |
| `__pycache__/`, `*.pyc`, `.pytest_cache/` | IGNORE | Python build artifacts |
| `.coverage`, `htmlcov/` | IGNORE | Test coverage reports |
| `*.db-wal`, `*.db-shm` | IGNORE | SQLite temp files |

### Category 3: RESET (Temporary/Stale)
These files were from past operations and should be removed.

| File Pattern | Action | Reason |
|--------------|--------|--------|
| `*.tmp`, `*.bak` | RESET | Temporary files |
| Old backup files (>7 days old) | RESET | Stale backups |
| `build/`, `dist/` | RESET | Build directories |

---

## 🔍 Intelligent File Detection Algorithm

```python
# Pseudo-code for file classification

def classify_untracked_files(untracked_list):
    """Classify all untracked files intelligently."""
    
    commits = []
    ignores = []
    resets = []
    
    for file in untracked_list:
        # Check explicit .gitignore patterns first
        if matches_gitignore(file):
            ignores.append(file)
            continue
        
        # Check file path and extension
        if is_implementation_file(file):  # src/**/*.py, tests/**/*.py, etc.
            commits.append(file)
        elif is_documentation_file(file):  # *.md, *.yaml in docs/tier*/
            commits.append(file)
        elif is_artifact_file(file):  # __pycache__, .pytest_cache, *.pyc
            ignores.append(file)
        elif is_temporary_file(file):  # *.tmp, *.bak, build/
            resets.append(file)
        elif file.endswith('.md') and is_analysis_doc(file):
            ignores.append(file)  # .cortex/*.md, refinement-*.md
        else:
            # Default: ask user
            user_choice = prompt_user(f"Classify {file}?")
            if user_choice == "commit":
                commits.append(file)
            elif user_choice == "ignore":
                add_to_gitignore(file)
                ignores.append(file)
            else:
                git_reset_file(file)
                resets.append(file)
    
    return commits, ignores, resets
```

---

## 🔗 Orchestrator Registration & Discovery

**When committing work, also register orchestrators:**

### Step 1: Discover Completed Orchestrators
```bash
# Search for new orchestrator files in src/orchestrators/
find src/orchestrators -name "*.py" -newer <last_commit>
# Check for orchestrator class definitions (marked with @OrchestratorRegistry.register)
```

### Step 2: Parse Orchestrator Metadata
```python
# Extract from orchestrator file:
# - Orchestrator ID (e.g., "crawler", "planner")
# - Domain (e.g., "analysis", "planning")
# - Capabilities (list of things it can do)
# - AC-IDs it implements
# - Phase completed in
```

### Step 3: Register in OrchestratorRegistry
```bash
python3 -m src.orchestrators.master.orchestrator_registry \
  register \
  --id <orchestrator_id> \
  --class-name <ClassName> \
  --domain <domain> \
  --capabilities <cap1,cap2,...> \
  --ac-ids <AC-001,AC-002,...>
```

### Step 4: Wire MCP Tools
```python
# For each capability, create MCP tool entry:
# - Tool name: camelCase version of capability
# - Tool description: From orchestrator docstring
# - Tool parameters: Extracted from function signatures
# - Tool handler: Points to orchestrator method
```

### Step 5: Update Intent Router
```yaml
# Update .github/prompts/AC-mappings.json
# Add new orchestrator to routing table:
intent_patterns:
  - pattern: "crawler"
    route_to: "crawler_orchestrator"
    priority: 35
    ac_ids: [AC-CRAWLER-001, AC-CRAWLER-002, ...]
```

---

## 🔄 Working Copy Sync Protocol

**When pulling from remote, sync orchestrators and capabilities:**

### Step 1: Detect Remote Changes
```bash
# Check what changed on remote
git fetch origin
git log --oneline origin/CORTEX6..HEAD | grep -E "src/orchestrators|AC-" | head -20
```

### Step 2: Extract New Orchestrators from Remote
```bash
# Find new orchestrator files
git diff --name-only origin/CORTEX6..HEAD | grep "src/orchestrators/"

# For each new file:
# 1. Extract orchestrator metadata
# 2. Register locally
# 3. Wire MCP tools
```

### Step 3: Merge AC-INDEX Changes
```python
# When AC-INDEX.yaml differs between local and remote:
# 1. Load both versions
# 2. Identify new AC-IDs on remote
# 3. Merge strategically:
#    - Keep local completed work
#    - Add new remote AC-IDs
#    - Reconcile conflicts via orchestrator phase tracking
# 4. Write merged AC-INDEX back
```

### Step 4: Update Orchestrator Registry
```bash
# For each new AC-ID from remote:
# 1. Find implementing orchestrator
# 2. Update local registry with new capability
# 3. Re-generate MCP tool manifests
# 4. Update routing tables
```

---

## 🎬 Git Commit Workflow

**Complete flow for intelligent git commit:**

```
START
  ↓
1. Load Current State
  - git status → get untracked files
  - Parse progress-tracker.json
  - Load orchestrator_registry.json
  ↓
2. Classify Untracked Files
  - For each file: COMMIT, IGNORE, or RESET?
  - Auto-detect via path patterns
  - Prompt user for ambiguous files
  ↓
3. Process Classifications
  - COMMIT files: git add
  - IGNORE files: add to .gitignore
  - RESET files: git checkout (discard)
  ↓
4. Register Orchestrators
  - Discover new/modified orchestrator files
  - Parse metadata (ID, domain, capabilities, AC-IDs)
  - Register in OrchestratorRegistry
  - Wire MCP tools
  - Update intent router
  ↓
5. Generate Commit Message
  - Format: category: description
  - Include: Phase #, AC-IDs, completion %
  - Include: Orchestrator registrations
  - Include: Capabilities added
  ↓
6. Commit Changes
  - git add (staged files)
  - git commit -m (message)
  ↓
7. Push to Remote
  - git push origin CORTEX6
  ↓
8. Sync Working Copy
  - Pull latest from remote
  - Register new remote orchestrators
  - Merge AC-INDEX changes
  - Update local registry
  ↓
9. Verify Clean State
  - git status → should show "nothing to commit"
  - Untracked files → must be zero
  - If not, return to step 2
  ↓
END (Working tree clean, all work registered)
```

---

## 📝 Commit Message Format

**MANDATORY format for commit messages:**

```
{category}: {short description}

{detailed description}

---
PHASE: {phase_number}
AC-IDS: {AC-001, AC-002, ...}
COMPLETION: {percentage}%
ORCHESTRATORS_REGISTERED: {count}
CAPABILITIES_ADDED: {count}
UNTRACKED_FILES_REMOVED: {count} (before cleanup)
```

**Examples:**

```
feat: Implement AC-CRAWLER-001 AST analyzer with multi-language support

- Python, JavaScript/TypeScript, C#, Java, Go, Rust AST parsing
- Semantic code representation with nodes and edges
- Knowledge graph construction for architecture inference
- Parallel crawler execution for performance

---
PHASE: 1.5
AC-IDS: AC-CRAWLER-001
COMPLETION: 50%
ORCHESTRATORS_REGISTERED: 1 (crawler_orchestrator)
CAPABILITIES_ADDED: 6 (ast_parse, code_analysis, graph_build, etc.)
UNTRACKED_FILES_REMOVED: 8
```

```
chore: Clean up untracked files and update .gitignore

- Added .cortex/*.md pattern (analysis artifacts)
- Added cortex-brain/cx6-plan/viewer/*-backup-*.json pattern
- Removed 9 stale backup files via git reset
- Added 2 new patterns to .gitignore

---
PHASE: 10.1
AC-IDS: (maintenance)
COMPLETION: 100%
ORCHESTRATORS_REGISTERED: 0
CAPABILITIES_ADDED: 0
UNTRACKED_FILES_REMOVED: 9
```

---

## 🔧 Implementation Details

### File Patterns (for auto-classification)

**COMMIT patterns** (work output to track):
```
src/orchestrators/*/\*.py           # New orchestrators
src/\*/\*.py                        # New features
tests/\*/\*.py                      # New tests
cortex-brain/tier*/orchestrators/*  # Orchestrator manifests
cortex-brain/tier*/\*.yaml          # Governance rules
cortex-brain/documents/\*.md        # Documentation
.github/prompts/\*.md               # Governance prompts
README.md, ARCHITECTURE.md          # Project docs
```

**IGNORE patterns** (already in .gitignore):
```
__pycache__/
*.pyc, *.pyo
.pytest_cache/
.coverage, htmlcov/
*.db-wal, *.db-shm
.cortex/\*.md
cortex-brain/cx6-plan/viewer/*-backup-\*.json
cortex-brain/audit-logs/\*.jsonl
.vscode/settings.json
.DS_Store
```

**RESET patterns** (temporary files to discard):
```
\*.tmp, \*.bak
build/, dist/
phase-removal/
```

---

## 🚀 Invocation via Python

**From MasterOrchestrator:**

```python
from src.orchestrators.git.git_commit_orchestrator import GitCommitOrchestrator

orchestrator = GitCommitOrchestrator(workspace_root=Path.cwd())

# Execute full workflow
result = orchestrator.run(
    phase_number=10,
    ac_ids=["AC-TEMPLATE-005"],
    completion_percentage=100,
    auto_classify=True,  # Auto-classify files, prompt for ambiguous
    register_orchestrators=True,  # Auto-register new orchestrators
    sync_working_copy=True,  # Pull and merge remote changes
)

# Check result
if result.success:
    print(f"Committed {result.committed_file_count} files")
    print(f"Registered {result.orchestrators_registered} orchestrators")
    print(f"Working tree now clean: {result.untracked_file_count == 0}")
else:
    print(f"Error: {result.error}")
```

---

## 🛡️ Safety Guarantees

**This orchestrator GUARANTEES:**

1. ✅ **Zero Untracked Files** – After completion, `git status` shows clean tree
2. ✅ **No Data Loss** – Files are COMMITTED or IGNORED, never silently deleted
3. ✅ **Orchestrator Discovery** – All completed work is registered
4. ✅ **Audit Trail** – Commit messages document what changed and why
5. ✅ **Conflict-Free** – Working copy always in sync with remote
6. ✅ **Idempotent** – Running twice produces same result (safe to retry)

---

## ⚠️ Error Handling

| Error | Recovery | Severity |
|-------|----------|----------|
| Merge conflict in AC-INDEX | Auto-merge via orchestrator tracking | MEDIUM |
| Unclassifiable file | Prompt user for classification | LOW |
| Orchestrator registration fails | Log error, skip registration, continue | MEDIUM |
| MCP tool wiring fails | Log error, skip MCP, continue | LOW |
| Push to remote fails | Stash changes, suggest manual push | HIGH |

---

## 📊 Audit Logging

**All operations logged to audit trail:**

```
timestamp: 2026-01-13T10:30:00Z
category: GIT
level: INFO
message: Git commit orchestrator execution complete
details:
  files_committed: 4
  files_ignored: 2
  files_reset: 1
  orchestrators_registered: 1
  capabilities_added: 6
  untracked_files_before: 9
  untracked_files_after: 0
  phase: 10.1
  ac_ids: [AC-TEMPLATE-005]
```

---

## 🔗 Integration Points

| Component | Integration | Purpose |
|-----------|-----------|---------|
| MasterOrchestrator | Delegates git operations | Maintains working tree consistency |
| OrchestratorRegistry | Registers discovered orchestrators | Central orchestrator catalog |
| EnterpriseAuditLogger | Logs all operations | Complete audit trail |
| AC-INDEX.yaml | Merge and update | Track completed AC-IDs |
| progress-tracker.json | Read for context | Phase/completion information |
| .gitignore | Update with new patterns | Evolving ignore rules |
| Intent Router | Update with new patterns | Routing table maintenance |

---

**Version History:**
- 1.0.0: Initial git commit orchestrator with intelligent file classification, orchestrator discovery, and working copy sync (2026-01-13)
