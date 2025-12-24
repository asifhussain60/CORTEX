# CORTEX Planner Engagement Fix Plan

## 🧠 CORTEX Critical Fix
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope

**Problem:** CORTEX Planning System not engaging automatically when users request planning work.

**Root Cause Analysis:**

1. **PlanningGate Exists** (`src/entry_point/planning_gate.py`) but has critical gaps:
   - ❌ Weak classification logic (missing "plan", "feature", "add" keywords)
   - ❌ Not integrated into `CortexEntry.process()` workflow
   - ❌ Uses basic keyword matching instead of TieredRouter

2. **TieredRouter Has Proper Patterns** (`src/operations/modules/routing/tiered_router.py`):
   - ✅ TIER_3_PATTERNS includes: `r"plan ado story"`, `r"authentication"`, `r"implement.*"`
   - ✅ TIER_4_PATTERNS includes: `r"architecture"`, `r"migrate.*database"`
   - ✅ Regex-based classification working correctly

3. **Integration Missing:**
   - ❌ `CortexEntry.process()` doesn't invoke `PlanningGate.process_request()` before agent routing
   - ❌ Template-based responses checked first (bypass planning)
   - ❌ No orchestrator engagement hints (🎭) shown to user

**Test Evidence:**
```python
# PlanningGate with weak classification:
gate.process_request("plan a new authentication feature")
# Result: {'complexity_tier': 1, 'proceed_to_execution': True}  ❌ WRONG

# TieredRouter with proper patterns:
router.classify("plan authentication feature")  
# Result: 3  ✅ CORRECT (Tier 3 - DOCUMENTED)
```

**Impact:**
- Users request planning work → CORTEX executes immediately without planning
- Violates SKULL MANDATORY_PLANNING_ENFORCEMENT rule
- No temporary plans created for Tier 3+ work
- No approval gates before complex operations

---

### ⚡ Approach & Considerations

**Challenge:** Integrate PlanningGate into main request flow without breaking existing workflows.

**Constraints:**
1. Must preserve template-based instant responses (help, status, version)
2. Must respect SKULL brain protection rules
3. Must show orchestrator engagement hints (🎭) for visibility
4. Must handle both implicit planning ("add auth") and explicit ("plan auth")

**Solution Strategy:**

**Phase 1: Fix PlanningGate Classification (GREEN PHASE)**
- Replace weak keyword matching with TieredRouter delegation
- PlanningGate becomes thin wrapper over TieredRouter
- Inherit all TIER_1-4 patterns

**Phase 2: Wire PlanningGate into CortexEntry (GREEN PHASE)**
- Insert planning triage BEFORE agent routing
- Order: templates → setup → **PLANNING GATE** → brain protector → routing
- Show 🎭 hints when planning engaged

**Phase 3: SKULL Test Coverage (RED PHASE)**
- Add tests for mandatory planning enforcement
- Verify Tier 3+ work creates temporary plans
- Validate approval gate blocking execution

**Phase 4: Visual Feedback (REFACTOR)**
- Orchestrator engagement hints throughout workflow
- Progress tracking for planning phases
- Clear approval prompts for users

---

### 💬 Response: Implementation Plan

#### Task 1: Enhance PlanningGate Classification

**File:** `src/entry_point/planning_gate.py`

**Change:** Use TieredRouter instead of hardcoded keywords

```python
# BEFORE (lines 100-168):
def _classify_complexity(self, request: str) -> int:
    request_lower = request.lower()
    
    # Hardcoded tier keywords (incomplete)
    tier_4_keywords = ['architecture overhaul', ...]
    tier_3_keywords = ['comprehensive', 'holistic', ...]
    # ... missing 'plan', 'feature', 'add', etc.
    
    return 1  # Default Tier 1 (WRONG for most requests)

# AFTER:
def _classify_complexity(self, request: str) -> int:
    """
    Classify using TieredRouter for consistency.
    Delegates to proven regex patterns.
    """
    if not hasattr(self, '_tiered_router'):
        from src.operations.modules.routing.tiered_router import TieredRouter
        self._tiered_router = TieredRouter()
    
    tier = self._tiered_router.classify(request)
    logger.info(f"🎭 Classified as Tier {tier}: {request[:50]}...")
    return tier
```

**Benefit:** Inherit all 20+ proven patterns from TieredRouter

---

#### Task 2: Wire PlanningGate into CortexEntry

**File:** `src/entry_point/cortex_entry.py`

**Change:** Add planning triage step in `process()` method

```python
# Current flow (lines 334-470):
def process(self, user_message: str, ...):
    # 1. Template response (instant)
    template_response = self._try_template_response(...)
    if template_response:
        return template_response
    
    # 2. Setup command
    if self._is_setup_command(...):
        return self._handle_setup_command(...)
    
    # 3. [MISSING: PLANNING GATE]
    
    # 4. Brain protector
    protection_result = self._validate_with_brain_protector(...)
    
    # 5. Agent routing
    routing_response = self.router.execute(request)

# NEW FLOW:
def process(self, user_message: str, ...):
    # 1. Template response (instant)
    template_response = self._try_template_response(...)
    if template_response:
        return template_response
    
    # 2. Setup command
    if self._is_setup_command(...):
        return self._handle_setup_command(...)
    
    # 3. ✅ PLANNING GATE (NEW)
    planning_result = self._planning_gate_triage(user_message)
    if planning_result['requires_planning']:
        # Create temporary plan, show approval UI
        return self._handle_planning_workflow(planning_result)
    
    # 4. Brain protector
    protection_result = self._validate_with_brain_protector(...)
    
    # 5. Agent routing (only if Tier 1-2)
    routing_response = self.router.execute(request)
```

**New Method:**
```python
@property
def planning_gate(self):
    """Lazy-load Planning Gate."""
    if self._planning_gate is None:
        from src.entry_point.planning_gate import PlanningGate
        self._planning_gate = PlanningGate(cortex_root=config.root_path)
    return self._planning_gate

def _planning_gate_triage(self, user_message: str) -> Dict[str, Any]:
    """
    Route request through planning triage.
    
    Returns dict with:
        - requires_planning: bool
        - complexity_tier: int
        - temp_plan_id: str (if Tier 3+)
        - proceed_to_execution: bool
    """
    logger.info("🎭 Orchestrator engaged: PlanningGate")
    result = self.planning_gate.process_request(user_message)
    
    if result['complexity_tier'] >= 3:
        logger.info(f"🎭 Phase transition: REQUEST → PLANNING (Tier {result['complexity_tier']})")
    
    return result

def _handle_planning_workflow(self, planning_result: Dict[str, Any]) -> str:
    """
    Handle Tier 3+ requests requiring planning.
    
    Creates temporary plan, shows approval UI, blocks execution.
    """
    temp_plan_id = planning_result['temp_plan_id']
    tier = planning_result['complexity_tier']
    
    # Show visual indicator with orchestrator hints
    response = f"""## 🎭 Planning System Engaged

**Complexity:** Tier {tier} ({'DOCUMENTED' if tier == 3 else 'COMPLEX'})
**Temporary Plan:** `{temp_plan_id}`
**Status:** ⏳ Awaiting your approval

### Planning Workflow

- ✅ Phase 1: Complexity analysis complete
- 🔄 Phase 2: Creating temporary plan...
- ⏳ Phase 3: Awaiting your review
- ⏳ Phase 4: Approval gate
- ⏳ Phase 5: Execution with checkpoints

### Your Temporary Plan

Location: `cortex-brain/documents/planning/features/temp-plans/{temp_plan_id}/`

**Next Steps:**
1. Review the temporary plan (opens automatically)
2. Provide feedback or refinements
3. Approve with `/approve {temp_plan_id}` to begin execution
4. Or modify plan and re-submit

**Blocked:** Execution will not proceed until plan approved (SKULL enforcement).
"""
    
    return response
```

---

#### Task 3: Add SKULL Test Coverage

**File:** `tests/tier0/test_mandatory_planning.py` (NEW)

```python
"""
SKULL Tests: Mandatory Planning Enforcement

Validates that Tier 3+ work ALWAYS creates temporary plans
before execution (MANDATORY_PLANNING_ENFORCEMENT rule).

Author: CORTEX TDD System
"""

import pytest
from src.entry_point import CortexEntry, PlanningGate


class TestMandatoryPlanningEnforcement:
    """Test SKULL rule: MANDATORY_PLANNING_ENFORCEMENT."""
    
    def test_tier3_request_creates_temporary_plan(self):
        """Tier 3 requests must create temporary plan."""
        gate = PlanningGate()
        
        result = gate.process_request("plan authentication feature")
        
        assert result['requires_planning'] is True
        assert result['complexity_tier'] == 3
        assert result['proceed_to_execution'] is False
        assert 'temp_plan_id' in result
    
    def test_tier4_request_creates_temporary_plan(self):
        """Tier 4 requests must create temporary plan."""
        gate = PlanningGate()
        
        result = gate.process_request("redesign system architecture")
        
        assert result['requires_planning'] is True
        assert result['complexity_tier'] == 4
        assert result['proceed_to_execution'] is False
        assert 'temp_plan_id' in result
    
    def test_tier1_request_executes_immediately(self):
        """Tier 1 requests execute without planning."""
        gate = PlanningGate()
        
        result = gate.process_request("help")
        
        assert result['requires_planning'] is False
        assert result['complexity_tier'] == 1
        assert result['proceed_to_execution'] is True
    
    def test_cortex_entry_blocks_tier3_without_approval(self):
        """CortexEntry must block Tier 3+ execution until approved."""
        entry = CortexEntry(skip_setup_check=True)
        
        response = entry.process("add authentication to login page")
        
        # Should return planning workflow UI, not execute
        assert "🎭 Planning System Engaged" in response
        assert "Awaiting your approval" in response
        assert "BLOCKED" in response.upper()
    
    def test_planning_gate_uses_tiered_router_patterns(self):
        """PlanningGate must use TieredRouter for classification."""
        gate = PlanningGate()
        
        # Test all tier patterns
        test_cases = [
            ("help", 1),
            ("fix typo in comment", 2),
            ("add authentication feature", 3),
            ("redesign system architecture", 4),
            ("implement login", 3),
            ("plan ado story", 3)
        ]
        
        for request, expected_tier in test_cases:
            result = gate.process_request(request)
            assert result['complexity_tier'] == expected_tier, \
                f"Request '{request}' classified as Tier {result['complexity_tier']}, expected {expected_tier}"
```

---

#### Task 4: Visual Feedback Enhancement

**File:** `src/entry_point/planning_gate.py`

**Enhancement:** Add orchestrator engagement hints throughout

```python
def process_request(self, user_request: str) -> Dict[str, Any]:
    """Process with visual feedback."""
    logger.info("🎭 Orchestrator engaged: PlanningGate")
    
    # Classify
    complexity_tier = self._classify_complexity(user_request)
    logger.info(f"🎭 Phase transition: TRIAGE → TIER_{complexity_tier}_ROUTING")
    
    if complexity_tier >= 3:
        # Create temporary plan
        temp_plan_id = self._create_temporary_plan(user_request, complexity_tier)
        logger.info(f"🎭 Phase transition: ROUTING → PLANNING")
        logger.info(f"🎭 Created temporary plan: {temp_plan_id}")
        
        # Show indicator
        self._show_planning_indicator(complexity_tier, temp_plan_id)
        
        return {
            'requires_planning': True,
            'complexity_tier': complexity_tier,
            'temp_plan_id': temp_plan_id,
            'plan_location': str(self.temp_plans_dir / temp_plan_id),
            'proceed_to_execution': False
        }
    
    # Tier 1-2: proceed
    logger.info(f"🎭 Orchestrator completing: ✅ TIER_{complexity_tier}_APPROVED")
    return {
        'requires_planning': False,
        'complexity_tier': complexity_tier,
        'proceed_to_execution': True
    }
```

---

### 📊 Impact & Changes

**Files Modified:**

1. **`src/entry_point/planning_gate.py`** (57 lines changed)
   - Replace `_classify_complexity()` with TieredRouter delegation
   - Add orchestrator engagement hints
   - Fix missing keywords issue

2. **`src/entry_point/cortex_entry.py`** (110 lines added)
   - Add `planning_gate` property (lazy-load)
   - Add `_planning_gate_triage()` method
   - Add `_handle_planning_workflow()` method
   - Wire into `process()` after templates, before routing

3. **`tests/tier0/test_mandatory_planning.py`** (NEW - 95 lines)
   - RED phase tests for SKULL enforcement
   - Verify temporary plan creation
   - Validate execution blocking
   - Test pattern matching accuracy

**Metrics:**
- **Code Added:** ~200 lines
- **Code Modified:** ~60 lines
- **Tests Added:** 7 tests
- **Coverage Target:** 100% for planning gate flow

**SKULL Compliance:**
- ✅ MANDATORY_PLANNING_ENFORCEMENT: Tier 3+ blocked until approved
- ✅ TDD_ENFORCEMENT: Tests first, implementation second
- ✅ HOLISTIC_CODE_DISCOVERY: Reuse TieredRouter (no duplication)

---

### 🔍 Next Steps

**Immediate (This Session):**
- [ ] **Task 1:** Modify `PlanningGate._classify_complexity()` to use TieredRouter
- [ ] **Task 2:** Wire PlanningGate into `CortexEntry.process()`
- [ ] **Task 3:** Create SKULL tests in `tests/tier0/test_mandatory_planning.py`
- [ ] **Task 4:** Run tests: `pytest tests/tier0/test_mandatory_planning.py -v`

**Validation:**
- [ ] Test: `entry.process("plan authentication")` → Shows planning UI
- [ ] Test: `entry.process("help")` → Instant template response
- [ ] Test: `entry.process("add login feature")` → Tier 3 planning
- [ ] Test: `entry.process("redesign architecture")` → Tier 4 planning

**Documentation:**
- [ ] Update `CORTEX.prompt.md` with planning gate flow
- [ ] Document approval workflow for users
- [ ] Add troubleshooting for "planning not engaging"

**Future Enhancements:**
- [ ] LLM-based classification (fallback to TieredRouter)
- [ ] Auto-approval for trusted patterns
- [ ] Planning template library
- [ ] Approval UI in VS Code sidebar

---

## 🎓 Technical Notes

**Why PlanningGate Classification Failed:**

Original patterns were too specific:
```python
tier_3_keywords = ['comprehensive', 'holistic', 'analyze', 'review', ...]
# Missing: 'plan', 'feature', 'add', 'create', 'implement'
```

TieredRouter has comprehensive regex patterns:
```python
TIER_3_PATTERNS = [
    r"add feature",       # ✅ Matches "add authentication feature"
    r"implement.*function", # ✅ Matches "implement login"  
    r"create.*class",     # ✅ Matches "create auth class"
    r"plan ado story",    # ✅ Matches "plan ado story"
    r"authentication"     # ✅ Matches "authentication"
]
```

**Integration Order Matters:**

Correct flow:
1. Template check (instant: help, status) → Return immediately
2. Setup command → Handle setup workflow
3. **Planning Gate** → Tier 3+ create temp plans, block execution
4. Brain Protector → SKULL validation
5. Agent routing → Only for Tier 1-2 (approved work)

**Visual Feedback Pattern:**

```
User: "plan authentication feature"
↓
🎭 Orchestrator engaged: PlanningGate
🎭 Phase transition: TRIAGE → TIER_3_ROUTING
🎭 Phase transition: ROUTING → PLANNING
🎭 Created temporary plan: TEMP-PLAN-20251216_133045-plan-authent
↓
[Shows approval UI with temp plan location]
```

---

**Plan Version:** 1.0.0  
**Status:** Ready for Implementation  
**TDD Phase:** RED (tests first)  
**Owner:** Asif Hussain
