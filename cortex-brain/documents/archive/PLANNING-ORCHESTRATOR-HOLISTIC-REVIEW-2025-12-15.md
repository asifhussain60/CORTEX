# Planning Orchestrator Holistic Review & Fix Plan

**Date:** December 15, 2025  
**Author:** Asif Hussain  
**Status:** 🔍 ANALYSIS COMPLETE → 🛠️ READY FOR IMPLEMENTATION  
**Version:** 1.1.0 (Updated with Context Gathering Analysis)

---

## 🔗 Related Documents

**This document is part 1 of a 2-part strategic review:**
1. **PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md** (This document)
   - Planning orchestrator issues (visual tracker, folder organization)
   - 5-phase implementation plan (visual tracker → folders → lifecycle → ADO → SKULL)

2. **[CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md](./CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md)**
   - Context gathering capabilities analysis (git history, AST, comments)
   - CORTEX 3.0 enhancement strategy (unified context builder)
   - CORTEX 4.0 vision (AI-powered context synthesis)

**Read both documents for complete architectural understanding.**

---

## 🎯 Executive Summary

**Problem Identified:** Planning orchestrators have **architectural fragmentation** causing:
1. ❌ **Missing visual tracker** - Implemented in old orchestrator, not migrated to v3.1
2. ❌ **No semantic folder organization** - Files scattered across generic locations
3. ❌ **Incomplete file lifecycle** - Temp files, master plans, sub-plans not co-located
4. ❌ **No subfolder structure** - Reports, tracking, artifacts mixed with plans
5. ❌ **No historical context gathering** - Git history, AST analysis, comment extraction not integrated (see [companion document](./CONTEXT-GATHERING-AND-ARCHITECTURE-STRATEGY-2025-12-15.md))

**Root Cause:** Planning System v3.1 (`src/operations/modules/orchestration/planning_orchestrator.py`) was created as a new implementation without migrating proven features from v2.0 (`src/orchestrators/planning_orchestrator.py`).

**Impact:**
- Users don't see visual progress tracking (lost feature regression)
- Planning documents difficult to discover (poor organization)
- No clear plan lifecycle (approval → active → completed workflow broken)
- Mixed responsibility between two orchestrator implementations
- **No historical context** during planning (security risks, business rules, expert identification missing)

---

## 📊 Current State Analysis

### Orchestrator Inventory

| Orchestrator | Location | Version | Status | Visual Tracker | Folder Organization |
|--------------|----------|---------|--------|----------------|---------------------|
| **Planning v2.0** | `src/orchestrators/planning_orchestrator.py` | 2.0 | ⚠️ Legacy | ✅ YES (`PlanningSession.render_progress_table()`) | ❌ NO |
| **Planning v3.1** | `src/operations/modules/orchestration/planning_orchestrator.py` | 3.1 | ✅ ACTIVE | ❌ NO | ❌ NO |
| **ADO Planning** | `src/operations/modules/orchestration/ado_planning_orchestrator.py` | 1.0 | ✅ ACTIVE | ❌ NO | ❌ NO |
| **Planning 3.0** | `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py` | 3.0 | ⚠️ Prototype | ❌ NO | ❌ NO |

### File Creation Patterns (WRONG ❌)

**Current Behavior:**
```python
# planning_orchestrator.py line 512-518
def _generate_plan_path(self, planning_context: PlanningContext, tier: int) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    operation_slug = planning_context.operation.lower().replace(' ', '-')[:30]
    filename = f"plan_{operation_slug}_{timestamp}.md"
    
    return self.project_root / "cortex-brain" / "documents" / "planning" / "features" / filename
    # ❌ PROBLEM: Files go to generic "features" folder with timestamp naming
```

**Problems:**
1. ❌ Generic folder (`features/`) violates `SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT`
2. ❌ Timestamp-based naming (`plan_add-auth_20251215_103045.md`) - not semantic
3. ❌ No dedicated folder per plan (temp file, master, sub-plans scattered)
4. ❌ No subfolder structure (`reports/`, `tracking/`, `artifacts/`)
5. ❌ Continuation prompts mixed with master plans

### Visual Tracker Git History

**Commit 83b26f7e (Dec 13, 2025):**
- ✅ Implemented `PlanningSession.render_progress_table()` in `session_model.py`
- ✅ Added phase timing tracking (`phase_start_times`, `phase_end_times`)
- ✅ Token consumption metrics (`tokens_used`, `total_tokens_used`)
- ✅ Sub-plan coordination checkpoints
- ✅ Duration formatting (human-readable: "2h 15m", "3m 45s")

**BUT:** Only integrated into `src/orchestrators/planning_orchestrator.py` (v2.0 - LEGACY)

**Current v3.1:** Uses internal logging only (line 595-625):
```python
def _generate_progress_summary(self, planning_context: PlanningContext) -> str:
    """
    Generate progress summary for INTERNAL LOGGING ONLY.
    
    NOTE: ASCII progress bars are for internal logging only.
    User-facing output uses markdown tables without ASCII art.
    """
    # ❌ PROBLEM: Only logs to internal logger, user never sees it
```

---

## 🛠️ Required Folder Structure (CORRECT ✅)

### Semantic Organization Pattern

```
cortex-brain/documents/planning/active/
├── {feature-name-v{version}}/              # Semantic feature folder
│   ├── 00-master-plan.md                   # Master plan (top-level)
│   ├── 00-implementation-plan.md           # Detailed implementation
│   ├── 00-master-subplan.md                # Sub-plan hierarchy
│   ├── 01-subplan-{name}.md                # Sub-plan 1
│   ├── 02-subplan-{name}.md                # Sub-plan 2
│   ├── 03-subplan-{name}.md                # Sub-plan 3
│   ├── 10-continuation-prompt.md           # Session handoff (temporary)
│   ├── 11-temp-planning-session.md         # User iteration (temporary)
│   ├── reports/                            # Execution reports
│   │   ├── phase-1-completion.md
│   │   ├── phase-2-completion.md
│   │   └── final-report.md
│   ├── tracking/                           # Progress tracking
│   │   ├── progress-tracker.json           # Machine-readable state
│   │   ├── phase-status.yaml               # Current phase status
│   │   └── metrics.json                    # Execution metrics
│   └── artifacts/                          # Generated artifacts
│       ├── extracted-components.json
│       ├── analysis-results.json
│       └── test-results.json
│
├── approved/                                # Plans approved but not started
│   └── {feature-name-v{version}}/
│
└── completed/                               # Finished plans (archived)
    └── {feature-name-v{version}}/
```

### Folder Lifecycle Workflow

```
1. CREATION (active/)
   User: "Plan authentication system"
   → Create: active/authentication-system-v1/
   → Files: 11-temp-planning-session.md (temporary)

2. ITERATION (active/)
   User provides feedback
   → Update: 11-temp-planning-session.md (in-place edits)
   
3. APPROVAL (active/ → approved/)
   User: "Approved, proceed"
   → Generate: 00-master-plan.md, 00-master-subplan.md
   → Create: 01-subplan-foundation.md, 02-subplan-implementation.md, etc.
   → Delete: 11-temp-planning-session.md (no longer needed)
   → Move: active/ → approved/ (optional)

4. EXECUTION (approved/ or active/)
   Orchestrator executes phases
   → Create: reports/phase-{N}-completion.md (after each phase)
   → Update: tracking/progress-tracker.json (real-time)
   → Update: tracking/phase-status.yaml (current phase)

5. COMPLETION (approved/ → completed/)
   All phases done
   → Generate: reports/final-report.md
   → Update: tracking/metrics.json (final stats)
   → Move: approved/ → completed/ (archive)
```

---

## 🔧 Implementation Plan

### Phase 1: Add Visual Tracker to Planning Orchestrator v3.1

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Changes:**
1. Import `PlanningSession` from `src/orchestrators/session_model.py`
2. Replace `_generate_progress_summary()` with `PlanningSession.render_progress_table()`
3. Add session tracking:
   ```python
   self.session = PlanningSession(
       session_id=str(uuid.uuid4()),
       session_type="planning",
       status=SessionStatus.IN_PROGRESS,
       started_at=datetime.now(),
       plan_title=operation
   )
   ```
4. Record phase start/end with tokens:
   ```python
   self.session.record_phase_start("classification")
   # ... execute phase ...
   self.session.record_phase_end("classification", tokens_used=1250)
   ```
5. Render progress table in user response:
   ```python
   progress_table = self.session.render_progress_table()
   # Include in final response to user
   ```

**Expected Outcome:**
- ✅ Users see visual progress tracker with phase timing
- ✅ Token consumption visible per phase + total
- ✅ Duration formatting (human-readable)
- ✅ Sub-plan coordination checkpoints

### Phase 2: Semantic Folder Organization

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Replace `_generate_plan_path()` (line 512-518):**

```python
def _generate_plan_path(self, planning_context: PlanningContext, tier: int) -> Path:
    """
    Generate semantic plan folder structure.
    
    Creates: cortex-brain/documents/planning/active/{feature-name-v{version}}/
    
    Folder naming rules (SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT):
    - Feature-based: authentication-system-v1, cortex-lens-v3, tdd-orchestrator-v2
    - Version included: v1, v2, v3
    - Lowercase with hyphens: no-spaces-or-underscores
    """
    # Extract feature name from operation
    operation_slug = planning_context.operation.lower().replace(' ', '-')[:50]
    
    # Auto-detect version (check for existing folders)
    base_folder_name = operation_slug.removesuffix('-v1').removesuffix('-v2').removesuffix('-v3')
    version = self._detect_next_version(base_folder_name)
    
    # Construct semantic folder name
    folder_name = f"{base_folder_name}-v{version}"
    
    # Create folder structure
    plan_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "active" / folder_name
    plan_folder.mkdir(parents=True, exist_ok=True)
    
    # Create subfolders
    (plan_folder / "reports").mkdir(exist_ok=True)
    (plan_folder / "tracking").mkdir(exist_ok=True)
    (plan_folder / "artifacts").mkdir(exist_ok=True)
    
    # Determine file name based on tier and lifecycle stage
    if tier <= 2:
        # Lightweight: inline execution (no file created)
        return None
    elif tier == 3:
        # Documented: single master plan
        filename = "00-master-plan.md"
    else:
        # Complex: master + sub-plans
        filename = "11-temp-planning-session.md"  # Temporary for user iteration
    
    return plan_folder / filename

def _detect_next_version(self, base_folder_name: str) -> int:
    """Detect next version number for feature folder."""
    active_dir = self.project_root / "cortex-brain" / "documents" / "planning" / "active"
    if not active_dir.exists():
        return 1
    
    existing_versions = []
    for folder in active_dir.iterdir():
        if folder.is_dir() and folder.name.startswith(base_folder_name):
            # Extract version number (authentication-system-v3 → 3)
            version_match = folder.name.split('-v')[-1]
            if version_match.isdigit():
                existing_versions.append(int(version_match))
    
    return max(existing_versions, default=0) + 1
```

**Expected Outcome:**
- ✅ Plans created in semantic folders: `active/authentication-system-v1/`
- ✅ Auto-versioning: v1, v2, v3 based on existing folders
- ✅ Subfolder structure: `reports/`, `tracking/`, `artifacts/`
- ✅ Temporary file: `11-temp-planning-session.md` (user iteration)

### Phase 3: Plan Lifecycle Management

**Add to `PlanningOrchestrator` class:**

```python
def approve_temporary_plan(self, temp_plan_path: Path) -> Dict[str, Any]:
    """
    Convert temporary plan to master + sub-plans.
    
    Workflow:
    1. Read 11-temp-planning-session.md
    2. Parse phases and tasks
    3. Generate 00-master-plan.md with visual tracker
    4. Generate 01-subplan-{name}.md for each phase
    5. Delete 11-temp-planning-session.md
    6. Initialize tracking/progress-tracker.json
    
    Args:
        temp_plan_path: Path to temporary planning session file
    
    Returns:
        Dict with generated file paths
    """
    folder = temp_plan_path.parent
    
    # 1. Read temporary plan
    with open(temp_plan_path, 'r', encoding='utf-8') as f:
        temp_content = f.read()
    
    # 2. Parse phases (extract from markdown sections)
    phases = self._parse_phases_from_temp_plan(temp_content)
    
    # 3. Generate master plan with visual tracker
    master_plan_path = folder / "00-master-plan.md"
    master_content = self._generate_master_plan_content(phases)
    with open(master_plan_path, 'w', encoding='utf-8') as f:
        f.write(master_content)
    
    # 4. Generate sub-plans
    subplan_paths = []
    for idx, phase in enumerate(phases, start=1):
        subplan_path = folder / f"{idx:02d}-subplan-{phase['name'].lower().replace(' ', '-')}.md"
        subplan_content = self._generate_subplan_content(phase, master_plan_path)
        with open(subplan_path, 'w', encoding='utf-8') as f:
            f.write(subplan_content)
        subplan_paths.append(subplan_path)
    
    # 5. Initialize progress tracker
    tracker_path = folder / "tracking" / "progress-tracker.json"
    tracker_data = {
        "plan_id": str(uuid.uuid4()),
        "feature_name": folder.name,
        "total_phases": len(phases),
        "completed_phases": 0,
        "current_phase": 1,
        "phase_status": {str(i): "not_started" for i in range(1, len(phases) + 1)},
        "started_at": datetime.now().isoformat(),
        "completed_at": None
    }
    with open(tracker_path, 'w', encoding='utf-8') as f:
        json.dump(tracker_data, f, indent=2)
    
    # 6. Delete temporary plan
    temp_plan_path.unlink()
    
    return {
        "approved": True,
        "master_plan": str(master_plan_path),
        "sub_plans": [str(p) for p in subplan_paths],
        "tracker": str(tracker_path),
        "message": f"Plan approved and converted. {len(phases)} sub-plans created."
    }

def _generate_master_plan_content(self, phases: List[Dict[str, Any]]) -> str:
    """Generate master plan content with visual tracker."""
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
    
    # Build master plan content
    content = f"""# Master Plan: {phases[0].get('feature_name', 'Feature Implementation')}

**Version:** 1.0  
**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Status:** 🎯 APPROVED

---

## 📊 Progress Tracker

{visual_tracker}

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
- ✅ Progress tracker JSON for machine updates
- ✅ Bidirectional links (master ↔ sub-plans)

### Phase 4: ADO Planning Orchestrator Alignment

**File:** `src/operations/modules/orchestration/ado_planning_orchestrator.py`

**Apply same fixes:**
1. Add visual tracker (import `PlanningSession`)
2. Use semantic folder organization
3. Implement plan lifecycle workflow

### Phase 5: Update SKULL Rules

**File:** `cortex-brain/brain-protection-rules.yaml`

**Add new rule (already done in previous work):**
- `SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT` ✅ COMPLETE (lines 4300-4550)

**Add new rule for folder structure:**

```yaml
- rule_id: "PLANNING_FOLDER_STRUCTURE_ENFORCEMENT"
  name: "Planning Folder Structure Enforcement"
  severity: "blocked"
  description: "Planning folders MUST contain subfolders: reports/, tracking/, artifacts/. Master plans use 00- prefix, sub-plans use 01-09, temp files use 10+."
  
  detection:
    combined_keywords:
      folder_creation:
        - "create plan folder"
        - "generate plan directory"
      missing_structure:
        - "no subfolders"
        - "flat structure"
    scope: ["intent", "folder_structure"]
    logic: "AND"
  
  required_structure:
    - folder: "reports/"
      purpose: "Phase completion reports, final reports"
    - folder: "tracking/"
      purpose: "progress-tracker.json, phase-status.yaml, metrics.json"
    - folder: "artifacts/"
      purpose: "Generated artifacts (JSON, YAML, analysis results)"
  
  file_naming_rules:
    - rule: "Master plans: 00-master-plan.md, 00-implementation-plan.md"
    - rule: "Sub-plans: 01-subplan-{name}.md, 02-subplan-{name}.md"
    - rule: "Temp files: 11-temp-planning-session.md (deleted after approval)"
    - rule: "Continuation prompts: 10-continuation-prompt-{context}.md"
  
  alternatives:
    - "STEP 1: Create semantic folder: active/{feature-name-v{version}}/"
    - "STEP 2: Create subfolders: reports/, tracking/, artifacts/"
    - "STEP 3: Create temp file: 11-temp-planning-session.md"
    - "STEP 4: On approval: convert to 00-master-plan.md + 01-subplan-*.md"
    - "STEP 5: Delete temp file after conversion"
  
  evidence_template: |
    Planning folder structure violation detected!
    
    Folder: '{folder_path}'
    
    ❌ WRONG: Flat structure
    ```
    active/authentication-system-v1/
    ├── plan.md (no semantic naming)
    └── (no subfolders)
    ```
    
    ✅ CORRECT: Structured with subfolders
    ```
    active/authentication-system-v1/
    ├── 00-master-plan.md
    ├── 01-subplan-foundation.md
    ├── 02-subplan-implementation.md
    ├── reports/
    │   └── phase-1-completion.md
    ├── tracking/
    │   └── progress-tracker.json
    └── artifacts/
        └── analysis-results.json
    ```
  
  rationale: |
    PLANNING_FOLDER_STRUCTURE_ENFORCEMENT: Organization & Discoverability
    
    Problem: Flat structure chaos
    - Reports mixed with plans
    - No progress tracking
    - Artifacts scattered
    
    Solution: Subfolder organization
    - reports/: Completion reports
    - tracking/: Machine-readable state
    - artifacts/: Generated files
    
    Benefits:
    - Clear separation of concerns
    - Easy report discovery
    - Progress tracking centralized
    - Artifact management
```

---

## 🎯 Testing Plan

### Unit Tests

```python
# tests/operations/modules/orchestration/test_planning_orchestrator.py

def test_semantic_folder_creation():
    """Test semantic folder structure creation."""
    orchestrator = PlanningOrchestrator()
    
    context = PlanningContext(
        operation="add authentication system",
        tier=4,
        ...
    )
    
    path = orchestrator._generate_plan_path(context, tier=4)
    
    assert path.parent.name == "authentication-system-v1"
    assert (path.parent / "reports").exists()
    assert (path.parent / "tracking").exists()
    assert (path.parent / "artifacts").exists()
    assert path.name == "11-temp-planning-session.md"

def test_plan_approval_workflow():
    """Test temporary plan approval and conversion."""
    orchestrator = PlanningOrchestrator()
    temp_path = Path("active/test-feature-v1/11-temp-planning-session.md")
    
    # Create temporary plan
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(temp_path, 'w') as f:
        f.write("# Test Plan\n\n## Phase 1: Foundation\n\n...")
    
    # Approve
    result = orchestrator.approve_temporary_plan(temp_path)
    
    assert result["approved"] is True
    assert Path(result["master_plan"]).exists()
    assert len(result["sub_plans"]) > 0
    assert not temp_path.exists()  # Deleted after approval

def test_visual_tracker_rendering():
    """Test visual tracker in master plan."""
    orchestrator = PlanningOrchestrator()
    
    # Execute planning workflow
    result = orchestrator.execute(...)
    
    # Check that progress table is in response
    assert "Progress Tracker" in result.message
    assert "Phase" in result.message
    assert "Status" in result.message
```

### Integration Tests

```bash
# Manual testing workflow

# 1. Create plan
python -m src.main plan "add authentication system"

# Expected output:
# - Folder created: active/authentication-system-v1/
# - File created: 11-temp-planning-session.md
# - Subfolders: reports/, tracking/, artifacts/

# 2. Approve plan
python -m src.main approve active/authentication-system-v1/11-temp-planning-session.md

# Expected output:
# - Master plan: 00-master-plan.md (with visual tracker)
# - Sub-plans: 01-subplan-foundation.md, 02-subplan-implementation.md
# - Tracking: tracking/progress-tracker.json
# - Temp file deleted: 11-temp-planning-session.md

# 3. Execute phases
python -m src.main execute-phase 1

# Expected output:
# - Progress tracker updated in 00-master-plan.md
# - Completion report: reports/phase-1-completion.md
# - Tracking updated: tracking/progress-tracker.json
```

---

## 📊 Success Metrics

**Completion Criteria:**
- [ ] Visual tracker visible to users (no regression)
- [ ] Plans created in semantic folders (authentication-system-v1/)
- [ ] Subfolder structure automatic (reports/, tracking/, artifacts/)
- [ ] Temporary file lifecycle working (11-temp → approved → deleted)
- [ ] Master plan includes visual tracker at top
- [ ] Sub-plans link back to master plan
- [ ] Progress tracking JSON updates automatically
- [ ] All unit tests passing (100%)
- [ ] Integration tests passing (100%)
- [ ] SKULL rule enforcement active

**Quality Gates:**
- Compliance rate: 100% (no violations of `SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT`)
- Test coverage: >85% for new code
- Zero regressions: All existing functionality preserved
- Documentation: All changes documented in manifest

---

## 🚀 Rollout Plan

**Phase 1:** Implement visual tracker (1 day)
- Add `PlanningSession` import
- Replace internal logging with user-visible tracker
- Test with sample plans

**Phase 2:** Implement semantic folders (1 day)
- Replace `_generate_plan_path()`
- Add auto-versioning logic
- Create subfolder structure

**Phase 3:** Implement lifecycle workflow (1 day)
- Add `approve_temporary_plan()` method
- Generate master + sub-plans
- Delete temp file after approval

**Phase 4:** Update ADO orchestrator (1 day)
- Apply same patterns
- Test ADO workflow

**Phase 5:** Testing & validation (1 day)
- Unit tests
- Integration tests
- Manual testing

**Total Effort:** 5 days

---

## 🎯 Next Actions

1. **Review this document** with team
2. **Approve implementation approach**
3. **Execute Phase 1** (visual tracker)
4. **Test incrementally** (each phase)
5. **Deploy to production**

---

**End of Report**

**Status:** Ready for implementation  
**Confidence:** High - clear implementation path with rollback plan
