🧠 CORTEX - Visual Tracker Migration Sub-Plan
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# Phase 1: Visual Tracker Migration

**Phase ID:** 01  
**Duration:** 2 days  
**Status:** ⏸️ PENDING  
**Dependencies:** Phase 0 (Governance Foundation) complete

---

## 🎯 Objectives

Migrate visual progress tracker from Planning System 2.0 (legacy) to Planning Orchestrator v3.1. Add pre-planning discovery to check for existing plans before creating new ones.

**Key Deliverables:**
1. Pre-planning discovery method
2. PlanningSession integration
3. Visual tracker in user responses
4. Visual tracker embedded in master plans
5. Session metrics (tokens, duration, phases)

---

## 📋 Tasks

### Task 1.1: Add Pre-Planning Discovery Method

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Implementation:**
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
    
    # Extract feature name from operation
    feature_slug = self._extract_feature_slug(operation)
    
    # Search active/ folder (current work)
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
    
    # Search temp-plans/ folder (unapproved work)
    temp_plans = self._search_plans(
        folder="temp-plans",
        query=feature_slug,
        time_range="last_30_days"
    )
    
    if temp_plans:
        results['found_existing'] = True
        results['recommendations'].append({
            'type': 'temp_plan_exists',
            'message': f"Found {len(temp_plans)} temporary plan(s) - may need approval",
            'plans': temp_plans,
            'action': 'approve_existing_or_create_new'
        })
    
    # Search completed/ folder (recently archived)
    completed_plans = self._search_plans(
        folder="completed",
        query=feature_slug,
        time_range="last_180_days"
    )
    
    if completed_plans:
        results['related_plans'].extend(completed_plans)
        results['recommendations'].append({
            'type': 'completed_plan_exists',
            'message': f"Found {len(completed_plans)} completed plan(s) - context available",
            'plans': completed_plans,
            'action': 'reuse_context_from_completed'
        })
    
    return results
```

**Tests:**
- [ ] `test_pre_planning_discovery_finds_active_plans()`
- [ ] `test_pre_planning_discovery_finds_temp_plans()`
- [ ] `test_pre_planning_discovery_finds_completed_plans()`
- [ ] `test_pre_planning_discovery_no_existing_plans()`

---

### Task 1.2: Add Helper Methods for Discovery

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Implementation:**
```python
def _extract_feature_slug(self, operation: str) -> str:
    """Extract feature slug from operation text."""
    # Remove common prefixes
    operation = operation.lower()
    for prefix in ["plan ", "implement ", "create ", "build "]:
        if operation.startswith(prefix):
            operation = operation[len(prefix):]
    
    # Convert to slug
    return operation.replace(' ', '-')[:50]

def _search_plans(self, folder: str, query: str, time_range: str) -> List[Dict[str, Any]]:
    """Search plans in specific folder by feature name and time range."""
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
                continue
            
            # Read master plan to get summary
            master_plan = self._find_master_plan(plan_folder)
            
            plans.append({
                'folder': str(plan_folder),
                'name': plan_folder.name,
                'last_modified': datetime.fromtimestamp(plan_folder.stat().st_mtime),
                'summary': self._extract_plan_summary(master_plan) if master_plan else "No summary",
                'has_context': (plan_folder / "context").exists(),
                'has_reports': (plan_folder / "reports").exists()
            })
    
    return plans

def _get_cutoff_date(self, time_range: str) -> Optional[datetime]:
    """Get cutoff date for time range filtering."""
    if time_range == "all":
        return None
    elif time_range == "last_30_days":
        return datetime.now() - timedelta(days=30)
    elif time_range == "last_180_days":
        return datetime.now() - timedelta(days=180)
    else:
        return None

def _find_master_plan(self, plan_folder: Path) -> Optional[Path]:
    """Find master plan file in plan folder."""
    candidates = ["00-master-plan.md", "11-temp-planning-session.md"]
    for candidate in candidates:
        path = plan_folder / candidate
        if path.exists():
            return path
    return None

def _extract_plan_summary(self, plan_file: Path) -> str:
    """Extract summary from plan file (first paragraph after title)."""
    with open(plan_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find first paragraph after title
    for i, line in enumerate(lines):
        if line.startswith("## ") and "summary" in line.lower():
            # Return next non-empty line
            for j in range(i+1, len(lines)):
                if lines[j].strip():
                    return lines[j].strip()[:200]
    
    return "No summary available"
```

**Tests:**
- [ ] `test_extract_feature_slug()`
- [ ] `test_search_plans_by_time_range()`
- [ ] `test_find_master_plan()`

---

### Task 1.3: Import PlanningSession

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Add to imports:**
```python
from src.orchestrators.session_model import PlanningSession, SessionStatus
```

**Initialize in plan() method:**
```python
def plan(self, operation: str):
    # NEW: Pre-planning discovery
    discovery = self.pre_planning_discovery(operation)
    if discovery['found_existing']:
        # Present discovery results to user
        self._present_discovery_results(discovery)
        # Wait for user decision...
    
    # Initialize session tracking
    self.session = PlanningSession(
        session_id=str(uuid.uuid4()),
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title=operation
    )
    
    # Continue with planning...
```

**Tests:**
- [ ] `test_planning_session_initialization()`
- [ ] `test_discovery_presented_to_user()`

---

### Task 1.4: Add Phase Tracking

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Replace `_generate_progress_summary()` with session tracking:**
```python
# REMOVE OLD METHOD:
# def _generate_progress_summary(self, phases: List[Dict]) -> str:
#     ...

# ADD SESSION TRACKING:
def _execute_planning_phase(self, phase_name: str, phase_func):
    """Execute a planning phase with session tracking."""
    self.session.record_phase_start(phase_name)
    
    try:
        result = phase_func()
        tokens_used = self._estimate_tokens_used(result)
        self.session.record_phase_end(phase_name, tokens_used=tokens_used)
        return result
    except Exception as e:
        self.session.record_phase_end(phase_name, error=str(e))
        raise

def _estimate_tokens_used(self, result: Any) -> int:
    """Estimate tokens used in phase (rough approximation)."""
    if isinstance(result, str):
        return len(result.split()) * 1.3  # ~1.3 tokens per word
    return 0
```

**Tests:**
- [ ] `test_phase_tracking_with_metrics()`
- [ ] `test_token_estimation()`

---

### Task 1.5: Render Visual Tracker in Responses

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Add to final response generation:**
```python
def _generate_final_response(self) -> str:
    """Generate final response with visual tracker."""
    # Render progress table
    progress_table = self.session.render_progress_table()
    
    response = f"""
## 🧠 CORTEX Planning Complete

{progress_table}

### 📊 Session Metrics
- **Total Duration:** {self.session.format_duration()}
- **Total Tokens:** {self.session.total_tokens:,}
- **Phases Completed:** {len(self.session.phases)}

### 📋 Next Steps
...
    """
    
    return response
```

**Tests:**
- [ ] `test_visual_tracker_in_response()`
- [ ] `test_session_metrics_display()`

---

### Task 1.6: Embed Tracker in Master Plans

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Update `_generate_master_plan_content()` method:**
```python
def _generate_master_plan_content(self, phases: List[Dict], folder: Path) -> str:
    """Generate master plan with embedded visual tracker."""
    # Create session for tracker
    session = PlanningSession(
        session_id=str(uuid.uuid4()),
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title=folder.name
    )
    
    for phase in phases:
        session.add_phase(phase['name'], phase.get('tasks', []))
    
    # Render tracker
    visual_tracker = session.render_progress_table()
    
    # Generate master plan with tracker embedded
    content = f"""🧠 CORTEX - {folder.name} Master Plan
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# {folder.name.replace('-', ' ').title()} Master Plan

...

## 📊 Visual Progress Tracker

{visual_tracker}

...
    """
    
    return content
```

**Tests:**
- [ ] `test_master_plan_with_visual_tracker()`
- [ ] `test_tracker_updates_in_real_time()`

---

### Task 1.7: Update Planning System 2.0 Manifest

**File:** `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`

**Add visual tracker requirements:**
```yaml
visual_progress_tracker:
  enabled: true
  source: "src/orchestrators/session_model.py::PlanningSession"
  location: "master plans (00-master-plan.md)"
  updates: "real-time during execution"
  metrics:
    - phase_timing
    - token_consumption
    - duration_formatting
    - progress_percentage

pre_planning_discovery:
  enabled: true
  search_folders:
    - "active/"
    - "temp-plans/"
    - "completed/"
  time_ranges:
    active: "all"
    temp_plans: "last_30_days"
    completed: "last_180_days"
  overhead: "30-60 seconds"
```

---

### Task 1.8: Integration Testing

**Create:** `tests/integration/test_visual_tracker_integration.py`

**Tests:**
- [ ] End-to-end planning with discovery
- [ ] Visual tracker visible in responses
- [ ] Tracker embedded in generated master plans
- [ ] Metrics accurately tracked
- [ ] Discovery finds existing plans

---

## ✅ Completion Criteria

- [ ] All unit tests passing (16 tests)
- [ ] Integration tests passing (5 tests)
- [ ] Pre-planning discovery functional (30-60 sec overhead)
- [ ] Visual tracker visible in Copilot responses
- [ ] Visual tracker embedded in master plans
- [ ] Session metrics accurate (tokens, duration)
- [ ] Planning System 2.0 manifest updated

---

## 📊 Estimated Effort

- **Development:** 12 hours
- **Testing:** 4 hours
- **Total:** 16 hours (2 days)

---

## 🔗 Related Files

- `src/orchestrators/session_model.py` (PlanningSession class)
- `src/operations/modules/orchestration/planning_orchestrator.py` (target file)
- `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml`
- `tests/orchestrators/test_planning_orchestrator.py`

---

**Status:** Ready to execute  
**Next Phase:** 02 - Semantic Folder Organization
