# CORTEX Git Commit Orchestrator

**Version:** 1.0.0 | **Category:** Autonomous Git Operations | **Safety:** Maximum  
**Purpose:** Deterministic, audit-driven Git workflow with zero tolerance for data loss  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Mission

Execute CORTEX "vacuum" workflow with mathematical determinism and complete auditability:
1. **Stash** local changes with traceable metadata
2. **Sync** from remote with intelligent merge
3. **Validate** working tree against quality gates
4. **Commit** with structured, intent-capturing message
5. **Push** with verification
6. **Clean** workspace to pristine state
7. **Audit** all decisions and state transitions

**Invariant:** Repository ends in clean, synchronized, auditable state with zero ambiguity.

---

## 🛡️ Safety-First Principles

### P1: No Data Loss Ever
- **All local changes** preserved in named, timestamped stash
- **All stash operations** logged with hash before/after
- **Merge conflicts** resolved via explicit rules, never heuristically
- **Destructive operations** (delete, overwrite) require explicit justification

### P2: Explainable Decisions
- Every file classification (add, ignore, delete) has documented reason
- Merge resolution shows evidence (test status, security score, docs)
- Audit log traces every state transition with correlation ID

### P3: Idempotent Execution
- Running twice produces identical result
- Intermediate failures leave breadcrumbs for recovery
- All operations check preconditions before execution

### P4: Zero Ambiguity
- Untracked files handled deterministically (no "manual review" escape hatch)
- Conflicts resolved by rules, not human intervention
- Success criteria defined upfront, not discovered during execution

---

## 📋 Execution Pipeline

### Stage 0: Precondition Check
```yaml
Required State:
  - Git repository initialized
  - Remote configured (origin)
  - Current branch known
  - Working directory exists

Verify:
  - .git/config exists
  - `git remote -v` shows origin
  - `git branch --show-current` succeeds
  - No active rebase/merge in progress

Failure Mode: ABORT with diagnostic message
```

### Stage 1: Stash Local Changes
```yaml
Operation: Stash with Metadata

Steps:
  1. Generate stash name:
     Format: "cortex-vacuum-{timestamp}-{correlation_id}"
     Example: "cortex-vacuum-20260110T153045Z-a7f3b21c"
  
  2. Capture pre-stash state:
     - HEAD commit hash
     - Working tree status (modified, deleted, untracked)
     - Staged changes
  
  3. Execute stash:
     Command: git stash push -u -m "{stash_name}" --include-untracked
     Flags: -u (include untracked), -m (message)
  
  4. Verify stash created:
     Command: git stash list | grep "{stash_name}"
     Confirm: Stash reference exists
  
  5. Log to audit:
     Event: STASH_CREATED
     Data: {stash_name, pre_hash, file_count, correlation_id}

Success Criteria:
  - Stash exists in `git stash list`
  - Working tree clean (`git status --porcelain` empty)
  - Audit entry written

Failure Mode: ABORT - cannot proceed without clean working tree
```

### Stage 2: Sync from Remote
```yaml
Operation: Fetch + Pull with Intelligent Merge

Steps:
  1. Fetch from remote:
     Command: git fetch origin
     Capture: Remote branch HEADs
  
  2. Analyze divergence:
     Local: git rev-parse HEAD
     Remote: git rev-parse origin/{current_branch}
     Check: Are we behind? Ahead? Diverged?
  
  3. Execute pull:
     Command: git pull origin {current_branch} --no-ff
     Strategy: Merge (not rebase, preserves history)
  
  4. Handle merge conflicts:
     If conflicts exist:
       - Enumerate conflicted files: `git diff --name-only --diff-filter=U`
       - For each file, resolve via Value-Based Rules (see Stage 2.1)
       - Stage resolved files: `git add {file}`
       - Complete merge: `git commit --no-edit`
  
  5. Log to audit:
     Event: SYNC_COMPLETED
     Data: {pre_hash, post_hash, files_merged, conflicts_resolved, strategy}

Success Criteria:
  - No merge conflicts remain
  - Working tree clean
  - Local ahead of remote or equal
  - Audit entry written

Failure Mode: Unresolvable conflict → create diagnostic report, ABORT
```

#### Stage 2.1: Value-Based Conflict Resolution
```yaml
Resolution Rules (Applied in Order):

Rule 1: Test Coverage Wins
  - If one version has passing tests, other doesn't → choose passing
  - Evidence: pytest exit code, coverage percentage
  - Log: TEST_COVERAGE_RESOLUTION

Rule 2: Security Posture Wins
  - If one version has security issues, other doesn't → choose secure
  - Evidence: Bandit scan, known CVEs, audit logs
  - Log: SECURITY_RESOLUTION

Rule 3: Architectural Consistency Wins
  - If one version follows CORTEX patterns, other doesn't → choose consistent
  - Evidence: Imports from src.orchestrators, uses DI, follows tier structure
  - Log: ARCHITECTURE_RESOLUTION

Rule 4: Documentation Wins
  - If one version has docstrings/type hints, other doesn't → choose documented
  - Evidence: Docstring presence, type annotation coverage
  - Log: DOCUMENTATION_RESOLUTION

Rule 5: Recency Wins (Tie-Breaker)
  - If both versions equal on above criteria → choose newer timestamp
  - Evidence: Git commit date
  - Log: RECENCY_RESOLUTION

Unresolvable: Both versions fail all criteria
  - Create conflict report: {file, rule_results, manual_review_required}
  - ABORT with diagnostic

Audit Requirement:
  - Each resolution logs: {file, rule_applied, chosen_version, evidence}
```

### Stage 3: Reapply Stash (Selective)
```yaml
Operation: Semantic Stash Reapplication

Steps:
  1. Retrieve stash:
     Command: git stash list | grep "cortex-vacuum"
     Get: Most recent CORTEX stash reference
  
  2. Analyze stash contents:
     Command: git stash show -p stash@{n}
     Extract: Changed files, line-level diffs
  
  3. Semantic conflict check:
     For each stashed file:
       - Does it conflict with remote changes?
       - If yes, apply Value-Based Rules (Stage 2.1)
       - If no, apply directly
  
  4. Apply stash:
     Command: git stash apply stash@{n}
     Handle conflicts: Use Value-Based Rules
  
  5. Cleanup stash:
     If application successful:
       Command: git stash drop stash@{n}
     Else:
       Keep stash, log failure
  
  6. Log to audit:
     Event: STASH_REAPPLIED
     Data: {stash_name, files_applied, conflicts_resolved, stash_dropped}

Success Criteria:
  - All stash changes integrated or resolved
  - Working tree dirty (local changes restored)
  - Audit entry written

Failure Mode: Stash conflicts unresolvable → create diagnostic, keep stash
```

### Stage 4: Validate Working Tree
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
    timestamp: "2026-01-10T15:30:47Z"
    data:
      stash_name: "cortex-vacuum-20260110T153045Z-a7f3b21c"
      pre_hash: "abc123def456"
      files_stashed: 12
      stash_reference: "stash@{0}"
  
  - stage: 2
    name: "Sync from Remote"
    status: "passed"
    timestamp: "2026-01-10T15:31:03Z"
    data:
      pre_hash: "abc123def456"
      post_hash: "def789ghi012"
      files_merged: 5
      conflicts_resolved: 2
      resolution_rules:
        - file: "src/orchestrators/core/master.py"
          rule: "TEST_COVERAGE_RESOLUTION"
          chosen: "remote"
          evidence: "remote has 95% coverage, local 80%"
        - file: "src/infrastructure/audit.py"
          rule: "SECURITY_RESOLUTION"
          chosen: "local"
          evidence: "local has no Bandit warnings, remote has 1"
  
  - stage: 3
    name: "Reapply Stash"
    status: "passed"
    timestamp: "2026-01-10T15:31:15Z"
    data:
      stash_name: "cortex-vacuum-20260110T153045Z-a7f3b21c"
      files_applied: 12
      conflicts_resolved: 0
      stash_dropped: true
  
  - stage: 4
    name: "Validate Working Tree"
    status: "passed"
    timestamp: "2026-01-10T15:31:45Z"
    data:
      files_validated: 12
      gates_passed:
        - python_syntax: true
        - python_lint: true
        - python_format: true
        - yaml_schema: true
        - html_validation: true
        - tests: true
        - security: true
      coverage_percentage: 87.3
  
  - stage: 5
    name: "Commit with Structured Message"
    status: "passed"
    timestamp: "2026-01-10T15:31:52Z"
    data:
      commit_hash: "ghi345jkl678"
      message: "feat(git): Add autonomous vacuum workflow orchestrator"
      files_changed: 12
      insertions: 543
      deletions: 87
      ac_ids: ["AC-GIT-001", "AC-GIT-002", "AC-AUDIT-008"]
  
  - stage: 6
    name: "Push to Remote"
    status: "passed"
    timestamp: "2026-01-10T15:32:05Z"
    data:
      local_hash: "ghi345jkl678"
      remote_hash: "ghi345jkl678"
      commits_pushed: 1
  
  - stage: 7
    name: "Clean Workspace"
    status: "passed"
    timestamp: "2026-01-10T15:32:08Z"
    data:
      files_added: 2
      files_ignored: 5
      files_deleted: 3
      ambiguous_count: 0
      gitignore_rules_added:
        - rule: "*.pyc"
          reason: "Python bytecode"
        - rule: "__pycache__/"
          reason: "Python cache directory"
  
  - stage: 8
    name: "Final Validation"
    status: "passed"
    timestamp: "2026-01-10T15:32:12Z"
    data:
      checks_passed:
        - git_status_clean: true
        - stash_empty: true
        - remote_synced: true
        - smoke_tests: true
        - audit_chain_complete: true

guarantees_upheld:
  - "No data loss: All local changes preserved and reapplied"
  - "Zero ambiguity: All files classified deterministically"
  - "Audit trail: Complete provenance with correlation ID"
  - "Quality gates: All validations passed"
  - "Clean state: Repository pristine and synchronized"

hashes:
  initial_head: "abc123def456"
  after_sync: "def789ghi012"
  after_commit: "ghi345jkl678"
  final_remote: "ghi345jkl678"
```

---

## 🚨 Failure Modes & Recovery

### Mode 1: Stash Failure
**Symptom:** Cannot create stash (working tree conflicts)  
**Recovery:**
1. Enumerate conflicted files: `git status --porcelain`
2. Create manual backup: `cp {file} {file}.backup`
3. Reset conflicts: `git reset --hard HEAD`
4. Retry stash with backups
5. Log: STASH_RECOVERY_TRIGGERED

### Mode 2: Unresolvable Merge Conflict
**Symptom:** Value-based rules cannot determine winner  
**Recovery:**
1. Create conflict report: `{file, both_versions, rule_results}`
2. Export to: `cortex-brain/documents/git-conflicts/{timestamp}.yaml`
3. Abort merge: `git merge --abort`
4. Restore stash: `git stash apply stash@{n}`
5. Log: MERGE_ABORTED_UNRESOLVABLE
6. Alert: Require manual intervention

### Mode 3: Quality Gate Failure
**Symptom:** Tests fail, lint errors, security issues  
**Recovery:**
1. Generate detailed report: `{gate, file, error, line_number}`
2. Export to: `cortex-brain/documents/validation-failures/{timestamp}.yaml`
3. Unstage changes: `git reset HEAD`
4. Restore stash: Keep stashed changes safe
5. Log: VALIDATION_FAILED_ABORT
6. Alert: Fix issues before retry

### Mode 4: Push Rejected
**Symptom:** Remote has diverged (non-fast-forward)  
**Recovery:**
1. Fetch remote: `git fetch origin`
2. Analyze divergence: `git log HEAD..origin/{branch}`
3. Return to Stage 2: Re-merge with latest remote
4. Retry push (max 3 attempts)
5. Log: PUSH_RETRY_TRIGGERED

### Mode 5: Ambiguous Untracked Files
**Symptom:** Files don't match any classification rule  
**Recovery:**
1. Enumerate ambiguous: `git ls-files --others --exclude-standard`
2. Export list: `cortex-brain/documents/ambiguous-files/{timestamp}.yaml`
3. Provide classification template
4. Log: AMBIGUOUS_FILES_DETECTED
5. Alert: Require manual classification

---

## 🎯 Success Criteria

At completion, the following MUST be true:

### Repository State
- ✅ Working tree clean: `git status --porcelain` is empty
- ✅ No pending stashes: `git stash list | grep cortex-vacuum` is empty
- ✅ Fully synchronized: `HEAD == origin/{branch}`
- ✅ All changes committed: No unstaged or untracked files

### Quality Guarantees
- ✅ All tests pass: pytest exit code 0
- ✅ Coverage meets threshold: ≥80% (configurable)
- ✅ No lint errors: ruff clean
- ✅ No security issues: Bandit clean
- ✅ Format consistent: black compliant

### Audit Trail
- ✅ Complete log: All 8 stages recorded
- ✅ Correlation ID: Links all operations
- ✅ Evidence preserved: Conflict resolutions documented
- ✅ Hashes captured: Before/after at each stage

### Data Integrity
- ✅ No loss: All local changes incorporated
- ✅ Conflict resolution: All decisions explainable
- ✅ File classification: All untracked files handled
- ✅ Backup available: Stash preserved until success

---

## 🔧 Integration with CORTEX

### Invocation from GitHub Copilot
```bash
# Via intent routing (preferred)
python3 -m src.main "perform git vacuum workflow" --format markdown

# Direct orchestrator call
python3 -m src.orchestrators.git.vacuum_orchestrator --auto-commit

# With custom options
python3 -m src.orchestrators.git.vacuum_orchestrator \
  --branch CORTEX6 \
  --remote origin \
  --coverage-threshold 85 \
  --correlation-id {uuid}
```

### Routing Pattern
```yaml
pattern: "git vacuum|commit workflow|sync and commit|clean repo"
orchestrator: "Git Vacuum Orchestrator"
mode: autonomous
priority: 50
ac_ids: ["AC-GIT-001", "AC-GIT-002", "AC-GIT-003", "AC-AUDIT-008"]
```

### Governance Rules Applied
- **CORE-001:** Incremental execution (stages 1-8)
- **CORE-005:** Portable paths (cross-platform Git)
- **CORE-008:** TDD enforcement (Stage 4 tests)
- **CORE-017:** Governance enforcement (quality gates)
- **CORE-023:** File validation (HTML, YAML, Python)

### Audit Integration
- Logger: `EnterpriseAuditLogger`
- Category: `GIT_OPERATIONS`
- Levels: INFO (success), WARNING (retry), ERROR (abort)
- Retention: 60 days (operational category)
- Query: `audit query --category GIT_OPERATIONS --correlation-id {uuid}`

---

## 📈 Metrics & Observability

### Key Metrics
- **Execution Time:** Total duration (target: <2 minutes)
- **Conflict Rate:** Merge conflicts per execution (target: <10%)
- **Quality Gate Pass Rate:** First-time validation success (target: >95%)
- **File Classification Accuracy:** Auto-classified vs ambiguous (target: >98%)
- **Data Loss Rate:** Lost changes per execution (target: 0%)

### Monitoring Queries
```bash
# Execution time trend
python3 -m src.main "audit query --category GIT_OPERATIONS --field duration --last 7d"

# Conflict resolution patterns
python3 -m src.main "audit query --category GIT_OPERATIONS --field resolution_rules --last 30d"

# Quality gate failures
python3 -m src.main "audit query --category GIT_OPERATIONS --level WARNING --field gate --last 7d"
```

---

## 🎓 Learning Integration

### Tier 3 Knowledge Capture
After each execution, update learned patterns:

```yaml
pattern_id: "GIT-PATTERN-001"
name: "Frequent Test Coverage Conflicts"
context: "src/orchestrators/core/*.py files often conflict during sync"
resolution: "Remote version wins if coverage ≥90%, else local"
evidence: "15 executions, 100% success rate"
confidence: 0.95
updated: "2026-01-10T15:32:12Z"
```

Location: `cortex-brain/tier3/patterns/git-operations.yaml`

### Adaptation Rules
- If conflict resolution rule fails >5% → escalate to manual review
- If ambiguous file appears >3 times → add to classification rules
- If quality gate fails >10% → adjust thresholds
- If execution time >3 minutes → optimize bottleneck stages

---

## 🔐 Security Considerations

### Secret Protection
- **Never commit:** API keys, passwords, tokens
- **Pre-commit hook:** Scan with detect-secrets
- **Stash encryption:** Optional for sensitive repos
- **Audit redaction:** Mask credentials in logs

### Access Control
- **Repository permissions:** Verified via Git config
- **Remote authentication:** Use SSH keys or tokens
- **Stash access:** Limited to current user
- **Audit logs:** Read-only for non-admin

### Compliance
- **GDPR:** No PII in commit messages or logs
- **SOC 2:** Complete audit trail for all operations
- **PCI DSS:** No card data in repository
- **HIPAA:** No PHI in commit history

---

## 📚 References

### CORTEX Core
- `.github/copilot-instructions.md` → Entry point, routing protocol
- `cortex-brain/tier0/governance/core-rules.yaml` → SKULL rules
- `cortex-brain/response-templates-v4.yaml` → Output formatting

### Implementation
- `src/orchestrators/git/vacuum_orchestrator.py` → Main executor
- `src/infrastructure/enhanced_audit_logger.py` → Audit logging
- `src/governance/enforcement_engine.py` → Quality gates
- `src/tools/git_operations.py` → Low-level Git wrappers

### Related AC-IDs
- **AC-GIT-001:** Stash with metadata
- **AC-GIT-002:** Value-based merge resolution
- **AC-GIT-003:** Deterministic file classification
- **AC-AUDIT-008:** Git operation logging
- **AC-CLEAN-001:** Workspace cleanup rules

---

## 🎯 Acceptance Criteria

### AC-GIT-001: Safe Stash Management
- [x] Named stash with correlation ID
- [x] Pre-stash state captured (hash, file list)
- [x] Stash verified before proceeding
- [x] Audit log entry with metadata

### AC-GIT-002: Intelligent Merge
- [x] Value-based conflict resolution (5 rules)
- [x] Evidence-driven decisions (tests, security, docs)
- [x] Unresolvable conflicts create diagnostic report
- [x] Audit log with resolution rationale

### AC-GIT-003: Workspace Hygiene
- [x] Untracked files classified (add, ignore, delete)
- [x] .gitignore updated with comments
- [x] No ambiguous files remain
- [x] Audit log with file actions

### AC-GIT-004: Quality Enforcement
- [x] Type-specific validation (Python, YAML, HTML)
- [x] Test coverage ≥ threshold
- [x] Security scan passes
- [x] Validation failures create detailed report

### AC-GIT-005: Audit Trail
- [x] All 8 stages logged with correlation ID
- [x] Hashes captured at each transition
- [x] Conflict resolutions with evidence
- [x] Queryable via correlation ID

---

**Version History:**
- 1.0.0: Initial production-grade Git orchestration prompt with deterministic workflow, value-based conflict resolution, and complete audit integration

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**  
This prompt is part of the CORTEX 6.0 Production-Grade AI Orchestration System.
