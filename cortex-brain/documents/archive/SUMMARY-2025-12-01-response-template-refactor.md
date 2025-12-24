# Response Template System Refactor - Executive Summary

**Version:** 1.0  
**Date:** 2025-12-01  
**Author:** Asif Hussain  
**Status:** Design Complete - Awaiting Approval

---

## 📊 Overview

This refactor transforms CORTEX's response template system from a monolithic 2,669-line YAML file into a modular, profile-driven architecture that adapts responses based on user preferences.

**Key Metrics:**
- **58% size reduction** (2,669 → 1,120 lines)
- **21 hours** implementation time (~3 days)
- **4 modular YAML files** replacing 1 monolithic file
- **72 test combinations** (18 templates × 4 modes)
- **Zero breaking changes** (full backward compatibility)

---

## 🎯 Business Value

### Current Problems
1. **Maintainability Crisis** - 2,669-line file causes merge conflicts, slow iteration
2. **No Personalization** - Templates ignore user profile preferences (experience level, interaction mode)
3. **Hard-Coded Styles** - Cannot adapt responses to user needs (verbose vs concise)
4. **Content Duplication** - 43% redundant content across templates
5. **Performance** - Large file slows template loading and parsing

### Proposed Solutions
1. **Modular Architecture** - 4 focused files (components, templates, variants, routing)
2. **Profile Integration** - Templates adapt based on user experience and preferences
3. **Response Detail Preference** - New onboarding question for verbosity control
4. **Component Reuse** - Shared sections referenced by ID (eliminates duplication)
5. **Composer Engine** - Python-based composition (<50ms target) with 24-hour cache

---

## 🏗️ Architecture Changes

### Current State
```
response-templates.yaml (2,669 lines)
├─ Schema + optimization metadata
├─ 3 base templates (YAML anchors)
│  ├─ standard_5_part_base
│  ├─ tech_aware_base
│  └─ compact_format_base
└─ 18 template definitions
   └─ Hard-coded inheritance via <<: *anchor
```

### Proposed State
```
response-base-components.yaml (200 lines)
├─ Shared header/footer definitions
├─ Reusable section templates
└─ Variant formats (concise/balanced/verbose)

response-template-definitions.yaml (400 lines)
├─ 18 templates with metadata
├─ Required/optional sections by ID
└─ No hard-coded content

response-profile-variants.yaml (300 lines)
├─ 4 interaction modes configuration
├─ 4 experience levels adaptation
└─ Section inclusion/exclusion rules

response-routing-rules.yaml (220 lines)
├─ Intent detection keywords
├─ Priority ordering
└─ Template selection logic

src/utils/template_composer.py (300 lines)
└─ Runtime composition engine
```

**Key Architectural Decisions:**
- ✅ **Preserve:** CORTEX header format (## 🧠 CORTEX) + author attribution
- ✅ **Change:** 5-part structure → flexible 3-section base + profile-driven additions
- ✅ **New:** `response_detail` attribute (concise/balanced/verbose) separate from `interaction_mode`
- ✅ **Performance:** <50ms composition time with 24-hour cache, lazy loading

---

## 📋 Implementation Status Checklist

### ☐ Phase 1: YAML Refactoring (4 hours)
- [ ] Create `response-base-components.yaml` (200 lines)
  - [ ] Define shared header/footer components
  - [ ] Create reusable section templates
  - [ ] Define variant formats (concise/balanced/verbose)
- [ ] Create `response-template-definitions.yaml` (400 lines)
  - [ ] Migrate 18 existing templates
  - [ ] Define section requirements (required/optional)
  - [ ] Add metadata (triggers, response_type, expected_orchestrator)
- [ ] Create `response-profile-variants.yaml` (300 lines)
  - [ ] Configure 4 interaction modes (Autonomous/Guided/Educational/Pair)
  - [ ] Configure 4 experience levels (Junior/Mid/Senior/Expert)
  - [ ] Define section inclusion rules
- [ ] Create `response-routing-rules.yaml` (220 lines)
  - [ ] Migrate intent detection keywords
  - [ ] Define priority ordering
  - [ ] Map triggers to templates
- [ ] Validate YAML syntax
  - [ ] Use `yamllint` on all 4 files
  - [ ] Test with Python `yaml.safe_load()`
- [ ] Create migration script
  - [ ] Backup original `response-templates.yaml`
  - [ ] Generate comparison report (old vs new)

### ☐ Phase 2: Composer Engine (5 hours)
- [ ] Create `src/utils/template_composer.py` (300 lines)
  - [ ] Implement `TemplateComposer` class
  - [ ] Implement `compose_response()` with profile integration
  - [ ] Implement `_build_section_list()` with variant logic
  - [ ] Implement `_apply_experience_level()` for content adaptation
  - [ ] Add 24-hour caching mechanism
- [ ] Create unit tests
  - [ ] Test basic composition (no profile)
  - [ ] Test profile-aware composition (4 modes × 3 detail levels = 12 tests)
  - [ ] Test section reordering
  - [ ] Test variant application
  - [ ] Test caching behavior
  - [ ] Test error handling (missing components, invalid profile)
  - [ ] Target: 25 tests, 85% coverage

### ☐ Phase 3: Profile Enhancement (3 hours)
- [ ] Update database schema
  - [ ] Add `response_detail` column to `user_profile` table
  - [ ] Set default value: 'balanced'
  - [ ] Create migration script
- [ ] Update `UserProfileManager` class
  - [ ] Add `response_detail` parameter to `create_profile()`
  - [ ] Add `response_detail` parameter to `update_profile()`
  - [ ] Add getter method `get_response_detail()`
- [ ] Update onboarding template
  - [ ] Add Question 2a: "How detailed should responses be?"
  - [ ] Add 3 options: Concise/Balanced/Verbose
  - [ ] Add descriptions for each option
  - [ ] Make question optional (default to 'balanced')
- [ ] Update user-profile-guide.md
  - [ ] Document new Question 2a
  - [ ] Add examples for each detail level
  - [ ] Update API reference

### ☐ Phase 4: Selection Integration (4 hours)
- [ ] Create `src/utils/template_selector.py` (150 lines)
  - [ ] Implement `TemplateSelector` class
  - [ ] Implement `select_template()` with intent detection
  - [ ] Implement `_get_variant()` with profile awareness
  - [ ] Add override logic (response_detail can override interaction_mode)
- [ ] Update `IntentRouter` integration
  - [ ] Replace direct YAML loading with TemplateSelector
  - [ ] Pass user profile to template selection
  - [ ] Handle backward compatibility (users without response_detail)
- [ ] Create end-to-end tests
  - [ ] Test full workflow: intent → template selection → composition → rendering
  - [ ] Test profile override scenarios
  - [ ] Test fallback behavior (missing profile)
  - [ ] Target: 15 tests

### ☐ Phase 5: Validation (3 hours)
- [ ] Test all template×mode combinations
  - [ ] 18 templates × 4 interaction modes = 72 tests
  - [ ] Verify section inclusion/exclusion correct
  - [ ] Verify content adaptation appropriate
- [ ] Test response_detail overrides
  - [ ] Concise overrides (even in Educational mode)
  - [ ] Verbose overrides (even in Autonomous mode)
  - [ ] Balanced respects interaction_mode defaults
- [ ] Performance benchmarking
  - [ ] Measure composition time (target: <50ms)
  - [ ] Measure cache hit rate (target: >90%)
  - [ ] Compare against baseline (current system)
- [ ] User acceptance testing
  - [ ] Test with internal users (all 4 interaction modes)
  - [ ] Gather feedback on response quality
  - [ ] Iterate on variant configurations if needed

### ☐ Phase 6: Documentation (2 hours)
- [ ] Update `template-guide.md`
  - [ ] Document new modular architecture
  - [ ] Add TemplateComposer usage examples
  - [ ] Document component IDs and variant names
- [ ] Update `user-profile-guide.md`
  - [ ] Document Question 2a (response detail preference)
  - [ ] Add examples for concise/balanced/verbose
  - [ ] Update interaction mode examples with new format
- [ ] Create migration guide
  - [ ] Document breaking changes (none expected)
  - [ ] Provide rollback instructions
  - [ ] Document feature flag usage
- [ ] Update `CORTEX.prompt.md`
  - [ ] Update response format section
  - [ ] Add link to template-guide.md
  - [ ] Document new onboarding question

---

## 📈 Success Metrics

### Quantitative
- ✅ **File Size:** 58% reduction (2,669 → 1,120 lines)
- ⏳ **Performance:** <50ms composition time (vs ~100ms baseline)
- ⏳ **Test Coverage:** ≥85% for new code (TemplateComposer, TemplateSelector)
- ⏳ **Cache Hit Rate:** >90% for repeated queries
- ⏳ **Migration Success:** 100% of existing users migrated without errors

### Qualitative
- ⏳ **User Satisfaction:** Positive feedback from 80%+ of users on response relevance
- ⏳ **Maintainability:** Reduced time to add new template from 45 min → 15 min
- ⏳ **Flexibility:** New variants can be added without code changes (YAML-only)

---

## ⚠️ Risk Assessment & Mitigation

### HIGH RISK: Backward Compatibility
**Risk:** Existing users/systems break during migration  
**Mitigation:**
- Keep `response-templates.yaml` with deprecation warning
- Add feature flag `enable_modular_templates` (default: false)
- Gradual rollout: 10% → 50% → 100% over 2 weeks
- Full rollback capability via feature flag

### MEDIUM RISK: Performance Regression
**Risk:** Composition slower than direct YAML loading  
**Mitigation:**
- 24-hour cache for composed templates
- Lazy loading of YAML files (load on-demand)
- Pre-compile option for production (generate static templates)
- Benchmark against baseline before deployment

### LOW RISK: User Confusion (New Onboarding Question)
**Risk:** Users confused by Question 2a (response detail)  
**Mitigation:**
- Make question optional (default to 'balanced')
- Provide clear examples for each option
- Smart default inference (Autonomous→concise, Educational→verbose)
- Allow updating preference after onboarding

---

## 🔄 Migration Strategy

### Automatic Migration (Existing Users)
1. **No Action Required** - System detects missing `response_detail` field
2. **Smart Inference** - Infers from `interaction_mode`:
   - Autonomous → concise
   - Guided → balanced
   - Educational → verbose
   - Pair → balanced
3. **Database Update** - Backfills `response_detail` for all existing users
4. **Notification** - One-time message: "We've enhanced responses - update preference in profile"

### Full Onboarding (New Users)
1. Existing Questions 1-2 (experience, interaction mode)
2. **NEW Question 2a** (response detail preference)
3. Question 3 (tech stack)

### Validation
- ✅ Verify all existing users have `response_detail` value
- ✅ Verify templates compose correctly for all profiles
- ✅ Compare output quality (old vs new system)

---

## 🔙 Rollback Plan

### Feature Flag Control
```python
# cortex.config.json
{
  "template_system": {
    "enable_modular_templates": false,  # Set to false to rollback
    "gradual_rollout_percentage": 10    # 10% / 50% / 100%
  }
}
```

### Rollback Triggers
- Performance degradation (>50ms composition time)
- Error rate >1% in template composition
- User complaints >20% of rollout group
- Critical bug in TemplateComposer

### Rollback Procedure
1. Set `enable_modular_templates: false` in config
2. Restart CORTEX services
3. System falls back to original `response-templates.yaml`
4. Investigate root cause
5. Fix and re-deploy with smaller rollout percentage

---

## ❓ Open Questions (Require Approval)

### Q1: Response Detail vs Interaction Mode
**Question:** Should `response_detail` completely override `interaction_mode` formatting, or should it only influence verbosity while respecting mode structure?

**Options:**
- A) Complete override (concise always minimal, even in Educational)
- B) Influenced verbosity (concise Educational = shorter explanations but still teaching-focused)

**Recommendation:** Option B (influenced verbosity) - preserves interaction mode intent

---

### Q2: Backward Compatibility Duration
**Question:** How long should we maintain dual-system support (both old and new templates)?

**Options:**
- A) 1 version cycle (remove in v3.3)
- B) 3 version cycles (remove in v3.5)
- C) Indefinitely (feature flag permanent)

**Recommendation:** Option B (3 cycles) - gives ecosystem time to adapt

---

### Q3: Response Detail as Primary
**Question:** Should response_detail become the primary driver for formatting, with interaction_mode as secondary?

**Current:** interaction_mode is primary (Autonomous = minimal, Educational = verbose)  
**Proposed:** response_detail is primary (user explicitly chooses verbosity)

**Impact:** Simplifies selection logic, empowers user choice

**Recommendation:** Yes - user preference should override system defaults

---

### Q4: Pre-Compile for Production
**Question:** Should we offer pre-compilation of templates to static YAML for production deployments?

**Benefits:** No runtime composition cost, faster loading  
**Drawbacks:** Loses dynamic profile adaptation

**Use Case:** High-traffic deployments where caching might not be sufficient

**Recommendation:** Phase 2 feature (not in initial release)

---

## 📅 Timeline

**Total Duration:** 21 hours (~3 working days)

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: YAML Refactoring | 4 hours | 4 modular YAML files |
| Phase 2: Composer Engine | 5 hours | TemplateComposer class + tests |
| Phase 3: Profile Enhancement | 3 hours | response_detail field + onboarding |
| Phase 4: Selection Integration | 4 hours | TemplateSelector class + integration |
| Phase 5: Validation | 3 hours | 72 tests + benchmarks |
| Phase 6: Documentation | 2 hours | Updated guides |

**Recommended Schedule:**
- Day 1: Phases 1-2 (YAML + Composer)
- Day 2: Phases 3-4 (Profile + Integration)
- Day 3: Phases 5-6 (Validation + Docs)

---

## ✅ Approval Checklist

Before proceeding with implementation, please approve:

- [ ] Architecture approach (4 modular YAML files + TemplateComposer)
- [ ] Response detail preference as 4th onboarding question
- [ ] Migration strategy (automatic inference for existing users)
- [ ] Timeline (21 hours / 3 days)
- [ ] Open Question Q1: Response detail behavior (Option A or B?)
- [ ] Open Question Q2: Backward compatibility duration (Option A, B, or C?)
- [ ] Open Question Q3: Response detail as primary driver (Yes or No?)
- [ ] Open Question Q4: Pre-compile option (Include or defer?)

---

## 📞 Next Steps

1. **Review this summary** - Ensure alignment with project goals
2. **Answer open questions** - Decide on Q1-Q4 above
3. **Approve implementation** - Confirm 21-hour timeline acceptable
4. **Begin Phase 1** - Start YAML refactoring (4 hours)

**Contact:** Asif Hussain  
**Documentation:** See `PLAN-2025-12-01-response-template-refactor.yaml` for full technical details

---

**Status:** ⏳ Awaiting stakeholder approval  
**Version:** 1.0  
**Last Updated:** 2025-12-01
