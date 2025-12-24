# Phase 15: Plan Generation Token Optimization

**Estimated Duration:** 3-4 hours  
**Priority:** HIGH  
**Dependencies:** Phase 13 (UnifiedPlanGenerator), Phase 14 (Existing Files Realignment)

---

## 🎯 Objective

Optimize token usage in generated master plans by reducing redundancy, implementing smart templating, and adding compression strategies without sacrificing readability or functionality.

---

## 📋 Current State Analysis

### Current Token Metrics (Post-Phase 14):
- **Unified Format Plans:** 350-800 tokens per plan
- **Legacy Format Plans:** 4,000-19,000 tokens per plan
- **Migration Savings:** 94.7% reduction achieved

### Remaining Optimization Opportunities:
1. **Continuation Prompt Verbosity:** 150-200 tokens (could be 50-80)
2. **Visual Progress Tracker:** Repeated status emojis and spacing
3. **Phase Table Redundancy:** Full phase names + status strings
4. **Metadata Duplication:** Author, date, plan ID repeated
5. **Template Boilerplate:** Fixed text in every plan

---

## 🔧 Implementation Tasks

### Task 15.1: Token Budget Analysis (30 mins)
**Goal:** Establish per-section token budgets

**Actions:**
- Analyze 11 migrated plans for token distribution
- Identify highest-cost sections
- Set target budgets per section:
  - Header/Metadata: 40-60 tokens (current: 80-100)
  - Continuation Prompt: 50-80 tokens (current: 150-200)
  - Visual Tracker: 100-150 tokens (current: 200-300)
  - Phase Table: 30-50 tokens per phase (current: 60-80)
  - Footer: 20-30 tokens (current: 40-50)

**Deliverables:**
- `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/reports/token-budget-analysis.md`

---

### Task 15.2: Implement Token Compression Strategies (TDD - 1.5h)

**RED Phase (30 mins):**
Create tests in `tests/test_token_optimization.py`:
```python
def test_compressed_continuation_prompt_reduces_tokens()
def test_abbreviated_status_indicators()
def test_minimal_phase_table_format()
def test_single_line_metadata()
def test_total_plan_under_target_budget()
```

**GREEN Phase (45 mins):**
Modify `UnifiedPlanGenerator`:
1. **Compressed Continuation Prompt:**
   ```markdown
   ## 🔄 Continue
   `plan-id` | ████░░ 31% (5/16) | Next: Phase 2 | TDD: RED→GREEN→REFACTOR
   ```

2. **Abbreviated Status:**
   - ✅ COMPLETE → ✅
   - ⏸️ PENDING → ⏸️
   - 🔄 IN PROGRESS → 🔄
   - Remove redundant "COMPLETE", "PENDING" text

3. **Minimal Phase Table:**
   ```markdown
   | # | Name | S | Time | Δ |
   |---|------|---|------|---|
   | 1 | Setup | ✅ | 1h | 0 |
   ```

4. **Single-Line Metadata:**
   ```markdown
   **ID:** plan-id | **Date:** 2025-12-15 | **Tier:** 4 | **Author:** AH
   ```

**REFACTOR Phase (15 mins):**
- Extract compression logic to separate module
- Add configuration flag for verbose/compressed modes

**Deliverables:**
- Modified `src/operations/modules/planning/unified_plan_generator.py`
- New tests: 5 tests, 100% passing
- Token reduction: Target 30-40% additional savings (from 350-800 → 250-550)

---

### Task 15.3: Template Caching System (1h)

**Goal:** Avoid regenerating static template parts

**Implementation:**
```python
class TemplateCacheManager:
    """Cache reusable template sections."""
    
    def __init__(self):
        self.cache = {}
    
    def get_header_template(self) -> str:
        """Return cached header with placeholders."""
        if 'header' not in self.cache:
            self.cache['header'] = self._generate_header_template()
        return self.cache['header']
    
    def get_footer_template(self) -> str:
        """Return cached footer with placeholders."""
        if 'footer' not in self.cache:
            self.cache['footer'] = self._generate_footer_template()
        return self.cache['footer']
```

**Benefits:**
- Reduce generation time by 20-30%
- Ensure consistency across all plans
- Enable A/B testing of template variations

**Deliverables:**
- `src/operations/modules/planning/template_cache_manager.py`
- Integration with UnifiedPlanGenerator
- Performance benchmarks

---

### Task 15.4: Smart Phase Name Compression (45 mins)

**Strategy:** Use abbreviations for long phase names

**Compression Rules:**
- "Integration" → "Integ"
- "Implementation" → "Impl"
- "Enhancement" → "Enhnc"
- "Orchestrator" → "Orch"
- "Architecture" → "Arch"

**Example:**
```markdown
Before: | 13 | Planning Architecture Unification | ✅ COMPLETE | 6.5h | 0 |
After:  | 13 | Planning Arch Unif | ✅ | 6.5h | 0 |
```

**Deliverables:**
- `src/operations/modules/planning/phase_name_compressor.py`
- Abbreviation dictionary with 50+ common terms
- Reversible compression (for full display when needed)

---

### Task 15.5: Emoji Optimization (30 mins)

**Current Issue:** Emojis take 2-4 tokens each

**Solutions:**
1. **Use single emojis instead of emoji + text:**
   - "✅ COMPLETE" (3 tokens) → "✅" (1 token)
   - "⏸️ PENDING" (3 tokens) → "⏸️" (1 token)

2. **Remove decorative emojis:**
   - "## 🎯 Executive Summary" → "## Summary"
   - "## 📊 Visual Progress Tracker" → "## Progress"

3. **Keep only essential emojis:**
   - Phase status indicators (✅, ⏸️, 🔄)
   - Progress bar visualization

**Target:** Save 20-30 tokens per plan

---

### Task 15.6: Validation & Rollout (30 mins)

**Validation Checklist:**
- [ ] All 14 migration tests still pass
- [ ] Token reduction meets 30-40% target
- [ ] Plans remain human-readable
- [ ] Continuation prompts still functional
- [ ] Phase lifecycle manager compatible

**Rollout Strategy:**
1. Re-migrate 1 test plan (cortex-lens-v3)
2. Compare old vs new token counts
3. Validate functionality
4. Re-migrate all 11 active plans
5. Update Phase 14 completion report with new metrics

---

## 📊 Expected Outcomes

### Token Savings Projection:

| Section | Before | After | Savings |
|---------|--------|-------|---------|
| Header/Metadata | 90 | 50 | 44% |
| Continuation Prompt | 180 | 70 | 61% |
| Visual Tracker | 250 | 120 | 52% |
| Phase Table (10 phases) | 600 | 350 | 42% |
| Footer | 40 | 20 | 50% |
| **Total** | **350-800** | **250-550** | **35-40%** |

### Cumulative Impact:
- **Phase 14:** 110,630 → 5,865 tokens (94.7% reduction)
- **Phase 15:** 5,865 → 3,800 tokens (35% additional reduction)
- **Total:** 110,630 → 3,800 tokens (96.6% total reduction)

---

## ✅ Definition of Done

- [ ] Token budget analysis complete with per-section targets
- [ ] 5 optimization tests written and passing (TDD)
- [ ] Template caching system implemented
- [ ] Phase name compression with 50+ abbreviations
- [ ] Emoji optimization applied
- [ ] All 11 active plans re-migrated with new format
- [ ] Token reduction: 30-40% achieved (5,865 → 3,800 tokens)
- [ ] Backward compatibility maintained
- [ ] Documentation updated

---

## 🚨 Risks & Mitigation

**Risk 1:** Over-compression makes plans unreadable
- **Mitigation:** Keep verbose mode as fallback, A/B test with users

**Risk 2:** Breaking changes to phase lifecycle manager
- **Mitigation:** Comprehensive integration tests, version compatibility checks

**Risk 3:** Marginal gains not worth effort
- **Mitigation:** Set minimum 25% reduction threshold to proceed

---

## 📝 Notes

- This phase complements Phase 14's format migration
- Future: Apply compression to Tier 2-4 plans (completed/ADO/archived)
- Consider: Dynamic compression based on plan complexity (LOW tier gets max compression, HIGH tier keeps verbosity)
