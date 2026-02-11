# 🚀 CORTEX Response Template Migration: Phase 50-52 Action Plan

**Created:** 2026-02-10  
**Authority:** cortex-architect.prompt.md v15.3  
**Urgency:** P0 CRITICAL  
**Owner:** GitHub Copilot (CORTEX Architect)

---

## Overview

This document provides a **step-by-step remediation plan** to fix the **critical gaps in CORTEX orchestrator response template compliance**:

- 🔴 193/263 orchestrators (73.4%) lack template inheritance
- 🔴 195/263 orchestrators (74.1%) lack compose() methods
- 🔴 263/263 orchestrators (100%) not Copilot Chat ready
- 🔴 3 CORE-049 (silent mode) violations

**Timeline:** 3 weeks (Phase 50-52)  
**Effort:** 60-80 hours  
**Outcome:** 100% template compliance, full Copilot Chat readiness

---

## Phase 50: Rapid Response (Week 1)

### Day 1-2: Discovery & Mapping

#### Task 1.1: Identify High-Priority Orchestrators

**Objective:** Categorize 263 orchestrators by impact

```bash
# Run discovery script
python cortex-audit-response-templates.py > audit-results.txt

# Extract critical orchestrators
grep "missing" audit-results.txt | head -30
```

**Output:** Prioritized list by:
1. User-facing orchestrators (support, domain)
2. Core orchestrators (MasterOrchestrator, TDDOrchestrator)
3. Response orchestrators (DigestSession, etc.)

**Deliverable:** `ORCHESTRATOR-PRIORITY-MAP.yaml`

```yaml
critical:
  - name: "MasterOrchestrator"
    category: "core"
    users: "All CORTEX operations"
    priority: P0
    effort: "2 hours"
  
  - name: "TDDOrchestrator"
    category: "core"
    users: "Implementation flow"
    priority: P0
    effort: "2 hours"

  - name: "DigestSessionOrchestrator"
    category: "support"
    users: "Session analysis"
    priority: P0
    effort: "1 hour"

high:
  - name: "RefactoringOrchestrator"
    # ...

medium:
  - name: "BrainHealthOrchestrator"
    # ...
```

#### Task 1.2: Set Up Migration Infrastructure

**Files to Create:**

1. **`scripts/orchestrator-template-migrator.py`** (400 lines)
   - Auto-detect orchestrators
   - Generate inheritance boilerplate
   - Inject compose() method template
   - Validate output

2. **`cortex/orchestrators/_base_template_for_new_orchestrators.py`** (50 lines)
   - Copy/paste template for new orchestrators
   - Shows correct pattern
   - Includes docstring example

3. **`tests/test_orchestrator_response_templates.py`** (200 lines)
   - Header generation tests
   - Section ordering tests
   - Copilot Chat markdown tests
   - Silent mode compliance tests

4. **`cortex/orchestrators/linters/response_format_linter.py`** (150 lines)
   - Validate orchestrator response compliance
   - Check header presence
   - Check compose() pattern
   - Warn on narration patterns

**Effort:** 8 hours

---

### Day 3: Fix Critical 5 Orchestrators

#### Orchestrators to Fix First:

1. **MasterOrchestrator** (persona/master_orchestrator.py)
2. **TDDOrchestrator** (migration/tdd_template_integration.py)
3. **EnforcementOrchestrator** (core/enforcement_orchestrator.py)
4. **DigestSessionOrchestrator** (support/digest_session_orchestrator.py)
5. **RefactoringOrchestrator** (domain/refactoring_orchestrator.py)

#### Pattern for Each:

```python
# STEP 1: Add inheritance
-class MasterOrchestrator:
+from cortex.orchestrators.core.base_response_template import BaseResponseTemplate
+
+class MasterOrchestrator(BaseResponseTemplate):

# STEP 2: Add __init__ with super()
+    def __init__(self):
+        super().__init__(
+            orchestrator_name="MasterOrchestrator",
+            mode="CORTEX"
+        )

# STEP 3: Add/update compose method
-    def execute(self):
-        return "result"
+    def compose(self, operation: str, **kwargs) -> str:
+        response = self.header(operation)
+        response += self.section("Analysis", "📊")
+        # existing logic here
+        return response

# STEP 4: Update response generation
-    def execute_operation(self):
-        # old code
-        return "result"
+    def execute_operation(self):
+        return self.compose("OPERATION_TYPE", ...)
```

**Deliverable:** 5 refactored orchestrators with:
- ✅ BaseResponseTemplate inheritance
- ✅ compose() method
- ✅ header() auto-generation
- ✅ Tests passing (100%)
- ✅ Copilot Chat validation

**Effort:** 10 hours (2 hours each)

---

### Day 4-5: Batch Process Next 30 Orchestrators

#### Automated Migration Script

```bash
# Run migration
python scripts/orchestrator-template-migrator.py \
  --mode batch \
  --count 30 \
  --start-after MasterOrchestrator \
  --verbose

# Output: 30 refactored orchestrators + migration report
```

#### Each Orchestrator Gets:

1. **Template Inheritance** ✅
2. **compose() Method** ✅
3. **Header Generation** ✅
4. **Unit Tests** ✅
5. **Migration Verification** ✅

**Deliverable:** 30 migrated orchestrators

**Effort:** 20 hours

---

### Day 5: Final Day - Fix Silent Mode Violations

#### Find 3 Violating Orchestrators

```bash
grep -r "input(" cortex/orchestrators/*.py | grep -i proceed
grep -r "print.*Let me" cortex/orchestrators/*.py
grep -r "Should I continue" cortex/orchestrators/*.py
```

#### For Each Violation:

```python
# ❌ REMOVE
print("Let me check the files...")
response = input("Should I proceed? (yes/no): ")
if response.lower() != "yes":
    return

# ✅ REPLACE WITH
# Silent execution - no prompts
progress_bar.update(stage=1)
# Continue automatically
```

**Deliverable:** 3 fixed orchestrators, no silent mode violations

**Effort:** 2 hours

---

## Summary: Phase 50 Outcomes

| Item | Status | Count | Effort |
|------|--------|-------|--------|
| **Orchestrators Migrated** | ✅ | 35 | 30h |
| **Silent Mode Violations Fixed** | ✅ | 3 | 2h |
| **Migration Infrastructure** | ✅ | 3 files | 8h |
| **Tests Created** | ✅ | 50+ | 10h |
| **Template Inheritance** | 26.6% → 39.5% | +30 | - |
| **Copilot Chat Ready** | 0.0% → 15.0% | +39 | - |

**Phase 50 Effort:** 50 hours  
**Phase 50 End State:** 39/263 orchestrators (15%) migrated

---

## Phase 51: Bulk Remediation (Week 2)

### Day 1-3: Automate Remaining 158 Orchestrators

#### Script Execution

```bash
# Run full batch migration
python scripts/orchestrator-template-migrator.py \
  --mode full-batch \
  --remaining 158 \
  --parallel 10 \
  --report migration-report-phase51.json

# Expected: 158 fully migrated orchestrators
```

#### Migration Validation

Each orchestrator verified for:
```yaml
checks:
  - name: "template_inheritance"
    status: "✅ BaseResponseTemplate in inheritance chain"
  - name: "compose_method"
    status: "✅ Callable compose() with operation parameter"
  - name: "header_generation"
    status: "✅ Calls self.header(operation)"
  - name: "section_ordering"
    status: "✅ sections in order: description → analysis → next-steps"
  - name: "no_narration"
    status: "✅ No print/input patterns"
  - name: "tests_passing"
    status: "✅ 100% unit tests passing"
```

**Effort:** 20 hours

---

### Day 4-5: GitHub Copilot Chat Integration

#### For Each Core/Domain Orchestrator (62 total)

Add CopilotChatTemplateEngine integration:

```python
from cortex.orchestrators.response.copilot_chat_templates import CopilotChatTemplateEngine

class MyOrchestrator(BaseResponseTemplate):
    def __init__(self):
        super().__init__(orchestrator_name="MyOrchestrator")
        self.chat_engine = CopilotChatTemplateEngine()
    
    def compose(self, operation: str, **kwargs) -> str:
        """Generate response using Copilot Chat templates."""
        
        if operation == "ANALYZE":
            return self.chat_engine.render_audit_summary(
                p0_count=kwargs.get('p0_count', 0),
                p1_count=kwargs.get('p1_count', 0),
                audit_details=kwargs.get('audit_details', ''),
                recommendations=kwargs.get('recommendations', []),
                next_steps=kwargs.get('next_steps', '')
            )
        
        if operation == "CHALLENGE":
            return self.chat_engine.render_design_challenge(
                user_request=kwargs.get('user_request', ''),
                extensibility_analysis=kwargs.get('extensibility_analysis', ''),
                # ...
            )
        
        # Fallback to base template
        return super().compose(operation, **kwargs)
```

**Coverage:**
- ✅ 15 ANALYZE operations → render_audit_summary
- ✅ 20 DESIGN operations → render_design_challenge
- ✅ 12 IMPLEMENTATION operations → render_implementation_complete
- ✅ 15 APPROVAL operations → render_dor_gate

**Effort:** 15 hours

---

### Day 5: Wiring Contract Update

#### Update `cortex/__wiring_contract__.yaml`

```yaml
orchestrators:
  - name: "MasterOrchestrator"
    module: "cortex.orchestrators.persona.master_orchestrator"
    class_name: "MasterOrchestrator"
    
    # NEW FIELDS
    response_template: "MasterOrchestratorTemplate"
    base_template: "BaseResponseTemplate"
    copilot_chat_ready: true
    silent_mode_compliant: true
    compose_method: true
    
    # Metadata
    response_format_version: "1.0.0"
    last_template_audit: "2026-02-15"
```

**Effort:** 5 hours

---

## Summary: Phase 51 Outcomes

| Item | Status | Count | Effort |
|------|--------|-------|--------|
| **Orchestrators Migrated** | ✅ | 158 | 20h |
| **Copilot Chat Integration** | ✅ | 62 | 15h |
| **Wiring Contract Updated** | ✅ | 263 | 5h |
| **Template Inheritance** | 39.5% → 100% | +224 | - |
| **Copilot Chat Ready** | 15.0% → 100% | +224 | - |

**Phase 51 Effort:** 40 hours  
**Phase 51 End State:** 193/263 orchestrators (100%) migrated

---

## Phase 52: Testing & Validation (Week 3)

### Day 1-2: Comprehensive Test Suite

#### Create Tests

**File:** `tests/test_orchestrator_response_compliance.py`

```python
class TestOrchestratorResponseCompliance:
    """Validate all 263 orchestrators for response compliance."""
    
    @pytest.mark.parametrize("orchestrator_class", ALL_ORCHESTRATORS)
    def test_has_base_response_template_inheritance(self, orchestrator_class):
        """All orchestrators inherit from BaseResponseTemplate."""
        assert issubclass(orchestrator_class, BaseResponseTemplate)
    
    @pytest.mark.parametrize("orchestrator_class", ALL_ORCHESTRATORS)
    def test_has_compose_method(self, orchestrator_class):
        """All orchestrators implement compose()."""
        assert hasattr(orchestrator_class, 'compose')
        assert callable(getattr(orchestrator_class, 'compose'))
    
    @pytest.mark.parametrize("orchestrator_class", CORE_ORCHESTRATORS)
    def test_copilot_chat_ready(self, orchestrator_class):
        """Core orchestrators use CopilotChatTemplateEngine."""
        instance = orchestrator_class()
        assert hasattr(instance, 'chat_engine')
        assert instance.chat_engine is not None
    
    @pytest.mark.parametrize("orchestrator_class", ALL_ORCHESTRATORS)
    def test_response_header_format(self, orchestrator_class):
        """Responses start with CORTEX header."""
        instance = orchestrator_class()
        response = instance.compose("TEST")
        assert response.startswith("## 🧠 CORTEX")
        assert "**Author:**" in response
        assert "**Orchestrator:**" in response
    
    @pytest.mark.parametrize("orchestrator_class", ALL_ORCHESTRATORS)
    def test_no_narration_patterns(self, orchestrator_class):
        """No narration in silent mode."""
        source = inspect.getsource(orchestrator_class)
        assert not re.search(r'"Let me', source)
        assert not re.search(r'"I\'ll', source)
        assert not re.search(r'input\(', source)
    
    @pytest.mark.parametrize("orchestrator_class", ALL_ORCHESTRATORS)
    def test_copilot_chat_markdown(self, orchestrator_class):
        """Responses render correctly in GitHub Copilot Chat."""
        instance = orchestrator_class()
        response = instance.compose("TEST")
        
        # Validate markdown
        sections = extract_markdown_sections(response)
        assert len(sections) > 0
        
        # Ensure Next Steps is last
        if "Next Steps" in response:
            assert response.rstrip().endswith("Next Steps") or \
                   "Next Steps" in response.split('\n')[-3:]
```

**Tests:** 1,500+ assertions across 263 orchestrators

**Effort:** 10 hours

---

### Day 3: Run Full Test Suite

```bash
# Run all orchestrator compliance tests
pytest tests/test_orchestrator_response_compliance.py -v --tb=short

# Expected output:
# test_has_base_response_template_inheritance[...] 263 PASSED
# test_has_compose_method[...] 263 PASSED
# test_response_header_format[...] 263 PASSED
# test_no_narration_patterns[...] 263 PASSED
# test_copilot_chat_ready[...] 62 PASSED

# Result: 1,315 tests, 100% PASSING
```

**Coverage:**
- ✅ 263/263 orchestrators have template inheritance
- ✅ 263/263 orchestrators have compose() methods
- ✅ 263/263 orchestrators generate correct headers
- ✅ 263/263 orchestrators have no narration patterns
- ✅ 62/62 core orchestrators Copilot Chat ready

**Effort:** 5 hours

---

### Day 4: Documentation & Validation

#### Create Documentation

1. **ORCHESTRATOR-MIGRATION-COMPLETE.md**
   - What was done
   - Validation results
   - Before/after metrics

2. **RESPONSE-TEMPLATE-USAGE-GUIDE.md**
   - How to use templates
   - Best practices
   - Examples

3. **UPDATE .github/copilot-instructions.md**
   - Add Response Header section if missing
   - Link to template guide
   - Examples of compliance

**Effort:** 5 hours

---

### Day 5: Final Validation & Rollout

#### Pre-Production Checklist

```
✅ All 263 orchestrators migrated
✅ 1,315+ tests passing
✅ Wiring contract updated
✅ Documentation complete
✅ No silent mode violations
✅ Copilot Chat rendering verified
✅ Performance benchmarks OK (<50ms response generation)
✅ Backward compatibility verified
```

#### Deployment

```bash
# Merge migration branch
git checkout main
git merge feature/phase50-52-response-templates

# Tag release
git tag -a "v7.7-CORTEX-RESPONSE-TEMPLATES" -m "Phase 50-52: 100% orchestrator template compliance"

# Update version in __wiring_contract__.yaml
# Update version in .github/copilot-instructions.md
```

**Effort:** 3 hours

---

## Summary: Phase 52 Outcomes

| Item | Status | Count | Effort |
|------|--------|-------|--------|
| **Test Suite Created** | ✅ | 1,315 tests | 10h |
| **All Tests Passing** | ✅ | 100% | 5h |
| **Documentation** | ✅ | 3 files | 5h |
| **Final Validation** | ✅ | Complete | 3h |

**Phase 52 Effort:** 23 hours  
**Phase 52 End State:** 100% compliance achieved

---

## Overall Program Summary

### Timeline

| Phase | Duration | Effort | Outcome |
|-------|----------|--------|---------|
| **Phase 50** | Week 1 (5 days) | 50h | 35/263 (13%) migrated |
| **Phase 51** | Week 2 (5 days) | 40h | 193/263 (100%) migrated |
| **Phase 52** | Week 3 (5 days) | 23h | 100% validated & tested |
| **TOTAL** | 3 weeks | **113 hours** | **✅ Production Ready** |

### Success Metrics (Phase 52 End)

| Metric | Baseline | Target | Achievement |
|--------|----------|--------|-------------|
| **Template Inheritance** | 26.6% | 100% | ✅ 100% |
| **compose() Methods** | 25.9% | 100% | ✅ 100% |
| **header() Methods** | 0.0% | 100% | ✅ 100% |
| **Copilot Chat Ready** | 0.0% | 100% | ✅ 100% |
| **Silent Mode Violations** | 3 | 0 | ✅ 0 |
| **CORE-029 Compliance** | 26.6% | 100% | ✅ 100% |
| **Test Coverage** | 0 | 1,315 | ✅ 1,315 |

### Risk Mitigation

| Risk | Mitigation | Responsible |
|------|------------|-------------|
| **Breaking Changes** | Run full test suite, backward compat check | Phase 52 Day 3 |
| **Performance Regression** | Benchmark response generation time | Phase 52 Day 3 |
| **Incomplete Migration** | Automated validation script, manual spot-check | Phase 52 Day 1-2 |
| **Documentation Out of Date** | Update all reference files | Phase 52 Day 4 |

---

## Next Steps After Phase 52

1. **Monitoring** (Week 4+)
   - Track response generation metrics
   - Monitor Copilot Chat session feedback
   - Alert on template violations

2. **Continuous Enforcement**
   - Pre-commit hook: validate response format
   - CI/CD gate: fail build if templates missing
   - Quarterly audit: ensure compliance maintained

3. **Enhancement** (Phase 53+)
   - Add domain-specific templates
   - Optimize for different user types
   - Build AI-driven response optimization

---

**Document Created:** 2026-02-10  
**Authority:** cortex-architect.prompt.md v15.3  
**Next Review:** Phase 50 Start (2026-02-17)
