# Phase 5: Response Template System Refactor - Implementation Plan

**Phase ID:** Phase 5  
**Priority:** 6/10  
**Status:** 🚀 **READY TO START**  
**Effort:** 38 hours (estimated)  
**Start Date:** December 2, 2025  
**Target Completion:** December 6, 2025  

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Phase Overview

Transform CORTEX's response template system from a monolithic 2,896-line YAML file into a modular, profile-driven architecture that adapts responses based on user preferences while maintaining backward compatibility.

### Success Criteria
- ✅ **58% size reduction** (2,896 → 1,200 lines across 4 files)
- ✅ **Zero breaking changes** (full backward compatibility)
- ✅ **Performance** (<50ms composition time)
- ✅ **Test coverage** (≥85% for new code)
- ✅ **100% template migration** (all 18 templates work in new system)

---

## 📋 Definition of Ready (DoR)

### Prerequisites Verified ✅
- [x] Phase 0 (Foundation) COMPLETE
- [x] User Profile System EXISTS (Phase 1 Todo 6-9)
- [x] UserProfileManager class FUNCTIONAL
- [x] Template system documentation REVIEWED
- [x] Existing planning documents READ:
  - SUMMARY-2025-12-01-response-template-refactor.md
  - response-template-architecture-review.md
  - template-integration-summary.md

### Current State Assessment
**Existing Components:**
- `cortex-brain/response-templates.yaml` (2,896 lines, monolithic)
- `src/response_templates/template_renderer.py` (267 lines, functional)
- `src/response_templates/template_loader.py` (210 lines, functional)
- `src/response_templates/template_registry.py` (exists)
- `src/response_templates/multi_template_orchestrator.py` (exists)
- User profile system with `interaction_mode` field

**Missing Components:**
- Template composition engine
- Modular YAML structure (4 files)
- `response_detail` preference in user profiles
- Profile-aware template selection
- Dynamic section rendering

---

## 📦 Deliverables

### 5.1 Modular YAML Structure (8 hours)
**Goal:** Split monolithic YAML into 4 focused, maintainable files

**Files to Create:**
1. `cortex-brain/response-base-components.yaml` (200 lines)
   - Shared header/footer components
   - Reusable section templates
   - Variant formats (concise/balanced/verbose)

2. `cortex-brain/response-template-definitions.yaml` (400 lines)
   - 18 template definitions with metadata
   - Required/optional sections by ID
   - No hard-coded content (references components)

3. `cortex-brain/response-profile-variants.yaml` (300 lines)
   - 4 interaction modes configuration
   - 4 experience levels adaptation
   - Section inclusion/exclusion rules

4. `cortex-brain/response-routing-rules.yaml` (300 lines)
   - Intent detection keywords
   - Priority ordering
   - Template selection logic

**Test Strategy:**
- YAML syntax validation (yamllint)
- Python `yaml.safe_load()` successful on all 4 files
- Schema validation (all required fields present)
- Comparison test (new system produces same output as old)

**TDD Checkpoints:**
- **RED:** Write test that loads all 4 YAML files → fails (files don't exist)
- **GREEN:** Create 4 YAML files with minimal content → test passes
- **REFACTOR:** Migrate full content from monolithic file

---

### 5.2 Template Composition Engine (12 hours)
**Goal:** Build Python engine that composes templates dynamically based on user profile

**File to Create:**
- `src/utils/template_composer.py` (300 lines)

**Classes:**
```python
class TemplateComposer:
    """Runtime template composition engine."""
    
    def compose_response(
        self, 
        template_id: str, 
        context: Dict[str, Any], 
        user_profile: Optional[Dict] = None
    ) -> str:
        """Compose template with profile-aware adaptation."""
        
    def _build_section_list(
        self, 
        template: Dict, 
        user_profile: Dict
    ) -> List[str]:
        """Determine which sections to include based on profile."""
        
    def _apply_experience_level(
        self, 
        content: str, 
        experience: str
    ) -> str:
        """Adapt content for experience level."""
        
    def _get_cached_template(self, cache_key: str) -> Optional[str]:
        """Retrieve from 24-hour cache if available."""
        
    def _cache_template(self, cache_key: str, content: str) -> None:
        """Cache composed template for 24 hours."""
```

**Features:**
- Profile-driven section selection (interaction_mode + response_detail)
- Experience level content adaptation
- 24-hour caching (reduce recomposition overhead)
- Lazy loading (load YAML files on-demand)
- Backward compatibility (works without profile)

**Test Strategy:**
- Unit tests for each method (25 tests target)
- Profile-aware composition (4 modes × 3 detail levels = 12 tests)
- Section reordering tests
- Variant application tests
- Caching behavior tests
- Error handling (missing components, invalid profile)
- Target: 85% code coverage

**TDD Checkpoints:**
- **RED:** Write test for basic composition → fails (class doesn't exist)
- **GREEN:** Implement `TemplateComposer` with basic composition → test passes
- **REFACTOR:** Add caching, profiling, optimization
- **RED:** Write test for profile-aware composition → fails
- **GREEN:** Implement profile integration → test passes
- **REFACTOR:** Extract methods, improve readability

---

### 5.3 UserProfile Integration (6 hours)
**Goal:** Add `response_detail` preference to user profiles

**Database Changes:**
- Add `response_detail` column to `user_profile` table (VARCHAR, default 'balanced')
- Values: 'concise', 'balanced', 'verbose'
- Create migration script

**Code Changes:**
- `src/tier1/user_profile_manager.py`:
  - Add `response_detail` parameter to `create_profile()`
  - Add `response_detail` parameter to `update_profile()`
  - Add getter method `get_response_detail()`

**Template Changes:**
- `cortex-brain/response-templates.yaml`:
  - Add Question 2a to onboarding template
  - "How detailed should responses be?"
  - Options: Concise / Balanced / Verbose
  - Make optional (default to 'balanced')

**Migration Strategy:**
- Automatic backfill for existing users:
  - Autonomous → concise
  - Guided → balanced
  - Educational → verbose
  - Pair → balanced
- Notification: "We've enhanced responses - update preference in profile"

**Test Strategy:**
- Database migration test (schema change succeeds)
- UserProfileManager CRUD tests (create, read, update with response_detail)
- Backfill script test (all existing users get default)
- Onboarding template test (Question 2a appears correctly)
- Integration test (response_detail affects template selection)

**TDD Checkpoints:**
- **RED:** Write test for `response_detail` field → fails (column doesn't exist)
- **GREEN:** Add migration script, run migration → test passes
- **REFACTOR:** Add constraints, indexes if needed
- **RED:** Write test for UserProfileManager methods → fails
- **GREEN:** Implement methods → test passes
- **REFACTOR:** Add validation, error handling

---

### 5.4 Dynamic Section Rendering (7 hours)
**Goal:** Enable templates to adapt sections based on user profile

**File to Create:**
- `src/utils/template_selector.py` (150 lines)

**Classes:**
```python
class TemplateSelector:
    """Selects appropriate template variant based on intent and profile."""
    
    def select_template(
        self, 
        intent: str, 
        user_profile: Optional[Dict] = None
    ) -> Tuple[str, Dict]:
        """Select template ID and variant configuration."""
        
    def _get_variant(
        self, 
        template_id: str, 
        user_profile: Dict
    ) -> Dict:
        """Get variant configuration for profile."""
        
    def _apply_overrides(
        self, 
        variant: Dict, 
        response_detail: str
    ) -> Dict:
        """Apply response_detail overrides to variant."""
```

**Integration Points:**
- Update `IntentRouter` to use `TemplateSelector`
- Pass user profile from Tier 1 to template selection
- Handle backward compatibility (users without response_detail)

**Test Strategy:**
- Unit tests for TemplateSelector (15 tests)
- End-to-end tests (intent → selection → composition → rendering)
- Profile override tests (response_detail overrides interaction_mode)
- Fallback tests (missing profile, missing response_detail)
- Performance tests (selection time <10ms)

**TDD Checkpoints:**
- **RED:** Write test for template selection → fails (class doesn't exist)
- **GREEN:** Implement `TemplateSelector` → test passes
- **REFACTOR:** Optimize lookup logic
- **RED:** Write test for profile override → fails
- **GREEN:** Implement override logic → test passes
- **REFACTOR:** Extract configuration to YAML

---

### 5.5 Backward Compatibility Layer (5 hours)
**Goal:** Ensure existing code continues working during migration

**Feature Flag:**
```json
// cortex.config.json
{
  "template_system": {
    "enable_modular_templates": false,  // Default: false (old system)
    "gradual_rollout_percentage": 0     // 0 / 10 / 50 / 100
  }
}
```

**Compatibility Wrapper:**
- Keep `response-templates.yaml` with deprecation warning
- Add `TemplateSystemAdapter` class:
  - Detects which system is enabled
  - Routes to old or new system accordingly
  - Logs usage metrics for migration tracking

**Migration Path:**
1. **Week 1:** 10% rollout (internal testing)
2. **Week 2:** 50% rollout (beta users)
3. **Week 3:** 100% rollout (all users)
4. **Week 4:** Remove old system (if no issues)

**Rollback Plan:**
- Set `enable_modular_templates: false` in config
- System falls back to original `response-templates.yaml`
- No data loss, no code changes needed

**Test Strategy:**
- Feature flag tests (on/off behavior)
- Adapter routing tests (old vs new system)
- Rollback tests (switch back works correctly)
- Migration percentage tests (10/50/100% rollout)

**TDD Checkpoints:**
- **RED:** Write test for feature flag → fails (config doesn't exist)
- **GREEN:** Add config, implement feature flag check → test passes
- **REFACTOR:** Add logging, metrics
- **RED:** Write test for adapter routing → fails
- **GREEN:** Implement TemplateSystemAdapter → test passes
- **REFACTOR:** Add error handling, fallback logic

---

## ✅ Definition of Done (DoD)

### Code Quality
- [ ] All deliverables implemented and tested
- [ ] 85%+ test coverage for new code
- [ ] All tests passing (pytest 100%)
- [ ] No pylint/flake8 errors
- [ ] Code reviewed and approved

### Functionality
- [ ] 18 templates work in new system (100% migration)
- [ ] User profile integration functional (response_detail)
- [ ] Template composition <50ms (performance target)
- [ ] Cache hit rate >90% (efficiency target)
- [ ] Backward compatibility verified (old code works)

### Documentation
- [ ] Phase 5 completion report generated
- [ ] Updated `template-guide.md` with new architecture
- [ ] Updated `user-profile-guide.md` with Question 2a
- [ ] Migration guide created (for users/developers)
- [ ] Updated `CORTEX.prompt.md` with new onboarding question

### Testing
- [ ] Unit tests: 25+ tests for TemplateComposer
- [ ] Integration tests: 15+ tests for end-to-end flow
- [ ] Performance tests: composition <50ms, cache >90%
- [ ] Validation tests: 72 tests (18 templates × 4 modes)
- [ ] Backward compatibility tests: old system works

### Deployment Readiness
- [ ] Feature flag configured (default: false)
- [ ] Rollback plan documented and tested
- [ ] Migration script created and tested
- [ ] Gradual rollout percentages defined (10/50/100)
- [ ] Monitoring/metrics added for migration tracking

---

## 🗓️ Implementation Schedule

### Day 1 (8 hours): Deliverable 5.1 - Modular YAML Structure
**TDD Cycle 1: RED Phase**
- Write YAML validation tests (4 tests)
- Write schema validation tests (4 tests)
- Write comparison tests (old vs new output)
- All tests FAIL (files don't exist)
- Commit: "test: Add RED phase tests for modular YAML structure"

**TDD Cycle 1: GREEN Phase**
- Create 4 YAML files with minimal structure
- Migrate 18 templates to new structure
- Run yamllint on all files
- All tests PASS
- Commit: "feat: Create modular YAML structure (GREEN phase)"

**TDD Cycle 1: REFACTOR Phase**
- Optimize YAML structure (reduce duplication)
- Add inline documentation/comments
- Validate all references resolve correctly
- Tests still PASS
- Commit: "refactor: Optimize modular YAML structure"

---

### Day 2 (12 hours): Deliverable 5.2 - Template Composition Engine

**TDD Cycle 2: RED Phase (Morning - 3h)**
- Write TemplateComposer unit tests (15 tests)
- Write caching tests (5 tests)
- Write profile integration tests (5 tests)
- All tests FAIL (class doesn't exist)
- Commit: "test: Add RED phase tests for TemplateComposer"

**TDD Cycle 2: GREEN Phase (Afternoon - 6h)**
- Implement `TemplateComposer` class
- Implement basic composition (no profile)
- Implement profile-aware composition
- Implement caching mechanism
- All tests PASS (may be minimal implementation)
- Commit: "feat: Implement TemplateComposer (GREEN phase)"

**TDD Cycle 2: REFACTOR Phase (Evening - 3h)**
- Extract methods for readability
- Optimize cache key generation
- Add lazy loading for YAML files
- Add performance profiling
- Tests still PASS
- Commit: "refactor: Optimize TemplateComposer performance"

---

### Day 3 (6 hours): Deliverable 5.3 - UserProfile Integration

**TDD Cycle 3: RED Phase (Morning - 2h)**
- Write database migration test
- Write UserProfileManager CRUD tests (5 tests)
- Write backfill script test
- All tests FAIL (column doesn't exist)
- Commit: "test: Add RED phase tests for response_detail field"

**TDD Cycle 3: GREEN Phase (Midday - 3h)**
- Create database migration script
- Run migration (add response_detail column)
- Implement UserProfileManager methods
- Implement backfill script
- All tests PASS
- Commit: "feat: Add response_detail to user profiles (GREEN phase)"

**TDD Cycle 3: REFACTOR Phase (Afternoon - 1h)**
- Add validation for response_detail values
- Add constraints/indexes to database
- Add error handling for invalid values
- Tests still PASS
- Commit: "refactor: Add validation for response_detail field"

---

### Day 4 (7 hours): Deliverable 5.4 - Dynamic Section Rendering

**TDD Cycle 4: RED Phase (Morning - 2h)**
- Write TemplateSelector unit tests (10 tests)
- Write integration tests (5 tests)
- All tests FAIL (class doesn't exist)
- Commit: "test: Add RED phase tests for TemplateSelector"

**TDD Cycle 4: GREEN Phase (Midday - 4h)**
- Implement `TemplateSelector` class
- Implement intent-based template selection
- Implement profile-aware variant selection
- Integrate with IntentRouter
- All tests PASS
- Commit: "feat: Implement TemplateSelector (GREEN phase)"

**TDD Cycle 4: REFACTOR Phase (Afternoon - 1h)**
- Optimize template lookup (use index)
- Extract configuration to YAML
- Add debug logging
- Tests still PASS
- Commit: "refactor: Optimize TemplateSelector performance"

---

### Day 5 (5 hours): Deliverable 5.5 - Backward Compatibility Layer

**TDD Cycle 5: RED Phase (Morning - 1.5h)**
- Write feature flag tests (3 tests)
- Write adapter routing tests (5 tests)
- Write rollback tests (3 tests)
- All tests FAIL (adapter doesn't exist)
- Commit: "test: Add RED phase tests for backward compatibility"

**TDD Cycle 5: GREEN Phase (Midday - 2.5h)**
- Add feature flag to cortex.config.json
- Implement TemplateSystemAdapter
- Implement routing logic (old vs new)
- All tests PASS
- Commit: "feat: Add backward compatibility layer (GREEN phase)"

**TDD Cycle 5: REFACTOR Phase (Afternoon - 1h)**
- Add migration metrics logging
- Add usage tracking
- Add deprecation warnings
- Tests still PASS
- Commit: "refactor: Add migration tracking and logging"

---

## 📊 Test Coverage Requirements

### Unit Tests (Target: 100 tests, 85% coverage)
| Component | Tests | Coverage Target |
|-----------|-------|----------------|
| TemplateComposer | 25 | 90% |
| TemplateSelector | 15 | 90% |
| UserProfileManager (new methods) | 5 | 100% |
| TemplateSystemAdapter | 10 | 85% |
| YAML loading/validation | 10 | 80% |

### Integration Tests (Target: 35 tests)
| Scenario | Tests |
|----------|-------|
| End-to-end flow (intent → response) | 5 |
| Profile-aware composition | 12 (4 modes × 3 details) |
| Feature flag routing | 5 |
| Backward compatibility | 5 |
| Migration scenarios | 8 |

### Validation Tests (Target: 72 tests)
| Validation | Tests |
|------------|-------|
| Template×Mode combinations | 72 (18 × 4) |

**Total Test Count:** ~207 tests  
**Execution Time Target:** <5 seconds

---

## ⚡ Performance Targets

| Metric | Target | Baseline | Measurement |
|--------|--------|----------|-------------|
| Template Composition | <50ms | ~100ms | pytest-benchmark |
| Cache Hit Rate | >90% | N/A | Custom metric |
| YAML Loading | <100ms | ~150ms | pytest-benchmark |
| Memory Usage | <50MB | ~80MB | memory_profiler |
| Template Selection | <10ms | N/A | pytest-benchmark |

---

## 🔄 Git Workflow

### Branch Strategy
```
main (protected)
└── CORTEX-3.0 (current)
    └── phase-5-template-refactor (feature branch)
```

### Commit Convention
- **RED Phase:** `test: Add RED phase tests for [feature]`
- **GREEN Phase:** `feat: Implement [feature] (GREEN phase)`
- **REFACTOR Phase:** `refactor: Optimize [feature]`
- **Documentation:** `docs: Update [document]`

### Checkpoint Commits (10 total)
1. RED: Modular YAML tests
2. GREEN: Modular YAML structure
3. REFACTOR: Optimize YAML
4. RED: TemplateComposer tests
5. GREEN: TemplateComposer implementation
6. REFACTOR: Optimize TemplateComposer
7. RED: UserProfile tests
8. GREEN: UserProfile integration
9. ... (continues for all 5 deliverables)

---

## 📋 Risk Management

### HIGH RISK: Breaking Changes
**Probability:** Medium  
**Impact:** High  
**Mitigation:**
- Maintain `response-templates.yaml` as fallback
- Feature flag allows instant rollback
- Comprehensive backward compatibility tests
- Gradual rollout (10% → 50% → 100%)

### MEDIUM RISK: Performance Regression
**Probability:** Low  
**Impact:** Medium  
**Mitigation:**
- 24-hour caching reduces recomposition
- Lazy loading minimizes startup time
- Benchmark against baseline before deployment
- Pre-compile option for production

### LOW RISK: User Confusion (New Question)
**Probability:** Medium  
**Impact:** Low  
**Mitigation:**
- Question 2a is optional (default: 'balanced')
- Clear examples for each option
- Smart inference from interaction_mode
- Can update preference post-onboarding

---

## 📚 Documentation Deliverables

### To Create
1. `PHASE-5-COMPLETION-REPORT.md` (auto-generated)
2. `migration-guide.md` (for developers)
3. `template-composition-guide.md` (for contributors)

### To Update
1. `template-guide.md` (new architecture section)
2. `user-profile-guide.md` (Question 2a documentation)
3. `CORTEX.prompt.md` (new onboarding question)
4. `CONSOLIDATED-PLAN-SUMMARY.md` (Phase 5 status)

---

## ✅ Approval Checklist

**Ready to Start:** ✅ YES

- [x] DoR validated (all prerequisites met)
- [x] DoD defined (clear success criteria)
- [x] TDD workflow planned (RED-GREEN-REFACTOR)
- [x] Schedule realistic (38 hours over 5 days)
- [x] Risk assessment complete (mitigation strategies defined)
- [x] Test coverage targets defined (207 tests, 85%+)
- [x] Performance targets defined (<50ms composition)
- [x] Git workflow defined (branch, commits, checkpoints)
- [x] Rollback plan defined (feature flag + adapter)

---

**Next Steps:**
1. Create feature branch: `git checkout -b phase-5-template-refactor`
2. Begin Day 1: Deliverable 5.1 - Modular YAML Structure (RED phase)
3. Follow TDD workflow strictly (RED → GREEN → REFACTOR)
4. Commit at each checkpoint
5. Update progress in todo list

**Estimated Completion:** December 6, 2025 (5 days, 38 hours)
