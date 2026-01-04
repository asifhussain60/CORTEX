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

### Phase 3: Plan Generation
5. **Create Folder Structure**
   ```
   cortex-brain/documents/planning/active/{plan-name}-v5/
   ├── 00-master-plan.md
   ├── context/
   ├── reports/
   ├── artifacts/
   └── tracking/
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
   - `reports/migration-report.md` (comprehensive analysis)
   - Copy context files from legacy plan

### Phase 4: Completion & Handoff
8. **Display Results**
   ```markdown
   ## 🎉 Plan Upgrade Complete
   
   **New Plan:** [00-master-plan.md](file:///.../00-master-plan.md)
   **Migration Report:** [migration-report.md](file:///.../migration-report.md)
   
   ### What Was Created
   - ✅ CORTEX-5.0 compliant master plan
   - ✅ Proper folder structure (4 subfolders)
   - ✅ REFACTOR phase with 18+ tasks
   - ✅ Visual progress tracker
   - ✅ Git checkpoint documentation
   - ✅ Migration report
   
   ### Next Steps
   1. **Review:** Open the new master plan (click link above)
   2. **Update Placeholders:** Search for `*()*` and fill in details
   3. **Verify Phases:** Ensure phase breakdown matches intent
   4. **Archive Original:** Optionally move legacy plan to `archived/`
   
   **Legacy plan preserved at:** {original_path}
   ```

9. **Offer Archive Option**
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
└── tracking/                   # Progress tracking
    └── progress-tracker.json
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
| **Subfolders** | `context/`, `reports/`, `artifacts/`, `tracking/` present | 10% | ✅ Yes |
| **Master Plan** | `00-master-plan.md` exists | 10% | ✅ Yes |
| **Progress Tracker** | Visual ASCII progress bars | 10% | ✅ Yes |
| **REFACTOR Phase** | Dedicated cleanup phase exists | 10% | ✅ Yes |
| **REFACTOR Tasks** | Minimum 18 tasks in REFACTOR phase | 10% | ✅ Yes |
| **Git Checkpoints** | Checkpoint commands documented | 10% | ✅ Yes |
| **Phase Count** | At least 3 phases defined | 10% | ⚠️ Partial |
| **Acceptance Criteria** | ACs defined and formatted | 10% | ⚠️ Partial |
| **Directory Structure** | Plan is directory (not single file) | 10% | ✅ Yes |
| **Context Files** | Context artifacts present | 10% | ℹ️ Info |

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

Copilot: [Analyzes plan]
         [Displays compliance score and issues]
         [Asks for confirmation]

User: yes

Copilot: [Generates new plan]
         [Creates all required files]
         [Displays clickable links to new plan]
         [Asks about archiving]

User: yes

Copilot: [Archives original plan]
         [Displays completion summary]
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
- ✅ Created `tracking/` subfolder
- ✅ Generated `00-master-plan.md`
- ✅ Generated `tracking/progress-tracker.json`

### Master Plan Content
- ✅ Visual progress tracker (ASCII bars)
- ✅ Phase breakdown with git checkpoints
- ✅ REFACTOR phase (18+ mandatory tasks)
- ✅ GIT_NO_PUSH_ENFORCEMENT documented
- ✅ SKULL rules section
- ✅ Acceptance criteria section
- ✅ Reference documentation section

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
└── tracking/
    └── progress-tracker.json  # ✅ Generated
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

---

## 📖 Related Documentation

- [Plan Upgrade Orchestrator (Full Docs)](../../docs/orchestrators/plan-upgrade-orchestrator.md)
- [Quick Start Guide](../../docs/orchestrators/QUICKSTART-plan-upgrade.md)
- [CORTEX-5.0 Master Plan](../../cortex-brain/documents/planning/active/CORTEX-5.0/00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md)
- [Sub-Plan 12: Production Validation Pipeline](../../cortex-brain/documents/planning/active/CORTEX-5.0/12-production-validation-pipeline/12-production-validation-pipeline.md)
- [Brain Protection Rules](../../cortex-brain/brain-protection-rules.yaml)

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
