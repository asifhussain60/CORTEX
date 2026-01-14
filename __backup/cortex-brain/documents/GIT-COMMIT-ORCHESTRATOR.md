# Git Commit Orchestrator (AC-GIT-001, AC-GIT-002, AC-GIT-003)

## Overview

The Git Commit Orchestrator is an intelligent git operations system that maintains zero untracked files, auto-discovers and registers orchestrators, and keeps working copies synchronized with remote repositories.

## Features

### AC-GIT-001: Automated File Classification
- **COMMIT** → Work output (source code, tests, documentation)
- **IGNORE** → Build artifacts (cache, logs, compiled code)
- **RESET** → Temporary files (backups, build directories)

Auto-classification via pattern matching with optional user prompts for ambiguous files.

### AC-GIT-002: Orchestrator Discovery & Registration
- Scans modified Python files for orchestrator class definitions
- Extracts orchestrator metadata (ID, domain, capabilities, AC-IDs)
- Registers discovered orchestrators in `orchestrator_registry.json`
- Wires MCP tools for discovered capabilities
- Updates intent routing tables

### AC-GIT-003: Working Copy Synchronization
- Pull latest changes from remote
- Auto-merge orchestrator registry updates
- Merge AC-INDEX changes with conflict resolution
- Sync local capabilities with remote completions
- Zero-conflict merging via orchestrator tracking

## Architecture

```
GitCommitOrchestrator
├── classify_untracked_files()     [AC-GIT-001]
│   ├── COMMIT patterns
│   ├── IGNORE patterns
│   └── RESET patterns
│
├── discover_orchestrators()       [AC-GIT-002]
│   ├── Find modified orchestrator files
│   ├── Extract class definitions
│   ├── Parse capabilities & AC-IDs
│   └── Return discoveries
│
├── register_orchestrators()       [AC-GIT-002]
│   ├── Update orchestrator_registry.json
│   ├── Wire MCP tools
│   └── Update intent routes
│
├── generate_commit_message()
│   ├── Include phase & AC-IDs
│   ├── Document orchestrator registrations
│   └── Calculate completion metrics
│
└── run()                          [Full workflow]
    ├── Get untracked files
    ├── Classify
    ├── git add/reset
    ├── Discover & register
    ├── Commit
    ├── Push
    └── Verify clean state
```

## Usage

### Basic Usage

```python
from src.orchestrators.git import GitCommitOrchestrator

orchestrator = GitCommitOrchestrator()

result = orchestrator.run(
    phase_number=10,
    ac_ids=["AC-GIT-001"],
    completion_percentage=50
)

print(f"Committed: {len(result.committed_files)} files")
print(f"Registered: {result.orchestrators_registered} orchestrators")
print(f"Clean tree: {result.untracked_files_after == 0}")
```

### File Classification

```python
# Classify individual file
result = orchestrator.classify_file("src/orchestrators/git/tool.py")
print(result.classification)  # FileClassification.COMMIT

# Classify multiple files
commits, ignores, resets, classifications = orchestrator.classify_untracked_files([
    "src/orchestrators/git/new.py",      # → COMMIT
    ".cortex/analysis.md",               # → IGNORE
    "backup.tmp"                         # → RESET
])
```

### Orchestrator Discovery

```python
# Discover from modified files
discoveries = orchestrator.discover_orchestrators([
    "src/orchestrators/git/git_commit_orchestrator.py"
])

for discovery in discoveries:
    print(f"Found: {discovery.class_name}")
    print(f"  ID: {discovery.orchestrator_id}")
    print(f"  Domain: {discovery.domain}")
    print(f"  Capabilities: {discovery.capabilities}")
    print(f"  AC-IDs: {discovery.ac_ids}")
```

### Registration

```python
# Register discovered orchestrators
orchestrators_count, capabilities = orchestrator.register_orchestrators(discoveries)

print(f"Registered: {orchestrators_count} orchestrators")
print(f"Added capabilities: {capabilities}")
```

## File Patterns

### COMMIT Patterns (Track These)
```
src/orchestrators/*/\*.py           # Orchestrator implementations
src/\*/\*.py                        # Feature code
tests/\*/\*.py                      # Test code
cortex-brain/tier*/orchestrators/*  # Orchestrator manifests
cortex-brain/tier*/\*.yaml          # Governance rules
cortex-brain/documents/\*.md        # Documentation
.github/prompts/\*.md               # Governance prompts
README.md, ARCHITECTURE.md          # Project docs
```

### IGNORE Patterns (Don't Track)
```
.cortex/\*.md                                    # Analysis artifacts
cortex-brain/cx6-plan/viewer/*-backup-\*.json  # Auto backups
cortex-brain/audit-logs/\*.jsonl               # Live audit logs
__pycache__/, \*.pyc                           # Python cache
.pytest_cache/, .coverage                      # Test artifacts
\*.db-wal, \*.db-shm                           # SQLite temp files
```

### RESET Patterns (Discard These)
```
\*.tmp, \*.bak              # Temporary files
build/, dist/               # Build directories
phase-removal/              # Phase cleanup temp
```

## Commit Message Format

```
{category}: {short description}

- {detailed point 1}
- {detailed point 2}

---
PHASE: {number}
AC-IDS: {AC-001, AC-002, ...}
COMPLETION: {percentage}%
ORCHESTRATORS_REGISTERED: {count}
CAPABILITIES_ADDED: {count}
UNTRACKED_FILES_REMOVED: {count}
```

## API Reference

### GitCommitOrchestrator

#### `classify_file(file_path: str) -> FileClassificationResult`
Classify a single file as COMMIT, IGNORE, RESET, or UNKNOWN.

#### `classify_untracked_files(files: List[str]) -> Tuple[List[str], List[str], List[str], List[FileClassificationResult]]`
Classify multiple untracked files.

#### `discover_orchestrators(modified_files: List[str]) -> List[OrchestratorDiscovery]`
Discover orchestrators in modified files.

#### `register_orchestrators(discoveries: List[OrchestratorDiscovery]) -> Tuple[int, List[str]]`
Register discovered orchestrators and return count and capabilities.

#### `generate_commit_message(...) -> str`
Generate comprehensive commit message with phase/AC-IDs/metrics.

#### `run(phase_number, ac_ids, completion_percentage, ...) -> GitCommitResult`
Execute full git commit workflow and return results.

## Safety Guarantees

✅ **Zero Untracked Files** – Working tree clean after completion  
✅ **No Data Loss** – Files COMMITTED or IGNORED, never silently deleted  
✅ **Orchestrator Discovery** – All work is registered and discoverable  
✅ **Audit Trail** – All operations logged with full provenance  
✅ **Conflict-Free** – Working copy stays in sync with remote  
✅ **Idempotent** – Safe to retry without side effects  

## Integration Points

| Component | Integration | Purpose |
|-----------|-----------|---------|
| MasterOrchestrator | Delegates git ops | Working tree consistency |
| OrchestratorRegistry | Registers discoveries | Central orchestrator catalog |
| EnterpriseAuditLogger | Logs all ops | Complete audit trail |
| AC-INDEX.yaml | Merge & update | Track completed AC-IDs |
| progress-tracker.json | Read for context | Phase/completion info |
| .gitignore | Update patterns | Evolving ignore rules |
| Intent Router | Update routes | Routing table maintenance |

## Testing

Comprehensive test suite with 25+ tests covering:
- File classification (COMMIT/IGNORE/RESET patterns)
- Batch file classification
- Orchestrator discovery from files
- Commit message generation
- Git operations (add, reset, commit, push)
- .gitignore updates
- Orchestrator registration
- Full workflow execution

Run tests:
```bash
pytest tests/orchestrators/test_git_commit_orchestrator.py -v
```

## Error Handling

| Error | Recovery | Severity |
|-------|----------|----------|
| Merge conflict in AC-INDEX | Auto-merge via tracking | MEDIUM |
| Unclassifiable file | Prompt user | LOW |
| Registration fails | Log error, skip, continue | MEDIUM |
| MCP wiring fails | Log error, skip, continue | LOW |
| Push fails | Stash, suggest manual push | HIGH |

---

**AC-GIT-001:** Automated file classification with zero untracked files policy  
**AC-GIT-002:** Orchestrator discovery and registration with MCP wiring  
**AC-GIT-003:** Working copy synchronization with conflict-free merging
