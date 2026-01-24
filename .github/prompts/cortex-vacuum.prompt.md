# CORTEX Vacuum Orchestrator - Repository Sanitization
**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** cortex-impl-map.yaml v3.0 | **Status:** 🚀 PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Vacuum
**Author:** Asif Hussain | **Phase:** Governance | **Orchestrator:** VacuumOrchestrator ✅

---
```

---

## 🎯 Purpose

**CORTEX Vacuum** intelligently cleanses the repository by:

1. **Traversing** all folders recursively (cortex/, cortex_brain/, docs/, _workspaces/, .github/)
2. **Classifying** files into categories: SYSTEM, DOCUMENTATION, INFORMATIONAL, DEPRECATED, GENERATED
3. **Deleting** obsolete informational reports and session summaries
4. **Reorganizing** useful content to canonical locations per cortex-doc.prompt.md strategy
5. **Archiving** historical artifacts to _workspaces/_archive/
6. **Preserving** system files (*.prompt.md, agents, governance YAML)
7. **Validating** integrity with audit trails and git checkpoints

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### Before EVERY Vacuum Operation:

**Step 1: Intent Classification**
```markdown
### 📋 Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `GOVERNANCE` |
| **Handler** | `VacuumOrchestrator` |
| **Confidence** | 🟢 High (90%) |
| **Scope** | `SYSTEM` |
| **Impact** | 🔴 High (destructive - deletions) |
| **Mode** | DRY_RUN (default) or EXECUTE |
| **Rules** | CORE-026 (checkpoint), CORE-027 (audit), CORE-029 (headers) |

---
**⏳ Awaiting approval to proceed...**
```

**Step 2: Wait for User Approval**

**Step 3: Execute Vacuum with Safeguards**

---

## 🚀 Quick Commands

| Command | Action |
|---------|--------|
| `/vacuum-analyze` | Scan repo, classify files, generate report |
| `/vacuum-dry-run` | Show deletions & relocations (no changes) |
| `/vacuum-execute` | Execute with git checkpoint |
| `/vacuum-status` | Show vacuum operation status |
| `/vacuum-rollback` | Restore from backup (if available) |

---

## 📁 File Classification System

### SYSTEM Files (🔒 PRESERVE)
```yaml
Patterns:
  - .github/prompts/**/*.prompt.md        # All prompt files
  - .github/agents/**/*.md                # All agent definitions
  - cortex_brain/tier0/governance/**      # Governance rules YAML
  - cortex_brain/tier1/**                 # Tier 1 acceptance criteria
  - cortex_brain/tier2/**                 # Tier 2 response templates
  - cortex_brain/tier3/knowledge/**       # Tier 3 knowledge YAMLs
  - cortex/**/*.py                        # Production code
  - requirements.txt, setup.py, etc.      # Dependency declarations

Action: ✅ PRESERVE
Reason: Core system infrastructure
```

### DOCUMENTATION Files (✨ VALIDATE & ORGANIZE)
```yaml
Patterns:
  - docs/**/*.md                          # Official documentation
  - README.md (root level only)           # Project README
  - cortex_brain/releases/**              # Release notes
  - cortex_brain/domain/**                # Domain documentation

Actions:
  1. Validate links & references
  2. Check creation source (auto-generated vs manual)
  3. Organize to proper docs/ section
  4. Archive outdated versions to docs/_archive/

Retention: 🟢 KEEP (with organization)
```

### INFORMATIONAL Files (📋 ARCHIVE or DELETE)
```yaml
Patterns:
  - _workspaces/PROJECT_COMPLETION_REPORT_*.md
  - _workspaces/SESSION-SUMMARY-*.md
  - _workspaces/SESSION-FINAL-REPORT-*.md
  - _workspaces/REMEDIATION-COMPLETION-SUMMARY.md
  - _workspaces/*CLEANUP*.md
  - _workspaces/ENHANCEMENT-COMPLETE.md
  - _workspaces/FINAL-DELIVERY-SUMMARY.md
  - _workspaces/TEST-FIXES-SUMMARY.md
  - _workspaces/UX-IMPROVEMENTS-SUMMARY.md
  - docs/GOVERNANCE_COMPLIANCE_REPORT.md
  - docs/USER_GUIDE_DoR_Approval_Workflow.md

Purpose: Progress tracking, session notes, temporary analysis
Lifespan: Session-specific or project-phase-specific
Action: ARCHIVE to _workspaces/_archive/ or DELETE (per config)

Retention: 🟡 ARCHIVE (unless flagged for docs migration)
```

### GENERATED Files (🔧 REGENERATE as NEEDED)
```yaml
Patterns:
  - **/*-COMPLETION-REPORT.md            # Auto-generated reports
  - **/*-SUMMARY.md                      # Auto-generated summaries
  - docs/08-reference/implementation-status.md
  - docs/08-reference/remediation-status.md
  - cortex_brain/state/**/*.json         # State snapshots

Action: DELETE (can be regenerated)
Reason: Stale unless actively updated by automation

Retention: ❌ DELETE
```

### DEPRECATED Files (⚠️ EVALUATE)
```yaml
Patterns:
  - docs_md/ folder                      # Forbidden location
  - cortex/.github/prompts/**            # Wrong location (use .github/prompts/)
  - Any root *.md except README.md

Action: RELOCATE or DELETE per rules

Retention: ❌ DELETE or RELOCATE
```

---

## 🎯 Vacuum Operations

### Phase 1: Analysis (DRY_RUN)
```yaml
Operation: FileClassificationAgent
Input: Repo root path
Output:
  - files_to_delete: List[str]
  - files_to_archive: List[str]
  - files_to_relocate: List[Tuple[src, dst]]
  - files_to_preserve: List[str]
  - summary: VacuumAnalysisReport

Steps:
  1. Traverse all directories recursively
  2. Classify each file using patterns
  3. Generate manifest with paths & reasons
  4. Calculate impact metrics
  5. Validate safeguards (no system files marked for deletion)
```

### Phase 2: Content Migration (INFORMATIONAL → DOCS)
```yaml
Operation: ContentRelocatorAgent
Input: files_to_relocate manifest
Output: Migration report with new locations

Strategies:
  - SESSION-SUMMARY-*.md → docs/04-guides/session-logs/ (if useful)
  - *-COMPLETION-REPORT.md → docs/06-release-notes/ (extract key insights)
  - EXECUTIVE_SUMMARY_*.md → docs/03-api-reference/ (if relevant)
  - Governance reports → docs/08-reference/governance/
  
Rules:
  - Preserve original dates in frontmatter
  - Add "Migrated from: {original_path}" header
  - Update all cross-references
  - Generate redirect entries in mkdocs.yml
```

### Phase 3: Sanitization (DELETION & ARCHIVAL)
```yaml
Operation: RepoSanitizerAgent
Input: files_to_delete, files_to_archive manifests
Output: Sanitization report with before/after stats

Steps:
  1. Create git branch for vacuum operation
  2. Backup files to _workspaces/_archive/ (optional)
  3. Delete files from working tree
  4. Update .gitignore if needed
  5. Scan for broken references
  6. Run git checkpoint CORE-026
  7. Generate audit trail AC_COMPLETE

Safeguards:
  - Dry-run mode by default (no deletions)
  - Preserves git history (deletions are tracked)
  - Creates backup manifest in _workspaces/_vacuum-backups/
  - Validates no system files deleted
  - Checks all *.prompt.md files untouched
  - Verifies all agents/*.md preserved
```

---

## 📊 Vacuum Configuration

### File Deletion Policies
```yaml
aggressive: false
  # Only delete DEPRECATED + GENERATED files
  # Preserve INFORMATIONAL for manual review

balanced: true (DEFAULT)
  # Delete GENERATED + DEPRECATED
  # Archive INFORMATIONAL to _archive/
  # Relocate useful DOCUMENTATION to docs/

conservative: false
  # Only delete DEPRECATED
  # Archive everything else
  # Require manual approval per file
```

### Directory Cleanup Strategy
```yaml
_workspaces/:
  preserve:
    - roadmap/
    - awakening-of-cortex/
    - cortex-vision/
    - docs/                    # Migrate relevant content to root docs/
    - ppt/
    - reports/
    - sts/                     # STS content (external)
    
  archive:
    - *.md (except README.md)  # Move to _archive/
    - *.md starting with SESSION-, PROJECT_, etc.
    
  structure:
    ├── _archive/
    │   ├── session-logs/      # SESSION-*.md
    │   ├── project-reports/   # PROJECT_COMPLETION_*.md
    │   ├── remediation/       # REMEDIATION-*.md
    │   └── INDEX.md           # Archive manifest

docs/:
  preserve:
    - 0-README.md
    - 01-getting-started/
    - 02-architecture/
    - 03-api-reference/
    - 04-guides/
    - 05-deployment/
    - 06-release-notes/
    - 07-troubleshooting/
    - 08-reference/
    - 09-tutorials/
    - _archive/
    
  clean:
    - Remove .md files not in above structure
    - Delete compliance reports (migrate key content to 08-reference/)
    - Archive outdated guides to _archive/

.github/:
  preserve:
    - prompts/                 # All *.prompt.md
    - agents/                  # All *.md agent files
    - workflows/
    - hooks/
    - copilot-instructions.md
    
  clean:
    - Consolidate duplicate prompts
```

---

## 🔗 Integration Points

### Vacuum Orchestrator
```python
from cortex.orchestrators.governance.vacuum_orchestrator import VacuumOrchestrator

vacuum = VacuumOrchestrator()

# Phase 1: Analyze
analysis = vacuum.analyze(
    repo_root="/Users/asifhussain/PROJECTS/CORTEX",
    dry_run=True
)

# Phase 2: Preview deletions/relocations
vacuum.preview(analysis)

# Phase 3: Execute (with checkpoint)
result = vacuum.execute(
    analysis=analysis,
    create_backup=True,
    git_checkpoint=True,
    audit_trail=True
)
```

### Content Relocator
```python
from cortex.orchestrators.governance.content_relocator import ContentRelocator

relocator = ContentRelocator()
relocations = relocator.plan_migrations(
    informational_files=analysis.files_to_relocate,
    docs_base="/Users/asifhussain/PROJECTS/CORTEX/docs"
)
```

### Repo Sanitizer
```python
from cortex.orchestrators.governance.repo_sanitizer import RepoSanitizer

sanitizer = RepoSanitizer()
result = sanitizer.execute(
    deletions=analysis.files_to_delete,
    archival=analysis.files_to_archive,
    git_checkpoint=True,
    audit_mode="AC_COMPLETE"
)
```

---

## 📋 Vacuum Operation Checklist (AC - Audit Trail)

```yaml
Pre-Execution (AC_START):
  ☐ User approval received
  ☐ Dry-run analysis complete
  ☐ No system files marked for deletion
  ☐ Git current branch clean (or stashed)
  ☐ Backup strategy confirmed
  ☐ Audit logger configured

Execution (AC_EXECUTE):
  ☐ Create feature branch: vacuum/repo-sanitization-YYYYMMDD
  ☐ Run file classification
  ☐ Execute content relocation
  ☐ Execute repo sanitization
  ☐ Verify safeguards
  ☐ Log all operations to audit trail

Post-Execution (AC_COMPLETE):
  ☐ Generate vacuum report
  ☐ Update .gitignore if needed
  ☐ Validate mkdocs site
  ☐ Create git checkpoint CORE-026
  ☐ Log AC_COMPLETE with metrics
  ☐ Ready for PR review
```

---

## 🛡️ Safeguards & Validations

### Pre-Deletion Checks
```yaml
System File Preservation:
  - Verify NO files in cortex/ marked for deletion
  - Verify NO files in cortex_brain/tier0/ marked for deletion
  - Verify ALL *.prompt.md files in preserve list
  - Verify ALL agents/*.md files in preserve list

Reference Integrity:
  - Scan for broken imports in *.py files
  - Check documentation cross-references
  - Validate mkdocs.yml references
  - Flag dangling symlinks

Git Safety:
  - Require clean working tree (or stash changes)
  - Create feature branch for vacuum operation
  - Preserve git history (deletions are tracked commits)
  - Generate rollback script from backup manifest
```

### Post-Deletion Validation
```yaml
Documentation Integrity:
  - Run mkdocs build validation
  - Check for dead links in HTML output
  - Validate all documentation TOC

Code Integrity:
  - Run Python syntax check on remaining *.py files
  - Verify no orphaned imports
  - Check YAML file syntax (cortex_brain/ rules)

Metrics:
  - Files deleted: N
  - Files archived: M
  - Files relocated: K
  - Disk space freed: X.XGB
  - Operation duration: HH:MM:SS
```

---

## 🚀 Deployment Strategy

### Stage 1: DRY-RUN (Mandatory)
```bash
# User runs dry-run first
/vacuum-analyze
/vacuum-dry-run

# Review manifest, approve
# Reply: "execute"
```

### Stage 2: EXECUTION (With Approval)
```bash
# System executes with all safeguards
1. Git checkpoint CORE-026
2. Create feature branch
3. Phase 1: Analysis
4. Phase 2: Content Migration
5. Phase 3: Sanitization
6. Generate reports
7. Ready for PR
```

### Stage 3: REVIEW & MERGE
```bash
# PR review checklist:
- Verify no system files deleted
- Spot-check relocated files
- Validate documentation updates
- Confirm git history integrity
- Merge to CORTEX branch
```

---

## 📊 Expected Cleanup Results

```yaml
Informational Files Archived:
  - ~19 session/project reports from _workspaces/
  - ~15 completion/summary files
  - ~5 governance compliance reports
  
Documentation Migrated to docs/:
  - Executive summaries → docs/06-release-notes/
  - Key insights → docs/08-reference/
  - Historical data → docs/_archive/

Disk Space Freed: ~5-8 MB
Repository Cleanliness Score: 85% → 95%
```

---

## 🔄 Post-Vacuum Maintenance

### Ongoing Cleanup
```yaml
Automation:
  - Monthly vacuum runs (DRY-RUN only)
  - Auto-archive session files older than 30 days
  - Auto-delete generated reports older than 90 days
  - Weekly broken link detection

Manual Review:
  - Quarterly review of _archive/ contents
  - Quarterly docs/ structure audit
  - Bi-annual deep cleanup

Monitoring:
  - Track repository size over time
  - Monitor documentation coverage
  - Alert on broken references
```

---

## 🚫 Never Do

- ❌ Delete files without DRY-RUN first
- ❌ Delete ANY *.prompt.md files
- ❌ Delete ANY agents/*.md files
- ❌ Delete cortex_brain/tier0/ governance files
- ❌ Execute without git checkpoint
- ❌ Skip audit trail logging
- ❌ Ignore safeguard validations
- ❌ Vacuum without user approval

---

## ✅ Exit Criteria

**Vacuum operation COMPLETE when:**
- [ ] All informational files archived/deleted
- [ ] All useful documentation relocated to docs/
- [ ] All system files preserved and validated
- [ ] Git checkpoint created (CORE-026)
- [ ] Audit trail logged (AC_START → AC_COMPLETE)
- [ ] Repository health verified
- [ ] PR ready for review
- [ ] Documentation site validates successfully
