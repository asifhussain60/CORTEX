# Planning System Root Cause Analysis
**Date:** December 16, 2025  
**Issue:** Temporary planner not engaged, artifacts created in root  
**Author:** CORTEX Analysis Agent  
**Severity:** 🔴 CRITICAL - Core workflow bypassed

---

## Executive Summary

Analysis of chat01.md conversation reveals **critical gaps in planning system invocation**. User request for workspace architecture review did NOT trigger temporary planning workflow, resulting in:

1. ❌ No visual planning indicators shown to user
2. ❌ Analysis document created in root instead of structured folder
3. ❌ Temporary plan not created despite multi-step work
4. ❌ SKULL enforcement bypassed (work without plan)

**Root Cause:** Planning System 3.0 has **no entry point enforcement** - relies on explicit "plan" keyword or manual orchestrator invocation, missing implicit planning scenarios.

---

## Problem Statement

### User Request (chat01.md)
```markdown
"to avoid setting up multiple python environmes for every repo, I've started 
using CORTEX in a workspace setting... Do a holistic review of CORTEX 
architecture and infrastructure and advise on how do enhance it to work in a 
workspace environment. Right now I just set the default at the bottom to the 
target repo. Create a comprehensive plan identifying gaps and how we can make 
it work."
```

### Expected Behavior
1. 🎭 Temporary planner creates TEMP-PLAN-YYYYMMDD-workspace-architecture-review
2. 📊 Visual progress tracker shows: DoR validation → complexity analysis → phase decomposition
3. 📁 Plan artifacts in: `cortex-brain/documents/planning/features/temp-plans/`
4. ✅ User sees: "Creating temporary plan (Tier 3 - DOCUMENTED - 30-60 minutes)"
5. 💬 Back-and-forth refinement before full plan approval

### Actual Behavior
1. ❌ No temporary plan created
2. ❌ Direct execution without planning phase
3. ❌ Document created at: `cortex-brain/documents/planning/CORTEX-4.0-WORKSPACE-ARCHITECTURE-PLAN.md` (root)
4. ❌ No visual indicators of planning workflow
5. ❌ No approval gate before 83-page document generation

---

## Root Cause Analysis

### Investigation Timeline

#### Discovery 1: Multiple Planning Orchestrators
```
FOUND: 14 planning-related orchestrator files
├── src/orchestrators/planning_orchestrator.py (5558 lines - ACTIVE)
├── src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py (888 lines - NEWER?)
├── src/operations/modules/orchestration/planning_orchestrator.py (exists?)
├── src/operations/modules/orchestration/ado_planning_orchestrator.py (ADO variant)
└── archive/cortex-brain/backups/obsolete-code/.../planning_orchestrator.py (2 archived)
```

**Conflict Identified:** Multiple implementations with unclear precedence

#### Discovery 2: Temporary Plan Manager Exists But Not Invoked
```python
# src/operations/modules/orchestration/temporary_plan_manager.py (681 lines)
class TemporaryPlanManager:
    """
    Manages temporary plans for implicit task requests.
    
    Workflow:
    1. User provides tasks without saying "create a plan"
    2. CORTEX creates temporary plan in active/ folder  # ← THIS DID NOT HAPPEN
    3. Back-and-forth refinement with user
    4. User explicitly approves (or rejects)
    """
```

**Status:** ✅ Implementation exists, ❌ Integration missing

#### Discovery 3: No Entry Point Enforcement
```yaml
# cortex-brain/brain-protection-rules.yaml
tier0_instincts:
  - TIERED_PLANNING_ENFORCEMENT  # ← EXISTS IN LIST
  # BUT: No detection rules defined for it!
```

**Gap:** SKULL rule exists but has no enforcement logic

#### Discovery 4: Planning System 3.0 Manifest
```yaml
# cortex-brain/orchestrator-manifests/planning-system-3.0-manifest.yaml
components:
  temporary_plan_manager:
    enabled: true
    source: "src/operations/modules/orchestration/temporary_plan_manager.py"
    description: "Manage implicit planning workflow"
    lifecycle:
      - "create" # User tasks without "create plan"  # ← SHOULD HAVE TRIGGERED
```

**Status:** Manifest declares capability, implementation never called

### Root Causes Identified

#### RC-1: No Request Interception Layer
**Problem:** User requests go directly to execution agents without planning triage.

**Evidence:**
- chat01.md shows immediate analysis document generation
- No planning orchestrator invoked
- No temporary plan creation logged

**Missing Component:** Request interceptor that routes all work through planning first

#### RC-2: Keyword-Based Planning Detection
**Problem:** Planning only triggered by explicit "plan" keyword.

**Evidence from chat01.md:**
```markdown
User: "Do a holistic review... Create a comprehensive plan"
               ^^^^^^^^^^^^^^ Only this triggered planning
               
But: "holistic review" should have triggered Tier 3 (DOCUMENTED) routing
```

**Current Logic:**
```python
# Intent detection looks for:
if "plan" in request.lower():
    route_to_planning_orchestrator()
else:
    route_to_execution()  # ← BYPASSES PLANNING
```

#### RC-3: Planning System Not in Tier 0 Governance
**Problem:** Planning is optional, not enforced.

**Brain Protection Rules Missing:**
```yaml
# SHOULD EXIST BUT DOESN'T:
- rule_id: MANDATORY_PLANNING_ENFORCEMENT
  name: All Multi-Step Work Requires Planning
  severity: blocked
  description: "No work exceeding Tier 2 complexity without approved plan"
  detection:
    multi_step_indicators:
      - "analyze and recommend"
      - "review and advise"
      - "comprehensive"
      - "holistic"
    complexity_signals:
      - multiple deliverables
      - architecture changes
      - >30 minute estimated work
  alternatives:
    - Create temporary plan first
    - Get user approval
    - Execute with checkpoints
```

#### RC-4: Temporary Plan Manager Not Wired to Entry Point
**Problem:** TemporaryPlanManager exists but never instantiated at request entry.

**Evidence:**
```python
# src/orchestrators/planning_orchestrator.py __init__
# NO REFERENCE TO TemporaryPlanManager integration
# Manual instantiation required (never happens automatically)
```

#### RC-5: No Visual Planning Indicators
**Problem:** Even when planning runs, user sees no progress.

**Manifest Declares:**
```yaml
visual_progress_tracker:
  enabled: true
  location: "User responses and master plans (00-master-plan.md)"
  # BUT: Not rendering in chat responses during planning
```

---

## Impact Assessment

### User Experience Impact

| Issue | User Impact | Frequency | Severity |
|-------|-------------|-----------|----------|
| No planning indication | Confusion about CORTEX process | Every implicit request | 🔴 High |
| Root-level artifacts | File disorganization | Every planning output | 🟡 Medium |
| SKULL bypass | Quality standards not enforced | Unknown (silent failure) | 🔴 Critical |
| No approval gates | Can't refine before execution | Every large request | 🟡 Medium |

### System Integrity Impact

1. **SKULL Violation:** Work executed without mandatory planning (brain protection bypassed)
2. **Tier 0 Integrity:** Instincts not enforced (governance failure)
3. **Unified Planning:** System fragmented across multiple implementations
4. **Test Coverage:** No tests validating planning invocation (gap)

---

## Similar Incidents

### Historical Context
Searched knowledge graph and conversation history:

1. **Issue #Unknown (Implicit):** Planning system added but never integrated to entry point
2. **Phase 13:** UnifiedPlanGenerator created but parallel systems still exist
3. **Planning System 3.0:** Manifest created but orchestrator not updated to match

**Pattern:** Features built but not integrated into request workflow.

---

## Remediation Plan

### Phase 1: Immediate Fixes (Week 1)

#### Fix 1.1: Add Request Interception Layer
**File:** `src/entry_point/planning_gate.py` (NEW)

```python
"""
Planning Gate - Routes all requests through planning triage.
"""
from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
from src.operations.modules.routing.tiered_router import TieredRouter

class PlanningGate:
    """Intercepts all requests for planning triage."""
    
    def __init__(self):
        self.temp_plan_manager = TemporaryPlanManager()
        self.tiered_router = TieredRouter()
    
    def process_request(self, user_request: str) -> Dict[str, Any]:
        """
        Route request through planning system first.
        
        Returns:
            {
                'requires_planning': bool,
                'complexity_tier': int,
                'temp_plan_id': str (if created),
                'proceed_to_execution': bool
            }
        """
        # Classify complexity
        tier = self.tiered_router.classify(user_request)
        
        # Tier 1-2: Execute directly (no planning needed)
        if tier <= 2:
            return {
                'requires_planning': False,
                'complexity_tier': tier,
                'proceed_to_execution': True
            }
        
        # Tier 3-4: Create temporary plan FIRST
        temp_plan = self.temp_plan_manager.create_temporary_plan(
            user_request=user_request,
            complexity_tier=tier,
            estimated_time=self._estimate_time(tier),
            approach=self._initial_approach(user_request)
        )
        
        return {
            'requires_planning': True,
            'complexity_tier': tier,
            'temp_plan_id': temp_plan.plan_id,
            'proceed_to_execution': False,  # Wait for approval
            'plan_location': str(temp_plan_folder)
        }
```

**Integration Point:** Wire into Copilot Chat entry point

#### Fix 1.2: Add SKULL Planning Enforcement Rule
**File:** `cortex-brain/brain-protection-rules.yaml`

```yaml
- rule_id: MANDATORY_PLANNING_ENFORCEMENT
  name: Mandatory Planning for Complex Work
  severity: blocked
  description: "All Tier 3-4 work MUST have approved plan before execution"
  detection:
    combined_keywords:
      complexity_signals:
        - "comprehensive"
        - "holistic"
        - "architecture"
        - "analysis"
        - "review"
        - "multiple phases"
        - "identify gaps"
      multi_step_indicators:
        - "analyze and"
        - "review and"
        - "create and execute"
        - "implement with"
    scope:
      - intent
      - description
      - estimated_scope
  enforcement:
    tier_threshold: 3  # Tier 3+ requires planning
    bypass_conditions:
      - user_explicitly_skips: false  # Cannot be bypassed
      - tier_1_2_work: true  # Allow instant/lightweight
  alternatives:
    - "BLOCKED: Create temporary plan first"
    - "Route through PlanningGate for complexity classification"
    - "Show visual progress: DoR → Complexity → Phases → Approval"
    - "Only proceed after user explicitly approves plan"
  evidence_template: |
    ❌ BLOCKED: Tier {tier} work requires approved plan
    
    Request: '{user_request}'
    Complexity: {complexity_tier}
    Estimated Time: {estimated_time}
    
    MANDATORY WORKFLOW:
    1. ⏳ Creating temporary plan...
    2. 📊 Showing complexity analysis...
    3. 💬 Awaiting your approval...
    4. ✅ Executing with checkpoints...
    
    Creating temporary plan now...
  rationale: |
    All non-trivial work must go through planning:
    - Prevents scope creep (explicit boundaries)
    - Enables user feedback before execution
    - Ensures deliverables match expectations
    - Provides execution checkpoints
    - Enforces CORTEX quality standards (DoR/DoD)
```

#### Fix 1.3: Wire Planning Gate to Entry Point
**File:** `src/entry_point/cortex_entry.py`

```python
from src.entry_point.planning_gate import PlanningGate

class CortexEntry:
    def __init__(self):
        # ... existing init ...
        self.planning_gate = PlanningGate()  # NEW
    
    def process(self, request: str) -> Dict[str, Any]:
        """Process request through planning gate first."""
        
        # NEW: Planning triage
        triage_result = self.planning_gate.process_request(request)
        
        if triage_result['requires_planning']:
            # Show temporary plan to user
            return self._show_temp_plan(triage_result['temp_plan_id'])
        
        # Tier 1-2: Execute directly
        return self._execute(request)
```

#### Fix 1.4: Add Visual Planning Indicators
**File:** `src/operations/modules/orchestration/temporary_plan_manager.py`

```python
def create_temporary_plan(self, ...) -> TemporaryPlan:
    """Create temporary plan with visual progress."""
    
    # NEW: Show visual indicator
    self._show_planning_start(complexity_tier, estimated_time)
    
    temp_plan = TemporaryPlan(...)
    
    # NEW: Render visual progress
    progress = self._render_planning_progress(temp_plan)
    
    return temp_plan

def _show_planning_start(self, tier: int, time: str):
    """Show visual planning indicator to user."""
    print(f"""
## 🎭 Planning System Engaged
**Complexity:** Tier {tier} ({self._tier_name(tier)})
**Estimated Time:** {time}
**Status:** Creating temporary plan...

⏳ Phase 1: Definition of Ready validation
⏳ Phase 2: Complexity analysis
⏳ Phase 3: Phase decomposition
⏳ Phase 4: Risk assessment
⏳ Phase 5: Approval gate

You'll see the plan shortly for review and approval.
""")
```

### Phase 2: Consolidation (Week 2)

#### Action 2.1: Unify Planning Orchestrators
**Problem:** 3+ implementations causing confusion

**Solution:**
1. **Keep:** `src/orchestrators/planning_orchestrator.py` (most mature)
2. **Deprecate:** `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
3. **Specialize:** `src/operations/modules/orchestration/ado_planning_orchestrator.py` (ADO-specific, inherits base)
4. **Archive:** Remaining duplicates

**Migration:**
- Move Planning System 3.0 enhancements to main orchestrator
- Update manifest to reference single source
- Add deprecation warnings to old files

#### Action 2.2: Document Organization Enforcement
**File:** `cortex-brain/brain-protection-rules.yaml` (ADD)

```yaml
- rule_id: PLAN_ARTIFACT_LOCATION_ENFORCEMENT
  name: Planning Artifacts Must Use Folder Structure
  severity: blocked
  description: "All planning artifacts in cortex-brain/documents/planning/features/{status}/"
  detection:
    keywords:
      - "creating plan"
      - "generating plan"
      - "save plan to"
    scope:
      - file_operations
      - artifact_creation
  enforcement:
    allowed_paths:
      - "cortex-brain/documents/planning/features/temp-plans/"
      - "cortex-brain/documents/planning/features/active/"
      - "cortex-brain/documents/planning/features/completed/"
    forbidden_paths:
      - "cortex-brain/documents/planning/*.md"  # Root level
      - "CORTEX/*.md"  # Project root
  alternatives:
    - "Use PlanFolderManager.create_plan_structure()"
    - "Save to: cortex-brain/documents/planning/features/temp-plans/{plan-id}/"
    - "Follow folder-based artifact organization"
```

### Phase 3: Testing & Validation (Week 3)

#### Test Suite: Planning Invocation
**File:** `tests/integration/test_planning_invocation.py` (NEW)

```python
"""
Integration tests for planning system invocation.
Validates that planning is triggered for appropriate requests.
"""
import pytest
from src.entry_point.cortex_entry import CortexEntry
from src.entry_point.planning_gate import PlanningGate

class TestPlanningInvocation:
    """Test planning system is correctly invoked."""
    
    @pytest.fixture
    def cortex_entry(self):
        return CortexEntry()
    
    def test_tier_3_triggers_planning(self, cortex_entry):
        """Tier 3 (DOCUMENTED) work triggers temporary planning."""
        request = "Do a comprehensive analysis of the architecture"
        
        result = cortex_entry.process(request)
        
        assert result['requires_planning'] == True
        assert result['complexity_tier'] == 3
        assert 'temp_plan_id' in result
        assert result['proceed_to_execution'] == False  # Wait for approval
    
    def test_tier_4_triggers_planning(self, cortex_entry):
        """Tier 4 (COMPLEX) work triggers nested planning."""
        request = "Create a comprehensive plan for workspace architecture"
        
        result = cortex_entry.process(request)
        
        assert result['requires_planning'] == True
        assert result['complexity_tier'] == 4
        assert 'temp_plan_id' in result
    
    def test_tier_1_skips_planning(self, cortex_entry):
        """Tier 1 (INSTANT) work skips planning."""
        request = "What's the current Python version?"
        
        result = cortex_entry.process(request)
        
        assert result['requires_planning'] == False
        assert result['proceed_to_execution'] == True
    
    def test_implicit_planning_keywords(self, cortex_entry):
        """Implicit planning keywords trigger workflow."""
        requests_requiring_planning = [
            "Analyze the codebase holistically",
            "Review architecture and recommend improvements",
            "Identify gaps in the system",
            "Create comprehensive documentation",
            "Do a deep dive into performance issues"
        ]
        
        for request in requests_requiring_planning:
            result = cortex_entry.process(request)
            assert result['requires_planning'] == True, f"Failed: {request}"
    
    def test_visual_indicator_shown(self, cortex_entry, capsys):
        """Visual planning indicator shown to user."""
        request = "Comprehensive architecture analysis"
        
        cortex_entry.process(request)
        
        captured = capsys.readouterr()
        assert "🎭 Planning System Engaged" in captured.out
        assert "Creating temporary plan" in captured.out
        assert "Phase 1:" in captured.out
    
    def test_artifacts_in_correct_folder(self, cortex_entry, tmp_path):
        """Planning artifacts created in temp-plans/ folder."""
        request = "Analyze and recommend architecture changes"
        
        result = cortex_entry.process(request)
        
        temp_plan_id = result['temp_plan_id']
        expected_path = tmp_path / "cortex-brain" / "documents" / "planning" / "features" / "temp-plans" / temp_plan_id
        assert expected_path.exists()
    
    def test_no_root_level_artifacts(self, cortex_entry, tmp_path):
        """No artifacts created at root level."""
        request = "Create comprehensive plan"
        
        cortex_entry.process(request)
        
        root_plans = list((tmp_path / "cortex-brain" / "documents" / "planning").glob("*.md"))
        assert len(root_plans) == 0, "Root-level artifacts found (should be in subfolders)"
```

**Coverage Target:** 100% for planning invocation logic

#### Test Suite: SKULL Enforcement
**File:** `tests/unit/test_skull_planning_enforcement.py` (NEW)

```python
"""Test SKULL planning enforcement rules."""
import pytest
from src.tier0.brain_protector import BrainProtector

class TestSKULLPlanningEnforcement:
    """Test MANDATORY_PLANNING_ENFORCEMENT SKULL rule."""
    
    @pytest.fixture
    def brain_protector(self):
        return BrainProtector()
    
    def test_tier_3_without_plan_blocked(self, brain_protector):
        """Tier 3 work without plan is blocked."""
        request = {
            'intent': 'analyze architecture comprehensively',
            'has_plan': False,
            'complexity_tier': 3
        }
        
        result = brain_protector.validate(request)
        
        assert result.is_blocked == True
        assert "MANDATORY_PLANNING_ENFORCEMENT" in result.rule_id
        assert "Create temporary plan first" in result.alternatives[0]
    
    def test_tier_1_without_plan_allowed(self, brain_protector):
        """Tier 1 work without plan is allowed."""
        request = {
            'intent': 'quick calculation',
            'has_plan': False,
            'complexity_tier': 1
        }
        
        result = brain_protector.validate(request)
        
        assert result.is_blocked == False
    
    def test_approved_plan_allows_execution(self, brain_protector):
        """Approved plan allows Tier 3+ execution."""
        request = {
            'intent': 'comprehensive analysis',
            'has_plan': True,
            'plan_approved': True,
            'complexity_tier': 4
        }
        
        result = brain_protector.validate(request)
        
        assert result.is_blocked == False
```

---

## Prevention Strategy

### Governance Updates

#### 1. Planning System Manifest Compliance
**Action:** Enforce manifest-code alignment

```yaml
# cortex-brain/orchestrator-manifests/planning-system-3.0-manifest.yaml
validation:
  manifest_tests:
    - test: "temporary_plan_manager integrated to entry point"
      validation_file: "tests/integration/test_planning_invocation.py"
      required_coverage: 100%
    
    - test: "SKULL enforcement active"
      validation_file: "tests/unit/test_skull_planning_enforcement.py"
      required_coverage: 100%
    
    - test: "Visual indicators rendering"
      validation_file: "tests/integration/test_planning_ux.py"
      required_coverage: 100%
```

#### 2. Entry Point Verification
**Test:** `tests/smoke/test_entry_point_planning.py`

```python
def test_entry_point_has_planning_gate():
    """Entry point MUST have planning gate integration."""
    from src.entry_point.cortex_entry import CortexEntry
    
    entry = CortexEntry()
    assert hasattr(entry, 'planning_gate'), "Planning gate not integrated!"
    assert entry.planning_gate is not None

def test_planning_gate_wired():
    """Planning gate MUST intercept all requests."""
    from src.entry_point.cortex_entry import CortexEntry
    
    entry = CortexEntry()
    # Simulate Tier 3 request
    result = entry.process("Do comprehensive analysis")
    
    assert 'requires_planning' in result, "Planning gate not invoked!"
```

#### 3. Continuous Monitoring
**Metric:** Track planning invocation rate

```python
# src/tier3/planning_metrics.py
def track_planning_invocation():
    """Track planning system usage."""
    metrics = {
        'total_requests': count_all_requests(),
        'tier_3_plus_requests': count_tier_3_plus(),
        'planning_invocations': count_planning_invocations(),
        'planning_skipped': count_tier_3_plus() - count_planning_invocations()
    }
    
    # Alert if planning skipped for Tier 3+ work
    if metrics['planning_skipped'] > 0:
        alert_governance_violation(metrics)
```

---

## Success Criteria

### Functional Requirements
- [ ] All Tier 3+ requests trigger temporary planning
- [ ] Visual indicators shown during planning phase
- [ ] Artifacts created in `features/temp-plans/` folder
- [ ] SKULL enforcement blocks work without approved plan
- [ ] Single unified planning orchestrator
- [ ] 100% test coverage for planning invocation

### User Experience Requirements
- [ ] User sees "🎭 Planning System Engaged" for Tier 3+ work
- [ ] Progress tracker shows: DoR → Complexity → Phases → Approval
- [ ] User can refine plan before execution
- [ ] Clear folder structure (no root-level artifacts)

### Quality Requirements
- [ ] No SKULL violations (brain protection active)
- [ ] Manifest compliance validated by tests
- [ ] Smoke tests run on every commit
- [ ] Planning metrics monitored in dashboard

---

## Timeline

### Week 1: Critical Fixes
- Day 1: Implement PlanningGate + SKULL rule
- Day 2: Wire to entry point + visual indicators
- Day 3: Integration tests
- Day 4-5: User acceptance testing

### Week 2: Consolidation
- Day 6-7: Unify orchestrators
- Day 8: Document organization enforcement
- Day 9: Update manifests
- Day 10: Regression testing

### Week 3: Validation
- Day 11-12: Comprehensive test suite
- Day 13: SKULL enforcement validation
- Day 14: Smoke tests + metrics
- Day 15: Documentation + release

---

## Lessons Learned

### What Went Wrong
1. **Feature built but not integrated** - TemporaryPlanManager exists but never called
2. **Keyword-based detection insufficient** - Missed "holistic review" as planning trigger
3. **SKULL rules incomplete** - TIERED_PLANNING_ENFORCEMENT declared but not enforced
4. **No entry point tests** - Planning invocation never validated

### What Went Right
1. **Manifest documented intent** - Planning System 3.0 manifest clearly defined expected behavior
2. **Implementation exists** - TemporaryPlanManager code is solid, just needs wiring
3. **User feedback clear** - chat01.md provided excellent evidence of failure

### Process Improvements
1. **Manifest-driven development** - Enforce manifest compliance with tests
2. **Entry point testing** - All request flows must have smoke tests
3. **Integration validation** - Features must prove integration before merge
4. **Visual feedback** - Users must see system state changes (planning engagement)

---

## Appendix

### Reference Files
- chat01.md - Original conversation showing failure
- planning-system-3.0-manifest.yaml - Expected behavior
- temporary_plan_manager.py - Existing implementation
- brain-protection-rules.yaml - SKULL enforcement

### Related Issues
- Planning System 3.0 implementation (partial)
- UnifiedPlanGenerator integration (partial)
- Folder-based artifact organization (incomplete)

### Stakeholders
- @asifhussain60 - Product owner, identified issue
- CORTEX Analysis Agent - RCA execution
- Planning Team - Remediation implementation

---

**Status:** 🟡 In Progress - Remediation Week 1  
**Next Review:** December 23, 2025  
**Owner:** Planning Team
