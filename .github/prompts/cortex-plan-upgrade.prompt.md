# 🔄 CORTEX Plan Upgrade Orchestrator

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Autonomous migration of legacy plans to CORTEX-5.0 standards via GitHub Copilot Chat.

---

## 📋 Usage in GitHub Copilot Chat

```
@workspace /CORTEX Plan Upgrade: path/to/legacy-plan
```

**Examples:**
```
@workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/active/old-auth-plan/
@workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/features/legacy-feature.md
@workspace /CORTEX Plan Upgrade: temp-plans/draft-plan/
```

---

## 🤖 Orchestrator Behavior

### Phase 0: Pre-Flight System Validation (ALWAYS RUN FIRST)

**Objective:** Ensure orchestrator reflects latest CORTEX-5.0 state before upgrading user plans

**Critical:** User plans must be migrated against the CURRENT, LIVE CORTEX-5.0 template, not stale cache.

**Tasks:**

1. **Check Remote for CORTEX-5.0 Updates**
   ```powershell
   # Fetch latest remote state (no merge)
   git fetch origin CORTEX-5.0
   
   # Compare local vs remote for CORTEX-5.0 plan folder
   $remoteHash = git rev-parse origin/CORTEX-5.0:cortex-brain/documents/planning/active/CORTEX-5.0
   $localHash = git rev-parse HEAD:cortex-brain/documents/planning/active/CORTEX-5.0
   
   if ($remoteHash -ne $localHash) {
       Write-Host "🔄 CORTEX-5.0 updates detected on remote. Pulling latest..."
       git pull origin CORTEX-5.0 -- cortex-brain/documents/planning/active/CORTEX-5.0
   }
   ```

2. **Self-Enhancement Check**
   - Compare `cortex-plan-upgrade.prompt.md` against CORTEX-5.0 plan structure
   - Validate compliance checks match current CORTEX-5.0 standards
   - Verify folder structure requirements up-to-date
   - Check REFACTOR phase task count (18+ still current?)

3. **Wiring Validation**
   - **Check:** `copilot-instructions.md` references Plan Upgrade orchestrator
   - **Check:** `CORTEX.prompt.md` includes Plan Upgrade routing pattern
   - **Verify:** Pattern: `^(upgrade plan|migrate plan|plan upgrade)`
   - **Verify:** Type: 🛡️ AUTONOMOUS or 📋 GUIDED
   - **If missing:** Display warning and recommendation

4. **Implementation State Audit**
   - Scan `src/orchestrators/plan_upgrade/` for implementation status
   - Check `cortex-upgrade-plan.py` CLI wrapper exists
   - Verify test coverage: `tests/orchestrators/plan_upgrade/`
   - Document gaps between specification and implementation

**Exit Criteria:**
- ✅ CORTEX-5.0 folder synchronized with remote
- ✅ Orchestrator specification up-to-date
- ✅ Wiring validated (or warnings issued)
- ✅ Implementation gaps documented (if any)

**Output Display:**
```markdown
## 🔍 Pre-Flight Validation Complete

**CORTEX-5.0 Sync:** ✅ Up-to-date (or ⚠️ Updated from remote)
**Orchestrator Spec:** ✅ Current
**Wiring Status:**
- copilot-instructions.md: ✅ Referenced
- CORTEX.prompt.md: ⚠️ Pattern missing (recommend adding)

**Implementation Status:**
- Python orchestrator: ⚠️ Not implemented yet
- CLI wrapper: ❌ Missing
- Tests: ❌ No tests found

**Ready to proceed:** ✅ Yes (GitHub Copilot can execute manually)
```

---

### Phase 1: Analysis & Discovery
1. **Validate Input Path**
   - Check path exists and is accessible
   - Determine if directory or single file
   - Locate master plan file (00-master-plan.md or first .md)

2. **Analyze Legacy Plan Structure**
   - Scan folder structure for compliance
   - Extract plan content (title, phases, ACs, context)
   - Calculate compliance score (0-100%)
   - Identify gaps vs CORTEX-5.0 standards

3. **Display Analysis Results**
   ```markdown
   ## 🔍 Plan Analysis Complete
   
   **Plan:** {plan_name}
   **Type:** {directory|single-file}
   **Compliance Score:** {score}%
   
   ### Structure Analysis
   - Master Plan: {✅ Found | ❌ Missing}
   - Subfolders: {✅ Complete | ⚠️ Partial | ❌ Missing}
   - Phases Detected: {count}
   - Acceptance Criteria: {count}
   
   ### Compliance Issues ({count})
   - {issue 1}
   - {issue 2}
   - ...
   
   **Migration Required:** {Yes|No}
   ```

### Phase 2: User Confirmation
4. **Ask for Approval**
   ```markdown
   ## ⚠️ Upgrade Confirmation Required
   
   I will:
   1. Create new CORTEX-5.0 compliant plan in `active/{plan-name}-v5/`
   2. Generate comprehensive master plan with:
      - Visual progress tracker
      - REFACTOR phase (18+ mandatory tasks)
      - Git checkpoint documentation
      - GIT_NO_PUSH_ENFORCEMENT
   3. Copy context files to new structure
   4. Generate migration report
   
   The original plan will NOT be modified or deleted.
   
   **Proceed with upgrade?** (Reply "yes" to continue)
   ```

### Phase 3: Backup & Plan Generation

**CRITICAL:** NEVER lose existing plan content during migration.

4. **Backup Original Plan (MANDATORY)**
   ```powershell
   # Create timestamped backup
   $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
   $backupPath = "cortex-brain/documents/planning/backups/{plan-name}-pre-v5-$timestamp/"
   
   # Copy entire plan folder
   Copy-Item "{original-plan-path}" $backupPath -Recurse
   
   # Create backup metadata
   @{
       backup_date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
       original_path = "{original-plan-path}"
       backup_reason = "Pre-CORTEX-5.0 migration"
       orchestrator_version = "1.0.0"
   } | ConvertTo-Json | Out-File "$backupPath/backup-metadata.json"
   ```

5. **Create Folder Structure**
   ```
   cortex-brain/documents/planning/active/{plan-name}-v5/
   ├── 00-master-plan.md
   ├── context/
   ├── reports/
   ├── artifacts/
   ├── phases/                     # Optional but recommended
   └── tracking/
       ├── progress-tracker.json
       └── acceptance-criteria.yaml # If complex plan with >10 ACs
   ```

6. **Generate Master Plan Content**
   - Extract and preserve core requirements from legacy plan
   - Generate CORTEX-5.0 compliant sections:
     - Progress tracker (ASCII bars)
     - Phase breakdown with git checkpoints
     - REFACTOR phase (18+ tasks)
     - GIT_NO_PUSH_ENFORCEMENT section
     - SKULL rules table
     - Acceptance criteria
     - Dependencies
     - Success criteria

7. **Generate Supporting Files**
   - `tracking/progress-tracker.json` (phase tracking)
   - `tracking/acceptance-criteria.yaml` (if >10 acceptance criteria)
   - `reports/migration-report.md` (comprehensive analysis)
   - Copy context files from legacy plan
   - Create `phases/README.md` explaining optional phase breakdown

### Phase 4: Verification & Alignment

**Objective:** Ensure migrated plan preserves all original content and intent

8. **Content Verification**
   ```powershell
   # Compare phase counts
   $originalPhases = (Select-String -Path "$backupPath/*.md" -Pattern "^###?\s+Phase\s+\d+" | Measure-Object).Count
   $migratedPhases = (Select-String -Path "{plan-name}-v5/00-master-plan.md" -Pattern "^###?\s+Phase\s+\d+" | Measure-Object).Count
   
   if ($originalPhases -ne $migratedPhases) {
       Write-Warning "⚠️ Phase count mismatch: Original=$originalPhases, Migrated=$migratedPhases"
   }
   
   # Compare acceptance criteria counts
   $originalACs = (Select-String -Path "$backupPath/*.md" -Pattern "AC-\d+|^\s*\d+\.\s+" | Measure-Object).Count
   $migratedACs = (Select-String -Path "{plan-name}-v5/00-master-plan.md" -Pattern "AC-\d+|^\s*\d+\.\s+" | Measure-Object).Count
   
   if ($originalACs -ne $migratedACs) {
       Write-Warning "⚠️ AC count mismatch: Original=$originalACs, Migrated=$migratedACs"
   }
   ```

9. **Alignment Corrections**
   - If phase count mismatch: Review missing phases in original, add to migrated plan
   - If AC count mismatch: Extract missing ACs from backup, append to migrated plan
   - If task descriptions truncated: Restore full descriptions from backup
   - If context files missing: Copy from backup to new `context/` folder

10. **Final Validation**
    - Run compliance checker on migrated plan: `check-cortex-5-compliance.ps1 {plan-name}-v5/`
    - Verify all CORTEX-5.0 requirements met: 100% score
    - Cross-reference backup metadata: all files accounted for
    - Generate verification report: `reports/verification-report.md`

11. **Backup Cleanup Decision**
    ```markdown
    ## 📦 Verification Complete
    
    **Content Integrity:** ✅ PASS
    - Original phases: {count} → Migrated phases: {count}
    - Original ACs: {count} → Migrated ACs: {count}
    - Context files: {count} copied
    
    **Compliance Score:** 100% ✅
    
    **Backup Location:** `{backupPath}`
    
    The backup can now be safely deleted. However, recommend keeping for 48 hours.
    
    **Delete backup now?** (Reply "delete backup" to remove, "keep backup" to preserve)
    ```

---

### Phase 5: Completion & Handoff
12. **Display Results**
   ```markdown
   ## 🎉 Plan Upgrade Complete
   
   **New Plan:** [00-master-plan.md](file:///.../00-master-plan.md)
   **Migration Report:** [migration-report.md](file:///.../migration-report.md)
   
   ### What Was Created
   - ✅ CORTEX-5.0 compliant master plan
   - ✅ Proper folder structure (5 subfolders: context, reports, artifacts, phases, tracking)
   - ✅ REFACTOR phase with 18+ tasks
   - ✅ Visual progress tracker
   - ✅ Git checkpoint documentation
   - ✅ Progress tracker JSON
   - ✅ Acceptance criteria (inline or separate file)
   - ✅ Migration report
   
   ### Next Steps
   1. **Review:** Open the new master plan (click link above)
   2. **Update Placeholders:** Search for `*()*` and fill in details
   3. **Verify Phases:** Ensure phase breakdown matches intent
   4. **Archive Original:** Optionally move legacy plan to `archived/`
   
   **Legacy plan preserved at:** {original_path}
   ```

13. **Offer Archive Option**
   ```markdown
   ## 📦 Archive Legacy Plan?
   
   Would you like me to archive the original plan?
   
   If yes, I will:
   - Move original plan to `archived/{plan-name}-archived-{timestamp}/`
   - Create archive metadata for traceability
   - Preserve all original files
   
   **Archive now?** (Reply "yes" or "no")
   ```

---

## 🛡️ CORTEX-5.0 Standards Applied

### Mandatory Folder Structure
```
{plan-name}-v5/
├── 00-master-plan.md          # Main plan document
├── context/                    # Context artifacts
├── reports/                    # Progress reports
│   └── migration-report.md
├── artifacts/                  # Supporting files
├── phases/                     # Individual phase documents (optional but recommended)
└── tracking/                   # Progress tracking
    ├── progress-tracker.json
    └── acceptance-criteria.yaml (optional - for complex plans)
```

### Master Plan Required Sections
1. **📊 Progress Tracker**
   - ASCII progress bars per phase
   - Overall progress percentage
   - Status indicators (⏸️ Not Started, ⚡ In Progress, ✅ Complete)

2. **🎯 Strategic Context**
   - Problem statement
   - Solution approach
   - Dependencies

3. **🏗️ Phase Breakdown**
   - Minimum 5 phases recommended
   - Each phase includes:
     - Objective
     - Tasks
     - Exit criteria
     - Git checkpoint command

4. **Phase N: REFACTOR - Holistic Cleanup (18+ Tasks)**
   - Code Quality (6): Duplicates, structure, complexity, SOLID, dead code, smells
   - Documentation (4): Docstrings, comments, links, READMEs
   - Testing (3): Missing tests, brittle tests, coverage
   - Performance (3): Queries, memory leaks, response times
   - Security (2): Debug code, input sanitization

5. **✅ Success Criteria (Acceptance Criteria)**
   - Format: AC-01, AC-02, AC-03...
   - Each criterion clearly defined
   - Testable and measurable

6. **🔄 GIT_NO_PUSH_ENFORCEMENT**
   - Git commit after every phase
   - NEVER `git push` automated
   - User controls when to push
   - Checkpoint format: `cortex-phase-{number}`

7. **🛡️ SKULL Rules Enforced**
   - GIT_NO_PUSH_ENFORCEMENT
   - GIT_CHECKPOINT_PHASE_PROTECTION
   - REFACTOR_CODE_CLEANUP_ENFORCEMENT
   - DEFINITION_OF_DONE

8. **📚 Reference Documentation**
   - Links to related plans
   - Migration notes
   - Compliance scores
   - Reference to FINAL-ACCEPTANCE-CRITERIA.md (if applicable)

9. **📋 Final Acceptance Criteria** (for production-ready plans)
   - Link to external acceptance criteria file OR
   - Inline acceptance criteria section
   - Format: `acceptance-criteria.yaml` in plan folder OR
   - Reference to `../../FINAL-ACCEPTANCE-CRITERIA.md`

### Progress Tracking JSON Schema
```json
{
  "plan_id": "plan-name-v5",
  "version": "5.0",
  "created": "2026-01-04T15:30:00Z",
  "migrated_from": "original-path",
  "overall_progress": 0,
  "phases": [
    {
      "number": 0,
      "name": "Setup & Discovery",
      "status": "not_started",
      "progress": 0,
      "tasks_completed": 0,
      "tasks_total": 0,
      "started": null,
      "completed": null
    }
  ]
}
```

---

## 🔍 Compliance Checks (10 Total)

| Check | Description | Weight | Auto-Fixed |
|-------|-------------|--------|------------|
| **Subfolders** | `context/`, `reports/`, `artifacts/`, `tracking/`, `phases/` present | 9% | ✅ Yes |
| **Master Plan** | `00-master-plan.md` exists | 9% | ✅ Yes |
| **Progress Tracker** | Visual ASCII progress bars | 9% | ✅ Yes |
| **REFACTOR Phase** | Dedicated cleanup phase exists | 9% | ✅ Yes |
| **REFACTOR Tasks** | Minimum 18 tasks in REFACTOR phase | 9% | ✅ Yes |
| **Git Checkpoints** | Checkpoint commands documented | 9% | ✅ Yes |
| **Phase Count** | At least 3 phases defined | 9% | ⚠️ Partial |
| **Acceptance Criteria** | ACs defined (inline or external file) | 10% | ⚠️ Partial |
| **Final Acceptance** | Links to FINAL-ACCEPTANCE-CRITERIA.md or has acceptance-criteria.yaml | 9% | ⚠️ Partial |
| **Directory Structure** | Plan is directory (not single file) | 9% | ✅ Yes |
| **Context Files** | Context artifacts present | 9% | ℹ️ Info |

**Scoring:**
- 90-100%: ✅ Excellent
- 70-89%: ⚠️ Good (upgrade recommended)
- 50-69%: 🔶 Needs Work (upgrade required)
- 0-49%: 🚨 Non-Compliant (full migration required)

---

## 📝 Content Extraction Logic

### From Legacy Plans

**Automatic Extraction (Regex-Based):**

1. **Plan Title**
   ```regex
   ^#\s+(.+)$  # First H1 header
   ```

2. **Phases**
   ```regex
   ###?\s+Phase\s+(\d+):?\s*(.+?)(?=###?|$)
   ```

3. **Acceptance Criteria**
   ```regex
   (?:AC-(\d+)|(?:^|\n)\s*\d+\.\s+)(.+?)(?=\n|$)
   ```

4. **Progress Tracker Presence**
   ```python
   any(indicator in content for indicator in ['░', '█', 'Progress:', 'Overall Progress'])
   ```

5. **REFACTOR Phase Presence**
   ```python
   any(keyword in content for keyword in ['REFACTOR', 'Refactor', 'Cleanup'])
   ```

6. **Git Checkpoint References**
   ```python
   any(keyword in content.lower() for keyword in ['git commit', 'git checkpoint', 'cortex-phase'])
   ```

**Content Preservation:**
- Problem statement (first 400 chars from context section)
- All context files (copied to new `context/`)
- Phase descriptions (first 200 chars per phase)

---

## ⚙️ Implementation Reference

**Python Orchestrator:**
```bash
# Direct Python execution (alternative to Copilot prompt)
python cortex-upgrade-plan.py path/to/legacy-plan/ [--archive]
```

**Files:**
- `src/orchestrators/plan_upgrade/plan_upgrade_orchestrator.py`
- `cortex-upgrade-plan.py` (CLI wrapper)
- `docs/orchestrators/plan-upgrade-orchestrator.md` (full documentation)
- `docs/orchestrators/QUICKSTART-plan-upgrade.md` (quick start)

---

## 🎯 Expected Workflow

### In GitHub Copilot Chat:

```
User: @workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/active/old-auth-plan/

Copilot: [Phase 0: Pre-Flight Validation]
         [Checks remote for CORTEX-5.0 updates]
         [Validates wiring and implementation state]
         [Phase 1: Analyzes plan]
         [Displays compliance score and issues]
         [Asks for confirmation]

User: yes

Copilot: [Phase 3: Backs up original plan]
         [Generates new plan]
         [Creates all required files]
         [Phase 4: Verifies content integrity]
         [Aligns any mismatches]
         [Displays clickable links to new plan]
         [Asks about backup cleanup]

User: delete backup

Copilot: [Removes backup after verification]
         [Displays completion summary]
         [Offers to archive original plan]

User: yes

Copilot: [Archives original plan]
         [Final completion summary]
```

---

## 🚨 Error Handling

### Invalid Path
```markdown
❌ Error: Plan path not found

The path `{provided_path}` does not exist.

**Suggestions:**
- Check spelling and verify path exists
- Plans are usually in:
  - `cortex-brain/documents/planning/active/`
  - `cortex-brain/documents/planning/features/`
  - `cortex-brain/documents/planning/temp-plans/`

**Try:**
\`\`\`bash
ls cortex-brain/documents/planning/active/
\`\`\`
```

### Empty or Invalid Plan
```markdown
⚠️ Warning: Minimal content detected

The plan at `{path}` appears to have minimal content:
- Title: {title or "Not found"}
- Phases: {count}
- Acceptance Criteria: {count}

**I can still upgrade this plan, but you'll need to add substantial content after generation.**

Proceed? (Reply "yes" to continue)
```

### Permission Errors
```markdown
❌ Error: Cannot write to output directory

Permission denied when creating: `{output_path}`

**Solutions:**
1. Check file permissions: `ls -la cortex-brain/documents/planning/active/`
2. Ensure VS Code has write access to the workspace
3. Try running with appropriate permissions
```

---

## 📚 Migration Report Example

```markdown
# 📊 Plan Migration Report

**Migration Date:** 2026-01-04 15:30:45  
**Original Plan:** cortex-brain/documents/planning/active/old-auth-plan  
**New Plan:** cortex-brain/documents/planning/active/old-auth-plan-v5  
**Migrated By:** CORTEX Plan Upgrade Orchestrator v1.0.0

---

## 🎯 Migration Summary

**Compliance Score:** 45% → 100%  
**Issues Fixed:** 6  
**Migration Required:** Yes

---

## 📋 Original Plan Analysis

### Structure
- **Type:** Directory
- **Master Plan:** ✅ Found
- **Subfolders:** ❌ Incomplete (missing: reports/, artifacts/, tracking/)

### Content
- **Phases:** 2
- **Acceptance Criteria:** 0
- **Progress Tracker:** ❌ Missing
- **REFACTOR Phase:** ❌ Missing
- **Git Checkpoints:** ❌ Not Mentioned

---

## ⚠️ Compliance Issues Fixed

1. Missing subfolders: reports/, artifacts/, tracking/
2. Missing visual progress tracker
3. Missing REFACTOR phase
4. Missing git checkpoint references
5. Only 2 phases defined (recommend 5+)
6. No acceptance criteria defined

---

## ✅ CORTEX-5.0 Compliance

### Folder Structure
- ✅ Created `context/` subfolder
- ✅ Created `reports/` subfolder
- ✅ Created `artifacts/` subfolder
- ✅ Created `phases/` subfolder
- ✅ Created `tracking/` subfolder
- ✅ Generated `00-master-plan.md`
- ✅ Generated `tracking/progress-tracker.json`
- ✅ Generated `tracking/acceptance-criteria.yaml` (if >10 ACs)

### Master Plan Content
- ✅ Visual progress tracker (ASCII bars)
- ✅ Phase breakdown with git checkpoints
- ✅ REFACTOR phase (18+ mandatory tasks)
- ✅ GIT_NO_PUSH_ENFORCEMENT documented
- ✅ SKULL rules section
- ✅ Acceptance criteria section (inline or external reference)
- ✅ Final acceptance criteria (link to FINAL-ACCEPTANCE-CRITERIA.md if production plan)
- ✅ Reference documentation section
- ✅ phases/ subfolder for detailed phase docs (optional)

### Git Workflow
- ✅ Git checkpoint format: `cortex-phase-{number}`
- ✅ Commit commands documented per phase
- ✅ GIT_NO_PUSH_ENFORCEMENT enforced
- ✅ User push control instructions included

---

## 🚀 Next Steps

1. **Review Migrated Plan**
   - Open: `{new_plan_path}/00-master-plan.md`
   - Update placeholders marked with `*()*`
   - Verify phase breakdown matches intent

2. **Archive Original Plan**
   - Original plan preserved at `{original_path}`
   - Run archive command if desired

3. **Begin Execution**
   - Follow phase-by-phase execution
   - Git commit after each phase (don't push!)
   - Update progress tracker JSON

---

**Migration Status:** ✅ COMPLETE  
**New Plan Ready:** {new_plan_path}
```

---

## 🔧 Response Templates

### Success Response
```markdown
## 🎉 Plan Upgrade Complete

**New Plan:** [00-master-plan.md](file:///{absolute_path}/00-master-plan.md)  
**Migration Report:** [migration-report.md](file:///{absolute_path}/reports/migration-report.md)

### ✅ Compliance Improved

**Before:** {old_score}%  
**After:** 100% ✅

### 📁 Created Structure

\`\`\`
{plan-name}-v5/
├── 00-master-plan.md          # ✅ CORTEX-5.0 compliant
├── context/                    # ✅ Context files copied
├── reports/
│   └── migration-report.md    # ✅ Generated
├── artifacts/
├── phases/                     # ✅ Created (optional phase docs)
│   └── README.md
└── tracking/
    ├── progress-tracker.json  # ✅ Generated
    └── acceptance-criteria.yaml # ✅ Generated (if >10 ACs)
\`\`\`

### 🎯 Next Steps

1. **Review:** Click the master plan link above
2. **Update Placeholders:** Search for `*()*` in the plan
3. **Verify Phases:** Ensure breakdown matches your intent
4. **Begin Execution:** Follow phase-by-phase workflow

**Original plan preserved at:** `{original_path}`

---

**Archive the original plan?** (Reply "yes" to archive, "no" to keep)
```

### Archive Confirmation
```markdown
## 📦 Legacy Plan Archived

**Original Location:** `{original_path}`  
**Archive Location:** `{archive_path}`  
**Archive Metadata:** `{archive_path}/archive-metadata.json`

The original plan has been safely archived with timestamp and metadata for full traceability.

**To restore:**
\`\`\`bash
cp -r {archive_path} {original_path}
\`\`\`
```

---

## 🛠️ Anti-Bloat Rules

1. **Concise Analysis:** Compliance report ≤ 20 lines
2. **Clickable Links:** Always use markdown file links
3. **No Code Dumps:** Reference files, don't display full content
4. **Progressive Disclosure:** Show summary first, offer details on request
5. **Action-Oriented:** Focus on "what's next" not "what happened"
6. **Backup Transparency:** Always show backup location and verification status
7. **Alignment Focus:** If content mismatch detected, fix it (don't just warn)
8. **Pre-Flight Speed:** Remote check + wiring validation ≤ 30 seconds

---

## 📖 Related Documentation

- [Plan Upgrade Orchestrator (Full Docs)](../../docs/orchestrators/plan-upgrade-orchestrator.md)
- [Quick Start Guide](../../docs/orchestrators/QUICKSTART-plan-upgrade.md)
- [CORTEX-5.0 Master Plan](../../cortex-brain/documents/planning/active/CORTEX-5.0/00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md)
- [Sub-Plan 12: Production Validation Pipeline](../../cortex-brain/documents/planning/active/CORTEX-5.0/12-production-validation-pipeline/12-production-validation-pipeline.md)
- [Brain Protection Rules](../../cortex-brain/brain-protection-rules.yaml)
- [Wiring Configuration](../../.github/copilot-instructions.md)
- [Intent Router](../../.github/prompts/CORTEX.prompt.md)

---

## 🎓 Examples

### Example 1: Directory-Based Plan
```
@workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/active/auth-feature/

Response:
- Analyzes directory structure
- Finds 00-master-plan.md
- Copies context/ files
- Generates compliant v5 plan
```

### Example 2: Single-File Plan
```
@workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/features/payment.md

Response:
- Converts single file to directory structure
- Extracts phases and ACs
- Creates full folder structure
- Generates compliant v5 plan
```

### Example 3: Temp Plan
```
@workspace /CORTEX Plan Upgrade: cortex-brain/documents/planning/temp-plans/draft-api/

Response:
- Analyzes draft plan
- Shows low compliance score
- Generates full structure
- Moves from temp-plans/ to active/
```

---

**Anti-Bloat:** This file is ~700 lines. Max 750 lines. All details defer to full documentation.

---

**Version:** 1.0.0  
**Last Updated:** January 4, 2026  
**Maintainer:** Asif Hussain

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
