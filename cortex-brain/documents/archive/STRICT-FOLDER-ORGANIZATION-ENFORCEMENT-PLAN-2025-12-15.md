🧠 CORTEX - Strict Folder Organization Enforcement Plan
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# Strict Folder Organization Enforcement Plan

**Date:** December 15, 2025  
**Author:** Asif Hussain  
**Status:** 🔍 DESIGN COMPLETE → 📋 READY FOR IMPLEMENTATION  
**Version:** 4.0.0 (CORTEX Architecture Only - Orchestration Integration)  
**Related:** PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md, CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md

---

## 🎯 Executive Summary

**User Requirement:** ZERO files in folder roots across ALL CORTEX operations. Everything must be organized in semantic folders with proper lifecycle management.

**Scope - CORTEX Architecture ONLY:**
1. ✅ **Planning Orchestrator** - Semantic folder organization, visual tracker, continuation prompts
2. ✅ **TDD Orchestrator** - Test reports in plan folders, coverage tracking
3. ✅ **ADO Orchestrator** - ADO work items in plan structure
4. ✅ **Maintenance Orchestrator** - System maintenance plans organized
5. ✅ **Cleanup Orchestrator** - Realignment utility for existing files
6. ✅ **Brain Tier Organization** - Folder structure for Tier 1, 2, 3 captures
7. ✅ **SKULL Governance** - New rule with test harness
8. ✅ **Copyright Headers** - All planning documents standardized

**OUT OF SCOPE (Moved to Cortex-Lens Plan):**
- ❌ Cortex-Lens v3 visualization work
- ❌ Landing page implementation
- ❌ Component extraction
- ❌ Three.js integration
- ❌ Dashboard development

**Architectural Integration:**
1. ✅ **Visual Progress Tracker** - Migrate from v2.0 (`PlanningSession.render_progress_table()`)
2. ✅ **Semantic Folder Organization** - Fix `_generate_plan_path()` in v3.1
3. ✅ **Plan Lifecycle Management** - Temp → Active → Completed workflow
4. ✅ **Universal Subfolder Structure** - context/, reports/, artifacts/, tracking/
5. ✅ **Historical Context Gathering** - Git history, AST, comments integration
6. 🆕 **Continuation Prompt System** - Session handoff mechanism in master plans
7. 🆕 **All Orchestrators Integration** - TDD, ADO, Execution, Maintenance, Cleanup
8. 🆕 **Brain Tier Organization** - Folder structure for Tier 1, 2, 3 captures
9. 🆕 **Manifest Updates** - Planning System 2.0 manifest compliance
10. 🆕 **Dashboard Metrics** - Folder organization health tracking

**SKULL Enforcement:** 
- ✅ STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule added to brain-protection-rules.yaml
- ✅ Test harness: tests/tier0/test_skull_strict_folder_organization.py
- ✅ Bulk copyright updater: src/operations/utilities/bulk_operations/copyright_updater.py

---

## 📋 Core Requirements Analysis

### User Requirements (Verbatim)

> "Even the temp planners should be created in dedicated folders. You can use a single folder to house all temp plans. Once they're converted to a full blown plan, all files (including the temp renamed as 00-) should be moved to the new planning folder."

> "There should NOT be any file in the root of a folder. I want everything neatly organized in folders. Only files that apply to all sub folders in the folder are allowed on root of folder as it pertains to all other folders in that folder."

> "Also comprehensive analysis documents created by CORTEX should be part of the plan. e.g. #file:PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md is created in the root. If CORTEX is meant to work using ONLY a planning structure (temp or intentional), they should ALL follow this folder structure."

> "When user submits a request, is there value in quickly checking existing plans to see if there was any work previously or recently done?"

> "I would like the planning system and CORTEX documentation to represent the office filing system pattern if you think there is benefit and merit to it."

> "Don't forget to add the realignment phase. Once implemented, realign ALL files folders recursively relocating them into the new structure. Deleting anything that is not needed."

### Office Filing System Pattern (Architectural Foundation)

**Physical Office Filing System:**
```
Filing Cabinet (Department)
├── Drawer (Category: HR, Finance, Projects)
│   ├── Hanging Folder (Project/Case Name)
│   │   ├── Manila Folder (Context: Background Research)
│   │   ├── Manila Folder (Reports: Status Updates)
│   │   ├── Manila Folder (Artifacts: Contracts, Forms)
│   │   └── Manila Folder (Tracking: Timeline, Checklist)
│   │   └── Documents (Individual files inside folders)
```

**CORTEX Equivalent:**
```
cortex-brain/documents/ (Filing Cabinet)
├── planning/ (Drawer: Projects)
│   ├── temp-plans/ (Section: Pending)
│   │   ├── {plan-name}/ (Hanging Folder: Specific Project)
│   │   │   ├── context/ (Manila Folder: Background)
│   │   │   ├── reports/ (Manila Folder: Status)
│   │   │   ├── artifacts/ (Manila Folder: Deliverables)
│   │   │   └── tracking/ (Manila Folder: Progress)
│   │   │       └── *.md, *.yaml, *.json (Documents)
│   ├── active/ (Section: In Progress)
│   └── completed/ (Section: Archived)
```

**Why This Pattern Works:**

1. **Universal Mental Model** - Everyone understands filing cabinets
2. **Proven at Scale** - Offices manage thousands of documents this way for decades
3. **Natural Discovery** - "Where's the auth project?" → "Check active folder" → "Look in that project's folder"
4. **Clear Lifecycle** - Pending → Active → Archived (same as office: Inbox → Active → Archive)
5. **Co-Location** - All documents for one project in one folder (same as one hanging folder contains all project materials)
6. **No Root Clutter** - Only index/schema at drawer level (same as only labels at drawer level)

**Office Filing System Rules Applied:**

| Office Rule | CORTEX Equivalent |
|-------------|-------------------|
| **All documents in folders** | No files in planning/ root |
| **One project = one hanging folder** | One plan = one {plan-name}/ folder |
| **Manila folders organize by type** | context/, reports/, artifacts/, tracking/ subfolders |
| **Label on folder, not loose** | README.md in folder, not scattered files |
| **Active vs Archive drawers** | active/ vs completed/ separation |
| **Pending tray for unprocessed** | temp-plans/ for unapproved work |

### Requirements Translation

| Requirement | Current State | Required State | Challenge |
|-------------|---------------|----------------|-----------|
| **Temp plans in dedicated folder** | `features/TEMP-PLAN-{timestamp}.md` | `temp-plans/{plan-id}/00-temp-plan.md` | ✅ Straightforward |
| **No root-level files** | Analysis docs in `reports/` | `temp-plans/{analysis-context}/reports/` | ⚠️  Routing logic |
| **Files with plan context** | Created independently | Part of plan folder structure | ⚠️  Context detection |
| **Root folder rule** | Not enforced | Only universal files (README, schemas) | ✅ Clear pattern |
| **Temp → Active lifecycle** | Manual move | Automated with file renaming | ✅ Existing workflow |
| **Visual progress tracker** | Only in v2.0 (legacy) | Migrate to v3.1 with session tracking | ⚠️  Code migration |
| **Semantic folder naming** | `features/plan_{slug}_{timestamp}.md` | `active/{feature-name-v1}/00-master-plan.md` | ✅ Straightforward |
| **Universal subfolders** | Not enforced | context/, reports/, artifacts/, tracking/ | ✅ Clear pattern |
| **Historical context** | Not integrated | Git history, AST, comments in context/ | ⚠️  Integration work |

### Architectural Issues from Holistic Review

**Planning Orchestrator v3.1 Problems:**

1. **Missing Visual Tracker (Feature Regression)**
   - **Problem:** `_generate_progress_summary()` only logs internally, users never see it
   - **Root Cause:** Visual tracker implemented in v2.0 but not migrated to v3.1
   - **Solution:** Import `PlanningSession` from `src/orchestrators/session_model.py`, use `render_progress_table()`
   - **Git History:** Commit 83b26f7e (Dec 13, 2025) implemented phase timing, token metrics, duration formatting

2. **Generic Folder Creation (SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT Violation)**
   - **Current Code:** Line 512-518 in `planning_orchestrator.py`
     ```python
     def _generate_plan_path(self, planning_context, tier):
         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
         operation_slug = planning_context.operation.lower().replace(' ', '-')[:30]
         filename = f"plan_{operation_slug}_{timestamp}.md"
         return self.project_root / "cortex-brain" / "documents" / "planning" / "features" / filename
     ```
   - **Problems:** Generic "features/" folder, timestamp naming, no subfolders, no lifecycle support
   - **Solution:** Semantic folders (`active/{feature-name-v1}/`), auto-versioning, universal subfolders

3. **No Plan Lifecycle Management**
   - **Problem:** Temp plans, master plans, sub-plans scattered across locations
   - **Solution:** Temp → Active → Completed workflow with folder moves
   - **Files:** `11-temp-planning-session.md` → `00-master-plan.md` + sub-plans

4. **No Historical Context Integration**
   - **Problem:** Git history, AST analysis, comments not gathered during planning
   - **Impact:** Security risks, business rules, expert identification missing
   - **Solution:** Create `context/` subfolder with git-history.yaml, ast-analysis.yaml, comments.yaml

5. **No Pre-Planning Discovery (New Issue)**
   - **Problem:** No check for existing/recent work before creating new plan
   - **Impact:** Duplicate plans, wasted effort, missed previous insights
   - **Solution:** Pre-planning discovery phase with semantic search

### Pre-Planning Discovery Workflow

**Question:** Should we check existing plans before creating new ones?

**Answer:** YES - High value, minimal overhead when properly implemented.

**Benefits:**
1. **Prevent Duplication** - "We already planned auth system v2, should we continue there?"
2. **Leverage Previous Work** - Reuse context, reports, artifacts from earlier attempts
3. **Continuity** - User sees we remember previous discussions
4. **Cost Savings** - Don't regenerate context already gathered

**Implementation: Discovery Phase (30-60 seconds)**

```python
def pre_planning_discovery(self, operation: str) -> Dict[str, Any]:
    """
    Check for existing/recent plans before creating new one.
    
    Office Filing System Analogy:
    Before creating new project folder, secretary checks:
    1. Active drawer (current projects)
    2. Pending tray (unapproved work)
    3. Archive drawer (recently completed - last 6 months)
    
    Returns discovery results with recommendations.
    """
    results = {
        'found_existing': False,
        'recommendations': [],
        'related_plans': []
    }
    
    # 1. Extract feature name from operation
    feature_slug = self._extract_feature_slug(operation)
    
    # 2. Search active/ folder (current work)
    active_plans = self._search_plans(
        folder="active",
        query=feature_slug,
        time_range="all"
    )
    
    if active_plans:
        results['found_existing'] = True
        results['recommendations'].append({
            'type': 'active_plan_exists',
            'message': f"Found {len(active_plans)} active plan(s) for '{feature_slug}'",
            'plans': active_plans,
            'action': 'continue_existing_or_new_version'
        })
    
    # 3. Search temp-plans/ folder (unapproved work)
    temp_plans = self._search_plans(
        folder="temp-plans",
        query=feature_slug,
        time_range="last_30_days"  # Only recent temp plans
    )
    
    if temp_plans:
        results['found_existing'] = True
        results['recommendations'].append({
            'type': 'temp_plan_exists',
            'message': f"Found {len(temp_plans)} temporary plan(s) - may need approval",
            'plans': temp_plans,
            'action': 'approve_existing_or_create_new'
        })
    
    # 4. Search completed/ folder (recently archived)
    completed_plans = self._search_plans(
        folder="completed",
        query=feature_slug,
        time_range="last_180_days"  # Last 6 months
    )
    
    if completed_plans:
        results['related_plans'].extend(completed_plans)
        results['recommendations'].append({
            'type': 'completed_plan_exists',
            'message': f"Found {len(completed_plans)} completed plan(s) - context available",
            'plans': completed_plans,
            'action': 'reuse_context_from_completed'
        })
    
    # 5. Semantic search across all plan reports/ folders
    semantic_matches = self._semantic_search_plans(
        query=operation,
        folders=["active", "temp-plans", "completed"],
        top_k=3
    )
    
    if semantic_matches:
        results['related_plans'].extend(semantic_matches)
    
    return results

def _search_plans(self, folder: str, query: str, time_range: str) -> List[Dict[str, Any]]:
    """
    Search plans in specific folder by feature name and time range.
    
    Office Filing System: Flip through hanging folders looking for project name.
    """
    plans = []
    search_path = self.project_root / "cortex-brain" / "documents" / "planning" / folder
    
    if not search_path.exists():
        return plans
    
    # Time range filtering
    cutoff_date = self._get_cutoff_date(time_range)
    
    for plan_folder in search_path.iterdir():
        if not plan_folder.is_dir():
            continue
        
        # Check if folder name matches query
        if query.lower() in plan_folder.name.lower():
            # Check modification time
            if cutoff_date and plan_folder.stat().st_mtime < cutoff_date.timestamp():
                continue  # Too old
            
            # Read master plan to get summary
            master_plan = self._find_master_plan(plan_folder)
            
            plans.append({
                'folder': str(plan_folder),
                'name': plan_folder.name,
                'last_modified': datetime.fromtimestamp(plan_folder.stat().st_mtime),
                'summary': self._extract_plan_summary(master_plan) if master_plan else "No summary",
                'has_context': (plan_folder / "context").exists(),
                'has_reports': (plan_folder / "reports").exists(),
                'has_artifacts': (plan_folder / "artifacts").exists()
            })
    
    return plans

def _semantic_search_plans(self, query: str, folders: List[str], top_k: int) -> List[Dict[str, Any]]:
    """
    Semantic search across plan reports/ for similar work.
    
    Office Filing System: Read file summaries to find related projects.
    """
    # Use Tier 2 semantic search across all reports/ folders
    from src.tier2.semantic_search import SemanticSearch
    
    search_results = []
    for folder in folders:
        folder_path = self.project_root / "cortex-brain" / "documents" / "planning" / folder
        if not folder_path.exists():
            continue
        
        # Search all reports/ subfolders
        for plan_folder in folder_path.iterdir():
            if not plan_folder.is_dir():
                continue
            
            reports_folder = plan_folder / "reports"
            if not reports_folder.exists():
                continue
            
            # Semantic search in this plan's reports
            matches = SemanticSearch.search(
                query=query,
                search_path=reports_folder,
                top_k=1  # Best match per plan
            )
            
            if matches:
                search_results.extend(matches)
    
    # Return top K overall matches
    return sorted(search_results, key=lambda x: x['score'], reverse=True)[:top_k]
```

**User Experience Flow:**

```
User: "Plan authentication system with JWT"

CORTEX: 
🔍 Checking existing plans...

Found:
✅ Active: authentication-system-v2/ (last modified: 2 days ago)
   - Has context/ (git history, AST analysis)
   - Has reports/ (2 execution reports)
   - Status: Phase 3 of 5 complete

📋 Recommendations:
1. CONTINUE EXISTING: Resume authentication-system-v2 at Phase 4
2. CREATE NEW VERSION: Start authentication-system-v3 (reuse context)
3. CREATE NEW PLAN: Start fresh authentication-jwt-v1

What would you like to do? (1/2/3)
```

**Discovery Performance:**

- File system scan: ~50-100ms (hundreds of folders)
- Semantic search: ~200-300ms (Tier 2 index)
- Total: <500ms (acceptable overhead)
- Cache: 5 minutes (subsequent requests instant)

**When to Skip Discovery:**

- User explicitly says "new plan" or "fresh start"
- Operation is generic ("help", "optimize", "cleanup")
- Discovery disabled in config (development mode)

---

## 🏗️ Proposed Folder Structure

### Complete Planning Hierarchy (Integrated Architecture)

```
cortex-brain/documents/planning/
├── README.md                                    # ✅ ALLOWED: Applies to ALL planning folders
├── planning-schema.yaml                         # ✅ ALLOWED: Universal schema
├── temp-plans/                                  # 🆕 All temporary plans
│   ├── {plan-id-1}/                            # Temporary plan folder
│   │   ├── 00-temp-plan.md                     # Temporary plan file
│   │   ├── 10-continuation-prompt.md           # Session handoff (temporary)
│   │   ├── 11-temp-planning-session.md         # User iteration (temporary)
│   │   ├── context/                            # Context artifacts (git history, AST, etc.)
│   │   │   ├── git-history.yaml                # Git blame, commits, authors
│   │   │   ├── ast-analysis.yaml               # Code structure, dependencies
│   │   │   ├── comments.yaml                   # Extracted comments, TODOs
│   │   │   └── code-graph.json                 # Dependency relationships
│   │   ├── reports/                            # Analysis documents for THIS plan
│   │   │   ├── HOLISTIC-REVIEW.md             # e.g., planning orchestrator analysis
│   │   │   └── CONTEXT-STRATEGY.md            # e.g., context gathering strategy
│   │   ├── artifacts/                          # Plan-specific artifacts
│   │   │   ├── complexity-analysis.json
│   │   │   └── extracted-styles.json
│   │   └── tracking/                           # Progress tracking (initialized on creation)
│   │       ├── progress-tracker.json           # Machine-readable state
│   │       └── phase-status.yaml               # Current phase status
│   ├── {plan-id-2}/
│   │   └── ... (same structure)
│   └── ... (more temp plans)
├── active/                                      # Active plans (approved or in-progress)
│   ├── {feature-name-v1}/                      # Semantic feature folder (auto-versioned)
│   │   ├── 00-master-plan.md                   # Master plan with VISUAL TRACKER
│   │   ├── 00-implementation-plan.md           # Implementation details
│   │   ├── 00-master-subplan.md                # Sub-plan hierarchy
│   │   ├── 01-subplan-{name}.md                # Sub-plan 1
│   │   ├── 02-subplan-{name}.md                # Sub-plan 2
│   │   ├── context/                            # Historical context (COPIED from temp-plans/)
│   │   │   ├── git-history.yaml
│   │   │   ├── ast-analysis.yaml
│   │   │   ├── comments.yaml
│   │   │   ├── code-graph.json
│   │   │   └── context-index.yaml              # Index of all context artifacts
│   │   ├── reports/                            # Execution reports + analysis
│   │   │   ├── execution-phase-1-report.md     # Generated after phase execution
│   │   │   ├── execution-phase-2-report.md
│   │   │   ├── HOLISTIC-REVIEW.md             # If related to this plan
│   │   │   └── CONTEXT-STRATEGY.md            # If related to this plan
│   │   ├── artifacts/                          # Execution artifacts
│   │   │   ├── extracted-components.json
│   │   │   └── dependency-graph.json
│   │   └── tracking/                           # Progress tracking (UPDATED during execution)
│   │       ├── progress-tracker.json           # Real-time progress (updated by PlanningSession)
│   │       ├── phase-status.yaml               # Current phase status
│   │       ├── metrics.json                    # Execution metrics (tokens, duration)
│   │       └── tdd-coverage.json               # TDD coverage per phase
│   ├── {feature-name-v2}/
│   │   └── ... (same structure)
│   └── ... (more active plans)
├── approved/                                    # Plans approved but not started (OPTIONAL)
│   └── {feature-name-v1}/
└── completed/                                   # Completed plans (archived)
    ├── {feature-name-v1}/                      # Same structure as active (preserved)
    │   └── ... (full structure preserved)
    └── ... (archived plans)
```

### Folder Lifecycle Workflow (Integrated with Visual Tracker)

```
1. CREATION (temp-plans/)
   User: "Plan authentication system"
   → Create: temp-plans/authentication-system-20251215/
   → Files: 11-temp-planning-session.md (temporary)
   → Subfolders: context/, reports/, artifacts/, tracking/
   → Initialize: tracking/progress-tracker.json (empty)
   → Visual Tracker: NOT shown (temp phase)

2. ITERATION (temp-plans/)
   User provides feedback
   → Update: 11-temp-planning-session.md (in-place edits)
   → Gather: context/git-history.yaml, context/ast-analysis.yaml
   → Visual Tracker: NOT shown (temp phase)
   
3. APPROVAL (temp-plans/ → active/)
   User: "Approved, proceed"
   → Generate: 00-master-plan.md with VISUAL TRACKER (PlanningSession.render_progress_table())
   → Create: 00-master-subplan.md
   → Create: 01-subplan-foundation.md, 02-subplan-implementation.md, etc.
   → Delete: 11-temp-planning-session.md (no longer needed)
   → Move: temp-plans/{plan-id}/ → active/{feature-name-v1}/ (entire folder)
   → Visual Tracker: EMBEDDED in 00-master-plan.md (shows phases, timing, tokens)

4. EXECUTION (active/)
   Orchestrator executes phases
   → Update: Visual tracker in 00-master-plan.md (real-time phase progress)
   → Create: reports/phase-{N}-completion.md (after each phase)
   → Update: tracking/progress-tracker.json (machine-readable)
   → Update: tracking/phase-status.yaml (current phase)
   → Update: tracking/metrics.json (tokens, duration per phase)
   → Visual Tracker: Shows completed phases with ✅, in-progress with ⏳, pending with ⏸️

5. COMPLETION (active/ → completed/)
   All phases done
   → Generate: reports/final-report.md (comprehensive summary)
   → Update: tracking/metrics.json (final stats, total tokens, total duration)
   → Move: active/{feature-name-v1}/ → completed/{feature-name-v1}/ (archive)
   → Visual Tracker: Shows 100% completion, all phases ✅
```
```

### Root Folder Rules

**✅ ALLOWED in `planning/` root:**
- `README.md` - Explains planning system for all folders
- `planning-schema.yaml` - Universal schema for all plans
- `.gitignore` - Applies to all subdirectories

**❌ PROHIBITED in `planning/` root:**
- `TEMP-PLAN-{timestamp}.md` - Must be in `temp-plans/{plan-id}/`
- `plan_{feature}_{timestamp}.md` - Must be in `active/{feature-name-v1}/`
- `HOLISTIC-REVIEW.md` - Must be in `temp-plans/{plan-id}/reports/` or `active/{feature}/reports/`
- Any plan-specific files

---

## 🔄 Continuation Prompt System (NEW)

### Purpose & Design

**Problem:** Users start plan execution in one Copilot Chat window, then need to continue in a new window (window closes, session timeout, deliberate break). Without context, new window doesn't know what to do next.

**Solution:** Continuation prompt section in `00-master-plan.md` that provides:
1. **Current State** - Which phase just completed
2. **Next Action** - Specific task to execute (NOT report on)
3. **Context Pointers** - Where to find relevant files
4. **Execution Instructions** - Clear directives for CORTEX to execute directly

### Master Plan Structure with Continuation Prompt

```markdown
# Master Plan: {Feature Name}

**Version:** 1.0  
**Created:** {date}  
**Status:** 🎯 APPROVED → ⏳ IN PROGRESS

---

## 📊 Progress Tracker

| Phase | Status | Duration | Tokens | Started | Completed |
|-------|--------|----------|--------|---------|-----------|
| 1. Foundation | ✅ DONE | 2h 15m | 12,450 | Dec 15 10:00 | Dec 15 12:15 |
| 2. Implementation | ⏳ IN PROGRESS | - | - | Dec 15 12:30 | - |
| 3. Testing | ⏸️ PENDING | - | - | - | - |
| 4. Deployment | ⏸️ PENDING | - | - | - | - |

**Overall Progress:** 25% (1/4 phases complete)

---

## 🔄 **CONTINUATION PROMPT** (Updated: Dec 15, 12:30 PM)

**STATUS:** Phase 1 (Foundation) complete. Beginning Phase 2 (Implementation).

**NEXT ACTION:** Execute Phase 2 implementation directly. DO NOT report - EXECUTE.

**CONTEXT:**
- Phase 1 completion report: `reports/execution-phase-1-report.md`
- Foundation artifacts: `artifacts/component-structure.json`
- Git context: `context/git-history.yaml`
- Sub-plan: `02-subplan-implementation.md`

**INSTRUCTIONS FOR CORTEX:**
```
You are continuing work on {feature-name-v1}. Phase 1 (Foundation) is complete.

EXECUTE Phase 2 (Implementation) directly by:
1. Read 02-subplan-implementation.md for detailed steps
2. Read reports/execution-phase-1-report.md for previous context
3. Implement components listed in artifacts/component-structure.json
4. Follow TDD workflow (RED→GREEN→REFACTOR) for all code
5. After each sub-task completion, update tracking/progress-tracker.json
6. When Phase 2 complete, update this continuation prompt for Phase 3

CRITICAL: EXECUTE the work directly. Do NOT just plan or report - write code, run tests, create files.

Start now with first task in 02-subplan-implementation.md.
```

---

## 🎯 Overview

{Feature overview text...}
```

### Continuation Prompt Update Workflow

**After Each Phase Completion:**

1. **Orchestrator Updates Continuation Prompt** in `00-master-plan.md`:
   ```python
   def update_continuation_prompt(self, plan_folder: Path, completed_phase: int, next_phase: int):
       """
       Update continuation prompt in master plan after phase completion.
       
       Args:
           plan_folder: Path to plan folder (e.g., active/authentication-system-v1/)
           completed_phase: Phase number just completed (1, 2, 3, ...)
           next_phase: Next phase number to execute (2, 3, 4, ...)
       """
       master_plan_path = plan_folder / "00-master-plan.md"
       
       # Read current master plan
       with open(master_plan_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       # Read next sub-plan for instructions
       next_subplan_path = plan_folder / f"{next_phase:02d}-subplan-*.md"
       next_subplan = self._find_subplan(plan_folder, next_phase)
       
       # Read latest execution report
       latest_report = plan_folder / f"reports/execution-phase-{completed_phase}-report.md"
       
       # Get current timestamp
       timestamp = datetime.now().strftime("%b %d, %I:%M %p")
       
       # Generate new continuation prompt
       continuation_prompt = f"""## 🔄 **CONTINUATION PROMPT** (Updated: {timestamp})

**STATUS:** Phase {completed_phase} complete. Beginning Phase {next_phase}.

**NEXT ACTION:** Execute Phase {next_phase} directly. DO NOT report - EXECUTE.

**CONTEXT:**
- Phase {completed_phase} completion report: `reports/execution-phase-{completed_phase}-report.md`
- Phase {completed_phase} artifacts: `artifacts/` (check for phase-specific files)
- Sub-plan: `{next_phase:02d}-subplan-{{name}}.md`
- Progress tracker: `tracking/progress-tracker.json`

**INSTRUCTIONS FOR CORTEX:**
```
You are continuing work on {plan_folder.name}. Phase {completed_phase} is complete.

EXECUTE Phase {next_phase} directly by:
1. Read {next_phase:02d}-subplan-{{name}}.md for detailed steps
2. Read reports/execution-phase-{completed_phase}-report.md for previous context
3. Review artifacts/ folder for deliverables from previous phases
4. Execute each task in the sub-plan sequentially
5. Follow TDD workflow (RED→GREEN→REFACTOR) for all code changes
6. Update tracking/progress-tracker.json after each sub-task
7. When Phase {next_phase} complete, generate execution report and update this prompt

CRITICAL: EXECUTE the work directly. Do NOT just plan or report.

Start now with first task in {next_phase:02d}-subplan-{{name}}.md.
```"""
       
       # Replace old continuation prompt section with new one
       updated_content = self._replace_continuation_prompt_section(content, continuation_prompt)
       
       # Write back to master plan
       with open(master_plan_path, 'w', encoding='utf-8') as f:
           f.write(updated_content)
       
       logger.info(f"Updated continuation prompt for Phase {next_phase}")
   ```

2. **Update Progress Tracker** (visual table) in same file

3. **User Experience:**
   ```
   [Phase 2 completes in Chat Window 1]
   
   User: [Closes window, opens new Copilot Chat window later]
   User: [Opens 00-master-plan.md, copies continuation prompt]
   User: [Pastes into new chat]
   
   CORTEX: [Reads context, begins Phase 3 execution directly]
   ```

### Continuation Prompt Benefits

1. **Session Recovery** - Pick up exactly where you left off
2. **Context Preservation** - All relevant file paths provided
3. **Execution Focus** - Clear instruction to execute, not plan
4. **Self-Documenting** - Master plan shows current state
5. **Handoff Protocol** - Team members can continue someone else's work

### When Continuation Prompt Updated

- ✅ After each phase completes successfully
- ✅ After each sub-plan completes (if sub-plans are sequential)
- ✅ When user explicitly requests "save progress"
- ❌ NOT updated mid-phase (wait for completion)
- ❌ NOT updated if phase fails (keep previous working state)

---

## 🔗 Orchestration System Integration (NEW)

### Current Orchestrators Requiring Integration

Based on holistic review of `src/operations/modules/orchestration/`:

1. **PlanningOrchestrator** (`planning_orchestrator.py`) - PRIMARY FOCUS
   - Lines 512-518: `_generate_plan_path()` refactor
   - Add pre-planning discovery
   - Add visual tracker migration
   - Add continuation prompt generation

2. **TDDOrchestrator** (`tdd_orchestrator.py`) - SECONDARY
   - Create test execution reports in `plan-folder/reports/`
   - Store TDD coverage in `plan-folder/tracking/tdd-coverage.json`
   - Link test results to phase tracking

3. **ADOPlanningOrchestrator** (`ado_planning_orchestrator.py`) - SECONDARY
   - Apply same folder organization as PlanningOrchestrator
   - Generate ADO work items in `artifacts/`
   - Store ADO summaries in `reports/`

4. **MaintenanceOrchestratorV3** (`maintenance_orchestrator_v3.py`) - TERTIARY
   - Create maintenance plans in `planning/system-maintenance-v{N}/`
   - Store healthcheck results in `reports/healthcheck-{timestamp}.md`
   - Track maintenance metrics in `tracking/maintenance-metrics.json`

5. **CleanupOrchestrator** (`cleanup_orchestrator.py`) - INTEGRATION TARGET
   - **RENAME TO:** `StrictFolderRealignmentOrchestrator`
   - Integrate with realignment module
   - Execute recursive folder cleanup
   - Generate cleanup reports in `planning/system-cleanup-v{N}/reports/`

6. **DocumentHygieneOrchestrator** (`document_hygiene_orchestrator.py`) - INTEGRATION TARGET
   - Enforce folder organization rules
   - Validate no files in roots
   - Report violations to `planning/document-hygiene-v{N}/reports/`

7. **RefactorCycleOrchestrator** (`refactor_cycle_orchestrator.py`) - MINOR
   - Store refactoring plans in `planning/refactoring-{feature}-v{N}/`
   - Track refactoring progress in `tracking/`

8. **VacuumOrchestrator** (`vacuum_orchestrator.py`) - MINOR
   - Store vacuum results in `planning/system-vacuum-v{N}/reports/`

### Orchestrator Integration Requirements

**Universal Requirements (ALL Orchestrators):**

```python
class BaseOrchestrator(BaseOperationModule):
    """Base class for all orchestrators with folder organization support."""
    
    def __init__(self, project_root: Path):
        super().__init__(project_root)
        self.folder_organizer = FolderOrganizationHelper(project_root)
    
    def create_plan_folder(self, plan_name: str, plan_type: str = "active") -> Path:
        """
        Create semantic plan folder with universal subfolders.
        
        Args:
            plan_name: Feature or operation name (e.g., "authentication-system")
            plan_type: "temp", "active", or "completed"
        
        Returns:
            Path to created plan folder
        """
        # Delegate to folder organizer
        return self.folder_organizer.create_plan_folder(plan_name, plan_type)
    
    def update_continuation_prompt(self, plan_folder: Path, phase_info: Dict[str, Any]):
        """Update continuation prompt in master plan."""
        return self.folder_organizer.update_continuation_prompt(plan_folder, phase_info)
    
    def generate_execution_report(self, plan_folder: Path, phase: int, results: Dict[str, Any]):
        """Generate execution report in reports/ subfolder."""
        report_path = plan_folder / "reports" / f"execution-phase-{phase}-report.md"
        # Generate report content...
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def update_progress_tracker(self, plan_folder: Path, phase: int, status: str, metrics: Dict[str, Any]):
        """Update tracking/progress-tracker.json."""
        tracker_path = plan_folder / "tracking" / "progress-tracker.json"
        # Update JSON...
```

### Brain Tier Organization (NEW)

**Tier 1 (Working Memory):**
```
cortex-brain/tier1/conversations/
├── active/                      # Current conversations (last 70)
│   ├── {conversation-id}/
│   │   ├── messages.jsonl      # Conversation messages
│   │   ├── context.yaml        # Extracted context
│   │   └── related-plans.yaml  # Links to planning folders
└── archived/                    # Older conversations (FIFO evicted)
    └── {year-month}/
        └── {conversation-id}/
```

**Tier 2 (Knowledge Graph):**
```
cortex-brain/tier2/patterns/
├── planning/                    # Planning patterns learned
│   ├── {pattern-name}/
│   │   ├── pattern-definition.yaml
│   │   ├── examples/           # Links to real plans
│   │   └── metrics.json
└── code/                        # Code patterns learned
    └── {pattern-name}/
```

**Tier 3 (Development Context):**
```
cortex-brain/tier3/project-state/
├── {project-name}/
│   ├── hotspots/               # Frequently modified files
│   │   └── hotspot-analysis.yaml
│   ├── metrics/                # Code metrics history
│   │   └── metrics-timeline.json
│   └── plans/                  # Links to planning folders
│       └── plan-references.yaml
```

### Dashboard Metrics Integration (NEW)

**Dashboard Data Collectors:**

```python
# src/operations/utilities/dashboard/folder_organization_collector.py

class FolderOrganizationMetricsCollector:
    """Collect folder organization health metrics for dashboard."""
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive folder organization metrics.
        
        Returns:
            Dict with metrics for dashboard visualization
        """
        return {
            'folder_health': {
                'root_violations': self._count_root_violations(),
                'proper_structure_percentage': self._calculate_proper_structure_percentage(),
                'plans_by_status': {
                    'temp': self._count_plans('temp-plans'),
                    'active': self._count_plans('active'),
                    'completed': self._count_plans('completed')
                },
                'subfolder_compliance': self._check_subfolder_compliance()
            },
            'plan_metrics': {
                'total_plans': self._count_all_plans(),
                'average_plan_size_mb': self._calculate_average_plan_size(),
                'plans_with_context': self._count_plans_with_context(),
                'plans_with_visual_tracker': self._count_plans_with_tracker(),
                'continuation_prompts': self._count_continuation_prompts()
            },
            'realignment_history': {
                'last_realignment': self._get_last_realignment_timestamp(),
                'files_moved': self._get_realignment_move_count(),
                'orphans_deleted': self._get_orphan_deletion_count()
            },
            'pre_planning_discovery': {
                'discovery_cache_hit_rate': self._get_discovery_cache_hit_rate(),
                'average_discovery_time_ms': self._get_average_discovery_time(),
                'plans_reused': self._count_plans_reused()
            }
        }
    
    def _count_root_violations(self) -> int:
        """Count files in root folders (should be 0)."""
        violations = 0
        for folder in [self.planning_root, self.reports_root]:
            if folder.exists():
                for item in folder.iterdir():
                    if item.is_file() and item.name not in ['README.md', '.gitignore']:
                        violations += 1
        return violations
    
    def _calculate_proper_structure_percentage(self) -> float:
        """Calculate percentage of plans with proper subfolder structure."""
        total_plans = 0
        proper_plans = 0
        
        for status_folder in ['temp-plans', 'active', 'completed']:
            folder_path = self.planning_root / status_folder
            if not folder_path.exists():
                continue
            
            for plan_folder in folder_path.iterdir():
                if not plan_folder.is_dir():
                    continue
                
                total_plans += 1
                
                # Check for required subfolders
                required = ['context', 'reports', 'artifacts', 'tracking']
                if all((plan_folder / subfolder).exists() for subfolder in required):
                    proper_plans += 1
        
        return (proper_plans / total_plans * 100) if total_plans > 0 else 100.0
```

**Dashboard Visualization:**

```yaml
# cortex-brain/dashboards/folder-organization-dashboard.yaml

dashboard:
  title: "Folder Organization Health"
  refresh_interval: 300  # 5 minutes
  
  metrics:
    - name: "Root Violations"
      type: "gauge"
      target: 0
      threshold:
        green: 0
        yellow: 1-5
        red: ">5"
      query: "folder_health.root_violations"
    
    - name: "Proper Structure"
      type: "percentage"
      target: 100
      query: "folder_health.proper_structure_percentage"
    
    - name: "Plans by Status"
      type: "bar_chart"
      query: "folder_health.plans_by_status"
    
    - name: "Pre-Planning Discovery Performance"
      type: "line_chart"
      query: "pre_planning_discovery.average_discovery_time_ms"
      threshold: 500  # Target <500ms
    
    - name: "Plans Reused (Discovery)"
      type: "counter"
      query: "pre_planning_discovery.plans_reused"
      description: "Plans continued from discovery instead of created new"
```

### Manifest Updates (NEW)

**File:** `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`

```yaml
# ADDITIONS to existing manifest

folder_organization:
  version: "3.0"
  
  structure:
    planning_root: "cortex-brain/documents/planning"
    status_folders:
      - "temp-plans"    # Temporary/unapproved plans
      - "active"        # Active/in-progress plans
      - "approved"      # Approved but not started (optional)
      - "completed"     # Archived/finished plans
    
    universal_subfolders:
      - "context"       # Historical context (git, AST, comments)
      - "reports"       # Execution reports, analysis documents
      - "artifacts"     # Generated deliverables
      - "tracking"      # Progress tracking, metrics
    
    required_files:
      temp_plan:
        - "11-temp-planning-session.md"  # Temporary planning file
      
      active_plan:
        - "00-master-plan.md"            # Master plan with visual tracker + continuation prompt
        - "00-master-subplan.md"         # Sub-plan hierarchy
        - "01-subplan-*.md"              # Phase sub-plans (1+)
      
      tracking:
        - "progress-tracker.json"        # Machine-readable state
        - "phase-status.yaml"            # Current phase
        - "metrics.json"                 # Execution metrics
  
  continuation_prompts:
    enabled: true
    location: "00-master-plan.md"
    section_marker: "## 🔄 **CONTINUATION PROMPT**"
    update_trigger: "phase_completion"
    format:
      - "STATUS: {completed_phase} done, starting {next_phase}"
      - "NEXT ACTION: Execute {next_phase} directly"
      - "CONTEXT: List of relevant files"
      - "INSTRUCTIONS: Step-by-step execution directives"
  
  pre_planning_discovery:
    enabled: true
    timeout_ms: 500
    search_folders:
      - "active"
      - "temp-plans"
      - "completed"  # Last 6 months only
    semantic_search:
      enabled: true
      top_k: 3
    cache_ttl_seconds: 300  # 5 minutes
  
  visual_tracker:
    enabled: true
    location: "00-master-plan.md"
    section_marker: "## 📊 Progress Tracker"
    update_frequency: "real_time"  # Update after each sub-task
    metrics:
      - "phase_status"
      - "duration"
      - "tokens_used"
      - "start_time"
      - "end_time"
  
  lifecycle_workflow:
    temp_to_active:
      trigger: "user_approval"
      actions:
        - "generate_master_plan"
        - "generate_subplans"
        - "move_folder"
        - "delete_temp_file"
        - "initialize_tracker"
    
    active_to_completed:
      trigger: "all_phases_complete"
      actions:
        - "generate_final_report"
        - "update_metrics"
        - "move_folder"
  
  orchestrator_integration:
    required_orchestrators:
      - name: "PlanningOrchestrator"
        integration_level: "full"
        folder_support: "required"
      
      - name: "TDDOrchestrator"
        integration_level: "reports"
        folder_support: "optional"
      
      - name: "ADOPlanningOrchestrator"
        integration_level: "full"
        folder_support: "required"
      
      - name: "MaintenanceOrchestratorV3"
        integration_level: "minimal"
        folder_support: "recommended"
    
    base_class: "BaseOrchestrator"
    required_methods:
      - "create_plan_folder(plan_name, plan_type)"
      - "update_continuation_prompt(plan_folder, phase_info)"
      - "generate_execution_report(plan_folder, phase, results)"
      - "update_progress_tracker(plan_folder, phase, status, metrics)"
  
  skull_enforcement:
    rule_id: "STRICT_FOLDER_ORGANIZATION_ENFORCEMENT"
    severity: "blocked"
    validation_frequency: "pre_commit"
  
  realignment:
    module: "src.operations.modules.realignment.strict_folder_realignment"
    config: "cortex-brain/config/realignment-config.yaml"
    schedule: "manual"  # Run on demand, not automated
    safety:
      dry_run_default: true
      backup_required: true
      orphan_deletion: false  # Explicit flag required
```

---

## 🛡️ SKULL Governance Rule

### Rule Definition

**File:** `cortex-brain/brain-protection-rules.yaml`

```yaml
- rule_id: "STRICT_FOLDER_ORGANIZATION_ENFORCEMENT"
  name: "Strict Folder Organization Enforcement"
  severity: "blocked"
  description: |
    ZERO files allowed in folder roots across ALL CORTEX operations. Every file must be in a semantic subfolder.
    
    Root Folder Rule: Only files that apply to ALL subfolders are allowed in root (README, schemas, .gitignore).
    
    Planning-Specific Rules:
    - Temporary plans → temp-plans/{plan-id}/
    - Active plans → active/{feature-name-v{version}}/
    - Analysis documents → Part of plan structure (reports/ subfolder)
    - All context, reports, artifacts, tracking in dedicated subfolders
    
    Lifecycle:
    1. Create temp plan in temp-plans/{plan-id}/00-temp-plan.md
    2. On approval: Move entire folder to active/{feature-name-v1}/
    3. Rename 00-temp-plan.md → 00-master-plan.md
    4. Generate sub-plans (01-, 02-, 03-) in same folder
    5. On completion: Move entire folder to completed/{feature-name-v1}/
  
  detection:
    combined_keywords:
      file_creation:
        - "create file"
        - "save file"
        - "write file"
        - "generate plan"
        - "create temp plan"
        - "create analysis"
      root_indicators:
        - "features/"
        - "planning/"
        - "reports/"
        - "documents/"
      prohibited_patterns:
        - "TEMP-PLAN-*.md"
        - "plan_*_*.md"
        - "*-REVIEW-*.md"
        - "*-STRATEGY-*.md"
        - "*-ANALYSIS-*.md"
    scope: ["file_operations", "plan_creation", "document_generation"]
    logic: "AND"
  
  folder_organization_rules:
    temp_plans:
      folder_pattern: "temp-plans/{plan-id}/"
      required_structure:
        - "00-temp-plan.md (mandatory)"
        - "context/ (optional, git history + AST + comments)"
        - "reports/ (optional, analysis documents)"
        - "artifacts/ (optional, plan artifacts)"
      file_naming:
        - "00-temp-plan.md (single temp plan file)"
      rationale: "All temporary plans isolated in dedicated folders, easy to find and manage"
    
    active_plans:
      folder_pattern: "active/{feature-name-v{version}}/"
      required_structure:
        - "00-master-plan.md (mandatory)"
        - "00-implementation-plan.md (optional)"
        - "00-master-subplan.md (optional)"
        - "01-subplan-*.md, 02-subplan-*.md, ... (sub-plans)"
        - "context/ (mandatory, historical context)"
        - "reports/ (mandatory, execution reports + analysis)"
        - "artifacts/ (optional, execution artifacts)"
        - "tracking/ (optional, progress tracking)"
      file_naming:
        - "00-master-plan.md (top-level plan)"
        - "01-subplan-{name}.md, 02-subplan-{name}.md, ... (sequential)"
      rationale: "Complete plan ecosystem in one semantic folder"
    
    completed_plans:
      folder_pattern: "completed/{feature-name-v{version}}/"
      required_structure: "Same as active_plans (preserved for archival)"
      rationale: "Completed plans moved to archive, structure preserved"
    
    root_folder_rule:
      allowed_files:
        - "README.md (explains system for ALL folders)"
        - "*-schema.yaml (universal schema)"
        - ".gitignore (applies to ALL subfolders)"
      prohibited_files:
        - "TEMP-PLAN-*.md"
        - "plan_*_*.md"
        - "*-REVIEW-*.md"
        - "*-STRATEGY-*.md"
        - "*-ANALYSIS-*.md"
        - "Any plan-specific files"
      rationale: "Root folder is for universal files only, not plan-specific content"
  
  lifecycle_workflow:
    - step: 1
      action: "Create temporary plan"
      location: "temp-plans/{plan-id}/00-temp-plan.md"
      details: "All analysis documents go in temp-plans/{plan-id}/reports/"
    
    - step: 2
      action: "User approval"
      location: "temp-plans/{plan-id}/ (no move yet)"
      details: "Mark plan as approved in temp-plan.md metadata"
    
    - step: 3
      action: "Convert to full plan"
      location: "Move entire folder: temp-plans/{plan-id}/ → active/{feature-name-v1}/"
      details: |
        - Rename 00-temp-plan.md → 00-master-plan.md
        - Generate sub-plans (01-, 02-, 03-) in same folder
        - Preserve context/, reports/, artifacts/ structure
    
    - step: 4
      action: "Execute plan"
      location: "active/{feature-name-v1}/"
      details: "Add execution reports to reports/, tracking to tracking/"
    
    - step: 5
      action: "Complete plan"
      location: "Move entire folder: active/{feature-name-v1}/ → completed/{feature-name-v1}/"
      details: "Archive with full structure preserved"
  
  analysis_document_routing:
    rule: "Analysis documents MUST be part of plan structure"
    examples:
      - document: "PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md"
        wrong: "cortex-brain/documents/reports/PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md"
        correct: "temp-plans/planning-system-enhancement-v1/reports/HOLISTIC-REVIEW.md"
        rationale: "Document created during planning enhancement work, belongs in plan folder"
      
      - document: "CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md"
        wrong: "cortex-brain/documents/reports/CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md"
        correct: "temp-plans/planning-system-enhancement-v1/reports/CONTEXT-STRATEGY.md"
        rationale: "Document created during planning enhancement work, belongs in plan folder"
      
      - document: "execution-phase-1-report.md"
        wrong: "cortex-brain/documents/reports/execution-phase-1-report.md"
        correct: "active/cortex-lens-v3/reports/execution-phase-1-report.md"
        rationale: "Document created during plan execution, belongs in plan folder"
    
    detection_logic: |
      IF document_created_during_planning_or_execution:
        route_to_plan_folder_reports_directory()
      ELSE IF document_is_universal_reference:
        allow_in_documents_reports_root()
      ELSE:
        block_creation_and_suggest_plan_folder()
  
  alternatives:
    - "STEP 1: Identify plan context for file creation"
    - "STEP 2: Create semantic folder: temp-plans/{plan-id}/ OR active/{feature-name-v1}/"
    - "STEP 3: Create file in appropriate subfolder (reports/, context/, artifacts/)"
    - "STEP 4: On plan approval: Move temp-plans/{plan-id}/ → active/{feature-name-v1}/"
    - "STEP 5: On plan completion: Move active/{feature-name-v1}/ → completed/{feature-name-v1}/"
  
  evidence_template: |
    Strict folder organization violation detected!
    
    Attempted File Creation: WRONG ❌
    ```
    cortex-brain/documents/reports/PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md
    ```
    
    Problems:
    - ❌ File created in root of reports/ folder
    - ❌ Not part of any plan structure
    - ❌ Difficult to discover which plan this relates to
    - ❌ No context, artifacts, or tracking co-located
    
    Required File Location: CORRECT ✅
    ```
    temp-plans/planning-system-enhancement-v1/
    ├── 00-temp-plan.md
    ├── context/
    │   ├── git-history.yaml
    │   └── ast-analysis.yaml
    ├── reports/                                 # ✅ Analysis documents HERE
    │   ├── HOLISTIC-REVIEW.md                   # ✅ Was: PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md
    │   └── CONTEXT-STRATEGY.md                  # ✅ Was: CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md
    └── artifacts/
        └── complexity-analysis.json
    ```
    
    Benefits:
    - ✅ All related files in one semantic folder
    - ✅ Easy discoverability (planning-system-enhancement-v1)
    - ✅ Context + reports + artifacts co-located
    - ✅ Clear lifecycle (temp → active → completed)
    - ✅ Zero files in root folders
    
    Root Folder Rule:
    Only files that apply to ALL subfolders are allowed in root:
    - ✅ README.md (explains planning system)
    - ✅ planning-schema.yaml (universal schema)
    - ❌ PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md (plan-specific)
  
  authoritative_sources:
    - source: "Martin Fowler - Refactoring (2018)"
      quote: "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."
      application: "Same applies to folder structures - semantic organization improves human understanding"
    
    - source: "The Pragmatic Programmer (2019)"
      quote: "Don't live with broken windows. Fix each one as soon as it is discovered."
      application: "Root folder clutter is a broken window - fix it immediately"
  
  rationale: |
    STRICT_FOLDER_ORGANIZATION_ENFORCEMENT: Zero Tolerance for Root Clutter
    
    Problem: Root folder chaos
    - Files scattered across planning/, reports/, features/
    - No semantic organization
    - Difficult to find related files
    - Poor lifecycle management
    - Context, reports, artifacts separated
    
    Solution: Strict folder hierarchy
    - temp-plans/{plan-id}/ for ALL temporary plans
    - active/{feature-name-v1}/ for ALL active plans
    - completed/{feature-name-v1}/ for ALL completed plans
    - ZERO files in root (except README, schemas)
    - Analysis documents PART OF plan structure
    
    Benefits:
    - ✅ Easy discoverability (semantic folder names)
    - ✅ Complete context (everything co-located)
    - ✅ Clear lifecycle (temp → active → completed)
    - ✅ Zero root clutter (only universal files)
    - ✅ Scalable (hundreds of plans, no chaos)

validator: "StrictFolderOrganizationValidator"
config: "cortex-brain/config/folder-organization-rules.yaml"
```

---

## 🧪 SKULL Test Harness

### Test File

**File:** `tests/unit/test_skull_strict_folder_organization.py`

```python
"""
SKULL Test: Strict Folder Organization Enforcement

Tests the STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule across all scenarios.

Author: Asif Hussain
Date: December 15, 2025
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from src.tier0.brain_protector import BrainProtector


class TestStrictFolderOrganizationSKULL:
    """Test suite for STRICT_FOLDER_ORGANIZATION_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX structure for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create structure
        planning_root = temp_dir / "cortex-brain" / "documents" / "planning"
        planning_root.mkdir(parents=True)
        
        # Create temp-plans, active, completed folders
        (planning_root / "temp-plans").mkdir()
        (planning_root / "active").mkdir()
        (planning_root / "completed").mkdir()
        
        # Create allowed root files
        (planning_root / "README.md").write_text("# Planning System")
        (planning_root / "planning-schema.yaml").write_text("schema_version: 1.0")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def brain_protector(self, temp_cortex_root):
        """Initialize BrainProtector with temp root."""
        return BrainProtector(project_root=temp_cortex_root)
    
    # ========================================
    # Test 1: Temp Plan Creation (CORRECT)
    # ========================================
    
    def test_temp_plan_in_dedicated_folder_passes(self, brain_protector, temp_cortex_root):
        """Test that temp plan in dedicated folder passes validation."""
        # Create temp plan in correct location
        plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / "TEMP-PLAN-001"
        plan_folder.mkdir(parents=True)
        plan_file = plan_folder / "00-temp-plan.md"
        plan_file.write_text("# Temporary Plan")
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(plan_file),
            context={"operation": "create temp plan"}
        )
        
        assert result['valid'], "Temp plan in dedicated folder should pass"
        assert not result.get('violations', []), "Should have no violations"
    
    # ========================================
    # Test 2: Temp Plan in Root (BLOCKED)
    # ========================================
    
    def test_temp_plan_in_root_blocked(self, brain_protector, temp_cortex_root):
        """Test that temp plan in root folder is blocked."""
        # Attempt to create temp plan in root
        plan_file = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "TEMP-PLAN-20251215.md"
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(plan_file),
            context={"operation": "create temp plan"}
        )
        
        assert not result['valid'], "Temp plan in root should be blocked"
        assert any('STRICT_FOLDER_ORGANIZATION_ENFORCEMENT' in v for v in result.get('violations', [])), \
            "Should cite STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule"
    
    # ========================================
    # Test 3: Active Plan in Semantic Folder (CORRECT)
    # ========================================
    
    def test_active_plan_in_semantic_folder_passes(self, brain_protector, temp_cortex_root):
        """Test that active plan in semantic folder passes."""
        # Create active plan in semantic folder
        plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "cortex-lens-v3"
        plan_folder.mkdir(parents=True)
        
        # Create required subfolders
        (plan_folder / "context").mkdir()
        (plan_folder / "reports").mkdir()
        (plan_folder / "artifacts").mkdir()
        (plan_folder / "tracking").mkdir()
        
        # Create master plan
        master_plan = plan_folder / "00-master-plan.md"
        master_plan.write_text("# Master Plan")
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(master_plan),
            context={"operation": "create active plan"}
        )
        
        assert result['valid'], "Active plan in semantic folder should pass"
    
    # ========================================
    # Test 4: Active Plan in Root (BLOCKED)
    # ========================================
    
    def test_active_plan_in_root_blocked(self, brain_protector, temp_cortex_root):
        """Test that active plan in root folder is blocked."""
        # Attempt to create active plan in root
        plan_file = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "plan_feature_20251215.md"
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(plan_file),
            context={"operation": "create active plan"}
        )
        
        assert not result['valid'], "Active plan in root should be blocked"
    
    # ========================================
    # Test 5: Analysis Document in Plan Folder (CORRECT)
    # ========================================
    
    def test_analysis_document_in_plan_folder_passes(self, brain_protector, temp_cortex_root):
        """Test that analysis document in plan folder passes."""
        # Create analysis document in plan reports folder
        plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / "planning-system-enhancement-v1"
        plan_folder.mkdir(parents=True)
        reports_folder = plan_folder / "reports"
        reports_folder.mkdir()
        
        analysis_doc = reports_folder / "HOLISTIC-REVIEW.md"
        analysis_doc.write_text("# Holistic Review")
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(analysis_doc),
            context={"operation": "create analysis document"}
        )
        
        assert result['valid'], "Analysis document in plan folder should pass"
    
    # ========================================
    # Test 6: Analysis Document in Reports Root (BLOCKED)
    # ========================================
    
    def test_analysis_document_in_reports_root_blocked(self, brain_protector, temp_cortex_root):
        """Test that analysis document in reports root is blocked."""
        # Create reports root
        reports_root = temp_cortex_root / "cortex-brain" / "documents" / "reports"
        reports_root.mkdir(parents=True)
        
        # Attempt to create analysis document in root
        analysis_doc = reports_root / "PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md"
        
        # Validate
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(analysis_doc),
            context={"operation": "create analysis document", "plan_context": "planning-system-enhancement"}
        )
        
        assert not result['valid'], "Analysis document in reports root should be blocked"
        assert 'reports/' in result.get('suggested_location', ''), "Should suggest plan folder location"
    
    # ========================================
    # Test 7: Root Folder Rule (Allowed Files)
    # ========================================
    
    def test_root_folder_allowed_files_pass(self, brain_protector, temp_cortex_root):
        """Test that README, schemas, .gitignore are allowed in root."""
        allowed_files = [
            "README.md",
            "planning-schema.yaml",
            ".gitignore"
        ]
        
        for filename in allowed_files:
            file_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / filename
            
            result = brain_protector.validate_file_operation(
                operation="create",
                file_path=str(file_path),
                context={"operation": f"create {filename}"}
            )
            
            assert result['valid'], f"{filename} should be allowed in root"
    
    # ========================================
    # Test 8: Lifecycle Workflow (Temp → Active)
    # ========================================
    
    def test_lifecycle_temp_to_active(self, brain_protector, temp_cortex_root):
        """Test temp plan to active plan lifecycle."""
        # Create temp plan
        temp_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / "TEMP-PLAN-001"
        temp_folder.mkdir(parents=True)
        temp_plan = temp_folder / "00-temp-plan.md"
        temp_plan.write_text("# Temp Plan")
        
        # Validate temp creation
        result1 = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(temp_plan),
            context={"operation": "create temp plan"}
        )
        assert result1['valid'], "Temp plan creation should pass"
        
        # Move to active (rename folder + file)
        active_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "active" / "feature-v1"
        temp_folder.rename(active_folder)
        master_plan = active_folder / "00-master-plan.md"
        (active_folder / "00-temp-plan.md").rename(master_plan)
        
        # Validate active plan
        result2 = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(master_plan),
            context={"operation": "convert to active plan"}
        )
        assert result2['valid'], "Active plan should pass after conversion"
    
    # ========================================
    # Test 9: Multiple Plans Coexistence
    # ========================================
    
    def test_multiple_plans_coexist(self, brain_protector, temp_cortex_root):
        """Test that multiple plans can coexist in dedicated folders."""
        # Create multiple temp plans
        for i in range(1, 4):
            plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / f"TEMP-PLAN-00{i}"
            plan_folder.mkdir(parents=True)
            plan_file = plan_folder / "00-temp-plan.md"
            plan_file.write_text(f"# Temp Plan {i}")
            
            result = brain_protector.validate_file_operation(
                operation="create",
                file_path=str(plan_file),
                context={"operation": f"create temp plan {i}"}
            )
            assert result['valid'], f"Temp plan {i} should pass"
        
        # Create multiple active plans
        for feature in ["cortex-lens-v3", "planning-system-3.0", "ado-operations"]:
            plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "active" / feature
            plan_folder.mkdir(parents=True)
            master_plan = plan_folder / "00-master-plan.md"
            master_plan.write_text(f"# {feature}")
            
            result = brain_protector.validate_file_operation(
                operation="create",
                file_path=str(master_plan),
                context={"operation": f"create active plan {feature}"}
            )
            assert result['valid'], f"Active plan {feature} should pass"
    
    # ========================================
    # Test 10: Context Detection
    # ========================================
    
    def test_context_detection_routes_correctly(self, brain_protector, temp_cortex_root):
        """Test that context detection routes files to correct plan folder."""
        # Create temp plan
        plan_folder = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / "planning-system-enhancement-v1"
        plan_folder.mkdir(parents=True)
        reports_folder = plan_folder / "reports"
        reports_folder.mkdir()
        
        # Create analysis document WITH context
        analysis_doc = reports_folder / "HOLISTIC-REVIEW.md"
        
        result = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(analysis_doc),
            context={
                "operation": "create analysis document",
                "plan_context": "planning-system-enhancement-v1",
                "document_type": "holistic_review"
            }
        )
        
        assert result['valid'], "Analysis document with context should pass"
        
        # Create analysis document WITHOUT context (should be blocked)
        reports_root = temp_cortex_root / "cortex-brain" / "documents" / "reports"
        reports_root.mkdir(parents=True)
        orphan_doc = reports_root / "ORPHAN-ANALYSIS.md"
        
        result2 = brain_protector.validate_file_operation(
            operation="create",
            file_path=str(orphan_doc),
            context={
                "operation": "create analysis document",
                "plan_context": None  # No context
            }
        )
        
        assert not result2['valid'], "Analysis document without context should be blocked"
```

### Running SKULL Tests

```bash
# Run specific SKULL test
pytest tests/unit/test_skull_strict_folder_organization.py -v

# Run with coverage
pytest tests/unit/test_skull_strict_folder_organization.py --cov=src.tier0 -v

# Run in isolation (like test_skull_discovery_only.py)
python tests/unit/test_skull_strict_folder_organization.py
```

---

## 🧹 Cleanup & Alignment Phase

### Implementation (Enhanced with Recursive Deletion)

**File:** `src/operations/modules/realignment/strict_folder_realignment.py`

```python
"""
Strict Folder Realignment Module

Enforces STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule by:
1. Detecting files in root folders (RECURSIVE traversal)
2. Inferring plan context from file content
3. Moving files to appropriate plan folders
4. Updating references in all files
5. DELETING orphaned files that don't fit new structure

Office Filing System Analogy:
When reorganizing filing cabinet, we:
1. Pull out ALL loose papers from drawer roots
2. Determine which project each belongs to
3. File in appropriate hanging folder
4. Throw away duplicates and outdated materials
5. Update any cross-references

Author: Asif Hussain
Date: December 15, 2025
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Set
import re
import shutil
import json

logger = logging.getLogger(__name__)


class StrictFolderRealignment:
    """Realigns existing files to strict folder organization with recursive traversal."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.documents_root = project_root / "cortex-brain" / "documents"
        self.planning_root = self.documents_root / "planning"
        self.reports_root = self.documents_root / "reports"
        
        self.violations_found = []
        self.moves_performed = []
        self.orphans_to_delete = []
        self.references_updated = []
    
    def execute_realignment(self, dry_run: bool = True, delete_orphans: bool = False) -> Dict[str, Any]:
        """
        Execute complete realignment with RECURSIVE traversal.
        
        Office Filing System Process:
        1. SCAN: Check every drawer, folder, and subfolder recursively
        2. IDENTIFY: Mark loose papers and misfiled documents
        3. INFER: Determine correct filing location
        4. MOVE: Relocate to proper folders
        5. UPDATE: Fix any cross-references
        6. PURGE: Delete duplicates and obsolete materials
        
        Args:
            dry_run: If True, report only (no actual moves/deletes)
            delete_orphans: If True, delete files that can't be categorized
        
        Returns:
            Dict with violations found, moves performed, orphans deleted, references updated
        """
        logger.info("="*80)
        logger.info(f"STRICT FOLDER REALIGNMENT - {'DRY RUN' if dry_run else 'LIVE EXECUTION'}")
        logger.info(f"Delete orphans: {delete_orphans}")
        logger.info("="*80)
        
        # Phase 1: RECURSIVE detection of violations
        logger.info("\n[PHASE 1] Detecting violations (RECURSIVE)...")
        self._detect_root_violations_recursive()
        
        # Phase 2: Infer plan contexts
        logger.info("\n[PHASE 2] Inferring plan contexts...")
        self._infer_plan_contexts()
        
        # Phase 3: Identify orphans (files with no clear context)
        logger.info("\n[PHASE 3] Identifying orphans...")
        self._identify_orphans()
        
        # Phase 4: Perform moves (if not dry run)
        if not dry_run:
            logger.info("\n[PHASE 4] Performing file moves...")
            self._perform_moves()
            
            # Phase 5: Update references
            logger.info("\n[PHASE 5] Updating references...")
            self._update_references()
            
            # Phase 6: Delete orphans (if enabled)
            if delete_orphans:
                logger.info("\n[PHASE 6] Deleting orphans...")
                self._delete_orphans()
        
        # Phase 7: Generate report
        logger.info("\n[PHASE 7] Generating report...")
        report = self._generate_report(dry_run, delete_orphans)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"REALIGNMENT {'DRY RUN' if dry_run else 'EXECUTION'} COMPLETE")
        logger.info(f"{'='*80}\n")
        
        return report
    
    def _detect_root_violations_recursive(self):
        """
        Detect files in root folders with RECURSIVE traversal.
        
        Office Filing System: Check EVERY drawer level, not just top level.
        We need to find loose papers at ALL levels.
        """
        logger.info("Scanning directories recursively...")
        
        # Scan planning/ root and all subdirectories
        if self.planning_root.exists():
            self._scan_directory_recursive(self.planning_root, allowed_root_files=['README.md', 'planning-schema.yaml', '.gitignore'])
        
        # Scan reports/ root and all subdirectories
        if self.reports_root.exists():
            self._scan_directory_recursive(self.reports_root, allowed_root_files=['README.md', '.gitignore'])
        
        # Scan features/ root if exists (legacy)
        features_root = self.planning_root / "features"
        if features_root.exists():
            self._scan_directory_recursive(features_root, allowed_root_files=[])
        
        logger.info(f"Found {len(self.violations_found)} violations across all directories")
    
    def _scan_directory_recursive(self, directory: Path, allowed_root_files: List[str]):
        """
        Recursively scan directory for violations.
        
        Args:
            directory: Directory to scan
            allowed_root_files: Files allowed in THIS directory root
        """
        if not directory.exists():
            return
        
        # Check files in THIS directory root
        for item in directory.iterdir():
            if item.is_file():
                if item.name not in allowed_root_files:
                    self.violations_found.append({
                        'file': item,
                        'location': str(directory.relative_to(self.project_root)),
                        'violation': 'file_in_root',
                        'depth': len(item.relative_to(self.documents_root).parts)
                    })
            elif item.is_dir():
                # Recursively scan subdirectories
                # Subdirectories should have NO files in root (except specific subfolders)
                if item.name in ['context', 'reports', 'artifacts', 'tracking']:
                    # These are content folders - files allowed
                    continue
                elif item.name in ['temp-plans', 'active', 'completed', 'approved']:
                    # These are organizational folders - recurse with empty allowed list
                    self._scan_directory_recursive(item, allowed_root_files=[])
                else:
                    # Unknown folder - scan it
                    self._scan_directory_recursive(item, allowed_root_files=[])
    
    def _identify_orphans(self):
        """
        Identify files that can't be categorized (orphans).
        
        Office Filing System: Papers we can't determine which project they belong to.
        Options:
        1. Move to "Miscellaneous" folder (system-analysis-v1)
        2. Delete if truly obsolete
        3. Ask user for guidance
        """
        for violation in self.violations_found:
            if violation.get('target_plan_type') == 'unknown':
                self.orphans_to_delete.append({
                    'file': violation['file'],
                    'reason': 'Cannot determine plan context',
                    'location': violation['location']
                })
    
    def _delete_orphans(self):
        """
        Delete orphaned files that can't be categorized.
        
        Office Filing System: Shred papers that are duplicates or obsolete.
        
        CAUTION: Only deletes files explicitly marked as orphans.
        """
        logger.info(f"Deleting {len(self.orphans_to_delete)} orphaned files...")
        
        for orphan in self.orphans_to_delete:
            file_path = orphan['file']
            try:
                # Safety check: Only delete .md files, never code or configs
                if file_path.suffix in ['.md', '.txt']:
                    logger.info(f"  DELETE: {file_path.name} (reason: {orphan['reason']})")
                    file_path.unlink()
                else:
                    logger.warning(f"  SKIP DELETE: {file_path.name} (not .md/.txt file)")
            except Exception as e:
                logger.error(f"  ERROR deleting {file_path}: {e}")
```

### Realignment Configuration

**File:** `cortex-brain/config/realignment-config.yaml`

```yaml
realignment:
  # Dry run by default (safety)
  default_dry_run: true
  
  # Delete orphans (files with no clear context)
  delete_orphans: false  # User must explicitly enable
  
  # Recursive traversal depth limit (prevent infinite loops)
  max_depth: 10
  
  # File patterns to NEVER delete (safety)
  protected_patterns:
    - "README.md"
    - "*.yaml"
    - "*.json"
    - ".gitignore"
  
  # Orphan handling
  orphan_strategy: "move_to_misc"  # Options: move_to_misc, delete, ask_user
  misc_folder: "planning/active/system-analysis-v1/"
  
  # Reference updating
  update_references: true
  reference_patterns:
    - "*.md"
    - "*.yaml"
  
  # Backup before execution
  create_backup: true
  backup_location: "cortex-brain/backups/realignment-{timestamp}/"
```

### Running Cleanup (Enhanced)

```bash
# 1. DRY RUN (report only - ALWAYS RUN FIRST)
python -m src.operations.realignment dry-run

# 2. Review dry run results
cat cortex-brain/realignment-dry-run-report.json

# 3. LIVE EXECUTION (moves files, updates references, NO deletion)
python -m src.operations.realignment execute

# 4. AGGRESSIVE MODE (moves + updates + DELETES orphans)
python -m src.operations.realignment execute --delete-orphans

# 5. Rollback if needed (restore from backup)
python -m src.operations.realignment rollback --backup-id <timestamp>
```

**Safety Measures:**

1. **Automatic Backup** - Before ANY move/delete, backup entire documents/ folder
2. **Dry Run Default** - Must explicitly pass `execute` to perform changes
3. **Protected Files** - README, schemas, configs never deleted
4. **Orphan Confirmation** - Must explicitly enable `--delete-orphans` flag
5. **Rollback Available** - Can restore from backup if issues found
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.planning_root = project_root / "cortex-brain" / "documents" / "planning"
        self.reports_root = project_root / "cortex-brain" / "documents" / "reports"
        
        self.violations_found = []
        self.moves_performed = []
    
    def execute_realignment(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute strict folder realignment.
        
        Args:
            dry_run: If True, only report violations (no moves)
        
        Returns:
            Dictionary with realignment results
        """
        logger.info("🔍 Starting strict folder realignment...")
        
        # Step 1: Detect violations
        self._detect_root_violations()
        
        # Step 2: Infer plan context
        self._infer_plan_contexts()
        
        # Step 3: Perform moves (if not dry_run)
        if not dry_run:
            self._perform_moves()
        
        # Step 4: Update references
        if not dry_run:
            self._update_references()
        
        # Step 5: Generate report
        report = self._generate_report(dry_run)
        
        logger.info(f"✅ Strict folder realignment complete (dry_run={dry_run})")
        return report
    
    def _detect_root_violations(self):
        """Detect files in root folders (prohibited)."""
        logger.info("Detecting root folder violations...")
        
        # Check planning root
        for file in self.planning_root.iterdir():
            if file.is_file() and file.name not in ["README.md", "planning-schema.yaml", ".gitignore"]:
                self.violations_found.append({
                    'file': file,
                    'location': 'planning_root',
                    'violation': 'file_in_root'
                })
        
        # Check reports root
        if self.reports_root.exists():
            for file in self.reports_root.iterdir():
                if file.is_file():
                    self.violations_found.append({
                        'file': file,
                        'location': 'reports_root',
                        'violation': 'file_in_root'
                    })
        
        # Check features root (old structure)
        features_root = self.planning_root / "features"
        if features_root.exists():
            for file in features_root.iterdir():
                if file.is_file():
                    self.violations_found.append({
                        'file': file,
                        'location': 'features_root',
                        'violation': 'file_in_root'
                    })
        
        logger.info(f"Found {len(self.violations_found)} violations")
    
    def _infer_plan_context(self, file_path: Path) -> Tuple[str, str]:
        """
        Infer plan context from file content.
        
        Returns:
            (plan_folder_name, plan_type) where plan_type is 'temp' or 'active'
        """
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"Cannot read {file_path}: {e}")
            return ("unknown-plan", "temp")
        
        # Infer from filename patterns
        filename = file_path.name.lower()
        
        # Check if it's a temp plan
        if filename.startswith("temp-plan") or "temporary" in filename:
            # Extract feature name
            match = re.search(r'temp-plan-\d+-(.+)\.md', filename)
            if match:
                feature_slug = match.group(1)
                return (f"{feature_slug}-v1", "temp")
            return ("unknown-temp-plan", "temp")
        
        # Check if it's an analysis document
        if any(keyword in filename for keyword in ["review", "strategy", "analysis", "report"]):
            # Try to infer from content
            content_lower = content.lower()
            
            # Look for feature mentions
            feature_patterns = [
                r'cortex[- ]lens',
                r'planning[- ]system',
                r'ado[- ]operations',
                r'tdd[- ]orchestrator',
                r'context[- ]gathering',
            ]
            
            for pattern in feature_patterns:
                if re.search(pattern, content_lower):
                    feature_name = re.sub(r'[- ]', '-', re.search(pattern, content_lower).group())
                    return (f"{feature_name}-v1", "temp")
            
            # Default to "system-analysis" if can't infer
            return ("system-analysis-v1", "temp")
        
        # Check if it's a regular plan
        if "plan" in filename or "master" in filename:
            # Extract feature name
            match = re.search(r'plan[_-](.+?)[_-]\d+', filename)
            if match:
                feature_slug = match.group(1).replace('_', '-')
                return (f"{feature_slug}-v1", "active")
            return ("feature-plan-v1", "active")
        
        # Default
        return ("unknown-plan-v1", "temp")
    
    def _infer_plan_contexts(self):
        """Infer plan context for each violation."""
        logger.info("Inferring plan contexts...")
        
        for violation in self.violations_found:
            plan_folder, plan_type = self._infer_plan_context(violation['file'])
            violation['target_plan_folder'] = plan_folder
            violation['target_plan_type'] = plan_type
            
            # Determine target location
            if plan_type == "temp":
                violation['target_location'] = self.planning_root / "temp-plans" / plan_folder
            else:
                violation['target_location'] = self.planning_root / "active" / plan_folder
    
    def _perform_moves(self):
        """Perform file moves to correct locations."""
        logger.info("Performing file moves...")
        
        for violation in self.violations_found:
            source_file = violation['file']
            target_folder = violation['target_location']
            
            # Create target folder structure
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Determine subfolder based on file type
            if violation['location'] == 'reports_root':
                # Analysis documents go to reports/
                target_subfolder = target_folder / "reports"
            else:
                # Plans go to root of plan folder
                target_subfolder = target_folder
            
            target_subfolder.mkdir(parents=True, exist_ok=True)
            
            # Determine target filename
            target_filename = self._normalize_filename(source_file.name)
            target_file = target_subfolder / target_filename
            
            # Move file
            try:
                shutil.move(str(source_file), str(target_file))
                self.moves_performed.append({
                    'source': source_file,
                    'target': target_file,
                    'success': True
                })
                logger.info(f"✅ Moved: {source_file.name} → {target_file.relative_to(self.project_root)}")
            except Exception as e:
                logger.error(f"❌ Failed to move {source_file}: {e}")
                self.moves_performed.append({
                    'source': source_file,
                    'target': target_file,
                    'success': False,
                    'error': str(e)
                })
    
    def _normalize_filename(self, filename: str) -> str:
        """Normalize filename to follow conventions."""
        # Remove timestamps
        filename = re.sub(r'-\d{8}-\d{6}', '', filename)
        filename = re.sub(r'_\d{8}_\d{6}', '', filename)
        
        # Convert to lowercase with hyphens
        filename = filename.lower().replace('_', '-')
        
        # Shorten long names
        if len(filename) > 50:
            parts = filename.rsplit('.', 1)
            name = parts[0][:45]
            ext = parts[1] if len(parts) > 1 else ''
            filename = f"{name}.{ext}" if ext else name
        
        return filename
    
    def _update_references(self):
        """Update references in files that link to moved files."""
        logger.info("Updating references...")
        
        # Build reference map
        reference_map = {}
        for move in self.moves_performed:
            if move['success']:
                old_path = str(move['source'].relative_to(self.project_root))
                new_path = str(move['target'].relative_to(self.project_root))
                reference_map[old_path] = new_path
        
        # Update references in all markdown files
        for md_file in self.project_root.rglob("*.md"):
            if not md_file.is_file():
                continue
            
            try:
                content = md_file.read_text(encoding='utf-8')
                modified = False
                
                for old_path, new_path in reference_map.items():
                    if old_path in content:
                        content = content.replace(old_path, new_path)
                        modified = True
                
                if modified:
                    md_file.write_text(content, encoding='utf-8')
                    logger.info(f"✅ Updated references in {md_file.relative_to(self.project_root)}")
            
            except Exception as e:
                logger.warning(f"Failed to update references in {md_file}: {e}")
    
    def _generate_report(self, dry_run: bool) -> Dict[str, Any]:
        """Generate realignment report."""
        return {
            'success': True,
            'dry_run': dry_run,
            'violations_found': len(self.violations_found),
            'moves_performed': len([m for m in self.moves_performed if m['success']]),
            'moves_failed': len([m for m in self.moves_performed if not m['success']]),
            'violations': [
                {
                    'file': str(v['file'].relative_to(self.project_root)),
                    'location': v['location'],
                    'target': str(v['target_location'].relative_to(self.project_root))
                }
                for v in self.violations_found
            ],
            'moves': [
                {
                    'source': str(m['source'].relative_to(self.project_root)),
                    'target': str(m['target'].relative_to(self.project_root)),
                    'success': m['success']
                }
                for m in self.moves_performed
            ]
        }
```

### Running Cleanup

```bash
# Dry run (report only, no moves)
python -c "from src.operations.modules.realignment.strict_folder_realignment import StrictFolderRealignment; from pathlib import Path; r = StrictFolderRealignment(Path('.')); result = r.execute_realignment(dry_run=True); print(result)"

# Execute moves
python -c "from src.operations.modules.realignment.strict_folder_realignment import StrictFolderRealignment; from pathlib import Path; r = StrictFolderRealignment(Path('.')); result = r.execute_realignment(dry_run=False); print(result)"
```

---

## 📝 Implementation Checklist

### Phase 1: Visual Tracker Migration (Week 1 - Days 1-2)

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Changes from Holistic Review:**
1. Import `PlanningSession` from `src/orchestrators/session_model.py`
2. Replace `_generate_progress_summary()` with `PlanningSession.render_progress_table()`
3. **ADD: Pre-Planning Discovery** before creating new plan
   ```python
   def plan(self, operation: str):
       # NEW: Check for existing plans first
       discovery = self.pre_planning_discovery(operation)
       
       if discovery['found_existing']:
           # Show user what we found
           self._present_discovery_results(discovery)
           
           # Wait for user decision: continue existing, new version, or fresh start
           user_choice = self._get_user_choice(discovery)
           
           if user_choice == 'continue_existing':
               return self._load_existing_plan(discovery['recommendations'][0]['plans'][0])
           elif user_choice == 'new_version':
               # Increment version, reuse context
               return self._create_new_version(discovery['recommendations'][0]['plans'][0])
       
       # Continue with normal planning flow
       ...
   ```
4. Add session tracking initialization:
   ```python
   self.session = PlanningSession(
       session_id=str(uuid.uuid4()),
       session_type="planning",
       status=SessionStatus.IN_PROGRESS,
       started_at=datetime.now(),
       plan_title=operation
   )
   ```
5. Record phase start/end with token metrics:
   ```python
   self.session.record_phase_start("classification")
   # ... execute phase ...
   self.session.record_phase_end("classification", tokens_used=1250)
   ```
6. Render progress table in user response:
   ```python
   progress_table = self.session.render_progress_table()
   # Include in final response to user
   ```
7. Embed visual tracker in `00-master-plan.md` during plan approval

**Expected Outcome:**
- ✅ Pre-planning discovery shows existing work (30-60 sec overhead)
- ✅ Users see visual progress tracker with phase timing
- ✅ Token consumption visible per phase + total
- ✅ Duration formatting (human-readable: "2h 15m", "3m 45s")
- ✅ Sub-plan coordination checkpoints
- ✅ Real-time progress updates during execution

**Testing:**
- [ ] Unit test: `test_pre_planning_discovery()`
- [ ] Unit test: `test_visual_tracker_rendering()`
- [ ] Integration test: Create plan, verify discovery runs first
- [ ] Integration test: Verify tracker visible
- [ ] Verify tracker updates during phase execution

---

### Phase 2: Semantic Folder Organization (Week 1 - Days 3-4)

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Replace `_generate_plan_path()` (line 512-518) with code from Holistic Review:**

```python
def _generate_plan_path(self, planning_context: PlanningContext, tier: int) -> Path:
    """
    Generate semantic plan folder structure.
    
    Creates: cortex-brain/documents/planning/temp-plans/{plan-id}/ (tier 1-2)
         or: cortex-brain/documents/planning/active/{feature-name-v{version}}/ (tier 3-4)
    
    Folder naming rules (SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT):
    - Feature-based: authentication-system-v1, cortex-lens-v3, tdd-orchestrator-v2
    - Version included: v1, v2, v3
    - Lowercase with hyphens: no-spaces-or-underscores
    """
    # Extract feature name from operation
    operation_slug = planning_context.operation.lower().replace(' ', '-')[:50]
    
    # Auto-detect version (check for existing folders)
    base_folder_name = operation_slug.removesuffix('-v1').removesuffix('-v2').removesuffix('-v3')
    
    if tier <= 2:
        # Lightweight/instant: temporary plan
        plan_id = f"{base_folder_name}-{datetime.now().strftime('%Y%m%d')}"
        plan_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        filename = "11-temp-planning-session.md"
    else:
        # Documented/complex: active plan
        version = self._detect_next_version(base_folder_name)
        folder_name = f"{base_folder_name}-v{version}"
        plan_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "active" / folder_name
        
        if tier == 3:
            filename = "00-master-plan.md"
        else:
            filename = "11-temp-planning-session.md"  # User iteration first
    
    # Create folder structure
    plan_folder.mkdir(parents=True, exist_ok=True)
    
    # Create universal subfolders
    (plan_folder / "context").mkdir(exist_ok=True)
    (plan_folder / "reports").mkdir(exist_ok=True)
    (plan_folder / "artifacts").mkdir(exist_ok=True)
    (plan_folder / "tracking").mkdir(exist_ok=True)
    
    # Initialize progress tracker
    tracker_path = plan_folder / "tracking" / "progress-tracker.json"
    if not tracker_path.exists():
        tracker_data = {
            "plan_id": plan_id if tier <= 2 else folder_name,
            "created_at": datetime.now().isoformat(),
            "status": "planning",
            "phases": []
        }
        with open(tracker_path, 'w', encoding='utf-8') as f:
            json.dump(tracker_data, f, indent=2)
    
    return plan_folder / filename

def _detect_next_version(self, base_folder_name: str) -> int:
    """Detect next version number for feature folder."""
    active_dir = self.project_root / "cortex-brain" / "documents" / "planning" / "active"
    if not active_dir.exists():
        return 1
    
    existing_versions = []
    for folder in active_dir.iterdir():
        if folder.is_dir() and folder.name.startswith(base_folder_name):
            version_match = folder.name.split('-v')[-1]
            if version_match.isdigit():
                existing_versions.append(int(version_match))
    
    return max(existing_versions, default=0) + 1
```

**Expected Outcome:**
- ✅ Temp plans (tier 1-2) created in `temp-plans/{plan-id}/`
- ✅ Active plans (tier 3-4) created in `active/{feature-name-v1}/`
- ✅ Auto-versioning: v1, v2, v3 based on existing folders
- ✅ Universal subfolders: context/, reports/, artifacts/, tracking/
- ✅ Progress tracker initialized automatically

**Testing:**
- [ ] Unit test: `test_semantic_folder_creation()`
- [ ] Test tier 1-2 routing to temp-plans/
- [ ] Test tier 3-4 routing to active/
- [ ] Test auto-versioning logic

---

### Phase 3: Plan Lifecycle Management + Continuation Prompts (Week 1 - Day 5)

**Add to `PlanningOrchestrator` class (from Holistic Review):**

```python
def approve_temporary_plan(self, temp_plan_path: Path) -> Dict[str, Any]:
    """
    Convert temporary plan to master + sub-plans with visual tracker + continuation prompt.
    
    Workflow:
    1. Read 11-temp-planning-session.md
    2. Parse phases and tasks
    3. Generate 00-master-plan.md with VISUAL TRACKER + CONTINUATION PROMPT
    4. Generate 01-subplan-{name}.md for each phase
    5. Delete 11-temp-planning-session.md
    6. Move temp-plans/{plan-id}/ → active/{feature-name-v1}/
    7. Initialize tracking/progress-tracker.json with session data
    8. **NEW:** Initialize continuation prompt (Phase 1 ready to execute)
    
    Args:
        temp_plan_path: Path to temporary planning session file
    
    Returns:
        Dict with generated file paths and visual tracker
    """
    folder = temp_plan_path.parent
    
    # 1. Read temporary plan
    with open(temp_plan_path, 'r', encoding='utf-8') as f:
        temp_content = f.read()
    
    # 2. Parse phases (extract from markdown sections)
    phases = self._parse_phases_from_temp_plan(temp_content)
    
    # 3. Generate master plan with visual tracker + continuation prompt
    master_plan_path = folder / "00-master-plan.md"
    master_content = self._generate_master_plan_content(phases, folder)
    with open(master_plan_path, 'w', encoding='utf-8') as f:
        f.write(master_content)
    
    # 4. Generate sub-plans
    subplan_paths = []
    for idx, phase in enumerate(phases, start=1):
        subplan_path = folder / f"{idx:02d}-subplan-{phase['name'].lower().replace(' ', '-')}.md"
        subplan_content = self._generate_subplan_content(phase, idx)
        with open(subplan_path, 'w', encoding='utf-8') as f:
            f.write(subplan_content)
        subplan_paths.append(subplan_path)
    
    # 5. Update progress tracker with session data
    tracker_path = folder / "tracking" / "progress-tracker.json"
    tracker_data = {
        "plan_id": str(uuid.uuid4()),
        "created_at": datetime.now().isoformat(),
        "approved_at": datetime.now().isoformat(),
        "status": "approved",
        "phases": [{"name": p['name'], "status": "pending"} for p in phases],
        "completed_phases": 0,
        "total_phases": len(phases),
        "started_at": None,
        "completed_at": None
    }
    with open(tracker_path, 'w', encoding='utf-8') as f:
        json.dump(tracker_data, f, indent=2)
    
    # 6. Delete temporary plan
    temp_plan_path.unlink()
    
    # 7. Determine if move needed (temp-plans/ → active/)
    if "temp-plans" in str(folder):
        # Extract feature name for active folder
        feature_name = self._extract_feature_name_from_plan(temp_content)
        version = self._detect_next_version(feature_name)
        active_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "active" / f"{feature_name}-v{version}"
        
        # Move entire folder
        shutil.move(str(folder), str(active_folder))
        folder = active_folder  # Update reference
    
    # 8. **NEW:** Initialize continuation prompt for Phase 1
    self.update_continuation_prompt(folder, completed_phase=0, next_phase=1)
    
    return {
        "approved": True,
        "master_plan": str(folder / "00-master-plan.md"),
        "subplan_count": len(phases),
        "subplan_paths": [str(p) for p in subplan_paths],
        "visual_tracker_embedded": True,
        "continuation_prompt_initialized": True,
        "message": f"Plan approved and converted. {len(phases)} sub-plans created with visual tracker and continuation prompt."
    }

def _generate_master_plan_content(self, phases: List[Dict[str, Any]], folder: Path) -> str:
    """Generate master plan content with visual tracker + continuation prompt."""
    # Use PlanningSession to render visual tracker
    session = PlanningSession(
        session_id=str(uuid.uuid4()),
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title=phases[0].get('feature_name', 'Feature Implementation')
    )
    
    for phase in phases:
        session.add_phase(phase['name'], phase.get('tasks', []))
    
    visual_tracker = session.render_progress_table()
    feature_name = phases[0].get('feature_name', 'Feature Implementation')
    
    # **NEW:** Generate initial continuation prompt placeholder
    timestamp = datetime.now().strftime("%b %d, %I:%M %p")
    continuation_prompt = f"""## 🔄 **CONTINUATION PROMPT** (Updated: {timestamp})

**STATUS:** Plan approved. Ready to begin Phase 1.

**NEXT ACTION:** Execute Phase 1 directly. DO NOT report - EXECUTE.

**CONTEXT:**
- Sub-plan: `01-subplan-{phases[0]['name'].lower().replace(' ', '-')}.md`
- Progress tracker: `tracking/progress-tracker.json`

**INSTRUCTIONS FOR CORTEX:**
You are beginning work on {folder.name}. The plan is approved.

EXECUTE Phase 1 directly by:
1. Read 01-subplan-{phases[0]['name'].lower().replace(' ', '-')}.md for detailed steps
2. Execute each task sequentially
3. Follow TDD workflow (RED→GREEN→REFACTOR)
4. Update tracking/progress-tracker.json after each sub-task
5. When Phase 1 complete, update this continuation prompt for Phase 2

CRITICAL: EXECUTE directly. Do NOT just plan or report.

Start now with first task in 01-subplan-{phases[0]['name'].lower().replace(' ', '-')}.md.
"""
    
    # Build master plan content
    content = f"""# Master Plan: {feature_name}

**Version:** 1.0  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** 🎯 APPROVED

---

## 📊 Progress Tracker

{visual_tracker}

---

{continuation_prompt}

---

## 🎯 Overview

{phases[0].get('overview', 'Feature implementation plan')}

---

## 📋 Phases

"""
    
    for idx, phase in enumerate(phases, start=1):
        content += f"""### Phase {idx}: {phase['name']}

**Sub-Plan:** [Phase {idx} Details](./{idx:02d}-subplan-{phase['name'].lower().replace(' ', '-')}.md)

**Objectives:**
{phase.get('objectives', 'TBD')}

---

"""
    
    return content
```

**Expected Outcome:**
- ✅ Temporary plan converts to master + sub-plans
- ✅ Visual tracker embedded in master plan
- ✅ **NEW:** Continuation prompt initialized (right after visual tracker)
- ✅ Progress tracker JSON initialized with session data
- ✅ Bidirectional links (master ↔ sub-plans)
- ✅ Automatic move from temp-plans/ to active/
- ✅ **NEW:** User can copy-paste continuation prompt to new Copilot Chat window

**Testing:**
- [ ] Unit test: `test_plan_approval_workflow()`
- [ ] Test visual tracker in master plan
- [ ] **NEW:** Test continuation prompt generation and placement
- [ ] Test folder move (temp-plans/ → active/)
- [ ] Test sub-plan generation

---

### Phase 4: SKULL Rule Implementation + Continuation Prompt in BaseOrchestrator (Week 1 - Day 6)

- [ ] Add `STRICT_FOLDER_ORGANIZATION_ENFORCEMENT` rule to `brain-protection-rules.yaml`
- [ ] Create SKULL test suite (`tests/unit/test_skull_strict_folder_organization.py`)
- [ ] **NEW:** Add `update_continuation_prompt()` method to `BaseOrchestrator` class
- [ ] **NEW:** Add continuation prompt tests (`test_continuation_prompt_update()`)
- [ ] Run SKULL tests and verify 100% pass rate
- [ ] Update `.github/copilot-instructions.md` with new rule reference

---

### Phase 5: Cleanup Module + Phase Completion Updates (Week 2 - Days 7-10)

- [ ] Create `src/operations/modules/realignment/strict_folder_realignment.py` with RECURSIVE traversal
- [ ] Create `cortex-brain/config/realignment-config.yaml` configuration
- [ ] Test dry-run on current codebase (RECURSIVE scan)
- [ ] Review dry-run results with team (ALL violations at ALL depths)
- [ ] Create backup before execution
- [ ] Execute cleanup phase 1: Move files (non-dry-run)
- [ ] **NEW:** After each cleanup sub-phase, update continuation prompt in master plan
- [ ] Execute cleanup phase 2: Update references
- [ ] **NEW:** Update continuation prompt for phase 2
- [ ] Execute cleanup phase 3: Delete orphans (OPTIONAL - requires explicit flag)
- [ ] **NEW:** Update continuation prompt for phase 3
- [ ] Verify all files moved correctly
- [ ] Verify references updated correctly
- [ ] Test rollback procedure (restore from backup)
- [ ] **NEW:** Test continuation prompt updates (verify prompt changes after each phase)

---

### Phase 6: Historical Context Integration + Continuation Prompt Updates (Week 2 - Days 11-12)

**Add context gathering to planning workflow:**

1. **Create Context Gathering Module** (if not exists)
   - Git history extraction: `src/operations/utilities/git_context_extractor.py`
   - AST analysis: `src/operations/utilities/ast_context_extractor.py`
   - Comment extraction: `src/operations/utilities/comment_extractor.py`

2. **Integrate into Planning Orchestrator**
   ```python
   def _gather_historical_context(self, planning_context: PlanningContext, plan_folder: Path):
       """Gather historical context during planning."""
       context_folder = plan_folder / "context"
       
       # Git history
       git_history = self._extract_git_history(planning_context)
       with open(context_folder / "git-history.yaml", 'w') as f:
           yaml.dump(git_history, f)
       
       # AST analysis
       ast_data = self._extract_ast_data(planning_context)
       with open(context_folder / "ast-analysis.yaml", 'w') as f:
           yaml.dump(ast_data, f)
       
       # Comments
       comments = self._extract_comments(planning_context)
       with open(context_folder / "comments.yaml", 'w') as f:
           yaml.dump(comments, f)
       
       # **NEW:** Update continuation prompt after context gathering
       # (If this is during initial planning, prompt says "Context gathered, ready for implementation")
   ```

3. **Call during plan creation**
   - After creating plan folder
   - Before generating master plan
   - Include in visual tracker as context phase
   - **NEW:** Update continuation prompt after context gathering complete

**Expected Outcome:**
- ✅ Git history available in context/ folder
- ✅ AST analysis for code understanding
- ✅ Comments extracted for business rules
- ✅ Security risks, expert identification integrated
- ✅ **NEW:** Continuation prompt reflects context gathering completion

**Testing:**
- [ ] Test git history extraction
- [ ] Test AST analysis generation
- [ ] Test comment extraction
- [ ] Integration test: Full context gathering workflow
- [ ] **NEW:** Test continuation prompt update after context gathering

---

### Phase 7: ADO Orchestrator Alignment + Continuation Prompts (Week 3 - Days 13-14)

- [ ] Update `ado_planning_orchestrator.py` with same patterns
- [ ] Add visual tracker support
- [ ] Apply semantic folder organization
- [ ] Implement plan lifecycle workflow
- [ ] **NEW:** Extend BaseOrchestrator in ADOPlanningOrchestrator
- [ ] **NEW:** Add continuation prompt updates after ADO work item phases
- [ ] **NEW:** Test continuation prompt with ADO workflows (User Story → Tasks → completion)
- [ ] Test ADO workflow end-to-end

---

### Phase 8: Validation Integration + Continuation Prompt Audits (Week 3 - Days 15-16)

- [ ] Create `StrictFolderOrganizationValidator` class
- [ ] Integrate with `BrainProtector`
- [ ] Add pre-commit hook for folder validation
- [ ] **NEW:** Add continuation prompt validation (ensure prompt exists in all active plans)
- [ ] **NEW:** Add continuation prompt format validation (STATUS, NEXT ACTION, CONTEXT, INSTRUCTIONS)
- [ ] Test validation on sample operations
- [ ] Document validation process
- [ ] **NEW:** Document continuation prompt validation rules

---

### Phase 9: Documentation & Rollout (Week 3 - Days 17-19)

- [ ] Update developer documentation
- [ ] Create migration guide for existing plans
- [ ] **NEW:** Create continuation prompt user guide (how to copy-paste and continue work)
- [ ] **NEW:** Add continuation prompt examples to documentation
- [ ] Train team on new folder organization
- [ ] **NEW:** Train team on continuation prompt usage
- [ ] Monitor for violations post-rollout
- [ ] **NEW:** Monitor continuation prompt usage patterns
- [ ] Gather feedback and iterate
- [ ] **NEW:** Gather feedback on continuation prompt usability

---

### Phase 10: Dashboard Integration (Week 3 - Days 20-21)

- [ ] Create `FolderOrganizationMetricsCollector` class
- [ ] Implement `collect_metrics()` method (folder health, plan metrics, realignment history)
- [ ] Implement `_count_root_violations()` method (target: 0)
- [ ] Implement `_calculate_proper_structure_percentage()` method (target: 100%)
- [ ] Create `cortex-brain/dashboards/folder-organization-dashboard.yaml`
- [ ] Add dashboard widgets:
  - [ ] Root Violations gauge (target 0, alert if >0)
  - [ ] Proper Structure percentage (target 100%)
  - [ ] Plans by Status bar chart (temp-plans, active, completed)
  - [ ] Discovery Performance line chart (search time <500ms)
  - [ ] Plans Reused counter (pre-planning discovery effectiveness)
- [ ] Test dashboard metrics collection
- [ ] Test dashboard visualization rendering
- [ ] Integrate with existing dashboard system (`src/operations/utilities/dashboard_renderer.py`)
- [ ] **NEW:** Add continuation prompt metrics to dashboard:
  - [ ] Continuation prompt update success rate (target: 100%)
  - [ ] Session recovery success rate (target: >95%)
  - [ ] Average continuation time (target: <30 seconds)

**Expected Outcome:**
- ✅ Real-time folder organization health monitoring
- ✅ Proactive violation detection (alert before issues accumulate)
- ✅ Pre-planning discovery performance tracking
- ✅ Continuation prompt effectiveness metrics

**Testing:**
- [ ] Unit test: `test_folder_organization_metrics_collection()`
- [ ] Unit test: `test_root_violations_count()`
- [ ] Integration test: Dashboard rendering with live data
- [ ] Performance test: Metrics collection <100ms

---

### Phase 11: Manifest Updates (Week 4 - Day 22)

- [ ] Open `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`
- [ ] Add `folder_organization` section (v3.0) with 8 subsections:
  - [ ] `structure`: planning_root, status_folders, universal_subfolders, required_files
  - [ ] `continuation_prompts`: enabled: true, location, section_marker, update_trigger, format
  - [ ] `pre_planning_discovery`: enabled: true, timeout_ms: 500, cache_ttl_seconds: 300
  - [ ] `visual_tracker`: enabled: true, location, update_frequency: real_time
  - [ ] `lifecycle_workflow`: temp_to_active, active_to_completed transitions
  - [ ] `orchestrator_integration`: required_orchestrators (8), base_class, required_methods
  - [ ] `skull_enforcement`: rule_id, severity: HIGH, validation_frequency: pre_commit
  - [ ] `realignment`: module, config, schedule: manual, safety_measures
- [ ] Validate manifest YAML syntax
- [ ] Test manifest parsing in orchestrators
- [ ] Document manifest changes in CHANGELOG.md
- [ ] Update orchestrator tests to validate against manifest requirements

**Expected Outcome:**
- ✅ Standardized folder organization specification across all orchestrators
- ✅ Continuation prompts documented as required feature
- ✅ Pre-planning discovery performance requirements specified
- ✅ Orchestrator integration requirements clear
- ✅ SKULL enforcement rules documented
- ✅ Realignment safety measures specified

**Testing:**
- [ ] Unit test: `test_manifest_yaml_valid()`
- [ ] Integration test: Orchestrators load and validate against manifest
- [ ] Compliance test: All 8 orchestrators meet manifest requirements

---

### Phase 12: Brain Tier Organization (Week 4 - Days 23-24)

- [ ] Create Tier 1 conversation folder structure:
  - [ ] `cortex-brain/tier1/conversations/active/`
  - [ ] `cortex-brain/tier1/conversations/archived/{year}/{month}/`
- [ ] Create Tier 2 pattern folder structure:
  - [ ] `cortex-brain/tier2/patterns/planning/` (planning patterns, complexity heuristics)
  - [ ] `cortex-brain/tier2/patterns/code/` (refactoring patterns, architecture patterns)
- [ ] Create Tier 3 project state folder structure:
  - [ ] `cortex-brain/tier3/project-state/{project-name}/hotspots/`
  - [ ] `cortex-brain/tier3/project-state/{project-name}/metrics/`
  - [ ] `cortex-brain/tier3/project-state/{project-name}/plan-references/`
- [ ] Implement linking mechanism:
  - [ ] Tier 1 conversations link to Tier 3 planning folders
  - [ ] Tier 2 patterns extracted from completed plans
  - [ ] Tier 3 project state aggregates metrics from active/completed plans
- [ ] Create README.md in each tier explaining purpose and structure
- [ ] Test tier organization with sample data
- [ ] Test cross-tier linking (conversation → plan → project state)
- [ ] Document brain tier organization in `cortex-brain/README-ORGANIZATION.md`

**Expected Outcome:**
- ✅ Tier 1 conversations separated by active/archived (with year/month)
- ✅ Tier 2 patterns extracted from planning/code work (learning)
- ✅ Tier 3 project state provides holistic view of all project work
- ✅ Links between tiers enable full context navigation
- ✅ Old conversations archived automatically (by date)

**Testing:**
- [ ] Unit test: `test_tier_folder_creation()`
- [ ] Integration test: Create conversation → link to plan → update project state
- [ ] Integration test: Archive old conversations (older than 6 months)
- [ ] Test cross-tier navigation (follow links between tiers)

- [ ] Update developer documentation
- [ ] Create migration guide for existing plans
- [ ] Train team on new folder organization
- [ ] Monitor for violations post-rollout
- [ ] Gather feedback and iterate

---

## 🎯 Success Metrics

| Metric | Target | Measurement | Source |
|--------|--------|-------------|--------|
| **Folder Organization Metrics** | | | |
| Root folder violations | 0 | File count in planning/, reports/, features/ roots (RECURSIVE) | Cleanup module |
| Plan folder compliance | 100% | % of plans in temp-plans/ or active/ | Folder scan |
| Analysis doc routing | 100% | % of analysis docs in plan folders (not reports/ root) | Document audit |
| Proper structure percentage | 100% | % of plan folders with correct subfolder structure | Dashboard metrics |
| Subfolder compliance | 100% | % of plans with context/, reports/, artifacts/, tracking/ | Folder validator |
| **Continuation Prompt Metrics** | | | |
| Continuation prompt update success rate | 100% | % of phase completions that update prompt | Orchestrator logs |
| Session recovery success rate | >95% | % of session handoffs that continue correctly | User tracking |
| Copy-paste usability | >4.5/5.0 | User survey: "Prompt enables quick continuation" | Team feedback |
| Average continuation time | <30 seconds | Time from paste to execution start | Performance monitoring |
| Prompt format compliance | 100% | % of prompts with STATUS, NEXT ACTION, CONTEXT, INSTRUCTIONS | Validator |
| **Planning System Metrics** | | | |
| Visual tracker visibility | 100% | % of plans with embedded tracker | User survey |
| Context gathering coverage | 100% | % of plans with context/ folder populated | Planning metrics |
| Phase timing accuracy | >95% | Variance between estimated vs actual | PlanningSession data |
| Token tracking accuracy | 100% | All phases report token usage | Metrics validation |
| Auto-versioning success | 100% | No version conflicts | Version detection tests |
| Lifecycle workflow success | 100% | temp → active → completed with no errors | Integration tests |
| **Pre-Planning Discovery Metrics** | | | |
| Pre-planning discovery accuracy | >90% | Correctly identifies existing plans | Discovery metrics |
| Pre-planning discovery speed | <500ms | Search + semantic match time | Performance monitoring |
| Plans reused (discovery) | Increase >20% | % increase in plan reuse vs baseline | Dashboard counter |
| False positive rate | <10% | % of discovery results user rejects | User feedback |
| **Cleanup & Realignment Metrics** | | | |
| Orphan detection accuracy | >95% | Correctly identifies uncategorizable files | Manual review |
| Reference update success | 100% | All references updated correctly | Post-cleanup validation |
| Realignment dry-run accuracy | 100% | Dry-run matches actual moves | Diff analysis |
| **Orchestration Integration Metrics** | | | |
| Orchestrators with folder support | 100% (8/8) | Count of orchestrators extending BaseOrchestrator | Code analysis |
| BaseOrchestrator adoption rate | 100% | % of orchestrators using base class methods | Codebase scan |
| Folder violations by orchestrator | 0 | Violations per orchestrator (should be 0) | Validator logs |
| **Testing & Compliance Metrics** | | | |
| SKULL test pass rate | 100% | pytest test_skull_strict_folder_organization.py | CI/CD |
| Manifest compliance rate | 100% | % of orchestrators meeting manifest requirements | Compliance validator |
| Dashboard metrics accuracy | >99% | Dashboard values match actual folder state | Metrics validation |
| **User Experience Metrics** | | | |
| Developer satisfaction | >4.5/5.0 | Survey: "New folder organization improves discoverability" | Team feedback |
| Continuation prompt satisfaction | >4.5/5.0 | Survey: "Prompt makes session handoff easy" | Team feedback |
| Time to find documents | Decrease >40% | Avg time to locate planning docs vs baseline | Time tracking |

---

## 🚨 Challenges & Mitigations (Enhanced)

| Challenge | Impact | Mitigation | Owner |
|-----------|--------|------------|-------|
| **Breaking existing workflows** | HIGH | Phased rollout, dry-run cleanup first, migration guide | Architecture |
| **Feature regression (visual tracker)** | HIGH | Unit tests, integration tests, visual verification | Engineering |
| **Context detection accuracy** | MEDIUM | Manual review of inferred contexts, user can override | Planning team |
| **Reference updates** | MEDIUM | Automated reference updating, test on subset first | DevOps |
| **Developer pushback** | MEDIUM | Clear communication of benefits, train on new system | Leadership |
| **Performance impact (context gathering)** | MEDIUM | Async context gathering, caching, progress indicators | Engineering |
| **Performance impact (pre-planning discovery)** | LOW | Cache results (5 min), semantic search optimization | Engineering |
| **Version conflict edge cases** | LOW | Robust version detection, conflict resolution logic | Architecture |
| **Git history size** | LOW | Limit to recent commits (6 months), summarize older | Planning team |
| **Orphan file decisions** | MEDIUM | Manual review of dry-run, conservative deletion policy | Architecture |
| **Backup storage growth** | LOW | Automatic cleanup of backups older than 30 days | DevOps |
| **False positive discovery** | LOW | Show user ALL matches, let them decide | Planning team |

---

## 📚 Related Documents

1. **PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md** - Source of architectural requirements
   - Visual tracker implementation (PlanningSession.render_progress_table())
   - Semantic folder organization (_generate_plan_path() refactor)
   - Plan lifecycle management (approve_temporary_plan() method)
   - Git commit 83b26f7e (visual tracker history)

2. **CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md** - Context gathering strategy
   - Git history extraction (security risks, business rules)
   - AST analysis (code structure, dependencies)
   - Comment extraction (expert identification)
   - CORTEX 3.0 enhancement roadmap

3. **brain-protection-rules.yaml** - SKULL governance rules
   - SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT (lines 4300-4550)
   - STRICT_FOLDER_ORGANIZATION_ENFORCEMENT (new rule)
   - TDD_ENFORCEMENT, RED_PHASE_VALIDATION

4. **cortex-operations.yaml** - Operation routing definitions
   - planning operation (copilot_chat execution)
   - ado operation (copilot_chat execution)
   - System operations (cli_wrapper execution)

5. **src/orchestrators/session_model.py** - PlanningSession implementation
   - render_progress_table() method
   - Phase timing tracking
   - Token consumption metrics

6. **src/operations/modules/orchestration/planning_orchestrator.py** - Current v3.1 implementation
   - Needs visual tracker migration (Phase 1)
   - Needs semantic folder fix (Phase 2)
   - Needs lifecycle management (Phase 3)

---

## 🏗️ Architectural Integration Summary

This plan integrates findings from **PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md** to address root causes:

### Problems Identified in Holistic Review

1. **Feature Regression:** Visual tracker implemented in v2.0 but lost in v3.1 migration
2. **Generic Folder Creation:** Line 512-518 creates `features/plan_{slug}_{timestamp}.md`
3. **No Lifecycle Management:** Temp files, master plans, sub-plans scattered
4. **Missing Historical Context:** No git history, AST, or comment extraction

### Solutions Integrated into This Plan

| Problem | Solution | Implementation Phase |
|---------|----------|---------------------|
| Visual tracker missing | Migrate `PlanningSession.render_progress_table()` from v2.0 | Phase 1 (Days 1-2) |
| No pre-planning discovery | Add discovery phase before plan creation | Phase 1 (Days 1-2) |
| Generic folder creation | Replace `_generate_plan_path()` with semantic routing | Phase 2 (Days 3-4) |
| No lifecycle workflow | Implement `approve_temporary_plan()` method | Phase 3 (Day 5) |
| No historical context | Add git/AST/comment extraction to context/ | Phase 6 (Days 11-12) |
| Root folder violations | Recursive realignment with orphan deletion | Phase 5 (Days 8-10) |

### Code Changes Required

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Line 512-518 (CURRENT - WRONG):**
```python
def _generate_plan_path(self, planning_context, tier):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    operation_slug = planning_context.operation.lower().replace(' ', '-')[:30]
    filename = f"plan_{operation_slug}_{timestamp}.md"
    return self.project_root / "cortex-brain" / "documents" / "planning" / "features" / filename
```

**New Implementation (CORRECT - Phase 2):**
- Semantic folders: `temp-plans/{plan-id}/` or `active/{feature-name-v1}/`
- Auto-versioning: Detect existing folders, increment version
- Universal subfolders: context/, reports/, artifacts/, tracking/
- Visual tracker: Embedded in master plan
- Historical context: Populated in context/ folder

### Integration Points

1. **PlanningSession (v2.0) → Planning Orchestrator (v3.1)**
   - Import `PlanningSession` from `src/orchestrators/session_model.py`
   - Use `render_progress_table()` for visual tracking
   - Record phase timing and token consumption

2. **Folder Structure → Lifecycle Workflow**
   - temp-plans/ for lightweight planning (tier 1-2)
   - active/ for documented planning (tier 3-4)
   - completed/ for archived plans
   - Automatic moves during lifecycle transitions

3. **Historical Context → Planning Context**
   - Git history provides security insights, business rules
   - AST analysis provides code structure, dependencies
   - Comments provide expert identification, TODOs
   - All stored in context/ subfolder for reusability

4. **SKULL Enforcement → All Orchestrators**
   - STRICT_FOLDER_ORGANIZATION_ENFORCEMENT blocks root files
   - Applied to planning, ADO, TDD, and all future orchestrators
   - Pre-commit hooks prevent violations

### Success Criteria from Holistic Review

- ✅ Users see visual progress tracker (no regression)
- ✅ Pre-planning discovery shows existing/related work (<500ms)
- ✅ Plans in semantic folders (authentication-system-v1/)
- ✅ Subfolder structure automatic (context/, reports/, artifacts/, tracking/)
- ✅ Temp → active → completed lifecycle working
- ✅ Master plans include visual tracker at top
- ✅ Historical context gathered during planning
- ✅ Office filing system pattern applied (universal mental model)
- ✅ Recursive realignment relocates ALL violations
- ✅ Orphan deletion optional (safety first)
- ✅ Reference updates maintain document integrity
- ✅ 100% test coverage for new functionality
- ✅ Zero violations of SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT

---

## 📖 Office Filing System Pattern Summary

**Why This Matters:**

The office filing system is the most successful organizational pattern in history. Every professional understands:
- Filing cabinets (cortex-brain/documents/)
- Drawers for categories (planning/, reports/, analysis/)
- Hanging folders for projects ({plan-name}/)
- Manila folders for document types (context/, reports/, artifacts/, tracking/)
- Papers filed inside folders (individual .md files)

**CORTEX Implementation:**

```
Physical Office              →    CORTEX Digital
─────────────────────────────────────────────────────────
Filing Cabinet               →    cortex-brain/documents/
Drawer (Projects)            →    planning/
Pending Tray                 →    temp-plans/
Active Files                 →    active/
Archive Drawer               →    completed/
Hanging Folder (Project X)   →    {authentication-system-v1}/
Manila Folder (Background)   →    context/
Manila Folder (Reports)      →    reports/
Manila Folder (Deliverables) →    artifacts/
Manila Folder (Tracking)     →    tracking/
Papers in folder             →    *.md, *.yaml, *.json files
```

**Secretary Workflow (Pre-Planning Discovery):**

Before creating new project folder:
1. Check active drawer (current projects)
2. Check pending tray (unapproved work)
3. Check archive (last 6 months)
4. Ask: "Should we continue existing project or start fresh?"

**Realignment = Filing Cabinet Cleanup:**

1. Pull out ALL loose papers (recursive scan)
2. Determine which project each belongs to (context inference)
3. File in appropriate folder (move + update references)
4. Discard duplicates and obsolete papers (orphan deletion)

---

## ✅ Approval Required

**Document Status:** ✅ Ready for Review (v3.0 - Comprehensive Orchestration Integration + Continuation Prompts)  
**Approval Required:** Asif Hussain (Architecture Lead)  
**Implementation Start:** Pending approval  
**Target Completion:** 24 days (Week of January 16, 2026)

**Key Changes from v2.0:**

**1. Continuation Prompt System (CRITICAL NEW FEATURE)**
   - Enables session recovery across Copilot Chat windows
   - Embedded in `00-master-plan.md` right after visual tracker
   - Single paragraph with STATUS, NEXT ACTION, CONTEXT, INSTRUCTIONS
   - Updated automatically after each phase completion
   - User can copy-paste to new chat window → CORTEX executes immediately (no re-planning)
   - **User Request:** "This prompt should have instructions for cortex to EXECUTE the next step directly in the new chat window, NOT report on it."

**2. Orchestration System Integration (8 Orchestrators)**
   - PRIMARY: PlanningOrchestrator (line 512-518 fix + continuation prompts)
   - SECONDARY: TDDOrchestrator (test reports in plan folders), ADOPlanningOrchestrator (ADO work items in artifacts/)
   - TERTIARY/MINOR: MaintenanceOrchestratorV3, CleanupOrchestrator (rename to StrictFolderRealignmentOrchestrator), DocumentHygieneOrchestrator, RefactorCycleOrchestrator, VacuumOrchestrator
   - BaseOrchestrator base class with universal methods (create_plan_folder, update_continuation_prompt, generate_execution_report, update_progress_tracker)
   - Consistent folder organization across ALL orchestrators

**3. Dashboard Metrics Integration (NEW)**
   - FolderOrganizationMetricsCollector class
   - Metrics: root_violations (target 0), proper_structure_percentage (target 100%), plans_by_status, discovery_performance (<500ms), plans_reused
   - Dashboard visualization: `cortex-brain/dashboards/folder-organization-dashboard.yaml`
   - Real-time health monitoring with alerts (root violations >0)

**4. Manifest Updates (NEW)**
   - planning-system-2.0-manifest.yaml comprehensive additions
   - folder_organization v3.0 specification with 8 subsections:
     - structure, continuation_prompts, pre_planning_discovery, visual_tracker, lifecycle_workflow, orchestrator_integration, skull_enforcement, realignment
   - Standardized configuration across all orchestrators
   - Clear requirements for orchestrator integration

**5. Brain Tier Organization (NEW)**
   - Tier 1: `conversations/active/` and `conversations/archived/{year}/{month}/`
   - Tier 2: `patterns/planning/` and `patterns/code/` (learning from completed work)
   - Tier 3: `project-state/{project-name}/` (hotspots, metrics, plan-references)
   - Cross-tier linking for full context navigation

**Implementation Changes:**
- Expanded from 9 to 12 phases (added Dashboard Integration, Manifest Updates, Brain Tier Organization)
- Added continuation prompt steps to all phases
- Timeline extended from 20 to 24 days (Week of January 16, 2026)
- Success metrics expanded from 15 to 31 metrics (added 5 categories)

**Key Insights from v3.0 Discussion:**

1. **Continuation Prompts are CRITICAL for Session Recovery** - Users frequently close Copilot Chat windows and need to resume work later. Copy-paste prompt enables seamless handoff without losing context or re-planning.

2. **Orchestration Integration Requires Base Class Pattern** - All 8 orchestrators creating files need consistent folder organization. BaseOrchestrator base class enforces DRY principle and consistent interface.

3. **Dashboard Visibility Enables Proactive Health Monitoring** - Real-time metrics (root violations, structure compliance, discovery performance) prevent issues from accumulating. Alert when violations >0.

4. **Manifest Documentation Prevents Implementation Drift** - Comprehensive specification in manifest ensures all orchestrators meet same standards. Compliance validation prevents regression.

5. **Brain Tier Organization Provides Full Context** - Separating conversations (Tier 1), patterns (Tier 2), and project state (Tier 3) with cross-tier linking enables holistic understanding of project work over time.

**Breaking Changes:**
- All orchestrators must extend BaseOrchestrator (migration required)
- Continuation prompt format is REQUIRED in all active plans
- Manifest compliance validation will fail on non-compliant orchestrators

**Migration Path:**
1. Phase 4: Implement BaseOrchestrator class
2. Phases 7-8: Migrate orchestrators to extend BaseOrchestrator
3. Phase 10-11: Add dashboard metrics and manifest validation
4. Phase 12: Create brain tier folder structure

---

**Challenge/Feedback:** This v3.0 plan transforms folder organization from a planning orchestrator fix into a comprehensive orchestration-wide standard with session recovery mechanism. The continuation prompt system is the key user-requested feature enabling work continuity across Copilot Chat sessions. Please review the BaseOrchestrator integration approach and continuation prompt design.

---

**End of Document**
