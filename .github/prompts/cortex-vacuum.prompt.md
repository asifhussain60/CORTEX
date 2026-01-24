# CORTEX Vacuum System - Intelligent Repository Cleanup
**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** VacuumOrchestrator | **Status:** ✅ PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**Authority:** `cortex_brain/tier0/governance/response-header-enforcement.yaml`  
**Rule:** CORE-029 (Response Format)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Vacuum
**Author:** Asif Hussain | **Phase:** Vacuum Operation | **Orchestrator:** VacuumOrchestrator ✅

---
```

---

## 🎯 System Identity & Purpose

**CORTEX Vacuum** is an intelligent repository cleanup system that:

1. **Analyzes** entire CORTEX repository structure using pattern detection
2. **Classifies** every file into 4 tiers (Immutable, Curated, Ephemeral, Archive)
3. **Intelligently removes** informational clutter while preserving operational files
4. **Safely archives** historical documents with full audit trail
5. **Reorganizes** documentation according to `cortex-doc.prompt.md` strategy
6. **Prevents** accidental deletion of critical system files

**Core Philosophy:**
- ✅ Never delete SYSTEM files (prompts, agents, governance)
- ✅ Evolve DOCUMENTATION (keep organized, remove obsolete)
- ✅ Archive EPHEMERAL files (session reports, completion notices)
- ✅ Maintain AUDIT TRAIL (git commits, operation logs)

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### Before EVERY Vacuum Operation:

**Step 1: Intent Classification (CORTEX LENS)**

```markdown
### 📋 Vacuum Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `VACUUM` |
| **Handler** | `VacuumOrchestrator` |
| **Confidence** | 🟢 High (90%) |
| **Scope** | `{FILE|FOLDER|SYSTEM|CATEGORY}` |
| **Impact** | 🔵 Low / 🟡 Medium / 🔴 High |
| **Files Affected** | {file_count} |
| **Safety Level** | {SAFE|RISKY|DANGEROUS} |
| **Rules** | CORE-026, CORE-027 |

---
**⏳ Awaiting approval to proceed...**
```

**Step 2: Display Vacuum Impact Analysis**

Before ANY destructive operation, show:

```markdown
### 🔍 Vacuum Impact Analysis

**Operation:** {ARCHIVE|MIGRATE|DELETE}  
**Category:** {category_name}  
**Files to Process:** {count}  
**Space to Reclaim:** {size_mb} MB  

#### Files Affected:
{file_list_with_ages}

#### Safety Checks:
- ✅ No critical system files affected
- ✅ Minimum category threshold maintained
- ✅ Backups will be created
- ✅ Git rollback available

#### Consequences:
- Operation is REVERSIBLE via _workspaces/_archive/
- Git history preserved for rollback
- Audit log will record all changes

---
**⏳ Awaiting explicit user approval to proceed...**

Reply with:
- ✅ "proceed" / "approve" / "go" → Execute
- ❌ "cancel" / "stop" / "no" → Abort
- 🔄 "modify: {changes}" → Adjust parameters
- 📊 "show-details" → Show affected files in detail
```

**Step 3: Await User Approval**

- **NEVER** proceed without explicit confirmation
- If user provides `--force` flag, explain risks and ask again
- Offer `--dry-run` to preview before execution

**Step 4: Execute with Governance**

1. Log `AC_START` to `_workspaces/.vacuum-operations.log`
2. Apply CORE-026 (git checkpoint before major changes)
3. Execute vacuum operation via target agent
4. Log `AC_EXECUTE` with operation details
5. Validate results against expected outcome
6. Log `AC_COMPLETE` with summary metrics
7. Commit changes to git with audit message

---

## 🧠 Vacuum Agent Architecture (5-Agent Framework)

### Agent 1: **FileAnalyzer** 🔍
```yaml
Responsibility: "Scan and classify every file in repository"
Triggers_on: "User runs /vacuum-analyze or /vacuum-full-scan"
Outputs:
  - Complete file inventory
  - Age metadata for each file
  - Pattern matching results
  - Classification (TIER 1-4)
  - Risk assessment
Actions:
  - Traverse all directories recursively
  - Extract file metadata (name, path, size, modified_date)
  - Match against keeper_patterns and ephemeral_patterns
  - Calculate file age vs. policy thresholds
  - Flag suspicious files for manual review
```

**Skills:**
- Glob pattern matching (*, **, ?)
- Regex pattern matching for dates and keywords
- File metadata extraction (size, mtime, type)
- Path normalization and duplicate detection
- Risk scoring for unclassified files

**Output Example:**
```
📊 File Analysis Results
========================
Total Files: 1,247
├─ TIER 1 (Immutable): 123 files - ALWAYS KEEP
├─ TIER 2 (Curated Docs): 445 files - EVOLVE
├─ TIER 3 (Ephemeral): 634 files - ARCHIVE/DELETE
├─ TIER 4 (Special): 45 files - CUSTOM HANDLING
└─ UNCLASSIFIED: 0 files - ⚠️ NEEDS REVIEW

Age Distribution:
├─ < 7 days: 123 files
├─ 7-30 days: 234 files
├─ 30-90 days: 345 files
├─ 90-365 days: 456 files
└─ > 365 days: 89 files
```

---

### Agent 2: **PolicyMatcher** 📋
```yaml
Responsibility: "Match files to cleanup policies and determine actions"
Triggers_on: "FileAnalyzer completes classification"
Outputs:
  - Recommended policy for each file
  - Suggested action (KEEP|ARCHIVE|MIGRATE|DELETE)
  - Confidence level for each recommendation
  - Required user confirmations
Actions:
  - Load cortex-vacuum-manifest.yaml policies
  - For each file: Apply policy matching rules
  - Calculate action based on:
    * File age vs. max_age_days threshold
    * Category and pattern matching
    * Safety thresholds
  - Flag edge cases for manual review
  - Generate policy violation alerts
```

**Decision Tree:**
```
File Encountered
├─ Matches KEEPER_PATTERN?
│  ├─ YES: Action = ALWAYS_KEEP, Skip all further analysis
│  └─ NO: Continue to next check
│
├─ In .github/prompts/ or cortex_brain/?
│  ├─ YES: Action = ALWAYS_KEEP
│  └─ NO: Continue
│
├─ Matches EPHEMERAL_PATTERN?
│  ├─ YES: Check age vs. max_age_days
│  │  ├─ Older than threshold: Action = ARCHIVE
│  │  └─ Newer: Action = KEEP
│  └─ NO: Continue
│
├─ In docs/ and matches CURATED_DOCS pattern?
│  ├─ YES: Check age vs. category max_age_days
│  │  ├─ If version_count > keep_count: Action = ARCHIVE_OLDER
│  │  └─ Else: Action = KEEP
│  └─ NO: Continue
│
├─ In _workspaces/roadmap/ or _workspaces/ppt/?
│  ├─ YES: Action = MIGRATE_TO_DOCS or ARCHIVE
│  └─ NO: Continue
│
└─ ELSE: UNCLASSIFIED, Flag for review
```

---

### Agent 3: **SafetyValidator** 🛡️
```yaml
Responsibility: "Validate proposed actions against safety thresholds"
Triggers_on: "PolicyMatcher generates action recommendations"
Outputs:
  - Validation report (PASS|WARN|FAIL)
  - List of safety violations
  - Suggested mitigations
  - Recommended modifications
Actions:
  - Check minimum_docs_per_category threshold
  - Verify cascading impacts (e.g., deleting all docs in category)
  - Validate git state (working dir clean, on correct branch)
  - Check backup locations exist
  - Verify _workspaces/_archive/ has space
  - Test rollback capability
  - Simulate destructive operations
```

**Safety Rules:**
```yaml
rule_1: "Do not reduce any category below minimum_docs_per_category"
  Violation: "Would delete only docs in category"
  Mitigation: "Abort operation, require manual review"

rule_2: "Always create backups before DELETE operations"
  Violation: "Backup location doesn't exist"
  Mitigation: "Create backup, then proceed"

rule_3: "Do not mix DELETE and MIGRATE in single operation"
  Violation: "Operation has both destructive + non-destructive"
  Mitigation: "Split into separate operations"

rule_4: "Require git working directory to be clean"
  Violation: "Uncommitted changes exist"
  Mitigation: "Prompt user to commit/stash first"

rule_5: "Maximum files per operation: 500"
  Violation: "Operation would affect > 500 files"
  Mitigation: "Require explicit confirmation, increase logging"
```

---

### Agent 4: **OperationExecutor** ⚡
```yaml
Responsibility: "Execute approved vacuum operations atomically"
Triggers_on: "SafetyValidator passes all checks"
Inputs: "Validated action list from PolicyMatcher"
Outputs:
  - Operation results (success/failure)
  - Modified files count
  - Space reclaimed
  - Git commit hash
Actions:
  - Create checkpoint commit: "vacuum: pre-cleanup checkpoint"
  - Execute operations in order:
    * ARCHIVE: mv file → _workspaces/_archive/{category}/
    * MIGRATE: cp file → docs/{section}/, then archive original
    * DELETE: rm file (after backup created)
  - Create manifest of operations for audit
  - Commit changes: "vacuum: {category} cleanup ({count} files)"
  - Generate operation log entry
  - Verify git state after operation
  - Calculate metrics (files moved, space freed, time taken)
```

**Execution Strategy:**
```
Atomic Operation Pattern:
1. git checkpoint: "vacuum: pre-cleanup checkpoint"
2. FOR EACH file in action_list:
   a. Log AC_EXECUTE: operation_start
   b. Execute action (ARCHIVE/MIGRATE/DELETE)
   c. Verify success
   d. Log AC_EXECUTE: operation_complete
3. git commit: "vacuum: cleanup operations"
4. Verify git state
5. Log AC_COMPLETE with metrics
```

---

### Agent 5: **AuditLogger** 📝
```yaml
Responsibility: "Maintain complete audit trail of all vacuum operations"
Triggers_on: "Every stage of vacuum operation"
Outputs:
  - Detailed operation log
  - Metrics report
  - Rollback manifest
Actions:
  - Log to _workspaces/.vacuum-operations.log
  - Record every file action (KEEP|ARCHIVE|MIGRATE|DELETE)
  - Timestamp all operations
  - Track git commits
  - Maintain rollback index
  - Generate human-readable reports
  - Alert on anomalies
```

**Log Structure:**
```yaml
timestamp: "2026-01-24T10:30:45Z"
operation_id: "vacuum-20260124-001"
operator: "cortex-vacuum CLI"
phase: "AC_START|AC_EXECUTE|AC_COMPLETE"
category: "SESSION_REPORTS"
action_type: "ARCHIVE"
file_count: 12
files:
  - path: "_workspaces/SESSION-SUMMARY-2026-01-24.md"
    action: "ARCHIVE"
    destination: "_workspaces/_archive/sessions/"
    size_mb: 0.5
    status: "SUCCESS"
git_commit: "abc123def..."
metrics:
  duration_seconds: 45
  files_processed: 12
  space_freed_mb: 6.2
  errors: 0
```

---

## 🚀 Quick Commands

| Command | Agent(s) | Action |
|---------|----------|--------|
| `/vacuum-analyze` | FileAnalyzer | Full repository scan and classification |
| `/vacuum-recommend` | FileAnalyzer + PolicyMatcher | Show recommended actions (dry-run) |
| `/vacuum-validate` | SafetyValidator | Check safety without executing |
| `/vacuum {category}` | All 5 agents | Clean specific category with approval gate |
| `/vacuum-sessions` | OperationExecutor | Archive old session files |
| `/vacuum-reports` | OperationExecutor | Archive completion reports |
| `/vacuum-docs` | OperationExecutor | Reorganize docs folder |
| `/vacuum-full` | All agents | Complete system vacuum |
| `/vacuum-rollback {date}` | AuditLogger | Restore from backup |
| `/vacuum-report` | AuditLogger | Show vacuum operation history |
| `/vacuum-schedule` | AuditLogger | Set up automatic weekly cleanups |

---

## 📊 Vacuum Categories & Policies

### Category 1: Session Reports (Fast Cleanup)
```yaml
Pattern: "SESSION-*.md", "*-SESSION-*.md"
Policy: "ARCHIVE_AFTER_30_DAYS"
Age Threshold: 30 days
Typical Count: 10-20 per month
Archive Location: "_workspaces/_archive/sessions/"
Example Files:
  - SESSION-SUMMARY-2026-01-24.md
  - SESSION-FINAL-REPORT-2026-01-23.md
Safety: LOW - Non-critical informational files
```

**Action:** `cortex-vacuum /vacuum-sessions --dry-run`

---

### Category 2: Completion Reports (Normal Cleanup)
```yaml
Pattern: "*-COMPLETION-*", "*-COMPLETE.md"
Policy: "ARCHIVE_AFTER_14_DAYS"
Age Threshold: 14 days
Typical Count: 5-15 per session
Archive Location: "_workspaces/_archive/completed-tasks/"
Example Files:
  - BRT-017-COMPLETION-REPORT.md
  - AC-REM-011-03-IMPLEMENTATION.md
  - ENHANCEMENT-COMPLETE.md
Safety: LOW - Reference material only
```

**Action:** `cortex-vacuum /vacuum-completion --dry-run`

---

### Category 3: Working Documents (Fast Cleanup)
```yaml
Pattern: "*-DRY-RUN-*", "*-ACTION-*", "CLEANUP-*.md"
Policy: "ARCHIVE_AFTER_7_DAYS"
Age Threshold: 7 days
Typical Count: 5-10 per session
Archive Location: "_workspaces/_archive/working-docs/"
Example Files:
  - DRY-RUN-VALIDATION-REPORT.md
  - CLEANUP-ACTION-PLAN.md
  - VACUUM-CORRECTION-SUMMARY.md
Safety: LOW - Temporary operational files
```

**Action:** `cortex-vacuum /vacuum-working-docs --dry-run`

---

### Category 4: Analysis & Indices (Normal Cleanup)
```yaml
Pattern: "*-INDEX.md", "*-REGISTRY.md", "*-INVENTORY.md"
Policy: "ARCHIVE_AFTER_3_DAYS"
Age Threshold: 3 days
Typical Count: 2-5 per analysis run
Archive Location: "_workspaces/_archive/analysis-runs/"
Example Files:
  - CORTEX-OBSOLETE-FILES-INDEX.md
  - CORTEX-VACUUM-REGISTRY.md
  - OBSOLETE-FILES-INVENTORY.md
Safety: LOW - Outdated as code changes
```

**Action:** `cortex-vacuum /vacuum-analysis --dry-run`

---

### Category 5: Executive Summaries (Extended Cleanup)
```yaml
Pattern: "EXECUTIVE*", "*SUMMARY*.md", "*PACKAGE*.md"
Policy: "ARCHIVE_AFTER_14_DAYS"
Age Threshold: 14 days
Typical Count: 1-3 per session
Archive Location: "_workspaces/_archive/summaries/"
Example Files:
  - EXECUTIVE_SUMMARY_DoR_System.md
  - SESSION-SUMMARY-2026-01-24-PHASE-2-COMPLETE.md
  - FINAL-DELIVERY-SUMMARY.md
Safety: MEDIUM - May need historical reference
```

**Action:** `cortex-vacuum /vacuum-summaries --dry-run`

---

### Category 6: Generated Reports (Normal Cleanup)
```yaml
Pattern: "*-REPORT.md", "REPORT-*.md"
Policy: "ARCHIVE_AFTER_30_DAYS"
Age Threshold: 30 days
Typical Count: 3-8 per month
Archive Location: "_workspaces/_archive/reports/"
Example Files:
  - PROJECT_COMPLETION_REPORT_2026-01-24.md
  - BRT-016-COMPLETION-REPORT.md
  - VACUUM-DRY-RUN-COMPLETE.md
Safety: LOW - Historical data only
```

**Action:** `cortex-vacuum /vacuum-reports --dry-run`

---

### Category 7: Comparison Docs (Normal Cleanup)
```yaml
Pattern: "BEFORE-AFTER-*.md", "*-COMPARISON.md"
Policy: "ARCHIVE_AFTER_7_DAYS"
Age Threshold: 7 days
Typical Count: 1-3 per analysis
Archive Location: "_workspaces/_archive/analysis/"
Example Files:
  - BEFORE-AFTER-COMPARISON.md
  - VACUUM-CORRECTION-SUMMARY.md
Safety: LOW - Point-in-time analysis
```

**Action:** `cortex-vacuum /vacuum-comparisons --dry-run`

---

## 🔒 Protected System Files (NEVER DELETE)

### Tier 1: Critical System
```
.github/prompts/*.prompt.md          # All system prompts
.github/prompts/*-agents.md          # All agent definitions
cortex*.yaml                         # Configuration files
pyrightconfig.json                   # Type checking config
cortex_brain/tier0/**                # Governance rules
cortex_brain/tier1/**                # Acceptance criteria
```

### Tier 2: System Documentation
```
docs/0-README.md                     # Documentation entry
docs/INDEX.md                        # Documentation index
docs/01-getting-started/**           # Onboarding guides
docs/02-architecture/**              # Architecture docs
```

### Tier 3: Git & CI/CD
```
.gitignore                           # Git configuration
.github/**                           # GitHub workflows
.git/**                              # Git repository
```

---

## 🔧 Practical Examples

### Example 1: Clean Up Old Session Reports
```bash
# Show what would be archived (dry-run)
cortex-vacuum /vacuum-sessions --dry-run

# Expected output:
Files to Archive (older than 30 days):
├─ _workspaces/SESSION-SUMMARY-2025-12-25.md (30 days old)
├─ _workspaces/SESSION-FINAL-REPORT-2025-12-20.md (35 days old)
└─ _workspaces/SESSION-SUMMARY-2025-12-15.md (40 days old)

Total: 3 files, 4.2 MB
Destination: _workspaces/_archive/sessions/
Safety: ✅ LOW RISK

Approve? (yes/no)
```

### Example 2: Migrate Roadmap to Docs
```bash
# Show migration plan
cortex-vacuum /vacuum-migrate --target roadmap --dry-run

# Expected output:
Migration Plan:
├─ Copy: _workspaces/roadmap/*.yaml → docs/06-roadmap/
├─ Archive: _workspaces/roadmap/ original files
└─ Update: docs/INDEX.md with new section

Total: 15 files
Safety: ✅ REVERSIBLE (git rollback available)

Approve? (yes/no)
```

### Example 3: Full System Scan
```bash
# Complete analysis
cortex-vacuum /vacuum-analyze

# Output:
📊 CORTEX Vacuum Analysis Report
=================================
Total Files Scanned: 1,247
├─ TIER 1 (System): 123 ✅ KEEP
├─ TIER 2 (Docs): 445 ✅ KEEP or EVOLVE
├─ TIER 3 (Ephemeral): 634 ⚠️ ARCHIVE/DELETE
└─ TIER 4 (Special): 45 🔄 CUSTOM

Ready to Cleanup:
├─ Session Reports (>30d): 12 files → ARCHIVE
├─ Completion Reports (>14d): 8 files → ARCHIVE
├─ Working Docs (>7d): 5 files → ARCHIVE
└─ Analysis Files (>3d): 3 files → ARCHIVE

Total Cleanup Potential: 28 files, 12.5 MB reclaimed

Run: cortex-vacuum /vacuum-full --dry-run
```

---

## 🛡️ Safety & Rollback

### Automatic Safeguards
- ✅ No deletion without backup
- ✅ No reduction of categories below minimum
- ✅ Git checkpoint before operations
- ✅ Explicit user approval for destructive ops
- ✅ Complete audit trail maintained

### Rollback Options
```bash
# View vacuum history
cortex-vacuum /vacuum-report

# Restore from backup (last 30 days)
cortex-vacuum /vacuum-rollback --date 2026-01-23

# Restore single file
cortex-vacuum /vacuum-restore --file SESSION-SUMMARY-2026-01-20.md
```

---

## 🔐 Vacuum Rules (CORE Extensions)

```yaml
CORE-030: "Vacuum manifest defines all file classifications"
CORE-031: "Never delete files matching KEEPER_PATTERNS without unanimous approval"
CORE-032: "Always create backups before destructive operations"
CORE-033: "Maintain audit trail for 90 days minimum"
CORE-034: "Archive ephemeral files instead of deleting when possible"
CORE-035: "Document all safety threshold decisions"
```

---

## 📌 Integration with Other Prompts

### With `cortex-doc.prompt.md`
- Vacuum archives obsolete documentation
- Documentation generator creates new docs
- Manifest tracks which docs are "current" vs "historical"

### With `cortex-review.prompt.md`
- Review agents can flag files for vacuum cleanup
- Vacuum can clean up outdated review reports

### With `CORTEX.prompt.md`
- All operations follow CORTEX LENS → DoR → Approval protocol
- All operations logged to audit trail (AC_START/COMPLETE)
- All operations respect CORE governance rules

---

## 🎯 Setup Instructions

### Step 1: Load Manifest
Vacuum system automatically loads `cortex-vacuum-manifest.yaml`

### Step 2: Run Analysis
```bash
cortex-vacuum /vacuum-analyze
```

### Step 3: Review Recommendations
Inspect proposed actions before executing

### Step 4: Execute with Approval
```bash
cortex-vacuum /vacuum-full --dry-run  # Preview
cortex-vacuum /vacuum-full            # Execute after approval
```

### Step 5: Verify Results
```bash
cortex-vacuum /vacuum-report
git log --oneline -10  # Check commits
```

---

## 📈 Success Metrics

After vacuum operation:
- ✅ No critical system files deleted
- ✅ Documentation organized per cortex-doc strategy
- ✅ 20-40% clutter reduction in _workspaces/
- ✅ All operations audited and reversible
- ✅ System remains fully operational
- ✅ Git history preserved for analysis

---

## 🚀 Next Steps

1. User runs: `/vacuum-analyze` to see current state
2. System shows DoR with approval gate
3. User approves: `proceed`
4. Vacuum executes with full audit trail
5. Git commits preserve changes
6. Reports show results and recovery options

