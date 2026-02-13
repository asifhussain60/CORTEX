# Phase 33 Integration Plan: Wire Verbosity Policies into CORTEX Execution

**Status:** READY FOR IMPLEMENTATION  
**Phase:** 33 (Architecture Alignment & Governance)  
**Effort:** 2 weeks | **Priority:** P0 (HIGH ROI: 0.70)  
**Authority:** Phases 29, 31, 31A + chat02.txt requirements

---

## 🎯 What Needs to Happen

Current state: All verbosity reduction code is written but **not in the execution path**.

Target state: All responses automatically compressed via policy pipeline before returning to user.

### Policy Execution Path (MISSING)

```
User Request
    ↓
MasterOrchestrator (NEEDS WIRING)
    ↓
  [NEW] ChatResponsePolicyValidator.validate_response_structure()
    ↓
  [NEW] suppress_verbosity(response)
    ↓
  [NEW] inject_plan_spine(response, phases)
    ↓
  [NEW] MarkdownReportBanPolicy.validate_no_writes()
    ↓
  [NEED TO UPDATE] UnifiedResponseComposer.format() [COMPACT mode]
    ↓
  [NEED TO UPDATE] BusinessLanguageOrchestrator.translate() [role-inclusive]
    ↓
User sees concise, 3-section response ✅
```

---

## 📍 Integration Points (Exact Locations)

### 1. MasterOrchestrator Response Pipeline (PRIMARY)

**File:** `cortex/orchestrators/master/master_orchestrator.py`

**Location:** Find `compose_response()` or equivalent method that returns final response

**What to Add:**

```python
from cortex.orchestrators.response.chat_response_policy import (
    ChatResponsePolicyValidator,
    suppress_verbosity,
    inject_plan_spine,
)
from cortex.orchestrators.response.markdown_report_ban_policy import (
    MarkdownReportBanPolicy,
)

def compose_response(
    self,
    content: str,
    operation: str = "IMPLEMENT",
    phases: Optional[List[Tuple[str, str]]] = None,
    **kwargs
) -> str:
    """Compose final response with policies applied."""
    
    # 1. Suppress verbosity (remove "Let me", "Perfect!", tool narration)
    response = suppress_verbosity(content)
    
    # 2. Inject compact plan spine if phases provided
    if phases:
        response = inject_plan_spine(response, phases, section_index=1)
    
    # 3. Validate 3-section structure
    validator = ChatResponsePolicyValidator()
    is_valid, errors = validator.validate_full_response(response)
    
    if not is_valid:
        # Log violations, but don't fail (graceful degradation)
        self.logger.warning(f"Response policy violations: {errors}")
    
    # 4. Apply business language (role-inclusive)
    response = self.business_language_orchestrator.compress_to_business_language(
        response,
        role_context=kwargs.get('target_roles', ['all']),
    )
    
    # 5. Format with COMPACT profile
    response = self.unified_response_composer.format(
        content=response,
        profile=FormattingProfile.COMPACT,  # Not STANDARD
        include_header=True,
        header_operation=operation,
    )
    
    return response
```

**Tests to Add:**
```python
# tests/integration/test_master_orchestrator_policy_integration.py
test_policies_applied_to_responses()
test_verbosity_suppression_active()
test_3_section_structure_enforced()
test_markdown_report_ban_active()
test_policy_bypass_prevented()  # Ensure policies are NOT optional
```

---

### 2. InteractionOrchestrator (SECONDARY)

**File:** `cortex/orchestrators/interaction/interaction_orchestrator.py`

**Location:** Find `_compose_response()` method

**What to Change:**

```python
class InteractionOrchestrator:
    
    def __init__(self, ...):
        # ADD THIS:
        self.narration_suppression_enabled = True
        self.autonomous_mode = False
        
    def set_autonomous_mode(self, enabled: bool) -> None:
        """Set autonomous execution mode (suppress preference questions)."""
        self.autonomous_mode = enabled
    
    def _compose_response(self, response: str) -> str:
        """Compose response with narration filtering."""
        
        if not self.narration_suppression_enabled:
            return response
        
        # Filter out blocked patterns
        blocked_patterns = [
            r"Which approach do you prefer\?",  # No choices after autonomous trigger
            r"(?:Let me|Now let me|Let's) \w+",  # "Let me read", "Let's check"
            r"\b(?:Perfect|Good|Excellent|Great)!\b",  # Filler exclamations
            r"(?:Ran terminal command|Read \[|Using )",  # Tool call narration
        ]
        
        result = response
        for pattern in blocked_patterns:
            result = re.sub(pattern, "", result, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        result = re.sub(r"\n{3,}", "\n\n", result)
        
        return result.strip()
```

**Tests to Add:**
```python
# tests/integration/test_interaction_orchestrator_narration_filtering.py
test_let_me_patterns_filtered()
test_perfect_good_excellent_removed()
test_tool_call_narration_removed()
test_choice_questions_blocked_in_autonomous_mode()
test_whitespace_cleanup()
```

---

### 3. UnifiedResponseComposer (TERTIARY)

**File:** `cortex/orchestrators/response/unified_response_composer.py`

**Location:** Find `format()` method or response formatting logic

**What to Change:**

```python
class UnifiedResponseComposer:
    
    DEFAULT_PROFILE = FormattingProfile.COMPACT  # Change from STANDARD
    
    def format(
        self,
        content: str,
        operation: str = "IMPLEMENT",
        profile: Optional[FormattingProfile] = None,
        include_header: bool = True,
        target_roles: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Format response with optional business language."""
        
        # Default to COMPACT for chat mode (unless explicitly VERBOSE)
        profile = profile or self.DEFAULT_PROFILE
        
        # Apply business language if target roles specified
        if target_roles and target_roles != ['all']:
            # Only compress if specific roles need accessibility
            if 'business' in target_roles or 'po' in target_roles:
                # Wire BusinessLanguageOrchestrator here
                content = self._apply_business_language(content)
        
        # Continue with existing formatting logic...
        return self._apply_profile(content, profile, include_header, operation)
    
    def _apply_business_language(self, content: str) -> str:
        """Translate technical language to business language."""
        return self.business_language_orchestrator.compress_to_business_language(
            content,
            exclude_technical_terms=False,  # Keep critical terms
            max_words_per_bullet=20,
        )
```

**Tests to Add:**
```python
# tests/integration/test_unified_composer_business_language.py
test_default_profile_is_compact()
test_business_language_applied_for_business_role()
test_compact_profile_reduces_lines()
test_technical_terms_preserved()
```

---

## 🧪 Test Suite to Add (40+ tests)

### Test File 1: Policy Integration
```python
# tests/integration/test_response_policy_integration.py
# 15 tests

class TestResponsePolicyPipeline:
    def test_all_policies_applied_in_order()
    def test_verbosity_suppression_active()
    def test_3_section_structure_enforced()
    def test_plan_spine_injected()
    def test_business_language_applied()
    def test_compact_formatting_used()
    def test_policies_not_bypassable()
    def test_output_length_60_percent_reduction()
    def test_token_count_73_percent_reduction()
    def test_narration_completely_removed()
    def test_backward_compatibility()
    def test_existing_tests_still_pass()
    def test_markdown_report_ban_active()
    def test_audit_logging_working()
    def test_metrics_tracked()
```

### Test File 2: MasterOrchestrator Integration
```python
# tests/integration/test_master_orchestrator_policy_integration.py
# 12 tests

class TestMasterOrchestratorPolicies:
    def test_policies_called_by_master_orchestrator()
    def test_response_length_reduced()
    def test_3_sections_validated()
    def test_plan_spine_displayed()
    def test_business_language_active()
    def test_audit_trail_logged()
    def test_violations_tracked()
    def test_performance_under_50ms()
    def test_context_overflow_prevented()
    def test_role_context_propagated()
    def test_autonomous_mode_enforced()
    def test_integrity_maintained()
```

### Test File 3: End-to-End Scenarios
```python
# tests/integration/test_autonomous_execution_verbosity.py
# 13 tests

class TestAutonomousExecutionVerbosity:
    def test_phase_implementation_response_format()
    def test_fix_bug_response_format()
    def test_refactor_code_response_format()
    def test_analyze_codebase_response_format()
    def test_business_leader_understands_response()
    def test_product_owner_understands_response()
    def test_production_owner_understands_response()
    def test_engineer_understands_response()
    def test_tool_narration_absent()
    def test_preference_questions_blocked()
    def test_markdown_reports_blocked()
    def test_context_budget_respected()
    def test_all_acceptance_criteria_met()
```

---

## ✅ Acceptance Criteria (Must Pass)

### Functional
- [ ] **AC-VER-001:** Every response has EXACTLY 3 sections
- [ ] **AC-VER-002:** Zero "Let me", "Perfect!", tool narration
- [ ] **AC-VER-003:** No markdown report files created
- [ ] **AC-VER-004:** Plan spine ≤ 3 lines
- [ ] **AC-VER-005:** Business language accessible to 4 roles

### Non-Functional
- [ ] **AC-VER-NF-001:** Response length ≤ 247 lines (60% reduction from 617)
- [ ] **AC-VER-NF-002:** Token count ≤ 4,000 tokens per response (73% reduction)
- [ ] **AC-VER-NF-003:** Policy enforcement latency < 50ms
- [ ] **AC-VER-NF-004:** 100% existing tests pass (zero breaking changes)
- [ ] **AC-VER-NF-005:** Context overflow 1 per 1000 lines (vs 1 per 13.7)

---

## 📦 Deliverables Checklist

### Code Changes
- [ ] Update MasterOrchestrator.compose_response() [~50 LOC]
- [ ] Update InteractionOrchestrator._compose_response() [~40 LOC]
- [ ] Update UnifiedResponseComposer.format() [~30 LOC]
- [ ] Add response policy configuration [~20 LOC]
- [ ] Add audit logging [~30 LOC]
- [ ] Add metrics tracking [~25 LOC]

**Total New Code:** ~195 LOC

### Tests
- [ ] test_response_policy_integration.py [~380 LOC, 15 tests]
- [ ] test_master_orchestrator_policy_integration.py [~320 LOC, 12 tests]
- [ ] test_autonomous_execution_verbosity.py [~400 LOC, 13 tests]

**Total New Tests:** ~1,100 LOC, 40 tests

### Documentation
- [ ] Update CORTEX.prompt.md (response format section)
- [ ] Update cortex-architect.prompt.md (policy enforcement)
- [ ] Add INTEGRATION.md (how policies work)
- [ ] Update README.md (reference policies)

---

## 🚀 Implementation Sequence (TDD-First)

### Day 1-2: Write Tests
```bash
# Create test files with comprehensive scenarios
tests/integration/test_response_policy_integration.py
tests/integration/test_master_orchestrator_policy_integration.py
tests/integration/test_autonomous_execution_verbosity.py

# Run tests (all should FAIL - RED phase)
pytest tests/integration/test_*_policy_*.py -v
```

### Day 3-5: Implement Integration
```python
# Wire policies into execution path
1. MasterOrchestrator.compose_response()
2. InteractionOrchestrator._compose_response()
3. UnifiedResponseComposer.format()

# Run tests (should turn GREEN)
pytest tests/integration/test_*_policy_*.py -v --tb=short
```

### Day 6-7: Validation & Docs
```bash
# Ensure all existing tests still pass
pytest tests/ -v

# Add documentation
# Update prompts
# Create user guide
```

### Day 8-10: Launch & Monitor
```bash
# Deploy to production
# Monitor metrics
# Measure actual impact vs projections
# Iterate based on feedback
```

---

## 📊 Success Metrics

### Before/After Measurements

**Response Length (using chat01.txt as baseline)**
```
Before: 1,281 lines (617 if compressed to Phase 31 + 31A)
After:  ≤ 247 lines (60% reduction target)
Success: Achieve ≤ 247 lines on comparable tasks
```

**Token Usage**
```
Before: ~15,000 tokens per response
After:  ≤ 4,000 tokens per response (73% reduction)
Success: Measure token count before/after
```

**Narration Elimination**
```
Before: 450 lines of narration (35% of content)
After:  0 lines of narration
Success: Zero tool call narration in responses
```

**Executive Accessibility**
```
Before: <30 seconds scan time (mostly skimming)
After:  <15 seconds scan time (full comprehension)
Success: User survey: "Response is easy to understand" (4/4 roles)
```

---

## 🔗 Related Files (Ready to Use)

```
✅ cortex/orchestrators/response/chat_response_policy.py (580 LOC)
✅ cortex/orchestrators/response/markdown_report_ban_policy.py (420 LOC)
✅ cortex/orchestrators/response/minimal_plan_spine.py (240 LOC)
✅ tests/unit/orchestrators/response/test_chat_response_and_report_ban_policies.py (770 LOC, 41 tests)
✅ tests/unit/orchestrators/response/test_minimal_plan_spine.py (280 LOC, 13 tests)

cortex/orchestrators/master/master_orchestrator.py (NEEDS WIRING)
cortex/orchestrators/interaction/interaction_orchestrator.py (NEEDS WIRING)
cortex/orchestrators/response/unified_response_composer.py (NEEDS WIRING)
```

---

## 📋 Go/No-Go Decision Criteria

### Prerequisites (All Must Be ✅)
- [ ] Phase 31, 31A fully tested & passing
- [ ] MasterOrchestrator architecture understood
- [ ] InteractionOrchestrator architecture understood
- [ ] UnifiedResponseComposer architecture understood
- [ ] Test framework in place (pytest)

### Go Criteria (Start Implementation If All ✅)
- [ ] All prerequisites met
- [ ] Acceptance criteria defined
- [ ] Test suite ready to implement
- [ ] Integration points identified
- [ ] Rollback plan documented

**Status:** ✅ **READY TO PROCEED**

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-06  
**Phase:** 33 (Architecture Alignment & Governance)  
**Ready for:** Immediate Implementation Kickoff
