# CORTEX Git Commit Orchestrator

**Version:** 1.1.0 | **Category:** Autonomous Git Operations | **Safety:** Maximum  
**Purpose:** Deterministic, audit-driven Git workflow with zero tolerance for data loss  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Mission

Execute CORTEX "vacuum" workflow with mathematical determinism and complete auditability. The orchestrator manages the complete lifecycle from stashing local changes through synchronization, validation, commit, push, and workspace cleanup. Every decision is logged with correlation tracking for full auditability.

The workflow guarantees the repository ends in a clean, synchronized, auditable state with zero ambiguity.

---

## 🛡️ Safety-First Principles

The orchestrator operates under four core safety principles:

**P1: No Data Loss Ever** - All local changes are preserved in named, timestamped stashes. Merge conflicts are resolved via explicit rules with documented evidence. Destructive operations require explicit justification.

**P2: Explainable Decisions** - Every file classification and merge resolution includes documented reasoning with evidence from tests, security scans, architectural consistency checks, and documentation quality.

**P3: Idempotent Execution** - Running the workflow multiple times produces identical results. Intermediate failures leave breadcrumbs for recovery. All operations validate preconditions before execution.

**P4: Zero Ambiguity** - Untracked files are handled deterministically through classification rules. Conflicts are resolved by evidence-based rules, not heuristics. Success criteria are defined upfront.

---

## 📋 Execution Pipeline

The orchestrator executes nine stages in sequence, with each stage validating preconditions before proceeding. Stages can be skipped if their preconditions indicate no action is needed.

### Stage 0: Precondition Check

Verifies the repository is in a valid state for operations. Confirms git initialization, remote configuration (origin), current branch identification, and absence of active rebase or merge operations. Failure at this stage aborts the entire workflow with a diagnostic message.

### Stage 1: Stash Local Changes

Creates a named stash with format "cortex-vacuum-{timestamp}-{correlation_id}" to preserve all local changes including untracked files. Captures pre-stash state (HEAD hash, working tree status, staged changes) and logs to audit trail. If working tree is already clean, this stage is skipped.

### Stage 2: Sync from Remote

Fetches from remote and analyzes divergence between local and remote branches. Executes merge using --no-ff strategy to preserve history. If merge conflicts occur, applies value-based resolution rules in priority order: test coverage, security posture, architectural consistency, documentation quality, and recency as tie-breaker. Unresolvable conflicts generate diagnostic reports and abort the workflow.

### Stage 2.1: Value-Based Conflict Resolution

Applies five evidence-based rules in strict priority order to resolve merge conflicts:

- **Rule 1: Test Coverage Wins** - Choose version with passing tests and higher coverage percentage
- **Rule 2: Security Posture Wins** - Choose version without security warnings from Bandit scans
- **Rule 3: Architectural Consistency Wins** - Choose version following CORTEX patterns (proper imports, DI, tier structure)
- **Rule 4: Documentation Wins** - Choose version with docstrings and type hints
- **Rule 5: Recency Wins** - Choose newer commit as tie-breaker

Each resolution logs the applied rule, chosen version, and supporting evidence.

### Stage 3: Reapply Stash

Retrieves the most recent cortex-vacuum stash and analyzes its contents. Performs semantic conflict checking against remote changes and applies value-based rules if conflicts exist. Successfully applied stashes are dropped; failed stash applications preserve the stash and log failure details.

### Stage 4: Validate Working Tree

Enforces CORE-023 quality gates on changed files:

- **Python files**: Syntax check, lint with ruff, format with black, type check with mypy
- **YAML files**: Schema validation with yamllint, parse verification
- **HTML files**: HTML5 validation, WCAG AA accessibility, link checking
- **Tests**: Run unit tests with pytest, enforce 80% coverage threshold
- **Security**: Bandit scan, secrets detection

Any gate failure generates a detailed report and aborts the workflow.

### Stage 5: Commit with Structured Message

Analyzes changed files to generate a structured commit message following conventional commit format: {type}({scope}): {subject} with detailed body and footer containing AC-IDs, breaking changes, and references. Commit types include feat, fix, docs, refactor, test, chore, perf, and ci. Stages all changes and creates the commit.

### Stage 6: Push to Remote

Verifies local is ahead of remote before pushing. Executes push with verbose output and verifies synchronization by confirming local HEAD matches remote HEAD. If push is rejected due to divergence, fetches, merges, and retries up to three times.

### Stage 7: Clean Workspace

Deterministically classifies all untracked files using four categories:

- **Required (Auto-Add)**: Python source, config files, docs, tests
- **Ignorable (Auto-Ignore)**: Cache files, IDE artifacts, OS files, build outputs
- **Disposable (Auto-Delete)**: Test artifacts, generated files, empty directories
- **Ambiguous (Error)**: Files not matching any rule trigger abort

Updates .gitignore with timestamped comments for ignored files.

### Stage 8: Final Validation

Executes comprehensive repository health check:

- Confirms clean working tree (git status --porcelain empty)
- Verifies no pending cortex-vacuum stashes
- Validates local and remote HEAD are synchronized
- Runs smoke tests to verify basic functionality
- Confirms complete audit trail with correlation ID

Any check failure generates diagnostic alert but does not abort (workflow already complete).

---

## 🔄 Machine Alignment Protocol

When pulling changes on a different machine to continue plan implementation, follow this alignment sequence to ensure consistent state:

### Pre-Pull Alignment Check

Before pulling changes, verify local machine state:

- Confirm Python environment matches project requirements (check .venv activation, package versions)
- Verify all CORTEX dependencies installed (requirements.txt synchronized)
- Check branch alignment (current branch matches target branch on remote)
- Validate no uncommitted local work conflicts with incoming changes

### Pull and Synchronization

Execute fetch and pull operations with merge strategy (not rebase) to preserve complete history. If divergence exists between local and remote, the value-based conflict resolution rules automatically apply. Local changes should be stashed before pull if working tree is dirty.

### Post-Pull Validation

After successful pull, validate the machine is ready for plan continuation:

- **Environment Check**: Verify Python interpreter, virtual environment, and package versions match requirements
- **Brain State Sync**: Confirm cortex-brain/ tier files (governance, tracking, AC registry) are current
- **Dependency Verification**: Run pip check to ensure no broken dependencies
- **Configuration Alignment**: Verify .github/prompts/ and cortex-brain/config/ are synchronized
- **Test Baseline**: Run smoke tests to confirm basic functionality before resuming work

### State File Verification

Critical state files must be verified for consistency:

- **progress-tracker.json**: Check active_epic, current_phase, current_todo match expectations
- **AC-INDEX.yaml**: Verify AC-ID registry is complete and no orphaned references exist
- **core-rules.yaml**: Confirm all 23 SKULL rules present and enforcement hooks active

If any state file is corrupted or stale, regenerate from git history or abort until resolved.

### Plan Continuation Readiness

Confirm readiness to resume plan implementation:

- Review TODO list in progress-tracker.json to understand current position in workflow
- Verify previous stage outputs exist (generated files, test results, artifacts)
- Check audit trail for correlation IDs linking to previous work
- Validate no blockers or failures recorded in tracking state

Only proceed with plan implementation after all alignment checks pass. Misaligned state will cause cascading failures and corrupt the audit trail.

### Automated Handoff Commands

Execute these commands on the pulling machine to ensure complete operational alignment:

```bash
# 1. Pull latest changes
git fetch origin
git pull origin CORTEX6

# 2. Verify Python environment
python --version  # Should match requirements
pip list --format=freeze | diff - requirements.txt  # Check package drift

# 3. Load working state
cat cortex-brain/tier1/tracking/progress-tracker.json | python -c "import sys, json; data=json.load(sys.stdin); print(f\"Epic: {data['active_epic']['id']}\"); print(f\"Phase: {data['current_phase']['number']} - {data['current_phase']['name']}\"); print(f\"Status: {data['current_phase']['status']}\")"

# 4. Verify governance rules
python -c "import yaml; rules=yaml.safe_load(open('cortex-brain/tier0/governance/core-rules.yaml')); print(f\"SKULL Rules: {len(rules.get('rules', []))}\")"

# 5. Check AC registry
python -c "import yaml; index=yaml.safe_load(open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')); print(f\"Total AC-IDs: {len(index.get('acceptance_criteria', []))}\")"

# 6. Validate test baseline
pytest tests/smoke/ -v --tb=short

# 7. Query audit trail for last activity
python -m src.main "audit query --last 1h --format markdown"
```

### CORTEX Alignment Verification Prompt

After pulling, ask CORTEX to verify alignment with this prompt:

```
CORTEX: Verify operational alignment after git pull. Check:
1. Load progress-tracker.json and report: active epic, current phase, current todo, blockers
2. Verify AC-INDEX.yaml integrity (count AC-IDs, check for orphans)
3. Confirm core-rules.yaml has all 23 SKULL rules
4. Check audit trail for last 5 operations (correlation IDs, timestamps, statuses)
5. Validate environment (Python version, installed packages, virtual environment)
6. Report any misalignment or corruption requiring remediation

If all checks pass, report: "✅ Operational alignment verified. Ready to resume plan implementation."
If any check fails, report: "🚨 Alignment failure detected: [DETAILS]. Remediation required before proceeding."
```

### Cross-Machine Handoff Checklist

Before pushing from Machine A (exiting work session):

- [ ] Commit all work with structured message (via this orchestrator)
- [ ] Push to remote and verify synchronization
- [ ] Update progress-tracker.json with current status and next steps
- [ ] Document any blockers or pending decisions in tracking state
- [ ] Generate evidence bundle if AC-ID completed
- [ ] Verify audit trail is complete with correlation IDs
- [ ] Push final state to remote

After pulling on Machine B (starting work session):

- [ ] Execute automated handoff commands (see above)
- [ ] Run CORTEX alignment verification prompt
- [ ] Review progress-tracker.json TODO list
- [ ] Check for any blockers or alerts from previous session
- [ ] Verify last correlation ID in audit trail matches expected state
- [ ] Run smoke tests to confirm operational readiness
- [ ] Resume plan implementation from current_todo

### Handoff Quality Gates

The handoff is considered successful only when all gates pass:

- **Gate 1: Repository Sync** - Local HEAD matches remote HEAD, no divergence
- **Gate 2: State Integrity** - All tracking files parse without errors, no orphaned references
- **Gate 3: Environment Parity** - Python version and packages match across machines
- **Gate 4: Governance Active** - All 23 SKULL rules loaded, enforcement hooks operational
- **Gate 5: Audit Continuity** - Last operation on Machine A logged, first operation on Machine B creates new correlation chain
- **Gate 6: Test Baseline** - Smoke tests pass, confirming basic functionality intact

Failure of any gate requires remediation before proceeding. Proceeding with failed gates risks corrupting the plan state and audit trail.

---

## 🚨 Failure Modes & Recovery
```yaml
Operation: Quality Gate Enforcement

Gates (Enforce CORE-023):
  1. Python Files:
     - Syntax: python -m py_compile {file}
     - Lint: ruff check {file}
     - Format: black --check {file}
     - Type: mypy {file} (if configured)
  
  2. YAML Files:
     - Schema: yamllint {file}
     - Parse: python -c "import yaml; yaml.safe_load(open('{file}'))"
  
  3. HTML Files:
     - HTML5: nu-validator {file} (W3C)
     - Accessibility: axe-core (WCAG AA)
     - Links: Check internal references
  
  4. Tests:
     - Unit: pytest tests/unit/ -v
     - Coverage: pytest --cov=src --cov-report=term
     - Threshold: 80% minimum (configurable)
  
  5. Security:
     - Bandit: bandit -r src/
     - Secrets: detect-secrets scan

Steps:
  1. Identify changed files:
     Command: git diff --name-only HEAD
  
  2. Run applicable gates:
     For each file type, run corresponding validators
  
  3. Collect results:
     Structure: {file, gate, status, message}
  
  4. Enforce thresholds:
     If any gate fails → ABORT with diagnostic
  
  5. Log to audit:
     Event: VALIDATION_PASSED
     Data: {files_validated, gates_passed, coverage_percentage}

Success Criteria:
  - All gates pass
  - Test coverage ≥ threshold
  - No security issues
  - Audit entry written

Failure Mode: Gate failure → detailed report, ABORT
```

### Stage 5: Commit with Structured Message
```yaml
Operation: Intent-Capturing Commit

Message Format:
  {type}({scope}): {subject}
  
  {body}
  
  {footer}

Components:
  - type: feat|fix|docs|refactor|test|chore|perf|ci
  - scope: Component affected (e.g., orchestrators, audit, governance)
  - subject: Imperative, <50 chars, no period
  - body: Detailed explanation, wrap at 72 chars
  - footer: AC-IDs, breaking changes, references

Example:
  feat(git): Add autonomous vacuum workflow orchestrator
  
  Implements deterministic Git operations with:
  - Named stash with metadata
  - Value-based merge conflict resolution
  - Quality gate enforcement
  - Audit trail for all decisions
  
  AC-GIT-001, AC-GIT-002, AC-AUDIT-008
  Refs: CORTEX-6.0 Phase 1

Steps:
  1. Analyze changes:
     Command: git diff --stat HEAD
     Extract: Files changed, insertions, deletions
  
  2. Identify affected components:
     Map files → CORTEX components (orchestrators, brain, tools, etc.)
  
  3. Determine commit type:
     New functionality → feat
     Bug fix → fix
     Documentation → docs
     Code restructuring → refactor
  
  4. Extract AC-IDs:
     Search changed files for AC-ID references in docstrings/comments
  
  5. Generate message:
     Use template above with extracted data
  
  6. Stage all changes:
     Command: git add -A
  
  7. Commit:
     Command: git commit -m "{message}"
  
  8. Log to audit:
     Event: COMMIT_CREATED
     Data: {commit_hash, message, files_changed, ac_ids}

Success Criteria:
  - Commit hash generated
  - Message follows format
  - All changes staged
  - Audit entry written

Failure Mode: Commit fails → rollback staging, ABORT
```

### Stage 6: Push to Remote
```yaml
Operation: Verified Push

Steps:
  1. Pre-push check:
     Verify: Local ahead of remote
     Command: git rev-list origin/{branch}..HEAD
  
  2. Push:
     Command: git push origin {branch}
     Flags: --verbose (for detailed output)
  
  3. Verify sync:
     Command: git fetch origin
     Check: git rev-parse HEAD == git rev-parse origin/{branch}
  
  4. Handle failures:
     If push rejected (non-fast-forward):
       - Fetch: git fetch origin
       - Merge: Return to Stage 2
       - Retry: Push again
  
  5. Log to audit:
     Event: PUSH_COMPLETED
     Data: {local_hash, remote_hash, commits_pushed}

Success Criteria:
  - Push succeeds
  - Local == remote
  - Audit entry written

Failure Mode: Push fails after retry → diagnostic report, ABORT
```

### Stage 7: Clean Workspace
```yaml
Operation: Deterministic Untracked File Handling

Classification Rules:
  1. Required (Auto-Add):
     - Python source: src/**/*.py, tests/**/*.py
     - Config: cortex-brain/**/*.yaml, cortex-brain/**/*.json
     - Docs: docs/**/*.md (with validation)
     - Tests: tests/**/*.py
     
     Action: git add {file}
     Log: FILE_ADDED_REQUIRED
  
  2. Ignorable (Auto-Ignore):
     - Cache: __pycache__/, *.pyc, .pytest_cache/
     - IDE: .vscode/, .idea/, *.swp
     - OS: .DS_Store, Thumbs.db
     - Build: dist/, build/, *.egg-info/
     - Temp: *.tmp, *.log (in temp dirs)
     
     Action: Append to .gitignore with comment
     Format: "# {reason} - {timestamp}"
     Log: FILE_IGNORED_AUTO
  
  3. Disposable (Auto-Delete):
     - Test artifacts: .coverage, htmlcov/, test-output/
     - Generated: *.auto.*, *.generated.*
     - Empty directories
     
     Action: rm -rf {file}
     Log: FILE_DELETED_DISPOSABLE
  
  4. Ambiguous (Error):
     - Files matching none of above
     
     Action: ABORT with list, require manual classification

Steps:
  1. Enumerate untracked:
     Command: git ls-files --others --exclude-standard
  
  2. Classify each file:
     Apply rules 1-4 in order
  
  3. Execute actions:
     For required: Stage
     For ignorable: Update .gitignore
     For disposable: Delete
     For ambiguous: ABORT
  
  4. Verify clean:
     Command: git status --porcelain
     Expect: Empty output (if no ambiguous files)
  
  5. Log to audit:
     Event: WORKSPACE_CLEANED
     Data: {files_added, files_ignored, files_deleted, ambiguous_count}

Success Criteria:
  - No untracked files remain (or all classified)
  - .gitignore updated with comments
  - Audit entry written

Failure Mode: Ambiguous files exist → list with diagnostic, ABORT
```

### Stage 8: Final Validation
```yaml
Operation: Repository Health Check

Checks:
  1. Git Status:
     Command: git status --porcelain
     Expect: Empty (clean working tree)
  
  2. Stash Status:
     Command: git stash list | grep "cortex-vacuum"
     Expect: Empty (all stashes applied/dropped)
  
  3. Remote Sync:
     Local: git rev-parse HEAD
     Remote: git rev-parse origin/{branch}
     Expect: Equal (fully synchronized)
  
  4. Quality Gates:
     Rerun: pytest tests/smoke/ (smoke tests only)
     Expect: All pass
  
  5. Audit Trail:
     Verify: All 8 stages logged with correlation ID
     Expect: Complete audit chain

Steps:
  1. Run all checks
  2. Collect results
  3. Generate health report
  4. Log to audit:
     Event: HEALTH_CHECK_PASSED
     Data: {checks_passed, correlation_id, duration}

Success Criteria:
  - All checks pass
  - Audit chain complete
  - Report generated

Failure Mode: Any check fails → detailed diagnostic, ALERT (not ABORT)
```

---

## 📊 Audit Log Structure

```yaml
schema_version: "1.0"
correlation_id: "a7f3b21c-8f34-4a91-b6e5-3d2c1e9f4b8a"
timestamp_start: "2026-01-10T15:30:45Z"
timestamp_end: "2026-01-10T15:32:12Z"
duration_seconds: 87

stages:
  - stage: 0
    name: "Precondition Check"
    status: "passed"
    timestamp: "2026-01-10T15:30:45Z"
    checks:
      - git_initialized: true
      - remote_configured: true
      - current_branch: "CORTEX6"
  
  - stage: 1
    name: "Stash Local Changes"
    status: "passed"

The orchestrator maintains a comprehensive audit log with correlation ID tracking for full traceability. Each stage logs its status, timestamp, and relevant data including hashes, file counts, resolution rules applied, and evidence used for decisions. The log structure captures guarantees upheld (no data loss, zero ambiguity, complete audit trail, clean state) and tracks hash transitions from initial HEAD through sync, commit, and final remote state.

---

## 🚨 Failure Modes & Recovery

The orchestrator handles five primary failure scenarios with explicit recovery procedures:

**Mode 1: Stash Failure** - When stash creation fails due to working tree conflicts, the system enumerates conflicted files, creates manual backups, resets conflicts, and retries stash creation while logging STASH_RECOVERY_TRIGGERED.

**Mode 2: Unresolvable Merge Conflict** - When value-based rules cannot determine a winner, the system creates a detailed conflict report with both versions and rule results, exports to cortex-brain/documents/git-conflicts/, aborts the merge, restores the stash, and requires manual intervention.

**Mode 3: Quality Gate Failure** - When tests fail or lint/security issues are detected, the system generates a detailed report with gate, file, error, and line number, exports to cortex-brain/documents/validation-failures/, unstages changes, preserves the stash, and requires fixes before retry.

**Mode 4: Push Rejected** - When remote has diverged (non-fast-forward), the system fetches remote changes, analyzes divergence, returns to Stage 2 for re-merge, and retries push up to three times while logging PUSH_RETRY_TRIGGERED.

**Mode 5: Ambiguous Untracked Files** - When files don't match any classification rule, the system enumerates ambiguous files, exports the list to cortex-brain/documents/ambiguous-files/, provides classification template, and requires manual classification before proceeding.

---

## 🎯 Success Criteria

At workflow completion, these guarantees must hold:

**Repository State** - Working tree is clean with no pending stashes, fully synchronized with remote (local HEAD equals remote HEAD), and all changes committed with no unstaged or untracked files.

**Quality Guarantees** - All tests pass with coverage meeting the 80% threshold (configurable), no lint errors from ruff, no security issues from Bandit, and consistent formatting per black standards.

**Audit Trail** - Complete log of all stages with correlation ID linking operations, conflict resolutions documented with evidence, and hashes captured at each state transition.

**Data Integrity** - No data loss with all local changes incorporated, all decisions explainable with documented reasoning, file classification deterministic, and stash preserved until successful completion.

---

## 🔧 Integration with CORTEX

### Invocation Patterns

The orchestrator integrates with CORTEX through multiple invocation methods:

- **Via intent routing** (preferred): Routes through src.main with pattern matching for "git vacuum", "commit workflow", "sync and commit", or "clean repo"
- **Direct orchestrator call**: Executes src.orchestrators.git.vacuum_orchestrator with auto-commit flag
- **Custom options**: Supports parameters for branch, remote, coverage threshold, and correlation ID

### Routing Configuration

Pattern matching assigns priority 50 with autonomous mode enabled. Associated AC-IDs include AC-GIT-001 through AC-GIT-005 covering stash management, intelligent merge, workspace hygiene, quality enforcement, and audit trail.

### Governance Integration

The orchestrator enforces CORTEX SKULL rules:

- **CORE-001**: Incremental execution through 8 discrete stages
- **CORE-005**: Portable paths ensuring cross-platform Git compatibility
- **CORE-008**: TDD enforcement during validation stage
- **CORE-017**: Governance enforcement through quality gates
- **CORE-023**: File type-specific validation for HTML, YAML, and Python

### Audit Integration

Logs to EnterpriseAuditLogger under GIT_OPERATIONS category with INFO level for success, WARNING for retry attempts, and ERROR for abort conditions. Retention is 60 days for operational queries. All logs are queryable by correlation ID for complete traceability.

---

## 📈 Metrics & Observability

Key performance indicators track orchestrator effectiveness:

- **Execution Time**: Target under 2 minutes for complete workflow
- **Conflict Rate**: Target under 10% merge conflicts per execution
- **Quality Gate Pass Rate**: Target over 95% first-time validation success
- **File Classification Accuracy**: Target over 98% auto-classified vs ambiguous
- **Data Loss Rate**: Target 0% with zero tolerance policy

Monitoring queries support trend analysis for execution duration, conflict resolution patterns, and quality gate failures over configurable time windows.

---

## 🎓 Learning Integration

The orchestrator feeds Tier 3 knowledge capture for continuous improvement. After each execution, learned patterns are documented with pattern ID, name, context, resolution strategy, evidence, confidence score, and timestamp. Patterns are stored in cortex-brain/tier3/patterns/git-operations.yaml.

Adaptation rules trigger on pattern thresholds. If conflict resolution rules fail above 5%, the system escalates to manual review. If ambiguous files appear more than three times, they are added to classification rules. Quality gate thresholds adjust if failure rates exceed 10%. Execution time optimization targets bottleneck stages when duration exceeds 3 minutes.

---

## 🔐 Security Considerations

The orchestrator implements comprehensive security controls:

**Secret Protection** - Never commits API keys, passwords, or tokens. Pre-commit hooks scan with detect-secrets. Optional stash encryption for sensitive repositories. Audit logs mask credentials.

**Access Control** - Repository permissions verified via Git config. Remote authentication uses SSH keys or tokens. Stash access limited to current user. Audit logs are read-only for non-admin users.

**Compliance** - GDPR compliance ensures no PII in commit messages or logs. SOC 2 compliance maintains complete audit trail for all operations. PCI DSS compliance prohibits card data in repository. HIPAA compliance prohibits PHI in commit history.

---

## 📚 References

### CORTEX Core Integration
- `.github/copilot-instructions.md`: Entry point and routing protocol
- `cortex-brain/tier0/governance/core-rules.yaml`: 23 SKULL rules
- `cortex-brain/response-templates-v4.yaml`: Output formatting standards

### Implementation Components
- `src/orchestrators/git/vacuum_orchestrator.py`: Main executor
- `src/infrastructure/enhanced_audit_logger.py`: Audit logging infrastructure
- `src/governance/enforcement_engine.py`: Quality gate enforcement
- `src/tools/git_operations.py`: Low-level Git operation wrappers

### Related Acceptance Criteria
- **AC-GIT-001**: Safe stash management with metadata and audit logging
- **AC-GIT-002**: Value-based merge resolution with evidence tracking
- **AC-GIT-003**: Deterministic file classification with documented reasoning
- **AC-GIT-004**: Quality enforcement through type-specific validation gates
- **AC-GIT-005**: Complete audit trail with correlation ID and hash tracking
- **AC-AUDIT-008**: Git operation logging to EnterpriseAuditLogger
- **AC-CLEAN-001**: Workspace cleanup rules and file classification

---

**Version History:**
- 1.0.0: Initial production-grade Git orchestration prompt with deterministic workflow, value-based conflict resolution, and complete audit integration
- 1.1.0: Reduced verbosity, added machine alignment protocol for multi-machine plan continuation, removed code snippets in favor of clear prose descriptions

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**  
This prompt is part of the CORTEX 6.0 Production-Grade AI Orchestration System.
