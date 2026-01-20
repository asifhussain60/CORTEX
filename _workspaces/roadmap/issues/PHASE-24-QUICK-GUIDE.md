# Phase 24 Quick Implementation Guide

## Current State
- **Phase 24:** IN_PROGRESS ✅
- **Status:** 2/4 ACs complete, 73/73 tests passing
- **Master File:** `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml`
- **Latest Commit:** 004fe08c5

## Completed ACs

### ✅ AC-RESP-001-01: Turn-by-Turn Response Generation
- File: `src/orchestrators/response/turn_response_generator.py`
- Tests: `tests/unit/orchestrators/test_turn_response_generation.py` (37 tests)
- Status: COMPLETED, 37/37 tests passing

### ✅ AC-RESP-002-01: Multi-Mode Response Formatting
- File: `src/orchestrators/response/multi_mode_formatter.py`
- Tests: `tests/unit/orchestrators/test_multi_mode_formatter.py` (36 tests)
- Status: COMPLETED, 36/36 tests passing

---

## Next: AC-RESP-003-01 - Response Template System

### Quick Start
```python
# Key classes to implement:
class ResponseTemplate:
    """Template for common response patterns"""
    template_id: str
    version: str
    pattern: str  # "Error processing {{ item }}: {{ reason }}"
    variables: Dict[str, VariableSpec]

class TemplateEngine:
    """Main template engine"""
    def apply_template(self, template_id: str, variables: Dict) -> str
    def get_template(self, template_id: str) -> ResponseTemplate
    def list_templates(self) -> List[ResponseTemplate]
```

### Test Requirements (20+ tests)
- Variable substitution accuracy
- Template versioning and lookup
- Missing variable handling
- Multi-mode template application
- Template caching
- Edge cases

### Implementation Checklist
- [ ] Define ResponseTemplate dataclass
- [ ] Implement TemplateEngine class
- [ ] Create template registry (5-10 patterns)
- [ ] Write variable substitution logic
- [ ] Implement version management
- [ ] Integration with ResponseFormattingEngine
- [ ] Write and pass all 20+ tests
- [ ] Update AC-RESP-003-01 status in cortex-master.yaml

---

## Then: AC-RESP-004-01 - UX Optimization

### Key Classes
```python
class ResponseQualityMetrics:
    """Quality scoring for responses"""
    clarity_score: float
    completeness_score: float
    relevance_score: float
    tone_appropriateness: float
    overall_quality: float

class ResponseUXOptimizer:
    """User experience optimization"""
    def calculate_quality_metrics(response) -> QualityMetrics
    def submit_feedback(feedback) -> None
    def create_ab_test(variant) -> str
    def get_winning_variant(variant_id) -> str
```

### Test Requirements (16+ tests)
- Quality metrics calculation
- User feedback storage and retrieval
- A/B test mechanics
- Statistical winner determination
- Optimization recommendations
- Edge cases

### Implementation Checklist
- [ ] Define quality metrics dataclass
- [ ] Implement metrics calculation
- [ ] Create feedback collection system
- [ ] Implement A/B test variant management
- [ ] Add statistical winner determination
- [ ] Integration with audit trail
- [ ] Write and pass all 16+ tests
- [ ] Update AC-RESP-004-01 status in cortex-master.yaml

---

## Final Steps

### Phase 24 Completion
```bash
# After both ACs are done:
1. Update cortex-master.yaml:
   - PHASE-24 status: COMPLETED
   - locked: true
   - completed_ac_ids: 4
   - completed_at: <timestamp>

2. Run full test suite:
   pytest tests/unit/orchestrators/test_*.py -v

3. Verify 109+ tests passing

4. Commit:
   git commit -m "phase-24: COMPLETED - All 4 ACs (109 tests)"

5. Ready for Phase 25
```

---

## File Locations to Update

### cortex-master.yaml locations:
1. **Phase Tracker** (line ~3886):
   ```yaml
   PHASE-24-RESPONSE-COMPOSITION:
     completed_ac_ids: 2  ← Update to 4
     status: IN_PROGRESS  ← Update to COMPLETED
   ```

2. **Phases Section** (line ~6558):
   ```yaml
   phase_24_response_composition:
     status: IN_PROGRESS  ← Update to COMPLETED
     locked: false        ← Update to true
     ac_ids:
       AC-RESP-003-01: status: NOT_STARTED  ← Update to COMPLETED
       AC-RESP-004-01: status: NOT_STARTED  ← Update to COMPLETED
   ```

---

## Command Reference

```bash
# Check current status
grep -A 20 "PHASE-24" /Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml

# Run AC-RESP-001-01 tests
python -m pytest tests/unit/orchestrators/test_turn_response_generation.py -v

# Run AC-RESP-002-01 tests
python -m pytest tests/unit/orchestrators/test_multi_mode_formatter.py -v

# Run all Phase 24 tests
python -m pytest tests/unit/orchestrators/test_*response*.py -v

# Commit Phase 24 completion
cd /Users/asifhussain/PROJECTS/CORTEX
git add _workspaces/roadmap/cortex-master.yaml
git commit -m "phase-24: COMPLETED - All 4 ACs (109 tests passing)"

# View Phase 24 progress
cat /Users/asifhussain/PROJECTS/CORTEX/docs/PHASE-24-PROGRESS-REPORT.md
```

---

## Key Principles

1. **TDD First**: Write tests before implementation
2. **100% Type Hints**: All functions must have type hints
3. **Full Docstrings**: Google-style docstrings required
4. **>95% Coverage**: Aim for >95% test coverage
5. **Governance**: CORE rules enforced at commit time
6. **Atomic Updates**: Each AC is a separate, testable unit

---

## Success Criteria

Phase 24 is COMPLETE when:
- ✅ AC-RESP-001-01: COMPLETED (37 tests)
- ✅ AC-RESP-002-01: COMPLETED (36 tests)
- ✅ AC-RESP-003-01: COMPLETED (20+ tests)
- ✅ AC-RESP-004-01: COMPLETED (16+ tests)
- ✅ Total: 109+ tests, 100% pass rate
- ✅ PHASE-24 status: COMPLETED, locked: true
- ✅ Git committed and pushed

**Expected Timeline:** 4-5 hours total
