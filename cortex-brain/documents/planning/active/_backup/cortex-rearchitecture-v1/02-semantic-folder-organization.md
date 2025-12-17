🧠 CORTEX - Semantic Folder Organization Sub-Plan
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# Phase 2: Semantic Folder Organization

**Phase ID:** 02  
**Duration:** 2 days  
**Status:** ⏸️ PENDING  
**Dependencies:** Phase 1 (Visual Tracker Migration) complete

---

## 🎯 Objectives

Replace generic folder creation with semantic, intent-based folder structure. Implement auto-versioning, universal subfolders, and tier-based routing.

**Key Deliverables:**
1. Semantic folder naming (feature-name-v1, not plan_timestamp)
2. Auto-versioning (v1, v2, v3)
3. Universal subfolders (context/, reports/, artifacts/, tracking/)
4. Tier-based routing (temp-plans/ vs active/)
5. Progress tracker initialization

---

## 📋 Tasks

### Task 2.1: Replace _generate_plan_path() Method

**File:** `src/operations/modules/orchestration/planning_orchestrator.py` (lines 512-518)

**REMOVE OLD CODE:**
```python
def _generate_plan_path(self, planning_context, tier):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    operation_slug = planning_context.operation.lower().replace(' ', '-')[:30]
    filename = f"plan_{operation_slug}_{timestamp}.md"
    return self.project_root / "cortex-brain" / "documents" / "planning" / "features" / filename
```

**ADD NEW CODE:**
```python
def _generate_plan_path(self, planning_context: PlanningContext, tier: int) -> Path:
    """
    Generate semantic plan folder structure with intent-based naming.
    
    Naming Rules (SEMANTIC_PLANNING_ORGANIZATION_ENFORCEMENT):
    - GOOD: authentication-system-v1 (user capability)
    - GOOD: cortex-rearchitecture-v1 (holistic system change)
    - BAD: strict-folder-organization-v1 (governance rule, not user intent)
    - BAD: tdd-enforcement-implementation-v1 (internal rule)
    
    Folder Structure:
    - Tier 1-2: temp-plans/{plan-id}/ (temporary, unapproved)
    - Tier 3-4: active/{feature-name-v{N}}/ (approved, active work)
    
    Universal Subfolders:
    - context/ (git history, AST, comments)
    - reports/ (analysis, execution reports)
    - artifacts/ (complexity analysis, extracted data)
    - tracking/ (progress tracker, metrics)
    """
    # Extract feature name from operation (holistic intent, not technical detail)
    operation_slug = self._extract_semantic_name(planning_context.operation)
    
    # Determine lifecycle stage based on tier
    if tier <= 2:
        # Lightweight/instant: temporary plan
        plan_id = f"{operation_slug}-{datetime.now().strftime('%Y%m%d')}"
        plan_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "temp-plans" / plan_id
        filename = "11-temp-planning-session.md"
    else:
        # Documented/complex: active plan with versioning
        version = self._detect_next_version(operation_slug)
        folder_name = f"{operation_slug}-v{version}"
        plan_folder = self.project_root / "cortex-brain" / "documents" / "planning" / "active" / folder_name
        filename = "00-master-plan.md" if tier == 4 else "11-temp-planning-session.md"
    
    # Create folder structure
    plan_folder.mkdir(parents=True, exist_ok=True)
    
    # Create universal subfolders
    (plan_folder / "context").mkdir(exist_ok=True)
    (plan_folder / "reports").mkdir(exist_ok=True)
    (plan_folder / "artifacts").mkdir(exist_ok=True)
    (plan_folder / "tracking").mkdir(exist_ok=True)
    
    # Initialize progress tracker
    self._initialize_progress_tracker(plan_folder, plan_id if tier <= 2 else folder_name)
    
    return plan_folder / filename
```

**Tests:**
- [ ] `test_semantic_folder_creation_temp_plans()`
- [ ] `test_semantic_folder_creation_active_plans()`
- [ ] `test_universal_subfolders_created()`

---

### Task 2.2: Add _extract_semantic_name() Method

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Implementation:**
```python
def _extract_semantic_name(self, operation: str) -> str:
    """
    Extract semantic, intent-based name from operation.
    
    Rules:
    - Represents USER INTENT, not technical implementation
    - Business language, not code component names
    - Holistic goal, not governance rule names
    
    Examples:
    - "Implement strict folder organization" → "cortex-rearchitecture"
    - "Add JWT authentication" → "authentication-system"
    - "Refactor planning orchestrator" → "planning-workflow"
    - "Enforce TDD rules" → "test-automation"
    """
    operation = operation.lower()
    
    # Remove common prefixes
    prefixes = ["implement ", "add ", "create ", "build ", "refactor ", "plan ", "enforce "]
    for prefix in prefixes:
        if operation.startswith(prefix):
            operation = operation[len(prefix):]
    
    # Remove governance rule language
    rule_patterns = [
        "strict folder organization",
        "tdd enforcement",
        "holistic code discovery"
    ]
    
    intent_mapping = {
        "strict folder organization": "cortex-rearchitecture",
        "folder organization": "cortex-rearchitecture",
        "tdd enforcement": "test-automation",
        "jwt token": "authentication-system",
        "auth": "authentication-system",
        "planning orchestrator": "planning-workflow"
    }
    
    # Check mappings
    for pattern, intent in intent_mapping.items():
        if pattern in operation:
            return intent
    
    # Default: clean slug (remove technical jargon)
    operation = operation.replace("orchestrator", "workflow")
    operation = operation.replace("enforcement", "automation")
    operation = operation.replace("implementation", "")
    
    # Convert to slug
    slug = operation.replace(' ', '-').strip('-')
    
    # Validate semantic quality
    if self._is_semantic_name(slug):
        return slug[:50]
    else:
        # Fallback: ask user or use generic with warning
        logger.warning(f"Could not extract semantic name from: {operation}")
        return "feature-implementation"

def _is_semantic_name(self, name: str) -> bool:
    """
    Validate semantic name quality (same logic as SKULL tests).
    
    Anti-patterns:
    - strict-folder-organization (governance rule)
    - tdd-enforcement (internal rule)
    - orchestrator-refactor (code component)
    """
    anti_patterns = [
        "cortex-enhancements",
        "strict-folder-organization",
        "tdd-enforcement",
        "ast-analysis",
        "orchestrator-refactor",
        "misc-plans",
        "new-features",
        "temp",
        "plan_",
        "implementation-v",
        "enforcement-v"
    ]
    
    for pattern in anti_patterns:
        if pattern in name:
            return False
    
    return "-" in name and len(name) > 5
```

**Tests:**
- [ ] `test_extract_semantic_name_mapping()`
- [ ] `test_semantic_name_validation()`
- [ ] `test_anti_pattern_detection()`

---

### Task 2.3: Add _detect_next_version() Method

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Implementation:**
```python
def _detect_next_version(self, base_folder_name: str) -> int:
    """
    Detect next version number for feature folder.
    
    Searches active/ and completed/ folders for existing versions.
    Returns next available version number.
    
    Examples:
    - No existing: returns 1
    - authentication-system-v2 exists: returns 3
    - authentication-system-v1, v2, v4 exist: returns 5 (max + 1)
    """
    import re
    
    version_pattern = re.compile(rf'^{re.escape(base_folder_name)}-v(\d+)$')
    existing_versions = []
    
    # Check active/ folder
    active_dir = self.project_root / "cortex-brain" / "documents" / "planning" / "active"
    if active_dir.exists():
        for folder in active_dir.iterdir():
            if folder.is_dir():
                match = version_pattern.match(folder.name)
                if match:
                    existing_versions.append(int(match.group(1)))
    
    # Check completed/ folder (in case of re-implementation)
    completed_dir = self.project_root / "cortex-brain" / "documents" / "planning" / "completed"
    if completed_dir.exists():
        for folder in completed_dir.iterdir():
            if folder.is_dir():
                match = version_pattern.match(folder.name)
                if match:
                    existing_versions.append(int(match.group(1)))
    
    return max(existing_versions, default=0) + 1
```

**Tests:**
- [ ] `test_detect_next_version_no_existing()`
- [ ] `test_detect_next_version_with_existing()`
- [ ] `test_detect_next_version_with_gaps()`

---

### Task 2.4: Add _initialize_progress_tracker() Method

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Implementation:**
```python
def _initialize_progress_tracker(self, plan_folder: Path, plan_id: str) -> None:
    """Initialize progress tracker JSON file in tracking/ subfolder."""
    tracker_path = plan_folder / "tracking" / "progress-tracker.json"
    
    if tracker_path.exists():
        return  # Already initialized
    
    tracker_data = {
        "plan_id": plan_id,
        "created_at": datetime.now().isoformat(),
        "status": "planning",
        "phases": [],
        "completed_phases": 0,
        "total_phases": 0,
        "started_at": None,
        "completed_at": None,
        "session_id": str(uuid.uuid4()),
        "total_tokens": 0,
        "total_duration_seconds": 0
    }
    
    with open(tracker_path, 'w', encoding='utf-8') as f:
        json.dump(tracker_data, f, indent=2)
```

**Tests:**
- [ ] `test_progress_tracker_initialization()`
- [ ] `test_progress_tracker_not_overwritten()`

---

### Task 2.5: Update Tier Classification Logic

**File:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Verify tier classification routing:**
```python
def _classify_complexity(self, operation: str) -> int:
    """
    Classify operation complexity (1-4).
    
    Tier 1-2: temp-plans/ (lightweight, instant response)
    Tier 3-4: active/ (documented, complex planning)
    """
    # ... existing classification logic ...
    
    # Ensure tier 3-4 operations route to active/
    if tier >= 3:
        logger.info(f"Tier {tier} operation routing to active/ folder")
    else:
        logger.info(f"Tier {tier} operation routing to temp-plans/ folder")
    
    return tier
```

**Tests:**
- [ ] `test_tier_1_2_routes_to_temp_plans()`
- [ ] `test_tier_3_4_routes_to_active()`

---

### Task 2.6: Integration with SKULL Rule

**Verify compliance with:** `cortex-brain/brain-protection-rules.yaml`

**STRICT_FOLDER_ORGANIZATION_ENFORCEMENT validation:**
- [ ] Semantic naming quality (intent-based, not rule-based)
- [ ] Universal subfolders created (context/, reports/, artifacts/, tracking/)
- [ ] No root-level files (only in semantic folders)
- [ ] Auto-versioning working (v1, v2, v3)
- [ ] Tier-based routing (temp-plans/ vs active/)

---

## ✅ Completion Criteria

- [ ] All unit tests passing (15 tests)
- [ ] SKULL tests still passing (16 tests)
- [ ] Semantic folder naming enforced
- [ ] Auto-versioning functional
- [ ] Universal subfolders created automatically
- [ ] Progress tracker initialized
- [ ] Tier-based routing working correctly

---

## 📊 Estimated Effort

- **Development:** 10 hours
- **Testing:** 6 hours
- **Total:** 16 hours (2 days)

---

## 🔗 Related Files

- `src/operations/modules/orchestration/planning_orchestrator.py` (lines 512-518)
- `cortex-brain/brain-protection-rules.yaml` (STRICT_FOLDER_ORGANIZATION_ENFORCEMENT)
- `tests/tier0/test_skull_strict_folder_organization.py`
- `tests/orchestrators/test_planning_orchestrator.py`

---

**Status:** Ready to execute  
**Next Phase:** 03 - Plan Lifecycle Management
