# CORTEX Multi-Machine Git Commit Orchestrator# 🔄 CORTEX Git Commit Orchestrator (v1.0)



**Version:** 2.0.0 | **Category:** Multi-Machine Git Operations | **Safety:** Maximum  **Purpose:** Intelligent git operations with zero untracked files, orchestrator registration, and working copy synchronization.  

**Purpose:** Cross-platform git workflow with brain data synchronization for MAC/WIN parallel development  **Design goal:** Automated, intelligent file classification + orchestrator discovery + remote sync.  

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**  **Version:** 1.0.0 | **Date:** 2026-01-13  

**Alignment:** master-plan.yaml v1.9.0 multi-machine development protocol**Integration:** Works with MasterOrchestrator to maintain working tree consistency.



------



## 🎯 Mission## 🎯 Philosophy



Execute CORTEX git workflow across parallel MAC/WIN development tracks with zero data loss and complete brain state synchronization. The orchestrator manages commit, push, pull, and brain data merging to ensure both machines maintain consistent state while allowing independent work streams.**Zero Untracked Files Policy:**

- Every untracked file is intentionally classified

**Core Guarantee:** Work from MAC never overwrites WIN progress, and vice versa. Brain state files merge intelligently using timestamp and machine-ID tracking.- Classification: COMMIT (work output) vs IGNORE (build artifacts) vs RESET (temporary)

- After each operation: `git status` shows clean working tree

---- All work is discoverable and auditable



## 🛡️ Multi-Machine Safety Principles**Orchestrator Registration:**

- Auto-discover completed orchestrators

**P1: Machine Isolation** - Each machine works on assigned phases (MAC: Phases 4, 9, 11; WIN: Phases 2, 3, 5-8, 10). Cross-phase commits are flagged with machine tags for visibility.- Wire in MCP tools for discovered capabilities

- Update orchestrator registry with phase completion

**P2: Brain Data Synchronization** - State files (progress-tracker.json, audit logs, evidence bundles) merge using CRDT-like conflict resolution with machine metadata and timestamps as tie-breakers.- Track implementation provenance



**P3: Feature Branch Protocol** - Each AC-ID gets a feature branch (`feat/AC-{ID}`). Machines merge to CORTEX6 only after cross-platform CI/CD validation passes.**Working Copy Sync:**

- Pull latest orchestrator code from remote

**P4: Atomic Brain Sync** - Brain data exports to git-tracked files before every push. On pull, imports merge remote brain state with local state using union semantics for arrays and timestamp precedence for scalars.- Merge new capabilities into local orchestrator registry

- Update AC-INDEX with new work completed on remote

---- Zero merge conflicts via intelligent merging



## 📋 Multi-Machine Execution Pipeline---



### Stage 0: Machine Context Detection## 📋 Untracked File Classification Protocol



Detects current machine (MAC/WIN), loads machine assignment from master-plan.yaml, validates phase ownership, and warns if committing work outside assigned phases. Creates machine-tagged commit messages (`[MAC]` or `[WIN]` prefix).**When git shows untracked files, classify each:**



**Example:**### Category 1: COMMIT (Work Output)

```These files represent completed work that should be tracked.

[MAC] feat(AC-COHERENCE-001): Implement cross-file symbol validation

[WIN] feat(AC-VALIDATE-001): Add input canonicalization| File Pattern | Action | Reason |

```|--------------|--------|--------|

| `src/**/*.py` (new implementations) | COMMIT | New features/orchestrators |

### Stage 1: Pre-Commit Brain Export| `tests/**/*.py` (new test files) | COMMIT | TDD evidence |

| `cortex-brain/tier*/orchestrators/*.yaml` | COMMIT | Orchestrator manifests |

Exports current brain state to git-tracked files with machine metadata:| `cortex-brain/documents/reports/*.md` | COMMIT | Architecture/implementation docs |

| `README.md`, `ARCHITECTURE.md` | COMMIT | Project documentation |

**Exported Files:**| `.github/prompts/*.md` (new prompts) | COMMIT | New governance/routing prompts |

- `cortex-brain/tier1/tracking/progress-tracker.json` (with `last_updated_machine` field)| `cortex-brain/tier*/governance/*.yaml` (new rules) | COMMIT | Governance rules |

- `cortex-brain/database/audit-sessions/session-{timestamp}.json` (audit trail snapshot)

- `cortex-brain/database/evidence-bundles/*.json` (evidence bundles generated locally)### Category 2: IGNORE (Build/Analysis Artifacts)

- `cortex-brain/tier3/learned-patterns-{machine}.yaml` (machine-specific patterns)These files are auto-generated and should never be tracked.



**Machine Metadata Added:**| File Pattern | Action | Reason |

```json|--------------|--------|--------|

{| `.cortex/*.md` | IGNORE | Chat/analysis documents (already in .gitignore) |

  "last_updated": "2026-01-13T22:30:00Z",| `cortex-brain/cx6-plan/viewer/*-backup-*.json` | IGNORE | Auto backups (already in .gitignore) |

  "last_updated_machine": "MAC",| `cortex-brain/audit-logs/*.jsonl` | IGNORE | Live audit logs |

  "machine_id": "mac-asif-mbp",| `cortex-brain/documents/reports/architecture-audit-*.json` | IGNORE | Auto-generated audit reports |

  "phase_context": 4,| `__pycache__/`, `*.pyc`, `.pytest_cache/` | IGNORE | Python build artifacts |

  "ac_id_context": "AC-COHERENCE-001"| `.coverage`, `htmlcov/` | IGNORE | Test coverage reports |

}| `*.db-wal`, `*.db-shm` | IGNORE | SQLite temp files |

```

### Category 3: RESET (Temporary/Stale)

### Stage 2: Stash Local ChangesThese files were from past operations and should be removed.



Creates machine-tagged stash: `cortex-vacuum-{machine}-{timestamp}-{correlation_id}`| File Pattern | Action | Reason |

|--------------|--------|--------|

Preserves all local changes including untracked files. Stash names include machine identifier for cross-machine debugging.| `*.tmp`, `*.bak` | RESET | Temporary files |

| Old backup files (>7 days old) | RESET | Stale backups |

### Stage 3: Pull and Merge from Remote| `build/`, `dist/` | RESET | Build directories |



Fetches from CORTEX6 and analyzes divergence. If remote has commits from other machine, applies **brain-aware merge strategy**:---



#### Brain-Aware Merge Rules (Priority Order)## 🔍 Intelligent File Detection Algorithm



**Rule 1: Array Union (Append-Only)**```python

- `recent_fixes[]`: Union of both arrays, deduplicate by timestamp# Pseudo-code for file classification

- `enhancements[]`: Union of both arrays, deduplicate by content

- `audit_entries[]`: Union sorted by timestampdef classify_untracked_files(untracked_list):

    """Classify all untracked files intelligently."""

**Rule 2: Timestamp Precedence (Scalars)**    

- `current_phase.number`: Choose entry with newer `last_updated`    commits = []

- `current_phase.status`: Choose entry with newer `last_updated`    ignores = []

- If timestamps within 60s, prefer machine assigned to that phase    resets = []

    

**Rule 3: Phase Ownership Precedence**    for file in untracked_list:

- MAC changes to Phases 4, 9, 11 always win over WIN changes        # Check explicit .gitignore patterns first

- WIN changes to Phases 2, 3, 5-8, 10 always win over MAC changes        if matches_gitignore(file):

- Cross-phase conflicts trigger manual review            ignores.append(file)

            continue

**Rule 4: Evidence Bundle Aggregation**        

- All evidence bundles from both machines are preserved        # Check file path and extension

- Deduplicate by AC-ID + test_hash        if is_implementation_file(file):  # src/**/*.py, tests/**/*.py, etc.

- Merge coverage data (take max coverage %)            commits.append(file)

        elif is_documentation_file(file):  # *.md, *.yaml in docs/tier*/

**Rule 5: Audit Trail Merge**            commits.append(file)

- Union all audit entries by correlation_id        elif is_artifact_file(file):  # __pycache__, .pytest_cache, *.pyc

- Sort by timestamp chronologically            ignores.append(file)

- Preserve complete provenance from both machines        elif is_temporary_file(file):  # *.tmp, *.bak, build/

            resets.append(file)

### Stage 4: Reapply Stash with Brain Validation        elif file.endswith('.md') and is_analysis_doc(file):

            ignores.append(file)  # .cortex/*.md, refinement-*.md

Applies machine-tagged stash and validates brain state consistency:        else:

            # Default: ask user

**Validation Checks:**            user_choice = prompt_user(f"Classify {file}?")

- `progress-tracker.json` parses without errors            if user_choice == "commit":

- No AC-ID double-completion (same AC marked done on both machines)                commits.append(file)

- Phase gates consistent (100% completion triggers verified on both sides)            elif user_choice == "ignore":

- Audit trail continuity preserved (no missing correlation chains)                add_to_gitignore(file)

                ignores.append(file)

If validation fails, generates diagnostic report and preserves stash for manual resolution.            else:

                git_reset_file(file)

### Stage 5: Brain State Consistency Check                resets.append(file)

    

Runs comprehensive brain state validation before commit:    return commits, ignores, resets

```

**Checks:**

1. **AC-INDEX Integrity:** All referenced AC-IDs exist, no orphans---

2. **Progress Tracker Coherence:** Current phase matches completed AC-IDs

3. **Audit Trail Completeness:** All completed AC-IDs have audit entries## 🔗 Orchestrator Registration & Discovery

4. **Evidence Bundle Coverage:** All completed AC-IDs have evidence bundles

5. **Machine Assignment Compliance:** Work aligns with machine-phase mapping**When committing work, also register orchestrators:**



Failures trigger `BRAIN_STATE_INCONSISTENT` error with remediation steps.### Step 1: Discover Completed Orchestrators

```bash

### Stage 6: Quality Gates (CORE-023)# Search for new orchestrator files in src/orchestrators/

find src/orchestrators -name "*.py" -newer <last_commit>

Same as single-machine workflow:# Check for orchestrator class definitions (marked with @OrchestratorRegistry.register)

- Python: syntax, lint (ruff), format (black), type (mypy)```

- YAML: schema validation (yamllint)

- HTML: HTML5 validation, WCAG AA### Step 2: Parse Orchestrator Metadata

- Tests: pytest with 80% coverage threshold```python

- Security: Bandit scan, secrets detection# Extract from orchestrator file:

# - Orchestrator ID (e.g., "crawler", "planner")

### Stage 7: Commit with Machine Tag# - Domain (e.g., "analysis", "planning")

# - Capabilities (list of things it can do)

Generates structured commit message with machine tag:# - AC-IDs it implements

# - Phase completed in

**Format:**```

```

[{MACHINE}] {type}({scope}): {subject}### Step 3: Register in OrchestratorRegistry

```bash

{body}python3 -m src.orchestrators.master.orchestrator_registry \

  register \

Machine: {machine_id}  --id <orchestrator_id> \

Phase: {phase_number}  --class-name <ClassName> \

AC-ID: {ac_id}  --domain <domain> \

Platform: {MAC|WIN}  --capabilities <cap1,cap2,...> \

Cross-Platform: {YES|NO}  --ac-ids <AC-001,AC-002,...>

```

{footer}

```### Step 4: Wire MCP Tools

```python

**Example:**# For each capability, create MCP tool entry:

```# - Tool name: camelCase version of capability

[WIN] feat(AC-VALIDATE-001): Implement intent canonicalization# - Tool description: From orchestrator docstring

# - Tool parameters: Extracted from function signatures

- Add regex-based input normalization# - Tool handler: Points to orchestrator method

- Implement AC-ID format validation```

- Add unicode handling for cross-platform paths

### Step 5: Update Intent Router

Machine: win-asif-desktop```yaml

Phase: 2# Update .github/prompts/AC-mappings.json

AC-ID: AC-VALIDATE-001# Add new orchestrator to routing table:

Platform: WINintent_patterns:

Cross-Platform: YES  - pattern: "crawler"

    route_to: "crawler_orchestrator"

BREAKING CHANGE: None    priority: 35

References: #issue-123    ac_ids: [AC-CRAWLER-001, AC-CRAWLER-002, ...]

``````



### Stage 8: Push to Remote with Conflict Detection---



Pushes to CORTEX6 with machine metadata in commit. If push is rejected:## 🔄 Working Copy Sync Protocol



**Retry Strategy:****When pulling from remote, sync orchestrators and capabilities:**

1. Fetch remote changes

2. Check if remote has commits from OTHER machine### Step 1: Detect Remote Changes

3. If yes, re-run brain merge (Stage 3) to incorporate other machine's work```bash

4. Revalidate brain state (Stage 5)# Check what changed on remote

5. Retry push (max 3 attempts)git fetch origin

git log --oneline origin/CORTEX6..HEAD | grep -E "src/orchestrators|AC-" | head -20

If all retries fail, generate cross-machine conflict report and abort.```



### Stage 9: Post-Push Brain State Verification### Step 2: Extract New Orchestrators from Remote

```bash

After successful push, verifies brain state synchronization:# Find new orchestrator files

git diff --name-only origin/CORTEX6..HEAD | grep "src/orchestrators/"

**Verifications:**

- Remote progress-tracker.json includes work from BOTH machines# For each new file:

- Audit trail has entries from BOTH machine IDs# 1. Extract orchestrator metadata

- Evidence bundles from BOTH machines are present# 2. Register locally

- No machine's work was lost in merge# 3. Wire MCP tools

```

Logs `BRAIN_SYNC_VERIFIED` to audit trail with checksums.

### Step 3: Merge AC-INDEX Changes

### Stage 10: Machine Handoff Preparation```python

# When AC-INDEX.yaml differs between local and remote:

Prepares machine for potential handoff to other machine:# 1. Load both versions

# 2. Identify new AC-IDs on remote

**Actions:**# 3. Merge strategically:

1. Exports current TODO list to `cortex-brain/tier1/tracking/machine-state-{machine}.json`#    - Keep local completed work

2. Documents blockers/decisions in handoff notes#    - Add new remote AC-IDs

3. Tags commit with `handoff-ready` if phase is paused#    - Reconcile conflicts via orchestrator phase tracking

4. Generates machine state summary for other machine to read# 4. Write merged AC-INDEX back

```

**Handoff File Format:**

```json### Step 4: Update Orchestrator Registry

{```bash

  "machine": "MAC",# For each new AC-ID from remote:

  "timestamp": "2026-01-13T22:45:00Z",# 1. Find implementing orchestrator

  "current_phase": 4,# 2. Update local registry with new capability

  "current_ac_id": "AC-COHERENCE-002",# 3. Re-generate MCP tool manifests

  "status": "in_progress",# 4. Update routing tables

  "next_steps": [```

    "Complete AC-COHERENCE-002 implementation",

    "Run cross-platform tests",---

    "Generate evidence bundle"

  ],## 🎬 Git Commit Workflow

  "blockers": [],

  "notes": "Symbol validation working, need to add type inference next"**Complete flow for intelligent git commit:**

}

``````

START

---  ↓

1. Load Current State

## 🔄 Brain Data Synchronization Strategy  - git status → get untracked files

  - Parse progress-tracker.json

### Brain Files and Merge Strategy  - Load orchestrator_registry.json

  ↓

| File | Merge Strategy | Conflict Resolution |2. Classify Untracked Files

|------|----------------|---------------------|  - For each file: COMMIT, IGNORE, or RESET?

| `progress-tracker.json` | Timestamp + Phase Ownership | Newer wins for assigned phase |  - Auto-detect via path patterns

| `AC-INDEX.yaml` | Manual only (SSOT) | Should never conflict |  - Prompt user for ambiguous files

| `audit-sessions/*.json` | Union (append-only) | Chronological order |  ↓

| `evidence-bundles/*.json` | Union by AC-ID | Dedupe by test_hash |3. Process Classifications

| `learned-patterns-{machine}.yaml` | Machine-specific | No merge needed |  - COMMIT files: git add

| `tier1/tracking/machine-state-{machine}.json` | Machine-specific | No merge needed |  - IGNORE files: add to .gitignore

  - RESET files: git checkout (discard)

### Progress Tracker Merge Algorithm  ↓

4. Register Orchestrators

```python  - Discover new/modified orchestrator files

def merge_progress_trackers(local, remote):  - Parse metadata (ID, domain, capabilities, AC-IDs)

    """  - Register in OrchestratorRegistry

    Merge progress trackers from two machines.  - Wire MCP tools

      - Update intent router

    Strategy:  ↓

    1. Union recent_fixes (dedupe by timestamp)5. Generate Commit Message

    2. Union enhancements (dedupe by content)  - Format: category: description

    3. Choose current_phase based on phase ownership + timestamp  - Include: Phase #, AC-IDs, completion %

    4. Merge completed AC-IDs (union)  - Include: Orchestrator registrations

    5. Preserve both machine metadata  - Include: Capabilities added

    """  ↓

    merged = {}6. Commit Changes

      - git add (staged files)

    # Union recent_fixes (sorted by timestamp, dedupe)  - git commit -m (message)

    merged['recent_fixes'] = sorted(  ↓

        list(set(local['recent_fixes'] + remote['recent_fixes'])),7. Push to Remote

        key=lambda x: extract_timestamp(x),  - git push origin CORTEX6

        reverse=True  ↓

    )8. Sync Working Copy

      - Pull latest from remote

    # Union enhancements (dedupe by content)  - Register new remote orchestrators

    merged['enhancements'] = list(set(  - Merge AC-INDEX changes

        local['enhancements'] + remote['enhancements']  - Update local registry

    ))  ↓

    9. Verify Clean State

    # Choose current_phase based on ownership + timestamp  - git status → should show "nothing to commit"

    local_machine = local.get('last_updated_machine', 'UNKNOWN')  - Untracked files → must be zero

    remote_machine = remote.get('last_updated_machine', 'UNKNOWN')  - If not, return to step 2

    local_phase = local['current_phase']['number']  ↓

    remote_phase = remote['current_phase']['number']END (Working tree clean, all work registered)

    ```

    # Check phase ownership

    local_owns = is_phase_owned_by_machine(local_phase, local_machine)---

    remote_owns = is_phase_owned_by_machine(remote_phase, remote_machine)

    ## 📝 Commit Message Format

    if local_owns and not remote_owns:

        merged['current_phase'] = local['current_phase']**MANDATORY format for commit messages:**

    elif remote_owns and not local_owns:

        merged['current_phase'] = remote['current_phase']```

    else:{category}: {short description}

        # Both valid or both invalid - use timestamp

        if local['last_updated'] > remote['last_updated']:{detailed description}

            merged['current_phase'] = local['current_phase']

        else:---

            merged['current_phase'] = remote['current_phase']PHASE: {phase_number}

    AC-IDS: {AC-001, AC-002, ...}

    # Merge completed AC-IDs (union, preserve phase grouping)COMPLETION: {percentage}%

    merged['phases'] = {}ORCHESTRATORS_REGISTERED: {count}

    for phase_key in set(local.get('phases', {}).keys()) | set(remote.get('phases', {}).keys()):CAPABILITIES_ADDED: {count}

        local_acs = set(local.get('phases', {}).get(phase_key, {}).get('completed', []))UNTRACKED_FILES_REMOVED: {count} (before cleanup)

        remote_acs = set(remote.get('phases', {}).get(phase_key, {}).get('completed', []))```

        merged['phases'][phase_key] = {

            'completed': sorted(list(local_acs | remote_acs))**Examples:**

        }

    ```

    # Preserve machine metadata from bothfeat: Implement AC-CRAWLER-001 AST analyzer with multi-language support

    merged['machine_history'] = {

        local_machine: local.get('last_updated'),- Python, JavaScript/TypeScript, C#, Java, Go, Rust AST parsing

        remote_machine: remote.get('last_updated')- Semantic code representation with nodes and edges

    }- Knowledge graph construction for architecture inference

    - Parallel crawler execution for performance

    merged['last_updated'] = max(local['last_updated'], remote['last_updated'])

    merged['last_updated_machine'] = (---

        local_machine if local['last_updated'] > remote['last_updated'] PHASE: 1.5

        else remote_machineAC-IDS: AC-CRAWLER-001

    )COMPLETION: 50%

    ORCHESTRATORS_REGISTERED: 1 (crawler_orchestrator)

    return mergedCAPABILITIES_ADDED: 6 (ast_parse, code_analysis, graph_build, etc.)

```UNTRACKED_FILES_REMOVED: 8

```

### Audit Trail Merge Algorithm

```

```pythonchore: Clean up untracked files and update .gitignore

def merge_audit_trails(local_sessions, remote_sessions):

    """- Added .cortex/*.md pattern (analysis artifacts)

    Merge audit sessions from two machines.- Added cortex-brain/cx6-plan/viewer/*-backup-*.json pattern

    - Removed 9 stale backup files via git reset

    Strategy:- Added 2 new patterns to .gitignore

    1. Union all session files by session ID

    2. Sort entries chronologically---

    3. Preserve correlation chains from both machinesPHASE: 10.1

    """AC-IDS: (maintenance)

    all_sessions = {}COMPLETION: 100%

    ORCHESTRATORS_REGISTERED: 0

    # Load all local sessionsCAPABILITIES_ADDED: 0

    for session_file in local_sessions:UNTRACKED_FILES_REMOVED: 9

        session_id = extract_session_id(session_file)```

        all_sessions[session_id] = load_session(session_file)

    ---

    # Merge remote sessions

    for session_file in remote_sessions:## 🔧 Implementation Details

        session_id = extract_session_id(session_file)

        if session_id in all_sessions:### File Patterns (for auto-classification)

            # Merge entries from same session

            all_sessions[session_id]['entries'] = sorted(**COMMIT patterns** (work output to track):

                all_sessions[session_id]['entries'] + load_session(session_file)['entries'],```

                key=lambda x: x['timestamp']src/orchestrators/*/\*.py           # New orchestrators

            )src/\*/\*.py                        # New features

        else:tests/\*/\*.py                      # New tests

            all_sessions[session_id] = load_session(session_file)cortex-brain/tier*/orchestrators/*  # Orchestrator manifests

    cortex-brain/tier*/\*.yaml          # Governance rules

    return all_sessionscortex-brain/documents/\*.md        # Documentation

```.github/prompts/\*.md               # Governance prompts

README.md, ARCHITECTURE.md          # Project docs

### Evidence Bundle Deduplication```



```python**IGNORE patterns** (already in .gitignore):

def merge_evidence_bundles(local_bundles, remote_bundles):```

    """__pycache__/

    Merge evidence bundles from two machines.*.pyc, *.pyo

    .pytest_cache/

    Strategy:.coverage, htmlcov/

    1. Group by AC-ID*.db-wal, *.db-shm

    2. Deduplicate by test_hash (same tests from both machines).cortex/\*.md

    3. Take max coverage percentagecortex-brain/cx6-plan/viewer/*-backup-\*.json

    4. Preserve platform-specific test resultscortex-brain/audit-logs/\*.jsonl

    """.vscode/settings.json

    merged_bundles = {}.DS_Store

    ```

    for ac_id in set(local_bundles.keys()) | set(remote_bundles.keys()):

        local = local_bundles.get(ac_id, {})**RESET patterns** (temporary files to discard):

        remote = remote_bundles.get(ac_id, {})```

        \*.tmp, \*.bak

        if not local:build/, dist/

            merged_bundles[ac_id] = remotephase-removal/

        elif not remote:```

            merged_bundles[ac_id] = local

        else:---

            # Both machines have evidence for this AC-ID

            merged_bundles[ac_id] = {## 🚀 Invocation via Python

                'ac_id': ac_id,

                'test_coverage': max(**From MasterOrchestrator:**

                    local.get('test_coverage', 0),

                    remote.get('test_coverage', 0)```python

                ),from src.orchestrators.git.git_commit_orchestrator import GitCommitOrchestrator

                'tests_passing': local.get('tests_passing', 0) + remote.get('tests_passing', 0),

                'platforms_validated': list(set(orchestrator = GitCommitOrchestrator(workspace_root=Path.cwd())

                    local.get('platforms_validated', []) +

                    remote.get('platforms_validated', [])# Execute full workflow

                )),result = orchestrator.run(

                'machine_results': {    phase_number=10,

                    'MAC': local if local.get('machine') == 'MAC' else remote,    ac_ids=["AC-TEMPLATE-005"],

                    'WIN': local if local.get('machine') == 'WIN' else remote    completion_percentage=100,

                }    auto_classify=True,  # Auto-classify files, prompt for ambiguous

            }    register_orchestrators=True,  # Auto-register new orchestrators

        sync_working_copy=True,  # Pull and merge remote changes

    return merged_bundles)

```

# Check result

---if result.success:

    print(f"Committed {result.committed_file_count} files")

## 🔄 Machine Handoff Protocol    print(f"Registered {result.orchestrators_registered} orchestrators")

    print(f"Working tree now clean: {result.untracked_file_count == 0}")

### Pre-Handoff (Exiting Machine)else:

    print(f"Error: {result.error}")

Before stopping work on Machine A:```



1. **Commit all work** via this orchestrator---

2. **Push to CORTEX6** and verify synchronization

3. **Export machine state** to `machine-state-{machine}.json`## 🛡️ Safety Guarantees

4. **Document blockers** in handoff notes

5. **Tag commit** with `handoff-ready` if pausing mid-phase**This orchestrator GUARANTEES:**

6. **Run smoke tests** to confirm operational readiness

7. **Push again** to ensure handoff state is on remote1. ✅ **Zero Untracked Files** – After completion, `git status` shows clean tree

2. ✅ **No Data Loss** – Files are COMMITTED or IGNORED, never silently deleted

### Post-Handoff (Entering Machine)3. ✅ **Orchestrator Discovery** – All completed work is registered

4. ✅ **Audit Trail** – Commit messages document what changed and why

After pulling on Machine B:5. ✅ **Conflict-Free** – Working copy always in sync with remote

6. ✅ **Idempotent** – Running twice produces same result (safe to retry)

1. **Pull from CORTEX6** with `--rebase=false` (preserve merge commits)

2. **Import brain state** from git-tracked files---

3. **Run brain validation** checks

4. **Load machine state** from `machine-state-{other-machine}.json`## ⚠️ Error Handling

5. **Review handoff notes** for blockers/decisions

6. **Verify audit trail** continuity (correlation IDs present)| Error | Recovery | Severity |

7. **Run smoke tests** to confirm environment alignment|-------|----------|----------|

8. **Resume work** from documented next steps| Merge conflict in AC-INDEX | Auto-merge via orchestrator tracking | MEDIUM |

| Unclassifiable file | Prompt user for classification | LOW |

### Handoff Validation Checklist| Orchestrator registration fails | Log error, skip registration, continue | MEDIUM |

| MCP tool wiring fails | Log error, skip MCP, continue | LOW |

**On Machine A (before handoff):**| Push to remote fails | Stash changes, suggest manual push | HIGH |

- [ ] All work committed with machine tag

- [ ] Brain state exported to git-tracked files---

- [ ] Machine state file created with next steps

- [ ] Blockers documented in handoff notes## 📊 Audit Logging

- [ ] Smoke tests passing

- [ ] Push successful and verified**All operations logged to audit trail:**

- [ ] Handoff commit tagged appropriately

```

**On Machine B (after handoff):**timestamp: 2026-01-13T10:30:00Z

- [ ] Pull successful from CORTEX6category: GIT

- [ ] Brain state imported and validatedlevel: INFO

- [ ] Machine state file loadedmessage: Git commit orchestrator execution complete

- [ ] Handoff notes revieweddetails:

- [ ] Audit trail continuity verified  files_committed: 4

- [ ] Environment aligned (Python, packages, config)  files_ignored: 2

- [ ] Smoke tests passing  files_reset: 1

- [ ] Ready to resume from next steps  orchestrators_registered: 1

  capabilities_added: 6

---  untracked_files_before: 9

  untracked_files_after: 0

## 🚨 Cross-Machine Conflict Scenarios  phase: 10.1

  ac_ids: [AC-TEMPLATE-005]

### Scenario 1: Both Machines Complete Same AC-ID```



**Detection:** Brain merge finds same AC-ID in completed list from both machines with different timestamps.---



**Resolution:**## 🔗 Integration Points

1. Compare evidence bundles (test results, coverage)

2. Choose version with higher test coverage| Component | Integration | Purpose |

3. Preserve both evidence bundles for audit|-----------|-----------|---------|

4. Log `AC_ID_DOUBLE_COMPLETION` warning| MasterOrchestrator | Delegates git operations | Maintains working tree consistency |

5. Keep chosen version in progress-tracker.json| OrchestratorRegistry | Registers discovered orchestrators | Central orchestrator catalog |

| EnterpriseAuditLogger | Logs all operations | Complete audit trail |

**Prevention:** Assign AC-IDs to specific machines via phase ownership.| AC-INDEX.yaml | Merge and update | Track completed AC-IDs |

| progress-tracker.json | Read for context | Phase/completion information |

### Scenario 2: Phase Boundary Crossed by Both Machines| .gitignore | Update with new patterns | Evolving ignore rules |

| Intent Router | Update with new patterns | Routing table maintenance |

**Detection:** Both machines mark phase complete (100%) independently.

---

**Resolution:**

1. Verify both machines have 100% completion for their assigned AC-IDs**Version History:**

2. Merge completion states (union of completed AC-IDs)- 1.0.0: Initial git commit orchestrator with intelligent file classification, orchestrator discovery, and working copy sync (2026-01-13)

3. If true 100% (all AC-IDs from both machines done), mark phase complete
4. Log `PHASE_GATE_CROSS_MACHINE_SYNC` to audit trail

**Prevention:** Phase gates run on CI/CD with both machines' work merged.

### Scenario 3: Conflicting Current Phase

**Detection:** Machine A says current phase is 4, Machine B says current phase is 2.

**Resolution:**
1. Check phase ownership (Phase 4 = MAC, Phase 2 = WIN)
2. Both are valid if machines are working in parallel
3. Store both in `active_phases: [2, 4]` array
4. Each machine filters to its assigned phase on load

**Prevention:** Multi-phase tracking in progress-tracker.json.

### Scenario 4: Governance Rule Violation from Remote Machine

**Detection:** Pull brings in code that violates CORE-005 (hardcoded `/Users/` path from MAC).

**Resolution:**
1. Pre-commit hook on Machine B detects violation
2. Generates `GOVERNANCE_VIOLATION_REMOTE` report
3. Alerts user to remote machine's non-compliant commit
4. Requires manual fix or revert before proceeding

**Prevention:** CI/CD runs governance checks on all commits before merge to CORTEX6.

---

## 📊 Multi-Machine Audit Log Structure

```yaml
schema_version: "2.0"
correlation_id: "a7f3b21c-8f34-4a91-b6e5-3d2c1e9f4b8a"
machine_id: "mac-asif-mbp"
machine_type: "MAC"
timestamp_start: "2026-01-13T22:30:00Z"
timestamp_end: "2026-01-13T22:32:15Z"
duration_seconds: 135

stages:
  - stage: 0_machine_context_detection
    status: SUCCESS
    machine_detected: "MAC"
    assigned_phases: [4, 9, 11]
    current_phase: 4
    phase_ownership_valid: true
    
  - stage: 1_brain_export
    status: SUCCESS
    files_exported:
      - cortex-brain/tier1/tracking/progress-tracker.json
      - cortex-brain/database/audit-sessions/session-2026-01-13T2230.json
      - cortex-brain/database/evidence-bundles/AC-COHERENCE-001.json
    machine_metadata_added: true
    
  - stage: 3_pull_and_merge
    status: SUCCESS
    remote_commits_detected: 3
    remote_machine: "WIN"
    brain_merge_triggered: true
    merge_rules_applied:
      - array_union_recent_fixes
      - timestamp_precedence_current_phase
      - evidence_bundle_aggregation
    conflicts_resolved: 0
    
  - stage: 5_brain_state_validation
    status: SUCCESS
    checks_passed:
      - ac_index_integrity
      - progress_tracker_coherence
      - audit_trail_completeness
      - evidence_bundle_coverage
      - machine_assignment_compliance
    
  - stage: 7_commit_with_machine_tag
    status: SUCCESS
    commit_hash: "a1b2c3d4e5f6"
    machine_tag: "[MAC]"
    commit_message: "feat(AC-COHERENCE-001): Implement cross-file symbol validation"
    
  - stage: 8_push_to_remote
    status: SUCCESS
    push_attempts: 1
    remote_head_before: "x1y2z3w4v5u6"
    remote_head_after: "a1b2c3d4e5f6"
    
  - stage: 9_brain_sync_verification
    status: SUCCESS
    machines_present: ["MAC", "WIN"]
    ac_ids_from_mac: ["AC-COHERENCE-001"]
    ac_ids_from_win: ["AC-VALIDATE-001", "AC-VALIDATE-002"]
    no_data_loss: true
    checksum_match: true

guarantees_upheld:
  - no_data_loss_either_machine
  - brain_state_consistent
  - audit_trail_complete_both_machines
  - phase_ownership_respected
```

---

## 🎯 Success Criteria

At workflow completion, these guarantees must hold:

**Repository State:**
- Working tree clean on current machine
- Fully synchronized with remote CORTEX6
- All changes committed with machine tag
- No unstaged or untracked files

**Brain State:**
- progress-tracker.json includes work from BOTH machines
- Audit trail has entries from BOTH machine IDs
- Evidence bundles from BOTH machines present
- Machine state files updated for handoff

**Cross-Machine Integrity:**
- No AC-ID double-completion conflicts
- Phase ownership respected in all commits
- Machine tags present in all commits
- Handoff readiness documented

**Quality Guarantees:**
- All tests pass (80% coverage threshold)
- No lint errors (ruff), no security issues (Bandit)
- Cross-platform paths (CORE-005 compliant)
- Governance rules enforced (CORE-017)

---

## 🔧 Integration with CORTEX

### Invocation Pattern

**Via intent routing (preferred):**
```bash
python3 -m src.main "git commit and sync" --format markdown
```

**Direct orchestrator call:**
```bash
python3 -m src.orchestrators.git.multi_machine_commit --machine-id mac-asif-mbp
```

### Routing Configuration

Pattern matching assigns priority 50 with autonomous mode. Associated AC-IDs:
- AC-GIT-MULTI-001: Machine context detection
- AC-GIT-MULTI-002: Brain data export/import
- AC-GIT-MULTI-003: Cross-machine merge strategy
- AC-GIT-MULTI-004: Machine handoff protocol
- AC-GIT-MULTI-005: Brain state validation

### Governance Integration

Enforces CORTEX SKULL rules:
- **CORE-001**: Incremental execution (10 stages)
- **CORE-005**: Portable paths (cross-platform validation)
- **CORE-008**: TDD enforcement (test gates)
- **CORE-017**: Governance enforcement (quality gates)
- **CORE-023**: File validation (HTML, YAML, Python)

---

## 📈 Metrics & Observability

Key performance indicators for multi-machine workflow:

- **Cross-Machine Merge Rate**: Target <5% per push
- **Brain Sync Accuracy**: Target 100% (zero data loss)
- **Handoff Success Rate**: Target >95% first-time alignment
- **Machine Conflict Resolution**: Target <3% manual intervention
- **Execution Time**: Target <3 minutes for complete workflow

---

## 🔐 Security Considerations

**Secret Protection:**
- Never commits API keys, passwords, tokens
- Pre-commit hooks scan with detect-secrets
- Audit logs mask credentials
- Machine-specific secrets isolated

**Machine Authentication:**
- Commits signed with machine-specific GPG key
- Machine ID verified against allowed list
- Phase ownership enforced by machine identity

---

## 📚 References

- **Master Plan:** `cortex-brain/cx6-plan/master-plan.yaml` (v1.9.0)
- **Multi-Machine Protocol:** `master-plan.yaml → multi_machine_development_protocol`
- **SSOT Architecture:** `master-plan.yaml → ssot_declaration`
- **Governance Rules:** `cortex-brain/tier0/governance/core-rules.yaml`

---

**END OF PROMPT – Version 2.0.0**  
**Multi-Machine Development: MAC/WIN Parallel Tracks with Brain Synchronization**
